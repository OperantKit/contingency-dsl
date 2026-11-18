# Dependency Types — Response→Stimulus, Stimulus→Stimulus, Time→Stimulus, Conditional Probability

> Part of the contingency-dsl foundations layer. Defines the paradigm-neutral dependency types out of which every procedure in the DSL is built. Only types used by an existing constructor are listed. Role names (reinforcer, discriminative stimulus, CS, US, and so on) are not used here; each paradigm layer names the positions in these types with its own aliases.

---

## 1. Contingent vs Non-Contingent

**Definition 1 (Contingent arrangement).** An arrangement is *contingent* when the probability of a stimulus presentation depends on the occurrence of a preceding event (a response or a stimulus). Formally, `P(presentation | antecedent) ≠ P(presentation | ¬antecedent)`.

**Definition 2 (Non-contingent arrangement).** An arrangement is *non-contingent* when the probability of a stimulus presentation is independent of the antecedent: `P(presentation | antecedent) = P(presentation | ¬antecedent)`.

In the operant layer, the canonical non-contingent schedules are **Time schedules** (FT, VT, RT), where a stimulus is presented on a time basis regardless of responding (Zeiler, 1968; Lattal, 1972). In the respondent layer, the canonical non-contingent control is **TrulyRandom** — the special case `Contingency(p, p)`, where the probability of the second stimulus is the same whether or not the first stimulus is present (Rescorla, 1967).

**Why the distinction is foundational.** Non-contingent arrangements are not trivial controls; they produce systematic behavioral effects (Skinner, 1948) and serve as the empirical reference point against which contingent arrangements are defined. The DSL treats response-independent primitives (FT/VT/RT, TrulyRandom) as first-class expressions, not as degenerate cases.

## 2. The Four Dependency Types

A dependency is a paradigm-neutral contingency `(A, B, P)` ([Foundations Definition 2](theory.md)) in which `B` is the onset or offset of a stimulus ([Stimuli](stimulus-typing.md)). The DSL uses four types, distinguished by what `A` is.

| Dependency type | Paradigm-neutral statement | Constructors that use it |
|---|---|---|
| Response→stimulus | A response determines a stimulus presentation (or its cancellation or postponement) | Ratio and interval schedules, `Overlay`, `Sidman`, `DiscriminatedAvoidance`, `Escape`, `@omission`, `@avoidance` |
| Stimulus→stimulus | The onset or offset of one stimulus determines the presentation of another, with a temporal relation | `Pair.*`, `Serial`, the link transitions of `Chain`, the `CSUSInterval` of `DiscriminatedAvoidance` |
| Time→stimulus | The passage of time alone determines a stimulus presentation | `FT`, `VT`, `RT`, `ITI`, `USOnly`, `CSOnly` |
| Conditional probability | Any of the three above with a probability attached: the probability of a presentation differs with the presence or absence of an event | `Contingency(p, q)`, `TrulyRandom`, `ExplicitlyUnpaired`, `RR` |

A procedure may combine several dependency types in one expression. A new dependency type is added to this table only together with a constructor that uses it.

## 3. Two-Term and Three-Term Contingencies

The two-term contingency and the three-term contingency are paradigm-layer names for particular shapes of the dependencies above:

- **Two-term contingency** — the respondent layer's name for a stimulus→stimulus dependency, usually with conditional probability. Defined in [Respondent Theory §0–§2](../respondent/theory.md#0-stimulus-roles-as-aliases).
- **Three-term contingency** — the operant layer's name for a response→stimulus dependency that holds while another stimulus is present. Defined in [Operant Theory, Stimulus Roles as Aliases](../operant/theory.md#stimulus-roles-as-aliases).

## 4. The Operant and Respondent Layers as Separate Vocabularies

The DSL keeps the operant and respondent layers as sibling vocabularies (see `architecture.md §4.1` and `design-philosophy.md §2`). The reason is historical: the Pavlov (1927) / Skinner (1938) distinction has been the stable disciplinary boundary for nearly a century (Catania, 2013), and the DSL respects the existing literature's usage. Both vocabularies are built from the dependency types of §2.

## 5. Higher-Order and Derived Relations

Higher-order relations (relational frames, stimulus equivalence classes, derived stimulus relations; Sidman, 1971; Hayes et al., 2001) are **not** foundational types in contingency-dsl. They are behavioral outcomes produced by specific training procedures (most notably MTS), not contingency primitives. The DSL specifies the procedures; the relations are observed.

## References

- Catania, A. C. (2013). *Learning* (5th ed.). Sloan.
- Hayes, S. C., Barnes-Holmes, D., & Roche, B. (Eds.). (2001). *Relational frame theory: A post-Skinnerian account of human language and cognition*. Kluwer Academic/Plenum.
- Lattal, K. A. (1972). Response-reinforcer independence and conventional extinction after fixed-interval and variable-interval schedules. *Journal of the Experimental Analysis of Behavior*, 18(1), 133–140. https://doi.org/10.1901/jeab.1972.18-133
- Lattal, K. A. (1995). Contingency and behavior analysis. *Mexican Journal of Behavior Analysis*, 21, 47–73.
- Pavlov, I. P. (1927). *Conditioned reflexes: An investigation of the physiological activity of the cerebral cortex* (G. V. Anrep, Trans.). Oxford University Press.
- Rescorla, R. A. (1967). Pavlovian conditioning and its proper control procedures. *Psychological Review*, 74(1), 71–80. https://doi.org/10.1037/h0024109
- Sidman, M. (1971). Reading and auditory-visual equivalences. *Journal of Speech and Hearing Research*, 14(1), 5–13. https://doi.org/10.1044/jshr.1401.05
- Skinner, B. F. (1938). *The behavior of organisms*. Appleton-Century.
- Skinner, B. F. (1948). 'Superstition' in the pigeon. *Journal of Experimental Psychology*, 38(2), 168–172. https://doi.org/10.1037/h0055873
- Zeiler, M. D. (1968). Fixed and variable schedules of response-independent reinforcement. *Journal of the Experimental Analysis of Behavior*, 11(4), 405–414. https://doi.org/10.1901/jeab.1968.11-405
