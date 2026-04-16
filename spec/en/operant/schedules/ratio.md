# Ratio Schedules — FR, VR, RR

> Part of the contingency-dsl operant layer. Response-based reinforcement schedules where the parameter specifies a response count.

---

## 1. Scope

Ratio schedules form the Ratio column of the 3×3 atomic taxonomy (`operant/theory.md §1.1`). The parameter `n` specifies the number of responses required for reinforcement; reinforcement is response-dependent and time-independent.

| Schedule | Distribution | Semantics | Canonical reference |
|---|---|---|---|
| **FR(n)** | Fixed | Exactly `n` responses per reinforcer | Ferster & Skinner (1957, Ch. 3) |
| **VR(n)** | Variable | Fleshler-Hoffman (1962) non-replacement sequence with mean `n` | Ferster & Skinner (1957, Ch. 4) |
| **RR(n)** | Random | Per-response geometric draw with mean `n` | Farmer (1963) |

## 2. Operational Definitions

### 2.1 FR — Fixed Ratio

Reinforcement is delivered on every `n`-th response. The parameter is an integer `n ≥ 1`.

```
FR 5        -- every 5th response reinforced
FR 1 ≡ CRF  -- continuous reinforcement (identity of ratio dimension)
```

Denotation: `⟦Atomic(Fixed, Ratio, n)⟧` (see `operant/theory.md §2.13.3`).

### 2.2 VR — Variable Ratio

Reinforcement is delivered after a variable number of responses whose *mean* equals `n`. The variable values are drawn from the Fleshler-Hoffman (1962) non-replacement sequence, which guarantees:

- Mean of drawn values = `n`
- No value repeats within a single pass through the sequence
- Constant probability of reinforcement per response across the sequence

```
VR 20       -- mean 20 responses per reinforcer
```

The Fleshler-Hoffman sequence is the quasi-random generator specified in Fleshler & Hoffman (1962). See `procedure-annotator/temporal` `@algorithm("fleshler-hoffman")` for generator configuration.

### 2.3 RR — Random Ratio

Reinforcement is delivered with per-response probability `1/n`, yielding a geometric inter-reinforcement count distribution with mean `n`. Unlike VR, RR samples independently on each response (memoryless).

```
RR 20       -- each response reinforced with probability 1/20
```

Denotation: `⟦Atomic(Random, Ratio, n)⟧` uses a geometric draw per response.

## 3. VR vs RR — The Critical Distinction

VR and RR are often conflated in the literature but differ structurally:

| Property | VR | RR |
|---|---|---|
| Sampling | Without replacement from a constrained sequence | With replacement (memoryless) |
| Mean guarantee | Mean over the sequence = `n` (strict) | Expected mean = `n` (law of large numbers) |
| Typical behavior | High, steady response rate with post-reinforcement pause | High, steady response rate without characteristic pause |
| Reference | Fleshler & Hoffman (1962); Ferster & Skinner (1957) | Farmer (1963) |

The DSL distinguishes them at the type level: `Distribution ∈ {Fixed, Variable, Random}`.

## 4. Post-Reinforcement Pause

Ratio schedules characteristically produce post-reinforcement pauses that scale with the ratio size (Ferster & Skinner, 1957, Ch. 3–4). The pause is a behavioral outcome, not a DSL parameter. The DSL records only the schedule structure; pause prediction belongs to the analysis layer.

## 5. Compositions Involving Ratio Schedules

Ratio schedules are freely composable with combinators from `operant/schedules/compound.md`:

```
Conc(FR 10, VR 20)                          -- concurrent ratios; see compound.md §3
Chain(FR 5, FI 30-s)                        -- FR then interval (see compound.md)
Tand(VR 20, DRL 5-s)                        -- tandem with IRT constraint
```

The **concurrent VR-VR vs concurrent VI-VI distinction** (exclusive choice vs matching) is a behavioral outcome, not a DSL parameter; see `operant/theory.md §2.6`.

## 6. Second-Order Ratio Schedules

`FR n(Unit)` composes a ratio-overall with an inner unit schedule (Kelleher, 1966; Kelleher & Fry, 1962):

```
FR 5(FI 30-s)       -- 5 unit completions of FI 30-s yields reinforcement
```

A ratio-overall second-order schedule is equivalent to a tandem of `n` unit copies (in the absence of brief stimuli): `FR n(S) ≡ Repeat(n, S)`. See `operant/theory.md §2.11.1`.

## 7. Errors and Warnings

| Code | Condition | Severity |
|---|---|---|
| `ATOMIC_NONPOSITIVE_VALUE` | `n ≤ 0` | SemanticError |
| `ATOMIC_RATIO_NON_INTEGER` | `n` has a non-integer value | SemanticError |
| `ATOMIC_UNEXPECTED_TIME_UNIT` | Ratio schedule carries a time unit | SemanticError |

See `conformance/operant/errors.json` for the full registry.

## 8. Design Decisions

The 3×3 atomic grid treats Distribution and Domain as orthogonal. See `operant/theory.md §1.1–§1.3` for the product-type formalization and `docs/en/design-rationale.md` for the rationale behind the VR vs RR separation.

## References

- Farmer, J. (1963). Properties of behavior under random interval reinforcement schedules. *Journal of the Experimental Analysis of Behavior*, 6(4), 607–616. https://doi.org/10.1901/jeab.1963.6-607
- Ferster, C. B., & Skinner, B. F. (1957). *Schedules of reinforcement*. Appleton-Century-Crofts.
- Fleshler, M., & Hoffman, H. S. (1962). A progression for generating variable-interval schedules. *Journal of the Experimental Analysis of Behavior*, 5(4), 529–530. https://doi.org/10.1901/jeab.1962.5-529
- Kelleher, R. T. (1966). Conditioned reinforcement in second-order schedules. *Journal of the Experimental Analysis of Behavior*, 9(5), 475–485. https://doi.org/10.1901/jeab.1966.9-475
- Kelleher, R. T., & Fry, W. (1962). Stimulus functions in chained fixed-interval schedules. *Journal of the Experimental Analysis of Behavior*, 5(2), 167–173. https://doi.org/10.1901/jeab.1962.5-167
- Schoenfeld, W. N., & Cole, B. K. (1972). *Stimulus schedules: The t-τ systems*. Harper & Row.
