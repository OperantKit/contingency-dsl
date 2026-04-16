# Time Schedules — FT, VT, RT

> Part of the contingency-dsl operant layer. Response-independent (non-contingent) reinforcement schedules. Reinforcement is delivered on a time basis regardless of whether the subject responds.

---

## 1. Scope

Time schedules form the Time column of the 3×3 atomic taxonomy (`operant/theory.md §1.1`). The parameter `t` specifies a time duration; reinforcement is delivered when time elapses, **independently of responding** (Zeiler, 1968; Lattal, 1972).

| Schedule | Distribution | Semantics | Canonical reference |
|---|---|---|---|
| **FT(t)** | Fixed | Reinforcer delivered every `t` seconds | Zeiler (1968); Herrnstein & Morse (1957) |
| **VT(t)** | Variable | Reinforcer delivered at variable intervals with mean `t` (Fleshler-Hoffman) | Zeiler (1968) |
| **RT(t)** | Random | Reinforcer delivered at random intervals with mean `t` | Lachter, Cole, & Schoenfeld (1971) |

## 2. Operational Definitions

### 2.1 FT — Fixed Time

A reinforcer is presented every `t` seconds, regardless of the subject's behavior. There is no response requirement.

```
FT 30-s     -- reinforcer every 30 seconds, response-independent
```

Characteristic behavioral pattern: positive acceleration (scalloping) despite response-independence (Herrnstein & Morse, 1957; Zeiler, 1968). This is one of the canonical demonstrations that temporal regularity alone can generate scalloped patterns without an operant contingency.

Denotation: `⟦Atomic(Fixed, Time, t)⟧` (see `operant/theory.md §2.13.3`). Response events do not affect state transitions or outcomes.

### 2.2 VT — Variable Time

Reinforcers are presented at variable intervals drawn from a Fleshler-Hoffman (1962) sequence with mean `t`.

```
VT 60-s     -- mean 60 s, response-independent
```

Behavioral pattern: steady or erratic responding distinct from FT (Zeiler, 1968). VT produces slower response decrement than conventional extinction under some conditions (Lattal, 1972), an asymmetry exploited in delay-of-reinforcement research.

### 2.3 RT — Random Time

Reinforcer onsets follow a Poisson process with mean inter-onset interval `t`. Unlike VT, RT is fully memoryless.

```
RT 60-s     -- Poisson-distributed deliveries, mean 60 s
```

Empirically, RT is less often used than FT/VT; Lachter, Cole, & Schoenfeld (1971) is the closest canonical demonstration.

## 3. Time vs Interval — Response Independence

Time schedules are the **non-contingent** column of the grid: reinforcement is delivered regardless of responding. Interval schedules (FI, VI, RI; see `operant/schedules/interval.md`) are contingent: the first response after the interval elapses is reinforced. This distinction is foundational — see `foundations/contingency-types.md` §1.

## 4. Adventitious Reinforcement and Superstition

Skinner's (1948) "superstition" experiment used FT-like procedures to demonstrate that response-independent reinforcement can maintain idiosyncratic response topographies through adventitious reinforcement. Time schedules are therefore central to the adventitious-reinforcement literature as well as the core 3×3 grid.

## 5. Response-Independent Delay of Reinforcement

Tandem `FT` is the canonical formalization of non-resetting unsignaled delay (Sizemore & Lattal, 1978):

```
Tand(VI 60-s, FT 5-s)        -- after VI satisfaction, wait 5 s regardless of responses
```

See `operant/theory.md §1.7` for the full reinforcement-delay treatment.

## 6. Compositions Involving Time Schedules

Time schedules participate in all compound combinators (see `operant/schedules/compound.md`):

```
Conc(VI 30-s, VT 60-s)          -- concurrent contingent-vs-noncontingent comparison
Mult(VI 60-s, VT 60-s)          -- Lachter (1971)-style rate-matched components
Chain(FR 5, FT 30-s)            -- chained ratio-then-time link
```

Because Time schedules are response-independent, they often serve as **control conditions** against which the effect of response contingencies can be measured (Herrnstein & Morse, 1957; Rachlin & Baum, 1972).

## 7. Errors and Warnings

| Code | Condition | Severity |
|---|---|---|
| `ATOMIC_NONPOSITIVE_VALUE` | `t ≤ 0` | SemanticError |
| `ATOMIC_TIME_UNIT_REQUIRED` | Time schedule without time unit | SemanticError |

See `conformance/operant/errors.json` for the full registry.

## 8. Design Decisions

FT and VT were standardized as a formal Domain by Catania (2013) and Zeiler (1968); the DSL treats Time as a first-class Domain rather than as a degenerate case of Interval with a zero response requirement. This reflects the procedural reality: FT and VT generate distinct behavioral patterns (Zeiler, 1968) and occupy a separate experimental role (control conditions, superstition research, delay arrangements).

## References

- Catania, A. C. (2013). *Learning* (5th ed.). Sloan.
- Fleshler, M., & Hoffman, H. S. (1962). A progression for generating variable-interval schedules. *Journal of the Experimental Analysis of Behavior*, 5(4), 529–530. https://doi.org/10.1901/jeab.1962.5-529
- Herrnstein, R. J., & Morse, W. H. (1957). Some effects of response-independent positive reinforcement on maintained operant behavior. *Journal of Comparative and Physiological Psychology*, 50(5), 461–467. https://doi.org/10.1037/h0048673
- Lachter, G. D., Cole, B. K., & Schoenfeld, W. N. (1971). Some temporal parameters of non-contingent reinforcement. *Journal of the Experimental Analysis of Behavior*, 16(2), 207–217. https://doi.org/10.1901/jeab.1971.16-207
- Lattal, K. A. (1972). Response-reinforcer independence and conventional extinction after fixed-interval and variable-interval schedules. *Journal of the Experimental Analysis of Behavior*, 18(1), 133–140. https://doi.org/10.1901/jeab.1972.18-133
- Rachlin, H., & Baum, W. M. (1972). Effects of alternative reinforcement: Does the source matter? *Journal of the Experimental Analysis of Behavior*, 18(2), 231–241. https://doi.org/10.1901/jeab.1972.18-231
- Sizemore, O. J., & Lattal, K. A. (1978). Unsignalled delay of reinforcement in variable-interval schedules. *Journal of the Experimental Analysis of Behavior*, 30(2), 169–175. https://doi.org/10.1901/jeab.1978.30-169
- Skinner, B. F. (1948). 'Superstition' in the pigeon. *Journal of Experimental Psychology*, 38(2), 168–172. https://doi.org/10.1037/h0055873
- Zeiler, M. D. (1968). Fixed and variable schedules of response-independent reinforcement. *Journal of the Experimental Analysis of Behavior*, 11(4), 405–414. https://doi.org/10.1901/jeab.1968.11-405
