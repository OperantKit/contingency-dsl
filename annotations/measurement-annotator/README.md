# measurement-annotator — JEAB Measurement Category

## Purpose

Declares **when and how** the effect of the Core contingency is read:
session termination rules, steady-state criteria, baseline measurement
conditions, dependent variable specifications, training volume tracking,
response microstructure analysis, phase termination logic, event logging,
inter-reinforcement interval analysis, and warmup exclusion.

Corresponds to the portion of JEAB Method sections that specifies
measurement parameters — information that belongs to neither Procedure
(what the experimenter arranges) nor Apparatus (what equipment is used)
nor Subjects (who is studied), but rather **how behavioral effects are
quantified and when data collection boundaries are drawn**.

Per [design-philosophy.md §4.2](../../spec/en/design-philosophy.md),
third-party programs are free to reinterpret, extend, or replace this
annotator. This README documents the DSL project's recommended set.

---

## Status

`Stable`

---

## Category

- [x] **Measurement** — steady-state, baseline, phase logic, DV specs

---

## Keywords

| Keyword | Purpose | Example |
|---|---|---|
| `@session_end` | Session termination rule | `@session_end(rule="first", time=60min, reinforcers=60)` |
| `@baseline` | Baseline (operant level) measurement | `@baseline(pre_training_sessions=3, measure="operant_level")` |
| `@steady_state` | Steady-state stability criterion | `@steady_state(window_sessions=5, max_change_pct=10, measure="rate")` |
| `@dependent_measure` | Primary dependent variable declaration | `@dependent_measure(variables=["rate", "irt", "prf_pause"], primary="rate")` |
| `@training_volume` | Cumulative training exposure tracking | `@training_volume(track=["sessions", "reinforcers"], criterion_sessions=20)` |
| `@microstructure` | Response microstructure analysis config | `@microstructure(burst_threshold=0.5s, prf_pause_method="latency_to_first")` |
| `@phase_end` | Compound phase termination criteria | `@phase_end(rule="all", min_sessions=10, stability="steady_state")` |
| `@logging` | Event-level data recording specification | `@logging(events=["response", "reinforcer"], format="jsonl", precision="ms")` |
| `@iri_window` | Inter-reinforcement interval analysis | `@iri_window(bin_width=5s, normalize="proportion", track_preceding_iri=true)` |
| `@warmup_exclude` | Session-onset exclusion for analysis | `@warmup_exclude(duration=5min, scope="analysis")` |
| `@session` | Trial-based session structure (added by R-7 Phase 2) | `@session(trials=72)` / `@session(blocks=6, block_size=12)` |
| `@probe_policy` | Equivalence-probe mixing policy (added by R-7 Phase 2) | `@probe_policy(baseline_reinforced=true, probe_ratio=0.5)` |

All keywords are `program`-scoped (apply to the entire session/program).

---

## Parameter Schemas

The canonical machine-readable schema is
[`schema/annotations/measurement.schema.json`](../../schema/annotations/measurement.schema.json).
Below is a human-readable summary of each keyword's parameters.

### `@session_end`

Session termination rule. Declares when a session ends.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `rule` | `string` enum: `"first"`, `"time_only"`, `"reinforcers_only"` | YES | Termination strategy |
| `time` | `time_value` | if rule in `[first, time_only]` | Maximum session duration |
| `reinforcers` | `integer` (>= 1) | if rule in `[first, reinforcers_only]` | Maximum reinforcer count |

**Conditional constraints:**
- `rule="time_only"` forbids `reinforcers`
- `rule="reinforcers_only"` forbids `time`

**Reference:** Baron, A., & Perone, M. (1998). Experimental design and analysis in the laboratory study of human operant behavior. In K. A. Lattal & M. Perone (Eds.), *Handbook of research methods in human operant behavior* (pp. 45-91). Plenum.

### `@baseline`

Baseline measurement declaration. Captures the operant level of the target
response before experimental training.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `pre_training_sessions` | `integer` (>= 1) | YES | — | Number of baseline sessions |
| `measure` | `string` enum: `"operant_level"`, `"no_training"`, `"custom"` | no | `"operant_level"` | What to measure |

**Reference:** Skinner, B. F. (1938). *The behavior of organisms*. Appleton-Century-Crofts.

### `@steady_state`

Steady-state criterion for phase termination. Declares when responding is
considered stable enough to end a phase.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `window_sessions` | `integer` (>= 2) | YES | — | Sessions evaluated for stability |
| `max_change_pct` | `number` (>= 0) | YES | — | Maximum percent change (e.g., 10 = +/-10%) |
| `measure` | `string` enum: `"rate"`, `"reinforcers"`, `"iri"`, `"latency"`, `"custom"` | no | `"rate"` | What to evaluate |
| `min_sessions` | `integer` (>= 1) | no | `window_sessions` | Minimum sessions before check applies |

**Reference:** Sidman, M. (1960). *Tactics of scientific research: Evaluating experimental data in psychology*. Basic Books.

### `@dependent_measure`

Primary dependent variable declaration. Specifies which behavioral measures
are recorded, reported, and analyzed.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `variables` | `array` of `string` (minItems: 1) | YES | Dependent variables to record |
| `primary` | `string` | no | Which variable is primary (defaults to first) |

**Variable enum:** `rate`, `irt`, `prf_pause`, `latency`, `bout_rate`, `bout_length`, `within_bout_rate`, `running_rate`, `reinforcers`, `consumption`, `response_rate_ratio`, `peak_time`, `spread`, `cv`, `breakpoint`, `demand_elasticity`, `suppression_ratio`, `changeover_rate`, `custom`

**Reference:** Johnston, J. M., & Pennypacker, H. S. (2009). *Strategies and tactics of behavioral research* (3rd ed.). Routledge.

### `@training_volume`

Cumulative training exposure tracking. Critical for overtraining paradigms
and habit formation research.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `track` | `array` of `string` enum: `"sessions"`, `"responses"`, `"reinforcers"` (minItems: 1) | YES | Metrics to track |
| `criterion_sessions` | `integer` (>= 1) | no | Session count threshold for overtraining |
| `criterion_responses` | `integer` (>= 1) | no | Response count threshold |
| `criterion_reinforcers` | `integer` (>= 1) | no | Reinforcer count threshold |

**Reference:** Adams, C. D., & Dickinson, A. (1981). Instrumental responding following reinforcer devaluation. *Quarterly Journal of Experimental Psychology*, *33B*(2), 109-121. https://doi.org/10.1080/14640748108400816

### `@microstructure`

Response microstructure measurement parameters. Configures fine-grained
temporal analysis of response patterns.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `irt_bin_width` | `time_value` | no | adaptive | IRT histogram bin width |
| `burst_threshold` | `time_value` | no | — | Within-bout IRT threshold |
| `prf_pause_method` | `string` enum: `"latency_to_first"`, `"latency_to_nth"`, `"quarter_life"` | no | `"latency_to_first"` | PRF pause measurement method |
| `prf_pause_n` | `integer` (>= 2) | if method = `latency_to_nth` | — | Response count for nth method |
| `report` | `array` of `string` | no | — | Analyses to include in reports |

**Report enum:** `irt_distribution`, `bout_statistics`, `prf_pause`, `run_length`, `changeover`, `log_survivor`, `scallop_index`, `reinforcement_proximity`

**Reference:** Shull, R. L., Gaynor, S. T., & Grimes, J. A. (2001). Response rate viewed as engagement bouts: Effects of rate of reinforcement. *Journal of the Experimental Analysis of Behavior*, *75*(3), 247-274. https://doi.org/10.1901/jeab.2001.75-247

### `@phase_end`

Compound phase termination criteria. Unlike `@session_end` (individual sessions)
and `@steady_state` (stability evaluation), `@phase_end` specifies when the
experimental phase as a whole terminates.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `rule` | `string` enum: `"all"`, `"any"`, `"first"` | YES | How criteria combine |
| `min_sessions` | `integer` (>= 1) | no | Minimum sessions before termination |
| `max_sessions` | `integer` (>= 1) | no | Maximum sessions (hard cap) |
| `stability` | `string` enum: `"steady_state"`, `"custom"` | no | Reference to stability criterion |
| `min_reinforcers` | `integer` (>= 1) | no | Minimum cumulative reinforcers |
| `cv_threshold` | `number` (>= 0) | no | Maximum CV of primary DV |

**Reference:** Sidman, M. (1960). *Tactics of scientific research: Evaluating experimental data in psychology*. Basic Books.

### `@logging`

Event-level data recording specification. Controls the granularity of data
available for post-hoc analysis.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `events` | `array` of `string` (minItems: 1) | YES | — | Event types to record |
| `format` | `string` enum: `"jsonl"`, `"csv"`, `"medpc"` | no | `"jsonl"` | Output format |
| `precision` | `string` enum: `"ms"`, `"us"`, `"ns"` | no | `"ms"` | Timestamp precision |

**Event enum:** `response`, `reinforcer`, `stimulus_onset`, `stimulus_offset`, `schedule_state`, `timer_tick`, `phase_change`, `session_marker`

**Reference:** Tatham, T. A., & Zurn, K. R. (1989). The MED-PC experimental apparatus programming system. *Behavior Research Methods, Instruments, & Computers*, *21*(2), 294-299. https://doi.org/10.3758/BF03205598

### `@iri_window`

Inter-reinforcement interval (IRI) aggregation window specification.
Critical for timing research where IRI serves as an implicit temporal cue
distinct from the nominal schedule parameter.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `bin_width` | `time_value` | no | adaptive | IRI distribution bin width |
| `normalize` | `string` enum: `"none"`, `"proportion"`, `"rate"` | no | `"none"` | Normalization method |
| `track_preceding_iri` | `boolean` | no | `false` | Record preceding IRI as covariate |
| `report` | `array` of `string` | no | — | IRI analyses to report |

**Report enum:** `distribution`, `mean`, `median`, `cv`, `sequential`

**Reference:** Catania, A. C., & Reynolds, G. S. (1968). A quantitative analysis of the responding maintained by interval schedules of reinforcement. *Journal of the Experimental Analysis of Behavior*, *11*(S3), 327-383. https://doi.org/10.1901/jeab.1968.11-s327

### `@warmup_exclude`

Warmup exclusion declaration. Specifies an initial period of each session to
exclude from dependent variable calculations.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `duration` | `time_value` | YES | — | Exclusion duration from session start |
| `scope` | `string` enum: `"analysis"`, `"logging_and_analysis"` | no | `"analysis"` | What to exclude |

**Reference:** Ferster, C. B., & Skinner, B. F. (1957). *Schedules of reinforcement*. Appleton-Century-Crofts.

### `@session` (R-7 Phase 2)

Trial-based session structure declaration. Specifies the structural/volumetric
organization of trials per session — distinct from `@session_end` (which
specifies termination rules). Used primarily for MTS / GoNoGo / DMTS and other
trial-based procedures.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `trials` | `integer` (≥ 1) | required unless `blocks` given | — | Total trials per session |
| `blocks` | `integer` (≥ 1) | no | — | Number of trial blocks per session (requires `block_size`) |
| `block_size` | `integer` (≥ 1) | required if `blocks` given | — | Trials per block (Arntzen 2012: modal 18–36) |

**Consistency constraint:** when all three are given, `trials = blocks × block_size` must hold (`SESSION_BLOCK_TRIALS_MISMATCH` otherwise).

**Co-existence with `@session_end`:** both may be declared. Runtime terminates
on whichever occurs first (OR semantics). Triggers WARNING
`SESSION_OVERLAPS_SESSION_END`.

**Reference:** Arntzen, E. (2012). Training and testing parameters in formation of stimulus equivalence: Methodological issues. *European Journal of Behavior Analysis*, 13(1), 123-135. https://doi.org/10.1080/15021149.2012.11434412

### `@probe_policy` (R-7 Phase 2)

Probe/baseline trial-mixing policy for stimulus-equivalence testing.
Supersedes the weakly-defined `@test_criterion.baseline_reinforced`
(alias retained for backward compatibility).

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `baseline_reinforced` | `boolean` | no | `true` | Whether baseline trials continue to receive training consequence during probe session |
| `probe_ratio` | `real` (0.0–1.0) | no | `0.5` | Fraction of session trials that are probes |
| `interspersed` | `boolean` | no | `true` | `true` = trial-level random mix; `false` = block-level separation |
| `order` | `string` enum: `"random"`, `"blocked"`, `"progressive"` | no | `"random"` | Ordering regime |

**Consistency constraint:** `interspersed=true` conflicts with `order="blocked"` (`PROBE_POLICY_INCONSISTENT_INTERSPERSED_ORDER`).

**Reference:** Fields, L., Reeve, K. F., Rosen, D., Varelas, A., Adams, B. J., Belanich, J., & Hobbie, S. A. (1997). Using the simultaneous protocol to study equivalence class formation. *JEAB*, 67(3), 367-389. https://doi.org/10.1901/jeab.1997.67-367

---

## Boundary Justification

**Is this annotation necessary for theoretical discussion: NO**

A schedule's theoretical properties (e.g., FI scallop, matching in
concurrent VI VI) can be discussed without specifying session termination
rules or steady-state criteria. These are measurement decisions, not
contingency definitions.

**Why this annotation should reside within the DSL:**

1. **Reproducibility**: Session termination rules and steady-state criteria
   are essential for replicating experiments. Without `@session_end`, two
   implementations of the same schedule could produce incomparable data.
2. **Compilability**: A paper-compiler can generate the Measurement subsection
   of JEAB Method sections directly from these annotations.
3. **Validation**: Cross-referencing `@phase_end(stability="steady_state")`
   against the presence of `@steady_state` catches specification errors
   at compile time rather than at runtime.

---

## Inclusion Criteria

Information about **when to stop collecting data** and **what to measure**:

- Session termination rules (time, reinforcer count, or compound)
- Phase termination criteria (stability, session count, CV thresholds)
- Steady-state stability criteria
- Baseline measurement conditions
- Dependent variable declarations
- Training volume tracking thresholds
- Response microstructure analysis parameters
- Event logging specifications
- Inter-reinforcement interval analysis configuration
- Warmup exclusion periods

## Exclusion Criteria

- **Procedure**: How the contingency is arranged (schedule parameters,
  stimulus identity, temporal parameters). Goes to `procedure-annotator`.
- **Apparatus**: Physical equipment identity and hardware binding.
  Goes to `apparatus-annotator`.
- **Subjects**: Who is studied and under what establishing operations.
  Goes to `subjects-annotator`.
- **Runtime implementation**: How a simulator implements the schedule
  (e.g., random number generation algorithm). `@algorithm` is Procedure;
  §4.3 of design-philosophy.md permits Measurement-oriented
  reinterpretation by third-party programs.
- **Automatic judgment execution**: The `@steady_state` annotation
  **declares** a criterion; the **automatic execution** of that judgment
  is the responsibility of session-analyzer, not the DSL.

---

## Boundary Review Checklist

All 10 keywords pass the following boundary tests:

### 1. Core independence (boundary-decision.md Phase A)

- [x] Q1: Can the schedule's theoretical properties be discussed without these keywords? **YES** — FI scallop, matching law, etc. do not require session termination or stability criteria.
- [x] Q2: Do these keywords alter evaluation semantics of schedule expressions? **NO** — `FR 5` evaluates identically with or without `@session_end`.
- [x] Q3: Can these keywords be mandatory at the Core grammar level? **NO** — They are program-registry decisions, not universal requirements.

### 2. Category fit

- [x] All keywords are consistent with the Measurement category.
- [x] All keywords address the single dimension: "when/how to quantify behavioral effects."
- [x] No keyword conflicts with other recommended annotators.

### 3. Necessity for recommendation

- [x] External-only expression (comments) is insufficient for machine-readable reproducibility.
- [x] Compilation targets (JEAB paper generation, session-analyzer) benefit directly.
- [x] All 10 keywords merit inclusion in the recommended set for basic EAB research.

---

## Dependencies

None. measurement-annotator is orthogonal to all other annotators.

Cross-reference note: `@phase_end(stability="steady_state")` semantically
references `@steady_state` within the same program. This is an intra-annotator
reference, not a dependency on another annotator.

---

## Implementation Reference

- **Schema**: [`schema/annotations/measurement.schema.json`](../../schema/annotations/measurement.schema.json)
- **Conformance tests**: [`conformance/annotations/measurement.json`](../../conformance/annotations/measurement.json)
- **Error tests**: [`conformance/annotations/errors.json`](../../conformance/annotations/errors.json)
- **Reference implementation**: `apps/experiment/contingency-annotator/src/contingency_annotator/measurement_annotator/` (planned)
