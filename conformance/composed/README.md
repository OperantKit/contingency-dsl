# conformance/composed/

Conformance fixtures for composed procedures that combine operant and respondent paradigms.

## Scope

Tests here validate parsing, semantic analysis, and canonicalization of composed-layer procedures. These procedures layer Pavlovian (respondent) contingencies over operant baselines — the classical JEAB preparations:

- **CER (Conditioned Emotional Response / Conditioned Suppression)** — Estes & Skinner (1941); operant baseline + pre-session CS→US pairing; suppression ratio on VI/VR baseline.
- **PIT (Pavlovian-Instrumental Transfer)** — Rescorla & Solomon (1967); specific vs general transfer protocols on operant baseline with CS probes.
- **Autoshaping** — Brown & Jenkins (1968); CS→US pairing producing sign-tracking under a free-operant or trial-based context.
- **Omission (Negative Automaintenance)** — Williams & Williams (1969); autoshape with response-contingent US cancellation expressed via `@omission`.
- **Two-process theory (Avoidance)** — Solomon & Wynne (1954); discriminated avoidance combining Pavlovian warning CS with operant avoidance response, expressed via `@avoidance`.

## Current status

Initial fixtures populated for all five procedures listed above. Each
fixture encodes the procedure as an experiment-layer `PhaseSequence`: a
sequence of `phase Name:` blocks hosting operant baselines
(`VI`/`VR`/`FR`/etc.) and Pavlovian overlays (`Pair.ForwardDelay(...)`,
`Compound(...)`, etc.), with `@cs`/`@us` program-level annotations
declaring stimulus metadata.

Response-contingent US modulation (omission; avoidance) is expressed
declaratively via the composed-layer annotations `@omission(response, during)`
and `@avoidance(response, mode)` attached to the underlying Pavlovian
primitive. The analyzer / executor pass interprets the annotation: when
the named response is emitted within the specified window, US delivery
is suppressed (omission) or postponed/cancelled (avoidance) for that
trial. The Pavlovian arrangement itself is not modified, so the AST
composes cleanly with Tier A respondent primitives.

## Schema references

Composed procedures do not have dedicated per-procedure AST schemas;
they reuse the experiment-layer and annotation schemas:

- `schema/experiment/phase-sequence.schema.json` — the `PhaseSequence` /
  `Phase` AST shape that hosts each composed procedure.
- `schema/operant/ast.schema.json` — operant baselines that appear inside
  phase bodies.
- `schema/respondent/ast.schema.json` — Pavlovian primitives that appear
  inside phase bodies.
- `schema/annotations/extensions/respondent-annotator.schema.json` —
  `@cs`, `@us`, `@iti`, `@cs_interval` declarations.
- `schema/annotations/extensions/composed-annotator.schema.json` —
  `@omission` and `@avoidance` annotations expressing response-contingent
  US-modulation rules.

## Format

Same JSON array format as other conformance directories — see `../README.md` for the full specification.
