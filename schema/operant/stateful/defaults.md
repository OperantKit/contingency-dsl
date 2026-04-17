# contingency-dsl — Operant Stateful Defaults

Explicit documentation of all implicit defaults in the operant stateful layer.
When a parameter is omitted, the following values apply.

## Percentile schedule (Pctl)

| Parameter | Default | Rationale |
|-----------|---------|-----------|
| `window` | **20** | Platt (1973) recommended a window of 20 responses for stable percentile estimation. Research typically uses 10–50. |
| `dir` | **"below"** | The most common use case is shaping toward shorter IRTs (reinforcing responses below the median). Galbicka (1994) used below-threshold reinforcement for IRT differentiation. |

**Initial state (window not yet filled):** Until `window` responses have been
emitted, all responses are reinforced (CRF equivalent). This follows
Platt (1973) original procedure. The initial CRF period is implicit in the
DSL semantics; explicit modification requires contingency-core phase transitions.

### Linter warnings

| Condition | Code | Rationale |
|-----------|------|-----------|
| `rank` == 0 or 100 | `PCTL_EXTREME_RANK` | rank=0 is CRF, rank=100 is EXT. Likely user error. |
| `window` < 5 | `PCTL_SMALL_WINDOW` | Distribution instability. |
| `window` > 100 | `PCTL_LARGE_WINDOW` | Adaptiveness degradation. |

References:
- Platt, J. R. (1973). Percentile reinforcement: Paradigms for experimental
  analysis of response shaping. In G. H. Bower (Ed.), *The psychology of
  learning and motivation* (Vol. 7, pp. 271-296). Academic Press.
- Galbicka, G. (1994). Shaping in the 21st century: Moving percentile
  schedules into applied settings. *JABA*, 27(4), 739-760.
  https://doi.org/10.1901/jaba.1994.27-739

## Adjusting schedule (Adj)

`Adj` (verbose alias: `Adjusting`) is a standalone schedule expression
in the operant stateful layer. It declares a contingency in which a schedule
parameter (delay, ratio, or amount) is systematically adjusted based on the
subject's recent performance, converging toward an indifference point or
threshold.

| Parameter | Position | Default | Dimension |
|-----------|----------|---------|-----------|
| target | positional (first) | no default (required) | enum: delay, ratio, amount |
| start | keyword (`start=V`) | no default (required) | same as target dimension |
| step | keyword (`step=S`) | no default (required) | same as target dimension |
| min | keyword (`min=L`) | **null** (no lower bound) | same as target dimension |
| max | keyword (`max=U`) | **null** (no upper bound) | same as target dimension |

### Dimension rules by target

| Target | Dimension | Time unit | Integer-only | Example |
|--------|-----------|-----------|-------------|---------|
| `delay` | time | **required** (s/ms/min) | no | `start=10s, step=1s` |
| `ratio` | dimensionless | **forbidden** | **yes** | `start=5, step=2` |
| `amount` | dimensionless | **forbidden** | no | `start=3, step=1` |

### Implicit base contingency

Each target implies a base contingency:

| Target | Implied contingency | Rationale |
|--------|--------------------|-----------|
| `delay` | CRF + adjusting delay | Mazur (1987): each response produces reinforcement after the adjusted delay |
| `ratio` | Adjusting FR | Ferster & Skinner (1957): the FR value itself adjusts |
| `amount` | CRF + adjusting amount | Richards et al. (1997): each response produces an adjusted quantity of reinforcement |

### Adjustment direction

The direction of adjustment (increase, decrease, or no change) is determined by
the **runtime**, not the DSL. The DSL declares only the magnitude (`step`) and
optional bounds (`min`, `max`). This follows the same principle as
`@algorithm("fleshler-hoffman")` — the DSL declares parameters, the runtime
implements the algorithm.

### Linter warnings

| Condition | Code | Rationale |
|-----------|------|-----------|
| `delay` target, `max` not specified | `ADJ_UNBOUNDED_DELAY` | Unbounded delay growth may exceed session duration. Safety concern. |
| `step` > `start` | `ADJ_LARGE_STEP` | First downward adjustment would produce ≤ 0 (if `min` not specified). |
| `min` = 0 with `delay` target | `ADJ_ZERO_MIN_DELAY` | Delay=0 is CRF (immediate reinforcement). Usually intentional but worth flagging. |
| `ratio` target, `min` < 1 | `ADJ_SUBUNIT_RATIO` | FR < 1 is procedurally undefined. |

References:
- Ferster, C. B., & Skinner, B. F. (1957). *Schedules of reinforcement*.
  Appleton-Century-Crofts.
- Blough, D. S. (1958). A method for obtaining psychophysical thresholds from
  the pigeon. *JEAB*, 1(1), 31-43.
  https://doi.org/10.1901/jeab.1958.1-31
- Mazur, J. E. (1987). An adjusting procedure for studying delayed reinforcement.
  In M. L. Commons et al. (Eds.), *Quantitative analyses of behavior* (Vol. 5,
  pp. 55-73). Erlbaum.
- Richards, J. B., Mitchell, S. H., de Wit, H., & Seiden, L. S. (1997).
  Determination of discount functions in rats with an adjusting-amount procedure.
  *JEAB*, 67(3), 353-366. https://doi.org/10.1901/jeab.1997.67-353

## Interlocking schedule (Interlock)

`Interlock` (verbose alias: `Interlocking`) is a standalone schedule
expression in the operant stateful layer. It declares a compound schedule in which
the ratio requirement decreases linearly as time elapses since the last
reinforcement. At each reinforcement, the ratio resets to its initial value.

| Parameter | Position | Default | Dimension |
|-----------|----------|---------|-----------|
| R0 | keyword (`R0=N`) | no default (required) | dimensionless positive integer |
| T | keyword (`T=V`) | no default (required) | time (s/ms/min, required) |

### Mathematical formulation

```
R(t) = max(1, ⌈R0 × (1 − t/T)⌉)
```

- t = 0 (immediately post-reinforcement): R(0) = R0 (maximum ratio)
- t = T (time window elapsed): R(T) = 1 (CRF — first response reinforced)
- At each reinforcement: reset to R0

### Behavioral implications

- Fast responding → high ratio cost (little time elapsed)
- Slow responding → low ratio cost (more time elapsed)
- No responding for T → next response is reinforced (CRF)
- Each reinforcement resets the function (contrast with Adj, which accumulates)

### Naming collision resolution

"Interlocking" in the DSL refers to Ferster & Skinner (1957) schedules.
Glenn (2004) "Interlocking Behavioral Contingencies" (metacontingency) uses the
annotation keyword `@ibc` (renamed from `@interlocking` to resolve the naming
collision). See `INTERLOCK_SCHEDULE_DESIGN_2026-04-13.md` §6.

### Linter warnings

| Condition | Code | Rationale |
|-----------|------|-----------|
| `R0` == 1 | `INTERLOCK_TRIVIAL_RATIO` | R0=1 is always CRF (ratio cannot decrease below 1). Effectively FT(T). |
| `R0` > 500 | `INTERLOCK_LARGE_RATIO` | Very high initial ratio may produce ratio strain. F&S 1957 used R0=300. |

References:
- Ferster, C. B., & Skinner, B. F. (1957). *Schedules of reinforcement*.
  Appleton-Century-Crofts.
- Berryman, R., & Nevin, J. A. (1962). Interlocking schedules of reinforcement.
  *JEAB*, 5(2), 213-223. https://doi.org/10.1901/jeab.1962.5-213
- Powers, R. B. (1968). Clock-delivered reinforcers in conjunctive and
  interlocking schedules. *JEAB*, 11(5), 579-586.
  https://doi.org/10.1901/jeab.1968.11-579
