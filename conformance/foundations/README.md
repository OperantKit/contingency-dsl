# conformance/foundations/

Paradigm-neutral lexical and structural conformance fixtures.

## Scope

Tests here validate behavior that is defined entirely by `schema/foundations/grammar.ebnf` — the shared, paradigm-neutral formal skeleton — and must pass regardless of which paradigm layer (`operant/`, `respondent/`, `composed/`) is active. The dividing principle is strict: **a fixture belongs here only if it can be parsed and validated against the foundations grammar alone**, without any operant, respondent, or composed productions.

Qualifying topics (future additions welcome):

- Identifier tokenization (`ident`, `upper_ident` regular sets, reserved-keyword disjointness)
- Numeric literal and time-unit parsing (`value`, `number`, `time_unit`, `time_sep`)
- String-literal format (`string_literal`)
- Comment handling (`--` line comments)
- Program envelope (`program ::= program_annotation* param_decl* binding* expr`)
- Annotation surface form (`annotation`, `annotation_args`, positional vs keyword-only)

## Non-scope

Fixtures whose inputs mention any operant schedule token (e.g. `FR`, `VI`, `Conc`, `DRL`, `LH`) belong in `../operant/`. Fixtures whose inputs mention respondent primitives (e.g. `Pair.ForwardDelay`, `CSOnly`) belong in `../respondent/`. Cross-paradigm composed procedures belong in `../composed/`.

## Current contents

Empty. Existing tests were judged to be operant-specific because their inputs embed operant schedule keywords even when the test intent is lexical. As foundations-only fixtures are added, they should use paradigm-neutral inputs (e.g. bare `let` bindings, bare annotation forms with no schedule body — if/when the grammar permits).

## Format

Same JSON array format as other conformance directories — see `../README.md` for the full specification.
