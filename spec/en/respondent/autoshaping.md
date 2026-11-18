# Autoshaping / Sign-Tracking

> Part of the contingency-dsl respondent layer. Autoshaping is the spontaneous emergence of approach and engagement responses directed at a localized CS (e.g., a key light, an inserted lever) under a forward CS–US pairing. No response→stimulus dependency is programmed, yet organisms come to emit a directed response to the CS.

**Companion documents:**
- [Omission](omission.md) — the variant in which a response during the CS cancels that trial's US.
- [Respondent Primitives](primitives.md) — `Pair.ForwardDelay` as the underlying arrangement.
- [Time Schedules](../operant/schedules/time.md#61-signaled-fixed-time-the-autoshaping-arrangement-in-operant-vocabulary) — the same arrangement written in the operant vocabulary (signaled FT).
- [Two-Process Theory](../composed/two-process-theory.md) — an interpretive framework that spans the operant and respondent layers.

---

## 1. Procedure

Brown and Jenkins (1968) trained naïve pigeons under a forward CS–US pairing: a response key was illuminated (CS) for a fixed duration, followed immediately by grain delivery (US). No key-peck was required for grain delivery. Within a small number of CS presentations, pigeons began to orient toward the lit key and ultimately to peck it. The pecking emerged in the absence of any response→stimulus dependency.

The procedure spread beyond pigeons: rats approach and contact inserted levers that signal food (lever-directed sign-tracking), and numerous species show comparable CS-directed behavior when the CS is localizable in the chamber.

## 2. Sign-Tracking and Goal-Tracking

Two response topographies are distinguished:

- **Sign-tracking.** The subject approaches and engages the CS itself (the key light, the lever). Sign-tracking is the signature effect that Brown and Jenkins (1968) described.
- **Goal-tracking.** The subject approaches the US delivery location (the food magazine) during CS presentation. Goal-tracking emerges under the same CS–US procedure but is directed at the US source rather than the CS.

Both topographies emerge under the same CS–US procedure but are differentially expressed across individuals and species. The DSL expresses the procedure identically in both cases; topography is an observable, not a grammar-level distinction.

## 3. DSL Encoding

```
@cs(label="key_light", duration=8-s, modality="visual")
@us(label="food", intensity="3s_access", delivery="unsignaled")

phase autoshaping_training:
  sessions = 10
  Pair.ForwardDelay(key_light, food, isi=8-s, cs_duration=8-s)
```

The encoding states these procedural facts:

1. **US delivery is set by CS offset and does not depend on the subject's response.** The programmed arrangement makes no reference to the key peck.
2. **The key peck is not part of the programmed arrangement.** It is an observed response, recorded through `@measurement` annotations (not shown), not a term of the arrangement.
3. **The omission variant adds one response→stimulus dependency.** In [Omission](omission.md), a response during the CS cancels that trial's US.

The key light is a localized CS (attached to a specific chamber operandum). The phase body is a single respondent primitive.

How the emergent key peck is interpreted is a question for the theory layers, not for this procedure document. The respondent tradition's reading is in [Respondent Theory §6](theory.md#6-interpretive-notes-the-respondent-traditions-reading-of-autoshaping-and-omission); the operant layer reserves a place for its reading in [Operant Theory, Interpretive Notes](../operant/theory.md#interpretive-notes--the-operant-traditions-reading-of-autoshaping-and-omission).

## 4. Citation

- Brown, P. L., & Jenkins, H. M. (1968). Auto-shaping of the pigeon's key-peck. *Journal of the Experimental Analysis of Behavior*, 11(1), 1–8. https://doi.org/10.1901/jeab.1968.11-1
