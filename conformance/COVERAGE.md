# Conformance Test Coverage Mapping

Maps grammar productions, semantic rules, and error codes to conformance test files.

## Grammar Production Coverage

| # | Production | Test File(s) | Status |
|---|---|---|---|
| 1 | `program` | `core/program.json` | ✅ |
| 2 | `program_annotation` | `annotations/program-level.json` | ✅ |
| 3 | `param_decl` | `core/program.json`, `core/limited_hold.json`, `core/reinforcement_delay.json` | ✅ |
| 4 | `param_name` | `core/program.json`, `core/compound-kw-aliases.json`, `core/reinforcement_delay.json` | ✅ |
| 5 | `binding` | `core/binding.json` | ✅ |
| 6 | `schedule` | (ubiquitous across all test files) | ✅ |
| 7 | `base_schedule` | (tested transitively via atomic, compound, modifier, ident, paren) | ✅ |
| 8 | `atomic_or_second` | `core/atomic.json`, `core/second_order.json` | ✅ |
| 9 | `parametric_atomic` | `core/atomic.json` (24 cases, all 3×3 grid) | ✅ |
| 10 | `simple_schedule` | `core/second_order.json` | ✅ |
| 11 | `dist` | `core/atomic.json` | ✅ F, V, R |
| 12 | `domain` | `core/atomic.json` | ✅ R, I, T |
| 13 | `ws` | (implicit in all files) | ⚠️ Incidental |
| 14 | `value` | `core/atomic.json`, `core/boundary-values.json` | ✅ |
| 15 | `time_sep` | `core/atomic.json` (JEAB notation variants) | ⚠️ Incidental |
| 16 | `time_unit` | `core/atomic.json`, `core/warnings.json` | ✅ s, ms, min |
| 17 | `number` | `core/atomic.json`, `core/boundary-values.json` | ✅ |
| 18 | `ident` | `core/binding.json` | ✅ |
| 19 | `reserved` | `core/errors.json` (RESERVED_WORD cases) | ✅ |
| 20 | `compound` | `core/compound.json` (27 cases) | ✅ |
| 21 | `combinator` | `core/compound.json` | ✅ All 9 combinators |
| 22 | `arg_list` | `core/compound.json`, `core/compound-kw-aliases.json` | ✅ |
| 23 | `positional_args` | `core/compound.json` | ✅ |
| 24 | `keyword_arg` | `core/compound.json`, `core/compound-kw-aliases.json` | ✅ |
| 25 | `scalar_kw_arg` | `core/compound.json`, `core/compound-kw-aliases.json` | ✅ |
| 26 | `directional_kw_arg` | `core/semantic-violations-extended.json`, `core/warnings.json` | ✅ |
| 27 | `dir_ref` | `core/errors.json` | ✅ |
| 28 | `kw_name` | `core/compound.json`, `core/compound-kw-aliases.json` | ✅ |
| 29 | `interpolate` | `core/interpolated.json` | ✅ |
| 30 | `interp_kw_arg` | `core/interpolated.json`, `core/errors.json` | ✅ |
| 31 | `modifier` | `core/modifier.json` (21 cases) | ✅ |
| 32 | `dr_mod` | `core/modifier.json` | ✅ DRL, DRH, DRO |
| 33 | `pr_mod` | `core/modifier.json` | ✅ |
| 34 | `pr_opts` | `core/modifier.json` | ✅ |
| 35 | `pr_step` | `core/modifier.json` | ✅ hodos, exponential, linear |
| 36 | `pr_param` | `core/modifier.json` | ✅ start, increment |
| 37 | `repeat` | `core/modifier.json`, `core/algebra.json` | ✅ |
| 38 | `lag_mod` | `core/modifier.json` | ✅ |
| 39 | `lag_kw_arg` | `core/modifier.json`, `core/errors.json` | ✅ |
| 40 | `aversive_schedule` | `core/aversive.json` (14 cases) | ✅ |
| 41 | `sidman_avoidance` | `core/aversive.json` | ✅ |
| 42 | `sidman_arg` | `core/aversive.json`, `core/errors.json` | ✅ |
| 43 | `sidman_kw` | `core/aversive.json` | ✅ |
| 44 | `discriminated_avoidance` | `core/aversive.json` | ✅ |
| 45 | `da_arg` | `core/aversive.json`, `core/errors.json` | ✅ |
| 46 | `da_temporal_kw` | `core/aversive.json` | ✅ |
| 47 | `da_mode` | `core/aversive.json`, `core/errors.json` | ✅ |
| 48 | `annotation` | `annotations/program-level.json`, `annotations/measurement.json` | ✅ |
| 49 | `annotation_args` | `annotations/program-level.json`, `annotations/measurement.json` | ✅ |
| 50 | `annotation_val` | `annotations/program-level.json`, `annotations/measurement.json` | ✅ |
| 51 | `pctl_mod` | `core-stateful/percentile.json` | ✅ |

**Summary:** 51 productions; 49 with dedicated coverage, 2 with incidental coverage only (`ws`, `time_sep`).

## Semantic Rule Coverage

| Rule | Description | Test File(s) | Status |
|---|---|---|---|
| LH propagation R1–R6 | §1.6.1 attribute grammar | `core/lh_propagation.json` (14 cases) | ✅ |
| Algebraic equivalence | §2.2 theorems 1–8, rewrite rules R1–R17 | `core/algebra.json` (24 cases) | ✅ |
| Binding expansion | let-binding macro substitution | `core/binding.json`, `core/program.json` | ✅ |
| Repeat desugaring | Repeat(n, S) → Tand | `core/algebra.json` | ✅ |
| Value range constraints | §P-3 refinement types | `core/boundary-values.json` (33 cases) | ✅ |
| SecondOrder operational semantics | §2.11.1 state machine | `core/second_order.json` (5 cases) | ⚠️ Basic only |
| Measurement annotation parsing | 10 keywords, v1.0–v1.2 | `annotations/measurement.json` (30 cases) | ✅ |
| Measurement annotation errors | required_if/forbidden_if, cross-annotation | `annotations/errors.json` (34 measurement cases) | ✅ |
| Cross-annotation composition | JEAB 4-category preamble | `annotations/program-level.json` (4 cases) | ✅ |

## Error Code Coverage

| Error Code | Type | Test File | Status |
|---|---|---|---|
| `UNEXPECTED_EOF` | ParseError | `core/errors.json` | ✅ |
| `UNEXPECTED_CHARACTER` | LexError | `core/errors.json` | ✅ |
| `UNEXPECTED_TOKEN` | ParseError | `core/errors.json` | ✅ |
| `INSUFFICIENT_COMPONENTS` | ParseError | `core/errors.json` | ✅ |
| `UNDEFINED_IDENTIFIER` | SemanticError | `core/errors.json` | ✅ |
| `FORWARD_REFERENCE` | SemanticError | `core/errors.json` | ✅ |
| `DUPLICATE_BINDING` | SemanticError | `core/errors.json` | ✅ |
| `RESERVED_WORD` | ParseError | `core/errors.json` | ✅ |
| `EXPECTED_VALUE` | ParseError | `core/errors.json` | ✅ |
| `EXPECTED_RPAREN` | ParseError | `core/errors.json` | ✅ |
| `EXPECTED_COMMA_OR_RPAREN` | ParseError | `core/errors.json` | ✅ |
| `EXPECTED_LPAREN_OR_NUMBER` | ParseError | `core/errors.json` | ✅ |
| `INVALID_SECOND_ORDER_OVERALL` | ParseError | `core/errors.json` | ✅ |
| `KEYWORD_BEFORE_POSITIONAL` | ParseError | `core/errors.json` | ✅ |
| `INVALID_KEYWORD_ARG` | SemanticError | `core/errors.json`, `core/semantic-violations-extended.json` | ✅ |
| `DUPLICATE_KEYWORD_ARG` | SemanticError | `core/errors.json` | ✅ |
| `ATOMIC_NONPOSITIVE_VALUE` | SemanticError | `core/errors.json` | ✅ |
| `DR_NONPOSITIVE_VALUE` | SemanticError | `core/errors.json` | ✅ |
| `PR_NONPOSITIVE_VALUE` | SemanticError | `core/errors.json` | ✅ |
| `PR_NON_INTEGER_VALUE` | SemanticError | `core/errors.json` | ✅ |
| `FRCO_NONPOSITIVE_VALUE` | SemanticError | `core/errors.json` | ✅ |
| `REPEAT_ZERO_COUNT` | SemanticError | `core/errors.json` | ✅ |
| `REPEAT_NON_INTEGER_COUNT` | SemanticError | `core/errors.json` | ✅ |
| `OVERLAY_REQUIRES_TWO` | SemanticError | `core/errors.json` | ✅ |
| `MISSING_SIDMAN_PARAM` | SemanticError | `core/errors.json` | ✅ |
| `SIDMAN_TIME_UNIT_REQUIRED` | SemanticError | `core/errors.json` | ✅ |
| `SIDMAN_NONPOSITIVE_PARAM` | SemanticError | `core/errors.json` | ✅ |
| `DUPLICATE_SIDMAN_PARAM` | SemanticError | `core/errors.json` | ✅ |
| `MISSING_DA_PARAM` | SemanticError | `core/errors.json` | ✅ |
| `MISSING_SHOCK_DURATION` | SemanticError | `core/errors.json` | ✅ |
| `INVALID_PARAM_FOR_MODE` | SemanticError | `core/errors.json` | ✅ |
| `DA_INVALID_MODE` | SemanticError | `core/errors.json` | ✅ |
| `DA_TIME_UNIT_REQUIRED` | SemanticError | `core/errors.json` | ✅ |
| `DA_NONPOSITIVE_PARAM` | SemanticError | `core/errors.json` | ✅ |
| `DA_ITI_TOO_SHORT` | SemanticError | `core/errors.json` | ✅ |
| `DUPLICATE_DA_PARAM` | SemanticError | `core/errors.json` | ✅ |
| `LAG_INVALID_N_VALUE` | SemanticError | `core/errors.json` | ✅ |
| `LAG_UNEXPECTED_TIME_UNIT` | SemanticError | `core/errors.json` | ✅ |
| `LAG_INVALID_LENGTH` | SemanticError | `core/errors.json` | ✅ |
| `DUPLICATE_LAG_KW_ARG` | SemanticError | `core/errors.json` | ✅ |
| `MISSING_INTERPOLATE_COUNT` | SemanticError | `core/errors.json` | ✅ |
| `INTERPOLATE_NONPOSITIVE_COUNT` | SemanticError | `core/errors.json` | ✅ |
| `INTERPOLATE_COUNT_TIME_UNIT` | SemanticError | `core/errors.json` | ✅ |
| `INTERPOLATE_REQUIRES_TWO` | SemanticError | `core/errors.json` | ✅ |
| `INTERPOLATE_ONSET_TIME_UNIT_REQUIRED` | SemanticError | `core/errors.json` | ✅ |
| `INTERPOLATE_NONPOSITIVE_ONSET` | SemanticError | `core/errors.json` | ✅ |
| `DUPLICATE_INTERPOLATE_KW_ARG` | SemanticError | `core/errors.json` | ✅ |
| `DIRECTIONAL_SELF_REFERENCE` | SemanticError | `core/errors.json` | ✅ |
| `DIRECTIONAL_INDEX_OUT_OF_RANGE` | SemanticError | `core/errors.json` | ✅ |
| `DUPLICATE_DIRECTIONAL_KW` | SemanticError | `core/errors.json` | ✅ |
| `INVALID_DIRECTIONAL_KW` | SemanticError | `core/errors.json` | ✅ |
| `DIRECTIONAL_IDENT_NOT_FOUND` | SemanticError | `core/errors.json` | ✅ |

### Measurement Annotation Error Codes

| Error Code | Type | Test File | Status |
|---|---|---|---|
| `SESSION_END_MISSING_PARAM` | SemanticError | `annotations/errors.json` | ✅ (2 cases: missing time, missing reinforcers) |
| `SESSION_END_INVALID_COMBO` | SemanticError | `annotations/errors.json` | ✅ (2 cases: time_only+reinforcers, reinforcers_only+time) |
| `SESSION_END_UNKNOWN_RULE` | SemanticError | `annotations/errors.json` | ✅ |
| `BASELINE_INVALID_SESSIONS` | SemanticError | `annotations/errors.json` | ✅ |
| `STEADY_STATE_INVALID_WINDOW` | SemanticError | `annotations/errors.json` | ✅ |
| `STEADY_STATE_NEGATIVE_CHANGE` | SemanticError | `annotations/errors.json` | ✅ |
| `STEADY_STATE_INVALID_MIN_SESSIONS` | SemanticError | `annotations/errors.json` | ✅ |
| `DEPENDENT_MEASURE_EMPTY_VARIABLES` | SemanticError | `annotations/errors.json` | ✅ |
| `DEPENDENT_MEASURE_UNKNOWN_VARIABLE` | SemanticError | `annotations/errors.json` | ✅ |
| `DEPENDENT_MEASURE_PRIMARY_NOT_IN_VARIABLES` | SemanticError | `annotations/errors.json` | ✅ |
| `TRAINING_VOLUME_EMPTY_TRACK` | SemanticError | `annotations/errors.json` | ✅ |
| `TRAINING_VOLUME_UNKNOWN_METRIC` | SemanticError | `annotations/errors.json` | ✅ |
| `TRAINING_VOLUME_NONPOSITIVE_CRITERION` | SemanticError | `annotations/errors.json` | ✅ |
| `MICROSTRUCTURE_NTH_MISSING` | SemanticError | `annotations/errors.json` | ✅ |
| `MICROSTRUCTURE_NTH_FORBIDDEN` | SemanticError | `annotations/errors.json` | ✅ |
| `MICROSTRUCTURE_UNKNOWN_METHOD` | SemanticError | `annotations/errors.json` | ✅ |
| `MICROSTRUCTURE_UNKNOWN_REPORT` | SemanticError | `annotations/errors.json` | ✅ |
| `MICROSTRUCTURE_NONPOSITIVE_BIN` | SemanticError | `annotations/errors.json` | ✅ |
| `MICROSTRUCTURE_NONPOSITIVE_THRESHOLD` | SemanticError | `annotations/errors.json` | ✅ |
| `PHASE_END_UNKNOWN_RULE` | SemanticError | `annotations/errors.json` | ✅ |
| `PHASE_END_NO_CRITERIA` | SemanticError | `annotations/errors.json` | ✅ |
| `PHASE_END_MAX_LESS_THAN_MIN` | SemanticError | `annotations/errors.json` | ✅ |
| `PHASE_END_UNKNOWN_STABILITY` | SemanticError | `annotations/errors.json` | ✅ |
| `PHASE_END_MISSING_STEADY_STATE` | SemanticError | `annotations/errors.json` | ✅ (cross-annotation) |
| `LOGGING_EMPTY_EVENTS` | SemanticError | `annotations/errors.json` | ✅ |
| `LOGGING_UNKNOWN_EVENT` | SemanticError | `annotations/errors.json` | ✅ |
| `LOGGING_UNKNOWN_FORMAT` | SemanticError | `annotations/errors.json` | ✅ |
| `LOGGING_UNKNOWN_PRECISION` | SemanticError | `annotations/errors.json` | ✅ |
| `IRI_WINDOW_NONPOSITIVE_BIN` | SemanticError | `annotations/errors.json` | ✅ |
| `IRI_WINDOW_UNKNOWN_NORMALIZE` | SemanticError | `annotations/errors.json` | ✅ |
| `IRI_WINDOW_UNKNOWN_REPORT` | SemanticError | `annotations/errors.json` | ✅ |
| `WARMUP_EXCLUDE_NONPOSITIVE` | SemanticError | `annotations/errors.json` | ✅ |
| `WARMUP_EXCLUDE_UNKNOWN_SCOPE` | SemanticError | `annotations/errors.json` | ✅ |
| `WARMUP_EXCLUDE_EXCEEDS_SESSION` | SemanticError | `annotations/errors.json` | ✅ (cross-annotation) |

### Warning Codes

| Warning Code | Test File | Status |
|---|---|---|
| `MISSING_TIME_UNIT` | `core/warnings.json` | ✅ |
| `MISSING_COD` | `core/warnings.json` | ✅ |
| `RSI_EXCEEDS_SSI` | `core/warnings.json` | ✅ |
| `LAG_LARGE_N` | `core/warnings.json` | ✅ |
| `MISSING_INTERPOLATE_ONSET` | `core/warnings.json` | ✅ |
| `REDUNDANT_DIRECTIONAL_COD` | `core/warnings.json` | ✅ |
| `VACUOUS_LH_RATIO` | `core/lh_propagation.json` | ✅ |

## Known Gaps

1. **Experiment layer** (`conformance/experiment/`): declared in README but test files not yet on disk. PhaseSequence, Phase, Criterion types have zero test coverage.
2. **SecondOrder operational semantics**: only 5 basic parsing tests; no tests for FR-desugaring equivalence or interval-overall state machine behavior.
3. **Multi-error recovery**: no conformance tests for parser behavior with multiple errors in a single input (§3.7).

## Resolved Gaps (2026-04-14)

1. **Measurement annotator**: A-1 complete. All 10 keywords (v1.0–v1.2) have parsing conformance tests (30 cases), error validation tests (34 cases including 2 cross-annotation), and JEAB 4-category composition test. Schema promoted to Stable.
