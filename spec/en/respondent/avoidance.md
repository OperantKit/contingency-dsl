# Avoidance (Respondent Vocabulary)

> Part of the contingency-dsl respondent layer. In the respondent vocabulary, an avoidance procedure is a forward CS–US pairing with one added response→stimulus dependency: a response during the CS cancels that trial's US or postpones it. `@avoidance` is the respondent layer's alias for the neutral response→stimulus dependency in its cancellation and postponement forms ([Respondent Theory §0](theory.md#0-stimulus-roles-as-aliases)).

**Companion documents:**
- [Omission](omission.md) — the other respondent-layer response→stimulus dependency (`@omission`).
- [composed-annotator](../annotations/extensions/composed-annotator.md) — the definition of `@avoidance` and its parameters.
- [Operant Theory §2.9](../operant/theory.md#29-discriminated-avoidance) — the same kind of procedure written in the operant vocabulary (`DiscriminatedAvoidance`).
- [Two-Process Theory](../composed/two-process-theory.md) — an interpretive framework that spans the operant and respondent layers; its conformance fixture combines an operant phase with this encoding.

---

## 1. Procedure

A warning stimulus (CS) is presented and is followed by an aversive US at its offset, as in a forward pairing. If the subject emits the named response during the CS, the US on that trial is cancelled (`mode="cancel"`, the default) or the CS offset / US onset is postponed (`mode="postpone"`).

## 2. DSL Encoding

```
@cs(label="tone", duration=5-s, modality="auditory")
@us(label="shock", intensity="0.8mA")

phase avoidance_training:
  sessions = 20
  Pair.ForwardDelay(tone, shock, isi=5-s, cs_duration=5-s) @avoidance(response="lever_press", mode="cancel")
```

The pairing itself is unchanged; an analyzer / executor pass interprets the annotation. At most one of `@omission` / `@avoidance` may be attached to a single respondent primitive (composed-annotator §4).

## 3. Two Vocabularies

The operant layer writes avoidance with its own primitives (`DiscriminatedAvoidance`, `Sidman`). This document does not state that a particular `DiscriminatedAvoidance` program and the encoding above produce the same stimulus sequence for the same response sequence; that has not been checked by an execution test.

## 4. Citation

- Solomon, R. L., & Wynne, L. C. (1954). Traumatic avoidance learning: The principles of anxiety conservation and partial irreversibility. *Psychological Review*, 61(6), 353–385. https://doi.org/10.1037/h0054540
