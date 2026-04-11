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
| `@steady_state` | Steady-state criterion for phase termination | `@steady_state(window_sessions=5, max_change_pct=10, measure="rate")` |

Additional keywords under consideration for future minor versions (see
[annotation-design.md §8](../../spec/annotation-design.md) extension proposals):

- `@phase_end(criterion="stability", min_sessions=10)` — explicit phase termination
- `@dependent_measure(measure="rate", window="whole_session")` — primary DV
- `@logging(resolution="10ms", events=[...])` — data recording specification
- `@iri_window(last_n=5)` — inter-reinforcement-interval aggregation window
- `@warmup_exclude(duration=300)` — exclude warmup data from analysis

## Parameter Schemas (v1.x formal specification)

All three v1.x keywords use the **keyword-only** annotation form (no
positional argument). This requires the `keyword_only_form` production in
grammar.ebnf (introduced 2026-04-12 to support natural measurement
annotation syntax).

### `@session_end` — Session termination rule

Declares when a session ends. Supports three termination strategies:
whichever-first, time-only, or reinforcers-only.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `rule` | string enum | Yes | — | Termination strategy: `"first"` (whichever first), `"time_only"`, `"reinforcers_only"` |
| `time` | time value (s/ms/min) | If `rule=first` or `rule=time_only` | — | Maximum session duration |
| `reinforcers` | integer | If `rule=first` or `rule=reinforcers_only` | — | Maximum reinforcer count |

**Semantic constraints:**
- `rule="first"` requires BOTH `time` and `reinforcers`. Missing either → `SESSION_END_MISSING_PARAM`.
- `rule="time_only"` requires `time`, forbids `reinforcers`. Violation → `SESSION_END_INVALID_COMBO`.
- `rule="reinforcers_only"` requires `reinforcers`, forbids `time`. Violation → `SESSION_END_INVALID_COMBO`.
- `time` must be positive. Non-positive → `SESSION_END_NONPOSITIVE_TIME`.
- `reinforcers` must be a positive integer. Non-positive → `SESSION_END_NONPOSITIVE_REINFORCERS`.
- Unknown `rule` value → `SESSION_END_UNKNOWN_RULE`.

**Examples:**

```
@session_end(rule="first", time=60min, reinforcers=60)
-- Session ends when first of: 60 minutes elapsed OR 60 reinforcers delivered

@session_end(rule="time_only", time=60min)
-- Fixed 60-minute session, regardless of reinforcer count

@session_end(rule="reinforcers_only", reinforcers=100)
-- Session terminates after exactly 100 reinforcers, no time limit
```

**Reference:** Baron, A., & Perone, M. (1998). Experimental design and
analysis in the laboratory study of human operant behavior. In K. A.
Lattal & M. Perone (Eds.), *Handbook of research methods in human operant
behavior* (pp. 45-91). Plenum.

### `@baseline` — Baseline measurement declaration

Declares the baseline measurement protocol before experimental training
begins. Used to capture the operant level (Skinner, 1938) of the target
response.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `pre_training_sessions` | integer (≥1) | Yes | — | Number of sessions allocated to baseline measurement |
| `measure` | string enum | No | `"operant_level"` | What to measure during baseline: `"operant_level"` (spontaneous rate, no reinforcer), `"no_training"` (response rate with no contingency), `"custom"` |

**Semantic constraints:**
- `pre_training_sessions` must be a positive integer. Non-positive → `BASELINE_INVALID_SESSIONS`.
- `measure` value outside the enum → `BASELINE_UNKNOWN_MEASURE`.

**Examples:**

```
@baseline(pre_training_sessions=3)
-- 3 pre-training baseline sessions, measuring operant level (default)

@baseline(pre_training_sessions=5, measure="operant_level")
-- Explicit 5-session operant level baseline

@baseline(pre_training_sessions=1, measure="no_training")
-- Single session with no contingency (exposure only)
```

**Reference:** Skinner, B. F. (1938). *The behavior of organisms*.
Appleton-Century-Crofts.

### `@steady_state` — Steady-state criterion for phase termination

Declares when responding is considered stable enough to end a phase and
begin the next. This is the Sidman (1960) *Tactics* steady-state strategy:
phases continue until behavior meets a stability criterion.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `window_sessions` | integer (≥2) | Yes | — | Number of recent sessions evaluated for stability |
| `max_change_pct` | number | Yes | — | Maximum percent change in `measure` across the window (e.g., `10` means ±10%) |
| `measure` | string enum | No | `"rate"` | What to evaluate: `"rate"` (response rate), `"reinforcers"` (reinforcer count), `"iri"` (inter-reinforcement interval), `"latency"`, `"custom"` |
| `min_sessions` | integer (≥1) | No | `window_sessions` | Minimum total sessions in the phase before stability check applies |

**Semantic constraints:**
- `window_sessions` must be ≥ 2. Otherwise → `STEADY_STATE_INVALID_WINDOW`.
- `max_change_pct` must be non-negative. Negative → `STEADY_STATE_NEGATIVE_CHANGE`.
- `min_sessions` must be ≥ `window_sessions`. Otherwise → `STEADY_STATE_INVALID_MIN_SESSIONS`.
- `measure` value outside the enum → `STEADY_STATE_UNKNOWN_MEASURE`.

**Examples:**

```
@steady_state(window_sessions=5, max_change_pct=10)
-- Phase ends when last 5 sessions show <10% change in response rate (default measure)

@steady_state(window_sessions=5, max_change_pct=10, measure="rate", min_sessions=10)
-- Same, but requires at least 10 sessions before checking stability

@steady_state(window_sessions=3, max_change_pct=15, measure="iri")
-- Phase ends when last 3 sessions show <15% change in inter-reinforcement interval
```

**Reference:** Sidman, M. (1960). *Tactics of scientific research: Evaluating
experimental data in psychology*. Basic Books.

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
