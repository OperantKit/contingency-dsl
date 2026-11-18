# Omission (Negative Automaintenance)

> Part of the contingency-dsl composed layer. In omission, a forward Pavlovian pairing is programmed as in autoshaping, with the additional constraint that any response during the CS **cancels** the scheduled US on that trial. How the theory layers read the responding maintained under this procedure is in [Respondent Theory §6](../respondent/theory.md#6-interpretive-notes-the-respondent-traditions-reading-of-autoshaping-and-omission) and [Operant Theory, Interpretive Notes](../operant/theory.md#interpretive-notes--the-operant-traditions-reading-of-autoshaping-and-omission).

**Companion documents:**
- [Autoshaping](autoshaping.md) — the same procedure without the response→US-cancellation term.
- [Two-Process Theory](two-process-theory.md) — an interpretive framework that spans the operant and respondent layers.
- [Respondent Primitives](../respondent/primitives.md) — `Pair.ForwardDelay` as the underlying arrangement.
- [Operant Schedules](../operant/schedules/differential.md) — related operant omission schedules (DRO).

---

## 1. Procedure

Williams and Williams (1969) trained pigeons under a modified autoshaping procedure: the key light (CS) was presented for a fixed duration and followed by grain (US) as in standard autoshaping, **except** that a key peck during CS presentation immediately cancelled the US for that trial.

Pigeons continued to peck the key light at substantial rates across many sessions, and the US was cancelled on those trials. Williams and Williams (1969) termed the effect "negative automaintenance" — the auto-maintained response persisted under a negative response–outcome dependency.

## 2. Interpretation

The procedure document records only the arrangement and the observation in §1. The respondent tradition's reading of the persistence is in [Respondent Theory §6](../respondent/theory.md#6-interpretive-notes-the-respondent-traditions-reading-of-autoshaping-and-omission); the operant layer reserves a place for its reading in [Operant Theory, Interpretive Notes](../operant/theory.md#interpretive-notes--the-operant-traditions-reading-of-autoshaping-and-omission).

## 3. Relationship to Autoshaping

Omission is a structural modification of autoshaping (`autoshaping.md`): same CS, same US, same forward Pavlovian arrangement, with one **added response→stimulus dependency** (a response during the CS cancels the US on that trial).

The response–US relationship in omission is **negative-contingent**: the response reduces the probability of the US. This is structurally distinct from punishment (which adds an aversive US contingent on a response) and from differential reinforcement of other behavior (DRO), which is an operant arrangement where the reinforcer is withheld unless the target response has been absent for a specified duration.

## 4. DSL Encoding

The omission contingency is expressed as an `@omission` annotation attached to the underlying Pavlovian pair, recording the response identity and the temporal window in which responses cancel the US. A minimal encoding:

```
@cs(label="key_light", duration=6-s, modality="visual")
@us(label="grain", delivery="cancelled_on_cs_response")

phase omission_training:
  sessions = 20
  Pair.ForwardDelay(key_light, grain, isi=6-s, cs_duration=6-s) @omission(response="key_peck", during="cs")
```

The `@omission` annotation parameters:

- `response` — the observable response class whose emission cancels the scheduled US on that trial.
- `during` — the presentation window in which the cancellation rule applies; `"cs"` (during CS presentation, the canonical case) is the default.

An analyzer / executor pass interprets the annotation: whenever a matching response is emitted during the specified window, US delivery is suppressed for that trial. The Pavlovian arrangement itself is unchanged, so the AST composes cleanly with Tier A respondent primitives and other composed-layer annotations.

## 5. Classification within the Taxonomy

Omission's contingency structure is identical to autoshaping except for the response→US-cancellation term. Because that one term changes the programmed arrangement, omission is documented as a named procedure rather than left implicit.

## 6. Citation

- Williams, D. R., & Williams, H. (1969). Auto-maintenance in the pigeon: Sustained pecking despite contingent non-reinforcement. *Journal of the Experimental Analysis of Behavior*, 12(4), 511–520. https://doi.org/10.1901/jeab.1969.12-511
