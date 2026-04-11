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
Conc(VI30s, VI60s, COD=2s)
```

**What this does:** Two response keys are simultaneously available. The left key operates on VI 30s, the right on VI 60s. After switching keys, a 2-second changeover delay must elapse before reinforcement becomes available on the new key.

**Why COD matters:** Without COD, rapid key-switching inflates the obtained reinforcement rate on both alternatives, destroying the orderly relationship between reinforcement rate and response allocation that the matching law describes (Herrnstein, 1961). Omitting COD in a concurrent VI-VI arrangement is a procedural concern. The DSL emits a linter WARNING (`MISSING_COD`) recommending explicit `COD` specification — `COD=0s` is accepted for control conditions and silences the warning. Omitting COD defaults to `COD=0s` at runtime.

**Reference:**
- Herrnstein, R. J. (1961). Relative and absolute strength of response as a function of frequency of reinforcement. *JEAB*, *4*, 267-272. https://doi.org/10.1901/jeab.1961.4-267
- Baum, W. M. (1974). On two types of deviation from the matching law. *JEAB*, *22*, 231-242. https://doi.org/10.1901/jeab.1974.22-231

---

## 3. Chained Schedule for Conditioned Reinforcement Research

**Scenario:** Testing whether stimulus change at component transitions functions as a conditioned reinforcer.

```
Chain(FR5, FI30s)
```

**What this does:** The pigeon first completes FR5 (initial link) in the presence of S^D-1 (e.g., red key light). Completion produces S^D-2 (e.g., green key light) and transitions to FI 30s (terminal link). Completing FI 30s produces food.

**Why it exists:** The stimulus change at the FR5→FI30 transition serves as a conditioned reinforcer — it signals proximity to food. Kelleher & Fry (1962) showed that the consistency of the stimulus-food distance relationship determines conditioned reinforcement strength. Without chaining, you cannot study how organisms learn to work through multi-step contingencies.

**Contrast with Tand:**
```
Tand(FR5, FI30s)   -- Same contingency, but NO stimulus change
```
Jwaideh (1973) showed that removing the stimulus change (Tand) shortens post-reinforcement pauses and weakens evidence of conditioned reinforcement — directly proving that the stimulus change is the active ingredient.

**References:**
- Kelleher, R. T., & Fry, W. T. (1962). Stimulus functions in chained fixed-interval schedules. *JEAB*, *5*, 167-173. https://doi.org/10.1901/JEAB.1962.5-167
- Jwaideh, A. R. (1973). Responding under chained and tandem fixed-ratio schedules. *JEAB*, *19*(2), 259. https://doi.org/10.1901/jeab.1973.19-259

---

## 4. Second-Order Schedule for Behavioral Pharmacology

**Scenario:** Maintaining stable cocaine self-administration behavior across a 2-hour session with infrequent drug delivery.

```
FI600(FR10)
```

**What this does:** The rat repeatedly completes FR10 units (10 lever presses per unit). After each unit, a brief stimulus (e.g., 2-second light previously paired with drug infusion) is presented. Once the FI 600s (10-minute) interval has elapsed and the next FR10 unit is completed, the rat receives a cocaine infusion.

**Why it exists:** In drug self-administration research, you need:

1. **Infrequent drug delivery** — too-frequent dosing saturates the pharmacological effect and prevents behavioral analysis
2. **Stable responding throughout** — without conditioned reinforcers, behavior collapses during long inter-reinforcement intervals
3. **Structured behavioral patterns** — the unit-level scalloping reveals motivational dynamics that a simple FR or FI cannot show

Second-order schedules solve all three problems. The brief stimulus acts as a conditioned reinforcer, bridging the gap between infrequent primary reinforcement episodes. Kelleher (1966) demonstrated that even with reinforcement as rare as once per 60 minutes (30 × FI 2min), the brief stimulus alone maintained orderly, scalloped responding in each FI component.

**Why not Tand?**
```
Tand(FI600, FR10)   -- NOT equivalent
```
Tand(FI600, FR10) means: wait 600 seconds, then complete one FR10. The organism does nothing during the 600-second wait. In contrast, `FI600(FR10)` has the organism actively completing FR10 units throughout the interval, producing data about the temporal pattern of behavior.

**References:**
- Kelleher, R. T. (1966). Conditioned reinforcement in second-order schedules. *JEAB*, *9*, 475. https://doi.org/10.1901/jeab.1966.9-475
- Goldberg, S. R. (1973). Comparable behavior maintained under fixed-ratio and second-order schedules of food presentation, cocaine injection or d-amphetamine injection in the squirrel monkey. *Journal of Pharmacology and Experimental Therapeutics*, *186*(1), 18-30.

---

## 5. Multiple Schedule for Behavioral Contrast

**Scenario:** Demonstrating that changing reinforcement in one context affects behavior in another.

```
Mult(VI60s, VI60s)     -- Phase 1: equal schedules in both components
Mult(VI60s, EXT)       -- Phase 2: extinction in component 2
```

**What this does:** Two components alternate (signaled by different key colors). In Phase 1, both have VI 60s. In Phase 2, component 2 switches to EXT. The prediction: response rate in component 1 *increases* despite its schedule being unchanged — this is behavioral contrast (Reynolds, 1961).

**Why it exists:** Multiple schedules isolate discriminative control from reinforcement effects. The discriminative stimuli (different key colors) tell the organism which schedule is in effect. Without discrimination (Mix), contrast effects are weaker or absent — proving that the stimulus-schedule correlation is necessary.

**Reference:**
- Reynolds, G. S. (1961). Behavioral contrast. *JEAB*, *4*(1), 57-71. https://doi.org/10.1901/jeab.1961.4-57

---

## 6. DRL for Timing Research

**Scenario:** Studying temporal discrimination — can the organism wait at least 20 seconds between responses?

```
DRL20s
```

**What this does:** Reinforcement is delivered only when the inter-response time (IRT) is ≥ 20 seconds. Responding too early resets the timer.

**Why it exists:** DRL produces a peaked IRT distribution centered near the required value, demonstrating that organisms can discriminate temporal intervals. The peak's precision reveals the organism's timing accuracy (Richards et al., 1993).

**With Limited Hold:**
```
DRL20s LH5s
```
Now the response must come between 20s and 25s after the previous response. Too early or too late — no reinforcement. This sharpens the temporal window and reveals finer-grained timing abilities (Kramer & Rilling, 1970).

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

## 8. Complex Real-World Experiment

**Scenario:** A two-component multiple schedule where one component uses a concurrent arrangement and the other uses a chained procedure, with program-level defaults.

```
COD = 2s
LH = 10s

let choice_component = Conc(VI30s, VI60s)
let chain_component = Chain(FR10, FI30s)
Mult(choice_component, chain_component)
```

**What this does:**
- Component 1 (S^D-1): Concurrent VI30 VI60 with 2s COD — the organism can allocate responses between two alternatives
- Component 2 (S^D-2): Chained FR10→FI30 — the organism first completes 10 responses, then waits ~30s for food
- Components alternate with discriminative stimulus changes
- All schedules have a 10s limited hold
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
| `let` | Readable complex programs | Unreadable nested expressions |

---

## References (Additional)

- Catania, A. C. (2013). *Learning* (5th ed.). Sloan Publishing.
- Cooper, J. O., Heron, T. E., & Heward, W. L. (2020). *Applied behavior analysis* (3rd ed.). Pearson.
- Ferster, C. B., & Skinner, B. F. (1957). *Schedules of reinforcement*. Appleton-Century-Crofts.
