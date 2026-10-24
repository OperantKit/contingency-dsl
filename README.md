# contingency-dsl

:jp: [日本語版 README](README.ja.md)

contingency-dsl is a short text notation for schedules of reinforcement and Pavlovian conditioning procedures, such as `Conc(VI 30-s, VI 60-s, COD=2-s)` or `Pair.ForwardDelay(cs=Tone, us=Shock, isi=10s, cs_duration=12s)`. This repository is its specification: the grammar, the JSON format of a parsed expression, and a set of test cases. It is the common language of [OperantKit](https://github.com/OperantKit): the parser, the schedule engines, and the Method-section tools all read the same expressions.

**In short**

- A schedule fits in a sentence or a table cell and states its parameters, such as the changeover delay (COD) and the limited hold, instead of leaving them to the program.
- The notation follows the abbreviations already used in Method sections (`FR 5`, `VI 60-s`, `Conc(...)`, `Mult(...)`).
- Every parser, in any language, can be checked against the same 1,065 test cases.

A Method section that says "concurrent VI 30 s VI 60 s" often leaves out how the changeover delay was handled or how the intervals were generated, and every lab's program fills the gap differently. Writing the procedure in a notation with a grammar makes those choices explicit and lets other people rerun the same procedure.

## Installation

This repository contains no code. To use the notation from Python, install the parser [contingency-dsl-py](https://github.com/OperantKit/contingency-dsl-py) (Python 3.11 or newer). The packages are not on PyPI yet, so install from GitHub:

```bash
git clone https://github.com/OperantKit/contingency-dsl
cd contingency-dsl
pip install git+https://github.com/OperantKit/contingency-dsl-py jsonschema
```

`jsonschema` is only needed to check a parsed expression against the JSON Schema, as in the example below.

## Example

Parse a concurrent schedule, check the result against this repository's JSON Schema, and replay one of the test cases. Run it from the root of the clone:

```python
import json
from pathlib import Path

from contingency_dsl import ParseError, parse, to_dict
from jsonschema import Draft202012Validator

schema = json.loads(Path("schema/operant/ast.schema.json").read_text(encoding="utf-8"))
validator = Draft202012Validator(schema)

ast = to_dict(parse("Conc(VI30s, VI60s, COD=2s)"))
print(ast["schedule"]["params"])  # {'COD': {'value': 2.0, 'time_unit': 's'}}
print(validator.is_valid(ast))  # True

ast["schedule"]["components"][0]["dist"] = "X"  # not a schedule distribution
print(validator.is_valid(ast))  # False

cases = json.loads(Path("conformance/operant/errors.json").read_text(encoding="utf-8"))
case = next(c for c in cases if c["id"] == "error_compound_one_component")
print(case["input"], case["error"])  # Conc(FR5) {'type': 'ParseError', 'code': 'INSUFFICIENT_COMPONENTS'}
try:
    parse(case["input"])
except ParseError as error:
    print(error)  # line 1, col 1: Conc requires at least 2 components
```

To run a parsed schedule against responses, use [contingency-py](https://github.com/OperantKit/contingency-py). To turn it into a Method-section paragraph, use [contingency-dsl2procedure](https://github.com/OperantKit/contingency-dsl2procedure); to extract it from published Method text, use [contingency-procedure2dsl](https://github.com/OperantKit/contingency-procedure2dsl).

## What the notation covers

A few expressions:

```
FR5                                     -- fixed ratio 5
Conc(VI30s, VI60s, COD=2s)              -- concurrent VI VI with a 2-s changeover delay
Chain(FR5, FI30s)                       -- chained FR 5 FI 30 s
FI30 LH10                               -- FI 30 s with a 10-s limited hold
Pair.ForwardDelay(cs=Tone, us=Shock, isi=10s, cs_duration=12s)
```

More examples, grouped by layer, are in [Syntax examples](docs/en/syntax-examples.md). The specification is organized in layers:

| Layer | What it describes |
|---|---|
| **Foundations** | The meta-grammar and the types shared by every layer (contingency, time scales, stimuli, context) |
| **Operant** | Three-term contingencies: ratio, interval, time, differential, compound, and progressive-ratio schedules; aversive control (Sidman avoidance, discriminated avoidance, escape, response cost); stateful schedules (percentile, adjusting, interlocking); trial-based procedures (matching-to-sample, go/no-go); limited hold, timeout, reinforcement delay |
| **Respondent** | Two-term (CS-US) contingencies: `Pair.*`, `Extinction`, `CSOnly`, `USOnly`, `Contingency`, `TrulyRandom`, `ExplicitlyUnpaired`, `Compound`, `Serial`, `ITI`, `Differential` |
| **Composed** | Procedures built from operant and respondent parts, such as conditioned suppression, Pavlovian-instrumental transfer, autoshaping, and omission |
| **Experiment** | Multi-phase designs, with phases and contexts as part of the program |
| **Annotation** | Metadata in the Method-section categories (Subjects, Apparatus, Procedure, Measurement), such as `@reinforcer`, `@sd`, `@species`, `@apparatus` |

Deeper Pavlovian procedures (blocking, overshadowing, latent inhibition, renewal, reinstatement, occasion setting, and others) are specified in the companion package [contingency-respondent-dsl](https://github.com/OperantKit/contingency-respondent-dsl).

## What is in this repository

- `spec/en/`, `spec/ja/`: the formal specification of each layer (theory, grammar, primitives, design rationale)
- `schema/`: the EBNF grammar of each layer and the JSON Schemas for the parsed form
- `conformance/`: the test cases (input text and the expected parsed form or error)
- `docs/en/`, `docs/ja/`: user documentation
- `scripts/`: converters from the EBNF grammar to Langium and Tree-sitter

Parsers live in separate packages:

- **contingency-dsl-py** — Python reference parser (sole reference implementation)

## Documentation

- [Syntax guide](docs/en/syntax-guide.md): the notation step by step
- [Syntax examples](docs/en/syntax-examples.md): examples for every layer
- [Use cases](docs/en/use-cases.md): what each construct is for, with citations
- [Annotations](docs/en/annotations.md): `@reinforcer`, `@punisher`, `@sd`, `@cs`, `@us`, `@species`, `@apparatus`, and the other metadata keywords
- [Paper examples](docs/en/paper-examples.md): published studies written in the notation
- [Tooling](docs/en/tooling.md): Tree-sitter and Langium grammars
- Specification: [architecture](spec/en/architecture.md), [design philosophy](spec/en/design-philosophy.md), [operant grammar](spec/en/operant/grammar.md), [respondent grammar](spec/en/respondent/grammar.md), [foundations grammar](spec/en/foundations/grammar.md)

## Conformance tests

`conformance/` holds 1,065 test cases in 57 JSON files; 370 of them expect an error. Each case pairs an input with the expected parsed form or the expected error, so a parser in any language can be checked against the same inputs. The format and the directory layout are described in [conformance/README.md](conformance/README.md).

The Python parser's test suite reads the cases from a `contingency-dsl` clone next to it:

```bash
git clone https://github.com/OperantKit/contingency-dsl
git clone https://github.com/OperantKit/contingency-dsl-py
cd contingency-dsl-py
pip install -e '.[test]'
pytest tests/test_conformance.py
```

## Limitations

- contingency-dsl-py does not accept every construct specified here. It ships six annotation extensions; the respondent annotations used in the composed examples (`@cs`, `@us`) are specified here but are not accepted by those extensions.
- `conformance/foundations/` has no cases: existing lexical tests use operant schedule keywords and are filed under `conformance/operant/` instead ([why](conformance/foundations/README.md)).

## For contributors

`dist/` (the generated Langium and Tree-sitter grammars) is not tracked. Regenerate it from `schema/**/grammar.ebnf`:

```bash
./scripts/gen-langium.sh      # dist/langium/contingency-dsl.langium
./scripts/gen-treesitter.sh   # dist/tree-sitter/grammar.js
```

Every `python` block in this README and in `README.ja.md` is run by `scripts/check_readme_examples.py`. Notes for AI coding agents are in [AGENTS.md](AGENTS.md).

## Citation and license

Cite this repository with [CITATION.cff](CITATION.cff). MIT License; see [LICENSE](LICENSE).
