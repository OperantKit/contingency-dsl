# Respondent Theory — The Two-Term Contingency (CS–US)

> Part of the contingency-dsl respondent layer. Defines the two-term contingency as a distinct formal object from the three-term (operant) contingency, introduces the Rescorla (1967, 1968) contingency space as the semantic target of the respondent grammar, discusses acquisition and extinction without appealing to response strengthening, and situates the intertrial interval (ITI) as a structural determinant of conditioned-response (CR) acquisition.

**Companion documents:**
- [Respondent Grammar](grammar.md) — EBNF productions and extension point.
- [Respondent Primitives](primitives.md) — R1–R14 operational definitions.
- [Foundations Theory](../foundations/theory.md) — paradigm-neutral definition of contingency.
- [Dependency Types](../foundations/contingency-types.md) — paradigm-neutral dependency types.
- [Stimuli](../foundations/stimulus-typing.md) — stimulus name, physical properties, onset and offset.

---

## 0. Stimulus Roles as Aliases

The foundations layer defines stimuli by name and physical properties and defines the paradigm-neutral dependency types. The respondent layer's role names are aliases for positions in those types. An alias adds no meaning beyond the position.

| Alias | Symbol | Position in the paradigm-neutral dependency types |
|---|---|---|
| Unconditioned stimulus | US | The later stimulus of a stimulus→stimulus dependency |
| Conditioned stimulus | CS | The earlier stimulus of a stimulus→stimulus dependency |

**CS and US are primitive-level.** In the respondent layer, CS and US are constructor arguments: `Pair.ForwardDelay(cs, us, isi, cs_duration)`, `Contingency(p_us_given_cs, p_us_given_no_cs)`, etc. Their physical properties are attached via `@cs` and `@us` annotations (provided by `annotations/extensions/respondent-annotator`).

```
Pair.ForwardDelay(tone, shock, isi=5-s, cs_duration=10-s)
  @cs("tone", frequency=4000, modality="auditory")
  @us("shock", intensity="0.5mA", modality="electrical")
```

The respondent layer also has response→stimulus dependencies in its own vocabulary. `@omission` and `@avoidance` are the respondent layer's aliases for the neutral response→stimulus dependency in its cancellation and postponement forms ([foundations/contingency-types.md](../foundations/contingency-types.md)); the procedures that use them are [Omission](omission.md) and [Avoidance](avoidance.md). The keywords and their schema are those of the composed-annotator extension ([composed-annotator](../annotations/extensions/composed-annotator.md)); only their placement as respondent-layer aliases is stated here.

### Notes: the Respondent Tradition's Effect Definitions and Valence

These notes record readings of the respondent tradition; they are not part of the alias definitions, and the DSL does not check them.

- **Effect definitions.** The tradition defines the US as a biologically significant stimulus that elicits an unconditioned response (UR), and the CS as a stimulus that comes to elicit a conditioned response (CR) through its pairing with the US (Pavlov, 1927).
- **Valence.** Respondent primitives (`Pair.*`, `Contingency(...)`, etc.) do not encode whether the US is appetitive or aversive. Fear conditioning (an aversive US in the tradition's reading) and appetitive conditioning share identical respondent-layer grammar; they differ only in which stimulus is named as the US. The DSL does not record valence; no annotation schema has a valence parameter.

---

## 1. The Two-Term Contingency as a Distinct Formal Object

Skinner (1938) drew a structural distinction between **operant** (three-term) and **respondent** (two-term) contingencies. The three-term contingency specifies a relation `P(Sr+ | R, SD)` in which a response `R` emitted in the presence of a discriminative stimulus `SD` is followed by a reinforcer; the two-term contingency specifies a relation `P(US | CS)` in which the presence of a conditional stimulus `CS` is differentially correlated, in the statistical sense, with the occurrence of an unconditional stimulus `US`. Both are specializations of the paradigm-neutral contingency `(A, B, P)` of [Foundations Definition 2](../foundations/theory.md); they differ in the event types they relate. The response `R` is *absent* from the respondent arrangement, and the respondent tradition treats this absence as structural rather than trivial.

The respondent tradition does not treat the two-term contingency as a "degenerate" three-term contingency in which the response position has been erased, because that reading would collapse the CS into an `SD` role and the CR into an operant `R`. The tradition gives three considerations against the collapse:

1. **The CR is elicited, not emitted.** In Pavlov (1927), salivation is elicited by the CS after training; it is not a behavior whose future probability is modulated by its consequence. An operant response, by contrast, is emitted and is selected by the consequence that follows it (Skinner, 1938).
2. **The US is unconditional on the subject's behavior.** In the canonical Pavlovian arrangement, the US is delivered whether or not the subject responds. When a response *is* required (or prohibited) for US delivery, the arrangement adds a response→stimulus dependency to the two-term contingency (see [Omission](omission.md)).
3. **CS predictiveness, not response strength, is the semantic target.** Rescorla (1967, 1968) established that the CS must *predict* the US in the statistical sense — `P(US | CS) ≠ P(US | ¬CS)` — for a CR to acquire. The semantic currency of the respondent layer is CS-US contingency, not response-reinforcer contingency.

Accordingly, the contingency-dsl respondent grammar (`grammar.md §2`) has its own productions for `PairExpr`, `ContingencyExpr`, `ExtinctionExpr`, and so on, and does not reduce to operant productions. The two-term and three-term contingencies share only the paradigm-neutral foundations layer (`foundations/contingency-types.md`).

---

## 2. The Rescorla Contingency Space

Rescorla (1967, 1968) demonstrated that the critical determinant of Pavlovian acquisition is not the mere number of CS-US pairings but the **differential probability of US given CS versus given no CS**. Two probabilities define a two-dimensional plane:

- `p = P(US | CS)` — probability of US during or just after a CS presentation.
- `q = P(US | ¬CS)` — probability of US during an intertrial interval (no CS).

The contingency-dsl Tier A primitive `Contingency(p, q)` parameterizes this plane directly. Every other Tier A Pavlovian arrangement corresponds to a specific region or point:

| Region / Point | Primitive | Description |
|---|---|---|
| `(1, 0)` corner | `Pair.ForwardDelay(cs, us, ...)` | Canonical forward pairing: US occurs iff CS occurred. |
| Diagonal `p = q` | `TrulyRandom(cs, us)` | CS–US statistical independence; `P(US | CS) = P(US | ¬CS)`. |
| `p = 0` axis (with `q > 0`) | `ExplicitlyUnpaired(cs, us, min_separation)` | Negative contingency with explicit temporal separation. |
| `(0, 0)` origin | `Extinction(cs)` (after acquisition) | No US is delivered at all; CR decrements. |
| `p = 0, q = 0` with CS-only trials | `CSOnly(cs, trials)` | Baseline / pre-exposure (latent-inhibition procedure when applied prior to acquisition). |

The grammar fixes the argument order `Contingency(p_us_given_cs, p_us_given_no_cs)` — CS-conditional first, ¬CS-conditional second — so that parse trees carry unambiguous semantics. The ordering is not permutable at the grammar level.

### 2.1 Why `Contingency(p, q)` Must Be Tier A

The contingency-space formulation is the modern foundation of respondent conditioning. A DSL that can express only the corner `(1, 0)` (forward pairing) and the origin `(0, 0)` (extinction) cannot encode the classic Rescorla (1967, 1968) demonstrations that `Pair.ForwardDelay` and `TrulyRandom` differ empirically in CR acquisition despite identical frequencies of CS-US co-occurrence. Placing `Contingency(p, q)` outside the Tier A set would therefore render the DSL unable to express a founding result of contemporary respondent theory.

### 2.2 `TrulyRandom` and `ExplicitlyUnpaired` as Control Procedures

Rescorla (1967) argued that "truly random" control procedures (`p = q`) and "explicitly unpaired" control procedures (`p = 0, q > 0`, with temporal separation) are empirically distinguishable and are the correct baselines for claims about CS-US association. Ayres, Benedict, and Witcher (1975) provided direct comparisons. Both controls are preserved as named primitives in Tier A (R9 and R10), not as convenience wrappers, because they encode distinct *experimenter intent* that should be visible in the parse tree.

---

## 3. Acquisition and Extinction Without Response Strengthening

Conditioned-response (CR) acquisition is a function of the differential correlation between CS and US (that is, CS predictiveness in the statistical sense: `P(US | CS) − P(US | ¬CS)`). The Rescorla–Wagner model (Rescorla & Wagner, 1972) formalizes this as error-driven associative strength: `ΔV_CS = α_CS β_US (λ - ΣV)` on each trial in which the CS is present. The model predicts (and Rescorla, 1968, confirms) that acquisition rate depends on `p - q`, not on `p` alone.

**Respondent extinction** (Pavlov, 1927; Bouton, 2004) is the decrement of CR when CS is presented without US. Three features distinguish respondent extinction from operant extinction:

1. **The original learning is not erased.** Bouton (2004) reviews evidence that the acquisition history persists through extinction: spontaneous recovery (recovery of CR after a retention interval), renewal (return of CR when context is changed), and reinstatement (return of CR after unsignaled US presentations) all indicate that extinction adds a new inhibitory association rather than overwriting the original.
2. **The semantic frame is CS predictiveness, not response strength.** Operant extinction can be described as a decrement in response rate under a zero-reinforcement schedule; respondent extinction is a decrement in CR magnitude when the CS ceases to predict the US. The two look similar in their decrement curves but refer to different empirical objects.
3. **Context-dependence is salient.** Because the CR is elicited rather than emitted, contextual stimuli present during extinction become part of what the subject learns (Bouton & Bolles, 1979). The respondent layer accommodates this via the `experiment/context.md` first-class Context construct and the `@context` annotation.

In contingency-dsl, extinction is represented by `Extinction(cs)` embedded in a phase that follows an acquisition phase. Phenomena that require context-sensitive account (renewal, reinstatement, spontaneous recovery) are delegated to `contingency-respondent-dsl` via the Respondent extension point.

---

## 4. Intertrial Interval and the I/T Ratio

The intertrial interval (ITI) is a structural determinant of CR acquisition, not merely a procedural detail. Gibbon and Balsam (1981) showed that the rate of CR acquisition in autoshaping is predicted by the **I/T ratio** — the ratio of average intertrial interval duration `I` to average trial (CS) duration `T`. When `I/T` is large, acquisition is rapid; when `I/T` is near 1, acquisition is slow or fails.

Gallistel and Gibbon (2000) generalized this into the Rate Estimation Theory (RET): the subject estimates the rate of US occurrence during the CS relative to during the context; CR onset occurs when the ratio of these estimates crosses a threshold. Under RET, `I/T` is the observable analog of the rate-ratio computation.

Two implications for the respondent layer:

1. **ITI must be specifiable at the primitive level.** Tier A includes `ITI(distribution, mean)` (R13). Without the ability to specify ITI, the DSL could not encode procedures whose empirical predictions depend on `I/T`.
2. **ITI is a structural element, not an annotation.** Annotations (`annotations/extensions/respondent-annotator.md`) add metadata to existing structure; they do not constitute structure. The `@iti` annotation provides jitter information that is orthogonal to the primitive-level ITI (mean and distribution family). When jitter is irrelevant, the primitive `ITI(...)` suffices; when jitter must be recorded, `@iti(distribution, mean, jitter)` annotates the enclosing phase.

The division of labor is:
- **Primitive `ITI(distribution, mean)`** — the structural element.
- **Annotation `@iti(distribution, mean, jitter)`** — the metadata overlay that records jitter and (optionally) redundantly the distribution and mean for reproducibility.

See `annotations/boundary-decision.md §2` (Q1–Q3) for the general principle: if omitting the construct alters the structure of the procedure, it is a primitive; if it only annotates an existing structure, it is an annotation.

---

## 5. Relationship to the Composed Layer

Two composed programs (`composed/conditioned-suppression.md`, `composed/pit.md`) combine an operant schedule with a respondent arrangement in one phase sequence. In each case, the respondent constituent is a Tier A primitive from this layer; the operant constituent is a schedule from `operant/schedules/`. `composed/two-process-theory.md` summarizes the Rescorla–Solomon (1967) two-process account, an interpretive tool that reads procedures across both theory layers.

Autoshaping, omission, and avoidance are written in the respondent vocabulary and are documented in this layer: [Autoshaping](autoshaping.md), [Omission](omission.md), [Avoidance](avoidance.md).

The present layer does not itself define the composed programs; it provides the respondent vocabulary those procedures draw upon.

---

## 6. Interpretive Notes: the Respondent Tradition's Reading of Autoshaping and Omission

The procedure documents ([Autoshaping](autoshaping.md), [Omission](omission.md)) record the arrangements and the observations only. This section states how the respondent tradition reads them. These are readings by that tradition, not conclusions of the DSL; the operant layer reserves a place for its own reading ([Operant Theory, Interpretive Notes](../operant/theory.md#interpretive-notes--the-operant-traditions-reading-of-autoshaping-and-omission)).

**Autoshaping.** The respondent tradition reads the key peck that emerges in Brown and Jenkins (1968) as an elicited / evoked response directed at a CS, not a response selected by its consequence. On this reading, the response class emerges under the CS–US dependency alone.

**Omission.** The respondent tradition reads the result of Williams and Williams (1969) as follows. If autoshaped pecking were maintained by its consequence, pecking should extinguish under the omission procedure, because each peck during the CS now cancels the US. If pecking is controlled by the CS–US dependency, pecking should persist because the CS still elicits it, even though the US is intermittently lost. Pigeons continued to peck, and the respondent tradition takes this persistence as its standard empirical argument that autoshaped pecking is under Pavlovian rather than operant control, and that omission separates the two kinds of control.

---

## References

- Ayres, J. J. B., Benedict, J. O., & Witcher, E. S. (1975). Systematic manipulation of individual events in a truly random control in rats. *Journal of Comparative and Physiological Psychology*, 88(1), 97–103. https://doi.org/10.1037/h0076215
- Bouton, M. E. (2004). Context and behavioral processes in extinction. *Learning & Memory*, 11(5), 485–494. https://doi.org/10.1101/lm.78804
- Bouton, M. E., & Bolles, R. C. (1979). Contextual control of the extinction of conditioned fear. *Learning and Motivation*, 10(4), 445–466. https://doi.org/10.1016/0023-9690(79)90057-2
- Brown, P. L., & Jenkins, H. M. (1968). Auto-shaping of the pigeon's key-peck. *Journal of the Experimental Analysis of Behavior*, 11(1), 1–8. https://doi.org/10.1901/jeab.1968.11-1
- Gallistel, C. R., & Gibbon, J. (2000). Time, rate, and conditioning. *Psychological Review*, 107(2), 289–344. https://doi.org/10.1037/0033-295X.107.2.289
- Gibbon, J., & Balsam, P. (1981). Spreading association in time. In C. M. Locurto, H. S. Terrace, & J. Gibbon (Eds.), *Autoshaping and conditioning theory* (pp. 219–253). Academic Press.
- Pavlov, I. P. (1927). *Conditioned reflexes: An investigation of the physiological activity of the cerebral cortex* (G. V. Anrep, Trans.). Oxford University Press.
- Rescorla, R. A. (1967). Pavlovian conditioning and its proper control procedures. *Psychological Review*, 74(1), 71–80. https://doi.org/10.1037/h0024109
- Rescorla, R. A. (1968). Probability of shock in the presence and absence of CS in fear conditioning. *Journal of Comparative and Physiological Psychology*, 66(1), 1–5. https://doi.org/10.1037/h0025984
- Rescorla, R. A., & Solomon, R. L. (1967). Two-process learning theory: Relationships between Pavlovian conditioning and instrumental learning. *Psychological Review*, 74(3), 151–182. https://doi.org/10.1037/h0024475
- Rescorla, R. A., & Wagner, A. R. (1972). A theory of Pavlovian conditioning: Variations in the effectiveness of reinforcement and nonreinforcement. In A. H. Black & W. F. Prokasy (Eds.), *Classical conditioning II: Current research and theory* (pp. 64–99). Appleton-Century-Crofts.
- Skinner, B. F. (1938). *The behavior of organisms*. Appleton-Century.
- Williams, D. R., & Williams, H. (1969). Auto-maintenance in the pigeon: Sustained pecking despite contingent non-reinforcement. *Journal of the Experimental Analysis of Behavior*, 12(4), 511–520. https://doi.org/10.1901/jeab.1969.12-511
