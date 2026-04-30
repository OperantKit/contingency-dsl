# apparatus-annotator — Apparatus & Hardware Declaration

## Purpose

Declares the **physical experimental apparatus** that realises a
contingency program: the chamber model, the hardware interface protocol,
and (where the program names a physical backend) the hardware identity
itself.

Corresponds to the JEAB Method/Apparatus subsection — the part of a
report that tells a reader *what equipment* the procedure ran on (e.g.,
"Sessions were conducted in a Med Associates ENV-007 chamber connected
via MED-PC"). The declarations are program-level intent: they identify
which apparatus the program targets, while the runtime backend that
actually drives the hardware is the responsibility of `experiment-io`.

This annotator is part of the **core recommended vocabulary** maintained
by the DSL project. Per
[design-philosophy.md §4.2](../../spec/en/design-philosophy.md), third-party
programs retain the freedom to reinterpret or replace these categories, but
the DSL project supplies and maintains the reference implementation in
[`contingency-dsl-py`](../../../contingency-dsl-py/) (sole reference implementation).

---

## Status

`Design`

---

## Category

- [x] **Setup** / **Apparatus** — JEAB Method/Apparatus declarations

---

## Keywords

| Keyword | Purpose | Example |
|---|---|---|
| `@chamber` | Chamber model identification | `@chamber("med-associates", model="ENV-007")` |
| `@interface` | Hardware interface specification | `@interface("serial", port="/dev/ttyUSB0")` |
| `@hardware` (alias `@hw`) | Physical hardware backend; presence implies physical apparatus, omission implies virtual/simulation mode | `@hardware("med-associates")` |

## Scope and attachment

All three keywords above are **program-level**: they appear in the
program preamble and surface in the AST under `program_annotations`.
They modify the surrounding program rather than any single schedule node
and do not attach postfix to a schedule expression.

## Validation rules

Sourced from [`apparatus.schema.json`](../../schema/annotations/apparatus.schema.json):

1. **`@chamber` requires a positional string.** Optional `model`
   parameter is a string identifying the chamber model.
2. **`@interface` requires a positional string** (the protocol or
   interface name). Optional `port` parameter is a string device-port
   path.
3. **`@hardware` requires a positional string** naming the backend.
   The keyword has no other parameters; `@hw` is an accepted alias and
   the canonical keyword surfaces as `hardware` in the AST with the
   source label preserved.
4. **All three keywords are program-level only.** They are rejected on
   any schedule-level attachment.

## Cross-references

- The runtime that binds these declared identities to a concrete driver
  (serial, MED-PC bridge, virtual loopback, etc.) lives in
  `experiment-io`. This annotator declares *which apparatus*; the
  runtime decides *how to drive it*.
- Stimulus identity (`@reinforcer`, `@sd`, `@brief`) belongs to
  `stimulus-annotator`; subject conditions belong to `subjects-annotator`.

## Future scope

Per [annotations/design.md §3.6.1](../../spec/en/annotations/design.md),
`@operandum` is identified as belonging to the Apparatus category on
JEAB grounds: an operandum is a physical device described in the
Apparatus section, even when the DSL also uses `@operandum(..., component=N)`
to assign that device to a schedule component. The keyword is currently
registered under `stimulus-annotator` and parsed there; the architecture
document records its intended consolidation into this annotator. When
that consolidation lands, `@operandum` will move here together with its
program-level / schedule-level dual semantics described in the schema.

## References

- American Psychological Association. (2020). *Publication manual of the American Psychological Association* (7th ed.). https://doi.org/10.1037/0000165-000

## Reference implementation

[`contingency_dsl.annotations.apparatus`](../../../contingency-dsl-py/src/contingency_dsl/annotations/apparatus/).
