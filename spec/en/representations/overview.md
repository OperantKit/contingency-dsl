# Alternative Representations

> Part of the [contingency-dsl theory documentation](../operant/theory.md). See also the formal specification at [`t-tau.md`](t-tau.md).

---

## 1. The T-tau Coordinate System

The 3×3 lattice (Distribution × Domain) is not the only formalization of the reinforcement schedule space. Schoenfeld & Cole (1972) proposed the **T-tau system**, a time-based parameterization that represents schedules as recurring cycles.

**Definition.** The T-tau representation parameterizes time-dependent schedules as:

```
TTauParams := (T: ℝ⁺, τ: ℝ⁺)  where  0 < τ ≤ T
duty_cycle := τ / T  ∈ (0, 1]
```

- **T** — cycle duration (seconds).
- **τ** — reinforcement window within each cycle (seconds).
- **duty_cycle** — the fundamental reinforcement density parameter.

The relationship between the 3×3 lattice and T-tau is analogous to **Cartesian and polar coordinates**: two representations of the same space, each making different properties transparent.

### 1.1 Conversion Domain (Partial Mapping)

T-tau covers Interval and Time schedules but not Ratio schedules. Ratio schedules define reinforcement as a function of response count; this dimension cannot be expressed in time without assuming a response rate, which is a dependent variable (organism behavior), not a schedule parameter. This boundary is enforced at the type level.

| Lattice | → T-tau | Notes |
|---------|---------|-------|
| FI(t), FT(t) | TTau(T=t, τ=t) | FI/FT collapse (response-requirement lost) |
| VI(t), VT(t) | TTau(T=t, τ=t) | Distribution shape lost |
| RI(t), RT(t) | TTau(T=t, τ=t) | Distribution type lost |
| FR(n), VR(n), RR(n) | **Type error** | Response count ∉ time domain |

### 1.2 Reverse Conversion and Disambiguation

Reverse conversion requires explicit disambiguation: `domain` (Interval vs. Time) and `distribution` (Fixed, Variable, Random) must be provided by the caller, since T-tau does not encode these dimensions.

### 1.3 Sub-unity Duty Cycle (τ < T)

When `duty_cycle < 1.0`, the schedule has a temporal window shorter than the cycle — structurally analogous to a Limited Hold ([operant/theory.md §1.6](../operant/theory.md)). The reverse mapping produces `Schedule LH τ`. Note that Schoenfeld & Cole place τ at the cycle start, while LH in the Ferster-Skinner tradition opens after criterion satisfaction; this positional difference means the mapping is a structural approximation.

### 1.4 Relationship to LH

Despite the surface similarity, T-tau and LH are fundamentally distinct (as noted in [operant/theory.md §1.6](../operant/theory.md)): T-tau cycles are clock-driven and recurring; LH windows are event-triggered. T-tau with `duty_cycle = 1.0` has no LH analogue — the entire cycle is available.

### 1.5 Approximate Conversion for Ratio Schedules

A separated layer accepts an explicit IRT (inter-response time) assumption to produce approximate T-tau coordinates. The result is typed as `TTauApprox` (distinct from `TTauParams`) to prevent silent conflation of definition with performance data.

### 1.6 Contribution: Cross-Literature Procedure Comparison

By converting T-tau-parameterized procedures to the 3×3 lattice, researchers can identify which historical experiments used procedurally similar schedules under a different notation. Conversely, lattice-defined schedules can be expressed in T-tau coordinates for duty-cycle-based analyses. This bidirectional mapping enables systematic cross-literature comparison that was previously manual and error-prone.

---

## References

- Schoenfeld, W. N., & Cole, B. K. (1972). *Stimulus schedules: The t-τ systems*. Harper & Row.
- Schoenfeld, W. N., & Cole, B. K. (1975). What is a "schedule of reinforcement"? *Pavlovian Journal of Biological Science*, 10(1), 5–13. https://doi.org/10.1007/BF03000622
