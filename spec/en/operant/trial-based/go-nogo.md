# Go/No-Go Discrimination — `GoNoGo`

> Part of the contingency-dsl Operant.TrialBased sublayer. Discrete-trial successive-discrimination procedure: on each trial, an SD or SΔ is presented and the subject is scored on whether a response occurs within the response window.

---

## 1. Origin

- Skinner, B. F. (1938). *The behavior of organisms: An experimental analysis*. Appleton-Century-Crofts.
- Terrace, H. S. (1963). Discrimination learning with and without "errors." *Journal of the Experimental Analysis of Behavior*, 6(1), 1–27. https://doi.org/10.1901/jeab.1963.6-1
- Dinsmoor, J. A. (1995a). Stimulus control: Part I. *The Behavior Analyst*, 18(1), 51–68.
- Nevin, J. A. (1969). Signal detection theory and operant behavior. *Journal of the Experimental Analysis of Behavior*, 12(3), 475–480. https://doi.org/10.1901/jeab.1969.12-475

## 2. Syntax

```
GoNoGo(responseWindow=5s, consequence=CRF, ITI=10s)             -- minimal
GoNoGo(responseWindow=5s, consequence=CRF, incorrect=FT10s,
       ITI=10s)                                                    -- with incorrect
GoNoGo(responseWindow=5s, consequence=CRF, incorrect=EXT,
       falseAlarm=FT10s, ITI=15s)                                 -- SDT-style
```

## 3. Parameters

| Parameter | Position | Type | Required | Default | Description |
|---|---|---|---|---|---|
| `responseWindow` | keyword | time value | YES | — | Duration of response opportunity |
| `consequence` | keyword | schedule | YES | — | Operant schedule for hit (Go + response) |
| `incorrect` | keyword | schedule | NO | `EXT` | Operant schedule for errors (miss + false-alarm fallback) |
| `falseAlarm` | keyword | schedule | NO | = `incorrect` | Operant schedule for NoGo errors (overrides `incorrect` for false alarms) |
| `ITI` | keyword | time value | YES | — | Inter-trial interval |

All parameters are keyword-only (no positional arguments).

## 4. Trial State Machine

A GoNoGo trial is a 4-state finite-state machine:

```
         ┌──────────────────────────────────────┐
         │                                      │
         ▼                                      │
    ┌──────────┐                                │
    │ STIMULUS │  ← SD or SΔ presented          │
    └──────────┘    responseWindow starts       │
         │                                      │
    ┌────┴────┐                                 │
    │         │                                 │
 response  window_expires                       │
    │         │                                 │
    ▼         ▼                                 │
┌──────────────┐                                │
│   EVALUATE   │                                │
└──────────────┘                                │
    │      │                                    │
 correct  incorrect                             │
    │      │                                    │
    ▼      ▼                                    │
┌──────────────┐                                │
│ CONSEQUENCE  │                                │
└──────────────┘                                │
         │                                      │
         ▼                                      │
    ┌─────────┐                                 │
    │   ITI   │─────────────────────────────────┘
    └─────────┘
```

States: `Q = {STIMULUS, EVALUATE, CONSEQUENCE, ITI}`, initial `q₀ = STIMULUS`, final `F = {ITI}`.

Trial structure:

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

## 5. 2×2 Outcome Matrix

|  | Response | No Response |
|---|---|---|
| **Go (SD)** | HIT → `consequence` | MISS → `incorrect` |
| **NoGo (SΔ)** | FALSE ALARM → `falseAlarm` | CORRECT REJECTION → EXT |

Correct rejection always produces EXT (no programmed consequence). This reflects the standard Go/No-Go procedure where correctly withholding a response has no explicit consequence (Dinsmoor, 1995a).

## 6. Consequence Asymmetry

The standard Go/No-Go procedure has an inherent consequence asymmetry: hits are reinforced, but correct rejections receive no programmed consequence. This contrasts with MTS, where all correct responses receive the same `consequence` schedule.

This asymmetry is **procedural, not a design limitation**. The correct rejection is defined by the *absence* of a response during SΔ — there is no response to reinforce. Reinforcing correct rejections would require a different contingency (e.g., DRO within trials), which is a distinct procedure reserved for future extension.

The `falseAlarm` parameter allows the common variant where false alarms receive a different consequence from misses — typically a timeout (Nevin, 1969). This models the signal-detection-theory arrangement where response bias is manipulated by differential consequences for the two error types.

## 7. Consequence Parameters

`consequence`, `incorrect`, and `falseAlarm` follow the same restrictions as MTS consequence parameters:

| Appropriate | Description |
|---|---|
| `CRF` / `FR 1` | Every hit reinforced (most common) |
| `EXT` | No feedback (probe trials, correct-rejection default) |
| `FT 10-s` | Timeout (typically for `falseAlarm` or `incorrect`) |
| `VR 3` | Intermittent reinforcement (maintenance phase) |

## 8. Signal Detection Theory Arrangement

The `falseAlarm` parameter enables the SDT-style asymmetric consequence arrangement (Nevin, 1969; Davison & Tustin, 1978):

```
-- Nevin (1969) style: false alarm → timeout, miss → extinction
GoNoGo(responseWindow=5s, consequence=CRF, incorrect=EXT,
       falseAlarm=FT10s, ITI=15s)
```

The 2×2 outcome matrix maps directly to SDT measures:

| SDT Measure | Definition |
|---|---|
| Hit rate | `P(response | Go stimulus)` |
| False alarm rate | `P(response | NoGo stimulus)` |
| Sensitivity (log d) | Discriminability between Go and NoGo |
| Bias (log b) | Overall tendency to respond or withhold |

These are derived behavioral measures computed at the analysis layer, not DSL parameters.

## 9. Annotations

Go/No-Go uses annotations for stimulus specification and trial-sequence parameters:

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

## 10. Compound Usage

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

## 11. Limited Hold Compatibility

**GoNoGo + LH:** Semantically redundant — `responseWindow` already defines the response opportunity duration. LH on GoNoGo triggers a linter WARNING. If LH < responseWindow, LH becomes the effective response window.

```
GoNoGo(responseWindow=5s, consequence=CRF, ITI=10s) LH 3-s   -- WARNING
```

## 12. Relationship to Free-Operant Discrimination

Go/No-Go and `Mult(schedule, EXT)` implement the same successive discrimination using different response-opportunity structures:

| | Go/No-Go | Mult(VI, EXT) |
|---|---|---|
| **Response opportunity** | Discrete trial (1 per trial) | Free-operant (continuous) |
| **Dependent variable** | Accuracy (hit rate, FA rate) | Response rate |
| **Behavioral contrast** | Not applicable (no baseline rate) | Reynolds (1961) |
| **SDT analysis** | Natural (2×2 matrix) | Requires rate-to-probability transform |
| **DSL representation** | `GoNoGo(...)` | `Mult(VI 30-s, EXT)` |

The DSL explicitly separates these: `GoNoGo(...)` for discrete-trial successive discrimination, `Mult(schedule, EXT)` for free-operant successive discrimination.

## 13. The responseWindow Parameter

`responseWindow` is the **structural parameter** of GoNoGo, analogous to `comparisons` in MTS:

| | MTS | GoNoGo |
|---|---|---|
| **Structural parameter** | `comparisons` (integer ≥ 2) | `responseWindow` (ℝ⁺ × TimeUnit) |
| **What it defines** | Number of selection alternatives | Duration of response opportunity |
| **Without it** | No selection task | No miss / CR determination |
| **Domain** | Dimensionless count | Temporal duration |

Without `responseWindow`, a Go/No-Go trial has no defined endpoint for the STIMULUS state — there is no principled way to distinguish "has not yet responded" from "miss" or "correct rejection."

## 14. Semantic Constraints

| Code | Condition | Severity |
|---|---|---|
| `GONOGO_NONPOSITIVE_RESPONSE_WINDOW` | `responseWindow ≤ 0` | SemanticError |
| `GONOGO_RESPONSE_WINDOW_TIME_UNIT_REQUIRED` | `responseWindow` without time unit | SemanticError |
| `MISSING_GONOGO_PARAM` | `responseWindow`, `consequence`, or `ITI` omitted | SemanticError |
| `GONOGO_NONPOSITIVE_ITI` | `ITI ≤ 0` | SemanticError |
| `GONOGO_ITI_TIME_UNIT_REQUIRED` | `ITI` without time unit | SemanticError |
| `GONOGO_INVALID_CONSEQUENCE` | `consequence` / `incorrect` / `falseAlarm` is a compound schedule | SemanticError |
| `GONOGO_RECURSIVE_CONSEQUENCE` | `consequence` / `incorrect` / `falseAlarm` is a trial_based_schedule | SemanticError |
| `DUPLICATE_GONOGO_KW_ARG` | Duplicate keyword argument | SemanticError |
| `GONOGO_SHORT_RESPONSE_WINDOW` | `responseWindow < 500ms` | WARNING |
| `GONOGO_LONG_RESPONSE_WINDOW` | `responseWindow > 60s` | WARNING |
| `GONOGO_NO_REINFORCEMENT` | `consequence=EXT` | WARNING |
| `GONOGO_SHORT_ITI` | `ITI < 1s` | WARNING |
| `GONOGO_LH_REDUNDANT` | `LH` applied to `GoNoGo` | WARNING |
| `GONOGO_FALSE_ALARM_WITHOUT_INCORRECT` | `falseAlarm` specified, `incorrect` omitted | WARNING |

## 15. Free-Operant vs Discrete-Trial Boundary

Operant.Literal and Operant.Stateful schedules assume a **free-operant** response opportunity: the subject may emit the target response at any time, and the schedule evaluates a continuous stream of responses against its criterion. The dependent variable is response rate (Skinner, 1938).

Operant.TrialBased schedules (MTS and GoNoGo) assume a **discrete-trial** response opportunity: the experimenter presents a structured stimulus configuration, the subject emits exactly one selection or Go/no-response decision per trial, and the schedule evaluates that decision against a correctness criterion. The dependent variable is accuracy.

This distinction is procedural, not behavioral — it describes what the experimenter arranges, not what the subject does. See `operant/trial-based/mts.md §6` for the parallel trial-state-machine discussion.

## 16. Modifier Incompatibility

Free-operant modifiers (DRL, DRH, DRO, Pctl, Lag) are semantically incompatible with trial-based schedules because each modifier assumes a property of the free-operant response stream that does not exist in trial-based procedures:

- **DRL/DRH/Pctl** require inter-response time (IRT) from a continuous stream. In a trial-based procedure, the "time between responses" is a structured interval containing experimenter-controlled events (ITI, STIMULUS state), not an IRT.
- **DRO** requires the absence of the target response for a specified duration. In a trial-based procedure, the target response is *impossible* during ITI, SAMPLE, and CONSEQUENCE states — the absence of responding is enforced by the procedure, not by the subject's behavior.
- **Lag** reinforces responses that differ from the previous n responses. In MTS, the correct comparison is determined by the sample, not by a variability requirement; a conflict arises with the MTS correctness criterion.

Combinators (`Conc`, `Mult`, `Chain`, etc.) remain permitted with trial-based schedules because they operate at a different level — they arrange schedules relative to each other, not within a schedule's response stream.

```
TRIAL_BASED_MODIFIER_INCOMPATIBLE:
  modifier applied directly to trial_based_schedule
```

## References

See inline references. Additional background:

- Davison, M. C., & Tustin, R. D. (1978). The relation between the generalized matching law and signal-detection theory. *Journal of the Experimental Analysis of Behavior*, 29(2), 331–336. https://doi.org/10.1901/jeab.1978.29-331
- Reynolds, G. S. (1961). Behavioral contrast. *Journal of the Experimental Analysis of Behavior*, 4(1), 57–71. https://doi.org/10.1901/jeab.1961.4-57
