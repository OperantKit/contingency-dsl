# Phase Sequence — First-Class Multi-Phase Experimental Design

> Part of the contingency-dsl experiment layer. Defines the `PhaseSequence` construct, the `Phase` element and its annotation inheritance rules, the `no_schedule` phase variant, and the JEAB-aligned Method-section conventions that motivate the design. This file is the human-facing specification; the corresponding JSON Schema is `schema/experiment/phase-sequence.schema.json`.

**Companion documents:**
- [Experiment / Paper](paper.md) — Experiment and Paper wrappers for multi-experiment publications.
- [Experiment / Context](context.md) — first-class Context and its interaction with phase sequencing.
- [Experiment / Criteria](criteria.md) — phase-change criteria (`Stability`, `FixedSessions`, `PerformanceCriterion`, `CumulativeReinforcements`, `ExperimenterJudgment`).
- [Respondent Primitives](../respondent/primitives.md) — respondent primitives that appear in phases.
- [Operant Grammar](../operant/grammar.md) — operant productions that appear in phases.
- [Composed / PIT](../composed/pit.md) — a canonical multi-phase composed procedure.

---

## 1. Rationale

JEAB papers and related EAB publications describe experimental procedures phase-by-phase in the Procedure section: an Acquisition phase followed by an Extinction phase, a Baseline followed by a Treatment and a Reversal, and so on. Individual contingencies do not capture the temporal ordering of phases or the declarative nature of phase-change criteria. The experiment layer elevates this multi-phase structure to a first-class construct.

A `PhaseSequence` is an ordered sequence of phases, each with its own schedule (operant) and / or respondent expression and an optional phase-change criterion. The final phase is terminal — it has no criterion because the experiment ends at its completion.

## 2. The `PhaseSequence` Construct

```
PhaseSequence(
  shared_annotations = [...],           -- inherited by every phase
  shared_param_decls = [...],            -- inherited by every phase
  phases = [Phase1, Phase2, ..., PhaseN]
)
```

A `PhaseSequence` has at least two phases; a single-phase experiment is just a bare `Program` (see `foundations/grammar.md §2`).

### 2.1 Shared vs Per-Phase Annotations

The JEAB Method section typically describes Subjects and Apparatus once at the beginning of Procedure and then describes each phase sequentially. The DSL mirrors this convention:

- **Shared annotations** (Subjects, Apparatus, and general Procedure) are attached to the `PhaseSequence` and inherited by every phase.
- **Per-phase annotations** (phase-specific Procedure details, phase-specific Measurement) are attached to individual `Phase` nodes and override shared annotations by keyword when the same annotation name appears in both.

The inheritance is a plain keyword-level override: if the shared level defines `@context(location="room_A")` and a phase defines `@context(location="room_B")`, the phase uses `room_B`. If a phase adds `@renewal_test` without a shared counterpart, it is simply added for that phase only.

### 2.2 The `no_schedule` Phase Variant

Some phases have no operant contingency. Pavlovian revaluation, context exposure, habituation, and certain recovery interventions present stimuli or let context conditions operate without any programmed response–consequence relation. The DSL expresses this by allowing `Phase.schedule = null`:

```
Phase(
  label = "context_exposure",
  schedule = null,                        -- no operant contingency
  phase_annotations = [@context(location="room_B")],
  criterion = FixedSessions(count=3)
)
```

Respondent expressions may still be attached; annotations (`@cs`, `@us`, `@context`) may still describe stimulus presentations. The `null` indicates only the absence of the operant layer, not the absence of events.

## 3. The `Phase` Element

```
Phase(
  label = <string>,
  schedule = <ScheduleExpr> | <RespondentExpr> | null,
  phase_annotations = [...],
  phase_param_decls = [...],
  criterion = <Criterion>?         -- absent on terminal phase
)
```

`label` is the human-readable phase name used in JEAB Procedure sections: Acquisition, Extinction, Reversal, Renewal Test, Baseline, Treatment, Probe, and so on. The label is metadata for the reader; it does not participate in the grammar's static verification.

`schedule` may be an operant `ScheduleExpr` (e.g., `VI 60-s`), a respondent expression (e.g., `Pair.ForwardDelay(tone, shock, isi=10-s, cs_duration=15-s)`), or composed expressions admitted by the composed layer. Each phase carries a single schedule body. CER-like procedures that combine an operant baseline with a Pavlovian overlay are encoded as a sequence of phases (baseline → pairing → test) rather than a single phase carrying two parallel schedules; see `../composed/conditioned-suppression.md` for the canonical encoding.

`criterion` is required on non-terminal phases and absent on the terminal phase. See `criteria.md` for the criterion catalog.

## 4. Phase Transition Criteria Syntax

Each non-terminal phase specifies how the experiment moves to the next phase:

```
criterion = Stability(window_sessions=5, max_change_pct=10, measure="rate")
criterion = FixedSessions(count=10)
criterion = PerformanceCriterion(measure="rate", threshold=1.0, op="<", window_sessions=3)
criterion = CumulativeReinforcements(count=300)
criterion = ExperimenterJudgment
```

The criterion is declarative and is enumerated in the schema — a program evaluates the criterion by tracking the relevant measure across sessions and advances the phase when the criterion resolves to true. See `criteria.md` for precise semantics.

## 5. JEAB Convention Notes

1. **Shared → per-phase override by keyword.** The DSL convention (`phase_annotations` override `shared_annotations` by keyword) matches the reading order of JEAB Procedure sections: first the general Subjects / Apparatus / Procedure, then each phase's specifics.
2. **Steady-state logic is the default.** Sidman (1960) argues that phase transitions should be based on the behavior itself — on steady-state stability — rather than on fixed session counts where possible. `Stability` is therefore the most common criterion in JEAB basic research, with `FixedSessions` reserved for extinction and probe / test phases where stability is not the goal.
3. **The terminal phase has no criterion.** The experiment's end is defined by reaching the terminal phase, not by a criterion on that phase.
4. **Annotation categories follow the JEAB Method headings.** The DSL annotation categories — Subjects, Apparatus, Procedure, Measurement — are shared-annotation defaults; per-phase annotations typically override Procedure and (sometimes) Measurement, while Subjects and Apparatus almost always remain at the shared level.

## 6. Relationship to the Existing Schema

The authoritative machine-readable form of this specification lives in `schema/experiment/phase-sequence.schema.json`. That schema defines the exact JSON shapes for `PhaseSequence`, `Phase`, and all `Criterion` variants, including constraint details (minimum session counts, measure enumerations, operator enumerations). The present file is the human-facing prose counterpart and is authoritative for the conceptual design; the schema is authoritative for the exact serialized form.

## 7. Example — A Simple Reversal Design

```
PhaseSequence(
  shared_annotations = [
    @subjects(species="rat", n=8),
    @apparatus(chamber="operant_chamber_1")
  ],
  phases = [
    Phase(
      label = "Baseline",
      schedule = VI 60-s,
      criterion = Stability(window_sessions=5, max_change_pct=10, measure="rate")
    ),
    Phase(
      label = "Reversal_1",
      schedule = VI 120-s,
      criterion = Stability(window_sessions=5, max_change_pct=10, measure="rate")
    ),
    Phase(
      label = "Reversal_2",
      schedule = VI 60-s         -- terminal; no criterion
    )
  ]
)
```

This encodes the Method-section description "Subjects were 8 rats trained in operant chamber 1 on a VI 60-s baseline; once responding stabilized (within 10% across 5 consecutive sessions), the schedule was changed to VI 120-s; after stability, the schedule reverted to VI 60-s."

## References

- Sidman, M. (1960). *Tactics of scientific research*. Basic Books.
