# contingency-dsl Foundations — Defaults and Scope

This document describes the paradigm-neutral productions grouped under
`schema/foundations/` and explains why each is classified as a Foundation-
level concern rather than an operant or respondent concern.

## Scope

Foundations defines the productions that every paradigm layer must share
in order for composed / experiment-layer programs to parse and validate
uniformly. If a production is bound to the internal structure of an
operant schedule (e.g., `Conc`, `FR`, `DRL`) or a respondent primitive
(e.g., `Pair.ForwardDelay`, `Extinction`), it does not belong here.

### What lives in Foundations

| Production | Role | Why paradigm-neutral |
|---|---|---|
| `file`, `program` | Top-level container | Both operant and respondent programs fit this shape; only the terminal `<expr>` differs. |
| `param_decl`, `binding` | Session-wide scalar defaults and name bindings | Applies to any paradigm; the keyword set per paradigm lives in that paradigm's grammar file. |
| `program_annotation` / `annotation` | Annotation attachment | Annotations cross-cut operant, respondent, composed, and experiment layers. |
| `ident`, `upper_ident` | Identifier tokenization | Lexical disjointness from paradigm keywords is a foundational invariant. |
| `value`, `number`, `time_unit`, `time_sep`, `ws` | Numeric and time-unit literals | `30-s`, `30s`, `30 s`, `30` must mean the same thing in every layer. |
| `string_literal`, `boolean` | Scalar literals | Used in annotation values, stimulus labels, and parameter values. |
| `annotation_args`, `annotation_kv`, etc. | Annotation argument grammar | Single source of truth for annotation parsing. |

### What is NOT in Foundations

- Schedule combinators (`Conc`, `Chain`, `Mult`, ...) — live in
  `schema/operant/grammar.ebnf`.
- Schedule atoms (`FR`, `VI`, `FI`, `EXT`, `CRF`, ...) — operant layer.
- Modifiers (`DRL`, `DRH`, `DRO`, `PR`, `Lag`, `Repeat`, ...) — operant.
- Aversive schedules (`Sidman`, `DiscriminatedAvoidance`) — operant.
- Timeout / ResponseCost postfix decorators — operant.
- Pavlovian primitives (`Pair.*`, `Extinction`, `Contingency`, ...) —
  `schema/respondent/grammar.ebnf`.
- Experiment-layer syntactic sugar (`phase`, `progressive`, `shaping`,
  `interleave`) — tracked in the experiment layer; the dispatch token
  `phase`/`progressive`/`shaping` is recognized here only as the first-
  token LL(1) branch between `experiment` and `program`.

## Shared-type JSON Schema

`schema/foundations/types.schema.json` exports the shared value / number /
duration / probability / identifier types. Paradigm-level AST schemas
(operant, respondent, composed) `$ref` into this file rather than
redefining these types. This guarantees uniform validation across
paradigms.

## Three-phase AST pipeline

Foundations also fixes the three-phase AST pipeline:

1. **Phase 1 (pre-expansion)** — validated by `operant/ast-parsed.schema.json`;
   may contain `IdentifierRef` and `RepeatModifier` nodes.
2. **Phase 2 (post-expansion)** — validated by `operant/ast-resolved.schema.json`;
   all references resolved, macro sugar expanded.
3. **Phase 3 (resolved with defaults)** — Phase 2 plus paradigm-level
   default propagation.

Respondent and composed layers follow the same three-phase shape; their
phase-specific schemas live in the respective layer directories.

## LL(2) property

The foundations grammar is LL(1) at every decision point. The sole LL(2)
decision point in the entire DSL (the `PosTail` disambiguation inside
operant compound `arg_list`) is local to the operant layer and is proved
in `spec/en/foundations/ll2-proof.md`. Foundations-level productions
never require more than one token of lookahead.

## References

- Aho, A. V., Lam, M. S., Sethi, R., & Ullman, J. D. (2006). *Compilers:
  Principles, techniques, and tools* (2nd ed.). Addison-Wesley.
