# procedure-annotator — JEAB Procedure Category

## Status: Restructured (2026-04-12)

## Purpose

`procedure-annotator` is the recommended annotator module for the
**Procedure** category in the JEAB-aligned taxonomy (see
[design-philosophy.md §4.1](../../spec/ja/design-philosophy.md) and
[annotation-design.md §3.6](../../spec/ja/annotation-design.md)).

The name `procedure-annotator` deliberately matches the JEAB Method section's
**Procedure** heading, following the principle of 1:1 correspondence between
annotator names and JEAB Method section headings. This is the convention
established in the 2026-04-12 annotator reorganization; see
[annotation-design.md §3.7](../../spec/ja/annotation-design.md).

## Sub-Annotators

Because the Procedure category has two qualitatively distinct dimensions
(**stimulus identity** and **session-level temporal structure**),
`procedure-annotator` is composed of two sub-annotators rather than a flat
keyword list. Each sub-annotator is a cohesive unit that can be reviewed and
evolved independently, while both share the same JEAB category mapping.

| Sub-annotator | Keywords | Purpose |
|---|---|---|
| [stimulus](stimulus/README.md) | `@reinforcer`, `@sd`, `@brief` | Stimulus identity: reinforcers, discriminative stimuli, second-order brief stimuli |
| [temporal](temporal/README.md) | `@clock`, `@warmup`, `@algorithm` | Session-level temporal parameters: time units, warm-up intervals, algorithmic schedule generation |

## Category Mapping

```
procedure-annotator  →  Procedure  (JEAB Method section heading)
```

Under design-philosophy §4.2 (categories are recommendations, not enforced),
third-party programs may:

- adopt both sub-annotators as-is,
- adopt only one (e.g., stimulus only; ignore temporal),
- redefine the sub-annotator structure,
- or map the same keywords to a different category entirely.

## Boundary

### Belongs in procedure-annotator

Anything that describes **the procedure the subject experiences**:

- Which stimuli are presented and in what role (`@reinforcer`, `@sd`, `@brief`)
- Session-level temporal parameters (`@clock`, `@warmup`)
- Algorithmic parameters for schedule generation (`@algorithm`) — see
  DIVERGENCE A in [annotation-design.md §3.6](../../spec/ja/annotation-design.md)
  for the open question about whether this keyword should eventually move to
  a Measurement sub-role

### Does NOT belong here

- **Physical apparatus**: chambers, operanda, hardware → [apparatus-annotator](../apparatus-annotator/README.md)
- **Subject descriptions**: species, deprivation, history → [subjects-annotator](../subjects-annotator/README.md)
- **Measurement structure**: session termination rules, steady-state criteria,
  dependent variable definitions → `measurement-annotator` (new; see
  [annotation-design.md §3.6](../../spec/ja/annotation-design.md))
- **Clinical metadata** (FBA results, social validity) → [extensions/clinical-annotator](../extensions/)
- **Multi-subject contingencies** → [extensions/social-annotator](../extensions/)

## Composition Example

```
FR5 LH10
  @reinforcer("food", type="unconditioned")   -- stimulus sub-annotator
  @sd("red_light", component=1)               -- stimulus sub-annotator
  @clock(unit="s")                            -- temporal sub-annotator
  @warmup(duration=60)                        -- temporal sub-annotator
  @algorithm("fleshler-hoffman", n=12)        -- temporal sub-annotator
```

All five annotations belong to `procedure-annotator` and therefore to the
**Procedure** category, though they address different dimensions (stimulus
identity vs session timing).

## Dependencies

None. The sub-annotators compose independently.

## Python Implementation Reference

`apps/experiment/contingency-annotator/src/contingency_annotator/procedure_annotator/`

Sub-annotator modules:
- `procedure_annotator/stimulus/`
- `procedure_annotator/temporal/`
