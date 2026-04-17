# Design Rationale

This document explains *why* certain DSL design decisions were made,
with references to the experimental literature. It complements the
normative specification in `spec/` — the spec says what the grammar *is*;
this document says why it is that way.

---

## 1. Layer Organization: Organizing by Scientific Category, Not by Formal Axis

### The Choice

The DSL is organized into six layers by **scientific category** rather than
by an abstract formal axis. The layers are:

| Layer | What it holds |
|---|---|
| **Foundations** | Paradigm-neutral formal base: CFG/LL(2), contingency-type theory (contingent vs. non-contingent; two-term vs. three-term), time scales, stimulus typing (SD, SΔ, CS, US, Sr+, Sr−), valence, context. |
| **Operant** | Three-term contingency (SD-R-SR): reinforcement schedules, stateful schedules with runtime-computed criteria, trial-based (discrete-trial) schedules. |
| **Respondent** | Two-term contingency (CS-US): Tier A Pavlovian primitives + an extension point for third-party additions. |
| **Composed** | Operant × respondent composites: CER, PIT, autoshaping, omission, two-process theory. |
| **Experiment** | Declarative multi-phase experimental designs with first-class Context. |
| **Annotation** | Program-scoped metadata, including two shipped extensions (`respondent-annotator`, `learning-models-annotator`). |

An alternative organization — grouping primitives by an abstract formal axis
such as "static vs. dynamic" or "literal vs. computed criterion" — was
considered and rejected.

### Why Scientific Category Won

The discipline itself already uses the operant / respondent distinction
(Skinner, 1938) and the two-process framing (Rescorla & Solomon, 1967) as
primary categories of procedure classification. Organizing the DSL along
the same axis produces an architecture that:

1. **Reads naturally to the target user.** The DSL's principal users are
   EAB researchers and their students. Placing `FR 5` under `operant/` and
   `Pair.ForwardDelay(cs, us)` under `respondent/` mirrors how the
   discipline already categorizes these procedures. A "dynamic vs. static"
   axis would require users to translate the discipline's categories into
   a formal taxonomy at every interaction.

2. **Protects the boundary between two- and three-term contingencies.**
   The three-term contingency (SD-R-SR) and the two-term contingency
   (CS-US) are structurally distinct relations. Attempting to nest them
   under a common "Paradigm" node either (a) forces an artificial
   parameterization that obscures their distinct grammars, or (b)
   collapses the structures into one, misrepresenting the discipline.
   Operant and Respondent are therefore first-class siblings, not
   specializations of a common super-relation.

3. **Gives composed procedures a principled home.** CER, PIT, autoshaping,
   and omission are not sub-cases of either operant or respondent — they
   are operant × respondent composites. A scientific-category organization
   represents this directly (`composed/` is a sibling of `operant/` and
   `respondent/`), whereas an axial organization would be forced to
   either duplicate them or fabricate a cross-cutting category.

4. **Matches JEAB publication structure.** Method sections in JEAB papers
   describe operant baseline schedules, Pavlovian overlays, and composed
   procedures as distinct units of methodological vocabulary. The layer
   structure makes each vocabulary directly addressable at the
   documentation level.

### Respondent Depth Is Minimal by Design

The Respondent layer holds fourteen Tier A primitives — the founding
procedures named by the Rescorla (1967) contingency-space formalism and
its immediate controls (see
[respondent/primitives.md](../../spec/en/respondent/primitives.md)). Deeper
respondent procedures (blocking, overshadowing, latent inhibition,
conditioned inhibition, renewal, reinstatement, spontaneous recovery,
counterconditioning, occasion-setting, and others) are delegated to the
companion package `contingency-respondent-dsl` through the Respondent
extension point (see design-philosophy §5.4).

The rationale for this split is scope discipline. The principal coverage
target of contingency-dsl is operant procedures + JEAB paper reproduction;
the respondent machinery required to express composed procedures (CER,
PIT, autoshaping, omission) bottoms out at the Tier A set. Admitting the
full respondent literature into the Core would (i) expand the primitive
set by an order of magnitude, (ii) require context-sensitive primitives
(e.g., renewal across ABA/ABC/AAB contexts) that strain the paradigm-
neutral Foundations, and (iii) dilute the audience focus. The extension
point preserves compositional reach without those costs.

### References

- Pavlov, I. P. (1927). *Conditioned reflexes: An investigation of the physiological activity of the cerebral cortex* (G. V. Anrep, Trans.). Oxford University Press.
- Rescorla, R. A. (1967). Pavlovian conditioning and its proper control procedures. *Psychological Review*, *74*(1), 71–80. https://doi.org/10.1037/h0024109
- Rescorla, R. A., & Solomon, R. L. (1967). Two-process learning theory: Relationships between Pavlovian conditioning and instrumental learning. *Psychological Review*, *74*(3), 151–182. https://doi.org/10.1037/h0024475
- Skinner, B. F. (1938). *The behavior of organisms*. Appleton-Century.

---

## 2. DRO: Why "Other Behavior" Is a Misnomer

### The Name

DRO stands for "Differential Reinforcement of Other behavior." The name
implies a simple mechanism: when the target behavior is absent for a
specified interval, *some other behavior* is reinforced, and this
alternative behavior competes with and displaces the target. Clinicians
have operated under this assumption for decades.

### What the Evidence Shows

Mazaleski, Iwata, Vollmer, Zarcone, and Smith (1993) separated the two
components of DRO in a study with three individuals who exhibited
self-injurious behavior (SIB):

1. **Reinforcement component** — delivering a reinforcer when SIB is
   absent for the interval.
2. **Extinction component** — withholding the reinforcer when SIB
   occurs.

For two of three participants, the reinforcement component *alone* was
ineffective. DRO only worked when the extinction component was in place.
The reinforcer delivery was neither necessary nor sufficient; it was the
*withholding* contingency that did the work.

Two later studies by Rey, Betz, Sleiman, Kuroda, and Podlesnik (2020a,
2020b) directly tested whether DRO adventitiously reinforces "other"
behavior. They found that while other behaviors transiently increased
early in DRO, these increases did not maintain — even as target behavior
remained suppressed across extended sessions. If DRO worked by
reinforcing alternatives, those alternatives should have strengthened
over time. They did not.

Most recently, Hronek and Kestner (2025) examined the asymmetry of
implementation errors. Commission errors (accidentally reinforcing after
the target behavior occurs) degraded DRO effectiveness far more than
omission errors (failing to deliver the reinforcer when earned). This
asymmetry is predicted by the omission/extinction account but not by the
alternative-reinforcement account.

### What This Means for the DSL

The current DSL represents DRO with a single time parameter:
`DRO(omission_time)`. This captures the *omission contingency* — the
duration for which the target response must be absent. The name "DRO"
is retained for literature compatibility, but the specification notes
that the mechanism is omission/extinction, not alternative reinforcement.

Lindberg, Iwata, Kahng, and DeLeon (1999) established a 2x2 taxonomy
that decomposes DRO along two orthogonal dimensions:

|                | Fixed interval | Variable interval |
|----------------|----------------|-------------------|
| **Whole-interval** | Traditional DRO: target must be absent for the *entire* interval | VI-DRO: interval duration varies |
| **Momentary**  | Check only at the interval endpoint | VM-DRO: check at variable timepoints |

The current DSL implements fixed whole-interval DRO. The full 2x2
taxonomy is deferred to v1.x, where `DRO` may accept optional keyword
arguments for `mode` (whole-interval vs. momentary) and `timing` (fixed
vs. variable).

### References

- Hronek, L. M., & Kestner, K. M. (2025). A human-operant evaluation of commission and omission errors during differential reinforcement of other behavior. *Journal of Applied Behavior Analysis*. https://doi.org/10.1002/jaba.70003
- Lindberg, J. S., Iwata, B. A., Kahng, S., & DeLeon, I. G. (1999). DRO contingencies: An analysis of variable-momentary schedules. *Journal of Applied Behavior Analysis*, *32*(2), 123-136. https://doi.org/10.1901/jaba.1999.32-123
- Mazaleski, J. L., Iwata, B. A., Vollmer, T. R., Zarcone, J. R., & Smith, R. G. (1993). Analysis of the reinforcement and extinction components in DRO contingencies with self-injury. *Journal of Applied Behavior Analysis*, *26*(2), 143-156. https://doi.org/10.1901/jaba.1993.26-143
- Rey, C. N., Betz, A. M., Sleiman, A. A., Kuroda, T., & Podlesnik, C. A. (2020a). The role of adventitious reinforcement during differential reinforcement of other behavior: A systematic replication. *Journal of Applied Behavior Analysis*, *53*(4), 2440-2449. https://doi.org/10.1002/jaba.678
- Rey, C. N., Betz, A. M., Sleiman, A. A., Kuroda, T., & Podlesnik, C. A. (2020b). Adventitious reinforcement during long-duration DRO exposure. *Journal of Applied Behavior Analysis*, *53*(3), 1716-1733. https://doi.org/10.1002/jaba.697

---

## 3. Progressive Ratio: Why the Step Function Is Required

### The Problem

A bare `PR` statement conceals a choice that changes the *kind* of data
you collect. Consider two researchers:

- **Researcher A** writes `PR` and gets `hodos` (arithmetic:
  1, 2, 3, 4, ...). Response rate declines linearly across ratios.
  Breakpoint at ratio 47.
- **Researcher B** writes `PR` and gets `hodos` by the same silent
  default. But their collaborator expected Richardson-Roberts exponential
  (1, 2, 4, 6, 9, 12, ...). Breakpoint at ratio 95.

Same drug, same dose, same animal — different breakpoints, different
conclusions about reinforcer efficacy. The silent default masks a
procedurally meaningful divergence.

### What the Literature Says

**Step function shape changes the response-rate function.**
Killeen, Posadas-Sanchez, Johansen, and Thrailkill (2009) directly
compared arithmetic and geometric progressions in pigeons (Experiment 1).
Under arithmetic steps, response rates declined *linearly* across
component ratios. Under geometric steps, rates declined with *negative
acceleration* toward an asymptote. These are not merely quantitatively
different — they are qualitatively different functional forms. A
mathematical model derived from the Mathematical Principles of
Reinforcement (MPR) predicts this difference: the bitonic equation takes
different shapes depending on the progression type.

**Breakpoint is robust to step size but other measures are not.**
Stafford and Branch (1998) varied arithmetic step sizes in pigeons. The
*largest completed ratio* (breakpoint) was relatively unaffected by
step-size magnitude — a reassuring finding for between-study
comparisons. However, the *number of ratios completed* and *average
response rate* both declined with increasing step sizes. Step function
choice therefore determines which dependent variable is informative.

**No consensus default exists.** The field has not converged:

| Tradition | Step function | Typical use |
|-----------|--------------|-------------|
| Hodos (1961) | Arithmetic (+constant) | Original PR; food reinforcement |
| Richardson & Roberts (1996) | Exponential (5·e^(j/5) - 5) | Drug self-administration; reaches breakpoint within one session |
| Linear | Arithmetic with custom start/increment | Flexible; used in human operant studies |
| Geometric | Multiplicative (start × ratio^n) | Killeen et al. (2009); qualitatively different rate function from arithmetic |

Richardson and Roberts' exponential became the *de facto* standard in
behavioral pharmacology because it reaches breakpoint within a
practical session length. But this is a practical convenience, not a
theoretical justification. The Hodos arithmetic progression remains
standard in basic reinforcement research with food.

### Breakpoint Is Not Pmax

A common assumption in behavioral pharmacology: "PR breakpoint measures
how much the animal is willing to pay for the drug." This maps PR onto
demand-curve economics, where Pmax is the price at unit elasticity and
alpha is the essential-value parameter.

Lambert et al. (2026, *JEAB*, n=96 adults with disabilities) tested this
mapping directly. Their findings:

- PR breakpoint **correlated with** demand *intensity* (Q0 — consumption
  at zero price, the "how much do they want it?" question).
- PR breakpoint **did not correlate with** demand *elasticity* (alpha)
  or *Pmax* (the "at what price do they stop?" question).

This is a consequential dissociation. If the research question is "how
essential is this reinforcer?" (intensity), PR breakpoint is informative.
If the question is "at what price does consumption become elastic?"
(Pmax), systematic FR variation across sessions is needed — not PR.

Bentzley, Fender, and Aston-Jones (2013) noted the same gap from the
pharmacology side: no unified mathematical model bridges PR breakpoint
to the exponential demand parameters (alpha, Q0, Pmax, Omax). The
relationship remains empirical, not formally derived.

### The DSL's Position

The DSL offers two forms, both requiring the researcher to commit to
a progression type:

- **Shorthand:** `PR 5` — expands to `PR(linear, start=5, increment=5)`,
  producing FR 5, FR 10, FR 15, ... This follows the notation proposed
  by Jarmolowicz and Lattal (2010) in *The Behavior Analyst*: the
  number after `PR` is the arithmetic step size, and the starting ratio
  equals the step size. This is the natural form for educational and
  clinical contexts, consistent with `FR 10`, `VI 30-s`, and other
  `KEYWORD NUMBER` schedule notations in the DSL.
- **Explicit:** `PR(hodos)`, `PR(linear, start=1, increment=5)`,
  `PR(exponential)`, or `PR(geometric, start=1, ratio=2)` — for full
  parametric control. Use this when the progression does not follow the
  simple `ratio(n) = step × n` pattern.

Bare `PR` without a number or parenthesized options is a parse error.
The researcher must always specify which progression they intend.

### References

- Bentzley, B. S., Fender, K. M., & Aston-Jones, G. (2013). The behavioral economics of drug self-administration: A review and new analytical approach for within-session procedures. *Psychopharmacology*, *226*(1), 113-125. https://doi.org/10.1007/s00213-012-2899-2
- Hodos, W. (1961). Progressive ratio as a measure of reward strength. *Science*, *134*(3483), 943-944. https://doi.org/10.1126/science.134.3483.943
- Jarmolowicz, D. P., & Lattal, K. A. (2010). On distinguishing progressively increasing response requirements for reinforcement. *The Behavior Analyst*, *33*(1), 33-47. https://doi.org/10.1007/BF03392202
- Killeen, P. R., Posadas-Sanchez, D., Johansen, E. B., & Thrailkill, E. A. (2009). Progressive ratio schedules of reinforcement. *Journal of Experimental Psychology: Animal Behavior Processes*, *35*(1), 35-50. https://doi.org/10.1037/a0012497
- Lambert, J. M., et al. (2026). Evaluating contributions of progressive ratio analysis to economic metrics of demand. *Journal of the Experimental Analysis of Behavior*. https://doi.org/10.1002/jeab.70077
- Richardson, N. R., & Roberts, D. C. S. (1996). Progressive ratio schedules in drug self-administration studies in rats. *Journal of Neuroscience Methods*, *66*(1), 1-11. https://doi.org/10.1016/0165-0270(95)00153-0
- Stafford, D., & Branch, M. N. (1998). Effects of step size and break-point criterion on progressive-ratio performance. *Journal of the Experimental Analysis of Behavior*, *70*(2), 123-138. https://doi.org/10.1901/jeab.1998.70-123

---

## 4. Lag: Why `length` Is Explicit

### The Parameter Problem

When Page and Neuringer (1985) introduced the Lag schedule, they used
2-key, 8-peck sequences: a pigeon produced a string of 8 left/right
pecks (e.g., LLRLRRLL), and reinforcement was delivered if the sequence
differed from each of the previous *n* sequences. The unit of
variability was the 8-response sequence.

But subsequent researchers chose different sequence lengths:

| Study | Sequence length | Species |
|-------|----------------|---------|
| Page & Neuringer (1985) | 8 | Pigeons |
| Abreu-Rodrigues, Lattal, & Santos (2005) | 4 | Pigeons |
| Ribeiro, Panetta, & Abreu-Rodrigues (2022) | 5 | Humans |
| Applied JABA studies (Lee et al., 2002; etc.) | 1 (individual response) | Humans |

There is no standard. The number of possible unique sequences grows
exponentially with length (2^k for 2 operanda), so `length=4` gives 16
possibilities while `length=8` gives 256. A Lag 5 requirement is trivial
to satisfy with 256 options but demanding with 16. The same `n` produces
different behavioral demands depending on `length`.

The DSL therefore requires `length` to be specified (defaulting to 1
when omitted, which matches applied research convention). The default is
a convenience, not a theoretical commitment — and theory.md documents
the non-standardization to ensure users make an informed choice.

### The DSL's Position

The DSL provides `Lag` as a procedural tool whose behavioral effects
are well-documented. The grammar is neutral: it defines what a Lag
schedule *does* (reinforce sequences differing from the previous *n*),
not what it *means* theoretically.

This is consistent with the DSL's general philosophy: the specification
describes contingency arrangements, not behavioral mechanisms. Whether
DRL performance is "timing" or "counting," whether DRO is "reinforcing
other behavior" or "omission training" — these are empirical questions
that the DSL leaves to the researcher.

### References

- Abreu-Rodrigues, J., Lattal, K. A., dos Santos, C. V., & Matos, R. A. (2005). Variation, repetition, and choice. *Journal of the Experimental Analysis of Behavior*, *83*(2), 147-168. https://doi.org/10.1901/jeab.2005.33-03
- Page, S., & Neuringer, A. (1985). Variability is an operant. *Journal of Experimental Psychology: Animal Behavior Processes*, *11*(3), 429-452. https://doi.org/10.1037/0097-7403.11.3.429
- Ribeiro, M. P., Panetta, N., & Abreu-Rodrigues, J. (2022). Effects of variability requirements on difficult sequence learning. *Journal of the Experimental Analysis of Behavior*, *118*(3), 442-461. https://doi.org/10.1002/jeab.798
