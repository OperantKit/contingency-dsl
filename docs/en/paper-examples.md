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

## 5. Conditioned Emotional Response (CER)

**Paper:** Estes, W. K., & Skinner, B. F. (1941). Some quantitative properties of anxiety. *Journal of Experimental Psychology*, *29*(5), 390-400. https://doi.org/10.1037/h0062283

**Design:** An appetitive operant baseline (VI reinforcement for lever press) is first established to stability. A Pavlovian CS-shock pairing is then superimposed: during CS presentation, an unsignaled shock is delivered at CS offset regardless of responding. Response suppression during CS relative to the pre-CS baseline is the dependent measure.

**DSL features demonstrated:** Composed layer (operant × respondent), `Pair.ForwardDelay`, `@cs`, `@us`, `PhaseSequence`, `Stability`

```
-- Estes & Skinner (1941) — Conditioned Emotional Response
@species("rat") @n(12)
@deprivation("80% free-feeding weight")
@reinforcer("food", type="pellet")

PhaseSequence(
  Phase(
    name = "baseline",
    operant = VI 60-s,
    criterion = Stability(window=5, tolerance=0.10)
  ),
  Phase(
    name = "cer_training",
    operant = VI 60-s,
    respondent = Pair.ForwardDelay(tone, shock, isi=60-s, cs_duration=60-s),
    criterion = FixedSessions(n=10)
  )
)
@cs(label="tone", duration=60-s, modality="auditory")
@us(label="shock", intensity="0.5mA", delivery="unsignaled")
@iti(distribution="exponential", mean=120-s, jitter=30-s)
```

**Notes:**
- US delivery is Pavlovian (response-independent), which structurally distinguishes CER from punishment.
- The operant baseline and the Pavlovian overlay coexist within the same `Phase` because the two contingencies operate concurrently.
- See [composed/conditioned-suppression.md](../../spec/en/composed/conditioned-suppression.md) for the full composed specification.

---

## 6. Suppression Ratio with Operant Baseline (Annau & Kamin, 1961)

**Paper:** Annau, Z., & Kamin, L. J. (1961). The conditioned emotional response as a function of intensity of the US. *Journal of Comparative and Physiological Psychology*, *54*(4), 428-432. https://doi.org/10.1037/h0042199

**Design:** Parametric replication of CER using the suppression-ratio metric `SR = B / (A + B)`, where A is the response count during the pre-CS interval and B is the response count during the CS. Five shock-intensity groups were compared.

**DSL features demonstrated:** Composed layer, suppression-ratio measurement annotation, parametric phase progression via `progressive`

```
-- Annau & Kamin (1961) — Parametric shock-intensity CER
@species("rat") @strain("Sprague-Dawley") @n(30)
@deprivation("80% free-feeding weight")
@reinforcer("food", type="pellet")

phase Baseline:
  sessions = 10
  stable(visual, window=5)
  VI 150-s
  @operandum("lever")

progressive SuppressionAcquisition:
  steps intensity = ["0.28mA", "0.49mA", "0.85mA", "1.55mA", "2.91mA"]
  sessions = 10
  VI 150-s
  respondent = Pair.ForwardDelay(tone, shock, isi=180-s, cs_duration=180-s)
  @operandum("lever")
  @cs(label="tone", duration=180-s, modality="auditory")
  @us(label="shock", intensity="{intensity}", delivery="unsignaled")
  @dependent_measure(variables=["suppression_ratio"],
                     suppression_ratio={method="annau_kamin",
                                        pre_cs_window=180-s,
                                        cs_window=180-s})
```

**Notes:**
- The `@dependent_measure` annotation names the suppression-ratio procedure and its windowing convention. This keeps the A / B interval specification explicit and reproducible.
- `progressive` expands to five phases, one per intensity level, each preserving the same baseline structure.
- Annau and Kamin's finding: suppression-ratio acquisition is a graded function of US intensity, with stronger shocks producing steeper and deeper suppression.

---

## 7. Autoshaping of the Pigeon Key Peck (Brown & Jenkins, 1968)

**Paper:** Brown, P. L., & Jenkins, H. M. (1968). Auto-shaping of the pigeon's key-peck. *Journal of the Experimental Analysis of Behavior*, *11*(1), 1-8. https://doi.org/10.1901/jeab.1968.11-1

**Design:** Naive pigeons received forward Pavlovian pairings of a key-light CS with a grain US. No operant-response contingency was programmed; a key-peck was not required for grain delivery. Within a small number of trials, pigeons began to peck the lit key — a Pavlovian emergent response.

**DSL features demonstrated:** Composed layer (autoshaping as operant × respondent placement), `Pair.ForwardDelay` with a localized CS, `@cs` modality annotation

```
-- Brown & Jenkins (1968) — Auto-shaping of the pigeon's key-peck
@species("pigeon") @n(36)
@deprivation("80% free-feeding weight")
@chamber("picture-frame", dimensions="30x30x30cm")
@reinforcer("food", type="grain", duration=4-s)

Phase(
  name = "autoshaping_training",
  respondent = Pair.ForwardDelay(key_light, food, isi=8-s, cs_duration=8-s),
  criterion = FixedSessions(n=10)
)
@cs(label="key_light", duration=8-s, modality="visual")
@us(label="food", intensity="4s_access", delivery="unsignaled")
@iti(distribution="uniform", mean=60-s, jitter=30-s)
```

**Notes:**
- No operant production appears; the emerged key-peck is Pavlovian and is recorded via measurement annotations (not shown).
- The CS is **localized** (attached to a chamber operandum); this is what distinguishes sign-tracking from goal-tracking.
- See [composed/autoshaping.md](../../spec/en/composed/autoshaping.md) for the rationale placing autoshaping under Composed rather than Operant.

---

## 8. Negative Automaintenance / Omission (Williams & Williams, 1969)

**Paper:** Williams, D. R., & Williams, H. (1969). Auto-maintenance in the pigeon: Sustained pecking despite contingent non-reinforcement. *Journal of the Experimental Analysis of Behavior*, *12*(4), 511-520. https://doi.org/10.1901/jeab.1969.12-511

**Design:** A modification of Brown and Jenkins' autoshaping: the Pavlovian pairing is as in autoshaping, but a key-peck during CS presentation immediately cancels the scheduled US on that trial. If pecking were operant, it should extinguish under the omission contingency; if pecking is Pavlovian, it should persist despite losing reinforcers.

**DSL features demonstrated:** Composed layer, response→US-cancellation contingency, comparison with autoshaping

```
-- Williams & Williams (1969) — Negative automaintenance
@species("pigeon") @n(16)
@deprivation("80% free-feeding weight")
@reinforcer("food", type="grain", duration=4-s)

PhaseSequence(
  Phase(
    name = "autoshaping_acquisition",
    respondent = Pair.ForwardDelay(key_light, food, isi=8-s, cs_duration=8-s),
    criterion = FixedSessions(n=5)
  ),
  Phase(
    name = "omission_contingency",
    respondent = Pair.ForwardDelay(key_light, food, isi=8-s, cs_duration=8-s),
    operant_constraint = Overlay(EXT, cancel_us_on_response=true),
    criterion = FixedSessions(n=40)
  )
)
@cs(label="key_light", duration=8-s, modality="visual")
@us(label="food", intensity="4s_access", delivery="cancelled_on_cs_response")
```

**Notes:**
- The `@us delivery="cancelled_on_cs_response"` annotation names the contingency; the `operant_constraint` field expresses the structural response→US-cancellation term.
- Williams and Williams (1969) showed that pecking persists across ~40 sessions under the omission contingency despite losing most reinforcers — the empirical argument for Pavlovian (not operant) control of autoshaped pecking.
- See [composed/omission.md](../../spec/en/composed/omission.md) for the full specification.

---

## 9. Pavlovian-to-Instrumental Transfer (PIT)

**Paper:** Estes, W. K. (1948). Discriminative conditioning. II. Effects of a Pavlovian conditioned stimulus upon a subsequently established operant response. *Journal of Experimental Psychology*, *38*(2), 173-177. https://doi.org/10.1037/h0057525; Lovibond, P. F. (1983). Facilitation of instrumental behavior by a Pavlovian appetitive conditioned stimulus. *Journal of Experimental Psychology: Animal Behavior Processes*, *9*(3), 225-247. https://doi.org/10.1037/0097-7403.9.3.225

**Design:** Three-phase structure. (1) Pavlovian training: CS paired with US in the absence of the operant response. (2) Instrumental training: operant response reinforced with the US without CS exposure. (3) Transfer test: the CS is presented while the operant response is available, typically under extinction. The change in operant response rate during CS relative to matched no-CS intervals quantifies the transfer effect.

**DSL features demonstrated:** Composed layer, `PhaseSequence` with independent training histories, extinction test, `CSOnly` for the test phase

```
-- Estes (1948) / Lovibond (1983) — Pavlovian-to-Instrumental Transfer
@species("rat") @n(16)
@deprivation("22h food deprivation")
@reinforcer("food", type="pellet", magnitude="45mg")

PhaseSequence(
  Phase(
    name = "pavlovian_training",
    respondent = Pair.ForwardDelay(tone, food, isi=10-s, cs_duration=10-s),
    criterion = FixedSessions(n=8)
  ),
  Phase(
    name = "instrumental_training",
    operant = VI 60-s,
    criterion = Stability(window=5, tolerance=0.10)
  ),
  Phase(
    name = "transfer_test",
    operant = EXT,
    respondent = CSOnly(tone, trials=8),
    criterion = FixedSessions(n=1)
  )
)
@cs(label="tone", duration=10-s, modality="auditory")
@us(label="food", intensity="45mg_pellet", delivery="signaled")
@iti(distribution="exponential", mean=90-s)
```

**Notes:**
- The three phases are in **separate sessions** (or clearly separated blocks), which the `PhaseSequence` construct enforces.
- The transfer test uses `EXT` on the operant schedule so that CS effects are read out against zero baseline reinforcement.
- See [composed/pit.md](../../spec/en/composed/pit.md) for the general-vs-outcome-specific PIT distinction.

---

## Summary

| Example | Key Constructs | Research Domain |
|---------|---------------|-----------------|
| Brown et al. (2020) | `Conc`, `phase`, `sessions` | Resurgence / translational |
| McLean et al. (2012) | `Mult`, `sessions >=`, `stable()` | Behavioral momentum / parametric |
| Craig et al. (2015) | `Mult`, `BO`, `@baseline`, `@algorithm` | Behavioral momentum / mass |
| Broomer & Bouton (2022) | `Overlay`, `@context`, `@punisher` | Renewal / aversive control |
| Estes & Skinner (1941) | `Pair.ForwardDelay`, `@cs`, `@us`, composed | CER / aversive Pavlovian |
| Annau & Kamin (1961) | `progressive`, suppression ratio, composed | CER parametric / intensity |
| Brown & Jenkins (1968) | `Pair.ForwardDelay`, no operant, composed | Autoshaping / sign-tracking |
| Williams & Williams (1969) | operant_constraint, omission, composed | Negative automaintenance |
| Estes (1948) / Lovibond (1983) | `PhaseSequence`, `CSOnly`, composed | Pavlovian-to-Instrumental Transfer |

---

## References

- Annau, Z., & Kamin, L. J. (1961). The conditioned emotional response as a function of intensity of the US. *Journal of Comparative and Physiological Psychology*, *54*(4), 428-432. https://doi.org/10.1037/h0042199
- Azrin, N. H., & Holz, W. C. (1966). Punishment. In W. K. Honig (Ed.), *Operant behavior: Areas of research and application* (pp. 380-447). Appleton-Century-Crofts.
- Broomer, S. T., & Bouton, M. E. (2022). Renewal of operant behavior following punishment or extinction in different contexts. *Learning & Behavior*, *51*(3), 262-273. https://doi.org/10.3758/s13420-022-00543-1
- Brown, P. L., & Jenkins, H. M. (1968). Auto-shaping of the pigeon's key-peck. *Journal of the Experimental Analysis of Behavior*, *11*(1), 1-8. https://doi.org/10.1901/jeab.1968.11-1
- Brown, T. L., Greer, B. D., Craig, A. R., Roane, H. S., & Shahan, T. A. (2020). Resurgence following differential reinforcement of alternative behavior implemented with and without extinction. *JEAB*, *113*(2), 449-467. https://doi.org/10.1002/jeab.590
- Craig, A. R., Cunningham, P. E., & Shahan, T. A. (2015). Behavioral momentum and accumulation of behavioral mass. *JEAB*, *103*(3), 437-449. https://doi.org/10.1002/jeab.145
- Estes, W. K. (1948). Discriminative conditioning. II. Effects of a Pavlovian conditioned stimulus upon a subsequently established operant response. *Journal of Experimental Psychology*, *38*(2), 173-177. https://doi.org/10.1037/h0057525
- Estes, W. K., & Skinner, B. F. (1941). Some quantitative properties of anxiety. *Journal of Experimental Psychology*, *29*(5), 390-400. https://doi.org/10.1037/h0062283
- Lovibond, P. F. (1983). Facilitation of instrumental behavior by a Pavlovian appetitive conditioned stimulus. *Journal of Experimental Psychology: Animal Behavior Processes*, *9*(3), 225-247. https://doi.org/10.1037/0097-7403.9.3.225
- McLean, A. P., Grace, R. C., & Nevin, J. A. (2012). Response strength in extreme multiple schedules. *JEAB*, *97*(1), 51-70. https://doi.org/10.1901/jeab.2012.97-51
- Rescorla, R. A., & Solomon, R. L. (1967). Two-process learning theory: Relationships between Pavlovian conditioning and instrumental learning. *Psychological Review*, *74*(3), 151-182. https://doi.org/10.1037/h0024475
- Williams, D. R., & Williams, H. (1969). Auto-maintenance in the pigeon: Sustained pecking despite contingent non-reinforcement. *Journal of the Experimental Analysis of Behavior*, *12*(4), 511-520. https://doi.org/10.1901/jeab.1969.12-511
