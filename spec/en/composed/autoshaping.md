# Autoshaping / Sign-Tracking

> Part of the contingency-dsl composed layer (Ψ). Autoshaping is the spontaneous emergence of approach and engagement responses directed at a localized CS (e.g., a key light, an inserted lever) under a forward Pavlovian CS–US contingency. No operant response contingency is programmed, yet organisms come to emit a directed response to the CS.

**Companion documents:**
- [Two-Process Theory](two-process-theory.md) — Pavlovian-instrumental framework.
- [Omission](omission.md) — the diagnostic procedure that distinguishes Pavlovian from operant control of autoshaped responding.
- [Respondent Primitives](../respondent/primitives.md) — `Pair.ForwardDelay` as the underlying Pavlovian arrangement.

---

## 1. Procedure

Brown and Jenkins (1968) trained naïve pigeons under a forward Pavlovian contingency: a response key was illuminated (CS) for a fixed duration, followed immediately by grain delivery (US). No key-peck was required for grain delivery; the US was Pavlovian. Within a small number of CS presentations, pigeons began to orient toward the lit key and ultimately to peck it. The pecking emerged in the absence of any response-contingent reinforcement arrangement.

The procedure spread beyond pigeons: rats approach and contact inserted levers that signal food (lever-directed sign-tracking), and numerous species show comparable CS-directed behavior when the CS is localizable in the chamber.

## 2. Sign-Tracking and Goal-Tracking

Two response topographies are distinguished:

- **Sign-tracking.** The subject approaches and engages the CS itself (the key light, the lever). Sign-tracking is the signature effect that Brown and Jenkins (1968) described.
- **Goal-tracking.** The subject approaches the US delivery location (the food magazine) during CS presentation. Goal-tracking is likewise Pavlovian but is directed at the US source rather than the CS.

Both topographies emerge under the same CS–US contingency but are differentially expressed across individuals and species. The DSL expresses the procedure identically in both cases; topography is an observable, not a grammar-level distinction.

## 3. Classification: Composed, Not Operant

Some reviews classify autoshaping as an operant procedure on the grounds that the emergent response (key peck) is the same topography that operant reinforcement typically maintains. This classification misreads the **contingency arrangement**: no operant contingency is programmed. The response is not required for US delivery and is in fact irrelevant to the programmed schedule.

The DSL places autoshaping under `composed/` rather than `operant/` for the following reasons:

1. **The US–schedule relation is Pavlovian.** US delivery is contingent on CS offset, not on the subject's response.
2. **The response class emerges under Pavlovian contingencies.** The subject's key peck is an elicited / evoked response directed at a CS, not a response selected by its consequence.
3. **The diagnostic procedure (omission; see `omission.md`) decisively separates Pavlovian from operant control.** When responses during CS cancel the US, autoshaped pecking often persists — the hallmark of Pavlovian-rather-than-operant maintenance.

Classifying autoshaping as composed preserves the structural distinction the DSL enforces between the two-term and three-term contingencies.

## 4. DSL Encoding

```
Phase(
  name = "autoshaping_training",
  respondent = Pair.ForwardDelay(key_light, food, isi=8-s, cs_duration=8-s),
  criterion = FixedSessions(n=10)
)
@cs(label="key_light", duration=8-s, modality="visual")
@us(label="food", intensity="3s_access", delivery="unsignaled")
```

The key light is a localized CS (attached to a specific chamber operandum); the DSL does not require a separate "operant response" production because none is programmed. The emergent key-peck is recorded via `@measurement` annotations (not shown) rather than through the operant grammar.

## 5. Citation

- Brown, P. L., & Jenkins, H. M. (1968). Auto-shaping of the pigeon's key-peck. *Journal of the Experimental Analysis of Behavior*, 11(1), 1–8. https://doi.org/10.1901/jeab.1968.11-1
