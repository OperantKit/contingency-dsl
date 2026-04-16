# Differential Reinforcement Schedules — DRO, DRL, DRH, DRA, DRI

> Part of the contingency-dsl operant layer. Reinforcement schedules that gate reinforcement on temporal properties of the response stream (inter-response time, response absence) rather than response count or elapsed time.

---

## 1. Scope

Differential reinforcement (DR) schedules sit orthogonally to the 3×3 atomic grid. They are **constraint schedules** or **modifiers** that can be composed with grid schedules via tandem or conjunctive arrangements. The DSL represents DRL/DRH/DRO as modifier expressions (see `operant/grammar.md §1.3`); DRA and DRI are patterns over concurrent arrangements.

```
DRConstraint ::= DRL(irt_min : ℝ⁺)       -- IRT ≥ threshold
               | DRH(irt_max : ℝ⁺)       -- IRT ≤ threshold
               | DRO(omission_time : ℝ⁺)  -- no response for duration
```

## 2. DRL — Differential Reinforcement of Low Rate

**Definition.** A response is reinforced iff its inter-response time (IRT) is ≥ `t` seconds. The primary procedural use is to establish low response rates by differentially reinforcing long IRTs.

```
DRL 5-s              -- IRT ≥ 5 s is reinforceable
Tand(VR 20, DRL 5-s) -- tandem composition: VR 20 count AND IRT ≥ 5 s
```

Standalone `DRL t` is semantically equivalent to `Tand(CRF, DRL t)`: every response satisfying the IRT criterion is reinforced (Ferster & Skinner, 1957, Ch. 8).

Canonical references:
- Ferster, C. B., & Skinner, B. F. (1957). *Schedules of reinforcement*. Appleton-Century-Crofts. (Ch. 8: original DRL formalization)
- Kramer, T. J., & Rilling, M. (1970). Differential reinforcement of low rates: A selective critique. *Psychological Bulletin*, 74(4), 225–254. https://doi.org/10.1037/h0029813

## 3. DRH — Differential Reinforcement of High Rate

**Definition.** A response is reinforced iff its IRT is ≤ `t` seconds — i.e., the response occurred within `t` seconds of the previous one. Used to establish high response rates.

```
DRH 2-s              -- IRT ≤ 2 s is reinforceable
```

## 4. DRO — Differential Reinforcement of Other Behavior

**Definition.** A reinforcer is delivered if the target response is *absent* for a duration of `t` seconds (Reynolds, 1961). The procedural name is historically misleading: the effect depends primarily on the omission/extinction component rather than on reinforcing "other" behavior.

```
DRO 10-s             -- no target response for 10 s → reinforcement
```

**Evidence for the "omission" interpretation.** Mazaleski, Iwata, Vollmer, Zarcone, and Smith (1993) separated the reinforcement and omission components and demonstrated that DRO's effectiveness depends primarily on the omission contingency. Rey, Betz, Sleiman, Kuroda, and Podlesnik (2020a, 2020b) replicated and extended this finding. Hronek and Kestner (2025) further examined asymmetry between commission and omission errors under DRO.

**Whole-interval vs variable-momentary DRO.** Lindberg, Iwata, Kahng, and DeLeon (1999) established a 2×2 taxonomy for DRO procedures (whole-interval vs momentary; fixed vs variable). The current DSL represents fixed whole-interval DRO; the 2×2 taxonomy is deferred to a future additive checkpoint.

Canonical references:
- Reynolds, G. S. (1961). Behavioral contrast. *Journal of the Experimental Analysis of Behavior*, 4(1), 57–71. https://doi.org/10.1901/jeab.1961.4-57
- Mazaleski, J. L., Iwata, B. A., Vollmer, T. R., Zarcone, J. R., & Smith, R. G. (1993). Analysis of the reinforcement and extinction components in DRO contingencies with self-injury. *Journal of Applied Behavior Analysis*, 26(2), 143–156. https://doi.org/10.1901/jaba.1993.26-143
- Lindberg, J. S., Iwata, B. A., Kahng, S., & DeLeon, I. G. (1999). DRO contingencies: An analysis of variable-momentary schedules. *Journal of Applied Behavior Analysis*, 32(2), 123–136. https://doi.org/10.1901/jaba.1999.32-123
- Rey, C. N., Betz, A. M., Sleiman, A. A., Kuroda, T., & Podlesnik, C. A. (2020a). The role of adventitious reinforcement during differential reinforcement of other behavior: A systematic replication. *Journal of Applied Behavior Analysis*, 53(4), 2440–2449. https://doi.org/10.1002/jaba.678
- Rey, C. N., Betz, A. M., Sleiman, A. A., Kuroda, T., & Podlesnik, C. A. (2020b). Adventitious reinforcement during long-duration DRO exposure. *Journal of Applied Behavior Analysis*, 53(3), 1716–1733. https://doi.org/10.1002/jaba.697
- Hronek, L. M., & Kestner, K. M. (2025). A human-operant evaluation of commission and omission errors during differential reinforcement of other behavior. *Journal of Applied Behavior Analysis*. https://doi.org/10.1002/jaba.70003

## 5. DRA — Differential Reinforcement of Alternative Behavior

**Definition (DRA).** Extinction for the target response, reinforcement for a specified alternative response. A clinical procedure commonly used in applied behavior analysis (Cooper, Heron, & Heward, 2020).

Unlike DRO/DRL/DRH (single-operandum modifiers defined by temporal parameters), DRA inherently specifies contingencies across **two** response classes. At the schedule level, DRA is expressible as a concurrent arrangement:

```
let dra = Conc(EXT, CRF)           -- target extinct, alternative continuously reinforced
let dra_vi = Conc(EXT, VI 30-s)    -- target extinct, alternative on VI 30
```

## 6. DRI — Differential Reinforcement of Incompatible Behavior

**Definition (DRI).** A special case of DRA where the alternative behavior is physically incompatible with the target (Cooper, Heron, & Heward, 2020). The schedule structure is identical to DRA; the distinction is topographical (which behavior serves as alternative).

DRA and DRI are **documented patterns** in contingency-dsl, not primitive constructors. The topographical distinction is delegated to the annotation layer (e.g., `@target`, `@replacement` in `extensions/clinical-annotator`).

## 7. Compositions

DR modifiers are composable with grid schedules and combinators:

```
Tand(VR 20, DRL 5-s)       -- ratio requirement AND IRT requirement
Mult(DRL 5-s, DRL 1-s)     -- alternating IRT requirements across components
Chain(FR 5, DRO 10-s)      -- FR 5 then DRO 10
```

Standalone DR modifiers are interpreted with an implicit CRF base: `DRL 5-s ≡ Tand(CRF, DRL 5-s)` (`operant/theory.md §1.4`).

## 8. Errors and Warnings

| Code | Condition | Severity |
|---|---|---|
| `DR_NONPOSITIVE_VALUE` | `t ≤ 0` for DRL/DRH/DRO | SemanticError |
| `DR_TIME_UNIT_REQUIRED` | DRL/DRH/DRO without time unit | SemanticError |

See `conformance/operant/errors.json` for the full registry.

## 9. Design Decisions

DR schedules are modeled as **filters / modifiers orthogonal to the 3×3 grid**, not as additional grid entries. They operate on a different dimension (IRT, response absence) than Distribution × Domain. This matches the procedural logic of DR and permits clean composition with grid schedules via `Tand` and `Conj`. See `operant/theory.md §1.4` for the formal treatment.

DRA and DRI are **not DSL primitives** — they are concurrent patterns with clinical annotations — because their defining property (topographical incompatibility of target vs alternative) is behavioral, not schedule-structural. See `operant/theory.md §1.4` (note on DRA/DRI).

## References

See Sections 2–4 for inline references; additional background:

- Cooper, J. O., Heron, T. E., & Heward, W. L. (2020). *Applied behavior analysis* (3rd ed.). Pearson.
- Ferster, C. B., & Skinner, B. F. (1957). *Schedules of reinforcement*. Appleton-Century-Crofts.
