# Autoshaping / Sign-Tracking

> Part of the contingency-dsl composed layer. Autoshaping is the spontaneous emergence of approach and engagement responses directed at a localized CS (e.g., a key light, an inserted lever) under a forward Pavlovian CS–US contingency. No operant response contingency is programmed, yet organisms come to emit a directed response to the CS.

**Companion documents:**
- [Two-Process Theory](two-process-theory.md) — Pavlovian-instrumental framework.
- [Omission](omission.md) — the variant in which a response during the CS cancels that trial's US.
- [Respondent Primitives](../respondent/primitives.md) — `Pair.ForwardDelay` as the underlying Pavlovian arrangement.

---

## 1. Procedure

Brown and Jenkins (1968) trained naïve pigeons under a forward Pavlovian contingency: a response key was illuminated (CS) for a fixed duration, followed immediately by grain delivery (US). No key-peck was required for grain delivery; the US was Pavlovian. Within a small number of CS presentations, pigeons began to orient toward the lit key and ultimately to peck it. The pecking emerged in the absence of any response-contingent reinforcement arrangement.

The procedure spread beyond pigeons: rats approach and contact inserted levers that signal food (lever-directed sign-tracking), and numerous species show comparable CS-directed behavior when the CS is localizable in the chamber.

## 2. Sign-Tracking and Goal-Tracking

Two response topographies are distinguished:

- **Sign-tracking.** The subject approaches and engages the CS itself (the key light, the lever). Sign-tracking is the signature effect that Brown and Jenkins (1968) described.
- **Goal-tracking.** The subject approaches the US delivery location (the food magazine) during CS presentation. Goal-tracking emerges under the same CS–US procedure but is directed at the US source rather than the CS.

Both topographies emerge under the same CS–US contingency but are differentially expressed across individuals and species. The DSL expresses the procedure identically in both cases; topography is an observable, not a grammar-level distinction.

## 3. Classification: Composed, Not Operant

The procedural facts that the DSL encodes are these:

1. **US delivery is set by CS offset and does not depend on the subject's response.** No response is required for US delivery, and the programmed schedule makes no reference to the key peck.
2. **The key peck is not part of the programmed arrangement.** It is an observed response, recorded through `@measurement` annotations (§4), not a term of the schedule.
3. **The omission variant adds one response→stimulus dependency.** In `omission.md`, a response during the CS cancels that trial's US.

How the emergent key peck should be interpreted is a question for the theory layers, not for this procedure document. The respondent tradition's reading of autoshaping and omission is in [Respondent Theory §6](../respondent/theory.md#6-interpretive-notes-the-respondent-traditions-reading-of-autoshaping-and-omission); the operant layer reserves a place for its reading in [Operant Theory, Interpretive Notes](../operant/theory.md#interpretive-notes--the-operant-traditions-reading-of-autoshaping-and-omission).

## 4. DSL Encoding

```
@cs(label="key_light", duration=8-s, modality="visual")
@us(label="food", intensity="3s_access", delivery="unsignaled")

phase autoshaping_training:
  sessions = 10
  Pair.ForwardDelay(key_light, food, isi=8-s, cs_duration=8-s)
```

The key light is a localized CS (attached to a specific chamber operandum); the DSL does not require a separate "operant response" production because none is programmed. The phase body is a single Pavlovian primitive. The emergent key-peck is recorded via `@measurement` annotations (not shown) rather than through the operant grammar.

## 5. Citation

- Brown, P. L., & Jenkins, H. M. (1968). Auto-shaping of the pigeon's key-peck. *Journal of the Experimental Analysis of Behavior*, 11(1), 1–8. https://doi.org/10.1901/jeab.1968.11-1
