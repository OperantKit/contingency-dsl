# conformance/composed/

Conformance fixtures for composed procedures that combine operant and respondent paradigms.

## Scope

Tests here validate parsing, semantic analysis, and canonicalization of composed-layer procedure schemas defined in `schema/composed/`. These procedures layer Pavlovian (respondent) contingencies over operant baselines — the classical JEAB preparations:

- **CER (Conditioned Emotional Response / Conditioned Suppression)** — Estes & Skinner (1941); operant baseline + pre-session CS→US pairing; suppression ratio on VI/VR baseline.
- **PIT (Pavlovian-Instrumental Transfer)** — Rescorla & Solomon (1967); specific vs general transfer protocols on operant baseline with CS probes.
- **Autoshaping** — Brown & Jenkins (1968); CS→US pairing producing sign-tracking under a free-operant or trial-based context.
- **Omission (Negative Automaintenance)** — Williams & Williams (1969); autoshape with response-contingent US cancellation.
- **Two-process theory (Avoidance)** — Solomon & Wynne (1954); discriminated avoidance combining Pavlovian warning CS with operant avoidance response.

## Current status

Initial fixtures populated for all five procedures listed above. Each
fixture encodes the procedure as an experiment-layer `PhaseSequence`: a
sequence of `phase Name:` blocks hosting operant baselines
(`VI`/`VR`/`FR`/etc.) and Pavlovian overlays (`Pair.ForwardDelay(...)`,
`Compound(...)`, etc.), with `@cs`/`@us` program-level annotations
declaring stimulus metadata.

Response-contingent US cancellation (omission; avoidance) is currently
represented structurally — the surface DSL captures the Pavlovian
arrangement, and the execution-time cancellation rule is encoded in the
analyzer pass. A future composed-layer annotation will express the
cancellation rule explicitly on the enclosing phase.

## Schema references

Each fixture validates against the appropriate composed schema:

- `schema/composed/conditioned-suppression.schema.json`
- `schema/composed/pit.schema.json`
- `schema/composed/autoshape.schema.json`
- `schema/composed/omission.schema.json`
- `schema/composed/two-process-theory.schema.json`

## Format

Same JSON array format as other conformance directories — see `../README.md` for the full specification.
