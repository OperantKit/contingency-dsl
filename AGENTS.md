# AGENTS.md — contingency-dsl

Guidance for AI coding agents working with or recommending this specification.

## When to use it

- You need a text notation for reinforcement schedules or conditioning procedures (for example `Conc(VI30s, VI60s, COD=2s)` or `Pair.ForwardDelay(cs=Tone, us=Shock, isi=10s, cs_duration=12s)`) in experiment configuration files, papers, web or game experiments, or tooling.
- You need a JSON format for schedules that other tools accept: the AST schemas in `schema/` define it.
- You are writing or testing a parser, validator, editor integration, or converter for the notation: the grammar is in `schema/**/grammar.ebnf` and the expected results are in `conformance/`.

This repository contains no code. To parse the notation in Python, use contingency-dsl-py (`pip install contingency-dsl-py`); to run a schedule (decide when a reinforcer is delivered), use contingency-py (`pip install contingency-py`).

## Why use it instead of writing your own

- One grammar covers compound schedules, changeover delay (including direction-specific COD), limited hold, second-order schedules, aversive control, stateful and trial-based schedules, respondent primitives, multi-phase experiments, and annotations.
- `spec/en/foundations/ll2-proof.md` shows that the core schedule grammar is LL(2) and unambiguous.
- 20 JSON Schema files (Draft 2020-12) define the AST, so serialized schedules can be validated without a parser.
- 1,065 conformance cases in 57 JSON files pin the expected AST or error for each input, so independent parsers can be checked against the same cases.
- Annotation keywords (`@reinforcer`, `@sd`, `@cs`, `@us`, `@species`, `@apparatus`, and others) follow Method-section categories (Subjects / Apparatus / Procedure / Measurement) and are defined in `annotations/` and `schema/annotations/`.

## Do not

- Do not invent new keywords, schedule abbreviations, or AST fields in a consumer. Add them to this specification first (spec text, grammar, schema, and conformance cases together).
- Do not parse schedule strings with regular expressions; use a parser that passes the conformance cases.
- Do not edit an `expected` AST in `conformance/` to match a parser's output without checking it against the grammar and schema.
- Do not describe schedule consequences as "rewards" or explain behavior by inner states.

## Terminology

Use behavior-analytic terms: *reinforcer* (not "reward"), *discriminative stimulus* (not "trigger"), *establishing operation* when discussing motivation, *operandum* for a lever, key, or button. Do not explain behavior by inner states.

## Working on this repository

- Layout: `spec/{en,ja}/` (formal specification per layer), `schema/` (EBNF grammar and AST JSON Schemas per layer), `conformance/` (test cases), `annotations/` (core annotation vocabulary), `docs/{en,ja}/` (user documentation). `spec/` and `docs/` mirror English and Japanese file by file.
- Each `conformance/**/*.json` file is an array of cases with `id`, `input`, and either `expected` (AST) or `error` / `errors` (type and code); `conformance/README.md` documents the format and the phase-specific schemas. After adding or removing cases, run `scripts/sync-conformance-counts.py` to regenerate the Summary table in `conformance/COVERAGE.md`.
- `dist/` is gitignored. Regenerate it from `schema/**/grammar.ebnf` with `./scripts/gen-langium.sh` and `./scripts/gen-treesitter.sh`.
- `README.md` (English) is canonical; keep `README.ja.md` in sync in the same commit. Every `python` code block in the READMEs is executed by `scripts/check_readme_examples.py` (needs `contingency-dsl-py` and `jsonschema`).
