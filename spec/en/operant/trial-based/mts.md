# Matching-to-Sample — `MTS`

> Part of the contingency-dsl Operant.TrialBased sublayer. Discrete-trial conditional-discrimination procedure: the subject is presented with a sample stimulus followed by comparison stimuli and must select the comparison that matches the sample under identity or arbitrary criteria.

---

## 1. Origin

- Cumming, W. W., & Berryman, R. (1965). The complex discriminated operant: Studies of matching-to-sample and related problems. In D. I. Mostofsky (Ed.), *Stimulus generalization* (pp. 284–330). Stanford University Press.
- Sidman, M. (1971). Reading and auditory-visual equivalences. *Journal of Speech and Hearing Research*, 14(1), 5–13. https://doi.org/10.1044/jshr.1401.05
- Sidman, M., & Tailby, W. (1982). Conditional discrimination vs. matching-to-sample: An expansion of the testing paradigm. *Journal of the Experimental Analysis of Behavior*, 37(1), 5–22. https://doi.org/10.1901/jeab.1982.37-5
- Blough, D. S. (1959). Delayed matching in the pigeon. *Journal of the Experimental Analysis of Behavior*, 2(2), 151–160. https://doi.org/10.1901/jeab.1959.2-151

## 2. Syntax

```
MTS(comparisons=3, consequence=CRF, ITI=5s)                       -- minimal
MTS(comparisons=3, consequence=CRF, incorrect=EXT, ITI=5s)        -- with incorrect
MTS(comparisons=2, consequence=CRF, incorrect=FT5s, ITI=10s, type=identity)
                                                                   -- fully specified
MTS(comparisons=3, consequence=CRF, ITI=5s, delay=5s)              -- DMTS
MTS(comparisons=3, consequence=CRF, ITI=5s, correction=true)       -- correction
MTS(comparisons=3, consequence=CRF, ITI=5s, delay=2s, correction=3) -- DMTS + bounded correction
```

## 3. Parameters

| Parameter | Position | Type | Required | Default | Description |
|---|---|---|---|---|---|
| `comparisons` | keyword | positive integer ≥ 2 | YES | — | Number of comparison stimuli per trial |
| `consequence` | keyword | schedule | YES | — | Operant schedule for correct response |
| `incorrect` | keyword | schedule | NO | `EXT` | Operant schedule for incorrect response |
| `ITI` | keyword | time value | YES | — | Inter-trial interval |
| `type` | keyword | enum | NO | `"arbitrary"` | Matching type: `"identity"` or `"arbitrary"` |
| `delay` | keyword | time value ≥ 0 | NO | `0s` | Retention interval between sample offset and comparison onset. `delay=0s` is equivalent to simultaneous MTS; `delay>0` yields DMTS (Blough, 1959). |
| `correction` | keyword | boolean / positive integer / `"repeat_until_correct"` | NO | `false` | Correction procedure (Harrison, 1970). `true` / `"repeat_until_correct"` repeats the same trial until correct; positive integer `N` bounds retries to `N`. |

All parameters are keyword-only (no positional arguments).

## 4. Matching Types

| Type | Correct response definition | Reference |
|---|---|---|
| `identity` | Select comparison physically identical to sample | Cumming & Berryman (1965) |
| `arbitrary` | Select comparison in same stimulus class as sample | Sidman (1971); Sidman & Tailby (1982) |

For `type=arbitrary`, class membership is defined by the `@stimulus_classes` annotation (not by the MTS primitive itself).

## 5. Consequence Parameters

`consequence` and `incorrect` accept any operant `schedule` expression syntactically, restricted by semantic constraints (compound and recursive trial-based schedules are rejected). Typical choices:

| Appropriate | Description |
|---|---|
| `CRF` / `FR 1` | Every correct response reinforced (most common) |
| `EXT` | No feedback (probe trials) |
| `VR 3` | Intermittent reinforcement (partial reinforcement) |
| `FT 5-s` | Timeout (typically for `incorrect`) |

## 6. Trial State Machine

An MTS trial is a 5-state finite-state machine:

```
         ┌──────────────────────────────────────────────┐
         │                                              │
         ▼                                              │
    ┌─────────┐     ┌────────────┐     ┌──────────┐    │
    │ SAMPLE  │────▶│ COMPARISON │────▶│ EVALUATE │    │
    └─────────┘     └────────────┘     └──────────┘    │
                                         │      │      │
                                    correct  incorrect  │
                                         │      │      │
                                         ▼      ▼      │
                                  ┌─────────────────┐   │
                                  │   CONSEQUENCE   │   │
                                  └────────┬────────┘   │
                                           │            │
                                           ▼            │
                                       ┌───────┐       │
                                       │  ITI  │───────┘
                                       └───────┘
```

States: `Q = {SAMPLE, COMPARISON, EVALUATE, CONSEQUENCE, ITI}`, initial `q₀ = SAMPLE`, final `F = {ITI}`.

Trial structure:

```
1. Sample presentation
2. [if delay > 0: sample offset → delay seconds → comparison onset] (DMTS)
3. Comparison presentation  (comparisons stimuli, position randomized)
4. Response                 (subject selects one comparison)
5. Consequence
   ├─ correct match  → execute consequence schedule
   └─ incorrect      → execute incorrect schedule
6. [if correction active: repeat trial per correction_spec]
7. Inter-Trial Interval     (ITI duration, all stimuli off)
8. → next trial
```

Correctness definition:

```
type=identity:   correct ⟺ response_stimulus == sample_stimulus
type=arbitrary:  correct ⟺ class(response_stimulus) == class(sample_stimulus)
```

## 7. DMTS (Delay)

When `delay > 0`, a retention interval is inserted after sample offset (Delayed Matching-to-Sample; Blough, 1959). During the retention interval the sample is removed, and comparison stimuli have not yet been presented (standard DMTS). `delay=0s` is formally equivalent to simultaneous MTS (pre-existing behavior); writing it explicitly documents intent.

The published parametric range is typically 0–60 s (Grant, 1975; White, 1985). `delay > 60s` triggers WARNING `MTS_LONG_DELAY`.

## 8. Correction Procedure

Declaratively controls the handling of incorrect trials (Harrison, 1970; Saunders & Green, 1999):

```
correction=false                    → advance to next trial on error (default)
correction=true                     → repeat same trial until correct
correction="repeat_until_correct"   → desugars to correction=true (idempotent)
correction=N  (integer N ≥ 1)       → repeat up to N times, then advance
```

Mind the position-bias risk (Dube & McIlvane, 1996). In the Sidman tradition, equivalence test trials are typically run without correction and without differential reinforcement. Combining `delay > 0` with `correction=true` / `"repeat_until_correct"` conflates retention and acquisition procedures, and thus triggers WARNING `DMTS_WITH_CORRECTION`.

## 9. AST Representation (Normalization)

`delay` and `correction` are materialized in the AST per the following rules:

| Surface syntax | AST |
|---|---|
| `delay` omitted | no `delay` / `delay_unit` fields |
| `delay=0s` | `delay: 0.0, delay_unit: "s"` (intent marker) |
| `delay=Xu` (X>0) | `delay: X, delay_unit: "u"` |
| `correction` omitted | no `correction` field |
| `correction=false` | `correction: { mode: "disabled" }` |
| `correction=true` | `correction: { mode: "unlimited" }` |
| `correction="repeat_until_correct"` | `correction: { mode: "unlimited" }` (identical AST to `true`; desugared) |
| `correction=N` (N≥1) | `correction: { mode: "bounded", limit: N }` |

**Omitted and explicit forms are distinguishable at the AST level** (for round-trip preservation), **but are behaviorally equivalent at runtime**. Downstream consumers (simulators, linters, visualizers) MUST treat them as identical.

### Backward Compatibility

For every pre-extension program `P` that contains neither `delay` nor `correction`, the current parser produces the same AST as the pre-extension parser for `P`. The `mts_kw_arg` extension is additive; pre-extension alternatives match `P`'s token stream verbatim; new productions are unreachable from `P`.

### Warning Emission Order

When multiple warnings apply to the same MTS expression, all are emitted in definition order (W1 → W2 → W3 → W4 → W5 → W7 → W8 → W9 → W1b). No suppression or precedence rule applies. Linters MAY group warnings in their reports but MUST NOT drop any of them.

## 10. Stimulus Equivalence and Annotations

MTS is the procedural foundation for stimulus equivalence research (Sidman, 1971). The DSL separates concerns:

- **MTS primitive** — trial structure (presentation → selection → consequence → ITI)
- **Annotations** — stimulus content, class relations, training/testing phases, mastery criteria

```
-- Training phase: AB relation
@stimulus_classes(A=["A1","A2","A3"], B=["B1","B2","B3"])
@training(relations=["AB"], criterion=90, consecutive_blocks=2)
MTS(comparisons=3, consequence=CRF, incorrect=FT3s, ITI=5s)

-- Test phase: BA symmetry test
@stimulus_classes(A=["A1","A2","A3"], B=["B1","B2","B3"])
@testing(relations=["BA"], probe_ratio=1.0)
MTS(comparisons=3, consequence=EXT, ITI=5s)
```

Training and testing use the **same MTS primitive** with different consequence schedules and annotations.

### Additional Annotations

For session structure and probe-mixing policy, use two keywords from `measurement-annotator`:

- **`@session(trials=N)`** / **`@session(blocks=K, block_size=M)`** — Trial-based session structure. Directly expresses the "72 trials per session" pattern in JEAB Method sections. See `annotations/measurement-annotator/README.md` §`@session`.
- **`@probe_policy(baseline_reinforced, probe_ratio, interspersed, order)`** — Strongly-defined probe/baseline trial-mixing policy for equivalence testing (Fields et al., 1997). See same README §`@probe_policy`.

Example (Arntzen 2012 + Fields 1997 recommended configuration):

```
@session(blocks=6, block_size=12)
@probe_policy(baseline_reinforced=true, probe_ratio=0.5)
@stimulus_classes(A=["A1","A2","A3"], B=["B1","B2","B3"])
@testing(relations=["BA"])
MTS(comparisons=3, consequence=CRF, ITI=5s)
```

## 11. Compound Usage

```
-- Multiple schedule: MTS alternating with extinction
Mult(MTS(comparisons=3, consequence=CRF, ITI=5s), EXT)

-- Chained: FR5 then MTS trial
Chain(FR5, MTS(comparisons=3, consequence=CRF, ITI=5s))

-- let binding
let ab_training = MTS(comparisons=3, consequence=CRF, incorrect=FT3s, ITI=5s)
let ba_test = MTS(comparisons=3, consequence=EXT, ITI=5s)
Mult(ab_training, ba_test)
```

## 12. Limited Hold Compatibility

**MTS + LH:** LH constrains the response window within the COMPARISON state. If the subject does not select a comparison within the LH duration, the trial terminates and `incorrect` executes. Standard MTS procedure.

```
MTS(comparisons=3, consequence=CRF, ITI=5s) LH 10-s
```

| Code | Condition | Severity |
|---|---|---|
| `MTS_LONG_LH` | `LH > 5min` on MTS | WARNING |

## 13. Semantic Constraints

| Code | Condition | Severity |
|---|---|---|
| `MTS_INVALID_COMPARISONS` | `comparisons < 2` or non-integer | SemanticError |
| `MTS_COMPARISONS_TIME_UNIT` | `comparisons` carries a time unit | SemanticError |
| `MISSING_MTS_PARAM` | `consequence` or `ITI` omitted | SemanticError |
| `MTS_NONPOSITIVE_ITI` | `ITI ≤ 0` | SemanticError |
| `MTS_ITI_TIME_UNIT_REQUIRED` | `ITI` without time unit | SemanticError |
| `MTS_INVALID_TYPE` | `type` not `"identity"` or `"arbitrary"` | SemanticError |
| `MTS_INVALID_CONSEQUENCE` | `consequence` is a compound schedule | SemanticError |
| `MTS_RECURSIVE_CONSEQUENCE` | `consequence` is a trial_based_schedule | SemanticError |
| `DUPLICATE_MTS_KW_ARG` | Duplicate keyword argument | SemanticError |
| `MTS_INVALID_DELAY` | `delay < 0` | SemanticError |
| `MTS_DELAY_TIME_UNIT_REQUIRED` | `delay` without time unit | SemanticError |
| `MTS_CORRECTION_LIMIT_NONPOSITIVE` | `correction=N` with `N ≤ 0` | SemanticError |
| `MTS_INVALID_CORRECTION` | `correction` not a boolean / positive integer / `"repeat_until_correct"` | SemanticError |
| `MTS_MANY_COMPARISONS` | `comparisons > 9` | WARNING |
| `MTS_TWO_COMPARISONS_WEAK` (W1b) | `comparisons = 2` — reject-control alone can yield 100% correct, leaving select-control undetected (Sidman, 1987; Carrigan & Sidman, 1992) | WARNING |
| `MTS_NO_REINFORCEMENT` | `consequence=EXT` | WARNING |
| `MTS_IDENTITY_WITH_CLASSES` | `type=identity` with `@stimulus_classes` | WARNING |
| `MTS_ARBITRARY_WITHOUT_CLASSES` | `type=arbitrary` without `@stimulus_classes` | WARNING |
| `MTS_SHORT_ITI` | `ITI < 1s` | WARNING |
| `DMTS_WITH_CORRECTION` | `delay > 0` and `correction=true` / `"repeat_until_correct"` | WARNING |
| `MTS_LONG_DELAY` | `delay > 60s` | WARNING |

## 14. What the DSL Does Not Represent

The DSL does not represent:

1. **Emergent relations** (reflexivity, symmetry, transitivity) — these are behavioral outcomes observed *after* MTS training, not procedural specifications.
2. **Derived stimulus relations** (Hayes et al., 2001) — theoretical constructs about the *process* underlying equivalence.
3. **Transfer of function** — a behavioral phenomenon observed across stimulus classes.

These are intentional omissions following the procedure-effect boundary established in `operant/theory.md §2.6`: *the DSL specifies procedures — what the experimenter arranges. It does not predict effects — what the organism does.*

## References

See inline references. Additional background:

- Carrigan, P. F., & Sidman, M. (1992). Conditional discrimination and equivalence relations: A theoretical analysis of control by negative stimuli. *Journal of the Experimental Analysis of Behavior*, 58(1), 183–204. https://doi.org/10.1901/jeab.1992.58-183
- Dube, W. V., & McIlvane, W. J. (1996). Implications of stimulus control topography analysis for emergent stimulus classes. In T. R. Zentall & P. M. Smeets (Eds.), *Stimulus class formation in humans and animals* (pp. 197–218). Elsevier.
- Fields, L., Adams, B. J., Buffington, D. M., Yang, W., & Verhave, T. (1997). Response transitions across and within testing trials: An ignored simultaneous discrimination. *Journal of the Experimental Analysis of Behavior*, 66(2), 323–339.
- Harrison, J. M. (1970). Effects of stimulus control procedures on discrimination learning. *Journal of the Experimental Analysis of Behavior*, 14(3), 345–351.
- Hayes, S. C., Barnes-Holmes, D., & Roche, B. (Eds.). (2001). *Relational frame theory: A post-Skinnerian account of human language and cognition*. Kluwer Academic/Plenum.
- Saunders, K. J., & Green, G. (1999). A discrimination analysis of training-structure effects on stimulus equivalence outcomes. *Journal of the Experimental Analysis of Behavior*, 72(1), 117–137. https://doi.org/10.1901/jeab.1999.72-117
- Sidman, M. (1987). Two choices are not enough. *Behavior Analysis*, 22(1), 11–18.
