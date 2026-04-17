# Boundary Decision Tree

> **Status:** Stable
>
> Single source of truth for the **Core vs. Annotation** boundary test
> and the subsequent **Tier classification**. All other documents
> (design.md, validation-modes.md, template.md) reference this file
> rather than restating the decision logic.

---

## 1. Purpose

When a new candidate `@X` is proposed, two sequential decisions must be
made:

1. **Phase A — Core vs. Annotation** (DSL-spec-level, universal)
2. **Phase B — Tier classification** (program-level, per-implementation)

Phase A is authoritative for all implementations. Phase B is the rule
followed by the Python reference implementation; other programs may
adopt a different tier classification per design-philosophy §4.2.

---

## 2. Phase A — Core vs. Annotation (Q1–Q3)

```
Q1. Is @X required to discuss the theoretical properties of the
    schedule (e.g., FI scallop)?
    YES → Core grammar candidate. Consider adding to Core, not annotation.
    NO  → Q2

Q2. Does @X alter the evaluation semantics of the schedule expression?
    YES → Schedule variant (Core grammar). Consider adding to Core.
    NO  → Q3

Q3. Is @X mandatory at the Core grammar level — universally required
    across the entire DSL spec, independent of any program's registry?
    YES → Core grammar candidate (subject to design-philosophy §8
          breaking-change constraints).
    NO  → Annotation candidate. Proceed to Phase B.
```

### Dangerous Patterns

```
-- NG: Annotation alters Core semantics
FI 10 @mode("resetting")     -- This is an FI variant → Core grammar

-- NG: Core grammar requires a specific annotation
FI 10 requires @clock, @operandum    -- Do not bake registry dependency into grammar

-- OK: Core is independent, annotation is additive
FI 10                        -- valid (in any registry)
FI 10 @clock(unit="s")       -- also valid (if the registry recognizes @clock)
```

### Note on Parse Errors

Whether the absence of `@X` causes a parse error **cannot be determined
at the DSL spec level**. It depends on the program's registry
(design-philosophy §4.2). Each program bears the responsibility of
defining what is required and what is optional in its own registry.

---

## 3. Phase B — Tier Classification (T-A–T-C)

Precondition: Phase A has judged the element an **Annotation candidate**
(all three questions answered NO/NO/NO).

```
T-A. Is @X a defaulted parameter? (e.g., @clock unit defaults to "s")
     YES → Tier 1 (defaulted)
     NO  → T-B

T-B. Is @X required when physical hardware is connected?
     (e.g., @session_end)
     YES → Tier 2 (mandatory in production mode)
     NO  → T-C

T-C. Is @X required in the publication phase? (e.g., @species)
     YES → Tier 3 (mandatory in publication mode)
     NO  → Tier 1 (informational metadata)
```

### Tier Summary

| Tier | When Required | Example |
|---|---|---|
| Tier 0 | Always (Core grammar) | Schedule expression itself |
| Tier 1 | Never mandatory; defaulted or informational | `@clock(unit)`, `@random(seed)` |
| Tier 2 | Production mode (physical HW connected) | `@session_end`, `@response(force)` |
| Tier 3 | Publication mode (manuscript preparation) | `@species`, `@strain`, `@deprivation` |

---

## 4. Application Examples

### 4.1 Reclassification of design.md §8 Proposals

| Proposal | Q1 | Q2 | Q3 | Phase A | T-A | T-B | T-C | Tier |
|---|---|---|---|---|---|---|---|---|
| `@session_end` | N | N | N | Annotation | N | Y | — | **Tier 2** |
| `@dependent_measure` | N | N | N | Annotation | N | N | Y | **Tier 3** |
| `@training_volume` | N | N | N | Annotation | N | N | Y | **Tier 3** |
| `@microstructure` | N | N | N | Annotation | N | N | Y | **Tier 3** |
| `@phase_end` | N | N | N | Annotation | N | N | Y | **Tier 3** |
| `@iri_window` | N | N | N | Annotation | N | N | Y | **Tier 3** |
| `@warmup_exclude` | N | N | N | Annotation | Y | — | — | **Tier 1** |
| `@response(force, IRT)` | N | N | N | Annotation | N | Y | — | **Tier 2** |
| `@logging` | N | N | N | Annotation | N | Y | — | **Tier 2** |
| `@clock(unit)` | N | N | N | Annotation | Y | — | — | **Tier 1** |
| `@clock(precision, sampling, sync)` | N | N | N | Annotation | N | Y | — | **Tier 2** |
| `@random(seed)` | N | N | N | Annotation | Y | — | — | **Tier 1** |
| `@timeout` | N | N | N | Annotation | N | Y | — | **Tier 2** (conditional) |
| `@session_onset` | N | N | N | Annotation | N | Y | — | **Tier 2** |
| `@reinforcer(clock_resume)` | N | N | N | Annotation | N | Y | — | **Tier 2** |
| `@species`, `@strain` | N | N | N | Annotation | N | N | Y | **Tier 3** |
| `@deprivation`, `@history`, `@n` | N | N | N | Annotation | N | N | Y | **Tier 3** |
| `@pretraining` | N | N | N | Annotation | N | N | Y | **Tier 3** |
| `@chamber(model)` | N | N | N | Annotation | N | N | Y | **Tier 3** |
| `@context(houselight)` | N | N | N | Annotation | N | Y | — | **Tier 2** |
| `@drug`, `@preparation` | N | N | N | Annotation | N | N | Y | **Tier 3** |
| `@phase` | N | N | N | Annotation | N | N | Y | **Tier 3** (see §5) |
| `@pr_breakpoint` | N | N | N | Annotation | N | Y | — | **Tier 2** |
| `@ioa`, `@ethics`, `@function` | N | N | N | Annotation | N | N | Y | **Tier 3** |

### 4.2 Boundary Test Template (for new proposals)

When proposing `@X`, complete the following (see also
[template.md](template.md)):

```markdown
## Boundary Review: @X → <annotator>

### Phase A: Core independence
- [ ] Q1: Can the theoretical properties of the schedule be discussed
      without @X? → YES means annotation OK
- [ ] Q2: Does @X alter the evaluation semantics of the schedule
      expression? → NO means annotation OK
- [ ] Q3: Is @X universally required across the entire DSL spec,
      independent of any registry? → NO means annotation OK

### Phase B: Tier classification
- [ ] T-A: Is @X a defaulted parameter? → YES → Tier 1
- [ ] T-B: Required when physical HW is connected? → YES → Tier 2
- [ ] T-C: Required for publication? → YES → Tier 3
- [ ] None of the above → Tier 1 (informational)
```

---

## 5. Resolved: `@phase` Classification

`@phase` is a **program-level-only informational annotation (Tier 3)**.

### Decision rationale

The apparent Q2 tension — "the same FR 1 under acquisition vs.
extinction constitutes a different experiment" — dissolves on closer
inspection: **extinction is expressed by changing the schedule to `EXT`,
not by annotating `FR5` with `@phase("extinction")`.**

```
-- Correct: the schedule itself changes
@phase("A1-baseline")       EXT
@phase("B1-treatment")      FR5 @reinforcer("pellet")
@phase("A2-reversal")       EXT
@phase("B2-replication")    FR5 @reinforcer("pellet")
```

`@phase` never alters the evaluation semantics of the schedule
expression (Q2 = NO). It labels experimental design periods for
organizing multi-session data. The schedule expression alone encodes
the operative contingency.

### Boundary test result

| Q | Answer | Reason |
|---|---|---|
| Q1 | NO | Schedule properties are discussed without `@phase` |
| Q2 | **NO** | Extinction = `EXT`, not `FR5 + @phase("extinction")`. The schedule expression, not the phase label, determines evaluation semantics |
| Q3 | NO | Not universally required; many single-phase studies have no `@phase` |

Phase B: T-A = NO, T-B = NO, T-C = YES → **Tier 3 (publication)**.

### Constraints

- `@phase` is **program-level only**. Schedule-level usage is a
  `SemanticError: PHASE_ONLY_PROGRAM_LEVEL`.
- `@phase` may serve as a trigger for tier rule dynamics (e.g.,
  `@phase("extinction")` exempts `@reinforcer` from Tier 2 requirements),
  but this is a validator concern, not a grammar concern.

---

## 6. Preservation of the §2 Principle

The core principle — "annotations are orthogonal metadata that do not
alter the evaluation semantics" — is **preserved** after the
introduction of the tier classification. The tier system extends the
principle by adding: "the requirement level branches into multiple
stages depending on the validation mode."

- The parser continues to accept annotations as optional
- The presence or absence of annotations does not change the
  mathematical properties of schedule expressions
- The tier-aware validator activates requirements according to the mode

---

## 7. References

- [design.md](design.md) §2 (original boundary test, now delegated here)
- [validation-modes.md](validation-modes.md) §6.1 (original tier
  classification, now delegated here)
- [design-philosophy.md](../design-philosophy.md) §4.2 (program-scoped
  closure), §8 (breaking-change constraints)
- [template.md](template.md) (annotation proposal template)
