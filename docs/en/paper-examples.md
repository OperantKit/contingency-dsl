# Paper Examples

> Full JEAB Method sections translated into contingency-dsl.
> These examples demonstrate how real experiments map to multi-phase DSL programs.
> For syntax details, see [syntax-guide.md](syntax-guide.md). For single-construct examples, see [use-cases.md](use-cases.md).

---

## 1. Resurgence: ABA Design

**Paper:** Brown, T. L., Greer, B. D., Craig, A. R., Roane, H. S., & Shahan, T. A. (2020). Resurgence following differential reinforcement of alternative behavior implemented with and without extinction. *JEAB*, *113*(2), 449-467. https://doi.org/10.1002/jeab.590

**Design:** Three-phase ABA resurgence design. Baseline establishes target responding on a concurrent schedule, DRA introduces an alternative reinforcement source, and Extinction suspends all reinforcement to test for resurgence of the target response.

**DSL features demonstrated:** `phase`, `sessions`, `Conc`, program-level annotations

### Multi-phase file

```
-- Brown, Greer, Craig et al. (2020) JEAB 113(2), 449-467
-- Resurgence following DRA with and without extinction
-- Group: DRA Without Extinction

@species("rat") @strain("Long-Evans") @n(5)
@deprivation("80% free-feeding weight")
@chamber("Med-Associates", dimensions="30x24x21cm")
@reinforcer("food", type="pellet", magnitude="45mg", duration=3s)

phase Baseline:
  sessions = 25

  Conc(
    VI 60-s @operandum("left-lever") @sd("stimulus-light"),
    EXT     @operandum("right-lever")
  )

phase DRA:
  sessions = 14

  Conc(
    VI 60-s @operandum("target-lever") @sd("stimulus-light"),
    VI 15-s @operandum("nose-poke") @sd("yellow-LED"),
    COD=3-s
  )

phase ExtinctionTest:
  sessions = 5

  Conc(
    EXT @operandum("target-lever") @sd("stimulus-light"),
    EXT @operandum("nose-poke") @sd("yellow-LED")
  )
```

### Split files

Each phase can also be written as an independent program:

**brown2020_baseline.cdsl:**
```
-- Brown et al. (2020) — Phase 1: Baseline
@species("rat") @strain("Long-Evans") @n(5)
@reinforcer("food", type="pellet", magnitude="45mg", duration=3s)

Conc(
  VI 60-s @operandum("left-lever") @sd("stimulus-light"),
  EXT     @operandum("right-lever")
)
```

**brown2020_dra.cdsl:**
```
-- Brown et al. (2020) — Phase 2: DRA Without Extinction
@species("rat") @strain("Long-Evans") @n(5)
@reinforcer("food", type="pellet", magnitude="45mg", duration=3s)

Conc(
  VI 60-s @operandum("target-lever") @sd("stimulus-light"),
  VI 15-s @operandum("nose-poke") @sd("yellow-LED"),
  COD=3-s
)
```

**brown2020_extinction.cdsl:**
```
-- Brown et al. (2020) — Phase 3: Extinction Test
@species("rat") @strain("Long-Evans") @n(5)

Conc(
  EXT @operandum("target-lever") @sd("stimulus-light"),
  EXT @operandum("nose-poke") @sd("yellow-LED")
)
```

---

## 2. Behavioral Momentum: Resistance to Change

**Paper:** McLean, A. P., Grace, R. C., & Nevin, J. A. (2012). Response strength in extreme multiple schedules. *JEAB*, *97*(1), 51-70. https://doi.org/10.1901/jeab.2012.97-51

**Design:** Multiple schedule with extreme reinforcer rate ratios. Each condition establishes a stable baseline (minimum 20 sessions + visual stability), then tests resistance to change via prefeeding. Conditions differ in the reinforcer rate ratio between components.

**DSL features demonstrated:** `sessions >=`, `stable()`, `Mult`, `@session_end`, `@clock`

```
-- McLean, Grace, & Nevin (2012) JEAB 97(1), 51-70
-- Response strength in extreme multiple schedules

@species("pigeon") @n(4)
@deprivation("85% ad-lib weight")
@chamber("custom", dimensions="32x34x34cm")
@reinforcer("food", type="grain", duration=3s)
@clock(resolution=50ms)
@session_end(rule="time", time=120min)

-- Conditions differ per subject (counterbalanced).
-- This file describes Subject P5's sequence.

phase Condition1:
  sessions >= 20
  stable(visual, window=5)

  Mult(
    RI 40-s @sd("red") @reinforcer("food"),
    RI 40-s @sd("green") @reinforcer("food")
  )

phase RTC_Test1:
  sessions = 5
  -- prefeeding: 20g, 30g, 30g, 40g, 40g

  Mult(
    RI 40-s @sd("red") @reinforcer("food"),
    RI 40-s @sd("green") @reinforcer("food")
  )

phase Condition2:
  sessions >= 20
  stable(visual, window=5)

  Mult(
    RI 20-s @sd("red") @reinforcer("food"),
    RI 160-s @sd("green") @reinforcer("food")
  )

phase RTC_Test2:
  sessions = 5

  Mult(
    RI 20-s @sd("red") @reinforcer("food"),
    RI 160-s @sd("green") @reinforcer("food")
  )

-- ... (additional conditions omitted for brevity)
```

**Notes:**
- `sessions >= 20` specifies the minimum; actual session count depends on stability.
- `stable(visual, window=5)` declares that phase transition requires visual stability over 5 sessions. The specific algorithm is experimenter-determined at runtime.
- Counterbalancing of condition order across subjects is outside DSL scope.

---

## 3. Behavioral Momentum: Mass Accumulation

**Paper:** Craig, A. R., Cunningham, P. E., & Shahan, T. A. (2015). Behavioral momentum and accumulation of behavioral mass. *JEAB*, *103*(3), 437-449. https://doi.org/10.1002/jeab.145

**Design:** Multiple VI 30-s VI 120-s. Seven conditions vary the number of schedule-stimulus association sessions (1, 2, 3, 5, 20). Each condition is followed by a 5-session extinction test. Conditions repeat with different association durations.

**DSL features demonstrated:** `Mult`, `BO`, `@baseline`, `@algorithm`, phase-level annotations

```
-- Craig, Cunningham, & Shahan (2015) JEAB 103(3), 437-449
-- Behavioral momentum and mass accumulation

@species("pigeon") @n(8)
@deprivation("80% free-feeding weight")
@reinforcer("food", type="pigeon-checkers", duration=1.5s)
@algorithm("fleshler-hoffman")

-- Condition 1: 20-session blocks
phase Baseline_C1:
  sessions = 40  -- 2 blocks x 20 sessions

  Mult(
    VI 30-s @sd("color-A"),
    VI 120-s @sd("color-B"),
    BO=30-s
  )
  @session_end(rule="time", time=30min)
  @baseline(component_duration=3min, components_per_session=10, alternation="strict")

phase Extinction_C1:
  sessions = 5

  Mult(
    EXT @sd("color-A"),
    EXT @sd("color-B"),
    BO=30-s
  )
  @session_end(rule="time", time=30min)

-- Condition 2: 5-session blocks
phase Baseline_C2:
  sessions = 40

  Mult(
    VI 30-s @sd("color-A"),
    VI 120-s @sd("color-B"),
    BO=30-s
  )

phase Extinction_C2:
  sessions = 5

  Mult(
    EXT @sd("color-A"),
    EXT @sd("color-B"),
    BO=30-s
  )

-- ... (conditions 3-7 similarly)
```

**Notes:**
- `BO=30-s` specifies the blackout (inter-component interval), distinct from `component_duration`.
- `@baseline(...)` provides session structure metadata (component duration, alternation pattern).
- Repeated phase structures with identical schedules motivate the `use` keyword for phase reuse (see syntax guide).

---

## 4. Renewal After Punishment

**Paper:** Broomer, S. T., & Bouton, M. E. (2022). Renewal of operant behavior following punishment or extinction in different contexts. *Learning & Behavior*, *51*(3), 262-273. https://doi.org/10.3758/s13420-022-00543-1

**Design:** ABA renewal design comparing punishment and extinction. Response training in Context A, punishment (or extinction) in Context B, then test in both contexts. Tests whether context change renews punished behavior.

**DSL features demonstrated:** `Overlay`, `@context`, `@punisher`, `@session_end`

```
-- Broomer & Bouton (2022) Learn Behav 51(3), 262-273
-- Renewal after punishment vs extinction (Exp 1a)

@species("rat") @strain("Wistar") @n(32)
@deprivation("80% free-feeding weight")
@reinforcer("food", type="pellet", magnitude="45mg")

phase MagazineTraining:
  sessions = 1  -- per context

  EXT  -- RT 30-s (response-independent pellet delivery)
  @context("A") @context("B")  -- both contexts

phase ResponseTraining:
  sessions = 6

  RI 30-s @operandum("lever")
  @context("A")
  @session_end(rule="time", time=30min)

phase Punishment:
  sessions = 4

  Overlay(
    RI 30-s @reinforcer("food"),
    VI 90-s @punisher("shock", intensity="0.5mA", duration=0.5s)
  ) @operandum("lever")
  @context("B")

phase RenewalTest:
  sessions = 1

  EXT @operandum("lever")
  @session_end(rule="time", time=10min)
  -- Tested in both Context A and Context B (counterbalanced order)
```

**Notes:**
- `Overlay(RI 30-s, VI 90-s)` superimposes punishment on maintained reinforcement — the defining feature of punishment research (Azrin & Holz, 1966).
- `@context("A")` / `@context("B")` annotate the environmental context, which is the critical independent variable in renewal designs.
- The test phase is conducted in both contexts; counterbalancing of test order is outside DSL scope.

---

## Summary

| Example | Key Constructs | Research Domain |
|---------|---------------|-----------------|
| Brown et al. (2020) | `Conc`, `phase`, `sessions` | Resurgence / translational |
| McLean et al. (2012) | `Mult`, `sessions >=`, `stable()` | Behavioral momentum / parametric |
| Craig et al. (2015) | `Mult`, `BO`, `@baseline`, `@algorithm` | Behavioral momentum / mass |
| Broomer & Bouton (2022) | `Overlay`, `@context`, `@punisher` | Renewal / aversive control |

---

## References

- Azrin, N. H., & Holz, W. C. (1966). Punishment. In W. K. Honig (Ed.), *Operant behavior: Areas of research and application* (pp. 380-447). Appleton-Century-Crofts.
- Broomer, S. T., & Bouton, M. E. (2022). Renewal of operant behavior following punishment or extinction in different contexts. *Learning & Behavior*, *51*(3), 262-273. https://doi.org/10.3758/s13420-022-00543-1
- Brown, T. L., Greer, B. D., Craig, A. R., Roane, H. S., & Shahan, T. A. (2020). Resurgence following differential reinforcement of alternative behavior implemented with and without extinction. *JEAB*, *113*(2), 449-467. https://doi.org/10.1002/jeab.590
- Craig, A. R., Cunningham, P. E., & Shahan, T. A. (2015). Behavioral momentum and accumulation of behavioral mass. *JEAB*, *103*(3), 437-449. https://doi.org/10.1002/jeab.145
- McLean, A. P., Grace, R. C., & Nevin, J. A. (2012). Response strength in extreme multiple schedules. *JEAB*, *97*(1), 51-70. https://doi.org/10.1901/jeab.2012.97-51
