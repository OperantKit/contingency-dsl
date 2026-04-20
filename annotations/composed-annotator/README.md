# composed-annotator — Composed-Layer Execution Semantics

## Purpose

Declares **how recorded responses modulate scheduled US delivery** during
composed procedures that layer Pavlovian contingencies over operant
baselines: negative automaintenance (omission) and discriminated
avoidance (two-process-theory preparations).

Corresponds to the portion of a JEAB Procedure section that specifies
*response-contingent* US rules on top of an underlying Pavlovian
pairing. The pairing itself is captured by the Tier A respondent
primitive; the cancellation or postponement rule is captured by a
`@omission` / `@avoidance` annotation attached to that primitive.

This annotator is part of the **core recommended vocabulary** maintained
by the DSL project. Per
[design-philosophy.md §4.2](../../spec/en/design-philosophy.md), third-party
programs retain the freedom to reinterpret or replace these categories, but
the DSL project supplies and maintains the reference implementation in
[`contingency-dsl-py`](../../../contingency-dsl-py/) and
[`contingency-dsl-rs`](../../../contingency-dsl-rs/).

---

## Status

`Stable`

---

## Category

- [x] **Procedure** — response-contingent US-modulation rules

---

## Keywords

| Keyword | Purpose | Example |
|---|---|---|
| `@omission` | Negative automaintenance: response during CS cancels US | `@omission(response="key_peck", during="cs")` |
| `@avoidance` | Discriminated avoidance: response during CS cancels or postpones US | `@avoidance(response="lever_press", mode="cancel")` |

## Scope and attachment

Both keywords are **schedule-level** annotations; they attach postfix to
a respondent primitive (`Pair.ForwardDelay(...)` typically) and surface
in the AST inside an `AnnotatedSchedule` node wrapping the primitive.

## Disjointness

At most one of `@omission` / `@avoidance` may be attached to a single
respondent primitive. Programs that need both simultaneously must
decompose them into separate phases.

## References

- Williams, D. R., & Williams, H. (1969). Auto-maintenance in the pigeon: Sustained pecking despite contingent non-reinforcement. *Journal of the Experimental Analysis of Behavior*, 12(4), 511–520. https://doi.org/10.1901/jeab.1969.12-511
- Solomon, R. L., & Wynne, L. C. (1954). Traumatic avoidance learning: The principles of anxiety conservation and partial irreversibility. *Psychological Review*, 61(6), 353–385. https://doi.org/10.1037/h0054540

## Reference implementation

[`contingency_dsl.annotations.composed.ComposedExtension`](../../../contingency-dsl-py/src/contingency_dsl/annotations/composed/).
