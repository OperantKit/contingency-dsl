# Use Cases

> Practical scenarios showing what contingency-dsl enables and why each construct exists.
> For syntax details, see [syntax-guide.md](syntax-guide.md). For formal theory, see [theory.md](../../spec/en/theory.md).

---

## 1. Basic Operant Experiment

**Scenario:** A standard FR5 schedule for a pigeon key-peck experiment.

```
FR5
```

**What this does:** Every 5th key-peck produces food.

**Why it exists:** FR is the simplest ratio schedule. It generates high, steady response rates with characteristic post-reinforcement pauses (Ferster & Skinner, 1957, Ch. 3). This is the foundation of all reinforcement schedule research.

---

## 2. Concurrent Schedule with Changeover Delay

**Scenario:** Measuring preference between two VI schedules (the standard matching law procedure).

```
Conc(VI 30-s, VI 60-s, COD=2-s)
```

**What this does:** Two response keys are simultaneously available. The left key operates on VI 30-s, the right on VI 60-s. After switching keys, a 2-second changeover delay must elapse before reinforcement becomes available on the new key.

**Why COD matters:** Without COD, rapid key-switching inflates the obtained reinforcement rate on both alternatives, destroying the orderly relationship between reinforcement rate and response allocation that the matching law describes (Herrnstein, 1961). Omitting COD in a concurrent VI-VI arrangement is a procedural concern. The DSL emits a linter WARNING (`MISSING_COD`) recommending explicit `COD` specification — `COD=0-s` is accepted for control conditions and silences the warning. Omitting COD defaults to `COD=0-s` at runtime.

**Reference:**
- Herrnstein, R. J. (1961). Relative and absolute strength of response as a function of frequency of reinforcement. *JEAB*, *4*, 267-272. https://doi.org/10.1901/jeab.1961.4-267
- Baum, W. M. (1974). On two types of deviation from the matching law. *JEAB*, *22*, 231-242. https://doi.org/10.1901/jeab.1974.22-231

---

## 3. Chained Schedule for Conditioned Reinforcement Research

**Scenario:** Testing whether stimulus change (transition between discriminative stimuli marking schedule component shifts) at component transitions functions as a conditioned reinforcer.

```
Chain(FR 5, FI 30-s)
```

**What this does:** The pigeon first completes FR 5 (initial link) in the presence of S^D-1 (e.g., red key light). Completion produces S^D-2 (e.g., green key light) and transitions to FI 30-s (terminal link). Completing FI 30-s produces food.

**Why it exists:** The stimulus change at the FR 5→FI 30-s transition serves as a conditioned reinforcer — it signals proximity to food. Kelleher & Fry (1962) showed that the consistency of the stimulus-food distance relationship determines conditioned reinforcement strength. Without chaining, you cannot study how organisms learn to work through multi-step contingencies.

**Contrast with Tand:**
```
Tand(FR 5, FI 30-s)   -- Same contingency, but NO stimulus change
```
Jwaideh (1973) showed that removing the stimulus change (Tand) shortens post-reinforcement pauses and weakens evidence of conditioned reinforcement — directly proving that the stimulus change is the active ingredient.

**References:**
- Kelleher, R. T., & Fry, W. T. (1962). Stimulus functions in chained fixed-interval schedules. *JEAB*, *5*, 167-173. https://doi.org/10.1901/JEAB.1962.5-167
- Jwaideh, A. R. (1973). Responding under chained and tandem fixed-ratio schedules. *JEAB*, *19*(2), 259. https://doi.org/10.1901/jeab.1973.19-259

---

## 4. Second-Order Schedule for Behavioral Pharmacology

**Scenario:** Maintaining stable cocaine self-administration behavior across a 2-hour session with infrequent drug delivery.

```
FI 600-s(FR 10)
```

**What this does:** The rat repeatedly completes FR 10 units (10 lever presses per unit). After each unit, a brief stimulus (e.g., 2-second light previously paired with drug infusion) is presented. Once the FI 600-s (10-minute) interval has elapsed and the next FR 10 unit is completed, the rat receives a cocaine infusion.

**Why it exists:** In drug self-administration research, you need:

1. **Infrequent drug delivery** — too-frequent dosing saturates the pharmacological effect and prevents behavioral analysis
2. **Stable responding throughout** — without conditioned reinforcers, behavior collapses during long inter-reinforcement intervals
3. **Structured behavioral patterns** — the unit-level scalloping reveals motivational dynamics that a simple FR or FI cannot show

Second-order schedules solve all three problems. The brief stimulus acts as a conditioned reinforcer, bridging the gap between infrequent primary reinforcement episodes. Kelleher (1966) demonstrated that even with reinforcement as rare as once per 60 minutes (30 × FI 2-min), the brief stimulus alone maintained orderly, scalloped responding in each FI component.

**Why not Tand?**
```
Tand(FI 600-s, FR 10)   -- NOT equivalent
```
Tand(FI 600-s, FR 10) means: wait 600 seconds, then complete one FR 10. The organism does nothing during the 600-second wait. In contrast, `FI 600-s(FR 10)` has the organism actively completing FR 10 units throughout the interval, producing data about the temporal pattern of behavior.

**References:**
- Kelleher, R. T. (1966). Conditioned reinforcement in second-order schedules. *JEAB*, *9*, 475. https://doi.org/10.1901/jeab.1966.9-475
- Goldberg, S. R. (1973). Comparable behavior maintained under fixed-ratio and second-order schedules of food presentation, cocaine injection or d-amphetamine injection in the squirrel monkey. *Journal of Pharmacology and Experimental Therapeutics*, *186*(1), 18-30.

---

## 5. Multiple Schedule for Behavioral Contrast

**Scenario:** Demonstrating that changing reinforcement in one context affects behavior in another.

```
Mult(VI 60-s, VI 60-s)     -- Phase 1: equal schedules in both components
Mult(VI 60-s, EXT)         -- Phase 2: extinction in component 2
```

**What this does:** Two components alternate (signaled by different key colors). In Phase 1, both have VI 60-s. In Phase 2, component 2 switches to EXT. The prediction: response rate in component 1 *increases* despite its schedule being unchanged — this is behavioral contrast (Reynolds, 1961).

**Why it exists:** Multiple schedules isolate discriminative control from reinforcement effects. The discriminative stimuli (different key colors) tell the organism which schedule is in effect. Without discrimination (Mix), contrast effects are weaker or absent — proving that the stimulus-schedule correlation is necessary.

**Reference:**
- Reynolds, G. S. (1961). Behavioral contrast. *JEAB*, *4*(1), 57-71. https://doi.org/10.1901/jeab.1961.4-57

---

## 6. DRL for Timing Research

**Scenario:** Studying temporal discrimination — can the organism wait at least 20 seconds between responses?

```
DRL 20-s
```

**What this does:** Reinforcement is delivered only when the inter-response time (IRT) is ≥ 20 seconds. Responding too early resets the timer.

**Why it exists:** DRL produces a peaked IRT distribution centered near the required value, demonstrating that organisms can discriminate temporal intervals. The peak's precision reveals the organism's timing accuracy (Richards et al., 1993).

**With Limited Hold:**
```
DRL 20-s LH 5-s
```
Now the response must come between 20-s and 25-s after the previous response. Too early or too late — no reinforcement. This sharpens the temporal window and reveals finer-grained timing abilities (Kramer & Rilling, 1970).

**References:**
- Richards, R. W., Sabol, T. J., & Seiden, L. S. (1993). DRL interresponse-time distributions. *JEAB*, *60*, 361. https://doi.org/10.1901/jeab.1993.60-361
- Kramer, T. J., & Rilling, M. (1970). Differential reinforcement of low rates: A selective critique. *Psychological Bulletin*, *74*(4), 225-254. https://doi.org/10.1037/h0029813

---

## 7. Progressive Ratio for Motivation Assessment

**Scenario:** Measuring how "hard" an organism will work for a reinforcer (breakpoint analysis).

```
PR(hodos)
```

**What this does:** The ratio requirement increases after each reinforcement: 1, 2, 4, 6, 9, 12, 15, 20, 25, ... (Hodos, 1961). The session continues until the organism stops responding for a criterion period (breakpoint).

**Why it exists:** The breakpoint is a quantitative measure of reinforcer efficacy. Higher-value reinforcers produce higher breakpoints. In behavioral pharmacology, PR breakpoints compare the reinforcing strength of different drug doses.

**References:**
- Hodos, W. (1961). Progressive ratio as a measure of reward strength. *Science*, *134*(3483), 943-944. https://doi.org/10.1126/science.134.3483.943
- Richardson, N. R., & Roberts, D. C. S. (1996). Progressive ratio schedules in drug self-administration studies in rats. *Psychopharmacology*, *128*(4), 327-335. https://doi.org/10.1007/s002130050138

---

## 8. Sidman Free-Operant Avoidance

**Scenario:** Measuring avoidance behavior maintained by negative reinforcement, where responses postpone an otherwise scheduled shock.

```
Sidman(SSI=20-s, RSI=5-s)
  @punisher("shock", intensity="0.5mA")
  @operandum("lever")
```

**What this does:** In the absence of responses, shocks are delivered every 20 seconds (SSI = Shock-Shock Interval). Each lever press postpones the next shock by 5 seconds (RSI = Response-Shock Interval). Formally, `next_shock = max(last_shock + SSI, last_response + RSI)`. Well-trained rats maintain responding indefinitely, keeping the interval between responses slightly shorter than RSI.

**Why it exists:** Sidman (1953) demonstrated that avoidance behavior can be maintained without any explicit warning stimulus — the temporal contingency alone suffices. This became a foundational procedure for studying aversive control, anxiety models, and negative reinforcement in behavioral pharmacology. Sidman avoidance cannot be expressed in the F/V/R × R/I/T reinforcement schedule matrix because it has **two independent temporal parameters** with distinct semantics and a response-contingent rescheduling rule.

**Alias equivalence.** `@punisher` is used here to make the experimenter's intent explicit, but `@reinforcer` is an equivalent alias:

```
Sidman(SSI=20-s, RSI=5-s) @reinforcer("shock", intensity="0.5mA")  -- equivalent
```

Both forms produce the same AST node.

**Composition with other schedules.** Sidman can appear inside any compound combinator, e.g., as a link in a chained schedule (de Waard, Galizio, & Baron, 1979):

```
Chain(FR 10 @reinforcer("food"),
      Sidman(SSI=20-s, RSI=5-s) @punisher("shock"))
```

**References:**
- Sidman, M. (1953). Two temporal parameters of the maintenance of avoidance behavior by the white rat. *Journal of Comparative and Physiological Psychology*, *46*(4), 253-261. https://doi.org/10.1037/h0060730
- Hineline, P. N. (1977). Negative reinforcement and avoidance. In W. K. Honig & J. E. R. Staddon (Eds.), *Handbook of operant behavior* (pp. 364-414). Prentice-Hall.
- de Waard, R. J., Galizio, M., & Baron, A. (1979). Chained schedules of avoidance. *JEAB*, *32*(3), 399-407. https://doi.org/10.1901/jeab.1979.32-399

---

## 9. Operant Variability with Lag Schedule

**Scenario:** Reinforcing response variability directly — training a subject to
emit response patterns that differ from recent responses. Used in applied
settings (ASD language therapy, creativity research) and basic research
(operant variability, Neuringer's program).

```
Lag(5, length=8)
  @reinforcer("grain")
  @operandum("left_key") @operandum("right_key")
```

**What this does:** The subject emits 8-peck sequences on two keys (LLLLLLLL,
LLLLLLLR, ..., RRRRRRRR = 256 possible sequences). A sequence is reinforced
only if it differs from each of the previous 5 sequences (Page & Neuringer,
1985). Well-trained pigeons produce near-random sequence distributions under
Lag 50 (Experiment 3), demonstrating that variability itself is a reinforceable
operant dimension.

**Why it exists:** Page & Neuringer (1985) showed that reinforcement
contingencies can directly control response variability, overturning Schwartz's
(1980) conclusion that variability cannot be operantly reinforced. This became
the foundational procedure for operant variability research and has been used in
ASD stereotypy reduction (Miller & Neuringer, 2000), autism mand training (Lee,
McComas, & Jawor, 2002), and creativity studies.

**Simple form for applied research.** For individual-response variability
(e.g., mand training), omit `length` — it defaults to 1:

```
Lag 5
  @reinforcer("praise+token")
  @target("varied mand across requests")
```

This treats each individual response (mand, tact, or lever press) as the unit,
reinforcing only responses that differ from the previous 5.

**Lag 0 as a control condition.** `Lag 0` is legal and is semantically
equivalent to CRF — useful as an explicit control in experiments comparing
"variability-required" vs "variability-allowed" conditions (Page & Neuringer's
Experiment 5 yoked control):

```
Mult(Lag(5, length=8), Lag 0)    -- variability vs no-variability baseline
```

**Composition with Mult.** A common pattern in Neuringer's program is to
alternate variability training with a CRF baseline or fixed-pattern schedule:

```
Mult(Lag(5, length=8), CRF, BO=5-s)
  @sd("red_light", component=1)
  @sd("green_light", component=2)
  @reinforcer("grain")
```

**References:**
- Page, S., & Neuringer, A. (1985). Variability is an operant. *Journal of Experimental Psychology: Animal Behavior Processes*, *11*(3), 429-452. https://doi.org/10.1037/0097-7403.11.3.429
- Neuringer, A. (2002). Operant variability: Evidence, functions, and theory. *Psychonomic Bulletin & Review*, *9*(4), 672-705. https://doi.org/10.3758/BF03196324
- Miller, N., & Neuringer, A. (2000). Reinforcing variability in adolescents with autism. *JABA*, *33*(2), 151-165. https://doi.org/10.1901/jaba.2000.33-151
- Lee, R., McComas, J. J., & Jawor, J. (2002). The effects of differential and lag reinforcement schedules on varied verbal responding by individuals with autism. *JABA*, *35*(4), 391-402. https://doi.org/10.1901/jaba.2002.35-391

---

## 10. Discriminated Avoidance

**Scenario:** A trial-based avoidance procedure where a warning signal (CS)
precedes an aversive stimulus (US). The subject can avoid the US by responding
during the CS-US interval. Used in fear conditioning, anxiety research, and
aversive control studies.

> **Keyword:** `DiscriminatedAvoidance` (short alias: `DiscrimAv`)

```
DiscriminatedAvoidance(CSUSInterval=10-s, ITI=3-min, mode=escape, MaxShock=2-min)
  @punisher("shock", intensity="1.0mA")
  @sd("light", modality="visual")
  @species("dog")
```

**What this does:** A light CS is presented. If the dog jumps the barrier within
10 seconds, shock is avoided (avoidance trial). If the dog fails to respond
within 10s, shock begins and continues until the dog jumps (escape trial), with
a 2-minute safety cutoff. The next CS appears 3 minutes after the current CS
onset regardless of trial outcome.

**Why it exists:** Solomon & Wynne (1953) demonstrated that discriminated
avoidance produces extremely persistent behavior — dogs continued to avoid after
hundreds of extinction trials. This paradigm is fundamental to understanding
anxiety, phobias, and the persistence of avoidance behavior in clinical
populations.

**Fixed-duration variant.** Some procedures use a brief, non-escapable US
(e.g., a 0.5s shock pulse):

```
DiscriminatedAvoidance(CSUSInterval=10-s, ITI=3-min, mode=fixed, ShockDuration=0.5-s)
  @punisher("shock", intensity="0.5mA")
```

**Composition with Chain.** A chained schedule where completing a food-
reinforced ratio transitions into a discriminated avoidance component:

```
Chain(FR 10 @reinforcer("food"),
      DiscrimAv(CSUSInterval=10-s, ITI=3-min, mode=escape))
```

**References:**
- Solomon, R. L., & Wynne, L. C. (1953). Traumatic avoidance learning: Acquisition in normal dogs. *Psychological Monographs: General and Applied*, 67(4), 1-19. https://doi.org/10.1037/h0093649

---

## 11. Punishment Overlay

**Scenario:** Studying the effect of response-contingent punishment on operant
behavior maintained by a reinforcement schedule. The baseline reinforcement
continues while punishment is added on top.

```
Overlay(VI 60-s, FR 1)
  @reinforcer("food")
  @punisher("shock", intensity="0.5mA")
```

**What this does:** Food reinforcement is delivered on a VI 60-s schedule.
Simultaneously, every response (FR 1) produces a brief shock. Both
contingencies operate on the same response stream. This allows the
experimenter to observe how punishment suppresses responding relative to the
unpunished baseline rate.

**Why it exists:** Azrin & Holz (1966) established the standard paradigm for
studying punishment: maintain responding with a reinforcement schedule, then
superimpose punishment of varying intensity or schedule. This reveals the
functional relationship between punishment parameters and response suppression,
while the baseline schedule ensures there is behavior to suppress.

**Intermittent punishment.** Not every response needs to be punished:

```
Overlay(VI 60-s, VI 30-s)
  @reinforcer("food")
  @punisher("shock", intensity="0.5mA")
```

**Concurrent baseline with punishment.** Punishment overlaid on a matching-law
preparation:

```
Overlay(Conc(VI 60-s, VI 180-s, COD=2-s), FR 1)
  @reinforcer("food")
  @punisher("shock", intensity="0.5mA")
```

**References:**
- Azrin, N. H., & Holz, W. C. (1966). Punishment. In W. K. Honig (Ed.), *Operant behavior: Areas of research and application* (pp. 380-447). Appleton-Century-Crofts.
- Todorov, J. C. (1971). Concurrent performances: Effect of punishment contingent on the switching response. *JEAB*, 16(1), 51-62. https://doi.org/10.1901/jeab.1971.16-51

---

## 12. Shaping with Percentile Schedule (Core-Stateful)

**Scenario:** Shaping lever-press IRT using a percentile schedule — the quantitative basis for automated shaping (Galbicka, 1994).

```
@species("Rattus norvegicus") @n(4)
@deprivation(hours=23, target="food")
Pctl(IRT, 50, window=20) @reinforcer("food pellets")
```

**What this does:** Reinforces lever presses whose IRT falls at or below the median of the last 20 IRTs. As the rat's IRTs shorten, the threshold automatically adapts — creating continuous shaping pressure without manual experimenter intervention.

**Why Pctl rather than DRL?**

| Schedule | Criterion | Adapts? | Use case |
|---|---|---|---|
| `DRL 5-s` | Fixed at 5 seconds | No | Maintain existing temporal discrimination |
| `Pctl(IRT, 50)` | Median of recent IRTs | Yes | Shape IRT toward shorter/longer values |

**Compound examples:**

```
-- Multiple schedule: shaping phase vs extinction control
Mult(Pctl(IRT, 50), EXT, BO=5-s)

-- Concurrent: shape different dimensions on different operanda
Conc(Pctl(IRT, 30), Pctl(force, 75, dir=above), COD=2-s)

-- Named binding for readability
let shaping = Pctl(IRT, 50, window=20)
Mult(shaping, EXT)
```

**Clinical application (ABA):**

```
-- Shape vocalization duration in ASD intervention
Pctl(duration, 50, window=15) @target("vocalization") @function("access")
```

**Key insight:** A single `Pctl(IRT, 50)` already performs shaping — the adaptive threshold ensures the distribution shifts continuously. Staged rank changes (50→40→30) control shaping speed and are handled by contingency-core phase transitions.

**References:**
- Platt, J. R. (1973). Percentile reinforcement. In G. H. Bower (Ed.), *The psychology of learning and motivation* (Vol. 7, pp. 271–296). Academic Press.
- Galbicka, G. (1994). Shaping in the 21st century. *JABA*, *27*(4), 739–760. https://doi.org/10.1901/jaba.1994.27-739
- Athens, E. S., Vollmer, T. R., & Pipkin, C. C. (2007). Shaping academic task engagement with percentile schedules. *JABA*, *40*(3), 475–488.

---

## 13. Complex Real-World Experiment

**Scenario:** A two-component multiple schedule where one component uses a concurrent arrangement and the other uses a chained procedure, with program-level defaults.

```
COD = 2-s
LH = 10-s

let choice_component = Conc(VI 30-s, VI 60-s)
let chain_component = Chain(FR 10, FI 30-s)
Mult(choice_component, chain_component)
```

**What this does:**
- Component 1 (S^D-1): Concurrent VI 30-s VI 60-s with 2-s COD — the organism can allocate responses between two alternatives
- Component 2 (S^D-2): Chained FR 10→FI 30-s — the organism first completes 10 responses, then waits ~30-s for food
- Components alternate with discriminative stimulus changes
- All schedules have a 10-s limited hold
- The `let` bindings make the multi-line program readable

**Why this matters:** Real experiments combine multiple schedule types. The DSL's composability means you can express any arrangement that the behavioral literature describes — and the named bindings keep complex designs readable.

---

## Summary: What Each Construct Enables

| Construct | Enables | Without It |
|-----------|---------|-----------|
| `Conc` | Preference measurement, matching law | Cannot study choice allocation |
| `Chain` / `Tand` | Multi-step contingencies, conditioned reinforcement | Limited to single-step schedules |
| `Mult` / `Mix` | Stimulus control, behavioral contrast | Cannot separate discrimination from reinforcement |
| `XX(YY)` second-order | Lean-schedule maintenance, drug self-admin | Behavior collapses under low reinforcement rates |
| `DRL` / `DRH` / `DRO` | IRT control, timing, omission training | Cannot reinforce temporal properties |
| `LH` | Temporal availability windows | Unlimited response opportunity distorts data |
| `PR` | Reinforcer efficacy measurement | No quantitative breakpoint metric |
| `COD` / `FRCO` | Clean concurrent data | Inflated reinforcement from rapid switching |
| `Sidman` | Free-operant avoidance, aversive control | Cannot express unsignaled avoidance procedures |
| `DiscrimAv` | Discriminated avoidance, fear conditioning, anxiety research | Cannot express trial-based CS-predicted avoidance |
| `Overlay` | Punishment overlay, suppression studies | Cannot express punishment on maintained behavior |
| `Lag` | Operant variability, ASD stereotypy reduction, creativity research | Cannot reinforce response variability directly |
| `Pctl` | Automated shaping, adaptive differentiation, clinical shaping | Manual shaping only; no quantitative criterion |
| `let` | Readable complex programs | Unreadable nested expressions |

---

## References (Additional)

- Catania, A. C. (2013). *Learning* (5th ed.). Sloan Publishing.
- Cooper, J. O., Heron, T. E., & Heward, W. L. (2020). *Applied behavior analysis* (3rd ed.). Pearson.
- Ferster, C. B., & Skinner, B. F. (1957). *Schedules of reinforcement*. Appleton-Century-Crofts.
