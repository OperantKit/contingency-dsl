# Percentile Schedule — `Pctl`

> Part of the contingency-dsl Operant.Stateful sublayer. Criterion = f(response history). Response-history-dependent differential reinforcement.

---

## 1. Origin

- Platt, J. R. (1973). Percentile reinforcement. In G. H. Bower (Ed.), *The psychology of learning and motivation* (Vol. 7, pp. 271–296).
- Galbicka, G. (1994). Shaping in the 21st century: Moving percentile schedules into applied settings. *Journal of Applied Behavior Analysis*, 27(4), 739–760. https://doi.org/10.1901/jaba.1994.27-739

Percentile is a generalization of DRL/DRH with **dynamic** (adaptive) rather than fixed thresholds. The criterion at time `t+1` is computed from the distribution of recent values of a response dimension (IRT, latency, duration, force, rate).

## 2. Admission Gate

`Pctl` qualifies for Operant.Stateful under `spec/en/design-philosophy.md §2.1` (disciplinary-establishment criteria N1/N2/N3, evidence E1–E5). The schedule is named, has primary literature (Platt, 1973; Galbicka, 1994), exhibits temporal persistence (50+ years), and has JEAB/JABA publication, cross-lab replication, and textbook inclusion. All parameters are declarative.

## 3. Syntax

```
Pctl(IRT, 50)                            -- minimal
Pctl(IRT, 25, window=30)                 -- with window
Pctl(latency, 75, window=50, dir=above)  -- fully specified
```

## 4. Parameters

| Parameter | Position | Type | Required | Default | Description |
|---|---|---|---|---|---|
| `target` | positional 1 | enum | YES | — | Response dimension: `IRT`, `latency`, `duration`, `force`, `rate` |
| `rank` | positional 2 | integer 0–100 | YES | — | Percentile threshold |
| `window` | keyword | positive integer | NO | 20 | Recent responses used for the distribution |
| `dir` | keyword | enum | NO | `"below"` | Reinforcement direction: `"below"` or `"above"` |

## 5. Semantics

Let `R = [r_{n-m+1}, ..., r_n]` be the `m` most recent values of the target dimension (where `m = window`). Let `p_k = percentile(R, rank)`.

```
dir=below:  reinforce(r_{n+1}) ⟺ r_{n+1} ≤ p_k
dir=above:  reinforce(r_{n+1}) ⟺ r_{n+1} ≥ p_k
```

**Initial state.** Until `window` responses have been emitted, all responses are reinforced (CRF equivalent), per Platt (1973).

## 6. Relationship to DRL / DRH

Percentile is a generalization of DRL/DRH with dynamic thresholds. Both remain in the grammar:

- `DRL 5-s` — fixed criterion, Operant.Literal (static, decidable equivalence) — see `operant/schedules/differential.md`.
- `Pctl(IRT, 50)` — dynamic criterion, Operant.Stateful (runtime-dependent equivalence).

## 7. Integration Point

`Pctl` extends the `modifier` production in the operant grammar (see `operant/grammar.md §1.3`). It may appear wherever a modifier is permitted — standalone or composed with grid schedules via `Tand` or `Conj`.

## 8. Semantic Constraints

| Code | Condition | Severity |
|---|---|---|
| `PCTL_INVALID_RANK` | `rank` not integer in `[0, 100]` | SemanticError |
| `PCTL_INVALID_WINDOW` | `window ≤ 0` or non-integer | SemanticError |
| `PCTL_UNKNOWN_TARGET` | `target` not in enum | SemanticError |
| `PCTL_INVALID_DIR` | `dir` not `"below"` or `"above"` | SemanticError |
| `PCTL_UNEXPECTED_TIME_UNIT` | `rank` carries a time unit | SemanticError |
| `DUPLICATE_PCTL_KW_ARG` | Duplicate keyword argument | SemanticError |
| `PCTL_EXTREME_RANK` | `rank == 0` or `rank == 100` | WARNING |
| `PCTL_SMALL_WINDOW` | `window < 5` | WARNING |
| `PCTL_LARGE_WINDOW` | `window > 100` | WARNING |

## 9. Applied Use

The `method=percentile` form of the shaping primitive (`operant/grammar.md §3.8.4`) desugars to `Pctl(...)` plus a stability criterion. Galbicka (1994) describes applications to clinical shaping in which the researcher wants automated adaptation to the subject's current response distribution rather than hand-tuned fixed thresholds.

## References

See §1. Additional background:
- Alleman, H. D., & Platt, J. R. (1973). Differential reinforcement of interresponse times with controlled probability of reinforcement per response. *Learning and Motivation*, 4(1), 40–73. https://doi.org/10.1016/0023-9690(73)90036-2
