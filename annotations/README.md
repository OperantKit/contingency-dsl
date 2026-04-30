# Annotations — Core Recommended Vocabulary

This directory defines the **core recommended vocabulary of annotations**
that the DSL project maintains. Annotations are `@`-prefixed keywords
that attach metadata to schedule expressions without changing the base
grammar (see
[`spec/en/design-philosophy.md §4`](../spec/en/design-philosophy.md)).

## Status

These annotators are **core to the DSL**, not third-party examples.
The DSL project supplies and maintains the reference implementation in:

- [`contingency-dsl-py/`](../../contingency-dsl-py/) — Python (sole reference implementation)

Per [`design-philosophy.md §4.2`](../spec/en/design-philosophy.md),
third-party programs retain the right to reinterpret, extend, or replace
any annotator without requiring grammar changes. The guarantee is
architectural, not a statement that these annotators are optional.

## Catalog

| Annotator | Keywords | Purpose |
|---|---|---|
| [stimulus-annotator](stimulus-annotator/) | `@reinforcer`, `@sd`, `@operandum`, `@brief` | Identity of stimuli that participate in a contingency |
| [temporal-annotator](temporal-annotator/) | `@iti`, `@session_duration`, … | Temporal boundaries and intervals |
| [subjects-annotator](subjects-annotator/) | `@subject`, `@body_weight`, … | Subject characteristics and establishing operations |
| [apparatus-annotator](apparatus-annotator/) | `@chamber`, `@feeder`, … | Physical apparatus binding (I/O delegated to `experiment-io`) |
| [composed-annotator](composed-annotator/) | `@omission`, `@avoidance`, … | Markers for composed operant × respondent procedures |
| [measurement-annotator](measurement-annotator/) | `@iri_window`, `@response_class`, … | How dependent measures are quantified |

Each annotator's directory contains its keyword list, categorical status,
and boundary tests. See individual READMEs for details.

## Adding new keywords

Keywords are added to an existing annotator when they fit its category.
New annotator categories require a design review (see
[`spec/en/design-philosophy.md §4`](../spec/en/design-philosophy.md) for
admission criteria).

Third-party programs that need categories outside the recommended set
should document them in their own packages rather than modifying this
directory.
