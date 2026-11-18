# conformance/composed/

Conformance fixtures for the composed layer: programs that use both the operant and the respondent vocabulary in one phase sequence, and the composed-annotator annotations (`@omission`, `@avoidance`).

## Scope

Tests here validate parsing, semantic analysis, and canonicalization. The composed layer is not a category of procedures; a procedure that can be written in one vocabulary belongs to that vocabulary's layer.

Programs that use both vocabularies in one phase sequence:

- **CER (Conditioned Emotional Response / Conditioned Suppression)** — Estes & Skinner (1941); operant baseline phase and a CS→US pairing phase; suppression ratio on VI/VR baseline.
- **PIT (Pavlovian-Instrumental Transfer)** — Rescorla & Solomon (1967); instrumental training phase, Pavlovian training phase, and a transfer test phase.
- **Two-process theory (Avoidance)** — Solomon & Wynne (1954); operant warm-up phase and a warning CS→US pairing with response-contingent US cancellation expressed via `@avoidance`.

Fixtures written with respondent primitives only (no operant schedule in the program):

- **Autoshaping** — Brown & Jenkins (1968); CS→US forward-delay pairing.
- **Omission (Negative Automaintenance)** — Williams & Williams (1969); CS→US pairing with response-contingent US cancellation expressed via `@omission`.

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
