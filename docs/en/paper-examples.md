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
@cs(label="key_light", duration=8-s, modality="visual")
@us(label="food", intensity="4s_access", delivery="cancelled_on_cs_response")

phase autoshaping_acquisition:
  sessions = 5
  Pair.ForwardDelay(key_light, food, isi=8-s, cs_duration=8-s)

phase omission_contingency:
  sessions = 40
  Pair.ForwardDelay(key_light, food, isi=8-s, cs_duration=8-s) @omission(response="key_peck", during="cs")
```

**Notes:**
- The `@omission(response="key_peck", during="cs")` annotation declares the response→US-cancellation rule on the Pavlovian primitive. An analyzer/executor pass interprets the annotation: any matching response during the specified window suppresses US delivery on that trial.
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

## 10. Second-Order Cocaine Self-Administration with Dose-Response Sweep

**Paper:** John, W. S., & Nader, M. A. (2016). Dose-response procedures for cocaine self-administration in rhesus monkeys (Method style reference; see also Goldberg, 1973 for the canonical second-order formulation).

**Design:** A behavioral-pharmacology dose-response sweep in which each test dose is followed by a return-to-baseline period. The reinforcement schedule is a second-order schedule in which completion of an FR 30 response unit produces a brief stimulus, and the first FR 30 completed after a 600-s fixed interval elapses produces the cocaine infusion. Six unit doses are tested in sequence; between each pair, the monkey returns to a fixed reference dose for three or more stable sessions.

**DSL features demonstrated:** Second-order schedule notation `FI(FR)`, `progressive` with `interleave`, template phases, `@reinforcer` placeholder substitution

```
-- John & Nader (2016) — Cocaine dose-response with interleaved recovery
@species("rhesus monkey") @n(4)
@apparatus(chamber="primate-test", operandum="lever")
@reinforcer("cocaine", delivery="IV")

phase Recovery:
  sessions >= 3
  stable(visual)
  FI 600-s(FR 30)
  @reinforcer("cocaine", dose="0.1mg/kg")

progressive DoseResponse:
  steps dose = [0.003, 0.01, 0.03, 0.1, 0.3, 0.56]
  interleave Recovery
  sessions >= 5
  stable(visual)
  FI 600-s(FR 30)
  @reinforcer("cocaine", dose="{dose}mg/kg")
```

**Notes:**
- `FI 600-s(FR 30)` is a second-order schedule: the reinforcement schedule is FI 600-s, but each response unit is itself FR 30. Completion of an FR 30 within the interval produces a brief stimulus; the first FR 30 completed after 600-s produces the infusion.
- `phase Recovery` is declared **before** the `progressive` block. Because it is referenced by `interleave`, it becomes a **template** that does not appear standalone in the timeline.
- The `interleave Recovery` clause expands to 12 phases (6 doses + 6 recoveries) — matching the Method statement "*each dose was followed by a return to baseline*" 1:1.
- Cloned recoveries carry the literal `@reinforcer("cocaine", dose="0.1mg/kg")`; the `{dose}` placeholder does not leak into clones (annotation locality).

---

## 11. Free-Operant Avoidance with Pavlovian Revaluation

**Paper:** Fernando, A. B. P., Urcelay, G. P., Mar, A. C., Dickinson, A., & Robbins, T. W. (2014). Free-operant avoidance behavior by rats after reinforcer revaluation using opioid agonists and d-amphetamine. *Journal of Neuroscience*, *34*(18), 6286-6293. https://doi.org/10.1523/JNEUROSCI.4146-13.2014

**Design:** Three-phase reinforcer-revaluation paradigm for free-operant avoidance. (1) Acquisition under a Sidman schedule with a feedback stimulus contingent on responding. (2) Revaluation: non-contingent shock presentations paired (or unpaired) with a systemic drug treatment, in the absence of the lever. (3) Extinction test in the original avoidance schedule without reinforcer delivery. If avoidance is goal-directed, the revaluation manipulation should modulate test-phase responding.

**DSL features demonstrated:** `Sidman`, `no_schedule`, `advance when manual`, `progressive` shaping with manual gating

```
-- Fernando et al. (2014) — Sidman avoidance with reinforcer revaluation
@species("rat") @strain("Lister-hooded") @n(32)
@deprivation("free-feeding")
@chamber("operant-conditioning", dimensions="25x25x25cm")
@punisher("shock", intensity="0.5mA", duration=0.5-s)

-- Shaping the avoidance response across progressively denser shock schedules.
-- Advancement is experimenter-determined (the paper specifies incremental
-- tightening of the response-shock interval without a fixed criterion).
progressive ShapingAcquisition:
  steps rsi = [120, 60, 30]
  advance when manual
  Sidman(SSI=5-s, RSI={rsi}-s)
  @feedback_stimulus(duration=5-s)

phase AvoidanceTraining:
  sessions = 30
  Sidman(SSI=5-s, RSI=5-s)
  @feedback_stimulus(duration=5-s)

phase Revaluation:
  sessions = 4
  no_schedule
  @punisher("shock", intensity="0.5mA", delivery="unsignaled")
  @pharmacology(treatment="morphine_or_d-amphetamine", schedule="paired_vs_unpaired")

phase ExtinctionTest:
  sessions = 1
  Sidman(SSI=5-s, RSI=5-s)
  @punisher("none")
  @feedback_stimulus(duration=5-s)
```

**Notes:**
- `Sidman(SSI=5-s, RSI=5-s)` is the final free-operant avoidance schedule: responses postpone the shock by the RSI; shocks recur at SSI if no response.
- `no_schedule` in the Revaluation phase suspends the operant contingency while permitting Pavlovian US exposure — the structural feature that distinguishes revaluation from extinction.
- `advance when manual` makes the progressive shaping compatible with `sessions = N` or `sessions >= N`, reflecting the paper's narrative "the RSI was reduced incrementally" without a numerical criterion.
- The pharmacological manipulation (morphine or d-amphetamine, paired or unpaired with shock) is carried on an `@pharmacology` annotation; the schedule-level syntax remains drug-agnostic.

---

## 12. DRL + Peak Procedure (Timing Precision)

**Paper:** Eckard, M. L., & Kyonka, E. G. E. (2018). Differential reinforcement of low rates differentially decreased timing precision. *Behavioural Processes*, *151*, 111-118. https://doi.org/10.1016/j.beproc.2018.03.018

**Design:** A three-phase timing-precision study. (1) FI shaping: the reinforced interval is progressively lengthened from 2-s to 18-s under a rate-based advancement criterion. (2) Baseline peak procedure: 45 reinforced FI 18-s trials and 15 unreinforced 54-s probe trials per session, randomly ordered. (3) DRL intervention: responding on FI is replaced by DRL of varying parameter (9-s, 18-s, or 27-s). Timing accuracy and precision are measured from probe-trial response distributions.

**DSL features demonstrated:** `progressive` with `advance when criterion(...)`, `@trial_mix` structured annotation, `Mix` for free-operant trial composition, `LH` (limited hold)

```
-- Eckard & Kyonka (2018) — DRL effects on peak-procedure timing
@species("mouse") @n(32)
@deprivation("85% free-feeding weight")
@reinforcer("food", type="evaporated-milk", duration=3-s)

-- Phase 1: FI shaping with rate-based advancement
progressive FI_Shaping:
  steps v = [2, 4, 8, 12, 18]
  advance when criterion(metric="rate", threshold=>=10, window=3 sessions)
  sessions >= 5
  FI {v}-s LH 3-s

-- Phase 2: Peak-procedure baseline (45 FI + 15 probe per session)
phase PeakBaseline:
  sessions = 15

  @trial_mix(
    type="peak",
    components=[
      {role="reinforced", ref=0, count=45},
      {role="probe",      ref=1, count=15, duration=54-s}
    ],
    ordering_spec="random"
  )
  Mix(FI 18-s LH 3-s, EXT)

-- Phase 3: DRL intervention (one of three parameters per subject)
phase DRL_Intervention:
  sessions = 10
  DRL 18-s
  -- Group assignment (9, 18, 27) is handled by @group annotation at program level
```

**Notes:**
- `Mix(FI 18-s LH 3-s, EXT)` composes the two trial types of the peak procedure: the reinforced FI component and the unreinforced probe component (EXT). `@trial_mix` parameterizes the per-session composition and ordering.
- The `duration=54-s` on the probe role specifies the probe-trial length (3× the FI, a canonical peak-procedure parameter).
- `progressive` + `advance when criterion(metric="rate", ...)` captures the rate-based shaping schedule typical of timing research: advance when the subject has sustained ≥10 responses/min over 3 sessions.
- Across-group variation in the DRL parameter (9-s / 18-s / 27-s) is handled at the program level via `@group` or by splitting into parallel DSL files.

---

## 13. Token Stimuli in Concurrent Variable-Interval Schedules

**Paper:** Mazur, J. E., & Biondi, D. R. (2013). Pigeons' choices with token stimuli in concurrent variable-interval schedules. *Journal of the Experimental Analysis of Behavior*, *100*(2), 233-252. https://doi.org/10.1002/jeab.37

**Design:** Pigeons chose between two concurrent VI 60-s schedules that delivered token stimuli rather than primary reinforcement. A fixed number of tokens, earned across either key, triggered an exchange period in which each token was redeemed for food on FR 1. The number of tokens required before the exchange period is varied parametrically across conditions to test how delay-to-primary modulates allocation.

**DSL features demonstrated:** `progressive` with `step` across exchange-requirement parameter, `Conc` with structured `@reinforcer` carrying token-economy metadata

```
-- Mazur & Biondi (2013) — Token concurrent VI VI with parametric exchange requirement
@species("pigeon") @n(12)
@deprivation("85% free-feeding weight")
@chamber("two-key", dimensions="32x32x32cm")
@reinforcer("token",
            exchange_terminal="grain",
            exchange_schedule="FR 1")

progressive ExchangeRequirement:
  steps tokens_per_exchange = [2, 4, 8, 16]
  sessions >= 25
  stable(visual, window=5)

  Conc(
    VI 60-s @operandum("left-key") @sd("left-light"),
    VI 60-s @operandum("right-key") @sd("right-light"),
    COD=2-s
  )
  @reinforcer("token",
              tokens_per_exchange={tokens_per_exchange},
              exchange_terminal="grain",
              exchange_schedule="FR 1")
```

**Notes:**
- The operant schedule (`Conc(VI 60-s, VI 60-s)`) does not change across conditions; only the exchange requirement is manipulated. This isolates the delay-to-primary variable.
- Token economies are expressed as annotations on the reinforcer rather than as a dedicated combinator: the token itself is the proximate reinforcer; the exchange terminal is carried as metadata for analysis pipelines (matching-law fits, hyperbolic-delay fits).
- The progressive-phase count (4 in this illustration) mirrors the parametric sweep in the paper's Method; the exact number of conditions per subject is counterbalanced and is outside DSL scope.

---

## 14. Progressive Ratio with Reinforcer-Volume Sweep

**Paper:** Rickard, J. F., Body, S., Zhang, Z., Bradshaw, C. M., & Szabadi, E. (2009). Effect of reinforcer magnitude on performance maintained by progressive-ratio schedules. *Journal of the Experimental Analysis of Behavior*, *91*(1), 75-87. https://doi.org/10.1901/jeab.2009.91-75

**Design:** Rats responded under a progressive-ratio (exponential) schedule with a 0.6-M sucrose solution reinforcer whose volume was varied parametrically across sessions in the range 6–300 μL. The dependent measures include the highest completed ratio (the "break point"), overall response rate across ratios, and post-reinforcement pause. The study evaluates Killeen's (1994) MPR predictions for the bitonic rate-by-ratio function.

**DSL features demonstrated:** `PR(exponential)`, `progressive` with `step` across magnitude parameter, `@reinforcer` placeholder substitution

```
-- Rickard et al. (2009) — PR schedule with sucrose-volume sweep
@species("rat") @strain("Wistar") @n(15)
@deprivation("80% free-feeding weight")
@chamber("standard-operant", dimensions="25x25x25cm")
@reinforcer("sucrose-solution", concentration="0.6M")

progressive MagnitudeAssay:
  steps volume_ul = [6, 12, 25, 50, 100, 200, 300]
  sessions = 30
  PR(exponential)
  @reinforcer("sucrose-solution",
              concentration="0.6M",
              volume="{volume_ul}uL",
              delivery="dipper")
  @dependent_measure(variables=["break_point",
                                "rate_by_ratio",
                                "post_reinforcement_pause"])
```

**Notes:**
- `PR(exponential)` selects the exponential-progression form `a·e^(bn) − 1` (Roberts & Richardson, 1992); fixed-step progressions are expressible as `PR(fixed, step=N)`.
- The 7-step volume sweep matches the paper's Method and the conformance fixture in `conformance/experiment/progressive-training.json`.
- `@dependent_measure` declares the MPR-relevant measurement set so downstream analysis pipelines can emit the correct derived variables without reparsing the Method.

---

## 15. Omission versus Extinction in ABA Renewal

**Paper:** Rey, C. N., Thrailkill, E. A., Goldberg, K. L., & Bouton, M. E. (2020). Relapse of operant behavior after response elimination with an extinction or an omission contingency. *Journal of the Experimental Analysis of Behavior*, *113*(1), 274-287. https://doi.org/10.1002/jeab.568

**Design:** ABA renewal comparing extinction and omission (DRO) as response-elimination procedures. (1) Acquisition in Context A under a VI schedule. (2) Elimination in Context B with either extinction or a DRO whose target-behavior-absence interval is ramped upward to the final value. (3) Test in Contexts A and B, with or without response-independent reinforcer delivery. The question is whether omission attenuates ABA renewal relative to extinction.

**DSL features demonstrated:** `@context`, `progressive` with `advance when manual` + `sessions = N`, `DRO` schedule, composition with annotations for context-switch designs

```
-- Rey et al. (2020) — Omission vs extinction in ABA renewal
@species("rat") @strain("Wistar") @n(32)
@deprivation("80% free-feeding weight")
@reinforcer("food", type="pellet", magnitude="45mg")

phase Acquisition:
  sessions = 10
  VI 30-s @operandum("lever")
  @context("A")

-- Omission group: DRO interval is ramped to its final value across
-- three experimenter-gated steps before the full omission phase begins.
progressive OmissionShaping:
  steps t = [10, 15, 20, 25, 30]
  advance when manual
  sessions = 3
  DRO {t}-s @operandum("lever")
  @context("B")

phase OmissionElimination:
  sessions = 10
  DRO 30-s @operandum("lever")
  @context("B")

phase ExtinctionElimination:
  sessions = 10
  EXT @operandum("lever")
  @context("B")
  @group("extinction-comparison")

phase RenewalTest:
  sessions = 1
  EXT @operandum("lever")
  -- Tested in both Context A and Context B (counterbalanced order).
  @session_end(rule="time", time=30min)
```

**Notes:**
- `advance when manual` combined with `sessions = N` is the legal construct (Constraint 79 exception) for experimenter-determined progression of a parameter ramp over a fixed session count per step.
- The omission and extinction groups are expressed as parallel phases; group assignment is outside the schedule grammar and carried via `@group` at the program level.
- `@context("A")` / `@context("B")` labels the environmental context — the critical independent variable in renewal designs. Context-specific discriminative stimuli are not part of the contingency itself.

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
| John & Nader (2016) | `FI(FR)`, `progressive`, `interleave` | Behavioral pharmacology / second-order |
| Fernando et al. (2014) | `Sidman`, `no_schedule`, `advance when manual` | Free-operant avoidance / revaluation |
| Eckard & Kyonka (2018) | `@trial_mix`, `Mix`, `advance when criterion(...)` | Timing / DRL + peak |
| Mazur & Biondi (2013) | `Conc`, `progressive`, token `@reinforcer` | Token economy / choice |
| Rickard et al. (2009) | `PR(exponential)`, `progressive` volume sweep | Progressive ratio / magnitude |
| Rey et al. (2020) | `DRO`, `EXT`, `@context`, `advance when manual` | Omission / renewal |

---

## References

- Annau, Z., & Kamin, L. J. (1961). The conditioned emotional response as a function of intensity of the US. *Journal of Comparative and Physiological Psychology*, *54*(4), 428-432. https://doi.org/10.1037/h0042199
- Azrin, N. H., & Holz, W. C. (1966). Punishment. In W. K. Honig (Ed.), *Operant behavior: Areas of research and application* (pp. 380-447). Appleton-Century-Crofts.
- Broomer, S. T., & Bouton, M. E. (2022). Renewal of operant behavior following punishment or extinction in different contexts. *Learning & Behavior*, *51*(3), 262-273. https://doi.org/10.3758/s13420-022-00543-1
- Brown, P. L., & Jenkins, H. M. (1968). Auto-shaping of the pigeon's key-peck. *Journal of the Experimental Analysis of Behavior*, *11*(1), 1-8. https://doi.org/10.1901/jeab.1968.11-1
- Brown, T. L., Greer, B. D., Craig, A. R., Roane, H. S., & Shahan, T. A. (2020). Resurgence following differential reinforcement of alternative behavior implemented with and without extinction. *JEAB*, *113*(2), 449-467. https://doi.org/10.1002/jeab.590
- Craig, A. R., Cunningham, P. E., & Shahan, T. A. (2015). Behavioral momentum and accumulation of behavioral mass. *JEAB*, *103*(3), 437-449. https://doi.org/10.1002/jeab.145
- Eckard, M. L., & Kyonka, E. G. E. (2018). Differential reinforcement of low rates differentially decreased timing precision. *Behavioural Processes*, *151*, 111-118. https://doi.org/10.1016/j.beproc.2018.03.018
- Estes, W. K. (1948). Discriminative conditioning. II. Effects of a Pavlovian conditioned stimulus upon a subsequently established operant response. *Journal of Experimental Psychology*, *38*(2), 173-177. https://doi.org/10.1037/h0057525
- Estes, W. K., & Skinner, B. F. (1941). Some quantitative properties of anxiety. *Journal of Experimental Psychology*, *29*(5), 390-400. https://doi.org/10.1037/h0062283
- Fernando, A. B. P., Urcelay, G. P., Mar, A. C., Dickinson, A., & Robbins, T. W. (2014). Free-operant avoidance behavior by rats after reinforcer revaluation using opioid agonists and d-amphetamine. *Journal of Neuroscience*, *34*(18), 6286-6293. https://doi.org/10.1523/JNEUROSCI.4146-13.2014
- Goldberg, S. R. (1973). Comparable behavior maintained under fixed-ratio and second-order schedules of food presentation, cocaine injection, or d-amphetamine injection in the squirrel monkey. *Journal of Pharmacology and Experimental Therapeutics*, *186*(1), 18-30.
- Killeen, P. R. (1994). Mathematical principles of reinforcement. *Behavioral and Brain Sciences*, *17*(1), 105-135. https://doi.org/10.1017/S0140525X00033628
- Lovibond, P. F. (1983). Facilitation of instrumental behavior by a Pavlovian appetitive conditioned stimulus. *Journal of Experimental Psychology: Animal Behavior Processes*, *9*(3), 225-247. https://doi.org/10.1037/0097-7403.9.3.225
- Mazur, J. E., & Biondi, D. R. (2013). Pigeons' choices with token stimuli in concurrent variable-interval schedules. *Journal of the Experimental Analysis of Behavior*, *100*(2), 233-252. https://doi.org/10.1002/jeab.37
- McLean, A. P., Grace, R. C., & Nevin, J. A. (2012). Response strength in extreme multiple schedules. *JEAB*, *97*(1), 51-70. https://doi.org/10.1901/jeab.2012.97-51
- Rescorla, R. A., & Solomon, R. L. (1967). Two-process learning theory: Relationships between Pavlovian conditioning and instrumental learning. *Psychological Review*, *74*(3), 151-182. https://doi.org/10.1037/h0024475
- Rey, C. N., Thrailkill, E. A., Goldberg, K. L., & Bouton, M. E. (2020). Relapse of operant behavior after response elimination with an extinction or an omission contingency. *Journal of the Experimental Analysis of Behavior*, *113*(1), 274-287. https://doi.org/10.1002/jeab.568
- Rickard, J. F., Body, S., Zhang, Z., Bradshaw, C. M., & Szabadi, E. (2009). Effect of reinforcer magnitude on performance maintained by progressive-ratio schedules. *Journal of the Experimental Analysis of Behavior*, *91*(1), 75-87. https://doi.org/10.1901/jeab.2009.91-75
- Roberts, S., & Richardson, N. R. (1992). Self-administration of cocaine on a progressive ratio schedule in rats: Dose-response relationship and effect of haloperidol pretreatment. *Psychopharmacology*, *106*(2), 251-255.
- Williams, D. R., & Williams, H. (1969). Auto-maintenance in the pigeon: Sustained pecking despite contingent non-reinforcement. *Journal of the Experimental Analysis of Behavior*, *12*(4), 511-520. https://doi.org/10.1901/jeab.1969.12-511
