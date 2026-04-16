# Valence — Appetitive vs Aversive

> Part of the contingency-dsl foundations layer (Ψ). Defines the appetitive / aversive axis as an orthogonal property independent of stimulus type.

---

## 1. The Valence Axis

**Definition 1 (Appetitive).** A stimulus whose presentation the subject works to obtain (or whose removal the subject works to avoid). Canonical examples: food, water, sexually receptive conspecifics, social attention (in appetitively motivated subjects).

**Definition 2 (Aversive).** A stimulus whose presentation the subject works to avoid, escape, or terminate (or whose removal the subject works to produce). Canonical examples: electric shock, loud noise, bright light, social attention (in aversively motivated subjects, a contextual judgment).

Valence is a **functional** property of a stimulus relative to a specific subject and state, not a property of the stimulus in isolation. A food pellet is appetitive to a food-deprived rat and may be irrelevant to a satiated one (Catania, 2013, Ch. 3). The DSL records valence at the annotation level where an experimenter has determined it; it does not predict it.

## 2. Orthogonality to Stimulus Type

Valence is orthogonal to the stimulus-type lattice defined in `stimulus-typing.md`. Every stimulus-type slot admits both valences:

| Type | Appetitive example | Aversive example |
|---|---|---|
| US | Food pellet | Shock |
| CS | Tone predicting food | Tone predicting shock |
| SD | Light signaling ratio-for-food | Light signaling avoidance opportunity |
| Sr+ / Sr− / Punisher | Food (Sr+) | Shock (punisher or, by removal, Sr−) |

## 3. The Four Operant Quadrants

The combination of valence and operation (presentation / removal) produces the four operant quadrants (see `stimulus-typing.md §5`):

|  | Presentation | Removal |
|---|---|---|
| **Appetitive** | Positive reinforcement | Negative punishment |
| **Aversive** | Positive punishment | Negative reinforcement |

The quadrant is determined by (a) the stimulus valence and (b) the schedule's consequence operation. The DSL surface grammar makes the *operation* explicit via the combinator or annotation (`Overlay(baseline, punisher)` vs bare `VI 60-s`, or `@reinforcer` vs `@punisher`). The *valence* is specified in the stimulus annotation (`@reinforcer("shock")` explicitly contradicts default conventions and should be linted).

## 4. Aversive Control in the Operant Layer

Two aversive-control primitives are first-class in the operant layer:

- **`Sidman(SSI, RSI)`** — free-operant avoidance (Sidman, 1953); see `operant/schedules/compound.md` or equivalent.
- **`DiscriminatedAvoidance(CSUSInterval, ITI, mode, ...)`** — trial-based avoidance (Solomon & Wynne, 1953).

Additionally, punishment is expressed via the `Overlay` combinator and the `PUNISH(...)` directive on `Conc`. See `operant/grammar.md` for the full set.

## 5. Valence in the Respondent Layer

Respondent primitives (`Pair.*`, `Contingency(...)`, etc.) do not themselves encode valence; the US's valence is recorded through the `@us` annotation. Classical fear conditioning (aversive US) and appetitive conditioning (appetitive US) share identical respondent-layer grammar; they differ only in the annotation attached to the US.

## 6. Why Valence Is Foundational

Valence cross-cuts paradigms:

- Composed procedures like CER (conditioned suppression) require that the CS be aversive at test time (Estes & Skinner, 1941). The CS's valence is not directly manipulated in the operant baseline; it is conferred by the respondent pairing.
- PIT requires that the operant baseline and respondent pairing use compatible valences (appetitive-appetitive for positive PIT; aversive-aversive for fear-potentiated startle variants).

Because valence spans operant, respondent, and composed layers, it belongs at the foundations layer rather than any one paradigm.

## References

- Catania, A. C. (2013). *Learning* (5th ed.). Sloan.
- Estes, W. K., & Skinner, B. F. (1941). Some quantitative properties of anxiety. *Journal of Experimental Psychology*, 29(5), 390–400. https://doi.org/10.1037/h0062283
- Sidman, M. (1953). Two temporal parameters of the maintenance of avoidance behavior by the white rat. *Journal of Comparative and Physiological Psychology*, 46(4), 253–261. https://doi.org/10.1037/h0060730
- Solomon, R. L., & Wynne, L. C. (1953). Traumatic avoidance learning: Acquisition in normal dogs. *Psychological Monographs: General and Applied*, 67(4), 1–19. https://doi.org/10.1037/h0093649
