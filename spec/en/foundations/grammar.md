# Foundations Grammar — Paradigm-Neutral Formal Skeleton

> Part of the contingency-dsl foundations layer (Ψ). Defines the paradigm-neutral CFG / LL(2) structure, meta-grammar, token types, parse-tree conventions, and identifier conventions. Operant-specific schedule productions live in `operant/grammar.md`; respondent-specific productions in `respondent/grammar.md`.

**Companion document:** [LL(2) Formal Proof](ll2-proof.md) — FIRST₁/FIRST₂/FOLLOW₂ sets, LL(2) parse table, unambiguity proof, and paradigm-preservation proofs. The grammar has exactly one LL(2) decision point (`PosTail` in compound `arg_list`); all other decision points are LL(1).

---

## 1. Design Principles

The DSL grammar satisfies four criteria at the foundations level:

1. **Notational fidelity**: Matches behavioral literature conventions (paradigm-specific forms live in `operant/grammar.md` and `respondent/grammar.md`).
2. **Unambiguous parsing**: Every expression has exactly one parse tree.
3. **Composability**: Supports arbitrarily nested expressions.
4. **Python embeddability**: Usable as both standalone text format and Python constructor calls.

These principles are paradigm-neutral: they hold for operant schedule expressions, respondent primitives, composed procedures, and the experiment layer alike.

## 2. Meta-Grammar (Paradigm-Neutral Skeleton)

The following BNF fragment is the portion that does **not** depend on whether the target paradigm is operant (three-term) or respondent (two-term). Paradigm-specific productions (`ScheduleExpr`, `PairExpr`, etc.) extend this skeleton in the respective layer specifications.

```bnf
<file>          ::= <experiment> | <program>

<program>       ::= <program_annotation>* <param_decl>* <binding>* <expr>
<expr>          ::= <paradigm_specific_expr>        -- defined per-layer

<binding>       ::= "let" <ident> "=" <expr>

<param_decl>    ::= <param_name> "=" <value>
                  -- Paradigm-specific keywords are listed by the
                  -- corresponding layer grammar (e.g., LH, COD, FRCO
                  -- belong to operant/grammar.md; @iti, @cs_interval
                  -- belong to annotations/extensions/respondent-annotator).

<value>         ::= <number> <time_unit>?
<time_unit>     ::= "s" | "ms" | "min"
<number>        ::= [0-9]+ ("." [0-9]+)?

<ident>         ::= [a-z_][a-zA-Z0-9_]*   -- must not match <reserved>
```

**Identifier naming constraint.** Identifiers must begin with a lowercase ASCII letter or underscore (`[a-z_]`), followed by any combination of ASCII letters, digits, or underscores. This ensures lexical disjointness from DSL keywords and schedule type prefixes, all of which begin with an uppercase letter. Each layer augments `<reserved>` with its own keyword set; the union across layers is disjoint from the `<ident>` regular set.

**Reserved for future use.** `def` is reserved at the foundations level to prevent identifier collisions when parameterized templates are introduced. See `architecture.md §4.4`.

## 3. Token Types

The lexer recognizes the following token categories. Paradigm layers introduce additional tokens (e.g., schedule prefix `FR`, primitive constructor `Pair.ForwardDelay`), but the following are foundational:

| Category | Examples | Notes |
|---|---|---|
| Number literal | `5`, `30.0`, `0.003` | `<number>` in §2 |
| Time unit suffix | `s`, `ms`, `min` | Attached or space-separated |
| Identifier | `baseline`, `treatment_1` | Must begin with `[a-z_]` |
| Upper identifier | `Baseline`, `Phase1` | Phase names, begin with `[A-Z]` |
| Keyword | `let`, `def`, `phase`, `use` | Reserved |
| Punctuation | `(` `)` `,` `=` `->` | Structural |
| String literal | `"Long-Evans"` | Double-quoted, for annotation values |
| Annotation marker | `@` | Introduces annotation attachment |

## 4. Parse-Tree Conventions

The DSL compiles source text into an Abstract Syntax Tree (AST) in three phases, each governed by a JSON Schema:

| Phase | Name | Type universe | Schema | Key property |
|---|---|---|---|---|
| Phase 1 | Pre-expansion | Includes `IdentifierRef`, `RepeatModifier` | `ast-parsed.schema.json` | May contain unresolved references |
| Phase 2 | Post-expansion | Excludes `IdentifierRef`, `RepeatModifier` | `ast-resolved.schema.json` | All references resolved, macro sugar expanded |
| Phase 3 | Resolved | Phase 2 + paradigm-level default propagation | `ast-resolved.schema.json` | Program-level defaults propagated |

Each phase transition is total: it either succeeds (producing a well-typed AST in the target phase) or fails with a semantic error. No partial ASTs are returned.

The three-phase pipeline is paradigm-neutral; operant and respondent layers use it uniformly. Paradigm-specific default propagation (e.g., operant-layer LH propagation in `operant/theory.md §1.6.1`) operates at Phase 2 → Phase 3.

## 5. Notational Flexibility (Foundations)

At the foundations level, the grammar permits multiple equivalent forms for the same value. Paradigm layers specify the exact atoms that use these forms; the foundations layer fixes only the lexical forms themselves:

```
<number>-<unit>        -- JEAB modern standard with hyphen (e.g., "60-s")
<number> <unit>        -- space-separated unit (e.g., "60 s")
<number><unit>         -- attached unit (e.g., "60s")
<number>               -- bare number, unit implied by context
```

All four resolve to the same `(value, unit)` pair at the AST level. The parser reads `<value>` uniformly regardless of the separator.

## 6. Syntactic Sugar (Foundations Level)

Two general-purpose sugars exist at the foundations level. Paradigm layers may introduce additional, paradigm-specific sugar forms.

**`let` bindings** are macro expansion (textual substitution). Binding names must satisfy `<ident>`: they must begin with a lowercase letter or underscore and must not match any reserved word.

```
let baseline = <expr_1>
let treatment = <expr_2>
<expr_using baseline, treatment>
```

expands to the corresponding let-free syntax tree. `let` does not introduce mutable state, closures, or recursive definitions. After expansion, the result is a let-free syntax tree within the base CFG.

**Scoping rules.** `let` bindings are subject to three semantic constraints:

1. **No shadowing.** Each binding name must be unique within a program. Duplicate names are a static error (e.g., `"duplicate binding 'x' (first defined at line N)"`).
2. **No forward references.** In binding `let x_k = e`, every identifier in `e` must be among `{x_1, ..., x_{k-1}}` — i.e., defined in a preceding binding. Referencing an undefined or later-defined identifier is a static error. As a corollary, transitive mutual references (e.g., `let a = b; let b = a`) are rejected.
3. **Top-level only.** Bindings appear only at the `<program>` level. `let` cannot appear inside paradigm-specific compound expressions.

Implementations SHOULD additionally emit a warning for unused bindings (a binding whose name is never referenced in the main expression or subsequent bindings).

**`def` (reserved).** Parameterized templates of the form `def name(args) = <expr>` are reserved for a future design checkpoint. The keyword is reserved now to prevent identifier collisions. When introduced, `def` will expand by macro substitution subject to a DAG well-formedness condition on the call graph (see `architecture.md §4.4`).

## 7. Error Recovery Policy (Paradigm-Neutral)

Conforming parsers MUST follow this error recovery policy regardless of the paradigm being parsed:

**Error reporting requirements (MUST):**
- Report at least one error with its error code, position (line and column), and error category (`LexError`, `ParseError`, or `SemanticError`).
- The error code MUST match one of the codes defined in the paradigm-specific error registries (`conformance/foundations/errors.json`, `conformance/operant/errors.json`, `conformance/respondent/errors.json`).

**Multiple error recovery (SHOULD):**
- Parsers SHOULD implement **panic-mode recovery** (Aho et al., 2006, §4.8.2): upon detecting an error, discard input tokens until a synchronization token is reached, then resume parsing.
- Synchronization tokens: `)`, `,`, newline (`\n`), `EOF`.
- Report all detected errors as a list, ordered by position.

**Partial AST (MUST NOT):**
- Parsers MUST NOT return a partial AST when errors are present. On error, the result is an error list with no AST.

**Error limits (MAY):**
- Parsers MAY stop after a configurable maximum number of errors (recommended default: 10) to prevent cascading error noise.

**Rationale.** Single-error-then-stop forces users to fix one error at a time, which is unacceptable for a DSL where a single misplaced character can mask downstream issues. Panic-mode recovery is the simplest strategy that enables multi-error reporting while avoiding the complexity of phrase-level or error-production recovery (Aho et al., 2006, §4.8).

## 8. LL(2) Property (Foundations Level)

The grammar skeleton above is LL(1) at every decision point. The only LL(2) decision point in the entire DSL lives inside operant compound `arg_list` (`PosTail` disambiguation); it is local to the operant layer and does not pollute the foundations skeleton. See `ll2-proof.md` for the formal proof.

## References

- Aho, A. V., Lam, M. S., Sethi, R., & Ullman, J. D. (2006). *Compilers: Principles, techniques, and tools* (2nd ed.). Addison-Wesley.
