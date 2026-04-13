# contingency-dsl

Language-independent specification for declaring reinforcement contingencies.

## What this package contains

- **`grammar.ebnf`** — Formal grammar (context-free, non-Turing-complete)
- **`ast-schema.json`** — JSON Schema for the Abstract Syntax Tree
- **`defaults.md`** — Explicit default values for omitted parameters
- **`conformance/`** — Conformance test suite (input text -> expected AST JSON)
- **`annotations/`** — Annotation definitions (stimulus, temporal, subject, apparatus)
- **`docs/`** — User-facing documentation (notation guide, use cases, annotations)
- **`spec/`** — Formal specification (theory, grammar, architecture, annotation design)

## What this package does NOT contain

- No code. No parser implementation. No runtime dependencies.
- Parser implementations live in separate packages:
  - **contingency-dsl-py** — Python reference parser
  - **contingency-dsl-rs** — Rust parser (future)

## Syntax examples

```
FR5                           -- Fixed Ratio 5
VI60s                         -- Variable Interval 60 seconds
Chain(FR5, FI30s)             -- Chained: FR5 then FI30
Conc(VI30s, VI60s)            -- Concurrent VI30 VI60
FR5(FI30)                     -- Second-order: 5 FI30 completions
let baseline = VI60s          -- Named binding
DRL5s                         -- Differential Reinforcement of Low rate
FI30 LH10                    -- Limited Hold: 10s availability window
```

## Documentation

- **[Syntax Guide (EN)](docs/en/syntax-guide.md)** / **[構文ガイド (JA)](docs/ja/syntax-guide.md)** — Progressive guide from `FR5` to `FI120(FR10)`
- **[Use Cases (EN)](docs/en/use-cases.md)** / **[ユースケース (JA)](docs/ja/use-cases.md)** — What each construct enables, with citations
- **[Annotations (EN)](docs/en/annotations.md)** / **[アノテーション (JA)](docs/ja/annotations.md)** — How to enrich schedules with experimental metadata
- **[Theory (EN)](spec/en/theory.md)** / **[理論 (JA)](spec/ja/theory.md)** — Formal algebraic type system
- **[Grammar (EN)](spec/en/grammar.md)** / **[文法 (JA)](spec/ja/grammar.md)** — BNF, notational flexibility, dual API
- **[Tooling (EN)](docs/en/tooling.md)** / **[ツーリング (JA)](docs/ja/tooling.md)** — Tree-sitter, Langium LSP, GitHub Releases

## Conformance testing

Any parser implementation should pass all tests in `conformance/`:

```bash
# Python example
pytest tests/test_conformance.py -v

# Rust example
cargo test conformance
```

## References

- Ferster, C. B., & Skinner, B. F. (1957). *Schedules of reinforcement*.
- Fleshler, M., & Hoffman, H. S. (1962). *JEAB*, 5(4), 529-530.
- Catania, A. C. (2013). *Learning* (5th ed.).
