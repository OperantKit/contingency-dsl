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

## §2. Adjusting Schedule — `Adj` (planned)

Blough, D. S. (1958). *JEAB*, *1*(1), 31–43.
Mazur, J. E. (1987). In Commons et al. (Eds.), *Quantitative analyses of behavior* (Vol. 5, pp. 55–73).

Syntax design pending. See `.local/planning/` for design drafts.

## §3. Interlocking Schedule (planned)

Ferster, C. B., & Skinner, B. F. (1957). *Schedules of reinforcement*.

Syntax design pending. See `.local/planning/` for design drafts.
