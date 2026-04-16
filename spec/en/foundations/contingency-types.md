# Contingency Types — Contingent vs Non-Contingent, Two-Term vs Three-Term

> Part of the contingency-dsl foundations layer (Ψ). Defines the foundational type distinctions that divide the DSL into paradigm layers. Not a treatise — this file fixes the canonical definitions used throughout the spec.

---

## 1. Contingent vs Non-Contingent

**Definition 1 (Contingent arrangement).** An arrangement is *contingent* when the probability of a consequence depends on the occurrence of a preceding event (typically a response or a stimulus). Formally, `P(consequence | antecedent) ≠ P(consequence | ¬antecedent)`.

**Definition 2 (Non-contingent arrangement).** An arrangement is *non-contingent* (response-independent) when the probability of a consequence is independent of the antecedent: `P(consequence | antecedent) = P(consequence | ¬antecedent)`.

In the operant layer, the canonical non-contingent schedules are **Time schedules** (FT, VT, RT), where reinforcement is delivered on a time basis regardless of responding (Zeiler, 1968; Lattal, 1972). In the respondent layer, the canonical non-contingent control is **TrulyRandom** — the special case `Contingency(p, p)` where `P(US | CS) = P(US | ¬CS)` (Rescorla, 1967).

**Why the distinction is foundational.** Non-contingent arrangements are not trivial controls; they produce systematic behavioral effects (adventitious reinforcement; Skinner, 1948) and serve as the empirical reference point against which contingent arrangements are defined. The DSL treats response-independent primitives (FT/VT/RT, TrulyRandom) as first-class expressions, not as degenerate cases.

## 2. Two-Term Contingency (CS–US)

**Definition 3 (Two-term contingency).** A two-term contingency is a probabilistic relation between a conditioned stimulus (CS) and an unconditioned stimulus (US). The canonical parameterization is Rescorla's (1967) contingency space:

```
two_term_contingency = (p_us_given_cs, p_us_given_no_cs)
```

The coordinate system has two axes:

- **X-axis:** `P(US | CS)` — probability of the US given the CS.
- **Y-axis:** `P(US | ¬CS)` — probability of the US in the absence of the CS.

Four canonical regions:

| Region | Operational meaning | Primitive |
|---|---|---|
| `(p, 0)` with `p > 0` | Excitatory CS–US pairing | `Pair.*` family |
| `(0, q)` with `q > 0` | Inhibitory (explicitly unpaired) | `ExplicitlyUnpaired` |
| `(p, p)` (diagonal) | Truly random, zero contingency | `TrulyRandom` |
| `(p, q)` arbitrary | General contingency point | `Contingency(p, q)` |

The two-term contingency is the domain of the **respondent** layer (`respondent/grammar.md`, `respondent/theory.md`). See Pavlov (1927) for the original formulation and Rescorla (1967, 1968) for the modern contingency-space framing.

## 3. Three-Term Contingency (SD–R–SR)

**Definition 4 (Three-term contingency).** A three-term contingency is a relation among a discriminative stimulus (SD), a response (R), and a consequence (SR):

```
three_term_contingency = (SD, R, SR)
  where
    SD  : discriminative stimulus — signals when R will produce SR
    R   : operant response class
    SR  : consequence (Sr+, Sr−, punisher)
```

The operational reading: *in the presence of SD, response R produces consequence SR*. This is the basic unit of the operant analysis (Skinner, 1938; 1953).

The three-term contingency is the domain of the **operant** layer (`operant/grammar.md`, `operant/theory.md`). Reinforcement schedules, stateful operant procedures, and trial-based operant procedures all express particular shapes of the three-term contingency.

## 4. Two-Term vs Three-Term as a Layer Boundary

The DSL treats the two-term / three-term distinction as the primary layer boundary (see `architecture.md §4.1` and `design-philosophy.md §2`). The rationale:

1. **Structural.** The two relations have different arities (2 vs 3) and different canonical parameterizations (`(p_us_given_cs, p_us_given_no_cs)` vs `(SD, R, SR)`). Nesting them under a common "Paradigm" node would force an artificial parameterization.
2. **Historical.** The Pavlov (1927) / Skinner (1938) distinction has been the stable disciplinary boundary for nearly a century (Catania, 2013). The DSL respects the existing literature's usage.
3. **Composability.** Procedures that combine both (CER, PIT, autoshaping, omission) are first-class residents of the `composed/` layer, not sub-cases of either respondent or operant.

## 5. Higher-Order and Derived Relations

Higher-order relations (relational frames, stimulus equivalence classes, derived stimulus relations; Sidman, 1971; Hayes et al., 2001) are **not** foundational types in contingency-dsl. They are behavioral outcomes produced by specific training procedures (most notably MTS), not contingency primitives. The DSL specifies the procedures; the relations are observed.

## References

- Catania, A. C. (2013). *Learning* (5th ed.). Sloan.
- Hayes, S. C., Barnes-Holmes, D., & Roche, B. (Eds.). (2001). *Relational frame theory: A post-Skinnerian account of human language and cognition*. Kluwer Academic/Plenum.
- Lattal, K. A. (1972). Response-reinforcer independence and conventional extinction after fixed-interval and variable-interval schedules. *Journal of the Experimental Analysis of Behavior*, 18(1), 133–140. https://doi.org/10.1901/jeab.1972.18-133
- Lattal, K. A. (1995). Contingency and behavior analysis. *Mexican Journal of Behavior Analysis*, 21, 47–73.
- Pavlov, I. P. (1927). *Conditioned reflexes: An investigation of the physiological activity of the cerebral cortex* (G. V. Anrep, Trans.). Oxford University Press.
- Rescorla, R. A. (1967). Pavlovian conditioning and its proper control procedures. *Psychological Review*, 74(1), 71–80. https://doi.org/10.1037/h0024109
- Rescorla, R. A. (1968). Probability of shock in the presence and absence of CS in fear conditioning. *Journal of Comparative and Physiological Psychology*, 66(1), 1–5. https://doi.org/10.1037/h0025984
- Sidman, M. (1971). Reading and auditory-visual equivalences. *Journal of Speech and Hearing Research*, 14(1), 5–13. https://doi.org/10.1044/jshr.1401.05
- Skinner, B. F. (1938). *The behavior of organisms*. Appleton-Century.
- Skinner, B. F. (1948). 'Superstition' in the pigeon. *Journal of Experimental Psychology*, 38(2), 168–172. https://doi.org/10.1037/h0055873
- Skinner, B. F. (1953). *Science and human behavior*. Macmillan.
- Zeiler, M. D. (1968). Fixed and variable schedules of response-independent reinforcement. *Journal of the Experimental Analysis of Behavior*, 11(4), 405–414. https://doi.org/10.1901/jeab.1968.11-405
