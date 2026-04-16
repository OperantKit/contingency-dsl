# Core-TrialBased Grammar

> Part of the contingency-dsl specification. Describes the grammar
> productions for the Core-TrialBased layer.
>
> For the formal EBNF, see [schema/core-trial-based/grammar.ebnf](../../../schema/core-trial-based/grammar.ebnf).
> For the architectural rationale, see [architecture.md §4.1](../architecture.md).

---

## Overview

Core-TrialBased schedules are integrated into the Core grammar via the
`base_schedule` production rule:

```ebnf
base_schedule ::= ... | trial_based_schedule
```

Core-TrialBased schedules differ from Core and Core-Stateful along
two independent axes:

| Axis | Core / Core-Stateful | Core-TrialBased |
|---|---|---|
| **Response opportunity** | Free-operant (continuous) | Discrete trial |
| **Reinforcement criterion** | Count / time / distribution | Stimulus–response matching |

### Structural Properties

1. **All-program common** — shared vocabulary, not program-scoped
2. **CFG syntax** — recursive-descent O(n) parsing
3. **Declarative parameters** — all values determined at parse time
4. **Consequence is explicit** — Core-TrialBased primitives take
   `consequence` and `incorrect` as Core schedule expressions,
   unlike Core/Core-Stateful where consequences are implicit

### Modifier Incompatibility

Modifiers (DRL, DRH, DRO, Pctl, Lag) assume a free-operant response
stream. Applying them to a trial-based schedule is a SemanticError:

```
TRIAL_BASED_MODIFIER_INCOMPATIBLE:
  modifier applied directly to trial_based_schedule
```

Combinators (Conc, Mult, Chain, etc.) are syntactically permitted;
semantically inappropriate combinations are handled by Linter WARNINGs.

### Limited Hold Compatibility

Unlike free-operant modifiers, **LH (Limited Hold) is compatible with
trial-based schedules**. The semantics differ by trial type:

**MTS + LH:** LH constrains the response window within the COMPARISON
state. If the subject does not select a comparison within the LH
duration, the trial terminates and `incorrect` executes. Standard
MTS procedure.

```
MTS(comparisons=3, consequence=CRF, ITI=5s) LH10s
```

**GoNoGo + LH:** Semantically redundant — `responseWindow` already
defines the response opportunity duration. LH on GoNoGo triggers a
linter WARNING. If LH < responseWindow, LH becomes the effective
response window.

```
GoNoGo(responseWindow=5s, consequence=CRF, ITI=10s) LH3s   -- WARNING
```

| Code | Condition | Severity |
|---|---|---|
| `MTS_LONG_LH` | LH > 5min on MTS | WARNING |
| `GONOGO_LH_REDUNDANT` | LH applied to GoNoGo | WARNING |

---

## §1. Matching-to-Sample — `MTS`

Cumming, W. W., & Berryman, R. (1965). The complex discriminated operant:
Studies of matching-to-sample and related problems. In D. I. Mostofsky
(Ed.), *Stimulus generalization* (pp. 284–330). Stanford University Press.

Sidman, M. (1971). Reading and auditory-visual equivalences. *Journal of
Speech and Hearing Research*, *14*(1), 5–13.
https://doi.org/10.1044/jshr.1401.05

Sidman, M., & Tailby, W. (1982). Conditional discrimination vs.
matching-to-sample. *JEAB*, *37*(1), 5–22.
https://doi.org/10.1901/jeab.1982.37-5

### Syntax

```
MTS(comparisons=3, consequence=CRF, ITI=5s)                       -- minimal
MTS(comparisons=3, consequence=CRF, incorrect=EXT, ITI=5s)        -- with incorrect
MTS(comparisons=2, consequence=CRF, incorrect=FT5s, ITI=10s, type=identity)
                                                                   -- fully specified
MTS(comparisons=3, consequence=CRF, ITI=5s, delay=5s)              -- DMTS (v1.1)
MTS(comparisons=3, consequence=CRF, ITI=5s, correction=true)       -- correction (v1.1)
MTS(comparisons=3, consequence=CRF, ITI=5s, delay=2s, correction=3) -- DMTS + bounded correction
```

### Parameters

| Parameter | Position | Type | Required | Default | Description |
|---|---|---|---|---|---|
| `comparisons` | keyword | positive integer ≥ 2 | YES | — | Number of comparison stimuli per trial |
| `consequence` | keyword | schedule | YES | — | Core schedule for correct response |
| `incorrect` | keyword | schedule | NO | `EXT` | Core schedule for incorrect response |
| `ITI` | keyword | time value | YES | — | Inter-trial interval |
| `type` | keyword | enum | NO | `"arbitrary"` | Matching type: `"identity"` or `"arbitrary"` |
| `delay` | keyword | time value ≥ 0 | NO | `0s` | **[v1.1, R-7]** Retention interval between sample offset and comparison onset. `delay=0s` is equivalent to simultaneous MTS; `delay>0` yields DMTS (Blough, 1959). |
| `correction` | keyword | boolean / positive integer / `"repeat_until_correct"` | NO | `false` | **[v1.1, R-7]** Correction procedure (Harrison, 1970). `true` / `"repeat_until_correct"` repeats the same trial until correct; a positive integer N bounds retries to N. |

All parameters are keyword-only (no positional arguments).

### Matching Types

| Type | Correct Response Definition | Reference |
|---|---|---|
| `identity` | Select comparison physically identical to sample | Cumming & Berryman (1965) |
| `arbitrary` | Select comparison in same stimulus class as sample | Sidman (1971); Sidman & Tailby (1982) |

For `type=arbitrary`, class membership is defined by `@stimulus_classes`
annotation (not by the MTS primitive itself).

### Consequence Parameters

`consequence` and `incorrect` accept any Core `schedule` expression
syntactically, but are restricted by semantic constraints:

| Appropriate | Description |
|---|---|
| `CRF` / `FR1` | Every correct response reinforced (most common) |
| `EXT` | No feedback (probe trials) |
| `VR3` | Intermittent reinforcement (partial reinforcement) |
| `FT5s` | Timeout (typically for `incorrect`) |

### Trial Structure (Semantics)

```
1. Sample presentation
2. [if delay > 0: sample offset → delay seconds → comparison onset] (v1.1: DMTS)
3. Comparison presentation  (comparisons stimuli, position randomized)
4. Response                 (subject selects one comparison)
5. Consequence
   ├─ correct match  → execute consequence schedule
   └─ incorrect      → execute incorrect schedule
6. [if correction active: repeat trial per correction_spec] (v1.1)
7. Inter-Trial Interval     (ITI duration, all stimuli off)
8. → next trial
```

Correctness definition:

```
type=identity:   correct ⟺ response_stimulus == sample_stimulus
type=arbitrary:  correct ⟺ class(response_stimulus) == class(sample_stimulus)
```

#### DMTS (Delay) — v1.1, R-7

When `delay > 0`, a retention interval is inserted after sample offset
(Delayed Matching-to-Sample; Blough, 1959). During the retention interval
the sample is removed, and comparison stimuli have not yet been presented
(standard DMTS). `delay=0s` is formally equivalent to simultaneous MTS
(pre-existing behavior); writing it explicitly documents intent.

The published parametric range is typically 0–60 s (Grant, 1975; White, 1985).
`delay > 60s` triggers WARNING `MTS_LONG_DELAY`.

#### Correction Procedure — v1.1, R-7

Declaratively controls the handling of incorrect trials
(Harrison, 1970; Saunders & Green, 1999):

```
correction=false                    → advance to next trial on error (default; v1.0 behavior)
correction=true                     → repeat same trial until correct
correction="repeat_until_correct"   → desugars to correction=true (idempotent)
correction=N  (integer N ≥ 1)       → repeat up to N times, then advance
```

Mind the position-bias risk (Dube & McIlvane, 1996). In the Sidman tradition,
equivalence test trials are typically run without correction and without
differential reinforcement. Combining `delay > 0` with
`correction=true` / `"repeat_until_correct"` conflates retention and
acquisition procedures, and thus triggers WARNING `DMTS_WITH_CORRECTION`.

### Stimulus Equivalence and Annotations

MTS is the procedural foundation for stimulus equivalence research
(Sidman, 1971). The DSL separates concerns:

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

Training and testing use the **same MTS primitive** with different
consequence schedules and annotations.

### Compound Usage

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

### Semantic Constraints

| Code | Condition | Severity |
|---|---|---|
| `MTS_INVALID_COMPARISONS` | comparisons < 2 or non-integer | SemanticError |
| `MTS_COMPARISONS_TIME_UNIT` | comparisons carries time unit | SemanticError |
| `MISSING_MTS_PARAM` | `consequence` or `ITI` omitted | SemanticError |
| `MTS_NONPOSITIVE_ITI` | ITI ≤ 0 | SemanticError |
| `MTS_ITI_TIME_UNIT_REQUIRED` | ITI without time unit | SemanticError |
| `MTS_INVALID_TYPE` | type not `"identity"` or `"arbitrary"` | SemanticError |
| `MTS_INVALID_CONSEQUENCE` | consequence is a compound schedule | SemanticError |
| `MTS_RECURSIVE_CONSEQUENCE` | consequence is a trial_based_schedule | SemanticError |
| `DUPLICATE_MTS_KW_ARG` | duplicate keyword argument | SemanticError |
| `MTS_INVALID_DELAY` | delay < 0 | SemanticError |
| `MTS_DELAY_TIME_UNIT_REQUIRED` | delay without time unit | SemanticError |
| `MTS_CORRECTION_LIMIT_NONPOSITIVE` | correction=N with N ≤ 0 | SemanticError |
| `MTS_INVALID_CORRECTION` | correction not a boolean / positive integer / `"repeat_until_correct"` | SemanticError |
| `MTS_MANY_COMPARISONS` | comparisons > 9 | WARNING |
| `MTS_NO_REINFORCEMENT` | consequence=EXT | WARNING |
| `MTS_IDENTITY_WITH_CLASSES` | type=identity with `@stimulus_classes` | WARNING |
| `MTS_ARBITRARY_WITHOUT_CLASSES` | type=arbitrary without `@stimulus_classes` | WARNING |
| `MTS_SHORT_ITI` | ITI < 1s | WARNING |
| `DMTS_WITH_CORRECTION` | delay > 0 and correction=true / `"repeat_until_correct"` | WARNING |
| `MTS_LONG_DELAY` | delay > 60s | WARNING |

---

## §2. Go/No-Go Discrimination — `GoNoGo`

Skinner, B. F. (1938). *The behavior of organisms: An experimental
analysis*. Appleton-Century-Crofts.

Terrace, H. S. (1963). Discrimination learning with and without
"errors." *JEAB*, *6*(1), 1–27.
https://doi.org/10.1901/jeab.1963.6-1

Dinsmoor, J. A. (1995a). Stimulus control: Part I. *The Behavior
Analyst*, *18*(1), 51–68.

Nevin, J. A. (1969). Signal detection theory and operant behavior.
*JEAB*, *12*(3), 475–480.
https://doi.org/10.1901/jeab.1969.12-475

### Syntax

```
GoNoGo(responseWindow=5s, consequence=CRF, ITI=10s)             -- minimal
GoNoGo(responseWindow=5s, consequence=CRF, incorrect=FT10s,
       ITI=10s)                                                    -- with incorrect
GoNoGo(responseWindow=5s, consequence=CRF, incorrect=EXT,
       falseAlarm=FT10s, ITI=15s)                                 -- SDT-style
```

### Parameters

| Parameter | Position | Type | Required | Default | Description |
|---|---|---|---|---|---|
| `responseWindow` | keyword | time value | YES | — | Duration of response opportunity |
| `consequence` | keyword | schedule | YES | — | Core schedule for hit (Go + response) |
| `incorrect` | keyword | schedule | NO | `EXT` | Core schedule for errors (miss + false alarm fallback) |
| `falseAlarm` | keyword | schedule | NO | = `incorrect` | Core schedule for NoGo errors (overrides `incorrect` for false alarms) |
| `ITI` | keyword | time value | YES | — | Inter-trial interval |

All parameters are keyword-only (no positional arguments).

### Trial Structure (Semantics)

```
1. Stimulus presentation   (SD or SΔ, single stimulus)
2. Response window          (responseWindow duration)
   ├─ response emitted     → EVALUATE with response=true
   └─ window expires       → EVALUATE with response=false
3. Evaluate (2×2 outcome matrix)
   ├─ Go + response        → HIT               → execute consequence
   ├─ Go + no response     → MISS              → execute incorrect
   ├─ NoGo + response      → FALSE ALARM       → execute falseAlarm
   └─ NoGo + no response   → CORRECT REJECTION → EXT (implicit)
4. Inter-Trial Interval     (ITI duration, all stimuli off)
5. → next trial
```

### 2×2 Outcome Matrix

|  | Response | No Response |
|---|---|---|
| **Go (SD)** | HIT → `consequence` | MISS → `incorrect` |
| **NoGo (SΔ)** | FALSE ALARM → `falseAlarm` | CORRECT REJECTION → EXT |

Correct rejection always produces EXT (no programmed consequence).
This reflects the standard Go/No-Go procedure where correctly
withholding a response has no explicit consequence (Dinsmoor, 1995a).

### Consequence Parameters

`consequence`, `incorrect`, and `falseAlarm` follow the same
restrictions as MTS consequence parameters:

| Appropriate | Description |
|---|---|
| `CRF` / `FR1` | Every hit reinforced (most common) |
| `EXT` | No feedback (probe trials, correct rejection default) |
| `FT10s` | Timeout (typically for `falseAlarm` or `incorrect`) |
| `VR3` | Intermittent reinforcement (maintenance phase) |

### Signal Detection Theory Arrangement

The `falseAlarm` parameter enables the SDT-style asymmetric
consequence arrangement (Nevin, 1969; Davison & Tustin, 1978):

```
-- Nevin (1969) style: false alarm → timeout, miss → extinction
GoNoGo(responseWindow=5s, consequence=CRF, incorrect=EXT,
       falseAlarm=FT10s, ITI=15s)
```

The 2×2 outcome matrix maps directly to SDT measures:

| SDT Measure | Definition |
|---|---|
| Hit rate | P(response \| Go stimulus) |
| False alarm rate | P(response \| NoGo stimulus) |
| Sensitivity (log d) | Discriminability between Go and NoGo |
| Bias (log b) | Overall tendency to respond or withhold |

These are derived behavioral measures computed at the analysis layer,
not DSL parameters.

### Annotations

Go/No-Go uses annotations for stimulus specification and
trial-sequence parameters:

```
-- Stimulus specification
@sd("tone", frequency=4000, duration=1s)
@s_delta("light", intensity=50)
@go_ratio(0.7)
GoNoGo(responseWindow=5s, consequence=CRF, incorrect=EXT,
       falseAlarm=FT10s, ITI=15s)

-- Errorless discrimination (Terrace, 1963)
@fading(method="stimulus", steps=10)
GoNoGo(responseWindow=5s, consequence=CRF, ITI=10s)
```

### Compound Usage

```
-- Multiple schedule: GoNoGo alternating with extinction
Mult(GoNoGo(responseWindow=5s, consequence=CRF, ITI=10s), EXT)

-- Chained: FR5 then discrimination trial
Chain(FR5, GoNoGo(responseWindow=5s, consequence=CRF, ITI=10s))

-- let binding: training vs probe
let training = GoNoGo(responseWindow=5s, consequence=CRF,
                       incorrect=EXT, falseAlarm=FT10s, ITI=15s)
let probe = GoNoGo(responseWindow=5s, consequence=EXT, ITI=15s)
Mult(training, probe)
```

### Semantic Constraints

| Code | Condition | Severity |
|---|---|---|
| `GONOGO_NONPOSITIVE_RESPONSE_WINDOW` | responseWindow ≤ 0 | SemanticError |
| `GONOGO_RESPONSE_WINDOW_TIME_UNIT_REQUIRED` | responseWindow without time unit | SemanticError |
| `MISSING_GONOGO_PARAM` | `responseWindow`, `consequence`, or `ITI` omitted | SemanticError |
| `GONOGO_NONPOSITIVE_ITI` | ITI ≤ 0 | SemanticError |
| `GONOGO_ITI_TIME_UNIT_REQUIRED` | ITI without time unit | SemanticError |
| `GONOGO_INVALID_CONSEQUENCE` | consequence/incorrect/falseAlarm is a compound schedule | SemanticError |
| `GONOGO_RECURSIVE_CONSEQUENCE` | consequence/incorrect/falseAlarm is a trial_based_schedule | SemanticError |
| `DUPLICATE_GONOGO_KW_ARG` | duplicate keyword argument | SemanticError |
| `GONOGO_SHORT_RESPONSE_WINDOW` | responseWindow < 500ms | WARNING |
| `GONOGO_LONG_RESPONSE_WINDOW` | responseWindow > 60s | WARNING |
| `GONOGO_NO_REINFORCEMENT` | consequence=EXT | WARNING |
| `GONOGO_SHORT_ITI` | ITI < 1s | WARNING |
| `GONOGO_LH_REDUNDANT` | LH applied to GoNoGo | WARNING |
| `GONOGO_FALSE_ALARM_WITHOUT_INCORRECT` | falseAlarm specified, incorrect omitted | WARNING |
