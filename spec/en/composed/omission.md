# Omission (Negative Automaintenance)

> Part of the contingency-dsl composed layer. Omission is a diagnostic procedure: a forward Pavlovian pairing is programmed as in autoshaping, but with the additional constraint that any response during the CS **cancels** the scheduled US on that trial. Omission separates Pavlovian from operant control of autoshaped responding: if the response were operant in nature, the omission contingency would quickly extinguish it; if the response is Pavlovian, it often persists despite the omission.

**Companion documents:**
- [Autoshaping](autoshaping.md) — the procedure from which omission diverges diagnostically.
- [Two-Process Theory](two-process-theory.md) — the theoretical framework that motivates the diagnostic distinction.
- [Respondent Primitives](../respondent/primitives.md) — `Pair.ForwardDelay` as the underlying arrangement.
- [Operant Schedules](../operant/schedules/differential.md) — related operant omission schedules (DRO).

---

## 1. Procedure

Williams and Williams (1969) trained pigeons under a modified autoshaping procedure: the key light (CS) was presented for a fixed duration and followed by grain (US) as in standard autoshaping, **except** that a key peck during CS presentation immediately cancelled the US for that trial. Under a purely operant account, pecking should extinguish because it no longer produces food; indeed, pecking is now an operant that *prevents* food.

Contrary to this prediction, pigeons continued to peck the key light at substantial rates across many sessions, losing reinforcement on trial after trial. Williams and Williams (1969) termed the effect "negative automaintenance" — the auto-maintained response persisted under a negative response–outcome contingency. This persistence is not compatible with a simple operant account of autoshaped pecking.

## 2. Diagnostic Function

The omission procedure is **diagnostic** for the locus of control of autoshaped responding:

- If autoshaping were operant in origin, pecking should extinguish under the omission contingency (because pecking now reduces reinforcement).
- If autoshaping is Pavlovian in origin, pecking should persist because the Pavlovian CS–US contingency still elicits the response — even though the US is intermittently lost.

The persistence observed by Williams and Williams (1969) is the standard empirical argument for the Pavlovian-control account of autoshaping.

## 3. Relationship to Autoshaping

Omission is a structural modification of autoshaping (`autoshaping.md`): same CS, same US, same forward Pavlovian arrangement, with an **added operant constraint** (response during CS → US cancellation on that trial). The modification introduces an operant constituent into what would otherwise be a pure Pavlovian procedure, which is why omission lives in the composed layer rather than the respondent layer.

The response–US relationship in omission is **negative-contingent**: the response reduces the probability of the US. This is structurally distinct from punishment (which adds an aversive US contingent on a response) and from differential reinforcement of other behavior (DRO), which is an operant arrangement where the reinforcer is withheld unless the target response has been absent for a specified duration.

## 4. DSL Encoding

The omission contingency is expressed by adding the `PUNISH(...)` directive or by using an operant constraint that cancels the scheduled US on response. A minimal encoding:

```
Phase(
  name = "omission_training",
  respondent = Pair.ForwardDelay(key_light, food, isi=8-s, cs_duration=8-s),
  operant_constraint = Overlay(EXT, cancel_us_on_response=true),
  criterion = FixedSessions(n=10)
)
@cs(label="key_light", duration=8-s, modality="visual")
@us(label="food", intensity="3s_access", delivery="cancelled_on_cs_response")
```

The `operant_constraint` field (part of the experiment-layer phase specification) expresses the contingency that a response during CS cancels the scheduled US. Programs may encode this via specific operant combinators or via a dedicated omission directive; the DSL's grammar admits both encodings as long as the semantic outcome (CS-response → US omission for that trial) is clear.

## 5. Classification within the Taxonomy

Omission is the single clearest case where a **diagnostic** procedure (rather than a theoretically novel one) earns a place in the composed layer. Its contingency structure is identical to autoshaping except for the response→US-cancellation term; that small structural addition is decisive for the interpretation of the maintained responding, and for that reason it is documented as a named procedure rather than left implicit.

## 6. Citation

- Williams, D. R., & Williams, H. (1969). Auto-maintenance in the pigeon: Sustained pecking despite contingent non-reinforcement. *Journal of the Experimental Analysis of Behavior*, 12(4), 511–520. https://doi.org/10.1901/jeab.1969.12-511
