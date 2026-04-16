# Time Scales — Trial, Session, Phase, ITI; Molar vs Molecular

> Part of the contingency-dsl foundations layer (Ψ). Fixes the canonical time-scale vocabulary used throughout the spec. Paradigm layers reuse these definitions; no layer redefines them.

---

## 1. Structural Time Units

The DSL recognizes four structural time units arranged by duration:

| Unit | Definition | Parameterized in |
|---|---|---|
| **Tick** | The finest temporal granularity used in denotational semantics (`Tick(t)` events mark clock advances). | `operant/theory.md §2.13` |
| **Trial** | A bounded unit of procedure with a defined start and end (e.g., CS onset → ITI end in respondent; sample → ITI end in trial-based operant). | `operant/trial-based/*.md`, respondent grammar |
| **Session** | A contiguous block of trials and/or free-operant time under a single schedule expression. | `annotations/extensions/measurement-annotator` (`@session`, `@session_end`) |
| **Phase** | An ordered segment of one or more sessions under a shared schedule expression and shared phase-change criterion. | `experiment/phase-sequence.md` |

A complete experimental design is a sequence of phases; each phase comprises one or more sessions; each session comprises one or more trials (in trial-based paradigms) or a continuous free-operant stream (in free-operant paradigms).

## 2. Inter-Trial Interval (ITI)

**Definition 1 (ITI).** The inter-trial interval is the time between two consecutive trials. It is measured *trial-onset to trial-onset* (or equivalently, ITI = gap between trial *k* end and trial *k+1* start, depending on the paradigm's convention).

ITI appears in two roles:

- **Primitive-level** (respondent layer): `ITI(distribution, mean)` is a Tier A structural primitive because the I/T ratio (CS duration to ITI) is a principal determinant of conditioned response acquisition speed (Gibbon & Balsam, 1981; Gallistel & Gibbon, 2000).
- **Annotation-level**: `@iti(distribution, mean, jitter)` (part of `respondent-annotator`) provides distributional refinement (jitter, sampling method) and may attach to phases or trial blocks.

The primitive carries only the structural parameters (distribution, mean); distributional refinement is an annotation concern. Both forms resolve to the same mean-ITI behavioral variable in conformance tests.

## 3. Molar vs Molecular Time Scales

The experimental analysis of behavior has two established time-scale analyses, which the DSL must accommodate without bias:

**Definition 2 (Molecular analysis).** Analysis at the level of individual responses and their immediate consequences. Dependent variables include inter-response time (IRT) distributions, post-reinforcement pause duration, and response-by-response choice patterns. Canonical references: Skinner (1938), Herrnstein (1961), Baum (1973).

**Definition 3 (Molar analysis).** Analysis at the level of aggregated rates and probabilities over extended time intervals (session, phase). Dependent variables include session response rate, matching-law ratios, overall choice proportions. Canonical references: Baum (2002, 2004), Rachlin (1978).

Both analyses operate on the same procedural primitives; they differ in the observation window applied to the behavioral data stream. The DSL is **molar/molecular-neutral** at the foundations level:

- Schedule expressions (e.g., `VI 60-s`, `Conc(VI 30-s, VI 60-s)`) describe contingency structures that can be analyzed at either scale.
- `@session_end`, `@dependent_measure`, `@steady_state` (measurement-annotator) can specify either molar or molecular dependent variables.
- No grammar construct privileges one analysis over the other.

This neutrality is load-bearing: DSL-level commitment to one scale would exclude half the literature.

## 4. Time Units in the Grammar

Numeric values in time-bearing positions carry an explicit unit suffix from `{s, ms, min}`. Bare numbers in time-bearing positions are either rejected (strict mode) or assumed to be seconds (lint-warning mode), depending on the paradigm layer's specification. Identity of the time unit is preserved in the AST (`time_unit: "s" | "ms" | "min"`) so that round-trip serialization reproduces the original notation.

## 5. What This Layer Does **Not** Define

- **Within-trial timing** (stimulus presentation latency, response-evaluation latency) is a runtime concern, not a DSL concern.
- **Real-time vs simulated time** clock sources are annotated via `@clock(...)` in `procedure-annotator/temporal`, not at the foundations layer.
- **Time-warping across phases** (e.g., compressed replay) is outside the DSL scope.

## References

- Baum, W. M. (1973). The correlation-based law of effect. *Journal of the Experimental Analysis of Behavior*, 20(1), 137–153. https://doi.org/10.1901/jeab.1973.20-137
- Baum, W. M. (2002). From molecular to molar: A paradigm shift in behavior analysis. *Journal of the Experimental Analysis of Behavior*, 78(1), 95–116. https://doi.org/10.1901/jeab.2002.78-95
- Baum, W. M. (2004). Molar and molecular views of choice. *Behavioural Processes*, 66(3), 349–359. https://doi.org/10.1016/j.beproc.2004.03.013
- Gallistel, C. R., & Gibbon, J. (2000). Time, rate, and conditioning. *Psychological Review*, 107(2), 289–344. https://doi.org/10.1037/0033-295X.107.2.289
- Gibbon, J., & Balsam, P. (1981). Spreading association in time. In C. M. Locurto, H. S. Terrace, & J. Gibbon (Eds.), *Autoshaping and conditioning theory* (pp. 219–253). Academic Press.
- Herrnstein, R. J. (1961). Relative and absolute strength of response as a function of frequency of reinforcement. *Journal of the Experimental Analysis of Behavior*, 4(3), 267–272. https://doi.org/10.1901/jeab.1961.4-267
- Rachlin, H. (1978). A molar theory of reinforcement schedules. *Journal of the Experimental Analysis of Behavior*, 30(3), 345–360. https://doi.org/10.1901/jeab.1978.30-345
- Skinner, B. F. (1938). *The behavior of organisms*. Appleton-Century.
