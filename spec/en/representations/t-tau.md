# T-tau Representation — Formal Definition

## Status: Draft

---

## 1. Overview

The T-tau system (Schoenfeld & Cole, 1972) is an alternative time-based parameterization
of reinforcement schedules. It represents all time-dependent schedules as recurring cycles
of length **T** seconds, within which a window of **τ** seconds permits reinforcement.

The fundamental control variable is the **duty cycle**: `dc = τ / T`.

This document formalizes T-tau as a **representation** of the contingency-dsl type system
(see [`DESIGN.md`](DESIGN.md)) and defines bidirectional conversion rules with the
3×3 lattice (Distribution × Domain).

### References

- Schoenfeld, W. N., & Cole, B. K. (1972). *Stimulus schedules: The t-τ systems*.
  Harper & Row.
- Schoenfeld, W. N., & Cole, B. K. (1975). What is a "schedule of reinforcement"?
  *Pavlovian Journal of Biological Science*, 10(1), 5–13.
  https://doi.org/10.1007/BF03000622

---

## 2. Formal Definition

### Definition 1: TTauParams

```
TTauParams := (T: ℝ⁺, τ: ℝ⁺)  where  0 < τ ≤ T
```

- **T** (cycle duration): The total length of one reinforcement cycle in seconds.
- **τ** (reinforcement window): The duration within each cycle during which
  a response may produce reinforcement. Must satisfy `0 < τ ≤ T`.

### Definition 2: Duty Cycle

```
duty_cycle(T, τ) := τ / T  ∈ (0, 1]
```

The duty cycle is the fundamental reinforcement density parameter.
When `duty_cycle = 1.0`, the entire cycle is a reinforcement window.

### Definition 3: Reinforcement Availability

```
is_available(t, T, τ) := 0 ≤ (t mod T) < τ
```

A response at elapsed time `t` produces reinforcement if and only if
the position within the current cycle falls within the τ window.

---

## 3. Conversion Domain

### Theorem 1: Partial Mapping

The T-tau representation covers a **proper subset** of the 3×3 lattice:

```
TTauConvertible := { S ∈ AtomicSchedule | S.domain ∈ {Interval, Time} }
```

**Ratio schedules (FR, VR, RR) are outside the T-tau domain.**

Proof sketch: Ratio schedules define reinforcement as a function of cumulative
response count. T-tau defines reinforcement as a function of elapsed time.
Response count cannot be expressed as a function of time without assuming a
response rate, which is a dependent variable (the organism's behavior under
the schedule), not an independent variable (the schedule's definition).
Embedding a dependent variable into a definitional transformation would
conflate schedule specification with schedule performance.

### Corollary: Type-Level Enforcement

```python
to_ttau(schedule: Atomic) -> TTauParams | RatioScheduleError
```

When `schedule.domain == Domain.RATIO`, the conversion function raises
`RatioScheduleError` rather than returning an approximate result.

---

## 4. Conversion Rules: Lattice → T-tau

### 4.1 Fixed Interval → T-tau

```
FI(t) → TTau(T=t, τ=t)       duty_cycle = 1.0
```

Rationale: In FI, the first response after `t` seconds produces reinforcement.
The entire cycle of length `t` is a reinforcement window in the sense that
once the interval elapses, reinforcement is immediately available.

### 4.2 Fixed Time → T-tau

```
FT(t) → TTau(T=t, τ=t)       duty_cycle = 1.0
```

Rationale: FT delivers reinforcement after `t` seconds regardless of responding.
The T-tau parameters are identical to FI; the distinction (response-dependent
vs. response-independent) is not captured by T-tau's (T, τ) parameterization.

**Information loss: FI and FT collapse to the same T-tau representation.**
The `response_required` dimension is lost. See §6 (Ambiguity Resolution).

### 4.3 Variable Interval / Variable Time → T-tau

```
VI(t) → TTau(T=t, τ=t)       duty_cycle = 1.0  (t = mean of distribution)
VT(t) → TTau(T=t, τ=t)       duty_cycle = 1.0
```

**Information loss:**
1. Distribution shape (Fleshler-Hoffman sequence, list length) is lost.
2. FI/FT ambiguity (same as §4.2).

### 4.4 Random Interval / Random Time → T-tau

```
RI(t) → TTau(T=t, τ=t)       duty_cycle = 1.0  (t = mean)
RT(t) → TTau(T=t, τ=t)       duty_cycle = 1.0
```

**Information loss:**
1. Distribution type (Random vs. Variable) is lost.
2. FI/FT ambiguity (same as §4.2).

### 4.5 Ratio Schedules → T-tau

```
FR(n) → RatioScheduleError
VR(n) → RatioScheduleError
RR(n) → RatioScheduleError
```

Not a conversion failure; this is the formal boundary of the T-tau representation.

---

## 5. Conversion Rules: T-tau → Lattice

The reverse conversion requires **disambiguation parameters** because T-tau
collapses information that the 3×3 lattice distinguishes.

### 5.1 Signature

```python
from_ttau(
    params: TTauParams,
    domain: Domain,              # INTERVAL or TIME (required)
    distribution: Distribution,  # FIXED, VARIABLE, or RANDOM (required)
) -> Atomic
```

Both `domain` and `distribution` are **mandatory** arguments.
There is no default — the caller must explicitly resolve the ambiguity.

### 5.2 Rules

```
TTau(T, τ) + domain=INTERVAL + dist=FIXED    → FI(T)   when τ = T
TTau(T, τ) + domain=TIME     + dist=FIXED    → FT(T)   when τ = T
TTau(T, τ) + domain=INTERVAL + dist=VARIABLE → VI(T)   when τ = T
TTau(T, τ) + domain=TIME     + dist=VARIABLE → VT(T)   when τ = T
TTau(T, τ) + domain=INTERVAL + dist=RANDOM   → RI(T)   when τ = T
TTau(T, τ) + domain=TIME     + dist=RANDOM   → RT(T)   when τ = T
```

### 5.3 Sub-unity Duty Cycle (τ < T)

When `τ < T` (duty_cycle < 1.0), the T-tau schedule has a "dead zone" of
`T - τ` seconds where reinforcement is unavailable. This corresponds to a
**Limited Hold** modifier on the lattice schedule:

```
TTau(T, τ) where τ < T
  + domain=INTERVAL + dist=FIXED
  → FI T LH τ
```

This mapping extends the conversion to sub-unity duty cycles by leveraging
the existing LH (Limited Hold) construct in the 3×3 lattice type system.

**Note:** Schoenfeld & Cole's original formulation places the τ window at
the **beginning** of the cycle (t ∈ [0, τ)), while LH in the Ferster-Skinner
tradition places the hold window **after** the interval elapses. This temporal
positioning difference means the mapping `TTau(T, τ<T) → Schedule LH τ` is
a **structural approximation**, not a strict equivalence. The conformance tests
document this distinction.

---

## 6. Ambiguity Resolution Protocol

### 6.1 FI ↔ FT Ambiguity

T-tau does not distinguish response-dependent (Interval) from
response-independent (Time) reinforcement. The `domain` parameter
in `from_ttau()` resolves this.

### 6.2 Distribution Ambiguity

T-tau does not encode whether parameter variation across cycles is
Fleshler-Hoffman (Variable), uniform random (Random), or constant (Fixed).
The `distribution` parameter in `from_ttau()` resolves this.

### 6.3 Round-Trip Property

For Interval and Time schedules with `duty_cycle = 1.0`:

```
from_ttau(to_ttau(schedule), domain=schedule.domain, distribution=schedule.dist) == schedule
```

This round-trip property holds **if and only if** the disambiguation
parameters match the original schedule. Conformance tests verify this.

---

## 7. Approximate Conversion (Separated Layer)

For Ratio schedules, an **approximate** conversion is available via a
separated function that requires explicit declaration of assumptions:

```python
@dataclass(frozen=True)
class IRTAssumption:
    """Assumed mean inter-response time (seconds)."""
    irt: float

@dataclass(frozen=True)
class TTauApprox:
    """T-tau approximation with explicit assumptions."""
    T: float
    tau: float
    assumption: IRTAssumption

def approximate_ttau(schedule: Atomic, irt: float) -> TTauApprox:
    """FR(n) ≈ TTau(T=n*irt, τ=n*irt) under IRT assumption."""
```

Key design decisions:
- `TTauApprox` is a **separate type** from `TTauParams` — they cannot be
  mixed in type-safe code.
- The `irt` parameter has **no default value** — the caller must provide it.
- The assumption is preserved in the result for traceability.

---

## 8. Conformance Tests

See `conformance/` directory:

| File | Purpose |
|------|---------|
| `to_ttau.json` | Lattice → T-tau conversion (including type errors for Ratio) |
| `from_ttau.json` | T-tau → Lattice conversion (with disambiguation params) |
| `roundtrip.json` | Lattice → T-tau → Lattice identity verification |
| `errors.json` | Invalid inputs, domain violations, constraint violations |
