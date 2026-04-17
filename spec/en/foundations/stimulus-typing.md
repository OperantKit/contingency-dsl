# Stimulus Typing — SD, SΔ, CS, US, Sr+, Sr−, Punisher

> Part of the contingency-dsl foundations layer. Fixes the canonical stimulus-type lattice used across operant, respondent, and composed layers. Paradigm layers reuse these types; they are not re-introduced per layer.

---

## 1. The Stimulus Type Lattice

The DSL distinguishes stimulus types by the **role** they play in a contingency, not by physical modality (light, tone, shock, food). Physical modality is an annotation-level property (`@reinforcer`, `@sd`, `@cs`, `@punisher`).

| Type | Symbol | Role | Paradigm | Canonical reference |
|---|---|---|---|---|
| Discriminative stimulus | SD, `S^D` | Signals when a response will be reinforced | Operant | Skinner (1938) |
| S-delta | SΔ, `S^Δ` | Signals when the same response will not be reinforced | Operant | Skinner (1938) |
| Conditioned stimulus | CS | Signal paired with US in respondent procedures | Respondent | Pavlov (1927) |
| Unconditioned stimulus | US | Biologically significant stimulus that elicits a UR | Respondent | Pavlov (1927) |
| Positive reinforcer | Sr+ | Consequence whose presentation increases R | Operant | Skinner (1953) |
| Negative reinforcer | Sr− | Consequence whose removal increases R | Operant | Sidman (1953) |
| Punisher | — | Consequence whose presentation decreases R | Operant | Azrin & Holz (1966) |

## 2. Orthogonal Dimensions

Stimulus type is orthogonal to two other dimensions:

- **Valence** — appetitive vs aversive; see `valence.md`.
- **Modality** — auditory, visual, tactile, gustatory, olfactory; annotation-level (`@cs`, `@reinforcer` parameters).

A given physical stimulus can play different roles across procedures (e.g., a tone that is a CS in a respondent pairing can later serve as an SD in a discriminated operant procedure). The DSL records the role; re-use across procedures is accomplished through `let` bindings of annotation-level stimulus identifiers.

## 3. SD / SΔ in the Operant Layer

In the operant layer, SD and SΔ are **annotation-level** labels attached via `@sd` and `@s_delta` to operant schedule expressions. They do not appear in the CFG as primitive constructors; the three-term contingency `(SD, R, SR)` is materialized by the pair (schedule expression, `@sd` annotation).

Example:

```
Mult(VI 30-s @sd("tone"), EXT @s_delta("light"))
```

The operant layer's `procedure-annotator/stimulus` module (`@sd`, `@s_delta`, `@reinforcer`) provides the full stimulus-typing apparatus for three-term contingencies.

## 4. CS / US in the Respondent Layer

In the respondent layer, CS and US are **primitive-level** constructor arguments: `Pair.ForwardDelay(cs, us, isi, cs_duration)`, `Contingency(p_us_given_cs, p_us_given_no_cs)`, etc. Their physical attributes are attached via `@cs` and `@us` annotations (provided by `annotations/extensions/respondent-annotator`).

Example:

```
Pair.ForwardDelay(tone, shock, isi=5-s, cs_duration=10-s)
  @cs("tone", frequency=4000, modality="auditory")
  @us("shock", intensity="0.5mA", modality="electrical")
```

## 5. Reinforcer and Punisher Quadrants

The combination of valence (appetitive/aversive) and operation (presentation/removal) yields four operant quadrants:

|  | Presentation | Removal |
|---|---|---|
| **Appetitive** | Positive reinforcement (Sr+) | Negative punishment |
| **Aversive** | Positive punishment | Negative reinforcement (Sr−) |

These quadrants are annotation-level (resolved via `@reinforcer` and `@punisher` with valence/operation parameters), not grammatical. The DSL does not enforce quadrant consistency at parse time; linters may warn on evident inconsistencies (e.g., `@reinforcer("shock")` without explicit valence declaration).

## 6. What This File Does **Not** Cover

- Physical modality parameters (frequency, intensity, duration). Those are annotation-level.
- Unconditioned responses (UR), conditioned responses (CR), operant responses (R) as **response-side** typing. The response-side taxonomy is treated in `operant/theory.md` and `respondent/theory.md`.
- Derived stimulus classes (equivalence classes, relational frames). Those are behavioral outcomes, not stimulus types.

## References

- Azrin, N. H., & Holz, W. C. (1966). Punishment. In W. K. Honig (Ed.), *Operant behavior: Areas of research and application* (pp. 380–447). Appleton-Century-Crofts.
- Catania, A. C. (2013). *Learning* (5th ed.). Sloan.
- Pavlov, I. P. (1927). *Conditioned reflexes: An investigation of the physiological activity of the cerebral cortex* (G. V. Anrep, Trans.). Oxford University Press.
- Sidman, M. (1953). Two temporal parameters of the maintenance of avoidance behavior by the white rat. *Journal of Comparative and Physiological Psychology*, 46(4), 253–261. https://doi.org/10.1037/h0060730
- Skinner, B. F. (1938). *The behavior of organisms*. Appleton-Century.
- Skinner, B. F. (1953). *Science and human behavior*. Macmillan.
