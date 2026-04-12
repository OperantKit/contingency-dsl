# contingency-dsl Conformance Test Suite

Language-independent test cases for validating parser and validator implementations.

## Structure

Tests are organized to mirror `schema/`:

```
conformance/
├── core/           — Core grammar tests (atomic, compound, modifier, binding, etc.)
├── annotations/    — Annotation system tests (program-level, measurement, errors)
└── representations/
    └── t-tau/      — T-tau coordinate transform tests (to/from/roundtrip/errors)
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

`expected` contains the AST matching `schema/core/ast.schema.json`.

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

### Semantic analysis cases

Some tests specify both `pre_expansion` (parser output with IdentifierRef nodes)
and `expected` (post-expansion result after semantic analysis). Parsers that do
not perform semantic analysis should validate against `pre_expansion` only.

## Test files

### core/

| File | Cases | Scope |
|------|-------|-------|
| `atomic.json` | 24 | FR5, VI60s, RR20, EXT, CRF, all 3x3 grid, JEAB notation variants |
| `compound.json` | 27 | Conc, Alt, Conj, Chain, Tand, Mult, Mix, Overlay, nested |
| `modifier.json` | 21 | DRL, DRH, DRO, PR, Repeat, Lag |
| `limited_hold.json` | 12 | FI30 LH10, program-level LH default |
| `second_order.json` | 5 | FR5(FI30), VI60(FR10), RR5(FT20s) |
| `binding.json` | 7 | let bindings, expansion |
| `aversive.json` | 14 | Sidman avoidance, discriminated avoidance |
| `program.json` | 4 | Program-level param_decls, bindings |
| `errors.json` | 56 | Lex errors, parse errors, semantic errors |

### annotations/

| File | Cases | Scope |
|------|-------|-------|
| `program-level.json` | 3 | Program-level annotations (subjects, apparatus, session) |
| `measurement.json` | 5 | @session_end, @baseline, @steady_state |
| `errors.json` | 7 | Annotation parameter validation errors |

### representations/t-tau/

| File | Cases | Scope |
|------|-------|-------|
| `to_ttau.json` | — | Lattice → T-tau conversion |
| `from_ttau.json` | — | T-tau → Lattice conversion |
| `roundtrip.json` | — | Bidirectional identity verification |
| `errors.json` | — | Type errors, domain violations |
