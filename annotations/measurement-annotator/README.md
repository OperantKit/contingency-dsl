# measurement-annotator — JEAB Measurement Category

## Status: Proposed (v1.x minimal set, 2026-04-12)

## Purpose

`measurement-annotator` is the recommended annotator module for the
**Measurement** category in the JEAB-aligned taxonomy (see
[design-philosophy.md §4.1](../../spec/ja/design-philosophy.md)).

Measurement annotations declare **when and how the effect of the Core
contingency is read**: session termination rules, steady-state criteria,
baseline measurement conditions, and dependent variable definitions. These
are distinct from Procedure (what the subject experiences), Subjects
(who the subject is), and Apparatus (what physical device is used).

## History

Before 2026-04-12, the Measurement category was defined in design-philosophy
§4.1 but had **no recommended annotator** (DIVERGENCE C in the 2026-04-12
annotation category audit; see
[annotation-design.md §3.6](../../spec/annotation-design.md)).
`measurement-annotator` was introduced during the 2026-04-12 annotator
reorganization to close this gap.

## Keywords (v1.x minimal set)

| Keyword | Purpose | Example |
|---|---|---|
| `@session_end` | Session termination rule | `@session_end(rule="first", time=60min, reinforcers=60)` |
| `@baseline` | Baseline (operant level) measurement | `@baseline(pre_training_sessions=3, measure="operant_level")` |
| `@steady_state` | Steady-state criterion for phase termination | `@steady_state(criterion="5 sessions < 10% change in rate")` |

Additional keywords under consideration for future minor versions (see
[annotation-design.md §8](../../spec/annotation-design.md) extension proposals):

- `@phase_end(criterion="stability", min_sessions=10)` — explicit phase termination
- `@dependent_measure(measure="rate", window="whole_session")` — primary DV
- `@logging(resolution="10ms", events=[...])` — data recording specification
- `@iri_window(last_n=5)` — inter-reinforcement-interval aggregation window
- `@warmup_exclude(duration=300)` — exclude warmup data from analysis

## Boundary Justification

**Can theoretical discussion proceed without this annotator? YES.**

- A `FI 10` schedule can be discussed without declaring when the session
  ends or what counts as stable responding.
- Measurement annotations are about **reading** the effect, not about the
  Core contingency itself.

**Why this annotator belongs in the DSL:**

- Reproducibility requires declaring *when* to stop a session and *what*
  counts as stable data. Informal prose in a Methods section is often
  ambiguous (e.g., "sessions continued until responding was stable").
- Paper compilation needs a source of truth for termination rules, steady-
  state criteria, and dependent measures.
- Without these annotations, two programs running the same DSL source may
  terminate sessions differently or compute different dependent variables,
  breaking the "single source of truth" claim of design-philosophy §1.

## Inclusion Criteria

- Declarations about **when a session or phase ends** (termination rules)
- Declarations about **what counts as stable data** (steady-state criteria)
- Declarations about **what baseline to measure** and how
- Declarations about **which dependent variables** to compute and how

## Exclusion Criteria

- **What the schedule is** → Core DSL (not an annotation)
- **What the reinforcer is** → [procedure-annotator/stimulus](../procedure-annotator/stimulus/README.md) (`@reinforcer`)
- **What the chamber is** → [apparatus-annotator](../apparatus-annotator/README.md) (`@chamber`)
- **Who the subject is** → [subjects-annotator](../subjects-annotator/README.md) (`@species`, `@strain`, etc.)
- **Actual observed behavioral data** → This is runtime / analysis output, not
  a DSL declaration. The DSL declares *what to measure*; the runtime collects
  *the data itself*.

## Recommended Scope

Most measurement annotations are **program-level** (session-wide):

```
@session_end(rule="first", time=60min, reinforcers=60)
@baseline(pre_training_sessions=3)
@steady_state(criterion="5 sessions < 10% change in rate")

FR5 @reinforcer("food")
```

Some may override at schedule level (e.g., different `@dependent_measure`
for different components of a multiple schedule), but this is less common.

## Design Notes

### Why is `@warmup` in procedure-annotator/temporal and not here?

`@warmup` declares that a warm-up period exists (session structure) — this is
a procedural fact. If you additionally want to declare that warm-up data
should be **excluded from analysis**, that is a separate measurement
annotation (`@warmup_exclude`, future). The split follows the principle:
procedure-annotator declares *what happens*, measurement-annotator declares
*what is analyzed*.

### Relationship to validation-modes.md

[spec/validation-modes.md](../../spec/validation-modes.md) defines a tier
system in which some annotations are required only for certain modes
(production, publication). Measurement annotations typically fall into the
**Tier 2 (production)** category: they are not needed for parse or dev
mode, but physical HW execution and publication require them.

## Dependencies

None in v1.x. Future keywords may reference constructs from other annotators
(e.g., `@steady_state` may reference a `@dependent_measure` declaration).

## Open Questions

- Should `@algorithm` (currently in procedure-annotator/temporal) eventually
  move to measurement-annotator? See
  [.local/planning/ANNOTATION_CATEGORY_FOLLOWUPS_2026-04-12.md](../../.local/planning/ANNOTATION_CATEGORY_FOLLOWUPS_2026-04-12.md)
  DIVERGENCE A (note: this file is gitignored; see annotation-design.md §3.6
  for the tracked version of the discussion).
- How should `@session_end` interact with `@phase_end`? One controls the
  session boundary, the other controls phase transitions. They need clear
  ordering semantics.
- Can steady-state criteria be automatically derived from response rate
  data, or must they be declared in advance? The DSL is declarative, so
  *declaration* is required; but the runtime may offer helpers to suggest
  values.

## Python Implementation Reference

`apps/experiment/contingency-annotator/src/contingency_annotator/measurement_annotator/`
(future)
