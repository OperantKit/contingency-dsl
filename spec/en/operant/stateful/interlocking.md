# Interlocking Schedule — `Interlock`

> Part of the contingency-dsl Operant.Stateful sublayer. Criterion = f(elapsed time, continuous). The only **deterministic** Operant.Stateful schedule: criterion is a continuous function of elapsed time, not of subject behavior.

---

## 1. Origin

- Ferster, C. B., & Skinner, B. F. (1957). *Schedules of reinforcement*. Appleton-Century-Crofts.
- Berryman, R., & Nevin, J. A. (1962). Interlocking schedules of reinforcement. *Journal of the Experimental Analysis of Behavior*, 5(2), 213–223. https://doi.org/10.1901/jeab.1962.5-213
- Powers, R. B. (1968). Clock-delivered reinforcers in conjunctive and interlocking schedules. *Journal of the Experimental Analysis of Behavior*, 11(5), 579–586. https://doi.org/10.1901/jeab.1968.11-579

## 2. Admission Gate

`Interlock` qualifies for Operant.Stateful under `spec/en/design-philosophy.md §2.1`. The original Ferster & Skinner (1957) formulation, with replication by Berryman & Nevin (1962) and Powers (1968), satisfies N1/N2/N3 and multiple evidence axes (E1 JEAB publication, E2 cross-lab replication, E4 parametric study).

## 3. Syntax

```
Interlock(R0=300, T=10min)       -- Ferster & Skinner (1957) original example
Interlock(R0=16, T=80s)          -- Powers (1968) condition
Interlocking(R0=250, T=5min)     -- verbose alias
```

## 4. Parameters

| Parameter | Position | Type | Required | Default | Description |
|---|---|---|---|---|---|
| `R0` | keyword | positive integer | YES | — | Initial ratio requirement (post-reinforcement) |
| `T` | keyword | time value | YES | — | Time window; at `t = T` the ratio requirement reaches 1 (CRF) |

## 5. Semantics

Ratio and interval requirements interlock: the ratio requirement **decreases linearly** as time elapses since the last reinforcement.

```
R(t) = max(1, ⌈R0 × (1 − t/T)⌉)

At t = 0:  R(0) = R0   (maximum ratio)
At t = T:  R(T) = 1    (CRF — first response reinforced)
At reinforcement: reset t₀ ← current_time
```

Behavioral implications:

- Fast responding → high ratio requirement (little time elapsed)
- Slow responding → low ratio requirement (time elapsed)
- No responding for `T` → first response reinforced (CRF equivalent)
- Each reinforcement resets the clock (non-cumulative)

## 6. Integration Point

Like `Adj`, `Interlock` extends `base_schedule` as a standalone schedule expression:

```ebnf
base_schedule ::= ... | interlock_schedule
```

## 7. Relationship to Conjunctive / Alternative

| Schedule | Reinforcement logic | Parameter nature |
|---|---|---|
| Conjunctive | AND (both requirements met) | Fixed |
| Alternative | OR (either requirement met) | Fixed |
| **Interlocking** | **Linked** (one modifies the other) | **Time-function, resets at reinforcement** |

## 8. Operant.Stateful Classification

`Interlock` is the only **deterministic** Operant.Stateful schedule. `Pctl` and `Adj` adapt to the subject's behavior; `Interlock`'s criterion is a continuous function of elapsed time alone, independent of behavior.

| Runtime state | Schedule | Nature |
|---|---|---|
| Response history (recent distribution) | `Pctl` | Adaptive |
| Trial outcome (recent performance) | `Adj` | Adaptive |
| **Elapsed time (continuous function)** | **`Interlock`** | **Deterministic** |

This classification is load-bearing: `Interlock`'s determinism is why it can live in the Operant.Stateful sublayer without violating the SEI properties P1–P3 (`architecture.md §4.1.1`). The criterion rule is parse-time-fixed; only the current threshold value varies as a deterministic function of time.

## 9. Naming Collision Resolution

"Interlocking" refers to Ferster & Skinner (1957) schedules in the DSL. Glenn (2004) "Interlocking Behavioral Contingencies" (metacontingency theory) uses the annotation `@ibc` to avoid collision. The `@ibc` annotation lives in `annotations/extensions/social-annotator`.

## 10. Semantic Constraints

| Code | Condition | Severity |
|---|---|---|
| `MISSING_INTERLOCK_PARAM` | `R0` or `T` omitted | SemanticError |
| `INTERLOCK_INVALID_R0` | `R0 ≤ 0` or non-integer | SemanticError |
| `INTERLOCK_UNEXPECTED_TIME_UNIT` | `R0` carries a time unit | SemanticError |
| `INTERLOCK_NONPOSITIVE_T` | `T ≤ 0` | SemanticError |
| `INTERLOCK_TIME_UNIT_REQUIRED` | `T` without time unit | SemanticError |
| `DUPLICATE_INTERLOCK_KW_ARG` | Duplicate keyword argument | SemanticError |
| `INTERLOCK_TRIVIAL_RATIO` | `R0 == 1` (effectively FT) | WARNING |
| `INTERLOCK_LARGE_RATIO` | `R0 > 500` | WARNING |

## References

See §1 for primary sources.
