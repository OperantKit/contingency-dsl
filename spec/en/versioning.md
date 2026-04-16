# Versioning Strategy

> Part of the [contingency-dsl spec](architecture.md). Defines DSL version management, annotator capability discovery, and backward compatibility guarantees.

**Status:** Draft (2026-04-14)
**Addresses:** EXTENSION_RULES_REVIEW §3.7 — "Versioning strategy gap"

---

## 1. Problem Statement

The DSL defines `AnnotationModule.version` (semver) and `schema-format.md` requires a `"version"` field per annotator schema. However, no mechanism exists for:

1. Detecting breaking changes at the DSL source level
2. Pinning conformance tests to specific versions
3. Managing Tier classification changes across versions
4. Ensuring that a DSL source file written for annotator v1.0 does not silently break under v1.0

Without a versioning strategy, the system will accumulate implicit compatibility assumptions that shatter as annotators evolve.

---

## 2. Design Approach: Capability Discovery

We adopt **capability discovery** over explicit version pragmas. The rationale:

- Version pragmas (`#[dsl_version = "1.0"]`) create boilerplate and raise the question of default behavior when omitted.
- Semver diamond dependency problems arise when multiple annotators pin different ranges.
- Capability discovery is **declarative**: the source itself declares what it needs by using specific keywords/features. The registry validates that its loaded annotators satisfy those needs.

### 2.1 Core Principle

> A DSL source file's required capabilities are fully determined by static analysis of its content. The registry checks that the loaded annotators provide those capabilities at compatible versions.

This means:

- `FR5` alone requires no annotator — capability set is empty.
- `FR5 @reinforcer("sucrose")` requires `procedure.stimulus >= 1.0`.
- `@species("rat") FR5 @reinforcer("sucrose")` requires `procedure.stimulus >= 1.0` AND `subjects >= 1.0`.

---

## 3. Capability Identifiers

### 3.1 Format

```
<category>[.<sub_annotator>] @ >= <major>.<minor>
```

Examples:

| Capability ID | Meaning |
|---|---|
| `procedure.stimulus@>=1.0` | procedure-annotator's stimulus sub-annotator, v1.0+ |
| `procedure.temporal@>=1.0` | procedure-annotator's temporal sub-annotator, v1.0+ |
| `subjects@>=1.0` | subjects-annotator, v1.0+ |
| `apparatus@>=1.0` | apparatus-annotator, v1.0+ |
| `measurement@>=1.0` | measurement-annotator, v1.0+ |

### 3.2 Derivation from Schema

Each annotator schema (`*.schema.json`) already declares `category`, `sub_annotator` (optional), and `version`. The capability ID is mechanically derived:

```
capability_id = category + ("." + sub_annotator if sub_annotator else "") + "@>=" + version
```

### 3.3 Version Semantics

Annotator versions follow semver with DSL-specific interpretation:

| Change type | Version bump | Example |
|---|---|---|
| New optional keyword added | MINOR | Adding `@baseline` to measurement-annotator |
| New required parameter on existing keyword | MAJOR | `@reinforcer` now requires `modality` |
| Keyword removed or renamed | MAJOR | `@sd` renamed to `@discriminative_stimulus` |
| Parameter type changed | MAJOR | `@clock(resolution)` from string to number |
| Default value changed (semantic effect) | MAJOR | `@session_end(rule)` default `"first"` → `"last"` |
| Description/documentation only | PATCH | Clarifying `@species` description |
| Error code added (new validation) | MINOR | New error `E_STRAIN_UNKNOWN` |

---

## 4. Capability Analysis

### 4.1 Static Analysis Function

```python
def analyze_capabilities(source: str) -> frozenset[str]:
    """Extract the set of capabilities required by a DSL source.

    Scans annotation usage and maps each annotation keyword to the
    annotator (category.sub_annotator) that owns it, using the
    keyword → annotator mapping from the registry's loaded schemas.
    """
    ...
```

### 4.2 Example

```python
source = """
@species("rat")
@deprivation("food", hours=23)
@reinforcer("sucrose", magnitude="0.1ml")
@chamber("med-associates", model="ENV-007")
VI 30s @clock(resolution="1ms")
"""

required = analyze_capabilities(source)
# → frozenset({
#     "subjects@>=1.0",
#     "procedure.stimulus@>=1.0",
#     "procedure.temporal@>=1.0",
#     "apparatus@>=1.0",
# })
```

### 4.3 Registry Validation

```python
@dataclass(frozen=True)
class AnnotationRegistry:

    @staticmethod
    def build(*annotators: AnnotationModule) -> "AnnotationRegistry":
        """Create a registry. Raises ValueError if:
        - Two annotators claim the same annotation keyword (disjointness violation)
        - An annotator's requires set is not satisfied (dependency violation)
        """
        ...

    def validate_capabilities(self, required: frozenset[str]) -> None:
        """Check that every required capability is satisfied by a loaded annotator.

        Raises:
            MissingCapabilityError: An annotator is not loaded or its version
                is too low.
        """
        ...
```

### 4.4 Error Reporting

```
MissingCapabilityError: DSL source requires 'subjects@>=1.0' but no
subjects-annotator is loaded. Either:
  1. Add SubjectsAnnotator() to the registry, or
  2. Remove @species/@strain/@deprivation annotations from the source.

VersionTooLowError: DSL source requires 'procedure.stimulus@>=1.1'
(keyword @reinforcer with param 'modality' introduced in v1.0),
but loaded procedure-annotator provides stimulus v1.0.
```

---

## 5. DSL Core Version

The DSL core grammar itself also carries a version. This is separate from annotator versions.

### 5.1 Core Version Scope

| Component | Current version | Versioned by |
|---|---|---|
| Base grammar (grammar.ebnf) | 1.0 | DSL core version |
| Combinators (Conc, Alt, Chain, ...) | 1.0 | DSL core version |
| Annotation syntax (`@name(args)`) | 1.0 | DSL core version |
| Individual annotator schemas | per-annotator | Annotator version (§3) |
| Validation modes | 1.0 | DSL core version |
| Representations (T-tau, etc.) | per-representation | Representation version |

### 5.2 Optional Source Header

For explicit version pinning (opt-in, not required):

```
#[dsl = "1.0"]

@species("rat")
FR5 @reinforcer("sucrose")
```

When present, the parser validates that its grammar version is compatible with the declared version. When absent, the parser uses its own version (latest) — this is the default for interactive/educational use.

---

## 6. Conformance Test Versioning

### 6.1 Test Suite Structure

```
conformance/
├── core/
│   ├── v1.0/          # Tests for core grammar v1.0
│   └── v1.0/          # Tests added in v1.0
├── annotators/
│   ├── procedure-stimulus/
│   │   ├── v1.0/
│   │   └── v1.0/
│   ├── subjects/
│   │   └── v1.0/
│   └── ...
└── compatibility.yaml  # Version compatibility matrix
```

### 6.2 Compatibility Matrix

```yaml
# conformance/compatibility.yaml
core:
  - version: "1.0"
    test_suite: conformance/core/v1.0/
  - version: "1.1"
    test_suite: conformance/core/v1.0/
    backward_compatible_with: "1.0"

annotators:
  procedure.stimulus:
    - version: "1.0"
      test_suite: conformance/annotators/procedure-stimulus/v1.0/
    - version: "1.1"
      test_suite: conformance/annotators/procedure-stimulus/v1.0/
      backward_compatible_with: "1.0"
      migration: migrations/procedure-stimulus-1.0-to-1.1.md
```

### 6.3 CI Enforcement

Each version entry in `compatibility.yaml` that declares `backward_compatible_with` MUST pass all test suites of the referenced version. CI runs the compatibility matrix to verify that minor version bumps do not break backward compatibility.

---

## 7. Tier Version Management

Tier classifications (Tier 1-4) from `validation-modes.md` may change as the DSL matures. A keyword initially classified as Tier 4 (Extension) may be promoted to Tier 3 (Publication) if it proves universally necessary.

### 7.1 Tier Change Policy

| Change | Impact | Requirement |
|---|---|---|
| Promotion (Tier 4 → 3, 3 → 2) | Non-breaking — validation becomes stricter for higher modes | MINOR version bump of the annotator |
| Demotion (Tier 2 → 3, 3 → 4) | Potentially breaking — previously required annotations become optional | MAJOR version bump of the annotator |
| New keyword at any Tier | Non-breaking for existing sources | MINOR version bump |
| Keyword removal | Breaking | MAJOR version bump |

### 7.2 Tier History

Each annotator schema SHOULD include a `tier_history` field:

```json
{
  "keywords": {
    "reinforcer": {
      "tier": 3,
      "tier_history": [
        { "version": "1.0", "tier": 3 },
        { "version": "0.9", "tier": 4 }
      ]
    }
  }
}
```

---

## 8. Migration Guides

When a MAJOR version bump occurs, a migration guide MUST be provided at:

```
migrations/<annotator>-<old>-to-<new>.md
```

Each migration guide MUST include:

1. **Breaking changes**: exhaustive list of incompatible changes
2. **Automated fix**: if a mechanical source transformation exists, provide it (or a script)
3. **Manual review**: changes requiring human judgment
4. **Conformance delta**: new test cases added, old test cases deprecated

---

## 9. Summary

| Mechanism | Purpose | When applied |
|---|---|---|
| Capability discovery (§4) | Detect missing/outdated annotators at load time | Every parse |
| Optional `#[dsl = "X.Y"]` header (§5.2) | Explicit core version pinning | Opt-in |
| Conformance matrix (§6) | CI-enforced backward compatibility | Every CI run |
| Tier history (§7.2) | Track Tier classification evolution | Schema updates |
| Migration guides (§8) | Human-readable upgrade path | MAJOR bumps |
