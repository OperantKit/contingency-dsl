# example-annotator — Annotation Template

## Purpose

This is a template for proposing a new annotator for the **DSL project's
recommended registry**. Copy this directory and fill in each section.

Per [design-philosophy.md §4.2](../design-philosophy.md), third-party
programs are free to build their own registries without following this
template. This template is for annotators that aim to be adopted into
the DSL project's recommended set.

---

## Status

`[ Proposed | Schema Design | Stable ]`

Lifecycle:
- **Proposed** — Keyword candidates and boundaries proposed, but parameter schemas undefined
- **Schema Design** — Parameter schemas defined. Boundary justification and inclusion/exclusion criteria documented
- **Stable** — Schema frozen; breaking changes avoided in principle

Provenance may be noted in parentheses.

---

## Category

Which of the JEAB-aligned recommended categories does this annotator
belong to? Choose one:

- [ ] **Procedure** — schedule description, equivalence, conversion fill-in
- [ ] **Subjects** — subject history, establishing operations, state
- [ ] **Apparatus** — chamber, operandum, HW binding, timing contract
- [ ] **Measurement** — steady-state, baseline, phase logic, DV specs
- [ ] **Extension** — clinical, derivational, provenance, domain-specific
      (requires justification for a new category)

---

## Keywords

| Keyword | Purpose | Example |
|---|---|---|
| @example_key | What this annotation declares | `@example_key("value", param=42)` |

---

## Boundary Justification

**Is this annotation necessary for theoretical discussion: YES / NO**

- (explain why the schedule's theoretical properties don't require this annotation)

**Why this annotation should reside within the DSL:**

- (explain what becomes verifiable / compilable / reproducible by having it in DSL)

---

## Inclusion Criteria

- What *belongs* in this annotator (one dimension, clearly stated)

## Exclusion Criteria

- What does *not* belong here, and where it should go instead

---

## Boundary Review Checklist

Fill this in when proposing a new keyword `@X`:

```markdown
### 1. Core independence (boundary-decision.md Phase A)
The following corresponds to Q1-Q3 in boundary-decision.md §2.
boundary-decision.md is authoritative; if this checklist conflicts, that file prevails.
- [ ] Q1: Can the schedule's theoretical properties (e.g., FI scallop) be discussed without `@X`? → If YES, annotation OK
- [ ] Q2: Does `@X` alter the evaluation semantics of the schedule expression? → If NO, annotation OK
- [ ] Q3: Can `@X` be claimed as mandatory at the Core grammar level (i.e., required across the entire DSL spec, independent of any registry)? → If NO, annotation OK
      (Promotion is permissible only under the constraints of design-philosophy §8)

### 2. Category fit
- [ ] Is `@X` consistent with the selected category (Procedure / Subjects / Apparatus / Measurement / Extension)?
- [ ] Does `@X` belong to the dimension covered by this annotator?
- [ ] Is `@X` semantically consistent with the existing keywords?
- [ ] Does `@X` avoid conflicts with keywords in other recommended annotators?

### 3. Necessity for recommendation
- [ ] Is expression outside the DSL (comments, external files) insufficient?
- [ ] Does compilation targets (papers, code generation, verification) benefit from this annotation?
- [ ] Does this annotation merit inclusion in the DSL project's recommended set, rather than remaining third-party only?

### 4. Domain expert sign-off
- [ ] EAB: Valid from the perspective of basic research
- [ ] (domain): Valid from the perspective of the relevant domain
- [ ] PLT: Consistent from the perspective of language design
```

---

## Dependencies

Other annotators this one requires (if any). Prefer none.

---

## Implementation Reference

Where the implementation lives (e.g., `apps/experiment/contingency-dsl-py/src/contingency_dsl.annotations/<name>_annotator/`).

Note: third-party programs may implement their own annotator conforming
to this schema without using the reference implementation.
