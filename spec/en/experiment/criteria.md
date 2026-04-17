# Phase-Change Criteria

> Part of the contingency-dsl experiment layer. Specifies the catalog of phase-change criteria — declarative conditions under which one phase ends and the next begins. The criterion set is an enumerated, non-TC family: `Stability`, `FixedSessions`, `PerformanceCriterion`, `CumulativeReinforcements`, `ExperimenterJudgment`. Runtime-conditioned criteria beyond this catalog (e.g., rate-based schedule switching) belong in `contingency-core`, not in the experiment layer.

**Companion documents:**
- [Experiment / Phase Sequence](phase-sequence.md) — where criteria attach.
- [Experiment / Context](context.md) — criterion interaction with context changes.
- Schema: `schema/experiment/phase-sequence.schema.json` — authoritative criterion shape definitions.

---

## 1. Rationale for an Enumerated Criterion Family

Sidman (1960) argues that steady-state logic is the proper foundation for phase-transition decisions in the experimental analysis of behavior: phase transitions should depend on the behavior's reaching a stable, replicable level rather than on arbitrary externally imposed time constraints. JEAB and related EAB publications generally follow this convention, but recognize that extinction phases, probe / test phases, and applied research settings sometimes require non-stability criteria.

The criterion family below enumerates the standard JEAB conventions. The family is closed (additive extensions follow design-philosophy §8.1) and declarative — each criterion is fully specified by literal parameters at parse time, and a program evaluates it by tracking the relevant measure across sessions. No criterion admits arbitrary runtime computation.

## 2. `Stability` — Steady-State Criterion

The most common criterion in JEAB basic research. A phase ends when a specified behavioral measure varies by less than a specified tolerance across a specified window of consecutive sessions.

```
Stability(window_sessions=5, max_change_pct=10, measure="rate", min_sessions=20)
```

**Parameters:**
- `window_sessions` — number of consecutive sessions across which variability is evaluated. Must be ≥ 2.
- `max_change_pct` — maximum percent change in the measured variable across the window. `10` means "≤ 10% variation."
- `measure` — which behavioral measure to evaluate. Enumerated: `rate` (responses per unit time), `iri` (inter-reinforcement interval), `latency` (response latency), `reinforcers` (reinforcements per session).
- `min_sessions` — minimum total sessions in the phase before the stability check can succeed. Prevents premature phase changes when initial variability is low for artifactual reasons.

**Example JEAB phrasing.** "Stability was judged when response rate varied less than 10% across 5 consecutive sessions, with a minimum of 20 sessions."

**Citation.** Sidman, M. (1960). *Tactics of scientific research*. Basic Books.

## 3. `FixedSessions` — Fixed Session Count

The phase lasts exactly `count` sessions regardless of behavior. Common in extinction phases (where stability of the decrement is not the goal) and in probe / test phases (where a fixed number of test trials is prescribed).

```
FixedSessions(count=10)
```

**Parameter:**
- `count` — number of sessions in the phase.

**Example JEAB phrasing.** "This phase lasted 10 sessions."

## 4. `PerformanceCriterion` — Behavior-Dependent Threshold

A phase ends when a specified measure crosses a threshold in a specified direction. Common in discrimination-training and applied research.

```
PerformanceCriterion(measure="rate", threshold=1.0, op="<", window_sessions=3)
```

**Parameters:**
- `measure` — behavioral measure. Enumerated: `rate`, `count`, `latency`, `iri`.
- `threshold` — numeric threshold.
- `op` — comparison operator: `<`, `<=`, `>`, `>=`.
- `window_sessions` — number of consecutive sessions the criterion must be met in. Default is 1 (single session suffices).

**Example JEAB phrasing.** "Until responding fell below 1 response per minute for 3 consecutive sessions."

## 5. `CumulativeReinforcements` — Total-Reinforcer Threshold

A phase ends after a cumulative number of reinforcers has been delivered across sessions. Common when training duration must be calibrated to reinforcement experience rather than time.

```
CumulativeReinforcements(count=300)
```

**Parameter:**
- `count` — total reinforcers across all sessions in the phase.

**Example JEAB phrasing.** "Training continued until 300 reinforcers were earned."

## 6. `ExperimenterJudgment` — Discretionary

The phase ends at the experimenter's discretion; there is no formal criterion. Common in older JEAB literature and in applied settings where protocol design admits discretionary decisions.

```
ExperimenterJudgment
```

**No parameters.**

**Example JEAB phrasing.** "Phase changes were made at the experimenter's discretion."

**Note.** `ExperimenterJudgment` is admitted because it is a genuine JEAB convention, not because it is recommended. Encoding a procedure with this criterion makes the discretionary nature of the phase transition explicit in the DSL, which is itself a form of methodological transparency.

## 7. Terminal Phase Convention

The terminal (last) phase of a `PhaseSequence` has **no criterion**. The experiment ends at the completion of the terminal phase. A program that encounters a terminal phase with a criterion field should emit a validation error; this is enforced at the schema level (`schema/experiment/phase-sequence.schema.json`).

## 8. Why the Catalog Is Closed

The experiment layer is non-TC by design (design-philosophy §2, architecture.md §4.1). Admitting arbitrary runtime-computed criteria — for example, criteria that depend on continuous monitoring of response rate with a switching rule — would push the experiment layer into Turing-complete territory. Such dynamic schedule transitions belong in `contingency-core`, which is explicitly TC and lives as a sibling package. The experiment layer handles the standard JEAB conventions declaratively; anything beyond those conventions escalates to `contingency-core`.

Additional criteria may be added to this catalog through the additive procedure in design-philosophy §8.1: the addition must not modify existing criterion semantics and must be specifiable as a declarative predicate over per-session measures.

## References

- Sidman, M. (1960). *Tactics of scientific research*. Basic Books.
