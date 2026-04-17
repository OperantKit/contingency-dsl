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
| **Foundations** | 0 | 0 | Forthcoming (paradigm-neutral lexical fixtures) |
| **Operant** | 19 | 420+ | ✅ Primary coverage |
| **Operant-Stateful** | 4 | 92 | ✅ Full coverage |
| **Operant-Trial-Based** | 3 | 84 | ✅ Full coverage |
| **Respondent** | 0 | 0 | Forthcoming (Tier A primitive fixtures) |
| **Composed** | 0 | 0 | Forthcoming (CER / PIT / autoshape / omission / two-process) |
| **Experiment** | 4 | 35 | ✅ Full coverage |
| **Annotations** | 8 | 140+ | ✅ Full coverage (incl. respondent-annotator extension stub) |
| **Representations (T-τ)** | 4 | 33 | ✅ Full coverage |
| **Total** | **42+** | **800+** | |

---

## §1. Grammar Production Coverage

### §1.1 Operant Grammar (`schema/operant/grammar.ebnf`)

| # | Production | Test File(s) | Test Case IDs | Status |
|---|---|---|---|---|
| 1 | `program` | `operant/program.json` | `program_lh_default`, `program_lh_and_bindings`, `program_minimal`, `program_comments_and_whitespace` | ✅ 4 cases |
| 2 | `program_annotation` | `annotations/program-level.json` | `program_annotations_subject_only`, `program_annotations_full_preamble`, `program_annotations_with_schedule_annotations`, `program_annotations_all_four_jeab_categories` | ✅ 4 cases |
| 3 | `param_decl` | `operant/program.json`, `operant/limited_hold.json`, `operant/reinforcement_delay.json` | `program_lh_default`, `program_lh_and_bindings`, `lh_alias_param_decl`, `rd_param_decl_ms`, `rd_param_decl_s`, `rd_param_decl_zero`, `rd_param_decl_alias`, `rd_with_other_param_decls` | ✅ |
| 4 | `param_name` | `operant/program.json`, `operant/compound-kw-aliases.json`, `operant/reinforcement_delay.json` | LH, COD, FRCO, BO, RD + verbose aliases | ✅ All 10 variants |
| 5 | `binding` | `operant/binding.json` | `let_simple` .. `let_in_second_order_both` | ✅ 9 cases |
| 6 | `schedule` | (ubiquitous) | — | ✅ Implicit |
| 7 | `base_schedule` | (tested via atomic, compound, modifier, ident, paren) | — | ✅ Transitive |
| 8 | `atomic_or_second` | `operant/atomic.json`, `operant/second_order.json` | 32 + 5 = 37 cases | ✅ |
| 9 | `parametric_atomic` | `operant/atomic.json` | `atomic_fr5` .. `atomic_ri_space_sec` (24 valid variants), all 3×3 dist×domain | ✅ Full grid |
| 10 | `simple_schedule` | `operant/second_order.json` | `second_order_fr5_fi30` .. `second_order_rr_ft` | ✅ 5 cases |
| 11 | `dist` | `operant/atomic.json` | F: `atomic_fr5`; V: `atomic_vi60s`; R: `atomic_rr20` | ✅ F, V, R |
| 12 | `domain` | `operant/atomic.json` | R: `atomic_fr5`; I: `atomic_vi60s`; T: `atomic_ft30s` | ✅ R, I, T |
| 13 | `ws` | (implicit in all files) | — | ⚠️ Incidental |
| 14 | `value` | `operant/atomic.json`, `operant/boundary-values.json` | integer, float, with/without unit | ✅ |
| 15 | `time_sep` | `operant/atomic.json` | `atomic_vi_hyphen_s` (hyphen), `atomic_vi_space_s` (space), `atomic_vi60s` (compact) | ✅ All 3 forms |
| 16 | `time_unit` | `operant/atomic.json`, `operant/warnings.json` | `atomic_vi60s` (s), `atomic_vi_ms` (ms), `atomic_fi_min` (min), `atomic_fi_hyphen_sec` (sec→s normalization) | ✅ s, sec, ms, min |
| 17 | `number` | `operant/atomic.json`, `operant/boundary-values.json` | integer: `atomic_fr5`; float: `atomic_fr_float`; large: `boundary_fr_large` | ✅ |
| 18 | `ident` | `operant/binding.json` | `let_simple`, `let_underscore_name` | ✅ |
| 19 | `reserved` | `operant/errors.json` | `error_reserved_word_as_ident`, `error_reserved_pr_step_hodos`, `error_reserved_pr_param_start`, `error_reserved_pr_step_linear`, `error_reserved_pr_step_exponential`, `error_reserved_pr_step_geometric`, `error_reserved_pr_param_increment` | ✅ 7 cases |
| 20 | `compound` | `operant/compound.json` | 34 cases | ✅ |
| 21 | `combinator` | `operant/compound.json` | Conc: `conc_vi_vi`; Alt: `alt_fr_fi`; Conj: `conj_fr_fi`; Chain: `chain_fr_fi`; Tand: `tand_vr_drl`; Mult: `mult_fr_ext`; Mix: `mix_fr_fr`; Overlay: `overlay_basic` | ✅ All 8 |
| 22 | `interpolate` | `operant/interpolated.json` | `interpolate_basic` .. `interpolate_with_let_binding` | ✅ 7 cases |
| 23 | `interp_kw_arg` | `operant/interpolated.json`, `operant/errors.json` | count: `interpolate_basic`; onset: `interpolate_with_onset` | ✅ Both keywords |
| 24 | `arg_list` | `operant/compound.json`, `operant/compound-kw-aliases.json` | positional-only + keyword-mixed | ✅ |
| 25 | `positional_args` | `operant/compound.json` | 2-component: `conc_vi_vi`; 3: `conc_three_components`; 5: `conc_five_components` | ✅ |
| 26 | `keyword_arg` | `operant/compound.json`, `operant/compound-kw-aliases.json` | scalar + directional + overlay_kw_arg forms | ✅ |
| 27 | `scalar_kw_arg` | `operant/compound.json`, `operant/compound-kw-aliases.json` | `conc_vi_vi_with_cod`, `conc_with_frco`, `mult_fr_ext_with_bo` | ✅ |
| 28 | `directional_kw_arg` | `operant/compound.json`, `operant/semantic-violations-extended.json`, `operant/warnings.json` | `conc_directional_cod_two` .. `conc_directional_cod_overrides_param_decl` | ✅ 7 cases |
| 29 | `dir_ref` | `operant/compound.json`, `operant/errors.json` | numeric: `conc_directional_cod_two`; ident: `conc_directional_cod_let_bindings` | ✅ Both forms |
| 30 | `kw_name` | `operant/compound.json`, `operant/compound-kw-aliases.json` | COD, ChangeoverDelay, FRCO, FixedRatioChangeover, BO, Blackout | ✅ All 6 |
| 30a | `overlay_kw_arg` | `operant/compound.json` | `overlay_target_changeover`, `overlay_target_all_explicit` | ✅ 2 cases |
| 30b | `target_value` | `operant/compound.json` | changeover: `overlay_target_changeover`; all: `overlay_target_all_explicit` | ✅ Both values |
| 30c | `punish_directive` | `operant/compound.json` | `conc_punish_directional`, `conc_punish_changeover`, `conc_punish_component`, `conc_punish_ident` | ✅ 4 cases |
| 30d | `punish_target` | `operant/compound.json` | changeover: `conc_punish_changeover`; directional: `conc_punish_directional`; single dir_ref: `conc_punish_component` | ✅ All 3 forms |
| 31 | `modifier` | `operant/modifier.json` | 23 cases | ✅ |
| 32 | `dr_mod` | `operant/modifier.json` | `drl_5s`, `drh_2s`, `dro_10s`, `drl_space` | ✅ DRL, DRH, DRO |
| 33 | `pr_mod` | `operant/modifier.json` | `pr_hodos`, `pr_linear`, `pr_exponential`, `pr_geometric`, `pr_geometric_defaults`, `pr_shorthand_5`, `pr_shorthand_1`, `pr_shorthand_no_space` | ✅ Both forms |
| 34 | `pr_opts` | `operant/modifier.json` | `pr_hodos` (no params), `pr_linear` (with params), `pr_geometric` (with params) | ✅ |
| 35 | `pr_step` | `operant/modifier.json` | `pr_hodos`, `pr_linear`, `pr_exponential`, `pr_geometric` | ✅ All 4 |
| 36 | `pr_param` | `operant/modifier.json` | start + increment in `pr_linear`; start + ratio in `pr_geometric` | ✅ |
| 37 | `repeat` | `operant/modifier.json`, `operant/algebra.json` | `repeat_3_fr10`, `repeat_nested`, `repeat_1_identity`, `repeat_identity`, `repeat_additive_decomposition` | ✅ |
| 38 | `lag_mod` | `operant/modifier.json` | `lag_simple_shorthand`, `lag_simple_no_space`, `lag_zero_equiv_crf`, `lag_parenthesized_n_only`, `lag_parenthesized_with_length`, `lag_page_neuringer_exp3`, `lag_in_mult_schedule`, `lag_let_binding` | ✅ 8 cases |
| 39 | `lag_kw_arg` | `operant/modifier.json`, `operant/errors.json` | `lag_parenthesized_with_length`, `lag_page_neuringer_exp3` | ✅ |
| 40 | `aversive_schedule` | `operant/aversive.json` | 14 cases | ✅ |
| 41 | `sidman_avoidance` | `operant/aversive.json` | `sidman_basic` .. `sidman_let_binding` | ✅ 7 cases |
| 42 | `sidman_arg` | `operant/aversive.json`, `operant/errors.json` | SSI, RSI, verbose aliases | ✅ |
| 43 | `sidman_kw` | `operant/aversive.json` | SSI: `sidman_basic`; ShockShockInterval: `sidman_verbose_alias`; RSI: `sidman_basic`; ResponseShockInterval: `sidman_verbose_alias` | ✅ All 4 |
| 44 | `discriminated_avoidance` | `operant/aversive.json` | `da_basic_escape` .. `da_param_order_swapped` | ✅ 7 cases |
| 45 | `da_arg` | `operant/aversive.json`, `operant/errors.json` | temporal + mode args | ✅ |
| 46 | `da_temporal_kw` | `operant/aversive.json` | CSUSInterval, ITI, ShockDuration, MaxShock | ✅ All 4 |
| 47 | `da_mode` | `operant/aversive.json`, `operant/errors.json` | `da_basic_escape` (escape), `da_basic_fixed` (fixed) | ✅ Both |
| 48 | `annotated_schedule` | `annotations/measurement.json`, `annotations/program-level.json` | 29 + 4 = 33 cases | ✅ |
| 49 | `annotation` | `annotations/measurement.json`, `annotations/program-level.json` | — | ✅ |
| 50 | `annotation_args` | `annotations/measurement.json` | positional + keyword-only forms | ✅ |
| 51 | `annotation_kv` | `annotations/measurement.json` | `measurement_session_end_first` etc. | ✅ |
| 52 | `annotation_val` | `annotations/measurement.json` | string, time_value, number | ✅ All 3 types |
| 53 | `time_value` (annotation) | `annotations/measurement.json` | `measurement_session_end_first` | ✅ |
| 54 | `string_literal` | `annotations/measurement.json`, `annotations/program-level.json` | `measurement_full_preamble`, `program_annotations_full_preamble` | ✅ |

**Summary:** 54 productions; 52 with dedicated coverage, 1 implicit (`ws`), 1 transitive (`base_schedule`).

### §1.1b Experiment Layer Grammar (`schema/operant/grammar.ebnf`, experiment additions)

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
| E12 | `progressive_decl` | `experiment/progressive-training.json` | `progressive_single_variable`, `progressive_fixed_sessions`, `progressive_multi_variable`, `progressive_mixed_with_phases` | ✅ 4 cases |
| E13 | `progressive_steps` | `experiment/progressive-training.json`, `experiment/errors.json` | single: `progressive_single_variable`; multi: `progressive_multi_variable`; empty: `error_progressive_empty_steps` | ✅ |
| E14 | `number_list` | `experiment/progressive-training.json` | 5 elements: `progressive_single_variable`; 7: `progressive_fixed_sessions`; 4: `progressive_multi_variable` | ✅ |
| E15 | `shaping_decl` (Skinner) | `experiment/shaping.json` | `shaping_artful_minimal`, `shaping_artful_with_approximations`, `shaping_artful_with_custom_criterion`, `shaping_percentile_force`, `shaping_staged`, `shaping_mixed_with_other_phases` | ✅ 6 cases |
| E16 | `shaping_meta` | `experiment/shaping.json` | target: `shaping_artful_minimal`; method+approximations: `shaping_artful_with_approximations`; dimension+percentile_*: `shaping_percentile_force`; stages: `shaping_staged` | ✅ |

**Summary:** 14 productions; all with dedicated coverage.

### §1.2 Operant-Stateful Grammar (`schema/operant/stateful/grammar.ebnf`)

| # | Production | Test File(s) | Test Case IDs | Status |
|---|---|---|---|---|
| S1 | `pctl_mod` | `operant/stateful/percentile.json` | `pctl_minimal` .. `pctl_with_annotations` | ✅ 10 cases |
| S2 | `pctl_target` | `operant/stateful/percentile.json` | IRT: `pctl_minimal`; force: `pctl_force_dimension`; duration: `pctl_duration_shaping`; rate: `pctl_rate_target`; latency: `pctl_fully_specified` | ✅ All 5 |
| S3 | `pctl_rank` | `operant/stateful/percentile.json`, `operant/stateful/errors.json` | valid: `pctl_minimal`; boundary: `pctl_warn_extreme_rank_zero`, `pctl_warn_extreme_rank_100` | ✅ |
| S4 | `pctl_kw_arg` | `operant/stateful/percentile.json` | window: `pctl_with_window`; dir: `pctl_fully_specified` | ✅ Both |
| S5 | `pctl_dir` | `operant/stateful/percentile.json` | below (default): `pctl_minimal`; above: `pctl_fully_specified` | ✅ Both |
| S6 | `adj_schedule` | `operant/stateful/adjusting.json` | `adj_delay_minimal` .. `adj_with_annotations` | ✅ 16 cases |
| S7 | `adj_target` | `operant/stateful/adjusting.json` | delay: `adj_delay_minimal`; ratio: `adj_ratio_minimal`; amount: `adj_amount_minimal` | ✅ All 3 |
| S8 | `adj_kw_arg` | `operant/stateful/adjusting.json` | start, step, min, max | ✅ All 4 |
| S9 | `interlock_schedule` | `operant/stateful/interlocking.json` | `interlock_standard` .. `interlock_with_annotations` | ✅ 12 cases |
| S10 | `interlock_kw_arg` | `operant/stateful/interlocking.json` | R0: `interlock_standard`; T: `interlock_standard` | ✅ Both |

**Summary:** 10 productions; all with dedicated coverage.

### §1.3 Operant-Trial-Based Grammar (`schema/operant/trial-based/grammar.ebnf`)

| # | Production | Test File(s) | Test Case IDs | Status |
|---|---|---|---|---|
| T1 | `trial_based_schedule` | `operant/trial-based/mts.json`, `operant/trial-based/gonogo.json` | (transitive via mts_schedule, gonogo_schedule) | ✅ Both branches |
| T2 | `mts_schedule` | `operant/trial-based/mts.json` | `mts_minimal` .. `mts_with_limited_hold` | ✅ 23 cases |
| T3 | `mts_kw_arg` | `operant/trial-based/mts.json` | comparisons, consequence, incorrect, ITI, type | ✅ All 5 |
| T4 | `mts_type` | `operant/trial-based/mts.json` | identity: `mts_fully_specified`; arbitrary: `mts_arbitrary_explicit` | ✅ Both |
| T5 | `gonogo_schedule` | `operant/trial-based/gonogo.json` | `gonogo_minimal` .. `gonogo_with_limited_hold_kwarg` | ✅ 22 cases |
| T6 | `gonogo_kw_arg` | `operant/trial-based/gonogo.json` | responseWindow, consequence, incorrect, falseAlarm, ITI, LH | ✅ All 6 |

**Summary:** 6 productions; all with dedicated coverage.

---

## §2. Semantic Rule Coverage

| Rule | Spec Reference | Test File(s) | Test Case IDs | Status |
|---|---|---|---|---|
| LH propagation R1–R6 | theory.md §1.6.1 | `operant/lh_propagation.json` | 27 cases (14 valid + 13 resolved ASTs) | ✅ |
| Algebraic equivalences | theory.md §2.2, Theorems 1–8 | `operant/algebra.json` | 25 cases: identity (R1–R5, R10), annihilator (R6–R9), associativity (R13–R17), commutativity, non-distributivity, Repeat decomposition | ✅ |
| Let-binding expansion | grammar.ebnf §5 | `operant/binding.json` | `let_simple` .. `let_in_second_order_both` (9 cases) | ✅ |
| Repeat desugaring | theory.md §2.2.3 | `operant/algebra.json` | `repeat_identity`, `repeat_additive_decomposition` | ✅ |
| Value range constraints | grammar.ebnf §46–§62 | `operant/boundary-values.json` | 54 cases (all atomic/DR/PR/LH/Repeat/FRCO/SecondOrder boundary values) | ✅ |
| SecondOrder semantics | theory.md §2.11.1 | `operant/second_order.json`, `operant/errors.json` | 5 basic parsing + 4 compound-unit rejection cases | ✅ |
| Annotation measurement parsing | annotations spec | `annotations/measurement.json` | 29 cases (all 10 keywords) | ✅ |
| Annotation measurement errors | annotations spec | `annotations/errors.json` | 36 cases (incl. 2 cross-annotation) | ✅ |
| Cross-annotation composition | design-philosophy.md §4 | `annotations/program-level.json` | `program_annotations_all_four_jeab_categories` | ✅ |
| T-τ representation conversion | representations/t-tau.md | `representations/t-tau/` | 33 cases total (to: 11, from: 9, roundtrip: 6, errors: 7) | ✅ |
| Pctl percentile criterion | operant/stateful/grammar.md | `operant/stateful/percentile.json` | 10 valid cases | ✅ |
| Adj adjusting mechanism | operant/stateful/grammar.md | `operant/stateful/adjusting.json` | 16 valid cases | ✅ |
| Interlocking R(t) formula | operant/stateful/grammar.md | `operant/stateful/interlocking.json` | 12 valid cases | ✅ |
| MTS trial structure | operant/trial-based/grammar.md | `operant/trial-based/mts.json` | 23 valid cases | ✅ |
| MTS + combinator interaction | operant/trial-based/grammar.md | `operant/trial-based/mts.json` | `mts_in_mult`, `mts_in_chain`, `mts_mult_training_test` | ✅ |
| MTS + LH compatibility | operant/trial-based/grammar.ebnf §LH | `operant/trial-based/mts.json` | `mts_with_limited_hold` | ✅ |
| Trial-based modifier incompatibility | operant/trial-based/grammar.ebnf | `operant/trial-based/errors.json` | `mts_error_drl_modifier` .. `mts_error_lag_modifier` | ✅ 5 cases |
| GoNoGo trial structure | operant/trial-based/grammar.ebnf §2 | `operant/trial-based/gonogo.json` | 22 cases (10 valid + 2 boundary + 2 LH + 8 error) | ✅ |
| GoNoGo + combinator interaction | operant/trial-based/grammar.ebnf §2 | `operant/trial-based/gonogo.json` | `gonogo_in_mult`, `gonogo_in_chain`, `gonogo_mult_training_probe` | ✅ |
| GoNoGo + LH redundancy | operant/trial-based/grammar.ebnf §LH | `operant/trial-based/gonogo.json` | `gonogo_with_limited_hold`, `gonogo_with_limited_hold_kwarg` | ✅ 2 cases |
| GoNoGo SDT-style asymmetric consequence | operant/trial-based/grammar.ebnf §2 | `operant/trial-based/gonogo.json` | `gonogo_sdt_style` | ✅ |

---

## §3. Error Code Coverage

### §3.1 Operant Parse Errors

| Error Code | Type | Test File(s) | Test Case IDs | Status |
|---|---|---|---|---|
| `UNEXPECTED_EOF` | ParseError | `operant/errors.json` | `error_empty_input` | ✅ |
| `UNEXPECTED_CHARACTER` | LexError | `operant/errors.json` | `error_invalid_char`, `multi_error_missing_value_and_unexpected_char`, `multi_error_lex_errors_multiline`, `multi_error_three_parse_errors` | ✅ 4 cases |
| `UNEXPECTED_TOKEN` | ParseError | `operant/errors.json`, `operant/semantic-violations-extended.json` | `error_paren_as_second_order`, `error_da_missing_all` | ✅ 2 cases |
| `INSUFFICIENT_COMPONENTS` | ParseError | `operant/errors.json`, `operant/semantic-violations-extended.json` | `error_compound_one_component`, `error_interpolate_one_component`, `error_overlay_one_component` | ✅ 3 cases |
| `EXPECTED_VALUE` | ParseError | `operant/errors.json`, `operant/boundary-values.json` | `error_missing_value`, `boundary_fr_negative`, `boundary_vi_negative`, `boundary_drl_negative`, `error_atomic_negative_value`, `error_atomic_negative_interval`, `error_lh_negative`, `error_lag_missing_positional_n`, `multi_error_two_missing_values`, `multi_error_missing_value_and_unexpected_char`, `multi_error_three_parse_errors` | ✅ 11 cases |
| `EXPECTED_RPAREN` | ParseError | `operant/errors.json` | `error_unclosed_paren`, `multi_error_three_parse_errors` | ✅ 2 cases |
| `EXPECTED_COMMA_OR_RPAREN` | ParseError | `operant/errors.json` | `error_missing_comma` | ✅ |
| `EXPECTED_LPAREN_OR_NUMBER` | ParseError | `operant/errors.json` | `error_pr_bare` | ✅ |
| `KEYWORD_BEFORE_POSITIONAL` | ParseError | `operant/errors.json` | `error_keyword_before_positional` | ✅ |
| `RESERVED_WORD` | ParseError | `operant/errors.json` | `error_reserved_word_as_ident`, `error_reserved_pr_step_hodos`, `error_reserved_pr_param_start`, `error_reserved_pr_step_linear`, `error_reserved_pr_step_exponential`, `error_reserved_pr_step_geometric`, `error_reserved_pr_param_increment` | ✅ 7 cases |
| `INVALID_SECOND_ORDER_OVERALL` | ParseError | `operant/errors.json` | `error_second_order_ext_overall`, `error_crf_second_order_overall` | ✅ 2 cases |

### §3.2 Operant Semantic Errors — Binding / Variable

| Error Code | Type | Test File(s) | Test Case IDs | Status |
|---|---|---|---|---|
| `UNDEFINED_IDENTIFIER` | SemanticError | `operant/errors.json` | `error_undefined_ident` | ✅ |
| `FORWARD_REFERENCE` | SemanticError | `operant/errors.json` | `error_forward_reference`, `error_self_referential_binding` | ✅ 2 cases |
| `DUPLICATE_BINDING` | SemanticError | `operant/errors.json` | `error_shadowing`, `multi_error_semantic_binding_and_keyword` | ✅ 2 cases |

### §3.3 Operant Semantic Errors — Value Range

| Error Code | Type | Test File(s) | Test Case IDs | Status |
|---|---|---|---|---|
| `ATOMIC_NONPOSITIVE_VALUE` | SemanticError | `operant/errors.json`, `operant/boundary-values.json` | `error_atomic_nonpositive_ratio`, `error_atomic_nonpositive_interval`, `boundary_fr_zero` .. `boundary_rt_zero` (10), `boundary_fr_zero_compact`, `boundary_second_order_fr0`, `multi_error_semantic_nonpositive_values`, `multi_error_semantic_mixed_codes`, `multi_error_semantic_nonpositive_and_duplicate_kw` | ✅ 17 cases |
| `DR_NONPOSITIVE_VALUE` | SemanticError | `operant/errors.json`, `operant/boundary-values.json` | `error_dr_nonpositive`, `boundary_drl_zero`, `boundary_drh_zero`, `boundary_dro_zero`, `multi_error_semantic_mixed_codes` | ✅ 5 cases |
| `PR_NONPOSITIVE_VALUE` | SemanticError | `operant/errors.json`, `operant/boundary-values.json` | `error_pr_nonpositive_shorthand`, `error_pr_nonpositive_start`, `error_pr_nonpositive_increment`, `boundary_pr_shorthand_zero`, `boundary_pr_linear_zero_start`, `boundary_pr_linear_zero_increment`, `boundary_pr_geometric_zero_start` | ✅ 7 cases |
| `PR_NON_INTEGER_VALUE` | SemanticError | `operant/errors.json`, `operant/boundary-values.json` | `error_pr_non_integer_start`, `error_pr_non_integer_increment`, `error_pr_non_integer_shorthand`, `boundary_pr_fractional_shorthand`, `boundary_pr_fractional_start`, `boundary_pr_fractional_increment` | ✅ 6 cases |
| `LH_NONPOSITIVE_VALUE` | SemanticError | `operant/errors.json`, `operant/boundary-values.json` | `error_lh_nonpositive_expression`, `error_lh_nonpositive_expression_ms`, `error_lh_nonpositive_program_level`, `boundary_lh_zero` | ✅ 4 cases |
| `FRCO_NONPOSITIVE_VALUE` | SemanticError | `operant/errors.json`, `operant/boundary-values.json` | `error_frco_nonpositive`, `boundary_conc_frco_zero` | ✅ 2 cases |
| `PR_GEOMETRIC_RATIO_NOT_PROGRESSIVE` | SemanticError | `operant/boundary-values.json` | `boundary_pr_geometric_ratio_one`, `boundary_pr_geometric_ratio_below_one` | ✅ 2 cases |
| `REPEAT_ZERO_COUNT` | SemanticError | `operant/errors.json` | `error_repeat_zero` | ✅ |
| `REPEAT_NON_INTEGER_COUNT` | SemanticError | `operant/errors.json`, `operant/boundary-values.json` | `error_repeat_non_integer`, `boundary_repeat_fractional`, `boundary_repeat_fractional_large` | ✅ 3 cases |

### §3.4 Operant Semantic Errors — Compound / Combinator

| Error Code | Type | Test File(s) | Test Case IDs | Status |
|---|---|---|---|---|
| `INVALID_KEYWORD_ARG` | SemanticError | `operant/errors.json`, `operant/semantic-violations-extended.json` | `error_cod_on_chain`, `error_cod_on_alt`, `error_frco_on_tand`, `error_bo_on_conc`, `error_bo_on_chain`, `error_bo_on_tand`, `error_bo_on_alt`, `error_overlay_keyword_arg`, `error_directional_frco`, `error_directional_bo`, `error_directional_cod_on_chain`, + 18 extended cases | ✅ 29 cases |
| `DUPLICATE_KEYWORD_ARG` | SemanticError | `operant/errors.json`, `operant/semantic-violations-extended.json` | `error_duplicate_keyword`, `error_duplicate_bo`, + 3 alias-collision cases, `multi_error_semantic_nonpositive_and_duplicate_kw`, `multi_error_semantic_binding_and_keyword` | ✅ 7 cases |
| `OVERLAY_REQUIRES_TWO` | SemanticError | `operant/errors.json` | `error_overlay_three_components` | ✅ |
| `INVALID_OVERLAY_TARGET` | SemanticError | `operant/compound.json` | `error_non_overlay_target` | ✅ |
| `TARGET_REQUIRES_CONC` | SemanticError | `operant/compound.json` | `error_overlay_target_non_conc` | ✅ |
| `EXPECTED_TARGET_VALUE` | ParseError | `operant/compound.json` | `error_overlay_target_unknown` | ✅ |
| `INVALID_PUNISH_COMBINATOR` | SemanticError | `operant/compound.json` | `error_punish_non_conc` | ✅ |
| `PUNISH_SELF_REFERENCE` | SemanticError | `operant/compound.json` | `error_punish_self_ref` | ✅ |
| `DUPLICATE_PUNISH_DIRECTIVE` | SemanticError | `operant/compound.json` | `error_punish_duplicate` | ✅ |
| `PUNISH_TARGET_CONFLICT` | SemanticError | `operant/compound.json` | `error_punish_target_conflict` | ✅ |
| `INTERPOLATE_REQUIRES_TWO` | SemanticError | `operant/errors.json`, `operant/semantic-violations-extended.json` | `error_interpolate_three_components`, `error_interp_alias_three_components` | ✅ 2 cases |
| `MISSING_INTERPOLATE_COUNT` | SemanticError | `operant/errors.json`, `operant/semantic-violations-extended.json` | `error_interpolate_missing_count`, `error_interp_alias_missing_count` | ✅ 2 cases |
| `INTERPOLATE_NONPOSITIVE_COUNT` | SemanticError | `operant/errors.json`, `operant/semantic-violations-extended.json` | `error_interpolate_count_zero`, `error_interpolate_count_negative` | ✅ 2 cases |
| `INTERPOLATE_COUNT_TIME_UNIT` | SemanticError | `operant/errors.json` | `error_interpolate_count_with_time_unit` | ✅ |
| `INTERPOLATE_ONSET_TIME_UNIT_REQUIRED` | SemanticError | `operant/errors.json` | `error_interpolate_onset_no_time_unit` | ✅ |
| `INTERPOLATE_NONPOSITIVE_ONSET` | SemanticError | `operant/errors.json`, `operant/semantic-violations-extended.json` | `error_interpolate_onset_nonpositive`, `error_interpolate_onset_negative` | ✅ 2 cases |
| `DUPLICATE_INTERPOLATE_KW_ARG` | SemanticError | `operant/errors.json`, `operant/semantic-violations-extended.json` | `error_interpolate_duplicate_count`, `error_interpolate_duplicate_onset` | ✅ 2 cases |
| `INVALID_SECOND_ORDER_UNIT` | SemanticError | `operant/errors.json` | `error_second_order_chain_unit`, `error_second_order_tand_unit`, `error_second_order_conc_unit`, `error_second_order_mult_unit` | ✅ 4 cases |

### §3.5 Operant Semantic Errors — Directional COD

| Error Code | Type | Test File(s) | Test Case IDs | Status |
|---|---|---|---|---|
| `DIRECTIONAL_SELF_REFERENCE` | SemanticError | `operant/errors.json` | `error_directional_cod_self_reference` | ✅ |
| `DIRECTIONAL_INDEX_OUT_OF_RANGE` | SemanticError | `operant/errors.json`, `operant/compound.json` | `error_directional_cod_index_out_of_range`, `error_punish_index_oob` | ✅ 2 cases |
| `DIRECTIONAL_IDENT_NOT_FOUND` | SemanticError | `operant/errors.json` | `error_directional_cod_ident_not_found` | ✅ |
| `DUPLICATE_DIRECTIONAL_KW` | SemanticError | `operant/errors.json` | `error_directional_cod_duplicate` | ✅ |
| `INVALID_DIRECTIONAL_KW` | SemanticError | `operant/errors.json` | `error_directional_frco`, `error_directional_bo` | ✅ 2 cases |

### §3.6 Operant Semantic Errors — Sidman Avoidance

| Error Code | Type | Test File(s) | Test Case IDs | Status |
|---|---|---|---|---|
| `MISSING_SIDMAN_PARAM` | SemanticError | `operant/errors.json`, `operant/semantic-violations-extended.json` | `error_sidman_missing_rsi`, `error_sidman_missing_ssi`, `error_sidman_verbose_alias_missing_rsi` | ✅ 3 cases |
| `SIDMAN_TIME_UNIT_REQUIRED` | SemanticError | `operant/errors.json`, `operant/semantic-violations-extended.json` | `error_sidman_no_time_unit`, `error_sidman_mixed_time_unit` | ✅ 2 cases |
| `SIDMAN_NONPOSITIVE_PARAM` | SemanticError | `operant/errors.json`, `operant/semantic-violations-extended.json` | `error_sidman_zero_ssi`, `error_sidman_zero_rsi` | ✅ 2 cases |
| `DUPLICATE_SIDMAN_PARAM` | SemanticError | `operant/errors.json`, `operant/semantic-violations-extended.json` | `error_sidman_duplicate_ssi`, `error_sidman_duplicate_alias`, `error_sidman_duplicate_rsi_alias` | ✅ 3 cases |

### §3.7 Operant Semantic Errors — Discriminated Avoidance

| Error Code | Type | Test File(s) | Test Case IDs | Status |
|---|---|---|---|---|
| `MISSING_DA_PARAM` | SemanticError | `operant/errors.json`, `operant/semantic-violations-extended.json` | `error_da_missing_mode`, `error_da_missing_csus`, `error_da_missing_iti`, `error_discrimav_alias_missing_mode` | ✅ 4 cases |
| `DA_TIME_UNIT_REQUIRED` | SemanticError | `operant/errors.json` | `error_da_no_time_unit` | ✅ |
| `DA_NONPOSITIVE_PARAM` | SemanticError | `operant/errors.json` | `error_da_nonpositive_csus` | ✅ |
| `DA_INVALID_MODE` | SemanticError | `operant/errors.json` | `error_da_invalid_mode` | ✅ |
| `MISSING_SHOCK_DURATION` | SemanticError | `operant/errors.json` | `error_da_fixed_missing_shock_duration` | ✅ |
| `INVALID_PARAM_FOR_MODE` | SemanticError | `operant/errors.json` | `error_da_fixed_with_max_shock`, `error_da_escape_with_shock_duration` | ✅ 2 cases |
| `DA_ITI_TOO_SHORT` | SemanticError | `operant/errors.json`, `operant/semantic-violations-extended.json` | `error_da_iti_too_short`, `error_da_iti_equals_csus` | ✅ 2 cases |
| `DUPLICATE_DA_PARAM` | SemanticError | `operant/errors.json` | `error_da_duplicate_param` | ✅ |

### §3.8 Operant Semantic Errors — Lag

| Error Code | Type | Test File(s) | Test Case IDs | Status |
|---|---|---|---|---|
| `LAG_INVALID_N_VALUE` | SemanticError | `operant/errors.json` | `error_lag_negative_n`, `error_lag_non_integer_n` | ✅ 2 cases |
| `LAG_UNEXPECTED_TIME_UNIT` | SemanticError | `operant/errors.json` | `error_lag_time_unit` | ✅ |
| `LAG_INVALID_LENGTH` | SemanticError | `operant/errors.json` | `error_lag_length_zero`, `error_lag_length_negative` | ✅ 2 cases |
| `DUPLICATE_LAG_KW_ARG` | SemanticError | `operant/errors.json` | `error_lag_duplicate_kw` | ✅ |

### §3.9 Operant Semantic Errors — Reinforcement Delay

| Error Code | Type | Test File(s) | Test Case IDs | Status |
|---|---|---|---|---|
| `RD_TIME_UNIT_REQUIRED` | SemanticError | `operant/reinforcement_delay.json` | `rd_error_no_time_unit` | ✅ |
| `RD_NEGATIVE_VALUE` | SemanticError | `operant/reinforcement_delay.json` | `rd_error_negative` | ✅ |

### §3.10 Operant Semantic Errors — Multi-Error Recovery

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

### §3.11 Operant-Stateful Semantic Errors — Percentile

| Error Code | Type | Test File(s) | Test Case IDs | Status |
|---|---|---|---|---|
| `PCTL_INVALID_RANK` | SemanticError | `operant/stateful/errors.json` | `pctl_error_rank_out_of_range`, `pctl_error_negative_rank`, `pctl_error_fractional_rank` | ✅ 3 cases |
| `PCTL_INVALID_WINDOW` | SemanticError | `operant/stateful/errors.json` | `pctl_error_window_zero`, `pctl_error_window_negative` | ✅ 2 cases |
| `PCTL_UNKNOWN_TARGET` | SemanticError | `operant/stateful/errors.json` | `pctl_error_unknown_target` | ✅ |
| `PCTL_INVALID_DIR` | SemanticError | `operant/stateful/errors.json` | `pctl_error_invalid_dir` | ✅ |
| `PCTL_UNEXPECTED_TIME_UNIT` | SemanticError | `operant/stateful/errors.json` | `pctl_error_rank_with_time_unit` | ✅ |
| `DUPLICATE_PCTL_KW_ARG` | SemanticError | `operant/stateful/errors.json` | `pctl_error_duplicate_window`, `pctl_error_duplicate_dir` | ✅ 2 cases |

### §3.12 Operant-Stateful Semantic Errors — Adjusting

| Error Code | Type | Test File(s) | Test Case IDs | Status |
|---|---|---|---|---|
| `ADJ_MISSING_PARAM` | SemanticError | `operant/stateful/errors.json` | `adj_error_missing_start`, `adj_error_missing_step`, `adj_error_no_args` | ✅ 3 cases |
| `ADJ_UNKNOWN_TARGET` | SemanticError | `operant/stateful/errors.json` | `adj_error_unknown_target` | ✅ |
| `ADJ_NONPOSITIVE_START` | SemanticError | `operant/stateful/errors.json` | `adj_error_nonpositive_start`, `adj_error_negative_start` | ✅ 2 cases |
| `ADJ_NONPOSITIVE_STEP` | SemanticError | `operant/stateful/errors.json` | `adj_error_nonpositive_step` | ✅ |
| `ADJ_TIME_UNIT_REQUIRED` | SemanticError | `operant/stateful/errors.json` | `adj_error_delay_missing_time_unit`, `adj_error_delay_max_missing_time_unit` | ✅ 2 cases |
| `ADJ_UNEXPECTED_TIME_UNIT` | SemanticError | `operant/stateful/errors.json` | `adj_error_ratio_with_time_unit`, `adj_error_amount_with_time_unit` | ✅ 2 cases |
| `ADJ_INVALID_BOUNDS` | SemanticError | `operant/stateful/errors.json` | `adj_error_invalid_bounds` | ✅ |
| `ADJ_START_OUT_OF_BOUNDS` | SemanticError | `operant/stateful/errors.json` | `adj_error_start_out_of_bounds_below`, `adj_error_start_out_of_bounds_above` | ✅ 2 cases |
| `ADJ_RATIO_NOT_INTEGER` | SemanticError | `operant/stateful/errors.json` | `adj_error_ratio_not_integer`, `adj_error_ratio_step_not_integer` | ✅ 2 cases |
| `DUPLICATE_ADJ_KW_ARG` | SemanticError | `operant/stateful/errors.json` | `adj_error_duplicate_start`, `adj_error_duplicate_step` | ✅ 2 cases |

### §3.13 Operant-Stateful Semantic Errors — Interlocking

| Error Code | Type | Test File(s) | Test Case IDs | Status |
|---|---|---|---|---|
| `INTERLOCK_MISSING_PARAM` | SemanticError | `operant/stateful/errors.json` | `interlock_error_missing_R0`, `interlock_error_missing_T`, `interlock_error_no_args` | ✅ 3 cases |
| `INTERLOCK_INVALID_R0` | SemanticError | `operant/stateful/errors.json` | `interlock_error_nonpositive_R0`, `interlock_error_negative_R0`, `interlock_error_fractional_R0` | ✅ 3 cases |
| `INTERLOCK_UNEXPECTED_TIME_UNIT` | SemanticError | `operant/stateful/errors.json` | `interlock_error_R0_with_time_unit` | ✅ |
| `INTERLOCK_NONPOSITIVE_T` | SemanticError | `operant/stateful/errors.json` | `interlock_error_nonpositive_T` | ✅ |
| `INTERLOCK_TIME_UNIT_REQUIRED` | SemanticError | `operant/stateful/errors.json` | `interlock_error_T_missing_time_unit` | ✅ |
| `DUPLICATE_INTERLOCK_KW_ARG` | SemanticError | `operant/stateful/errors.json` | `interlock_error_duplicate_R0` | ✅ |

### §3.14 Operant-Trial-Based Semantic Errors — MTS

| Error Code | Type | Test File(s) | Test Case IDs | Status |
|---|---|---|---|---|
| `MTS_INVALID_COMPARISONS` | SemanticError | `operant/trial-based/errors.json` | `mts_error_comparisons_less_than_2`, `mts_error_comparisons_zero`, `mts_error_comparisons_negative`, `mts_error_comparisons_fractional` | ✅ 4 cases |
| `MTS_COMPARISONS_TIME_UNIT` | SemanticError | `operant/trial-based/errors.json` | `mts_error_comparisons_time_unit` | ✅ |
| `MTS_MISSING_PARAM` | SemanticError | `operant/trial-based/errors.json` | `mts_error_missing_consequence`, `mts_error_missing_iti`, `mts_error_missing_comparisons` | ✅ 3 cases |
| `MTS_NONPOSITIVE_ITI` | SemanticError | `operant/trial-based/errors.json` | `mts_error_iti_zero`, `mts_error_iti_negative` | ✅ 2 cases |
| `MTS_ITI_TIME_UNIT_REQUIRED` | SemanticError | `operant/trial-based/errors.json` | `mts_error_iti_no_time_unit` | ✅ |
| `MTS_INVALID_TYPE` | SemanticError | `operant/trial-based/errors.json` | `mts_error_invalid_type` | ✅ |
| `MTS_INVALID_CONSEQUENCE` | SemanticError | `operant/trial-based/errors.json` | `mts_error_consequence_compound`, `mts_error_consequence_chain` | ✅ 2 cases |
| `MTS_INVALID_INCORRECT` | SemanticError | `operant/trial-based/errors.json` | `mts_error_incorrect_compound` | ✅ |
| `MTS_RECURSIVE_CONSEQUENCE` | SemanticError | `operant/trial-based/errors.json` | `mts_error_consequence_recursive_mts`, `mts_error_incorrect_recursive_mts` | ✅ 2 cases |
| `DUPLICATE_MTS_KW_ARG` | SemanticError | `operant/trial-based/errors.json` | `mts_error_duplicate_comparisons`, `mts_error_duplicate_consequence`, `mts_error_duplicate_iti`, `mts_error_duplicate_type` | ✅ 4 cases |
| `TRIAL_BASED_MODIFIER_INCOMPATIBLE` | SemanticError | `operant/trial-based/errors.json` | `mts_error_drl_modifier`, `mts_error_drh_modifier`, `mts_error_dro_modifier`, `mts_error_pctl_modifier`, `mts_error_lag_modifier` | ✅ 5 cases |

### §3.15 Operant-Trial-Based Semantic Errors — GoNoGo

| Error Code | Type | Test File(s) | Test Case IDs | Status |
|---|---|---|---|---|
| `GONOGO_NONPOSITIVE_RESPONSE_WINDOW` | SemanticError | `operant/trial-based/gonogo.json` | `gonogo_error_responseWindow_zero` | ✅ |
| `GONOGO_RESPONSE_WINDOW_TIME_UNIT_REQUIRED` | SemanticError | `operant/trial-based/gonogo.json` | `gonogo_error_responseWindow_no_unit` | ✅ |
| `MISSING_GONOGO_PARAM` | SemanticError | `operant/trial-based/gonogo.json` | `gonogo_error_missing_responseWindow`, `gonogo_error_missing_consequence` | ✅ 2 cases |
| `GONOGO_NONPOSITIVE_ITI` | SemanticError | `operant/trial-based/gonogo.json` | `gonogo_error_negative_iti` | ✅ |
| `GONOGO_INVALID_CONSEQUENCE` | SemanticError | `operant/trial-based/gonogo.json` | `gonogo_error_compound_consequence` | ✅ |
| `GONOGO_RECURSIVE_CONSEQUENCE` | SemanticError | `operant/trial-based/gonogo.json` | `gonogo_error_recursive_consequence` | ✅ |
| `DUPLICATE_GONOGO_KW_ARG` | SemanticError | `operant/trial-based/gonogo.json` | `gonogo_error_duplicate_kwarg` | ✅ |

### §3.16 Representations — T-τ Errors

| Error Code | Type | Test File(s) | Test Case IDs | Status |
|---|---|---|---|---|
| `TTAU_T_ZERO` | RepresentationError | `representations/t-tau/errors.json` | `error_ttau_T_zero` | ✅ |
| `TTAU_T_NEGATIVE` | RepresentationError | `representations/t-tau/errors.json` | `error_ttau_T_negative` | ✅ |
| `TTAU_TAU_ZERO` | RepresentationError | `representations/t-tau/errors.json` | `error_ttau_tau_zero` | ✅ |
| `TTAU_TAU_EXCEEDS_T` | RepresentationError | `representations/t-tau/errors.json` | `error_ttau_tau_exceeds_T` | ✅ |
| `TO_TTAU_VALUE_ZERO` | RepresentationError | `representations/t-tau/errors.json` | `error_to_ttau_value_zero` | ✅ |
| `FROM_TTAU_RATIO_DOMAIN_ERROR` | RepresentationError | `representations/t-tau/from_ttau.json` | `from_ttau_ratio_domain_error` | ✅ |
| `TO_TTAU_RATIO_DOMAIN_ERROR` | RepresentationError | `representations/t-tau/to_ttau.json` | `to_ttau_fr5_error`, `to_ttau_vr10_error`, `to_ttau_rr20_error` | ✅ 3 cases |

### §3.17 Annotation Errors

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

### §4.1 Operant Warnings

| Warning Code | Test File(s) | Test Case IDs | Status |
|---|---|---|---|
| `MISSING_TIME_UNIT` | `operant/warnings.json`, `operant/atomic.json` | `warn_fi_missing_time_unit`, `warn_vi_missing_time_unit`, `warn_ri_missing_time_unit`, `warn_ft_missing_time_unit`, `warn_vt_missing_time_unit`, `warn_rt_missing_time_unit`, `warn_fi_in_compound_missing_time_unit`, `warn_drl_missing_time_unit`, `warn_drh_missing_time_unit`, `warn_dro_missing_time_unit`, `atomic_fi30_no_unit` .. `atomic_rt15_no_unit` (6 in atomic) | ✅ 16 cases |
| `MISSING_COD` | `operant/warnings.json`, `operant/compound.json`, `operant/binding.json` | `warn_conc_missing_cod_basic`, `conc_vi_vi`, `conc_three_components`, `nested_conc_chain_alt`, `conc_deep_nesting_depth3`, `conc_five_components`, `let_binding_in_compound` | ✅ 7+ cases |
| `RSI_EXCEEDS_SSI` | `operant/warnings.json` | `warn_sidman_rsi_exceeds_ssi` | ✅ |
| `LAG_LARGE_N` | `operant/warnings.json` | `warn_lag_large_n_51`, `warn_lag_large_n_100`, `warn_lag_large_n_parenthesized` | ✅ 3 cases |
| `MISSING_INTERPOLATE_ONSET` | `operant/warnings.json` | `warn_interpolate_missing_onset`, `warn_interp_alias_missing_onset` | ✅ 2 cases |
| `REDUNDANT_DIRECTIONAL_COD` | `operant/warnings.json` | `warn_redundant_directional_cod` | ✅ |
| `VACUOUS_LH_RATIO` | `operant/lh_propagation.json` | `lh_prop_explicit_override`, `lh_prop_nested_chain_in_conc`, `lh_prop_ratio_warning`, `lh_prop_mult` | ✅ 4 cases |
| `RD_LARGE_DELAY` | `operant/reinforcement_delay.json` | `rd_warning_large_delay` | ✅ |

### §4.2 Operant-Stateful Warnings

| Warning Code | Test File(s) | Test Case IDs | Status |
|---|---|---|---|
| `PCTL_EXTREME_RANK` | `operant/stateful/errors.json` | `pctl_warn_extreme_rank_zero`, `pctl_warn_extreme_rank_100` | ✅ 2 cases |
| `PCTL_SMALL_WINDOW` | `operant/stateful/errors.json` | `pctl_warn_small_window` | ✅ |
| `PCTL_LARGE_WINDOW` | `operant/stateful/errors.json` | `pctl_warn_large_window` | ✅ |
| `ADJ_UNBOUNDED_DELAY` | `operant/stateful/errors.json` | `adj_warn_unbounded_delay` | ✅ |
| `ADJ_LARGE_STEP` | `operant/stateful/errors.json` | `adj_warn_large_step` | ✅ |
| `ADJ_ZERO_MIN_DELAY` | `operant/stateful/errors.json` | `adj_warn_zero_min_delay` | ✅ |
| `ADJ_SUBUNIT_RATIO` | `operant/stateful/errors.json` | `adj_warn_subunit_ratio` | ✅ |
| `INTERLOCK_TRIVIAL_RATIO` | `operant/stateful/errors.json` | `interlock_warn_trivial_ratio` | ✅ |
| `INTERLOCK_LARGE_RATIO` | `operant/stateful/errors.json` | `interlock_warn_large_ratio` | ✅ |

### §4.3 Operant-Trial-Based Warnings

| Warning Code | Test File(s) | Test Case IDs | Status |
|---|---|---|---|
| `MTS_MANY_COMPARISONS` | `operant/trial-based/errors.json` | `mts_warn_many_comparisons`, `mts_warn_comparisons_boundary` | ✅ 2 cases |
| `MTS_NO_REINFORCEMENT` | `operant/trial-based/errors.json` | `mts_warn_no_reinforcement` | ✅ |
| `MTS_IDENTITY_WITH_CLASSES` | `operant/trial-based/errors.json` | `mts_warn_identity_with_stimulus_classes` | ✅ |
| `MTS_ARBITRARY_WITHOUT_CLASSES` | `operant/trial-based/errors.json` | `mts_warn_arbitrary_without_stimulus_classes`, `mts_warn_default_arbitrary_without_stimulus_classes` | ✅ 2 cases |
| `MTS_SHORT_ITI` | `operant/trial-based/errors.json` | `mts_warn_short_iti` | ✅ |
| `MTS_LONG_LH` | `operant/trial-based/errors.json` | `mts_warn_long_lh` | ✅ |
| `GONOGO_LH_REDUNDANT` | `operant/trial-based/gonogo.json` | `gonogo_with_limited_hold`, `gonogo_with_limited_hold_kwarg` | ✅ 2 cases |

---

## §5. Negative Coverage (Confirmed Non-Triggering Cases)

These test cases verify that valid inputs do NOT produce false warnings or errors.

| File | Test Case IDs | Verifies |
|---|---|---|
| `operant/warnings.json` | `no_warn_fr_no_time_unit` | FR (ratio domain) has no MISSING_TIME_UNIT |
| `operant/warnings.json` | `no_warn_fi_with_time_unit` | FI with explicit unit has no warning |
| `operant/warnings.json` | `warn_sidman_rsi_equals_ssi` | RSI = SSI does NOT trigger RSI_EXCEEDS_SSI |
| `operant/warnings.json` | `no_warn_sidman_rsi_less_than_ssi` | RSI < SSI is clean |
| `operant/warnings.json` | `no_warn_lag_50` | Lag 50 does NOT trigger LAG_LARGE_N |
| `operant/warnings.json` | `no_warn_interpolate_with_onset` | Interpolate with onset has no warning |
| `operant/warnings.json` | `no_warn_conc_with_cod_explicit` | Conc with explicit COD has no warning |
| `operant/warnings.json` | `no_warn_conc_with_cod_zero` | COD=0s does NOT trigger MISSING_COD |
| `operant/warnings.json` | `warn_directional_cod_no_missing_cod` | Directional COD suppresses MISSING_COD |
| `operant/atomic.json` | `atomic_fr5_no_warning`, `atomic_vi60s_no_warning` | Clean valid cases produce no diagnostics |
| `operant/trial-based/mts.json` | `mts_comparisons_9_no_warning` | comparisons=9 does NOT trigger MTS_MANY_COMPARISONS |
| `operant/trial-based/mts.json` | `mts_iti_1s_no_warning` | ITI=1s does NOT trigger MTS_SHORT_ITI |
| `operant/trial-based/gonogo.json` | `gonogo_responseWindow_boundary_500ms` | responseWindow=500ms does NOT trigger GONOGO_SHORT_RESPONSE_WINDOW |
| `operant/trial-based/gonogo.json` | `gonogo_iti_1s_no_warning` | ITI=1s does NOT trigger GONOGO_SHORT_ITI |

---

## §6. File-Level Test Case Inventory

| File | Valid | Error | Warning | Total |
|---|---|---|---|---|
| `operant/atomic.json` | 24 | 0 | 8 | 32 |
| `operant/compound.json` | 27 | 0 | 7 | 34 |
| `operant/modifier.json` | 23 | 0 | 0 | 23 |
| `operant/binding.json` | 8 | 0 | 1 | 9 |
| `operant/second_order.json` | 5 | 0 | 0 | 5 |
| `operant/limited_hold.json` | 12 | 0 | 0 | 12 |
| `operant/lh_propagation.json` | 23 | 0 | 4 | 27 |
| `operant/aversive.json` | 14 | 0 | 0 | 14 |
| `operant/interpolated.json` | 7 | 0 | 0 | 7 |
| `operant/program.json` | 4 | 0 | 0 | 4 |
| `operant/reinforcement_delay.json` | 7 | 2 | 1 | 10 |
| `operant/algebra.json` | 25 | 0 | 0 | 25 |
| `operant/errors.json` | 0 | 96 | 0 | 96 |
| `operant/boundary-values.json` | 19 | 35 | 0 | 54 |
| `operant/warnings.json` | 9 | 0 | 24 | 33 |
| `operant/compound-kw-aliases.json` | 12 | 0 | 0 | 12 |
| `operant/semantic-violations-extended.json` | 0 | 41 | 0 | 41 |
| `operant/stateful/percentile.json` | 10 | 0 | 0 | 10 |
| `operant/stateful/adjusting.json` | 16 | 0 | 0 | 16 |
| `operant/stateful/interlocking.json` | 12 | 0 | 0 | 12 |
| `operant/stateful/errors.json` | 0 | 38 | 16 | 54 |
| `operant/trial-based/mts.json` | 23 | 0 | 0 | 23 |
| `operant/trial-based/gonogo.json` | 14 | 8 | 2 | 22 † |
| `operant/trial-based/errors.json` | 0 | 29 | 10 | 39 |
| `annotations/measurement.json` | 29 | 0 | 0 | 29 |
| `annotations/program-level.json` | 4 | 0 | 0 | 4 |
| `annotations/errors.json` | 0 | 36 | 0 | 36 |
| `representations/t-tau/to_ttau.json` | 8 | 3 | 0 | 11 |
| `representations/t-tau/from_ttau.json` | 8 | 1 | 0 | 9 |
| `representations/t-tau/roundtrip.json` | 6 | 0 | 0 | 6 |
| `representations/t-tau/errors.json` | 0 | 7 | 0 | 7 |
| **Total** | **389** | **296** | **73** | **698** † |

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

---

## §8. Error Code Summary

| Layer | Error Codes | Warning Codes | All Tested |
|---|---|---|---|
| Operant (Parse) | 11 | — | ✅ |
| Operant (Semantic) | 42 | 8 | ✅ |
| Operant-Stateful | 16 | 9 | ✅ |
| Operant-Trial-Based (MTS) | 11 | 6 | ✅ |
| Operant-Trial-Based (GoNoGo) | 7 | 1 | ✅ |
| Annotations | 34 | — | ✅ |
| Representations (T-τ) | 7 | — | ✅ |
| **Total** | **128** | **24** | **✅ 100%** |

---

*References: `schema/foundations/grammar.ebnf`, `schema/operant/grammar.ebnf`, `schema/operant/stateful/grammar.ebnf`, `schema/operant/trial-based/grammar.ebnf`, `schema/respondent/grammar.ebnf`, `schema/composed/*.schema.json`, `schema/annotations/extensions/respondent-annotator.schema.json`*
