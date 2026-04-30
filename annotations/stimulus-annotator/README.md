# stimulus-annotator — Stimulus Identity Dimension

## Purpose

Declares the **identity of stimuli** that participate in a contingency:
which physical events serve as reinforcers (unconditioned, conditioned,
or generalized), which exteroceptive events function as discriminative
stimuli, which response devices the subject contacts, and which brief
stimuli punctuate components of a second-order schedule.

Corresponds to the stimulus-identity portion of a JEAB Procedure section
(architecture.md §4.7): the base schedule grammar specifies only the
abstract structure of reinforcement (e.g. `FR 5`); the stimulus-annotator
binds that structure to named events in the experimental world. This
separation keeps the schedule expression theoretical (analyzable in terms
of matching, scallops, etc.) while letting a single program be wired to
concrete reinforcers, signals, and operanda.

This annotator is part of the **core recommended vocabulary** maintained
by the DSL project. Per
[design-philosophy.md §4.2](../../spec/en/design-philosophy.md), third-party
programs retain the freedom to reinterpret or replace these categories, but
the DSL project supplies and maintains the reference implementation in
[`contingency-dsl-py`](../../../contingency-dsl-py/) (sole reference implementation).

---

## Status

`Stable`

---

## Category

- [x] **Procedure** — stimulus identity (reinforcers, SDs, operanda, brief stimuli)

---

## Keywords

| Keyword | Purpose | Example |
|---|---|---|
| `@reinforcer` | Declares a reinforcer with type and (for conditioned/generalized) backup chain | `@reinforcer("tone", type="conditioned", backup="food", alpha0=0.3)` |
| `@sd` | Binds a discriminative stimulus to a schedule (or a Mult/Mix component) | `@sd("red_light", component=1)` |
| `@operandum` | Names a response device (lever, key, nose-poke) attached to a schedule | `@operandum("left_lever")` |
| `@brief` | Specifies the brief stimulus terminating a unit schedule in a second-order schedule | `@brief("light", duration=2)` |

## Scope and attachment

`@reinforcer` is **program-level** by convention (a reinforcer named once
applies wherever it is referenced). `@sd`, `@operandum`, and `@brief` are
**schedule-level**: they attach postfix to a schedule expression and
surface in the AST inside an `AnnotatedSchedule` node wrapping the
schedule. The schedule-level binding is what permits divergent stimuli
across components of a `Conc` or `Mult` without ambiguity.

## Validation rules

The `validate()` pass enforces three rules over the collected
`ReinforcerAnnotation` set:

1. **Conditioned reinforcers must specify a backup.** A `@reinforcer`
   declared with `type="conditioned"` and an empty `backup` chain is
   rejected: a conditioned reinforcer is defined by its pairing relation
   to a backup, so the DSL refuses to model an unsupported one.
2. **Generalized reinforcers require at least two backups.** The
   defining property of a generalized conditioned reinforcer is
   association with multiple backup reinforcers; fewer than two collapses
   the construct to an ordinary conditioned reinforcer.
3. **Referential integrity.** Every name appearing in a `backup=` field
   must itself be declared as a `@reinforcer` somewhere in the program.
   Dangling backup references are rejected.

## Disjointness

The four keywords are independent declarations and may co-occur freely on
the same schedule. There is no mutual exclusion within stimulus-annotator
itself. Cross-annotator constraints (e.g. apparatus binding for
`@operandum`) are enforced at the integration layer, not here.

## References

- Skinner, B. F. (1938). *The behavior of organisms.* Appleton-Century-Crofts.
- Wolfe, J. B. (1936). Effectiveness of token rewards for chimpanzees. *Comparative Psychology Monographs*, 12(5), 1–72.
- Williams, B. A. (1994). Conditioned reinforcement: Experimental and theoretical issues. *The Behavior Analyst*, 17(2), 261–285. https://doi.org/10.1007/BF03392675

## Reference implementation

[`contingency_dsl.annotations.stimulus.StimulusExtension`](../../../contingency-dsl-py/src/contingency_dsl/annotations/stimulus/).
