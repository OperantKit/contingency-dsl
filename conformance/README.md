# contingency-dsl Conformance Test Suite

Language-independent test cases for validating parser and validator implementations.

## Structure

Tests are organized to mirror `schema/`:

```
conformance/
├── foundations/           — Paradigm-neutral lexical tests (placeholder; see foundations/README.md)
├── operant/               — Operant schedule tests (atomic, compound, modifier, binding, etc.)
│   ├── stateful/          — Stateful operant schedules (percentile, adjusting, interlocking)
│   └── trial-based/       — Trial-based operant procedures (MTS matching-to-sample, GoNoGo)
├── respondent/            — Respondent (Pavlovian) primitive tests (Tier A: Pair variants, elementary, contingency controls, compound stimuli)
├── composed/              — Programs using both vocabularies (CER, PIT, two-process)
├── experiment/            — Experiment-layer tests (phase-sequence, criterion, annotation inheritance)
├── equivalence/           — Same-experiment fixtures: one arrangement in two vocabularies, compared by execution
├── annotations/           — Annotation system tests (program-level, measurement, errors)
│   └── extensions/        — Annotator extension tests (respondent-annotator)
└── representations/
    └── t-tau/             — T-tau coordinate transform tests (to/from/roundtrip/errors)
```

## Format

Each JSON file contains an array of test cases:

```json
[
  {
    "id": "unique_test_id",
    "description": "Human-readable description",
    "input": "DSL text to parse",
    "expected": { ... }
  }
]
```

### Success cases

`expected` contains the AST matching `schema/operant/ast.schema.json` (operant-layer schema; the respondent layer has its own `schema/respondent/ast.schema.json`; composed procedures are encoded as `PhaseSequence` AST trees per `schema/experiment/phase-sequence.schema.json`, with composed-layer behavior carried by `@omission` / `@avoidance` annotations defined in `schema/annotations/extensions/composed-annotator.schema.json`).

For phase-specific validation of operant fixtures:
- `pre_expansion` fields validate against `schema/operant/ast-parsed.schema.json` (Phase 1: includes IdentifierRef, RepeatModifier)
- `expected` fields validate against `schema/operant/ast-resolved.schema.json` (Phase 2/3: no IdentifierRef, no RepeatModifier)
- `resolved` fields validate against `schema/operant/ast-resolved.schema.json` (Phase 3: post-LH-propagation)

Execution engines SHOULD validate against `ast-resolved.schema.json` to reject unresolved ASTs.

### Error cases

```json
{
  "id": "error_case_id",
  "input": "invalid input",
  "error": {
    "type": "ParseError | LexError | SemanticError",
    "code": "ERROR_CODE"
  }
}
```

### Multi-error cases

Tests with multiple errors use `errors` (array) instead of `error` (single object):

```json
{
  "id": "multi_error_case_id",
  "input": "input with multiple errors",
  "errors": [
    {"type": "ParseError", "code": "FIRST_ERROR_CODE"},
    {"type": "LexError", "code": "SECOND_ERROR_CODE"}
  ]
}
```

Parsers that implement panic-mode recovery (§3.7 SHOULD) MUST detect all listed errors
in the specified order. Parsers without multi-error recovery MUST detect at least the
first error in the list.

### Semantic analysis cases

Some tests specify both `pre_expansion` (parser output with IdentifierRef nodes)
and `expected` (post-expansion result after semantic analysis). Parsers that do
not perform semantic analysis should validate against `pre_expansion` only.

### LH propagation cases

Tests in `lh_propagation.json` specify both `expected` (post-parse / pre-propagation AST)
and `resolved` (post-LH-default-propagation AST). The `resolved` field shows the AST after
the attribute grammar rules of §1.6.1 have been applied. Implementations that do not perform
LH default propagation should validate against `expected` only.

## Test files

### foundations/

Empty (placeholder). See `foundations/README.md` for the dividing principle and qualifying topics.

### operant/

| File | Scope |
|------|-------|
| `atomic.json` | FR5, VI60s, RR20, EXT, CRF, all 3x3 grid, JEAB notation variants |
| `compound.json` | Conc, Alt, Conj, Chain, Tand, Mult, Mix, Overlay, nested |
| `modifier.json` | DRL, DRH, DRO, PR, Repeat, Lag |
| `limited_hold.json` | FI30 LH10, program-level LH default |
| `second_order.json` | FR5(FI30), VI60(FR10), RR5(FT20s) |
| `binding.json` | let bindings, expansion |
| `aversive.json` | Sidman avoidance, discriminated avoidance |
| `program.json` | Program-level param_decls, bindings |
| `errors.json` | Lex errors, parse errors, semantic errors, multi-error recovery (§3.7) |
| `compound-kw-aliases.json` | Verbose keyword alias parsing (ChangeoverDelay, FixedRatioChangeover, Blackout) |
| `semantic-violations-extended.json` | Cross-combinator keyword validation, verbose alias errors, alias duplicate detection |
| `boundary-values.json` | Zero/edge values for atomic, modifier, LH, Lag, PR, Repeat, compound params |
| `warnings.json` | Linter warnings: MISSING_TIME_UNIT, RSI_EXCEEDS_SSI, LAG_LARGE_N, MISSING_INTERPOLATE_ONSET, MISSING_COD |
| `algebra.json` | Algebraic equivalence (≡) and non-equivalence (≢) pairs: identity, annihilator, commutativity, associativity, Repeat, non-distributivity |
| `lh_propagation.json` | LH default propagation attribute grammar (§1.6.1): R1–R6 rules, SecondOrder unit isolation, aversive isolation, Overlay punisher isolation, explicit override, binding expansion phase ordering |
| `interpolated.json` | Interpolate / Interp alias with count + onset kwargs |
| `reinforcement_delay.json` | RD param_decl and schedule-level RD with time-unit variants |
| `response_cost.json` | ResponseCost(amount) — response-contingent removal of conditioned reinforcer (Weiner, 1962; Kazdin, 1972) |
| `timeout.json` | TO(duration, reset_on_response) — post-reinforcement timeout |

### operant/stateful/

| File | Scope |
|------|-------|
| `percentile.json` | Pctl minimal, all targets, compound, let binding, annotations |
| `adjusting.json` | Adjusting delay / ratio / amount with bounds |
| `interlocking.json` | Interlocking R(t) formula with R0 and T parameters |
| `errors.json` | Stateful semantic errors (Pctl/Adj/Interlock) + linter warnings |

### operant/trial-based/

| File | Scope |
|------|-------|
| `mts.json` | MTS minimal, fully specified, time units, let binding, annotations, kwarg order, compound (Mult/Chain), boundary values, LH |
| `gonogo.json` | GoNoGo trial structure, LH redundancy, SDT-style asymmetric consequence |
| `errors.json` | MTS semantic errors (M1–M11), modifier incompatibility, linter warnings (W1–W5 + W7) |

### respondent/

| File | Scope |
|------|-------|
| `pair.json` | Pair.ForwardDelay / ForwardTrace / Simultaneous / Backward |
| `elementary.json` | Extinction, CSOnly, USOnly, ITI, Compound, Serial, Differential |
| `contingency-controls.json` | Contingency(p_us_given_cs, p_us_given_no_cs), TrulyRandom, ExplicitlyUnpaired |
| `compound-stimulus.json` | Compound and Serial CS lists with mode variants |
| `autoshape.json` | Autoshaping (Brown & Jenkins, 1968): CS→US forward-delay pairing |
| `omission.json` | Omission (Williams & Williams, 1969): pairing with `@omission` |

Tier B respondent primitives (blocking, overshadowing, latent inhibition, renewal, reinstatement, occasion-setting, higher-order conditioning) are out of scope here and live in the companion package `contingency-respondent-dsl`.

### composed/

Three fixtures (CER, PIT, two-process), each using both vocabularies. See `composed/README.md`.

### experiment/

| File | Scope |
|------|-------|
| `phase.json` | Phase declarations (ABA, stability criteria, `use` references, shared annotations) |
| `progressive-training.json` | ProgressiveTraining expansion (single/multi-variable, mixed with phases, parametric, interleave, advance conditions) |
| `shaping.json` | Skinner Shaping (artful / percentile / staged methods; error cases) |
| `errors.json` | Experiment-layer semantic errors (constraints 63–82, including R-4 progressive_advance errors) |

### equivalence/

Two programs are **the same experiment** when the same response sequence yields the same stimulus sequence. Each fixture writes one arrangement in the respondent and the operant vocabularies and gives the stimulus sequence both must produce. Unlike the other directories, these fixtures are checked by **execution**, not by comparing ASTs.

| File | Scope |
|------|-------|
| `autoshaping.json` | Autoshaping (Brown & Jenkins, 1968): `Pair.ForwardDelay` with a fixed ITI / signaled FT `Chain(FT 52-s, FT 8-s) @sd("key_light", component=2)` |
| `superstition-ft.json` | Response-independent food (Skinner, 1948): `USOnly` with a fixed ITI / `FT 15-s` |

Each file is an array with one object (no `id` field, so the AST runners skip it):

```json
[
  {
    "equivalence": "name",
    "description": "...",
    "source": {"procedure": "APA reference", "values": "where the values come from"},
    "programs": {
      "respondent": {"input": "DSL text", "ast": { ... }},
      "operant":    {"input": "DSL text", "ast": { ... }}
    },
    "presentation_s": {"food": 3.0},
    "end": {"stimulus_offsets": {"food": 3}},
    "inputs": [{"name": "...", "responses": [[10.0, "key_peck"]]}],
    "expected": [[52.0, "key_light", "on"], [60.0, "key_light", "off"]]
  }
]
```

- `ast` is the parser's output for `input` (without the `kwargs` mirror of annotation `params`), so a runner that does not parse DSL text can read it directly.
- `presentation_s` is the duration of each presented stimulus that neither program carries (a property of the apparatus). Both runners use the same value.
- `end` stops the session after the given number of offsets of each named stimulus.
- `expected` is a list of `[time_s, stimulus, "on" | "off"]`, sorted by time; at the same time, offsets come before onsets, then by stimulus name.

Timing rules the expected sequences follow:

- The session starts with the interval before the first trial (the ITI, or the first link of the chain).
- In the respondent program, the ITI runs from the offset of the last stimulus of a trial to the next trial start.
- In the operant program, the schedule clock stops while the reinforcer is presented and restarts at its offset.
- Values are fixed (no `VT`, no variable ITI), so every run gives one sequence.

How to run: each theory's runner executes **only its own vocabulary's program** with each `inputs[].responses` and compares the result with `expected`. No test package imports both runners; the expected sequence stands between them. The respondent program is run by respondent-sim (`tests/test_equivalence.py`). A fixture is added only when both vocabularies can write the arrangement with fixed values.

### annotations/

| File | Scope |
|------|-------|
| `program-level.json` | Program-level annotations (subjects, apparatus, session) |
| `procedure-stimulus.json` | @reinforcer, @punisher/@consequentStimulus aliases, @sd, @brief, @stimulus_classes, @training, @testing |
| `procedure-temporal.json` | @clock, @warmup, @algorithm (Fleshler-Hoffman, arithmetic) |
| `procedure-trial-structure.json` | Trial-structure annotations (correction, correction-latency) |
| `subjects.json` | @species, @strain, @deprivation, @history, @n |
| `apparatus.json` | @chamber, @operandum (dual scope), @interface, @hardware/@hw alias |
| `measurement.json` | @session_end, @baseline, @steady_state, @dependent_measure, @training_volume, @microstructure, @phase_end, @logging, @iri_window, @warmup_exclude |
| `errors.json` | Annotation parameter validation errors (measurement + stimulus + temporal + subjects + apparatus) |

### annotations/extensions/

| File | Scope |
|------|-------|
| `respondent-annotator.json` | @cs, @us, @iti, @cs_interval — respondent stimulus and timing metadata extension (paired with `schema/annotations/extensions/respondent-annotator.schema.json`) |

### representations/t-tau/

| File | Scope |
|------|-------|
| `to_ttau.json` | Lattice → T-tau conversion |
| `from_ttau.json` | T-tau → Lattice conversion |
| `roundtrip.json` | Bidirectional identity verification |
| `errors.json` | Type errors, domain violations |
