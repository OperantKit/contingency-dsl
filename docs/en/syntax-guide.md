# Syntax Guide

> A progressive guide to contingency-dsl syntax — from basic schedules to advanced constructs.
> For the formal grammar (BNF), see [grammar.md](../../spec/en/grammar.md).

---

## Level 1: Atomic Schedules

The building blocks. Every expression is a **two-letter type prefix** followed by a **value**.

```
FR 5         -- Fixed Ratio 5: reinforce every 5th response
VI 30-s      -- Variable Interval 30-s: reinforce the first response
             --   after a mean 30-s interval (Fleshler-Hoffman distribution)
FT 10-s      -- Fixed Time 10-s: deliver reinforcer every 10-s regardless of behavior
```

### The 3 × 3 Grid

The first letter selects the **distribution** (how values are chosen), the second selects the **domain** (what the value measures):

|              | R (Ratio — responses) | I (Interval — time + response) | T (Time — time only) |
|--------------|----------------------|-------------------------------|---------------------|
| **F** (Fixed)    | FR 5  | FI 30-s  | FT 10-s  |
| **V** (Variable) | VR 20 | VI 60-s  | VT 15-s  |
| **R** (Random)   | RR 10 | RI 45-s  | RT 20-s  |

Two special cases:
```
CRF          -- Continuous Reinforcement (= FR1): every response is reinforced
EXT          -- Extinction: no response is ever reinforced
```

### Notational Variants

All of these are **identical** — use whichever matches your context:

```
VI 60-s      -- JEAB modern standard (recommended)
VI 60-sec    -- JEAB older papers (e.g., JEAB 1960s-1970s)
VI 60 s      -- space-separated unit (JEAB 1986, 2012)
VI 60 sec    -- space-separated unit (Ferster & Skinner, 1957)
VI 60-min    -- minutes (for longer intervals, e.g., VI 1-min)
VI 60 min    -- minutes, space-separated
VI 60s       -- attached unit (no separator)
VI60s        -- compact with unit
VI60         -- compact (unit implied)
VI 60        -- whitespace-separated, no unit (Ferster & Skinner, 1957)
```

---

## Level 2: Compound Schedules

Combine two or more schedules using **combinators**. The syntax is always `Combinator(schedule, schedule, ...)`.

### Parallel Combinators

```
Conc(VI 30-s, VI 60-s, COD=2-s)  -- Concurrent: two schedules available simultaneously
                                  --   COD (changeover delay) is required for Conc
Alt(FR 10, FI 5-min)              -- Alternative: whichever schedule completes first
                                  --   delivers reinforcement (OR logic)
Conj(FR 5, FI 30-s)              -- Conjunctive: BOTH conditions must be met
                                  --   before reinforcement (AND logic)
```

### Sequential Combinators

> **Stimulus change**: transition between discriminative stimuli marking schedule component shifts.

```
Chain(FR 5, FI 30-s)              -- Chained: complete FR 5, then FI 30-s with stimulus change
Tand(VR 20, DRL 5-s)              -- Tandem: same as Chain but NO stimulus change
```

### Alternating Combinators

```
Mult(FR 5, EXT)                 -- Multiple: FR 5 and EXT alternate with stimulus change
Mix(FR 5, FR 10)                -- Mixed: same but NO stimulus change
```

### Nesting

Combinators compose freely:

```
Conc(Chain(FR 5, VI 60-s), Alt(FR 10, FT 30-s), COD=2-s)
```

### Punishment Combinators

```
Overlay(VI 60-s, FR 1)                              -- punish every response
Overlay(Conc(VI 30-s, VI 60-s, COD=2-s), FR 1,
        target=changeover)                          -- punish changeovers only
                                                    --   (Todorov, 1971)

-- Response-class-specific punishment: PUNISH directive on Conc
Conc(VI 30-s, VI 60-s, COD=2-s, PUNISH(1->2)=FR 1, PUNISH(2->1)=FR 1)
                                                    -- asymmetric directional
Conc(VI 30-s, VI 60-s, COD=2-s, PUNISH(changeover)=FR 1)
                                                    -- all changeovers (shorthand)
Conc(VI 30-s, VI 60-s, COD=2-s, PUNISH(1)=VI 30-s)     -- component-targeted
                                                    --   (de Villiers, 1980)
```

### Compound Keyword Arguments

| Keyword | Combinator(s) | Form | Purpose |
|---|---|---|---|
| `COD` | Conc | `COD=2-s` (scalar) or `COD(1->2)=2-s` (directional) | Changeover delay (Catania, 1966) |
| `FRCO` | Conc | `FRCO=3` | Fixed-ratio changeover (Hunter & Davison, 1985) |
| `BO` | Mult, Mix | `BO=5-s` | Blackout between components (Reynolds, 1961) |
| `count` | Interpolate | `count=16` | Reinforcements in interpolated block |
| `onset` | Interpolate | `onset=3-min` | Delay before interpolation |
| `target` | Overlay | `target=changeover` or `target=all` | Response-class targeting (v1.y) |
| `PUNISH(...)` | Conc | `PUNISH(changeover)=S` / `PUNISH(x->y)=S` / `PUNISH(n)=S` | Response-class-specific punishment (v1.y) |

---

## Level 3: Modifiers

### Differential Reinforcement

```
DRL 5-s      -- Low rate: reinforce only if IRT ≥ 5-s (slow responding)
DRH 2-s      -- High rate: reinforce only if IRT ≤ 2-s (fast responding)
DRO 10-s     -- Other behavior: reinforce absence of target for 10-s
```

### Lag Schedule (Operant Variability)

Reinforce only if the current response differs from the previous *n* responses (Page & Neuringer, 1985):

```
Lag 5                   -- differ from each of the previous 5 responses
Lag(5, length=8)        -- 8-response sequence as the comparison unit
Lag 0                   -- no variability requirement (equivalent to CRF)
```

`Lag 1` is the most common clinical form (e.g., mand variability training). The optional `length` parameter specifies the response-unit size: `length=1` (default) means individual responses; `length=8` means 8-response sequences as in Page & Neuringer (1985).

Lag composes with compound schedules:

```
Mult(Lag(5, length=8), CRF, BO=5-s)   -- variability vs baseline
Conj(Lag 1, FR 3)                      -- varied AND 3 responses per reinforcer
```

### Progressive Ratio

```
PR(hodos)                       -- Hodos (1961) step function
PR(linear, start=1, increment=5) -- Linear: 1, 6, 11, 16, ...
PR(exponential)                 -- Exponential: Richardson & Roberts (1996)
PR(geometric, start=1, ratio=2) -- Geometric: 1, 2, 4, 8, 16, ...
```

### Percentile Schedule (Core-Stateful)

A differential reinforcement procedure where the criterion adapts to the subject's behavior:

```
Pctl(IRT, 50)                            -- Reinforce IRTs below the median
Pctl(IRT, 25, window=30)                 -- Below 25th percentile, 30-response window
Pctl(latency, 75, window=50, dir=above)  -- Latencies above 75th percentile
Pctl(force, 90, window=15, dir=above)    -- Force above 90th percentile
Pctl(duration, 10, window=20)            -- Short durations (below 10th percentile)
```

Unlike DRL/DRH (fixed thresholds), Pctl computes the criterion from the subject's recent response distribution. This is the quantitative basis for **shaping** (Galbicka, 1994).

Parameters: `target` (response dimension), `rank` (0–100 percentile), `window` (default 20), `dir` (`below`/`above`, default `below`).

### Limited Hold

A **post-fix** modifier — reinforcement is available for a limited window:

```
FI 30-s LH 10-s                    -- FI 30-s with 10-s availability window
Conc(VI 30-s LH 5-s, VI 60-s LH 10-s, COD=2-s) -- per-component hold
```

---

## Level 4: Second-Order Schedules ⚠️

> **Terminology note: component, unit, and link** — This DSL distinguishes three terms for positions within compound schedules.
> - **Component**: a position within `Conc` / `Mult` (e.g., each side of `Conc(VI 30-s, VI 60-s)`)
> - **Unit**: the repeated response pattern within a second-order schedule (e.g., `FR 10` in `FI 120-s(FR 10)`)
> - **Link**: a sequential position within `Chain` / `Tand` (e.g., the initial and terminal links of `Chain(FR 5, FI 30-s)`)

**This is the syntax most likely to confuse newcomers.** It looks like a function call, but it is not.

```
FI 120-s(FR 10)      -- Second-order schedule
```

### What This Means

`FI 120-s(FR 10)` means:

> "Treat each completion of FR10 as a *unit*. Reinforce the first unit completion after 120 seconds have elapsed."

It does **NOT** mean "FI120 called with argument FR10" or "FI120 applied to FR10" in a programming sense. The parenthesized part is the **unit schedule** that the organism repeatedly performs.

### Reading the Syntax

```
FI 120-s(FR 10)
│       │
│       └── unit: the pattern repeated inside the interval
│           (complete 10 responses = 1 unit)
│
└── overall: the schedule that controls when units produce reinforcement
    (first unit completion after 120-s = food)
```

### How It Works (Step by Step)

```
Time →
|── FR 10 ──| brief |── FR 10 ──| brief |── FR 10 ──| brief |── FR 10 ──| FOOD
                                                                ↑
                                                      FI 120-s elapsed + unit done
```

1. The organism repeatedly completes FR 10 (10 responses per unit)
2. After each unit, a **brief stimulus** (a short-duration stimulus presentation, typically functioning as a conditioned reinforcer) may be presented
3. Once 120 seconds have elapsed **AND** the next FR 10 unit is completed → primary reinforcement (food)
4. The cycle restarts

### Why Not Just Use Tand?

`Tand(FI 120-s, FR 10)` means something **different**:

| | `Tand(FI 120-s, FR 10)` | `FI 120-s(FR 10)` |
|---|---|---|
| During FI interval | Wait (no responding required) | **Repeatedly complete FR 10 units** |
| How many FR 10? | Exactly 1 (after FI elapsed) | Multiple (throughout the interval) |
| Brief stimulus | None (tandem = no stimulus change) | After each unit completion |
| Behavioral pattern | FI scallop → FR run | **Unit-level scallops** within FI |

The distinction matters because second-order schedules maintain behavior under very lean (infrequent) reinforcement by using brief stimuli as conditioned reinforcers — this is impossible with Tand.

### More Examples

```
FR 5(FI 30-s)    -- Complete 5 FI 30-s units to earn reinforcement
                  --   (≈ 150-s minimum, with FI scallop pattern in each unit)
VI 60-s(FR 20)   -- Complete FR 20 units; after mean 60-s, next unit → food
FR 10(FR 5)      -- Complete 10 FR 5 units to earn reinforcement
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
let baseline = VI 60-s
let probe = Conc(VI 30-s, VI 60-s, COD=2-s)
Mult(baseline, probe)
```

Names are expanded at parse time (macro substitution). No mutable state.

### Program-Level Defaults

Set parameters that apply to all matching constructs:

```
LH = 10-s
COD = 2-s
Conc(VI 30-s, VI 60-s)     -- inherits COD=2-s, each component gets LH=10-s
```

Local values override defaults:

```
LH = 10-s
Conc(VI 30-s LH 5-s, VI 60-s, COD=2-s)  -- VI 30-s uses LH=5-s, VI 60-s uses LH=10-s
```

---

## Level 6: Experiment Layer (Multi-Phase)

For across-session designs (A-B-A reversal, dose-response, parametric studies), the DSL provides `phase` and `shaping` declarations.

### Phase Declarations

A `phase` is a named program with a phase-change criterion (session count or stability):

```
phase Baseline:
  sessions = 25
  Conc(VI 30-s, VI 60-s, COD=2-s)

phase Reversal:
  sessions >= 10
  stable(visual)
  use Baseline      -- reuse Baseline's schedule expression
```

### Shaping (Parametric Progression)

`shaping` desugars to a numbered sequence of `phase` declarations. Useful for FI-progression training, dose-response, reinforcer-magnitude studies:

```
shaping FI_Training:
  steps v = [2, 4, 8, 12, 18]
  sessions >= 3
  stable(visual)
  FI {v}-s LH 3-s
```

Expands to `FI_Training_1, …, FI_Training_5` with the `{v}` placeholder substituted from the steps list.

### Interleave (Recovery / Intervening Baselines)

Add an `interleave R` clause to insert a clone of pre-declared phase `R` between every pair of generated phases. Default semantics is **intercalate** (a clone is also appended after the last generated phase). Use `no_trailing` to switch to intersperse.

```
phase Recovery:                       -- declared BEFORE the shaping (no forward refs)
  sessions >= 3
  stable(visual)
  FI 600-s(FR 30)
  @reinforcer("cocaine", dose="0.1mg/kg")

shaping DoseResponse:
  steps dose = [0.003, 0.01, 0.03, 0.1, 0.3, 0.56]
  interleave Recovery                 -- intercalate (default)
  sessions >= 5
  stable(visual)
  FI 600-s(FR 30)
  @reinforcer("cocaine", dose="{dose}mg/kg")
```

The `phase Recovery` declaration becomes a **template**: it does not appear standalone in the timeline. Instead, six clones (`Recovery_after_DoseResponse_1` … `Recovery_after_DoseResponse_6`) are interleaved with the six dose conditions, yielding 12 phases total — matching the John & Nader (2016) JEAB Method "*each dose was followed by a return to baseline*" 1:1.

Multiple `interleave` lines compose a gap block in declaration order:

```
shaping DR:
  steps v = [2, 4, 8]
  interleave Recovery
  interleave Probe        -- gap = [Recovery_clone, Probe_clone]
  ...
```

---

## Quick Reference: Syntax Patterns

| Pattern | Type | Example | Meaning |
|---------|------|---------|---------|
| `XX ##` | Atomic | `FR 5` | Fixed Ratio 5 |
| `Comb(S, S, ...)` | Compound | `Conc(VI 30-s, VI 60-s, COD=2-s)` | Concurrent |
| `DRx ##-s` | Modifier | `DRL 5-s` | Differential reinforcement |
| `Lag ##` | Modifier | `Lag 5` | Variability requirement (Page & Neuringer, 1985) |
| `S LH ##-s` | Limited Hold | `FI 30-s LH 10-s` | Temporal availability window |
| `XX ##-s(YY ##)` | **Second-Order** | `FI 120-s(FR 10)` | Overall(Unit) |
| `let x = S` | Binding | `let a = VI 60-s` | Named schedule |
| `Repeat(n, S)` | Sugar | `Repeat(3, FR 10)` | = `Tand(FR 10, FR 10, FR 10)` |
| `phase Name: ... S` | Experiment | `phase Baseline: sessions = 25 VI 60-s` | Named phase with criterion |
| `shaping Name: steps x = [...] S({x})` | Experiment | `shaping FI: steps v=[2,4,8] FI {v}-s` | Parametric phase progression |
| `interleave R [no_trailing]` | Experiment | `interleave Recovery` | Insert R-clones between (intercalate default) |

---

## References

- Ferster, C. B., & Skinner, B. F. (1957). *Schedules of reinforcement*. Appleton-Century-Crofts.
- Fleshler, M., & Hoffman, H. S. (1962). A progression for generating variable-interval schedules. *JEAB*, *5*(4), 529-530. https://doi.org/10.1901/jeab.1962.5-529
- Kelleher, R. T. (1966). Conditioned reinforcement in second-order schedules. *JEAB*, *9*, 475. https://doi.org/10.1901/jeab.1966.9-475
- Kelleher, R. T., & Gollub, L. R. (1962). A review of positive conditioned reinforcement. *JEAB*, *5*(S4), 543-597. https://doi.org/10.1901/jeab.1962.5-s543
- Malagodi, E. F., DeWeese, J., & Johnston, J. M. (1973). Second-order schedules. *JEAB*, *20*(3), 447-461. https://doi.org/10.1901/jeab.1973.20-447
- Page, S., & Neuringer, A. (1985). Variability is an operant. *JEAP*, *11*(3), 429-452. https://doi.org/10.1037/0097-7403.11.3.429
- Catania, A. C. (2013). *Learning* (5th ed.). Sloan Publishing.
