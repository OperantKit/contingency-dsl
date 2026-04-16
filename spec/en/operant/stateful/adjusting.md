# Adjusting Schedule — `Adj`

> Part of the contingency-dsl Operant.Stateful sublayer. Criterion = f(trial outcome). Trial-outcome-dependent bidirectional parameter adjustment.

---

## 1. Origin

- Blough, D. S. (1958). A method for obtaining psychophysical thresholds from the pigeon. *Journal of the Experimental Analysis of Behavior*, 1(1), 31–43. https://doi.org/10.1901/jeab.1958.1-31
- Mazur, J. E. (1987). An adjusting procedure for studying delayed reinforcement. In M. L. Commons et al. (Eds.), *Quantitative analyses of behavior* (Vol. 5, pp. 55–73). Erlbaum.
- Richards, J. B., Mitchell, S. H., de Wit, H., & Seiden, L. S. (1997). Determination of discount functions in rats with an adjusting-amount procedure. *Journal of the Experimental Analysis of Behavior*, 67(3), 353–366. https://doi.org/10.1901/jeab.1997.67-353

Adjusting schedules provide bidirectional (increase/decrease) parameter adaptation based on recent trial outcomes. The canonical use is the Mazur (1987) adjusting-delay procedure for measuring delay discounting.

## 2. Admission Gate

`Adj` qualifies for Operant.Stateful under `spec/en/design-philosophy.md §2.1`. Named procedure with primary literature (Blough, 1958; Mazur, 1987), 60+ years of use, extensive JEAB publication, cross-lab replication in delay-discounting research, and applied/translational use (human choice experiments). All parameters are declarative (runtime interprets the adjustment direction but the rule is parse-time-fixed).

## 3. Syntax

```
Adj(delay, start=10s, step=1s)                     -- minimal
Adj(delay, start=10s, step=2s, min=0s, max=120s)   -- with bounds
Adj(ratio, start=5, step=2)                        -- adjusting-ratio
Adj(amount, start=3, step=1, min=1, max=10)        -- adjusting-amount
Adjusting(delay, start=10s, step=1s)               -- verbose alias
```

## 4. Parameters

| Parameter | Position | Type | Required | Default | Description |
|---|---|---|---|---|---|
| `target` | positional 1 | enum | YES | — | What parameter is adjusted: `delay`, `ratio`, `amount` |
| `start` | keyword | value | YES | — | Initial parameter value |
| `step` | keyword | value | YES | — | Adjustment magnitude per step (additive) |
| `min` | keyword | value | NO | none | Lower bound on adjusted parameter |
| `max` | keyword | value | NO | none | Upper bound on adjusted parameter |

## 5. Target Dimensions

| Target | Adjusted parameter | Dimension | Implicit base contingency | Reference |
|---|---|---|---|---|
| `delay` | Reinforcement delay | time (unit required) | CRF + adjusting delay | Mazur (1987) |
| `ratio` | Response ratio requirement | dimensionless (integer) | Adjusting FR | Ferster & Skinner (1957) |
| `amount` | Reinforcer magnitude | dimensionless (runtime-interpreted) | CRF + adjusting amount | Richards et al. (1997) |

## 6. Semantics

```
Let P(t) be the adjusted parameter value at trial t.
P(0) = start.

After each reinforcement (or trial block completion):
  If "increase" criterion met:  P(t+1) = clamp(P(t) + step, min, max)
  If "decrease" criterion met:  P(t+1) = clamp(P(t) - step, min, max)
  Otherwise:                    P(t+1) = P(t)
```

The **increase/decrease direction rule** is delegated to the runtime. The DSL declares the parametric structure; the adjustment algorithm (e.g., Mazur's 4-trial block majority rule) is a runtime implementation detail, analogous to `@algorithm("fleshler-hoffman")` for VI value generation.

## 7. Integration Point

`Adj` extends `base_schedule` (not `modifier`), because it defines a standalone contingency structure rather than modifying a reinforcement criterion. This differs from `Pctl`, which extends `modifier`.

```ebnf
base_schedule ::= ... | adj_schedule
```

## 8. Relationship to PR

| | `PR(linear, start=1, increment=5)` | `Adj(ratio, start=5, step=2)` |
|---|---|---|
| Direction | Monotonic increase only | Bidirectional (behavior-dependent) |
| Change rule | Deterministic (fixed increment each reinforcement) | Behavior-dependent (recent performance) |
| Convergence | None (increases until breakpoint) | Yes (indifference point) |
| Layer | Operant.Literal (schedules/progressive.md) | Operant.Stateful (this file) |

The distinguishing criterion: PR's step function is indexed only by reinforcement count; `Adj` is conditioned on recent trial outcomes.

## 9. Semantic Constraints

| Code | Condition | Severity |
|---|---|---|
| `MISSING_ADJ_PARAM` | `start` or `step` omitted | SemanticError |
| `ADJ_UNKNOWN_TARGET` | `target` not in enum | SemanticError |
| `ADJ_NONPOSITIVE_START` | `start ≤ 0` | SemanticError |
| `ADJ_NONPOSITIVE_STEP` | `step ≤ 0` | SemanticError |
| `ADJ_TIME_UNIT_REQUIRED` | `delay` target without time unit | SemanticError |
| `ADJ_UNEXPECTED_TIME_UNIT` | `ratio` / `amount` target with time unit | SemanticError |
| `ADJ_INVALID_BOUNDS` | `min ≥ max` | SemanticError |
| `ADJ_START_OUT_OF_BOUNDS` | `start` outside `[min, max]` | SemanticError |
| `ADJ_RATIO_NOT_INTEGER` | `ratio` target with non-integer values | SemanticError |
| `DUPLICATE_ADJ_KW_ARG` | Duplicate keyword argument | SemanticError |
| `ADJ_UNBOUNDED_DELAY` | `delay` target without `max` | WARNING |
| `ADJ_LARGE_STEP` | `step > start` | WARNING |
| `ADJ_ZERO_MIN_DELAY` | `min=0` with `delay` target | WARNING |
| `ADJ_SUBUNIT_RATIO` | `ratio` target with `min < 1` | WARNING |

## References

See §1 for primary sources. Additional background:
- Ferster, C. B., & Skinner, B. F. (1957). *Schedules of reinforcement*. Appleton-Century-Crofts.
