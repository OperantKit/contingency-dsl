# Conformance Test Coverage Mapping

Maps every grammar production rule, semantic constraint, error code, and warning code
to the specific conformance test file(s) and test case ID(s) that exercise it.

**Purpose (I-4):** Resolves P-10 (coverage criteria undefined). Serves as an
implementation checklist, prevents test duplication, and exposes untested paths.

**Maintenance:** Update this file whenever adding/removing conformance test cases.

---

## Summary

| Layer | Files | Test Cases | Status |
|---|---|---|---|
| **Core** | 16 | 420 | ✅ Primary coverage |
| **Core-Stateful** | 4 | 92 | ✅ Full coverage |
| **Core-Trial-Based** | 2 | 62 | ✅ Full coverage |
| **Experiment** | 3 | 20 | ✅ Full coverage |
| **Annotations** | 3 | 69 | ✅ Full coverage |
| **Representations (T-τ)** | 4 | 33 | ✅ Full coverage |
| **Total** | **33** | **696** | |

---

## §1. Grammar Production Coverage

### §1.1 Core Grammar (`schema/core/grammar.ebnf`)

| # | Production | Test File(s) | Test Case IDs | Status |
|---|---|---|---|---|
| 1 | `program` | `core/program.json` | `program_lh_default`, `program_lh_and_bindings`, `program_minimal`, `program_comments_and_whitespace` | ✅ 4 cases |
| 2 | `program_annotation` | `annotations/program-level.json` | `program_annotations_subject_only`, `program_annotations_full_preamble`, `program_annotations_with_schedule_annotations`, `program_annotations_all_four_jeab_categories` | ✅ 4 cases |
| 3 | `param_decl` | `core/program.json`, `core/limited_hold.json`, `core/reinforcement_delay.json` | `program_lh_default`, `program_lh_and_bindings`, `lh_alias_param_decl`, `rd_param_decl_ms`, `rd_param_decl_s`, `rd_param_decl_zero`, `rd_param_decl_alias`, `rd_with_other_param_decls` | ✅ |
| 4 | `param_name` | `core/program.json`, `core/compound-kw-aliases.json`, `core/reinforcement_delay.json` | LH, COD, FRCO, BO, RD + verbose aliases | ✅ All 10 variants |
| 5 | `binding` | `core/binding.json` | `let_simple` .. `let_in_second_order_both` | ✅ 9 cases |
| 6 | `schedule` | (ubiquitous) | — | ✅ Implicit |
| 7 | `base_schedule` | (tested via atomic, compound, modifier, ident, paren) | — | ✅ Transitive |
| 8 | `atomic_or_second` | `core/atomic.json`, `core/second_order.json` | 32 + 5 = 37 cases | ✅ |
| 9 | `parametric_atomic` | `core/atomic.json` | `atomic_fr5` .. `atomic_ri_space_sec` (24 valid variants), all 3×3 dist×domain | ✅ Full grid |
| 10 | `simple_schedule` | `core/second_order.json` | `second_order_fr5_fi30` .. `second_order_rr_ft` | ✅ 5 cases |
| 11 | `dist` | `core/atomic.json` | F: `atomic_fr5`; V: `atomic_vi60s`; R: `atomic_rr20` | ✅ F, V, R |
| 12 | `domain` | `core/atomic.json` | R: `atomic_fr5`; I: `atomic_vi60s`; T: `atomic_ft30s` | ✅ R, I, T |
| 13 | `ws` | (implicit in all files) | — | ⚠️ Incidental |
| 14 | `value` | `core/atomic.json`, `core/boundary-values.json` | integer, float, with/without unit | ✅ |
| 15 | `time_sep` | `core/atomic.json` | `atomic_vi_hyphen_s` (hyphen), `atomic_vi_space_s` (space), `atomic_vi60s` (compact) | ✅ All 3 forms |
| 16 | `time_unit` | `core/atomic.json`, `core/warnings.json` | `atomic_vi60s` (s), `atomic_vi_ms` (ms), `atomic_fi_min` (min), `atomic_fi_hyphen_sec` (sec→s normalization) | ✅ s, sec, ms, min |
| 17 | `number` | `core/atomic.json`, `core/boundary-values.json` | integer: `atomic_fr5`; float: `atomic_fr_float`; large: `boundary_fr_large` | ✅ |
| 18 | `ident` | `core/binding.json` | `let_simple`, `let_underscore_name` | ✅ |
| 19 | `reserved` | `core/errors.json` | `error_reserved_word_as_ident`, `error_reserved_pr_step_hodos`, `error_reserved_pr_param_start`, `error_reserved_pr_step_linear`, `error_reserved_pr_step_exponential`, `error_reserved_pr_step_geometric`, `error_reserved_pr_param_increment` | ✅ 7 cases |
| 20 | `compound` | `core/compound.json` | 34 cases | ✅ |
| 21 | `combinator` | `core/compound.json` | Conc: `conc_vi_vi`; Alt: `alt_fr_fi`; Conj: `conj_fr_fi`; Chain: `chain_fr_fi`; Tand: `tand_vr_drl`; Mult: `mult_fr_ext`; Mix: `mix_fr_fr`; Overlay: `overlay_basic` | ✅ All 8 |
| 22 | `interpolate` | `core/interpolated.json` | `interpolate_basic` .. `interpolate_with_let_binding` | ✅ 7 cases |
| 23 | `interp_kw_arg` | `core/interpolated.json`, `core/errors.json` | count: `interpolate_basic`; onset: `interpolate_with_onset` | ✅ Both keywords |
| 24 | `arg_list` | `core/compound.json`, `core/compound-kw-aliases.json` | positional-only + keyword-mixed | ✅ |
| 25 | `positional_args` | `core/compound.json` | 2-component: `conc_vi_vi`; 3: `conc_three_components`; 5: `conc_five_components` | ✅ |
| 26 | `keyword_arg` | `core/compound.json`, `core/compound-kw-aliases.json` | scalar + directional forms | ✅ |
| 27 | `scalar_kw_arg` | `core/compound.json`, `core/compound-kw-aliases.json` | `conc_vi_vi_with_cod`, `conc_with_frco`, `mult_fr_ext_with_bo` | ✅ |
| 28 | `directional_kw_arg` | `core/compound.json`, `core/semantic-violations-extended.json`, `core/warnings.json` | `conc_directional_cod_two` .. `conc_directional_cod_overrides_param_decl` | ✅ 7 cases |
| 29 | `dir_ref` | `core/compound.json`, `core/errors.json` | numeric: `conc_directional_cod_two`; ident: `conc_directional_cod_let_bindings` | ✅ Both forms |
| 30 | `kw_name` | `core/compound.json`, `core/compound-kw-aliases.json` | COD, ChangeoverDelay, FRCO, FixedRatioChangeover, BO, Blackout | ✅ All 6 |
| 31 | `modifier` | `core/modifier.json` | 23 cases | ✅ |
| 32 | `dr_mod` | `core/modifier.json` | `drl_5s`, `drh_2s`, `dro_10s`, `drl_space` | ✅ DRL, DRH, DRO |
| 33 | `pr_mod` | `core/modifier.json` | `pr_hodos`, `pr_linear`, `pr_exponential`, `pr_geometric`, `pr_geometric_defaults`, `pr_shorthand_5`, `pr_shorthand_1`, `pr_shorthand_no_space` | ✅ Both forms |
| 34 | `pr_opts` | `core/modifier.json` | `pr_hodos` (no params), `pr_linear` (with params), `pr_geometric` (with params) | ✅ |
| 35 | `pr_step` | `core/modifier.json` | `pr_hodos`, `pr_linear`, `pr_exponential`, `pr_geometric` | ✅ All 4 |
| 36 | `pr_param` | `core/modifier.json` | start + increment in `pr_linear`; start + ratio in `pr_geometric` | ✅ |
| 37 | `repeat` | `core/modifier.json`, `core/algebra.json` | `repeat_3_fr10`, `repeat_nested`, `repeat_1_identity`, `repeat_identity`, `repeat_additive_decomposition` | ✅ |
| 38 | `lag_mod` | `core/modifier.json` | `lag_simple_shorthand`, `lag_simple_no_space`, `lag_zero_equiv_crf`, `lag_parenthesized_n_only`, `lag_parenthesized_with_length`, `lag_page_neuringer_exp3`, `lag_in_mult_schedule`, `lag_let_binding` | ✅ 8 cases |
| 39 | `lag_kw_arg` | `core/modifier.json`, `core/errors.json` | `lag_parenthesized_with_length`, `lag_page_neuringer_exp3` | ✅ |
| 40 | `aversive_schedule` | `core/aversive.json` | 14 cases | ✅ |
| 41 | `sidman_avoidance` | `core/aversive.json` | `sidman_basic` .. `sidman_let_binding` | ✅ 7 cases |
| 42 | `sidman_arg` | `core/aversive.json`, `core/errors.json` | SSI, RSI, verbose aliases | ✅ |
| 43 | `sidman_kw` | `core/aversive.json` | SSI: `sidman_basic`; ShockShockInterval: `sidman_verbose_alias`; RSI: `sidman_basic`; ResponseShockInterval: `sidman_verbose_alias` | ✅ All 4 |
| 44 | `discriminated_avoidance` | `core/aversive.json` | `da_basic_escape` .. `da_param_order_swapped` | ✅ 7 cases |
| 45 | `da_arg` | `core/aversive.json`, `core/errors.json` | temporal + mode args | ✅ |
| 46 | `da_temporal_kw` | `core/aversive.json` | CSUSInterval, ITI, ShockDuration, MaxShock | ✅ All 4 |
| 47 | `da_mode` | `core/aversive.json`, `core/errors.json` | `da_basic_escape` (escape), `da_basic_fixed` (fixed) | ✅ Both |
| 48 | `annotated_schedule` | `annotations/measurement.json`, `annotations/program-level.json` | 29 + 4 = 33 cases | ✅ |
| 49 | `annotation` | `annotations/measurement.json`, `annotations/program-level.json` | — | ✅ |
| 50 | `annotation_args` | `annotations/measurement.json` | positional + keyword-only forms | ✅ |
| 51 | `annotation_kv` | `annotations/measurement.json` | `measurement_session_end_first` etc. | ✅ |
| 52 | `annotation_val` | `annotations/measurement.json` | string, time_value, number | ✅ All 3 types |
| 53 | `time_value` (annotation) | `annotations/measurement.json` | `measurement_session_end_first` | ✅ |
| 54 | `string_literal` | `annotations/measurement.json`, `annotations/program-level.json` | `measurement_full_preamble`, `program_annotations_full_preamble` | ✅ |

**Summary:** 54 productions; 52 with dedicated coverage, 1 implicit (`ws`), 1 transitive (`base_schedule`).

### §1.1b Experiment Layer Grammar (`schema/core/grammar.ebnf`, v2.0 additions)

| # | Production | Test File(s) | Test Case IDs | Status |
|---|---|---|---|---|
| E1 | `file` | `experiment/phase.json` | `phase_simple_aba` (experiment path) + all core tests (program path) | ✅ Both branches |
| E2 | `experiment` | `experiment/phase.json` | `phase_simple_aba`, `phase_shared_annotations` | ✅ |
| E3 | `phase_decl` | `experiment/phase.json` | `phase_simple_aba` (3 phases), `phase_with_stability`, `phase_with_cv_stability`, `phase_use_reference` | ✅ 5 cases |
| E4 | `phase_name` | `experiment/phase.json` | Baseline, Treatment, Reversal, Training, Rich, Lean | ✅ 6 names |
| E5 | `phase_body` | `experiment/phase.json` | with schedule, with `use` reference | ✅ Both |
| E6 | `phase_meta` | `experiment/phase.json` | session_spec: `phase_simple_aba`; stability_spec: `phase_with_stability` | ✅ Both |
| E7 | `session_spec` | `experiment/phase.json`, `experiment/errors.json` | `=`: `phase_simple_aba`; `>=`: `phase_with_stability` | ✅ Both operators |
| E8 | `stability_spec` | `experiment/phase.json` | visual: `phase_with_stability`; cv: `phase_with_cv_stability` | ✅ 2 methods |
| E9 | `stability_method` | `experiment/phase.json` | `visual`, `cv` | ✅ 2 of 6 |
| E10 | `stability_param` | `experiment/phase.json` | window=5, threshold=5% | ✅ |
| E11 | `phase_ref` | `experiment/phase.json`, `experiment/errors.json` | `phase_use_reference`, `error_undefined_phase_ref`, `error_forward_phase_ref` | ✅ 3 cases |
| E12 | `shaping_decl` | `experiment/shaping.json` | `shaping_single_variable`, `shaping_fixed_sessions`, `shaping_multi_variable`, `shaping_mixed_with_phases` | ✅ 4 cases |
| E13 | `shaping_steps` | `experiment/shaping.json`, `experiment/errors.json` | single: `shaping_single_variable`; multi: `shaping_multi_variable`; empty: `error_shaping_empty_steps` | ✅ |
| E14 | `number_list` | `experiment/shaping.json` | 5 elements: `shaping_single_variable`; 7: `shaping_fixed_sessions`; 4: `shaping_multi_variable` | ✅ |

**Summary:** 14 productions; all with dedicated coverage.

### §1.2 Core-Stateful Grammar (`schema/core-stateful/grammar.ebnf`)

| # | Production | Test File(s) | Test Case IDs | Status |
|---|---|---|---|---|
| S1 | `pctl_mod` | `core-stateful/percentile.json` | `pctl_minimal` .. `pctl_with_annotations` | ✅ 10 cases |
| S2 | `pctl_target` | `core-stateful/percentile.json` | IRT: `pctl_minimal`; force: `pctl_force_dimension`; duration: `pctl_duration_shaping`; rate: `pctl_rate_target`; latency: `pctl_fully_specified` | ✅ All 5 |
| S3 | `pctl_rank` | `core-stateful/percentile.json`, `core-stateful/errors.json` | valid: `pctl_minimal`; boundary: `pctl_warn_extreme_rank_zero`, `pctl_warn_extreme_rank_100` | ✅ |
| S4 | `pctl_kw_arg` | `core-stateful/percentile.json` | window: `pctl_with_window`; dir: `pctl_fully_specified` | ✅ Both |
| S5 | `pctl_dir` | `core-stateful/percentile.json` | below (default): `pctl_minimal`; above: `pctl_fully_specified` | ✅ Both |
| S6 | `adj_schedule` | `core-stateful/adjusting.json` | `adj_delay_minimal` .. `adj_with_annotations` | ✅ 16 cases |
| S7 | `adj_target` | `core-stateful/adjusting.json` | delay: `adj_delay_minimal`; ratio: `adj_ratio_minimal`; amount: `adj_amount_minimal` | ✅ All 3 |
| S8 | `adj_kw_arg` | `core-stateful/adjusting.json` | start, step, min, max | ✅ All 4 |
| S9 | `interlock_schedule` | `core-stateful/interlocking.json` | `interlock_standard` .. `interlock_with_annotations` | ✅ 12 cases |
| S10 | `interlock_kw_arg` | `core-stateful/interlocking.json` | R0: `interlock_standard`; T: `interlock_standard` | ✅ Both |

**Summary:** 10 productions; all with dedicated coverage.

### §1.3 Core-Trial-Based Grammar (`schema/core-trial-based/grammar.ebnf`)

| # | Production | Test File(s) | Test Case IDs | Status |
|---|---|---|---|---|
| T1 | `trial_based_schedule` | `core-trial-based/mts.json` | (transitive via mts_schedule) | ✅ |
| T2 | `mts_schedule` | `core-trial-based/mts.json` | `mts_minimal` .. `mts_with_limited_hold` | ✅ 23 cases |
| T3 | `mts_kw_arg` | `core-trial-based/mts.json` | comparisons, consequence, incorrect, ITI, type | ✅ All 5 |
| T4 | `mts_type` | `core-trial-based/mts.json` | identity: `mts_fully_specified`; arbitrary: `mts_arbitrary_explicit` | ✅ Both |

**Summary:** 4 productions; all with dedicated coverage.

---

## §2. Semantic Rule Coverage

| Rule | Spec Reference | Test File(s) | Test Case IDs | Status |
|---|---|---|---|---|
| LH propagation R1–R6 | theory.md §1.6.1 | `core/lh_propagation.json` | 27 cases (14 valid + 13 resolved ASTs) | ✅ |
| Algebraic equivalences | theory.md §2.2, Theorems 1–8 | `core/algebra.json` | 25 cases: identity (R1–R5, R10), annihilator (R6–R9), associativity (R13–R17), commutativity, non-distributivity, Repeat decomposition | ✅ |
| Let-binding expansion | grammar.ebnf §5 | `core/binding.json` | `let_simple` .. `let_in_second_order_both` (9 cases) | ✅ |
| Repeat desugaring | theory.md §2.2.3 | `core/algebra.json` | `repeat_identity`, `repeat_additive_decomposition` | ✅ |
| Value range constraints | grammar.ebnf §46–§62 | `core/boundary-values.json` | 54 cases (all atomic/DR/PR/LH/Repeat/FRCO/SecondOrder boundary values) | ✅ |
| SecondOrder semantics | theory.md §2.11.1 | `core/second_order.json`, `core/errors.json` | 5 basic parsing + 4 compound-unit rejection cases | ✅ |
| Annotation measurement parsing | annotations spec | `annotations/measurement.json` | 29 cases (all 10 keywords v1.0–v1.2) | ✅ |
| Annotation measurement errors | annotations spec | `annotations/errors.json` | 36 cases (incl. 2 cross-annotation) | ✅ |
| Cross-annotation composition | design-philosophy.md §4 | `annotations/program-level.json` | `program_annotations_all_four_jeab_categories` | ✅ |
| T-τ representation conversion | representations/t-tau.md | `representations/t-tau/` | 33 cases total (to: 11, from: 9, roundtrip: 6, errors: 7) | ✅ |
| Pctl percentile criterion | core-stateful/grammar.md | `core-stateful/percentile.json` | 10 valid cases | ✅ |
| Adj adjusting mechanism | core-stateful/grammar.md | `core-stateful/adjusting.json` | 16 valid cases | ✅ |
| Interlocking R(t) formula | core-stateful/grammar.md | `core-stateful/interlocking.json` | 12 valid cases | ✅ |
| MTS trial structure | core-trial-based/grammar.md | `core-trial-based/mts.json` | 23 valid cases | ✅ |
| MTS + combinator interaction | core-trial-based/grammar.md | `core-trial-based/mts.json` | `mts_in_mult`, `mts_in_chain`, `mts_mult_training_test` | ✅ |
| MTS + LH compatibility | core-trial-based/grammar.ebnf §LH | `core-trial-based/mts.json` | `mts_with_limited_hold` | ✅ |
| Trial-based modifier incompatibility | core-trial-based/grammar.ebnf | `core-trial-based/errors.json` | `mts_error_drl_modifier` .. `mts_error_lag_modifier` | ✅ 5 cases |

---

## §3. Error Code Coverage

### §3.1 Core Parse Errors

| Error Code | Type | Test File(s) | Test Case IDs | Status |
|---|---|---|---|---|
| `UNEXPECTED_EOF` | ParseError | `core/errors.json` | `error_empty_input` | ✅ |
| `UNEXPECTED_CHARACTER` | LexError | `core/errors.json` | `error_invalid_char`, `multi_error_missing_value_and_unexpected_char`, `multi_error_lex_errors_multiline`, `multi_error_three_parse_errors` | ✅ 4 cases |
| `UNEXPECTED_TOKEN` | ParseError | `core/errors.json`, `core/semantic-violations-extended.json` | `error_paren_as_second_order`, `error_da_missing_all` | ✅ 2 cases |
| `INSUFFICIENT_COMPONENTS` | ParseError | `core/errors.json`, `core/semantic-violations-extended.json` | `error_compound_one_component`, `error_interpolate_one_component`, `error_overlay_one_component` | ✅ 3 cases |
| `EXPECTED_VALUE` | ParseError | `core/errors.json`, `core/boundary-values.json` | `error_missing_value`, `boundary_fr_negative`, `boundary_vi_negative`, `boundary_drl_negative`, `error_atomic_negative_value`, `error_atomic_negative_interval`, `error_lh_negative`, `error_lag_missing_positional_n`, `multi_error_two_missing_values`, `multi_error_missing_value_and_unexpected_char`, `multi_error_three_parse_errors` | ✅ 11 cases |
| `EXPECTED_RPAREN` | ParseError | `core/errors.json` | `error_unclosed_paren`, `multi_error_three_parse_errors` | ✅ 2 cases |
| `EXPECTED_COMMA_OR_RPAREN` | ParseError | `core/errors.json` | `error_missing_comma` | ✅ |
| `EXPECTED_LPAREN_OR_NUMBER` | ParseError | `core/errors.json` | `error_pr_bare` | ✅ |
| `KEYWORD_BEFORE_POSITIONAL` | ParseError | `core/errors.json` | `error_keyword_before_positional` | ✅ |
| `RESERVED_WORD` | ParseError | `core/errors.json` | `error_reserved_word_as_ident`, `error_reserved_pr_step_hodos`, `error_reserved_pr_param_start`, `error_reserved_pr_step_linear`, `error_reserved_pr_step_exponential`, `error_reserved_pr_step_geometric`, `error_reserved_pr_param_increment` | ✅ 7 cases |
| `INVALID_SECOND_ORDER_OVERALL` | ParseError | `core/errors.json` | `error_second_order_ext_overall`, `error_crf_second_order_overall` | ✅ 2 cases |

### §3.2 Core Semantic Errors — Binding / Variable

| Error Code | Type | Test File(s) | Test Case IDs | Status |
|---|---|---|---|---|
| `UNDEFINED_IDENTIFIER` | SemanticError | `core/errors.json` | `error_undefined_ident` | ✅ |
| `FORWARD_REFERENCE` | SemanticError | `core/errors.json` | `error_forward_reference`, `error_self_referential_binding` | ✅ 2 cases |
| `DUPLICATE_BINDING` | SemanticError | `core/errors.json` | `error_shadowing`, `multi_error_semantic_binding_and_keyword` | ✅ 2 cases |

### §3.3 Core Semantic Errors — Value Range

| Error Code | Type | Test File(s) | Test Case IDs | Status |
|---|---|---|---|---|
| `ATOMIC_NONPOSITIVE_VALUE` | SemanticError | `core/errors.json`, `core/boundary-values.json` | `error_atomic_nonpositive_ratio`, `error_atomic_nonpositive_interval`, `boundary_fr_zero` .. `boundary_rt_zero` (10), `boundary_fr_zero_compact`, `boundary_second_order_fr0`, `multi_error_semantic_nonpositive_values`, `multi_error_semantic_mixed_codes`, `multi_error_semantic_nonpositive_and_duplicate_kw` | ✅ 17 cases |
| `DR_NONPOSITIVE_VALUE` | SemanticError | `core/errors.json`, `core/boundary-values.json` | `error_dr_nonpositive`, `boundary_drl_zero`, `boundary_drh_zero`, `boundary_dro_zero`, `multi_error_semantic_mixed_codes` | ✅ 5 cases |
| `PR_NONPOSITIVE_VALUE` | SemanticError | `core/errors.json`, `core/boundary-values.json` | `error_pr_nonpositive_shorthand`, `error_pr_nonpositive_start`, `error_pr_nonpositive_increment`, `boundary_pr_shorthand_zero`, `boundary_pr_linear_zero_start`, `boundary_pr_linear_zero_increment`, `boundary_pr_geometric_zero_start` | ✅ 7 cases |
| `PR_NON_INTEGER_VALUE` | SemanticError | `core/errors.json`, `core/boundary-values.json` | `error_pr_non_integer_start`, `error_pr_non_integer_increment`, `error_pr_non_integer_shorthand`, `boundary_pr_fractional_shorthand`, `boundary_pr_fractional_start`, `boundary_pr_fractional_increment` | ✅ 6 cases |
| `LH_NONPOSITIVE_VALUE` | SemanticError | `core/errors.json`, `core/boundary-values.json` | `error_lh_nonpositive_expression`, `error_lh_nonpositive_expression_ms`, `error_lh_nonpositive_program_level`, `boundary_lh_zero` | ✅ 4 cases |
| `FRCO_NONPOSITIVE_VALUE` | SemanticError | `core/errors.json`, `core/boundary-values.json` | `error_frco_nonpositive`, `boundary_conc_frco_zero` | ✅ 2 cases |
| `PR_GEOMETRIC_RATIO_NOT_PROGRESSIVE` | SemanticError | `core/boundary-values.json` | `boundary_pr_geometric_ratio_one`, `boundary_pr_geometric_ratio_below_one` | ✅ 2 cases |
| `REPEAT_ZERO_COUNT` | SemanticError | `core/errors.json` | `error_repeat_zero` | ✅ |
| `REPEAT_NON_INTEGER_COUNT` | SemanticError | `core/errors.json`, `core/boundary-values.json` | `error_repeat_non_integer`, `boundary_repeat_fractional`, `boundary_repeat_fractional_large` | ✅ 3 cases |

### §3.4 Core Semantic Errors — Compound / Combinator

| Error Code | Type | Test File(s) | Test Case IDs | Status |
|---|---|---|---|---|
| `INVALID_KEYWORD_ARG` | SemanticError | `core/errors.json`, `core/semantic-violations-extended.json` | `error_cod_on_chain`, `error_cod_on_alt`, `error_frco_on_tand`, `error_bo_on_conc`, `error_bo_on_chain`, `error_bo_on_tand`, `error_bo_on_alt`, `error_overlay_keyword_arg`, `error_directional_frco`, `error_directional_bo`, `error_directional_cod_on_chain`, + 18 extended cases | ✅ 29 cases |
| `DUPLICATE_KEYWORD_ARG` | SemanticError | `core/errors.json`, `core/semantic-violations-extended.json` | `error_duplicate_keyword`, `error_duplicate_bo`, + 3 alias-collision cases, `multi_error_semantic_nonpositive_and_duplicate_kw`, `multi_error_semantic_binding_and_keyword` | ✅ 7 cases |
| `OVERLAY_REQUIRES_TWO` | SemanticError | `core/errors.json` | `error_overlay_three_components` | ✅ |
| `INTERPOLATE_REQUIRES_TWO` | SemanticError | `core/errors.json`, `core/semantic-violations-extended.json` | `error_interpolate_three_components`, `error_interp_alias_three_components` | ✅ 2 cases |
| `MISSING_INTERPOLATE_COUNT` | SemanticError | `core/errors.json`, `core/semantic-violations-extended.json` | `error_interpolate_missing_count`, `error_interp_alias_missing_count` | ✅ 2 cases |
| `INTERPOLATE_NONPOSITIVE_COUNT` | SemanticError | `core/errors.json`, `core/semantic-violations-extended.json` | `error_interpolate_count_zero`, `error_interpolate_count_negative` | ✅ 2 cases |
| `INTERPOLATE_COUNT_TIME_UNIT` | SemanticError | `core/errors.json` | `error_interpolate_count_with_time_unit` | ✅ |
| `INTERPOLATE_ONSET_TIME_UNIT_REQUIRED` | SemanticError | `core/errors.json` | `error_interpolate_onset_no_time_unit` | ✅ |
| `INTERPOLATE_NONPOSITIVE_ONSET` | SemanticError | `core/errors.json`, `core/semantic-violations-extended.json` | `error_interpolate_onset_nonpositive`, `error_interpolate_onset_negative` | ✅ 2 cases |
| `DUPLICATE_INTERPOLATE_KW_ARG` | SemanticError | `core/errors.json`, `core/semantic-violations-extended.json` | `error_interpolate_duplicate_count`, `error_interpolate_duplicate_onset` | ✅ 2 cases |
| `INVALID_SECOND_ORDER_UNIT` | SemanticError | `core/errors.json` | `error_second_order_chain_unit`, `error_second_order_tand_unit`, `error_second_order_conc_unit`, `error_second_order_mult_unit` | ✅ 4 cases |

### §3.5 Core Semantic Errors — Directional COD

| Error Code | Type | Test File(s) | Test Case IDs | Status |
|---|---|---|---|---|
| `DIRECTIONAL_SELF_REFERENCE` | SemanticError | `core/errors.json` | `error_directional_cod_self_reference` | ✅ |
| `DIRECTIONAL_INDEX_OUT_OF_RANGE` | SemanticError | `core/errors.json` | `error_directional_cod_index_out_of_range` | ✅ |
| `DIRECTIONAL_IDENT_NOT_FOUND` | SemanticError | `core/errors.json` | `error_directional_cod_ident_not_found` | ✅ |
| `DUPLICATE_DIRECTIONAL_KW` | SemanticError | `core/errors.json` | `error_directional_cod_duplicate` | ✅ |
| `INVALID_DIRECTIONAL_KW` | SemanticError | `core/errors.json` | `error_directional_frco`, `error_directional_bo` | ✅ 2 cases |

### §3.6 Core Semantic Errors — Sidman Avoidance

| Error Code | Type | Test File(s) | Test Case IDs | Status |
|---|---|---|---|---|
| `MISSING_SIDMAN_PARAM` | SemanticError | `core/errors.json`, `core/semantic-violations-extended.json` | `error_sidman_missing_rsi`, `error_sidman_missing_ssi`, `error_sidman_verbose_alias_missing_rsi` | ✅ 3 cases |
| `SIDMAN_TIME_UNIT_REQUIRED` | SemanticError | `core/errors.json`, `core/semantic-violations-extended.json` | `error_sidman_no_time_unit`, `error_sidman_mixed_time_unit` | ✅ 2 cases |
| `SIDMAN_NONPOSITIVE_PARAM` | SemanticError | `core/errors.json`, `core/semantic-violations-extended.json` | `error_sidman_zero_ssi`, `error_sidman_zero_rsi` | ✅ 2 cases |
| `DUPLICATE_SIDMAN_PARAM` | SemanticError | `core/errors.json`, `core/semantic-violations-extended.json` | `error_sidman_duplicate_ssi`, `error_sidman_duplicate_alias`, `error_sidman_duplicate_rsi_alias` | ✅ 3 cases |

### §3.7 Core Semantic Errors — Discriminated Avoidance

| Error Code | Type | Test File(s) | Test Case IDs | Status |
|---|---|---|---|---|
| `MISSING_DA_PARAM` | SemanticError | `core/errors.json`, `core/semantic-violations-extended.json` | `error_da_missing_mode`, `error_da_missing_csus`, `error_da_missing_iti`, `error_discrimav_alias_missing_mode` | ✅ 4 cases |
| `DA_TIME_UNIT_REQUIRED` | SemanticError | `core/errors.json` | `error_da_no_time_unit` | ✅ |
| `DA_NONPOSITIVE_PARAM` | SemanticError | `core/errors.json` | `error_da_nonpositive_csus` | ✅ |
| `DA_INVALID_MODE` | SemanticError | `core/errors.json` | `error_da_invalid_mode` | ✅ |
| `MISSING_SHOCK_DURATION` | SemanticError | `core/errors.json` | `error_da_fixed_missing_shock_duration` | ✅ |
| `INVALID_PARAM_FOR_MODE` | SemanticError | `core/errors.json` | `error_da_fixed_with_max_shock`, `error_da_escape_with_shock_duration` | ✅ 2 cases |
| `DA_ITI_TOO_SHORT` | SemanticError | `core/errors.json`, `core/semantic-violations-extended.json` | `error_da_iti_too_short`, `error_da_iti_equals_csus` | ✅ 2 cases |
| `DUPLICATE_DA_PARAM` | SemanticError | `core/errors.json` | `error_da_duplicate_param` | ✅ |

### §3.8 Core Semantic Errors — Lag

| Error Code | Type | Test File(s) | Test Case IDs | Status |
|---|---|---|---|---|
| `LAG_INVALID_N_VALUE` | SemanticError | `core/errors.json` | `error_lag_negative_n`, `error_lag_non_integer_n` | ✅ 2 cases |
| `LAG_UNEXPECTED_TIME_UNIT` | SemanticError | `core/errors.json` | `error_lag_time_unit` | ✅ |
| `LAG_INVALID_LENGTH` | SemanticError | `core/errors.json` | `error_lag_length_zero`, `error_lag_length_negative` | ✅ 2 cases |
| `DUPLICATE_LAG_KW_ARG` | SemanticError | `core/errors.json` | `error_lag_duplicate_kw` | ✅ |

### §3.9 Core Semantic Errors — Reinforcement Delay

| Error Code | Type | Test File(s) | Test Case IDs | Status |
|---|---|---|---|---|
| `RD_TIME_UNIT_REQUIRED` | SemanticError | `core/reinforcement_delay.json` | `rd_error_no_time_unit` | ✅ |
| `RD_NEGATIVE_VALUE` | SemanticError | `core/reinforcement_delay.json` | `rd_error_negative` | ✅ |

### §3.10 Core Semantic Errors — Multi-Error Recovery

| Test Case ID | Error Codes | Type |
|---|---|---|
| `multi_error_two_missing_values` | `EXPECTED_VALUE` × 2 | Parse |
| `multi_error_missing_value_and_unexpected_char` | `EXPECTED_VALUE`, `UNEXPECTED_CHARACTER` | Parse+Lex |
| `multi_error_lex_errors_multiline` | `UNEXPECTED_CHARACTER` × 2 | Lex |
| `multi_error_three_parse_errors` | `EXPECTED_VALUE`, `UNEXPECTED_CHARACTER`, `EXPECTED_RPAREN` | Mixed |
| `multi_error_semantic_nonpositive_values` | `ATOMIC_NONPOSITIVE_VALUE` × 2 | Semantic |
| `multi_error_semantic_mixed_codes` | `ATOMIC_NONPOSITIVE_VALUE`, `DR_NONPOSITIVE_VALUE` | Semantic |
| `multi_error_semantic_binding_and_keyword` | `DUPLICATE_BINDING`, `INVALID_KEYWORD_ARG` | Semantic |
| `multi_error_semantic_nonpositive_and_duplicate_kw` | `ATOMIC_NONPOSITIVE_VALUE`, `DUPLICATE_KEYWORD_ARG` | Semantic |

✅ 8 multi-error cases covering parse, lex, semantic, and mixed recovery.

### §3.11 Core-Stateful Semantic Errors — Percentile

| Error Code | Type | Test File(s) | Test Case IDs | Status |
|---|---|---|---|---|
| `PCTL_INVALID_RANK` | SemanticError | `core-stateful/errors.json` | `pctl_error_rank_out_of_range`, `pctl_error_negative_rank`, `pctl_error_fractional_rank` | ✅ 3 cases |
| `PCTL_INVALID_WINDOW` | SemanticError | `core-stateful/errors.json` | `pctl_error_window_zero`, `pctl_error_window_negative` | ✅ 2 cases |
| `PCTL_UNKNOWN_TARGET` | SemanticError | `core-stateful/errors.json` | `pctl_error_unknown_target` | ✅ |
| `PCTL_INVALID_DIR` | SemanticError | `core-stateful/errors.json` | `pctl_error_invalid_dir` | ✅ |
| `PCTL_UNEXPECTED_TIME_UNIT` | SemanticError | `core-stateful/errors.json` | `pctl_error_rank_with_time_unit` | ✅ |
| `DUPLICATE_PCTL_KW_ARG` | SemanticError | `core-stateful/errors.json` | `pctl_error_duplicate_window`, `pctl_error_duplicate_dir` | ✅ 2 cases |

### §3.12 Core-Stateful Semantic Errors — Adjusting

| Error Code | Type | Test File(s) | Test Case IDs | Status |
|---|---|---|---|---|
| `ADJ_MISSING_PARAM` | SemanticError | `core-stateful/errors.json` | `adj_error_missing_start`, `adj_error_missing_step`, `adj_error_no_args` | ✅ 3 cases |
| `ADJ_UNKNOWN_TARGET` | SemanticError | `core-stateful/errors.json` | `adj_error_unknown_target` | ✅ |
| `ADJ_NONPOSITIVE_START` | SemanticError | `core-stateful/errors.json` | `adj_error_nonpositive_start`, `adj_error_negative_start` | ✅ 2 cases |
| `ADJ_NONPOSITIVE_STEP` | SemanticError | `core-stateful/errors.json` | `adj_error_nonpositive_step` | ✅ |
| `ADJ_TIME_UNIT_REQUIRED` | SemanticError | `core-stateful/errors.json` | `adj_error_delay_missing_time_unit`, `adj_error_delay_max_missing_time_unit` | ✅ 2 cases |
| `ADJ_UNEXPECTED_TIME_UNIT` | SemanticError | `core-stateful/errors.json` | `adj_error_ratio_with_time_unit`, `adj_error_amount_with_time_unit` | ✅ 2 cases |
| `ADJ_INVALID_BOUNDS` | SemanticError | `core-stateful/errors.json` | `adj_error_invalid_bounds` | ✅ |
| `ADJ_START_OUT_OF_BOUNDS` | SemanticError | `core-stateful/errors.json` | `adj_error_start_out_of_bounds_below`, `adj_error_start_out_of_bounds_above` | ✅ 2 cases |
| `ADJ_RATIO_NOT_INTEGER` | SemanticError | `core-stateful/errors.json` | `adj_error_ratio_not_integer`, `adj_error_ratio_step_not_integer` | ✅ 2 cases |
| `DUPLICATE_ADJ_KW_ARG` | SemanticError | `core-stateful/errors.json` | `adj_error_duplicate_start`, `adj_error_duplicate_step` | ✅ 2 cases |

### §3.13 Core-Stateful Semantic Errors — Interlocking

| Error Code | Type | Test File(s) | Test Case IDs | Status |
|---|---|---|---|---|
| `INTERLOCK_MISSING_PARAM` | SemanticError | `core-stateful/errors.json` | `interlock_error_missing_R0`, `interlock_error_missing_T`, `interlock_error_no_args` | ✅ 3 cases |
| `INTERLOCK_INVALID_R0` | SemanticError | `core-stateful/errors.json` | `interlock_error_nonpositive_R0`, `interlock_error_negative_R0`, `interlock_error_fractional_R0` | ✅ 3 cases |
| `INTERLOCK_UNEXPECTED_TIME_UNIT` | SemanticError | `core-stateful/errors.json` | `interlock_error_R0_with_time_unit` | ✅ |
| `INTERLOCK_NONPOSITIVE_T` | SemanticError | `core-stateful/errors.json` | `interlock_error_nonpositive_T` | ✅ |
| `INTERLOCK_TIME_UNIT_REQUIRED` | SemanticError | `core-stateful/errors.json` | `interlock_error_T_missing_time_unit` | ✅ |
| `DUPLICATE_INTERLOCK_KW_ARG` | SemanticError | `core-stateful/errors.json` | `interlock_error_duplicate_R0` | ✅ |

### §3.14 Core-Trial-Based Semantic Errors — MTS

| Error Code | Type | Test File(s) | Test Case IDs | Status |
|---|---|---|---|---|
| `MTS_INVALID_COMPARISONS` | SemanticError | `core-trial-based/errors.json` | `mts_error_comparisons_less_than_2`, `mts_error_comparisons_zero`, `mts_error_comparisons_negative`, `mts_error_comparisons_fractional` | ✅ 4 cases |
| `MTS_COMPARISONS_TIME_UNIT` | SemanticError | `core-trial-based/errors.json` | `mts_error_comparisons_time_unit` | ✅ |
| `MTS_MISSING_PARAM` | SemanticError | `core-trial-based/errors.json` | `mts_error_missing_consequence`, `mts_error_missing_iti`, `mts_error_missing_comparisons` | ✅ 3 cases |
| `MTS_NONPOSITIVE_ITI` | SemanticError | `core-trial-based/errors.json` | `mts_error_iti_zero`, `mts_error_iti_negative` | ✅ 2 cases |
| `MTS_ITI_TIME_UNIT_REQUIRED` | SemanticError | `core-trial-based/errors.json` | `mts_error_iti_no_time_unit` | ✅ |
| `MTS_INVALID_TYPE` | SemanticError | `core-trial-based/errors.json` | `mts_error_invalid_type` | ✅ |
| `MTS_INVALID_CONSEQUENCE` | SemanticError | `core-trial-based/errors.json` | `mts_error_consequence_compound`, `mts_error_consequence_chain` | ✅ 2 cases |
| `MTS_INVALID_INCORRECT` | SemanticError | `core-trial-based/errors.json` | `mts_error_incorrect_compound` | ✅ |
| `MTS_RECURSIVE_CONSEQUENCE` | SemanticError | `core-trial-based/errors.json` | `mts_error_consequence_recursive_mts`, `mts_error_incorrect_recursive_mts` | ✅ 2 cases |
| `DUPLICATE_MTS_KW_ARG` | SemanticError | `core-trial-based/errors.json` | `mts_error_duplicate_comparisons`, `mts_error_duplicate_consequence`, `mts_error_duplicate_iti`, `mts_error_duplicate_type` | ✅ 4 cases |
| `TRIAL_BASED_MODIFIER_INCOMPATIBLE` | SemanticError | `core-trial-based/errors.json` | `mts_error_drl_modifier`, `mts_error_drh_modifier`, `mts_error_dro_modifier`, `mts_error_pctl_modifier`, `mts_error_lag_modifier` | ✅ 5 cases |

### §3.15 Representations — T-τ Errors

| Error Code | Type | Test File(s) | Test Case IDs | Status |
|---|---|---|---|---|
| `TTAU_T_ZERO` | RepresentationError | `representations/t-tau/errors.json` | `error_ttau_T_zero` | ✅ |
| `TTAU_T_NEGATIVE` | RepresentationError | `representations/t-tau/errors.json` | `error_ttau_T_negative` | ✅ |
| `TTAU_TAU_ZERO` | RepresentationError | `representations/t-tau/errors.json` | `error_ttau_tau_zero` | ✅ |
| `TTAU_TAU_EXCEEDS_T` | RepresentationError | `representations/t-tau/errors.json` | `error_ttau_tau_exceeds_T` | ✅ |
| `TO_TTAU_VALUE_ZERO` | RepresentationError | `representations/t-tau/errors.json` | `error_to_ttau_value_zero` | ✅ |
| `FROM_TTAU_RATIO_DOMAIN_ERROR` | RepresentationError | `representations/t-tau/from_ttau.json` | `from_ttau_ratio_domain_error` | ✅ |
| `TO_TTAU_RATIO_DOMAIN_ERROR` | RepresentationError | `representations/t-tau/to_ttau.json` | `to_ttau_fr5_error`, `to_ttau_vr10_error`, `to_ttau_rr20_error` | ✅ 3 cases |

### §3.16 Annotation Errors

| Error Code | Type | Test File(s) | Test Case IDs | Status |
|---|---|---|---|---|
| `SESSION_END_MISSING_PARAM` | SemanticError | `annotations/errors.json` | `error_session_end_first_missing_time`, `error_session_end_first_missing_reinforcers` | ✅ 2 cases |
| `SESSION_END_INVALID_COMBO` | SemanticError | `annotations/errors.json` | `error_session_end_time_only_with_reinforcers`, `error_session_end_reinforcers_only_with_time` | ✅ 2 cases |
| `SESSION_END_UNKNOWN_RULE` | SemanticError | `annotations/errors.json` | `error_session_end_unknown_rule` | ✅ |
| `BASELINE_INVALID_SESSIONS` | SemanticError | `annotations/errors.json` | `error_baseline_invalid_sessions` | ✅ |
| `STEADY_STATE_INVALID_WINDOW` | SemanticError | `annotations/errors.json` | `error_steady_state_small_window` | ✅ |
| `STEADY_STATE_NEGATIVE_CHANGE` | SemanticError | `annotations/errors.json` | `error_steady_state_negative_change` | ✅ |
| `STEADY_STATE_INVALID_MIN_SESSIONS` | SemanticError | `annotations/errors.json` | `error_steady_state_min_sessions_less_than_window` | ✅ |
| `DEPENDENT_MEASURE_EMPTY_VARIABLES` | SemanticError | `annotations/errors.json` | `error_dependent_measure_empty_variables` | ✅ |
| `DEPENDENT_MEASURE_UNKNOWN_VARIABLE` | SemanticError | `annotations/errors.json` | `error_dependent_measure_unknown_variable` | ✅ |
| `DEPENDENT_MEASURE_PRIMARY_NOT_IN_VARIABLES` | SemanticError | `annotations/errors.json` | `error_dependent_measure_primary_not_in_variables` | ✅ |
| `TRAINING_VOLUME_EMPTY_TRACK` | SemanticError | `annotations/errors.json` | `error_training_volume_empty_track` | ✅ |
| `TRAINING_VOLUME_UNKNOWN_METRIC` | SemanticError | `annotations/errors.json` | `error_training_volume_unknown_metric` | ✅ |
| `TRAINING_VOLUME_NONPOSITIVE_CRITERION` | SemanticError | `annotations/errors.json` | `error_training_volume_nonpositive_criterion` | ✅ |
| `MICROSTRUCTURE_NTH_MISSING` | SemanticError | `annotations/errors.json` | `error_microstructure_nth_missing` | ✅ |
| `MICROSTRUCTURE_NTH_FORBIDDEN` | SemanticError | `annotations/errors.json` | `error_microstructure_nth_forbidden` | ✅ |
| `MICROSTRUCTURE_UNKNOWN_METHOD` | SemanticError | `annotations/errors.json` | `error_microstructure_unknown_method` | ✅ |
| `MICROSTRUCTURE_UNKNOWN_REPORT` | SemanticError | `annotations/errors.json` | `error_microstructure_unknown_report` | ✅ |
| `MICROSTRUCTURE_NONPOSITIVE_BIN` | SemanticError | `annotations/errors.json` | `error_microstructure_nonpositive_bin_width` | ✅ |
| `MICROSTRUCTURE_NONPOSITIVE_THRESHOLD` | SemanticError | `annotations/errors.json` | `error_microstructure_nonpositive_threshold` | ✅ |
| `PHASE_END_NO_CRITERIA` | SemanticError | `annotations/errors.json` | `error_phase_end_no_criteria` | ✅ |
| `PHASE_END_MAX_LESS_THAN_MIN` | SemanticError | `annotations/errors.json` | `error_phase_end_max_less_than_min` | ✅ |
| `PHASE_END_UNKNOWN_RULE` | SemanticError | `annotations/errors.json` | `error_phase_end_unknown_rule` | ✅ |
| `PHASE_END_UNKNOWN_STABILITY` | SemanticError | `annotations/errors.json` | `error_phase_end_unknown_stability` | ✅ |
| `PHASE_END_MISSING_STEADY_STATE` | SemanticError | `annotations/errors.json` | `error_phase_end_stability_without_steady_state` | ✅ (cross-annotation) |
| `LOGGING_EMPTY_EVENTS` | SemanticError | `annotations/errors.json` | `error_logging_empty_events` | ✅ |
| `LOGGING_UNKNOWN_EVENT` | SemanticError | `annotations/errors.json` | `error_logging_unknown_event` | ✅ |
| `LOGGING_UNKNOWN_FORMAT` | SemanticError | `annotations/errors.json` | `error_logging_unknown_format` | ✅ |
| `LOGGING_UNKNOWN_PRECISION` | SemanticError | `annotations/errors.json` | `error_logging_unknown_precision` | ✅ |
| `IRI_WINDOW_NONPOSITIVE_BIN` | SemanticError | `annotations/errors.json` | `error_iri_window_nonpositive_bin` | ✅ |
| `IRI_WINDOW_UNKNOWN_NORMALIZE` | SemanticError | `annotations/errors.json` | `error_iri_window_unknown_normalize` | ✅ |
| `IRI_WINDOW_UNKNOWN_REPORT` | SemanticError | `annotations/errors.json` | `error_iri_window_unknown_report` | ✅ |
| `WARMUP_EXCLUDE_NONPOSITIVE` | SemanticError | `annotations/errors.json` | `error_warmup_exclude_nonpositive` | ✅ |
| `WARMUP_EXCLUDE_UNKNOWN_SCOPE` | SemanticError | `annotations/errors.json` | `error_warmup_exclude_unknown_scope` | ✅ |
| `WARMUP_EXCLUDE_EXCEEDS_SESSION` | SemanticError | `annotations/errors.json` | `error_warmup_exclude_exceeds_session_end` | ✅ (cross-annotation) |

---

## §4. Warning Code Coverage

### §4.1 Core Warnings

| Warning Code | Test File(s) | Test Case IDs | Status |
|---|---|---|---|
| `MISSING_TIME_UNIT` | `core/warnings.json`, `core/atomic.json` | `warn_fi_missing_time_unit`, `warn_vi_missing_time_unit`, `warn_ri_missing_time_unit`, `warn_ft_missing_time_unit`, `warn_vt_missing_time_unit`, `warn_rt_missing_time_unit`, `warn_fi_in_compound_missing_time_unit`, `warn_drl_missing_time_unit`, `warn_drh_missing_time_unit`, `warn_dro_missing_time_unit`, `atomic_fi30_no_unit` .. `atomic_rt15_no_unit` (6 in atomic) | ✅ 16 cases |
| `MISSING_COD` | `core/warnings.json`, `core/compound.json`, `core/binding.json` | `warn_conc_missing_cod_basic`, `conc_vi_vi`, `conc_three_components`, `nested_conc_chain_alt`, `conc_deep_nesting_depth3`, `conc_five_components`, `let_binding_in_compound` | ✅ 7+ cases |
| `RSI_EXCEEDS_SSI` | `core/warnings.json` | `warn_sidman_rsi_exceeds_ssi` | ✅ |
| `LAG_LARGE_N` | `core/warnings.json` | `warn_lag_large_n_51`, `warn_lag_large_n_100`, `warn_lag_large_n_parenthesized` | ✅ 3 cases |
| `MISSING_INTERPOLATE_ONSET` | `core/warnings.json` | `warn_interpolate_missing_onset`, `warn_interp_alias_missing_onset` | ✅ 2 cases |
| `REDUNDANT_DIRECTIONAL_COD` | `core/warnings.json` | `warn_redundant_directional_cod` | ✅ |
| `VACUOUS_LH_RATIO` | `core/lh_propagation.json` | `lh_prop_explicit_override`, `lh_prop_nested_chain_in_conc`, `lh_prop_ratio_warning`, `lh_prop_mult` | ✅ 4 cases |
| `RD_LARGE_DELAY` | `core/reinforcement_delay.json` | `rd_warning_large_delay` | ✅ |

### §4.2 Core-Stateful Warnings

| Warning Code | Test File(s) | Test Case IDs | Status |
|---|---|---|---|
| `PCTL_EXTREME_RANK` | `core-stateful/errors.json` | `pctl_warn_extreme_rank_zero`, `pctl_warn_extreme_rank_100` | ✅ 2 cases |
| `PCTL_SMALL_WINDOW` | `core-stateful/errors.json` | `pctl_warn_small_window` | ✅ |
| `PCTL_LARGE_WINDOW` | `core-stateful/errors.json` | `pctl_warn_large_window` | ✅ |
| `ADJ_UNBOUNDED_DELAY` | `core-stateful/errors.json` | `adj_warn_unbounded_delay` | ✅ |
| `ADJ_LARGE_STEP` | `core-stateful/errors.json` | `adj_warn_large_step` | ✅ |
| `ADJ_ZERO_MIN_DELAY` | `core-stateful/errors.json` | `adj_warn_zero_min_delay` | ✅ |
| `ADJ_SUBUNIT_RATIO` | `core-stateful/errors.json` | `adj_warn_subunit_ratio` | ✅ |
| `INTERLOCK_TRIVIAL_RATIO` | `core-stateful/errors.json` | `interlock_warn_trivial_ratio` | ✅ |
| `INTERLOCK_LARGE_RATIO` | `core-stateful/errors.json` | `interlock_warn_large_ratio` | ✅ |

### §4.3 Core-Trial-Based Warnings

| Warning Code | Test File(s) | Test Case IDs | Status |
|---|---|---|---|
| `MTS_MANY_COMPARISONS` | `core-trial-based/errors.json` | `mts_warn_many_comparisons`, `mts_warn_comparisons_boundary` | ✅ 2 cases |
| `MTS_NO_REINFORCEMENT` | `core-trial-based/errors.json` | `mts_warn_no_reinforcement` | ✅ |
| `MTS_IDENTITY_WITH_CLASSES` | `core-trial-based/errors.json` | `mts_warn_identity_with_stimulus_classes` | ✅ |
| `MTS_ARBITRARY_WITHOUT_CLASSES` | `core-trial-based/errors.json` | `mts_warn_arbitrary_without_stimulus_classes`, `mts_warn_default_arbitrary_without_stimulus_classes` | ✅ 2 cases |
| `MTS_SHORT_ITI` | `core-trial-based/errors.json` | `mts_warn_short_iti` | ✅ |
| `MTS_LONG_LH` | `core-trial-based/errors.json` | `mts_warn_long_lh` | ✅ |

---

## §5. Negative Coverage (Confirmed Non-Triggering Cases)

These test cases verify that valid inputs do NOT produce false warnings or errors.

| File | Test Case IDs | Verifies |
|---|---|---|
| `core/warnings.json` | `no_warn_fr_no_time_unit` | FR (ratio domain) has no MISSING_TIME_UNIT |
| `core/warnings.json` | `no_warn_fi_with_time_unit` | FI with explicit unit has no warning |
| `core/warnings.json` | `warn_sidman_rsi_equals_ssi` | RSI = SSI does NOT trigger RSI_EXCEEDS_SSI |
| `core/warnings.json` | `no_warn_sidman_rsi_less_than_ssi` | RSI < SSI is clean |
| `core/warnings.json` | `no_warn_lag_50` | Lag 50 does NOT trigger LAG_LARGE_N |
| `core/warnings.json` | `no_warn_interpolate_with_onset` | Interpolate with onset has no warning |
| `core/warnings.json` | `no_warn_conc_with_cod_explicit` | Conc with explicit COD has no warning |
| `core/warnings.json` | `no_warn_conc_with_cod_zero` | COD=0s does NOT trigger MISSING_COD |
| `core/warnings.json` | `warn_directional_cod_no_missing_cod` | Directional COD suppresses MISSING_COD |
| `core/atomic.json` | `atomic_fr5_no_warning`, `atomic_vi60s_no_warning` | Clean valid cases produce no diagnostics |
| `core-trial-based/mts.json` | `mts_comparisons_9_no_warning` | comparisons=9 does NOT trigger MTS_MANY_COMPARISONS |
| `core-trial-based/mts.json` | `mts_iti_1s_no_warning` | ITI=1s does NOT trigger MTS_SHORT_ITI |

---

## §6. File-Level Test Case Inventory

| File | Valid | Error | Warning | Total |
|---|---|---|---|---|
| `core/atomic.json` | 24 | 0 | 8 | 32 |
| `core/compound.json` | 27 | 0 | 7 | 34 |
| `core/modifier.json` | 23 | 0 | 0 | 23 |
| `core/binding.json` | 8 | 0 | 1 | 9 |
| `core/second_order.json` | 5 | 0 | 0 | 5 |
| `core/limited_hold.json` | 12 | 0 | 0 | 12 |
| `core/lh_propagation.json` | 23 | 0 | 4 | 27 |
| `core/aversive.json` | 14 | 0 | 0 | 14 |
| `core/interpolated.json` | 7 | 0 | 0 | 7 |
| `core/program.json` | 4 | 0 | 0 | 4 |
| `core/reinforcement_delay.json` | 7 | 2 | 1 | 10 |
| `core/algebra.json` | 25 | 0 | 0 | 25 |
| `core/errors.json` | 0 | 96 | 0 | 96 |
| `core/boundary-values.json` | 19 | 35 | 0 | 54 |
| `core/warnings.json` | 9 | 0 | 24 | 33 |
| `core/compound-kw-aliases.json` | 12 | 0 | 0 | 12 |
| `core/semantic-violations-extended.json` | 0 | 41 | 0 | 41 |
| `core-stateful/percentile.json` | 10 | 0 | 0 | 10 |
| `core-stateful/adjusting.json` | 16 | 0 | 0 | 16 |
| `core-stateful/interlocking.json` | 12 | 0 | 0 | 12 |
| `core-stateful/errors.json` | 0 | 38 | 16 | 54 |
| `core-trial-based/mts.json` | 23 | 0 | 0 | 23 |
| `core-trial-based/errors.json` | 0 | 29 | 10 | 39 |
| `annotations/measurement.json` | 29 | 0 | 0 | 29 |
| `annotations/program-level.json` | 4 | 0 | 0 | 4 |
| `annotations/errors.json` | 0 | 36 | 0 | 36 |
| `representations/t-tau/to_ttau.json` | 8 | 3 | 0 | 11 |
| `representations/t-tau/from_ttau.json` | 8 | 1 | 0 | 9 |
| `representations/t-tau/roundtrip.json` | 6 | 0 | 0 | 6 |
| `representations/t-tau/errors.json` | 0 | 7 | 0 | 7 |
| **Total** | **375** | **288** | **71** | **676** † |

† Some test cases contain both warnings and valid ASTs; counted once in the dominant category.

---

## §7. Known Gaps

### Coverage Gaps (no conformance test exists)

| # | Area | Description | Priority |
|---|---|---|---|
| G-1 | SecondOrder operational semantics | Only 5 basic parsing tests; no tests for FR-desugaring equivalence or interval-overall state machine behavior | MEDIUM |
| G-2 | Compound nesting depth ≥ 4 | Tested up to depth 3 (`conc_deep_nesting_depth3` etc.); deeper nesting is uncovered | LOW |
| G-3 | Pctl + Adj + Interlock stacking | No tests for stacking stateful modifiers (e.g., `Pctl(IRT, 50)` with Adj inside Conc) | LOW |
| G-4 | Annotation inheritance across binding expansion | Let-bindings referencing annotated schedules; propagation not thoroughly tested | LOW |
| G-5 | Experiment layer | Declared in README (`conformance/experiment/`) but no test files on disk; PhaseSequence, Phase, Criterion types have zero coverage | BLOCKED (spec pending) |

### Resolved Gaps

| # | Description | Resolution Date |
|---|---|---|
| R-1 | Measurement annotator coverage | 2026-04-14 — 29 parsing + 36 error + 4 program-level cases |
| R-2 | Multi-error recovery | 2026-04-14 — 8 multi-error cases (parse + lex + semantic + mixed) |
| R-3 | Reinforcement Delay error codes | 2026-04-14 — `RD_TIME_UNIT_REQUIRED`, `RD_NEGATIVE_VALUE`, `RD_LARGE_DELAY` |
| R-4 | Core-Stateful error codes (Pctl/Adj/Interlock) | 2026-04-14 — 54 error/warning cases |
| R-5 | Core-Trial-Based error codes (MTS) | 2026-04-14 — 39 error/warning cases |
| R-6 | T-τ representation errors | 2026-04-14 — 7 error cases + 3 ratio-domain errors |

---

## §8. Error Code Summary

| Layer | Error Codes | Warning Codes | All Tested |
|---|---|---|---|
| Core (Parse) | 11 | — | ✅ |
| Core (Semantic) | 42 | 8 | ✅ |
| Core-Stateful | 16 | 9 | ✅ |
| Core-Trial-Based | 11 | 6 | ✅ |
| Annotations | 34 | — | ✅ |
| Representations (T-τ) | 7 | — | ✅ |
| **Total** | **121** | **23** | **✅ 100%** |

---

*Last updated: 2026-04-14*
*References: grammar.ebnf (Core), grammar.ebnf (Core-Stateful), grammar.ebnf (Core-Trial-Based)*
