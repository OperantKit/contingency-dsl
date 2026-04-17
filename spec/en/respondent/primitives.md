# Respondent Primitives — Tier A Specifications (R1–R14)

> Part of the contingency-dsl respondent layer. Operational definitions, parameter semantics, citations, and illustrative DSL examples for the fourteen Tier A Pavlovian primitives. For grammar productions, see `grammar.md`; for theoretical motivation, see `theory.md`; for extension-point primitives (Tier B), see the companion package `contingency-respondent-dsl`.

---

## Organization

Each primitive specifies:
- **Canonical DSL spelling** — the grammar-level form.
- **Operational definition** — CS/US timing relationship stated precisely.
- **Parameter semantics** — what each argument controls.
- **Example** — one-line DSL usage.
- **Primary citation** — APA 7 with DOI.
- **Related primitives** — relationship to other Tier A constructs.

---

## R1. `Pair.ForwardDelay(cs, us, isi, cs_duration)`

**Operational definition.** CS onset occurs; after a delay of `isi - cs_duration` (or some overlap interval), the US begins while the CS is still present; both may terminate together or the CS may terminate shortly before the US offset. Forward delay conditioning is the canonical Pavlovian arrangement: the CS and US **temporally overlap**, with CS onset preceding US onset.

**Parameter semantics.**
- `cs` — identifier or string label for the conditional stimulus.
- `us` — identifier or string label for the unconditional stimulus.
- `isi` — the interstimulus interval from CS onset to US onset.
- `cs_duration` — the total CS duration. When `cs_duration > isi`, CS and US overlap; when `cs_duration = isi`, CS offset = US onset (boundary with trace conditioning at zero trace).

**Example.**
```
Pair.ForwardDelay(tone, shock, isi=10-s, cs_duration=15-s)
```

**Primary citation.** Pavlov, I. P. (1927). *Conditioned reflexes: An investigation of the physiological activity of the cerebral cortex* (G. V. Anrep, Trans.). Oxford University Press.

**Related primitives.** Boundary with R2 (`Pair.ForwardTrace`) at `cs_duration = isi` (trace interval = 0). Corresponds to the `(p=1, q=0)` corner of the contingency space (see R8).

---

## R2. `Pair.ForwardTrace(cs, us, trace_interval)`

**Operational definition.** CS onset and offset precede US onset, with a **trace gap** of duration `trace_interval` between CS offset and US onset during which neither stimulus is present. The subject must bridge the trace gap for CR acquisition.

**Parameter semantics.**
- `cs`, `us` — CS and US labels.
- `trace_interval` — duration of the empty interval from CS offset to US onset.

**Example.**
```
Pair.ForwardTrace(tone, food, trace_interval=5-s)
```

**Primary citations.**
- Pavlov, I. P. (1927). *Conditioned reflexes*. Oxford University Press.
- Ellison, G. D. (1964). Differential salivary conditioning to traces. *Journal of Comparative and Physiological Psychology*, 57(3), 373–380. https://doi.org/10.1037/h0043484

**Related primitives.** Distinct from R1 (forward delay) precisely when `trace_interval > 0`. Trace conditioning typically yields weaker CR than delay conditioning at comparable CS-US intervals (Ellison, 1964).

---

## R3. `Pair.Simultaneous(cs, us)`

**Operational definition.** CS onset coincides with US onset (`isi = 0`). CS and US are presented simultaneously, often for equal durations.

**Parameter semantics.**
- `cs`, `us` — CS and US labels.

**Example.**
```
Pair.Simultaneous(light, airpuff)
```

**Primary citation.** Rescorla, R. A. (1980). Simultaneous and successive associations in sensory preconditioning. *Journal of Experimental Psychology: Animal Behavior Processes*, 6(3), 207–216. https://doi.org/10.1037/0097-7403.6.3.207

**Related primitives.** Theoretical boundary with R1 at `isi = 0`. Simultaneous conditioning typically yields weaker overt CR than forward delay but produces measurable CS-US association detectable by sensory preconditioning or post-training tests (Rescorla, 1980).

---

## R4. `Pair.Backward(us, cs, isi)`

**Operational definition.** US onset precedes CS onset. The canonical procedure places US offset before CS onset, separated by `isi`. The US reference appears first in the argument list to match the temporal order.

**Parameter semantics.**
- `us`, `cs` — US and CS labels (US first, following temporal order).
- `isi` — duration from US offset to CS onset.

**Example.**
```
Pair.Backward(shock, tone, isi=2-s)
```

**Primary citation.** Spetch, M. L., Wilkie, D. M., & Pinel, J. P. J. (1981). Backward conditioning: A reevaluation of the empirical evidence. *Psychological Bulletin*, 89(1), 163–175. https://doi.org/10.1037/0033-2909.89.1.163

**Related primitives.** Backward conditioning often functions as a **conditioned inhibitor** rather than an excitor under standard parameters (Spetch et al., 1981). Contrast with R1 (forward delay).

---

## R5. `Extinction(cs)`

**Operational definition.** After an acquisition history (typically `Pair.ForwardDelay` or similar), CS is presented alone — without the US — until CR decrements. Extinction does not erase the original association; it adds an inhibitory association that is context-sensitive (Bouton, 2004).

**Parameter semantics.**
- `cs` — CS label. The prior training history is inherited from the enclosing `PhaseSequence`; bare `Extinction(cs)` outside a phase context is semantically ill-formed unless the program defines a default.

**Example.**
```
Phase(name="acquisition", schedule=Pair.ForwardDelay(tone, shock, isi=10-s, cs_duration=15-s)),
Phase(name="extinction", schedule=Extinction(tone))
```

**Primary citations.**
- Pavlov, I. P. (1927). *Conditioned reflexes*. Oxford University Press.
- Bouton, M. E. (2004). Context and behavioral processes in extinction. *Learning & Memory*, 11(5), 485–494. https://doi.org/10.1101/lm.78804

**Related primitives.** Distinct from R6 (`CSOnly`), which is phase-independent and does not presuppose prior acquisition. Phenomena that depend on context-sensitive extinction properties (renewal, reinstatement, spontaneous recovery) are delegated to the Respondent extension point.

---

## R6. `CSOnly(cs, trials)`

**Operational definition.** CS is presented alone for `trials` presentations. Unlike R5, `CSOnly` is phase-independent and does not presuppose prior acquisition; it is suitable for baseline exposure (e.g., the pre-exposure phase of latent-inhibition procedures) as well as for test probes.

**Parameter semantics.**
- `cs` — CS label.
- `trials` — number of CS-alone presentations.

**Example.**
```
Phase(name="pre_exposure", schedule=CSOnly(tone, trials=40))
```

**Primary citation.** Lubow, R. E., & Moore, A. U. (1959). Latent inhibition: The effect of nonreinforced pre-exposure to the conditional stimulus. *Journal of Comparative and Physiological Psychology*, 52(4), 415–419. https://doi.org/10.1037/h0046700

**Related primitives.** Differs from R5 (`Extinction`) by being phase-independent. Latent inhibition as a named procedure is Tier B and belongs to `contingency-respondent-dsl`; `CSOnly` is the Tier A primitive from which such procedures are constructed.

---

## R7. `USOnly(us, trials)`

**Operational definition.** US is presented alone for `trials` presentations, without any CS. Used for US pre-exposure procedures, habituation to the US, or as a control condition.

**Parameter semantics.**
- `us` — US label.
- `trials` — number of US-alone presentations.

**Example.**
```
Phase(name="us_habituation", schedule=USOnly(shock, trials=20))
```

**Primary citation.** Randich, A., & LoLordo, V. M. (1979). Associative and nonassociative theories of the UCS preexposure phenomenon. *Psychological Bulletin*, 86(3), 523–548. https://doi.org/10.1037/0033-2909.86.3.523

**Related primitives.** The US preexposure effect (Tier B) is constructed from `USOnly` followed by a standard acquisition phase. The Tier A primitive encodes only the US-alone exposure itself.

---

## R8. `Contingency(p_us_given_cs, p_us_given_no_cs)`

**Operational definition.** Parameterizes an arbitrary point in the Rescorla (1967) contingency space. The first argument is `P(US | CS)`; the second is `P(US | ¬CS)`. CS and US event streams are generated so that these two conditional probabilities are approximated over a sufficiently long session. The argument order is fixed at the grammar level (CS-conditional first) and is not permutable.

**Parameter semantics.**
- `p_us_given_cs` — probability of US during / immediately after a CS presentation, in [0, 1].
- `p_us_given_no_cs` — probability of US during an intertrial interval (no CS), in [0, 1].

**Example.**
```
Contingency(0.9, 0.1)     -- strong positive contingency
Contingency(0.5, 0.5)     -- on the diagonal (truly random)
Contingency(0.0, 0.3)     -- negative contingency (US occurs only without CS)
```

**Primary citations.**
- Rescorla, R. A. (1967). Pavlovian conditioning and its proper control procedures. *Psychological Review*, 74(1), 71–80. https://doi.org/10.1037/h0024109
- Rescorla, R. A. (1968). Probability of shock in the presence and absence of CS in fear conditioning. *Journal of Comparative and Physiological Psychology*, 66(1), 1–5. https://doi.org/10.1037/h0025984

**Related primitives.** R9 (`TrulyRandom`) is sugar for the diagonal `Contingency(p, p)`; R10 (`ExplicitlyUnpaired`) refines `Contingency(0, q)` with a temporal-separation constraint. The Pair primitives (R1–R4) are structural specializations near the `(1, 0)` corner.

---

## R9. `TrulyRandom(cs, us)`

**Operational definition.** Syntactic sugar for a point on the diagonal of the contingency space, `Contingency(p, p)`, in which `P(US | CS) = P(US | ¬CS)`. Under this arrangement, the CS carries no predictive information about the US. Rescorla (1967) proposed this as the correct control condition for claims about CS-US association.

**Parameter semantics.**
- `cs`, `us` — CS and US labels.
- Optional `p` keyword argument (see grammar §2.3) specifies the shared probability. Default program-scoped behavior is specified by the program's respondent registry.

**Example.**
```
TrulyRandom(tone, shock)
TrulyRandom(tone, shock, p=0.2)
```

**Primary citation.** Rescorla, R. A. (1967). Pavlovian conditioning and its proper control procedures. *Psychological Review*, 74(1), 71–80. https://doi.org/10.1037/h0024109

**Related primitives.** Special case of R8. Distinct from R10 (`ExplicitlyUnpaired`): truly-random does not prohibit US occurrence during or adjacent to CS; it only equates the two conditional probabilities.

---

## R10. `ExplicitlyUnpaired(cs, us, min_separation)`

**Operational definition.** Corresponds to `Contingency(0, p)` with an additional temporal constraint: the US is placed only during intertrial intervals, and every US is separated from every CS by at least `min_separation`. This stricter control was introduced to address criticisms of the truly-random procedure (Ayres, Benedict, & Witcher, 1975).

**Parameter semantics.**
- `cs`, `us` — CS and US labels.
- `min_separation` — minimum temporal separation between any CS and any US event, typically expressed in seconds.

**Example.**
```
ExplicitlyUnpaired(tone, shock, min_separation=30-s)
```

**Primary citations.**
- Rescorla, R. A. (1967). Pavlovian conditioning and its proper control procedures. *Psychological Review*, 74(1), 71–80. https://doi.org/10.1037/h0024109
- Ayres, J. J. B., Benedict, J. O., & Witcher, E. S. (1975). Systematic manipulation of individual events in a truly random control in rats. *Journal of Comparative and Physiological Psychology*, 88(1), 97–103. https://doi.org/10.1037/h0076200

**Related primitives.** Refinement of R8 with `p_us_given_cs = 0`. Distinct from R9 (`TrulyRandom`) by the `min_separation` constraint, which prevents accidental short-latency CS-US co-occurrences.

---

## R11. `Compound(cs_list, mode=Simultaneous)`

**Operational definition.** Multiple CSs are presented together. In the default `Simultaneous` mode, all CSs in `cs_list` share onset and offset; other modes are extensions and are not defined at Tier A.

**Parameter semantics.**
- `cs_list` — two or more CS labels.
- `mode` — onset-coordination mode; defaults to `Simultaneous`. Other modes live in the Respondent extension point.

**Example.**
```
Compound([tone, light])                          -- defaults to mode=Simultaneous
Compound([tone, light], mode=Simultaneous)       -- explicit
```

**Primary citation.** Rescorla, R. A., & Wagner, A. R. (1972). A theory of Pavlovian conditioning: Variations in the effectiveness of reinforcement and nonreinforcement. In A. H. Black & W. F. Prokasy (Eds.), *Classical conditioning II: Current research and theory* (pp. 64–99). Appleton-Century-Crofts.

**Related primitives.** Paired with a US (via an enclosing phase-level annotation or by embedding in a `Pair.*` construction that admits compound CSs) forms the basis of blocking, overshadowing, and related Tier B procedures.

---

## R12. `Serial(cs_list, isi)`

**Operational definition.** CSs are presented in temporal order with an inter-CS interval of `isi`. Unlike `Compound`, `Serial` does not accept a `mode` argument — seriality already implies temporal ordering.

**Parameter semantics.**
- `cs_list` — two or more CS labels, in presentation order.
- `isi` — inter-CS interval between consecutive CS offsets and onsets.

**Example.**
```
Serial([light, tone], isi=3-s)
```

**Primary citation.** Rescorla, R. A. (1972). Informational variables in Pavlovian conditioning. In G. H. Bower (Ed.), *The psychology of learning and motivation* (Vol. 6, pp. 1–46). Academic Press. https://doi.org/10.1016/S0079-7421(08)60383-7

**Related primitives.** Serial compound stimuli are the structural basis for serial-order Pavlovian arrangements, including some feature-positive and feature-negative procedures at Tier B.

---

## R13. `ITI(distribution, mean)`

**Operational definition.** The intertrial interval between successive CS-US or CS-alone trials. ITI is a structural determinant of CR acquisition rate via the I/T ratio (Gibbon & Balsam, 1981; Gallistel & Gibbon, 2000).

**Parameter semantics.**
- `distribution` — one of `fixed`, `uniform`, `exponential`.
- `mean` — mean ITI duration.

**Example.**
```
ITI(exponential, mean=60-s)
ITI(fixed, mean=30-s)
```

**Primary citations.**
- Gibbon, J., & Balsam, P. (1981). Spreading association in time. In C. M. Locurto, H. S. Terrace, & J. Gibbon (Eds.), *Autoshaping and conditioning theory* (pp. 219–253). Academic Press.
- Gallistel, C. R., & Gibbon, J. (2000). Time, rate, and conditioning. *Psychological Review*, 107(2), 289–344. https://doi.org/10.1037/0033-295X.107.2.289

**Related primitives.** Distinguished from the `@iti(distribution, mean, jitter)` annotation (see `annotations/extensions/respondent-annotator.md`): the primitive is a structural element; the annotation adds jitter metadata. When jitter is irrelevant, the primitive alone suffices.

---

## R14. `Differential(cs_positive, cs_negative, us)`

**Operational definition.** Two CSs are trained contrastively: `cs_positive` is paired with the US on every reinforced trial; `cs_negative` is presented without the US on every non-reinforced trial. The procedure establishes Pavlovian discrimination (CR to CS+; no CR or reduced CR to CS−).

**Parameter semantics.**
- `cs_positive` — CS paired with US.
- `cs_negative` — CS presented without US.
- `us` — the US used on reinforced trials. Explicit in the full form; the short form `Differential(cs_positive, cs_negative)` elides this and infers the US from an enclosing `@us` annotation.

**Example.**
```
Differential(tone_plus, tone_minus, shock)   -- full form
Differential(tone_plus, tone_minus)          -- short form; US from @us annotation
```

**Primary citations.**
- Pavlov, I. P. (1927). *Conditioned reflexes*. Oxford University Press.
- Mackintosh, N. J. (1974). *The psychology of animal learning*. Academic Press.

**Related primitives.** Rationale for Tier A: encoding the contrastive intent as a composition of R1 (`Pair.ForwardDelay`) plus R6 (`CSOnly`) loses the experimenter-intent signal that `cs_positive` and `cs_negative` are jointly varied. JEAB and related journals use differential conditioning as a common procedure; promoting it to Tier A avoids boundary-edge cases in extension-package design. The feature-positive / feature-negative variants and conditioned-inhibition procedures (Rescorla, 1969) remain in Tier B.

---

## Tier A / Tier B Boundary Summary

The Tier A set above is closed under the intent "cover the founding respondent procedures that the contingency-space (Rescorla, 1967) formalism directly names or requires as controls." Procedures whose operational definitions add **structural relationships across trials or phases** (e.g., blocking requires a prior acquisition phase with compound CS; renewal requires context change) are placed in Tier B and delegated to the Respondent extension point (`contingency-respondent-dsl`).

---

## Consolidated References

- Ayres, J. J. B., Benedict, J. O., & Witcher, E. S. (1975). Systematic manipulation of individual events in a truly random control in rats. *Journal of Comparative and Physiological Psychology*, 88(1), 97–103. https://doi.org/10.1037/h0076200
- Bouton, M. E. (2004). Context and behavioral processes in extinction. *Learning & Memory*, 11(5), 485–494. https://doi.org/10.1101/lm.78804
- Ellison, G. D. (1964). Differential salivary conditioning to traces. *Journal of Comparative and Physiological Psychology*, 57(3), 373–380. https://doi.org/10.1037/h0043484
- Gallistel, C. R., & Gibbon, J. (2000). Time, rate, and conditioning. *Psychological Review*, 107(2), 289–344. https://doi.org/10.1037/0033-295X.107.2.289
- Gibbon, J., & Balsam, P. (1981). Spreading association in time. In C. M. Locurto, H. S. Terrace, & J. Gibbon (Eds.), *Autoshaping and conditioning theory* (pp. 219–253). Academic Press.
- Lubow, R. E., & Moore, A. U. (1959). Latent inhibition: The effect of nonreinforced pre-exposure to the conditional stimulus. *Journal of Comparative and Physiological Psychology*, 52(4), 415–419. https://doi.org/10.1037/h0046700
- Mackintosh, N. J. (1974). *The psychology of animal learning*. Academic Press.
- Pavlov, I. P. (1927). *Conditioned reflexes: An investigation of the physiological activity of the cerebral cortex* (G. V. Anrep, Trans.). Oxford University Press.
- Randich, A., & LoLordo, V. M. (1979). Associative and nonassociative theories of the UCS preexposure phenomenon. *Psychological Bulletin*, 86(3), 523–548. https://doi.org/10.1037/0033-2909.86.3.523
- Rescorla, R. A. (1967). Pavlovian conditioning and its proper control procedures. *Psychological Review*, 74(1), 71–80. https://doi.org/10.1037/h0024109
- Rescorla, R. A. (1968). Probability of shock in the presence and absence of CS in fear conditioning. *Journal of Comparative and Physiological Psychology*, 66(1), 1–5. https://doi.org/10.1037/h0025984
- Rescorla, R. A. (1969). Pavlovian conditioned inhibition. *Psychological Bulletin*, 72(2), 77–94. https://doi.org/10.1037/h0027760
- Rescorla, R. A. (1972). Informational variables in Pavlovian conditioning. In G. H. Bower (Ed.), *The psychology of learning and motivation* (Vol. 6, pp. 1–46). Academic Press. https://doi.org/10.1016/S0079-7421(08)60383-7
- Rescorla, R. A. (1980). Simultaneous and successive associations in sensory preconditioning. *Journal of Experimental Psychology: Animal Behavior Processes*, 6(3), 207–216. https://doi.org/10.1037/0097-7403.6.3.207
- Rescorla, R. A., & Wagner, A. R. (1972). A theory of Pavlovian conditioning: Variations in the effectiveness of reinforcement and nonreinforcement. In A. H. Black & W. F. Prokasy (Eds.), *Classical conditioning II: Current research and theory* (pp. 64–99). Appleton-Century-Crofts.
- Spetch, M. L., Wilkie, D. M., & Pinel, J. P. J. (1981). Backward conditioning: A reevaluation of the empirical evidence. *Psychological Bulletin*, 89(1), 163–175. https://doi.org/10.1037/0033-2909.89.1.163
