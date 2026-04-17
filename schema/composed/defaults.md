# contingency-dsl — Composed Defaults

Explicit documentation of the composed layer's structural conventions
and defaults. Composed procedures combine an operant constituent
(`schema/operant/ast.schema.json`) with a respondent constituent
(`schema/respondent/ast.schema.json`) and are distinct from either
paradigm taken alone.

## Composition principle

Every composed schema in this directory `$ref`s both the operant and
respondent AST schemas for its constituent fields:

- Operant baseline or schedule → `../operant/ast.schema.json#/$defs/ScheduleExpr`
- Respondent pairing / extinction / CS-only → `../respondent/ast.schema.json#/$defs/RespondentExpr`
- Stimulus references → `../respondent/ast.schema.json#/$defs/StimulusRef`
- Durations → `../respondent/ast.schema.json#/$defs/Duration`

A program that loads a composed-layer schema therefore loads (transitively)
both paradigm schemas. This `$ref` pattern preserves a single source of
truth for each paradigm's vocabulary.

## Files

| File | Procedure | Primary reference |
|---|---|---|
| `conditioned-suppression.schema.json` | CER / conditioned suppression | Estes & Skinner (1941); Annau & Kamin (1961) |
| `pit.schema.json` | Pavlovian-to-Instrumental Transfer | Estes (1948); Rescorla & Solomon (1967); Lovibond (1983) |
| `autoshape.schema.json` | Autoshaping / sign-tracking | Brown & Jenkins (1968) |
| `omission.schema.json` | Omission / negative automaintenance | Williams & Williams (1969) |
| `two-process-theory.schema.json` | Theoretical meta-tag (not a procedure) | Rescorla & Solomon (1967) |

The first four files each define a single `<Procedure>` `$def` node
carrying the composed procedure's structure. `two-process-theory.schema.json`
is a meta-schema: it defines only a theoretical tag (`TwoProcessTheoryTag`)
with optional advisory fields. Two-process theory is the unifying
*account* that makes the other four procedures coherent; it is not
itself a contingency structure, so the companion schema is deliberately
thin.

## Discriminator values

| File | `type` const |
|---|---|
| `conditioned-suppression.schema.json` | `"ConditionedSuppression"` |
| `pit.schema.json` | `"PIT"` |
| `autoshape.schema.json` | `"Autoshape"` |
| `omission.schema.json` | `"Omission"` |
| `two-process-theory.schema.json` | `"TwoProcessTheoryTag"` |

Implementations MAY union these into a composed-layer oneOf
discriminator at the program level; the layer itself does not impose a
union because phases typically host exactly one composed procedure.

## PIT mode field

The `mode` field on the PIT procedure carries the general-versus-outcome-
specific distinction (`"general"` | `"outcome_specific"`). No schema-level
constraint enforces that `outcome_specific` PIT uses the same US label
across Pavlovian and instrumental phases; that consistency check is a
Phase 2 program-level concern (general PIT deliberately uses
motivationally-matched but label-distinct USs across phases).

## Autoshaping topography

The `topography` field on the autoshape procedure is advisory. Its
default (`"observed"`) means the program does not commit ex ante to a
sign-tracking-versus-goal-tracking prediction; measurement annotations
record the emergent topography.

## Omission cancellation scope

The `cancellation_rule` on the omission procedure fixes
`cancel_us_on_response = true` and defaults `scope = "current_trial"`.
Williams and Williams (1969) cancelled the US only for the trial on
which the response occurred; subsequent trials proceeded normally. The
DSL admits only this scope value at present; future variants
(e.g., "next_trial", "session") would require a grammar extension.

## Composed procedures and the experiment layer

Composed procedures typically appear inside a `Phase` or
`PhaseSequence` node from the experiment layer
(`schema/experiment/phase-sequence.schema.json`). The composition is
expressed as follows:

- Single-phase composed procedures (CER, autoshape, omission): one
  `Phase` hosts the procedure; the `Phase`'s `operant` and `respondent`
  fields are populated from the composed procedure's constituents.
- Multi-phase composed procedures (PIT): one `PhaseSequence` with three
  `Phase` nodes, one per composed phase (`pavlovian_training`,
  `instrumental_training`, `transfer_test`).

Schema validation at the experiment layer proceeds separately from
composed-layer validation; `schema/experiment/*.schema.json` checks the
structural shape of phases and sequences, while the composed-layer
schemas check the contingency structure of any composed procedure
embedded in a phase.

## References

- Annau, Z., & Kamin, L. J. (1961). The conditioned emotional response
  as a function of intensity of the US. *Journal of Comparative and
  Physiological Psychology*, 54(4), 428-432.
  https://doi.org/10.1037/h0042199
- Brown, P. L., & Jenkins, H. M. (1968). Auto-shaping of the pigeon's
  key-peck. *Journal of the Experimental Analysis of Behavior*, 11(1),
  1-8. https://doi.org/10.1901/jeab.1968.11-1
- Estes, W. K. (1948). Discriminative conditioning. II. Effects of a
  Pavlovian conditioned stimulus upon a subsequently established
  operant response. *Journal of Experimental Psychology*, 38(2),
  173-177. https://doi.org/10.1037/h0057525
- Estes, W. K., & Skinner, B. F. (1941). Some quantitative properties of
  anxiety. *Journal of Experimental Psychology*, 29(5), 390-400.
  https://doi.org/10.1037/h0062283
- Lovibond, P. F. (1983). Facilitation of instrumental behavior by a
  Pavlovian appetitive conditioned stimulus. *Journal of Experimental
  Psychology: Animal Behavior Processes*, 9(3), 225-247.
  https://doi.org/10.1037/0097-7403.9.3.225
- Rescorla, R. A., & Solomon, R. L. (1967). Two-process learning theory:
  Relationships between Pavlovian conditioning and instrumental
  learning. *Psychological Review*, 74(3), 151-182.
  https://doi.org/10.1037/h0024475
- Williams, D. R., & Williams, H. (1969). Auto-maintenance in the
  pigeon: Sustained pecking despite contingent non-reinforcement.
  *Journal of the Experimental Analysis of Behavior*, 12(4), 511-520.
  https://doi.org/10.1901/jeab.1969.12-511
