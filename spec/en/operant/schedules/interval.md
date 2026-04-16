# Interval Schedules — FI, VI, RI

> Part of the contingency-dsl operant layer. Time-based reinforcement schedules with a response requirement at the end of the interval.

---

## 1. Scope

Interval schedules form the Interval column of the 3×3 atomic taxonomy (`operant/theory.md §1.1`). The parameter `t` specifies a time duration; reinforcement is contingent upon the **first response after the interval has elapsed** — a conjunction of a time requirement and a response requirement.

| Schedule | Distribution | Semantics | Canonical reference |
|---|---|---|---|
| **FI(t)** | Fixed | First response after exactly `t` seconds | Ferster & Skinner (1957, Ch. 5) |
| **VI(t)** | Variable | First response after variable interval with mean `t` (Fleshler-Hoffman) | Ferster & Skinner (1957, Ch. 6); Fleshler & Hoffman (1962) |
| **RI(t)** | Random | First response after random interval with mean `t` (exponential sampling) | Farmer (1963) |

## 2. Operational Definitions

### 2.1 FI — Fixed Interval

After each reinforcement, the schedule waits for exactly `t` seconds. The first response after `t` elapses is reinforced. Responses during the interval have no programmed effect.

```
FI 30-s     -- first response after 30 seconds reinforced
```

Characteristic behavioral pattern: scalloped or break-and-run responding with post-reinforcement pause (Ferster & Skinner, 1957, Ch. 5).

Denotation: `⟦Atomic(Fixed, Interval, t)⟧` (see `operant/theory.md §2.13.3`).

### 2.2 VI — Variable Interval

After each reinforcement, the schedule waits for a variable interval drawn from a Fleshler-Hoffman (1962) sequence with mean `t` seconds. The VI generator guarantees:

- Mean interval = `t`
- Constant probability of reinforcement per unit time (approximately)
- No interval value repeats within a single pass

```
VI 60-s     -- mean 60-second interval
VI 60 s     -- same schedule, space-separated unit
VI 1-min    -- equivalent expression in minutes
```

The Fleshler-Hoffman (1962) algorithm is the de-facto standard for VI-value generation in JEAB research. The generator is specified in the original paper; implementations should use the corrected 12-interval progression. See `procedure-annotator/temporal` `@algorithm("fleshler-hoffman")`.

### 2.3 RI — Random Interval

Inter-reinforcement intervals are independently sampled from an exponential distribution with mean `t`. Unlike VI, RI is memoryless: probability of reinforcement at time `u` past the last reinforcement is `1/t` regardless of `u`.

```
RI 60-s     -- exponentially distributed intervals, mean 60 s
```

Denotation: `⟦Atomic(Random, Interval, t)⟧` uses per-tick Bernoulli sampling.

## 3. Interval vs Time — The Response Requirement

Interval schedules (FI, VI, RI) are **conjunctive**: they require both (a) time `t` elapsed and (b) a response. Time schedules (FT, VT, RT; see `operant/schedules/time.md`) are **response-independent**: reinforcement is delivered at the time threshold regardless of responding.

This distinction is captured at the Domain level: `Domain ∈ {Ratio, Interval, Time}`.

## 4. Limited Hold

Interval schedules commonly carry a **Limited Hold** (LH) qualifier that bounds the window during which the first post-interval response is reinforceable:

```
FI 30-s LH 10-s      -- first response within 10 s of interval elapse is reinforced
VI 60-s LH 5-s       -- VI 60 with 5-s hold
```

See `operant/theory.md §1.6` for LH semantics, §1.6.1 for default-propagation attribute grammar, and `operant/grammar.md` for the surface syntax.

## 5. Compositions Involving Interval Schedules

Interval schedules participate in all compound combinators (see `operant/schedules/compound.md`):

```
Conc(VI 30-s, VI 60-s, COD=2-s)       -- concurrent VI-VI, the matching-law preparation
Chain(FR 5, FI 30-s)                  -- fixed-ratio link chained to fixed-interval link
Mult(VI 30-s, EXT)                    -- multiple VI-EXT (behavioral contrast paradigm)
```

The **concurrent VI-VI matching law** (Herrnstein, 1961) is a behavioral outcome, not a DSL parameter. See `operant/theory.md §2.6` for the procedure-effect boundary.

## 6. Second-Order Interval Schedules

`FI t(Unit)` composes an interval-overall with an inner unit schedule (Kelleher, 1966):

```
FI 300-s(FR 10)      -- 10-response unit, interval-gated at 300 s
```

Unlike ratio-overall second-order schedules, interval-overall second-order schedules are **not** reducible to `Repeat`. The interval-overall imposes temporal structure across unit completions. See `operant/theory.md §2.11.1`.

## 7. Errors and Warnings

| Code | Condition | Severity |
|---|---|---|
| `ATOMIC_NONPOSITIVE_VALUE` | `t ≤ 0` | SemanticError |
| `ATOMIC_INTERVAL_TIME_UNIT_REQUIRED` | Interval schedule without time unit | SemanticError |
| `MISSING_COD` | `Conc(VI, VI)` without COD specification | WARNING |

See `conformance/operant/errors.json` for the full registry.

## 8. VI Value Generation — Fleshler-Hoffman Algorithm

The Fleshler-Hoffman (1962) algorithm generates VI value sequences that approximate constant response probability per unit time. Implementations should use the corrected 12-value progression documented in the original paper. The `contingency-py` and `contingency-rs` runtime packages provide reference implementations; see `implementation.md` for the Python mapping.

## References

- Farmer, J. (1963). Properties of behavior under random interval reinforcement schedules. *Journal of the Experimental Analysis of Behavior*, 6(4), 607–616. https://doi.org/10.1901/jeab.1963.6-607
- Ferster, C. B., & Skinner, B. F. (1957). *Schedules of reinforcement*. Appleton-Century-Crofts.
- Fleshler, M., & Hoffman, H. S. (1962). A progression for generating variable-interval schedules. *Journal of the Experimental Analysis of Behavior*, 5(4), 529–530. https://doi.org/10.1901/jeab.1962.5-529
- Herrnstein, R. J. (1961). Relative and absolute strength of response as a function of frequency of reinforcement. *Journal of the Experimental Analysis of Behavior*, 4(3), 267–272. https://doi.org/10.1901/jeab.1961.4-267
- Kelleher, R. T. (1966). Conditioned reinforcement in second-order schedules. *Journal of the Experimental Analysis of Behavior*, 9(5), 475–485. https://doi.org/10.1901/jeab.1966.9-475
