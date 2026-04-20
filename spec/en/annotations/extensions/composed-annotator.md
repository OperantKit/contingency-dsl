# composed-annotator

> Annotation extension for the composed layer. Defines `@omission` and
> `@avoidance` — the two response-contingent US-modulation rules that
> distinguish CER, PIT, autoshaping, omission, and two-process-theory
> preparations from a pure Pavlovian arrangement.

**Category.** Procedure (response-contingent US rules).

**Companion documents.**
- [respondent-annotator](respondent-annotator.md) — the `@cs` / `@us` /
  `@iti` / `@cs_interval` metadata on which composed procedures build.
- [composed/omission.md](../../composed/omission.md) — negative
  automaintenance, the canonical use-case for `@omission`.
- [composed/two-process-theory.md](../../composed/two-process-theory.md)
  — the theoretical frame for `@avoidance`.

---

## 1. Design

Composed procedures in the contingency-dsl are expressed by hosting a
Pavlovian primitive (`Pair.ForwardDelay`, typically) inside an
experiment-layer phase block. The structural arrangement is already
complete at that level: CS, US, ISI, trial count, phase criterion, and
shared `@cs` / `@us` metadata all surface on the Tier A / experiment-layer
AST.

What remains — and what `composed-annotator` supplies — is the
**execution-time modulation rule**: a recorded response of a named class
alters the scheduled US on that trial. The omission procedure cancels
the US; the avoidance procedure cancels or postpones it. Both rules are
declarative: they name the response and the window, and an analyzer /
executor pass interprets the rule.

---

## 2. `@omission(response, during?)`

### Operational definition

Emission of `response` during the `during` window cancels the scheduled
US on that trial. The Pavlovian pairing otherwise proceeds as programmed:
the CS turns on, the CS offsets at its scheduled offset, and (if no
response is emitted in the window) the US is delivered.

### Parameters

- `response` *(string, required)* — observable response class whose
  emission cancels the US. Typically matches a key-peck or lever-press
  operandum identifier declared via `@operandum`.
- `during` *(string, optional, default `"cs"`, one of `{"cs", "iti", "trial"}`)* —
  temporal window in which the cancellation rule applies.

### Example

```
@cs(label="key_light", duration=6s, modality="visual")
@us(label="grain", delivery="cancelled_on_cs_response")

phase omission_training:
  sessions = 20
  Pair.ForwardDelay(key_light, grain, isi=6s, cs_duration=6s) @omission(response="key_peck", during="cs")
```

### Citation

Williams, D. R., & Williams, H. (1969). Auto-maintenance in the pigeon:
Sustained pecking despite contingent non-reinforcement. *Journal of the
Experimental Analysis of Behavior*, 12(4), 511–520.
https://doi.org/10.1901/jeab.1969.12-511

---

## 3. `@avoidance(response, mode?)`

### Operational definition

Emission of `response` during the CS either cancels the US for that
trial (`mode="cancel"`, the default) or postpones CS offset / US onset
(`mode="postpone"`).

### Parameters

- `response` *(string, required)* — observable response class that
  prevents the US.
- `mode` *(string, optional, default `"cancel"`, one of `{"cancel", "postpone"}`)* —
  avoidance modality.

### Example

```
@cs(label="tone", duration=5s, modality="auditory")
@us(label="shock", intensity="0.8mA")

phase avoidance_training:
  sessions = 20
  Pair.ForwardDelay(tone, shock, isi=5s, cs_duration=5s) @avoidance(response="lever_press", mode="cancel")
```

### Citation

Solomon, R. L., & Wynne, L. C. (1954). Traumatic avoidance learning:
The principles of anxiety conservation and partial irreversibility.
*Psychological Review*, 61(6), 353–385.
https://doi.org/10.1037/h0054540

---

## 4. Composition rules

Both keywords attach at schedule level (postfix on a respondent
primitive) and are parsed into the `AnnotatedSchedule` node enclosing
the primitive. At most one of `@omission` / `@avoidance` may be attached
to a single respondent primitive: their execution semantics conflict
(cancel vs. cancel-or-postpone). Programs that need both simultaneously
must decompose them into separate phases.

---

## 5. Reference implementation

The Python reference implementation lives in the
`contingency_dsl.annotations.composed` package as the `ComposedExtension`
class. It conforms to the `ExtensionModule` protocol defined in
`contingency_dsl.extensions`, supplies semantic validation for each
annotation's required / enumerated parameters, and provides an
`extract()` classmethod that walks a `PhaseSequence` or `Program` AST
and returns typed `OmissionAnnotation` / `AvoidanceAnnotation`
instances for downstream consumers.
