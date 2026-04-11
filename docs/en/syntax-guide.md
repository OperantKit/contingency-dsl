# Syntax Guide

> A progressive guide to contingency-dsl syntax — from basic schedules to advanced constructs.
> For the formal grammar (BNF), see [grammar.md](../../spec/en/grammar.md).

---

## Level 1: Atomic Schedules

The building blocks. Every expression is a **two-letter type prefix** followed by a **value**.

```
FR5          -- Fixed Ratio 5: reinforce every 5th response
VI30s        -- Variable Interval 30s: reinforce the first response
             --   after a mean 30s interval (Fleshler-Hoffman distribution)
FT10s        -- Fixed Time 10s: deliver reinforcer every 10s regardless of behavior
```

### The 3 × 3 Grid

The first letter selects the **distribution** (how values are chosen), the second selects the **domain** (what the value measures):

|              | R (Ratio — responses) | I (Interval — time + response) | T (Time — time only) |
|--------------|----------------------|-------------------------------|---------------------|
| **F** (Fixed)    | FR5  | FI30s  | FT10s  |
| **V** (Variable) | VR20 | VI60s  | VT15s  |
| **R** (Random)   | RR10 | RI45s  | RT20s  |

Two special cases:
```
CRF          -- Continuous Reinforcement (= FR1): every response is reinforced
EXT          -- Extinction: no response is ever reinforced
```

### Notational Variants

All of these are **identical** — use whichever matches your context:

```
VI60         -- compact (most common in JEAB/JABA papers)
VI 60        -- whitespace-separated (Ferster & Skinner, 1957 style)
VI60s        -- with time unit (recommended when ambiguity is possible)
VI(60)       -- Python constructor form
```

---

## Level 2: Compound Schedules

Combine two or more schedules using **combinators**. The syntax is always `Combinator(schedule, schedule, ...)`.

### Parallel Combinators

```
Conc(VI30s, VI60s, COD=2s)    -- Concurrent: two schedules available simultaneously
                               --   COD (changeover delay) is required for Conc
Alt(FR10, FI5min)              -- Alternative: whichever schedule completes first
                               --   delivers reinforcement (OR logic)
Conj(FR5, FI30s)               -- Conjunctive: BOTH conditions must be met
                               --   before reinforcement (AND logic)
```

### Sequential Combinators

```
Chain(FR5, FI30s)              -- Chained: complete FR5, then FI30 with stimulus change
Tand(VR20, DRL5s)              -- Tandem: same as Chain but NO stimulus change
```

### Alternating Combinators

```
Mult(FR5, EXT)                 -- Multiple: FR5 and EXT alternate with stimulus change
Mix(FR5, FR10)                 -- Mixed: same but NO stimulus change
```

### Nesting

Combinators compose freely:

```
Conc(Chain(FR5, VI60s), Alt(FR10, FT30s), COD=2s)
```

---

## Level 3: Modifiers

### Differential Reinforcement

```
DRL5s        -- Low rate: reinforce only if IRT ≥ 5s (slow responding)
DRH2s        -- High rate: reinforce only if IRT ≤ 2s (fast responding)
DRO10s       -- Other behavior: reinforce absence of target for 10s
```

### Progressive Ratio

```
PR(hodos)                       -- Hodos (1961) step function
PR(linear, start=1, increment=5) -- Linear: 1, 6, 11, 16, ...
PR(exponential)                 -- Exponential growth
```

### Limited Hold

A **post-fix** modifier — reinforcement is available for a limited window:

```
FI30s LH10s                    -- FI 30s with 10s availability window
Conc(VI30s LH5s, VI60s LH10s, COD=2s) -- per-component hold
```

---

## Level 4: Second-Order Schedules ⚠️

**This is the syntax most likely to confuse newcomers.** It looks like a function call, but it is not.

```
FI120(FR10)      -- Second-order schedule
```

### What This Means

`FI120(FR10)` means:

> "Treat each completion of FR10 as a *unit*. Reinforce the first unit completion after 120 seconds have elapsed."

It does **NOT** mean "FI120 called with argument FR10" or "FI120 applied to FR10" in a programming sense. The parenthesized part is the **unit schedule** that the organism repeatedly performs.

### Reading the Syntax

```
FI120(FR10)
│     │
│     └── unit: the pattern repeated inside the interval
│         (complete 10 responses = 1 unit)
│
└── overall: the schedule that controls when units produce reinforcement
    (first unit completion after 120s = food)
```

### How It Works (Step by Step)

```
Time →
|── FR10 ──| brief |── FR10 ──| brief |── FR10 ──| brief |── FR10 ──| FOOD
                                                              ↑
                                                    FI 120s elapsed + unit done
```

1. The organism repeatedly completes FR10 (10 responses per unit)
2. After each unit, a **brief stimulus** may be presented (conditioned reinforcer)
3. Once 120 seconds have elapsed **AND** the next FR10 unit is completed → primary reinforcement (food)
4. The cycle restarts

### Why Not Just Use Tand?

`Tand(FI120, FR10)` means something **different**:

| | `Tand(FI120, FR10)` | `FI120(FR10)` |
|---|---|---|
| During FI interval | Wait (no responding required) | **Repeatedly complete FR10 units** |
| How many FR10? | Exactly 1 (after FI elapsed) | Multiple (throughout the interval) |
| Brief stimulus | None (tandem = no stimulus change) | After each unit completion |
| Behavioral pattern | FI scallop → FR run | **Unit-level scallops** within FI |

The distinction matters because second-order schedules maintain behavior under very lean (infrequent) reinforcement by using brief stimuli as conditioned reinforcers — this is impossible with Tand.

### More Examples

```
FR5(FI30s)       -- Complete 5 FI-30s units to earn reinforcement
                  --   (≈ 150s minimum, with FI scallop pattern in each unit)
VI60(FR20)       -- Complete FR20 units; after mean 60s, next unit → food
FR10(FR5)        -- Complete 10 FR5 units to earn reinforcement
                  --   (= 50 responses total, but structured as 10 bursts of 5)
```

### Where This Is Used

Second-order schedules are foundational in:

- **Behavioral pharmacology**: Drug self-administration under lean schedules (Kelleher, 1966)
- **Conditioned reinforcement research**: Testing what stimuli maintain behavior (Malagodi et al., 1973)
- **Long-session experiments**: Maintaining stable performance over hours with infrequent primary reinforcement

---

## Level 5: Program-Level Features

### Named Bindings

Assign names to schedules for readability:

```
let baseline = VI60s
let probe = Conc(VI30s, VI60s, COD=2s)
Mult(baseline, probe)
```

Names are expanded at parse time (macro substitution). No mutable state.

### Program-Level Defaults

Set parameters that apply to all matching constructs:

```
LH = 10s
COD = 2s
Conc(VI30s, VI60s)     -- inherits COD=2s, each component gets LH=10s
```

Local values override defaults:

```
LH = 10s
Conc(VI30s LH5s, VI60s, COD=2s)  -- VI30 uses LH=5s, VI60 uses LH=10s
```

---

## Quick Reference: Syntax Patterns

| Pattern | Type | Example | Meaning |
|---------|------|---------|---------|
| `XX##` | Atomic | `FR5` | Fixed Ratio 5 |
| `Comb(S, S, ...)` | Compound | `Conc(VI30, VI60, COD=2s)` | Concurrent |
| `DRx##` | Modifier | `DRL5s` | Differential reinforcement |
| `S LH##` | Limited Hold | `FI30 LH10` | Temporal availability window |
| `XX##(YY##)` | **Second-Order** | `FI120(FR10)` | Overall(Unit) |
| `let x = S` | Binding | `let a = VI60` | Named schedule |
| `Repeat(n, S)` | Sugar | `Repeat(3, FR10)` | = `Tand(FR10, FR10, FR10)` |

---

## References

- Ferster, C. B., & Skinner, B. F. (1957). *Schedules of reinforcement*. Appleton-Century-Crofts.
- Fleshler, M., & Hoffman, H. S. (1962). A progression for generating variable-interval schedules. *JEAB*, *5*(4), 529-530. https://doi.org/10.1901/jeab.1962.5-529
- Kelleher, R. T. (1966). Conditioned reinforcement in second-order schedules. *JEAB*, *9*, 475. https://doi.org/10.1901/jeab.1966.9-475
- Kelleher, R. T., & Gollub, L. R. (1962). A review of positive conditioned reinforcement. *JEAB*, *5*(S4), 543-597. https://doi.org/10.1901/jeab.1962.5-s543
- Malagodi, E. F., DeWeese, J., & Johnston, J. M. (1973). Second-order schedules. *JEAB*, *20*(3), 447-461. https://doi.org/10.1901/jeab.1973.20-447
- Catania, A. C. (2013). *Learning* (5th ed.). Sloan Publishing.
