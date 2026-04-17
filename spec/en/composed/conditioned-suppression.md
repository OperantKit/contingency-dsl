# Conditioned Suppression (CER)

> Part of the contingency-dsl composed layer. The Conditioned Emotional Response (CER) procedure combines an operant appetitive baseline with a Pavlovian aversive overlay; conditioned suppression of the operant baseline during CS presentation is the principal dependent measure.

**Companion documents:**
- [Two-Process Theory](two-process-theory.md) — the Rescorla–Solomon (1967) framework that motivates composed procedures.
- [Operant Grammar](../operant/grammar.md) — operant baseline productions.
- [Respondent Grammar](../respondent/grammar.md) — Pavlovian overlay productions.
- [Experiment / Phase Sequence](../experiment/phase-sequence.md) — multi-phase composition.

---

## 1. Procedure

Estes and Skinner (1941) introduced the CER procedure. A subject is first trained on an operant appetitive schedule (typically a variable-interval schedule maintaining a stable baseline response rate). After baseline stability, a Pavlovian forward-delay pairing is superimposed: a CS (e.g., tone) is presented for a fixed duration, terminating with an aversive US (e.g., unsignaled brief shock). The US is delivered **independently of the subject's responding** — the CS–US relation is Pavlovian, not operant.

Response rate during the CS is suppressed relative to response rate in the pre-CS baseline interval. The suppression magnitude is the primary dependent measure.

## 2. Suppression Ratio

Annau and Kamin (1961) formalized the **suppression ratio** as the standard quantitative measure:

`SR = B / (A + B)`

where `A` is the response count during the pre-CS interval (of the same duration as CS) and `B` is the response count during the CS. Values:

- `SR = 0.5` — no suppression (response rate during CS = pre-CS rate).
- `SR = 0` — complete suppression (no responses during CS).
- `SR → 0` during acquisition — the CS suppresses operant baseline as the Pavlovian association strengthens.

Annau and Kamin (1961) showed that suppression-ratio acquisition is a graded function of US intensity.

## 3. DSL Encoding

CER is composed at the Experiment layer: an operant baseline schedule runs throughout the session; a Pavlovian phase-level overlay introduces the CS–US contingency. The DSL expresses this via a single phase whose operant component is a VI baseline and whose respondent component is a forward-delay Pair primitive. Annotations (`@cs`, `@us` from `annotations/extensions/respondent-annotator.md`) record stimulus metadata.

```
Phase(
  name = "cer_training",
  operant = VI 60-s,
  respondent = Pair.ForwardDelay(tone, shock, isi=60-s, cs_duration=60-s),
  criterion = Stability(window=5, tolerance=0.10)
)
@cs(label="tone", duration=60-s, modality="auditory")
@us(label="shock", intensity="0.5mA", delivery="unsignaled")
```

The operant baseline and the Pavlovian overlay coexist in the same phase because the US is delivered on the Pavlovian schedule independently of the operant response class. This temporal independence is what makes CER a composed procedure rather than a punishment procedure on the operant baseline.

## 4. Distinction from Punishment

Punishment delivers the aversive stimulus **contingent on a response** (a three-term aversive contingency). CER delivers the aversive stimulus **contingent on a stimulus** (a two-term Pavlovian contingency). The structural distinction is preserved at the grammar level: punishment is an operant-layer construct (see `operant/grammar.md §1.4` and the `Overlay` combinator); CER's US delivery is a respondent-layer construct.

## 5. Relationship to Two-Process Theory

CER is the canonical demonstration that a Pavlovian CS acquires motivational properties that modulate operant performance. Under the Rescorla–Solomon (1967) two-process framework (see `two-process-theory.md`), the CS–shock association generates a conditioned aversive state; this state suppresses appetitive operant performance because the two states are motivationally incompatible.

## 6. Citations

- Annau, Z., & Kamin, L. J. (1961). The conditioned emotional response as a function of intensity of the US. *Journal of Comparative and Physiological Psychology*, 54(4), 428–432. https://doi.org/10.1037/h0042199
- Estes, W. K., & Skinner, B. F. (1941). Some quantitative properties of anxiety. *Journal of Experimental Psychology*, 29(5), 390–400. https://doi.org/10.1037/h0062283
- Rescorla, R. A., & Solomon, R. L. (1967). Two-process learning theory: Relationships between Pavlovian conditioning and instrumental learning. *Psychological Review*, 74(3), 151–182. https://doi.org/10.1037/h0024475
