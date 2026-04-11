# annotations/extensions — Extension Annotators

This directory holds recommended annotators that **do not map to any of the
four JEAB-aligned categories** (Procedure / Subjects / Apparatus /
Measurement).

## What is an "extension" annotator?

The 2026-04-12 annotator reorganization established a 1:1 correspondence
between annotator names and JEAB Method section headings:

- [`procedure-annotator/`](../procedure-annotator/README.md) → **Procedure**
- [`subjects-annotator/`](../subjects-annotator/README.md) → **Subjects**
- [`apparatus-annotator/`](../apparatus-annotator/README.md) → **Apparatus**
- [`measurement-annotator/`](../measurement-annotator/README.md) → **Measurement**

Annotators that describe dimensions outside these four — such as clinical
metadata (FBA results, intervention labels), multi-subject contingencies
(cooperation tasks), or domain-specific extensions (behavioral pharmacology,
neuroscience integration) — are placed here as **extensions**.

## When is an extension annotator appropriate?

A new dimension is an extension (not a new first-class category) when:

1. It is relevant to a **specific research domain or application area**
   rather than EAB in general.
2. Mainstream JEAB papers do not have a dedicated Method section heading
   for it.
3. It can be ignored by programs that do not care about the domain.

If a dimension is so general that mainstream EAB research universally needs
it (e.g., Measurement was added in 2026-04-12 for exactly this reason), it
should become a first-class annotator, not an extension.

## Current extensions

| Extension | Keywords (candidate) | Domain |
|---|---|---|
| `social-annotator` (future) | `@subject`, `@interlocking` | Multi-subject contingencies, cooperation tasks |
| `clinical-annotator` (future) | `@function`, `@target`, `@replacement` | ABA intervention metadata, FBA results |

These are **proposed** but not yet implemented as README files in this
directory. They are referenced in
[spec/annotation-design.md §3](../../spec/annotation-design.md) as
recommendation candidates.

## Relationship to Schedule Extension layer

Extension **annotators** (here) are distinct from the **Schedule Extension
layer** described in
[design-philosophy.md §5](../../spec/ja/design-philosophy.md):

- **Extension annotators** add metadata (they don't change Core DSL evaluation
  semantics). They live in `annotations/extensions/`.
- **Schedule Extension layer** adds new schedule *constructs* (e.g., percentile
  schedules, adjusting schedules). Schedule grammar is extended, not just
  metadata. This is a different layer entirely.

## Third-party extensions

Under design-philosophy §4.2 (program-scoped closure), third-party programs
may define their own extension annotators without any coordination with the
contingency-dsl project. The extensions listed in this directory are simply
the project's **recommended** extension set.
