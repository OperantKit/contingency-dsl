# Annotation Schema Format — Language-Independent Meta-DSL

> **Status:** Stable (2026-04-13)
>
> This document defines the **Annotation Schema Format**: the
> language-independent schema language used to describe annotation
> keywords, their parameters, types, constraints, and scoping.
>
> It resolves the "メタDSL 未定義" issue identified in
> annotation-design.md §1 and §7.1.

---

## 1. Purpose

The Annotation Schema Format serves as the **single source of truth**
for annotation keyword definitions. Every implementation language
(Python, Rust, Kotlin, etc.) reads from the same schema files and
generates equivalent `AnnotationModule` implementations.

### Design decision: JSON Schema extension

The format is based on [JSON Schema 2020-12](https://json-schema.org/draft/2020-12/schema)
with DSL-specific extensions. This was chosen over alternatives (EBNF
extension, independent schema DSL) for the following reasons:

1. **Existing ecosystem** — mature validator libraries in Python
   (`jsonschema`), Rust (`jsonschema-rs`), Kotlin (`json-schema-validator`)
2. **Consistency** — the DSL's AST already uses JSON Schema
3. **Tooling** — LSP completion, linting, and documentation generation
   are achievable with standard JSON Schema tooling
4. **Low adoption cost** — no new parser or generator to implement

The DSL-specific extensions (`keywords`, `scope`, `positional`,
`required_if`, `forbidden_if`, `aliases`, `errors`) are placed in
properties that standard JSON Schema validators ignore, making the
files valid JSON Schema documents that also carry DSL semantics.

---

## 2. Terminology

| Term | Definition |
|---|---|
| **Annotator** | A named module that owns a set of annotation keywords. Maps 1:1 to a JEAB Method section category (design-philosophy §3.7). |
| **Keyword** | A single annotation name (e.g., `reinforcer`, `session_end`). Appears in DSL source as `@keyword(...)`. |
| **Positional argument** | The first unnamed argument of an annotation: `@species("rat")`. At most one per keyword. |
| **Keyword argument** | A named argument: `@session_end(rule="first", time=60min)`. Zero or more per keyword. |
| **Scope** | Where an annotation may appear: `program` (session-wide default) or `schedule` (attached to a specific schedule expression). |
| **Registry** | The set of annotators loaded by a specific program (runtime/interpreter). Program-scoped per design-philosophy §4.2. |
| **Schema file** | A JSON file conforming to this specification that defines one annotator. |

---

## 3. File conventions

### 3.1 Location

Schema files reside in:

```
schema/annotations/<annotator-name>.schema.json
```

For annotators with sub-annotators (e.g., `procedure-annotator` with
`stimulus` and `temporal` sub-annotators):

```
schema/annotations/procedure-stimulus.schema.json
schema/annotations/procedure-temporal.schema.json
```

Extension annotators (outside the 4 JEAB categories):

```
schema/annotations/extensions/<name>.schema.json
```

### 3.2 Naming

- File names use kebab-case: `procedure-stimulus.schema.json`
- The `.schema.json` suffix is required
- The file name (minus suffix) must match the `title` field

### 3.3 Encoding

UTF-8, no BOM. Standard JSON (no trailing commas, no comments).

---

## 4. Top-level structure (meta-schema)

Every schema file MUST contain the following top-level properties:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://operantkit.dev/contingency-dsl/schema/annotations/<name>.schema.json",
  "title": "<annotator-name>",
  "description": "<one-line purpose>",
  "category": "<JEAB category>",
  "version": "<semver>",
  "status": "<lifecycle>",
  "keywords": { ... }
}
```

### Property definitions

| Property | Type | Required | Description |
|---|---|---|---|
| `$schema` | string | YES | Always `"https://json-schema.org/draft/2020-12/schema"` |
| `$id` | string (URI) | YES | Canonical URI for this schema |
| `title` | string | YES | Annotator name. Must match file name (minus `.schema.json`) |
| `description` | string | YES | One-line description |
| `category` | string | YES | JEAB category: `"Procedure"`, `"Subjects"`, `"Apparatus"`, `"Measurement"`, or `"Extension"` |
| `sub_annotator` | string | NO | Sub-annotator name within a category (e.g., `"stimulus"`, `"temporal"`) |
| `version` | string | YES | Semantic version of this schema |
| `status` | string | YES | Lifecycle stage (see §4.1) |
| `keywords` | object | YES | Keyword definitions (see §5) |
| `future_keywords` | array of strings | NO | Planned keyword names not yet defined |

### 4.1 Lifecycle stages

| Status | Meaning |
|---|---|
| `Proposed` | Keyword candidates and boundaries proposed; parameter schemas undefined |
| `Schema Design` | Parameter schemas defined; boundary justification documented |
| `Stable` | Schema frozen; breaking changes avoided in principle |

Provenance may be noted in parentheses:
`"Schema Design (restructured 2026-04-12)"`.

---

## 5. Keyword definition

Each entry in `keywords` maps a keyword name (string) to a keyword
definition object.

```json
"reinforcer": {
  "description": "Reinforcer identification and classification.",
  "scope": ["program", "schedule"],
  "positional": { "type": "string", "required": true, "description": "Stimulus identity" },
  "params": { ... },
  "aliases": ["punisher", "consequentStimulus"],
  "alias_note": "All three collapse to the same AST node.",
  "errors": { ... },
  "reference": "Skinner, B. F. (1938). The behavior of organisms. Appleton-Century-Crofts."
}
```

### Property definitions

| Property | Type | Required | Description |
|---|---|---|---|
| `description` | string | YES | What this annotation declares |
| `scope` | array of strings | YES | Allowed scoping levels: `"program"`, `"schedule"`, or both |
| `positional` | object or null | YES | Positional argument definition (§5.1). `null` if keyword-only |
| `params` | object | YES | Keyword argument definitions (§6). Empty object `{}` if none |
| `aliases` | array of strings | NO | Alternative keyword names (§8) |
| `alias_note` | string | NO | Explanation of alias behavior |
| `errors` | object | NO | Error code definitions (§9) |
| `reference` | string or null | YES | APA-format citation, or `null` if no single canonical reference |

### 5.1 Positional argument

The `positional` field describes the single unnamed argument that may
appear first in the annotation's argument list.

When `positional` is not `null`:

| Property | Type | Required | Description |
|---|---|---|---|
| `type` | string | YES | Value type (§7) |
| `required` | boolean | YES | Whether the positional argument is mandatory |
| `description` | string | NO | What the value represents |

When `positional` is `null`, the keyword accepts only keyword arguments
(or no arguments at all if `params` is also empty).

**DSL surface syntax mapping:**

```
@species("rat")                    → positional = "rat"
@session_end(rule="first", ...)    → no positional (keyword-only)
@chamber("med-associates", model="ENV-007")  → positional + keyword args
```

---

## 6. Parameter definition

Each entry in `params` maps a parameter name to a parameter definition
object.

```json
"time": {
  "type": "time_value",
  "required_if": { "rule": ["first", "time_only"] },
  "forbidden_if": { "rule": ["reinforcers_only"] },
  "description": "Maximum session duration"
}
```

### Property definitions

| Property | Type | Required | Default | Description |
|---|---|---|---|---|
| `type` | string | YES | — | Value type (§7) |
| `required` | boolean | NO | `false` | Unconditionally required |
| `required_if` | object | NO | — | Conditionally required (§6.1) |
| `forbidden_if` | object | NO | — | Conditionally forbidden (§6.1) |
| `enum` | array | NO | — | Exhaustive set of allowed values |
| `minimum` | number | NO | — | Minimum value (inclusive). Applicable to `number` and `integer` types |
| `default` | any | NO | — | Default value when omitted |
| `default_expr` | string | NO | — | Default derived from another parameter's value (§6.2) |
| `description` | string | YES | — | What the parameter represents |

### 6.1 Conditional constraints: `required_if` / `forbidden_if`

These express parameter requirements that depend on the value of
another parameter in the same keyword.

**Schema:**

```json
"required_if": { "<param_name>": ["<value1>", "<value2>", ...] }
"forbidden_if": { "<param_name>": ["<value1>", "<value2>", ...] }
```

**Semantics:**

- `required_if`: the parameter is REQUIRED when `<param_name>` has any
  of the listed values.
- `forbidden_if`: the parameter is FORBIDDEN (must not appear) when
  `<param_name>` has any of the listed values.

**Example** (from `measurement.schema.json`):

```json
"time": {
  "type": "time_value",
  "required_if": { "rule": ["first", "time_only"] },
  "forbidden_if": { "rule": ["reinforcers_only"] }
}
```

This means:
- When `rule="first"` or `rule="time_only"`, `time` MUST be specified
- When `rule="reinforcers_only"`, `time` MUST NOT be specified

**Constraint:**
- `required_if` and `forbidden_if` MUST NOT overlap (no value may
  appear in both arrays for the same parameter).
- Both refer to a parameter within the same keyword definition.
- At most one `required_if` and one `forbidden_if` per parameter.

### 6.2 Derived defaults: `default_expr`

When a parameter's default value is the value of another parameter in
the same keyword, use `default_expr` instead of `default`.

```json
"min_sessions": {
  "type": "integer",
  "minimum": 1,
  "default_expr": "window_sessions",
  "description": "Minimum total sessions before stability check"
}
```

This means: if `min_sessions` is omitted, its value defaults to the
value of `window_sessions`.

**Constraints:**
- `default_expr` is a string containing the name of another parameter
  in the same keyword.
- `default` and `default_expr` are mutually exclusive.
- The referenced parameter MUST be defined in the same keyword's `params`.

---

## 7. Type vocabulary

The schema format defines the following type identifiers. These
correspond to the DSL grammar's `annotation_val` production
(grammar.ebnf §4.7).

| Type identifier | DSL surface syntax | JSON representation | Grammar production |
|---|---|---|---|
| `"string"` | `"quoted text"` | JSON string | `string_literal` |
| `"number"` | `3.14` | JSON number | `number` |
| `"integer"` | `42` | JSON integer | `number` (semantic: no decimal point) |
| `"time_value"` | `60min`, `30s`, `2000ms` | JSON number (normalized to seconds) | `time_value` → `number time_unit` |

### 7.1 `time_value` normalization

In the DSL source, time values carry explicit units (`s`, `ms`, `min`).
In the AST and in schema validation, time values are normalized to
**seconds** as a JSON number. The original unit is discarded after
normalization.

| Source | Normalized value |
|---|---|
| `60min` | `3600` |
| `30s` | `30` |
| `2000ms` | `2` |

Programs MAY choose a different normalization convention, but the
schema format assumes seconds as the canonical unit.

### 7.2 `integer` vs `number`

Both map to the grammar's `number` production. The distinction is
semantic:

- `integer`: the value MUST NOT contain a decimal point. Represents
  counts, indices, and other discrete quantities.
- `number`: the value MAY contain a decimal point. Represents
  continuous quantities (durations, percentages, rates).

### 7.3 Type extensions

The type vocabulary is intentionally minimal, matching the DSL
grammar's `annotation_val` production. If future annotations require
structured/nested values, the type vocabulary will be extended via an
additive revision of this specification.

Current `annotation_val` does NOT support:
- Arrays / lists
- Nested objects
- Schedule expression references
- Boolean values

If these become necessary, they require a grammar extension to
`annotation_val` (additive, per design-philosophy §8.1) and a
corresponding type identifier in this specification.

---

## 8. Aliases

A keyword MAY declare aliases — alternative names that collapse to
the same AST node.

```json
"reinforcer": {
  "aliases": ["punisher", "consequentStimulus"],
  "alias_note": "All three collapse to the same AST node. The source keyword is preserved as a pragmatic hint."
}
```

### Semantics

1. All aliases are **strictly equivalent** to the primary keyword at
   the AST level.
2. The source keyword name is preserved as a `label` field in the AST
   for pragmatic purposes (e.g., paper compilation) but is ignored in
   equivalence judgment.
3. A program's registry MAY adopt all aliases, only the primary, or
   add its own aliases.

### Constraints

- Alias names MUST NOT collide with any other keyword name (in the
  same annotator or across recommended annotators).
- The primary keyword is the one listed as the key in `keywords`.
  Aliases are listed in the `aliases` array.

See annotation-design.md §3.5 for the theoretical justification.

---

## 9. Error codes

A keyword MAY declare error codes that implementations should use
when validation fails.

```json
"errors": {
  "SESSION_END_MISSING_PARAM": "rule=first requires both time and reinforcers",
  "SESSION_END_INVALID_COMBO": "rule=time_only forbids reinforcers"
}
```

### Conventions

- Error code names use UPPER_SNAKE_CASE.
- Error code names are prefixed with the keyword name (uppercased) to
  avoid collisions across keywords.
- The value is a human-readable error message template.
- Implementations MUST use these codes (or a superset) when reporting
  annotation validation errors.

---

## 10. Scope semantics

The `scope` array declares where an annotation may appear in DSL source.

| Scope | DSL position | Semantics |
|---|---|---|
| `"program"` | Before `param_decl*` / `binding*` / `schedule` | Session-wide default |
| `"schedule"` | After a `schedule` expression | Attached to that expression; overrides program-level |

**Scoping resolution** (from grammar.ebnf §4.7):

```
resolve(key, S) = S.annotations[key]  if key in S.annotations
                  program.annotations[key]  otherwise
```

A keyword with `scope: ["program", "schedule"]` may appear at both
levels. The schedule-level annotation overrides the program-level
default for that expression only.

A keyword with `scope: ["program"]` at the schedule level is a
SemanticError. A keyword with `scope: ["schedule"]` at the program
level is a SemanticError.

---

## 11. Registry construction protocol

A **registry** is the set of annotators that a specific program
recognizes. Registries are program-scoped (design-philosophy §4.2).

### 11.1 From schema files to runtime registry

```
schema/annotations/*.schema.json
    ↓  schema loader (per-language)
AnnotationRegistry (runtime object)
    ↓  parser integration
Parser validates @keyword(...) against registry
```

Each implementation language provides a schema loader that:

1. Reads all `*.schema.json` files from the configured schema directory
2. Validates each file against this specification (§4 meta-schema)
3. Builds a keyword → validator mapping
4. Registers alias → primary keyword mappings
5. Exposes a `validate(keyword, args) → Result` interface

### 11.2 3rd-party registries

Third-party programs construct their own registries by:

- Adopting the DSL project's recommended schema files (all or subset)
- Adding their own schema files (same format)
- Ignoring or replacing recommended annotators

All registries share the same schema format. Interoperability is
guaranteed at the schema level: a DSL source valid in registry A can
be checked against registry B's schemas to determine compatibility.

### 11.3 Composite registries

A program MAY compose its registry from multiple schema files. When
composing:

- Keyword name collisions across schema files are an error
  (except alias → primary mappings within the same annotator)
- Category metadata is informational and does not affect validation

---

## 12. Relationship to grammar.ebnf

The Annotation Schema Format operates at a **different level** than
grammar.ebnf:

| Concern | Governed by |
|---|---|
| Annotation **syntax** (`@name(args)`) | grammar.ebnf §4.7 |
| Annotation **names and argument schemas** | This specification |
| Annotation **name resolution** (known vs unknown) | Program registry |

grammar.ebnf defines the syntactic form of annotations as:

```ebnf
annotation       ::= "@" annotation_name ("(" annotation_args ")")?
annotation_val   ::= string_literal | time_value | number
```

This specification defines **what `annotation_name` values exist** and
**what argument shapes they accept**. The grammar is deliberately
open (any `annotation_name` is syntactically valid); the schema
provides the semantic layer that a given program's registry uses to
validate names and arguments.

---

## 13. Conformance requirements

### For schema files

A schema file is **conformant** if it:

1. Is valid JSON
2. Contains all required top-level properties (§4)
3. Every keyword definition contains all required properties (§5)
4. Every parameter definition contains all required properties (§6)
5. All `type` values are in the type vocabulary (§7)
6. `required_if` / `forbidden_if` arrays do not overlap (§6.1)
7. `default` and `default_expr` are mutually exclusive (§6.2)
8. `default_expr` references an existing parameter in the same keyword

### For implementations

An implementation is **conformant** if it:

1. Can load any conformant schema file
2. Validates annotations against loaded schemas
3. Uses the specified error codes when validation fails
4. Implements scope resolution per §10
5. Normalizes `time_value` to seconds (or documents its convention)
6. Treats aliases as equivalent to the primary keyword in AST

---

## 14. Existing conformant schemas

The following schema files conform to this specification as of
2026-04-13:

| Schema file | Category | Keywords | Status |
|---|---|---|---|
| `procedure-stimulus.schema.json` | Procedure | `reinforcer`, `sd`, `brief` | Schema Design |
| `procedure-temporal.schema.json` | Procedure | `clock`, `warmup`, `algorithm` | Schema Design |
| `procedure-trial-structure.schema.json` | Procedure | `trial_mix` (types: peak, reinstatement, temporal_bisection) | Proposed |
| `subjects.schema.json` | Subjects | `species`, `strain`, `deprivation`, `history`, `n` | Schema Design |
| `apparatus.schema.json` | Apparatus | `chamber`, `operandum`, `interface`, `hardware` | Schema Design |
| `measurement.schema.json` | Measurement | `session_end`, `baseline`, `steady_state` | Schema Design |

Total: 6 annotation schema files, 18 keywords, 4 JEAB categories fully covered.

Note: The `schema/experiment/` directory contains separate schemas for multi-phase experimental designs (`phase-sequence.schema.json`, `experiment.schema.json`). These are not annotation schemas but structural schemas that reference Core AST types and annotations via `$ref`.

---

## Relationship to other specifications

This document is subordinate to [design-philosophy.md](../design-philosophy.md):

- design-philosophy §4.2 (program-scoped closure) governs registry composition
- design-philosophy §4.3 (category-neutral equivalence) governs category semantics
- design-philosophy §6 (language independence) motivates this specification
- design-philosophy §8 (breaking change policy) governs schema evolution

This document is a peer of:

- [annotations/design.md](design.md) — annotation boundary principles and annotator ownership
- [annotations/validation-modes.md](validation-modes.md) — tier × mode validation

---

## Provenance

This specification formalizes the de facto schema format that emerged
from the 5 annotator schema files created during 2026-04-12. The
format was adopted as Option (b) — JSON Schema extension — from the
alternatives enumerated in `.local/annotations/meta/schema-design.md`.
