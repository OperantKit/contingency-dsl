# conformance/respondent/

Conformance fixtures for the respondent (Pavlovian / classical-conditioning) paradigm layer.

## Scope

Tests here validate parsing and semantic analysis of respondent primitives defined in `schema/respondent/grammar.ebnf` and `schema/respondent/ast.schema.json`. The respondent layer covers Tier A primitives:

- `Pair.ForwardDelay(cs, us, ...)`, `Pair.ForwardTrace(...)`, `Pair.Simultaneous(...)`, `Pair.Backward(...)`
- `Extinction(cs)` — respondent extinction
- `CSOnly(cs)`, `USOnly(us)` — control primitives
- `Compound(cs_set, us)`, `Serial(cs_a, cs_b, us)`, `Differential(cs_plus, cs_minus, us)`
- `ITI(distribution, mean)` — intertrial-interval declaration

## Current status

Tier A primitive fixtures are populated:

| File | Scope |
|------|-------|
| `pair.json` | Pair.ForwardDelay / ForwardTrace / Simultaneous / Backward |
| `elementary.json` | Extinction, CSOnly, USOnly, ITI, Compound, Serial, Differential |
| `contingency-controls.json` | Contingency(p_us_given_cs, p_us_given_no_cs), TrulyRandom, ExplicitlyUnpaired |
| `compound-stimulus.json` | Compound and Serial CS lists with mode variants |

(Case counts intentionally omitted — see the fixture file for the current count, or run `jq length <file>.json`.)

## Extension point

The respondent layer is extensible: Tier B primitives (conditioned inhibition, occasion-setting, higher-order conditioning, sensory preconditioning, latent inhibition, overshadowing, blocking, etc.) register into the extension registry defined in `schema/respondent/`. Conformance fixtures for Tier B primitives belong here under a subdirectory (planned: `conformance/respondent/extensions/`).

## Cross-paradigm composed procedures

Procedures that layer respondent over operant (CER, PIT, autoshaping, omission, two-process theory) are tested in `../composed/`, not here. This directory covers **respondent-only** programs.

## Format

Same JSON array format as other conformance directories — see `../README.md` for the full specification.
