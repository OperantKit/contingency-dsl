# Core-Stateful Grammar

> Part of the contingency-dsl specification. Describes the grammar
> productions for the Core-Stateful layer.
>
> For the formal EBNF, see [schema/core-stateful/grammar.ebnf](../../../schema/core-stateful/grammar.ebnf).
> For the architectural rationale, see [design-philosophy.md §2.1](../design-philosophy.md).

---

## Overview

Core-Stateful schedules are integrated into the Core grammar via the
`modifier` production rule:

```ebnf
modifier ::= dr_mod | pr_mod | repeat | lag_mod
           | pctl_mod                    -- Core-Stateful
```

All Core-Stateful productions follow the same CFG structure as Core
productions. The difference is semantic: Core-Stateful criteria are
computed from runtime state, not compared against literal values.

---

## §1. Percentile Schedule — `Pctl`

Platt, J. R. (1973). Percentile reinforcement. In G. H. Bower (Ed.),
*The psychology of learning and motivation* (Vol. 7, pp. 271–296).

Galbicka, G. (1994). Shaping in the 21st century. *JABA*, *27*(4), 739–760.
https://doi.org/10.1901/jaba.1994.27-739

### Syntax

```
Pctl(IRT, 50)                            -- minimal
Pctl(IRT, 25, window=30)                 -- with window
Pctl(latency, 75, window=50, dir=above)  -- fully specified
```

### Parameters

| Parameter | Position | Type | Required | Default | Description |
|---|---|---|---|---|---|
| `target` | positional 1 | enum | YES | — | Response dimension: `IRT`, `latency`, `duration`, `force`, `rate` |
| `rank` | positional 2 | integer 0–100 | YES | — | Percentile threshold |
| `window` | keyword | positive integer | NO | 20 | Recent responses for distribution |
| `dir` | keyword | enum | NO | `"below"` | Reinforcement direction: `"below"` or `"above"` |

### Semantics

Let R = [r_{n-m+1}, ..., r_n] be the m most recent values of the target dimension.
Let p_k = percentile(R, rank).

```
dir=below:  reinforce(r_{n+1}) ⟺ r_{n+1} ≤ p_k
dir=above:  reinforce(r_{n+1}) ⟺ r_{n+1} ≥ p_k
```

**Initial state:** Until `window` responses have been emitted, all
responses are reinforced (CRF equivalent), per Platt (1973).

### Relationship to DRL/DRH

Percentile is a generalization of DRL/DRH with dynamic (adaptive) rather
than fixed thresholds. Both remain in the grammar:

- `DRL 5s` — fixed criterion, Core (static, decidable equivalence)
- `Pctl(IRT, 50)` — dynamic criterion, Core-Stateful (runtime-dependent equivalence)

### Semantic Constraints

| Code | Condition | Severity |
|---|---|---|
| `PCTL_INVALID_RANK` | rank not integer in [0, 100] | SemanticError |
| `PCTL_INVALID_WINDOW` | window ≤ 0 or non-integer | SemanticError |
| `PCTL_UNKNOWN_TARGET` | target not in enum | SemanticError |
| `PCTL_INVALID_DIR` | dir not `"below"` or `"above"` | SemanticError |
| `PCTL_UNEXPECTED_TIME_UNIT` | rank carries time unit | SemanticError |
| `DUPLICATE_PCTL_KW_ARG` | duplicate keyword argument | SemanticError |
| `PCTL_EXTREME_RANK` | rank == 0 or 100 | WARNING |
| `PCTL_SMALL_WINDOW` | window < 5 | WARNING |
| `PCTL_LARGE_WINDOW` | window > 100 | WARNING |

---

## §2. Adjusting Schedule — `Adj`

Blough, D. S. (1958). A method for obtaining psychophysical thresholds
from the pigeon. *JEAB*, *1*(1), 31–43. https://doi.org/10.1901/jeab.1958.1-31

Mazur, J. E. (1987). An adjusting procedure for studying delayed
reinforcement. In M. L. Commons et al. (Eds.), *Quantitative analyses
of behavior* (Vol. 5, pp. 55–73). Erlbaum.

Richards, J. B., Mitchell, S. H., de Wit, H., & Seiden, L. S. (1997).
Determination of discount functions in rats with an adjusting-amount
procedure. *JEAB*, *67*(3), 353–366. https://doi.org/10.1901/jeab.1997.67-353

### Syntax

```
Adj(delay, start=10s, step=1s)                     -- minimal
Adj(delay, start=10s, step=2s, min=0s, max=120s)   -- with bounds
Adj(ratio, start=5, step=2)                        -- adjusting-ratio
Adj(amount, start=3, step=1, min=1, max=10)        -- adjusting-amount
Adjusting(delay, start=10s, step=1s)               -- verbose alias
```

### Parameters

| Parameter | Position | Type | Required | Default | Description |
|---|---|---|---|---|---|
| `target` | positional 1 | enum | YES | — | What parameter is adjusted: `delay`, `ratio`, `amount` |
| `start` | keyword | value | YES | — | Initial parameter value |
| `step` | keyword | value | YES | — | Adjustment magnitude per step (additive) |
| `min` | keyword | value | NO | none | Lower bound on adjusted parameter |
| `max` | keyword | value | NO | none | Upper bound on adjusted parameter |

### Target Dimensions

| Target | Adjusted Parameter | Dimension | Implicit Base Contingency | Reference |
|---|---|---|---|---|
| `delay` | Reinforcement delay | time (unit required) | CRF + adjusting delay | Mazur (1987) |
| `ratio` | Response ratio requirement | dimensionless (integer) | Adjusting FR | Ferster & Skinner (1957) |
| `amount` | Reinforcer magnitude | dimensionless (runtime-interpreted) | CRF + adjusting amount | Richards et al. (1997) |

### Semantics

```
Let P(t) be the adjusted parameter value at trial t.
P(0) = start.

After each reinforcement (or trial block completion):
  If "increase" criterion met:  P(t+1) = clamp(P(t) + step, min, max)
  If "decrease" criterion met:  P(t+1) = clamp(P(t) - step, min, max)
  Otherwise:                    P(t+1) = P(t)
```

The increase/decrease direction rule is **delegated to the runtime**.
The DSL declares the parametric structure; the adjustment algorithm
(e.g., Mazur's 4-trial block majority rule) is a runtime implementation
detail, analogous to `@algorithm("fleshler-hoffman")` for VI value
generation.

### Integration Point

Adj extends `base_schedule` (not `modifier`), because it defines a
standalone contingency structure rather than modifying a reinforcement
criterion. This differs from Pctl, which extends `modifier`.

```ebnf
base_schedule ::= ... | adj_schedule
```

### Relationship to PR

| | PR(linear, start=1, increment=5) | Adj(ratio, start=5, step=2) |
|---|---|---|
| Direction | Monotonic increase only | Bidirectional (behavior-dependent) |
| Change rule | Deterministic (fixed increment each reinforcement) | Behavior-dependent (recent performance) |
| Convergence | None (increases until breakpoint) | Yes (indifference point) |
| Layer | Core (non-TC) | Core-Stateful (runtime state) |

### Semantic Constraints

| Code | Condition | Severity |
|---|---|---|
| `MISSING_ADJ_PARAM` | `start` or `step` omitted | SemanticError |
| `ADJ_UNKNOWN_TARGET` | target not in enum | SemanticError |
| `ADJ_NONPOSITIVE_START` | start ≤ 0 | SemanticError |
| `ADJ_NONPOSITIVE_STEP` | step ≤ 0 | SemanticError |
| `ADJ_TIME_UNIT_REQUIRED` | `delay` target without time unit | SemanticError |
| `ADJ_UNEXPECTED_TIME_UNIT` | `ratio`/`amount` target with time unit | SemanticError |
| `ADJ_INVALID_BOUNDS` | min ≥ max | SemanticError |
| `ADJ_START_OUT_OF_BOUNDS` | start outside [min, max] | SemanticError |
| `ADJ_RATIO_NOT_INTEGER` | `ratio` target with non-integer values | SemanticError |
| `DUPLICATE_ADJ_KW_ARG` | duplicate keyword argument | SemanticError |
| `ADJ_UNBOUNDED_DELAY` | `delay` target without `max` | WARNING |
| `ADJ_LARGE_STEP` | step > start | WARNING |
| `ADJ_ZERO_MIN_DELAY` | min=0 with `delay` target | WARNING |
| `ADJ_SUBUNIT_RATIO` | `ratio` target with min < 1 | WARNING |

---

## §3. Interlocking Schedule — `Interlock`

Ferster, C. B., & Skinner, B. F. (1957). *Schedules of reinforcement*.
Appleton-Century-Crofts.

Berryman, R., & Nevin, J. A. (1962). Interlocking schedules of
reinforcement. *JEAB*, *5*(2), 213–223.
https://doi.org/10.1901/jeab.1962.5-213

Powers, R. B. (1968). Clock-delivered reinforcers in conjunctive and
interlocking schedules. *JEAB*, *11*(5), 579–586.
https://doi.org/10.1901/jeab.1968.11-579

### Syntax

```
Interlock(R0=300, T=10min)       -- F&S 1957 original example
Interlock(R0=16, T=80s)          -- Powers (1968) condition
Interlocking(R0=250, T=5min)     -- verbose alias
```

### Parameters

| Parameter | Position | Type | Required | Default | Description |
|---|---|---|---|---|---|
| `R0` | keyword | positive integer | YES | — | Initial ratio requirement (post-reinforcement) |
| `T` | keyword | time value | YES | — | Time window; at t = T the ratio requirement reaches 1 (CRF) |

### Semantics

Ratio and interval requirements interlock: the ratio requirement
decreases linearly as time elapses since the last reinforcement.

```
R(t) = max(1, ⌈R0 × (1 − t/T)⌉)

At t = 0:  R(0) = R0   (maximum ratio)
At t = T:  R(T) = 1    (CRF — first response reinforced)
At reinforcement: reset t₀ ← current_time
```

Behavioral implications:
- Fast responding → high ratio requirement (little time elapsed)
- Slow responding → low ratio requirement (time elapsed)
- No responding for T → first response reinforced (CRF equivalent)
- Each reinforcement resets the clock (non-cumulative)

### Integration Point

Like Adj, Interlocking extends `base_schedule` as a standalone
schedule expression:

```ebnf
base_schedule ::= ... | interlock_schedule
```

### Relationship to Conjunctive/Alternative

| Schedule | Reinforcement Logic | Parameter Nature |
|---|---|---|
| Conjunctive | AND (both requirements met) | Fixed |
| Alternative | OR (either requirement met) | Fixed |
| **Interlocking** | **Linked** (one modifies the other) | **Time-function, resets at reinforcement** |

### Core-Stateful Classification

Interlocking is the only **deterministic** Core-Stateful schedule.
Pctl and Adj adapt to the subject's behavior; Interlocking's criterion
is a function of elapsed time alone, independent of behavior.

| Runtime State | Schedule | Nature |
|---|---|---|
| Response history (recent distribution) | Pctl | Adaptive |
| Trial outcome (recent performance) | Adj | Adaptive |
| **Elapsed time (continuous function)** | **Interlock** | **Deterministic** |

### Naming Collision Resolution

"Interlocking" refers to Ferster & Skinner (1957) schedules in the DSL.
Glenn (2004) "Interlocking Behavioral Contingencies" (metacontingency
theory) uses the annotation `@ibc` to avoid collision.

### Semantic Constraints

| Code | Condition | Severity |
|---|---|---|
| `MISSING_INTERLOCK_PARAM` | `R0` or `T` omitted | SemanticError |
| `INTERLOCK_INVALID_R0` | R0 ≤ 0 or non-integer | SemanticError |
| `INTERLOCK_UNEXPECTED_TIME_UNIT` | R0 carries time unit | SemanticError |
| `INTERLOCK_NONPOSITIVE_T` | T ≤ 0 | SemanticError |
| `INTERLOCK_TIME_UNIT_REQUIRED` | T without time unit | SemanticError |
| `DUPLICATE_INTERLOCK_KW_ARG` | duplicate keyword argument | SemanticError |
| `INTERLOCK_TRIVIAL_RATIO` | R0 == 1 (effectively FT) | WARNING |
| `INTERLOCK_LARGE_RATIO` | R0 > 500 | WARNING |
