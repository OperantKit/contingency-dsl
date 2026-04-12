# contingency-dsl Core-Stateful Defaults

Explicit documentation of all implicit defaults in the Core-Stateful layer.
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
