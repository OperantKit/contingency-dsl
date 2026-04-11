# contingency-dsl Conformance Test Suite

Language-independent test cases for validating parser implementations.

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

`expected` contains the AST matching `ast-schema.json`.

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

### COD warning (v1.0)

`Conc` without a COD parameter is syntactically and semantically valid
(constraint §7). A linter WARNING (`MISSING_COD`) is emitted when no COD
is specified at either the expression level or the program level.
Test cases that trigger this warning include a `"warnings"` array.
Explicit `COD=0s` does NOT trigger the warning.

## Test files

| File | Cases | Scope |
|------|-------|-------|
| `atomic.json` | 15 | FR5, VI60s, RR20, EXT, CRF, all 3x3 grid |
| `compound.json` | 19 | Conc, Alt, Conj, Chain, Tand, Mult, Mix, nested, deep nesting depth≥3, wide (5 components) |
| `modifier.json` | 13 | DRL, DRH, DRO, PR, Repeat |
| `limited_hold.json` | 12 | FI30 LH10, program-level LH default, LH on EXT/CRF/SecondOrder |
| `second_order.json` | 5 | FR5(FI30), VI60(FR10), RR5(FT20s) |
| `binding.json` | 7 | let bindings, expansion, compound refs, LH bindings |
| `program.json` | 4 | Complete programs with param_decls + bindings |
| `aversive.json` | 7 | Sidman free-operant avoidance (v1.x), verbose aliases, composition with Chain, let binding |
| `errors.json` | 31 | Lex errors, parse errors, semantic errors, reserved words, self-reference, Sidman param errors |
