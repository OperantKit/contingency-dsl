# contingency-dsl

:gb: [English README](README.md)

contingency-dsl は、強化スケジュールと Pavlov 型条件づけの手続きを `Conc(VI 30-s, VI 60-s, COD=2-s)` や `Pair.ForwardDelay(cs=Tone, us=Shock, isi=10s, cs_duration=12s)` のような短いテキストで書くための記法です。このリポジトリはその仕様で、文法、式を構文解析した結果の JSON 形式、テストケースの集まりを収めています。[OperantKit](https://github.com/OperantKit) の共通言語で、パーサ・スケジュールエンジン・方法セクション（Method 節）の道具はどれも同じ式を読みます。

**要点**

- スケジュールが 1 文や表の 1 マスに収まり、切替遅延（changeover delay, COD）や制限時間（limited hold）のようなパラメータをプログラム任せにせず式の中に書けます。
- 記法は Method 節ですでに使われている略記（`FR 5`、`VI 60-s`、`Conc(...)`、`Mult(...)`）に沿っています。
- どの言語のパーサも、同じ 1,065 件のテストケースで確かめられます。

「並立 VI 30 秒 VI 60 秒」と書かれた Method 節では、切替遅延をどう扱ったか、間隔をどう生成したかが省かれることが多く、その空白を研究室ごとのプログラムがそれぞれ違うやり方で埋めています。文法のある記法で手続きを書けば、そうした選択がはっきり書かれ、他の人が同じ手続きを再実行できます。

## インストール

このリポジトリにはコードがありません。Python からこの記法を使うには、パーサ [contingency-dsl-py](https://github.com/OperantKit/contingency-dsl-py) を入れます（Python 3.11 以上）。パッケージはまだ PyPI に登録されていないので、GitHub から入れます。

```bash
git clone https://github.com/OperantKit/contingency-dsl
cd contingency-dsl
pip install git+https://github.com/OperantKit/contingency-dsl-py jsonschema
```

`jsonschema` は、下の例のように構文解析の結果を JSON Schema で検査するときだけ必要です。

## 例

並立スケジュールを構文解析し、結果をこのリポジトリの JSON Schema で検査し、テストケースを 1 件再生します。clone したリポジトリの最上位で実行してください。

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

ast["schedule"]["components"][0]["dist"] = "X"  # スケジュールの分布として不正な値
print(validator.is_valid(ast))  # False

cases = json.loads(Path("conformance/operant/errors.json").read_text(encoding="utf-8"))
case = next(c for c in cases if c["id"] == "error_compound_one_component")
print(case["input"], case["error"])  # Conc(FR5) {'type': 'ParseError', 'code': 'INSUFFICIENT_COMPONENTS'}
try:
    parse(case["input"])
except ParseError as error:
    print(error)  # line 1, col 1: Conc requires at least 2 components
```

構文解析したスケジュールを反応に対して実行するには [contingency-py](https://github.com/OperantKit/contingency-py) を使います。Method 節の段落にするには [contingency-dsl2procedure](https://github.com/OperantKit/contingency-dsl2procedure) を、公刊された Method 節の文章から取り出すには [contingency-procedure2dsl](https://github.com/OperantKit/contingency-procedure2dsl) を使います。

## 記法で書けるもの

式の例をいくつか示します。

```
FR5                                     -- 固定比率 5
Conc(VI30s, VI60s, COD=2s)              -- 切替遅延 2 秒の並立 VI VI
Chain(FR5, FI30s)                       -- 連鎖 FR 5 FI 30 秒
FI30 LH10                               -- 制限時間 10 秒の FI 30 秒
Pair.ForwardDelay(cs=Tone, us=Shock, isi=10s, cs_duration=12s)
```

レイヤごとの例は [構文例](docs/ja/syntax-examples.md) にあります。仕様は次のレイヤに分かれています。

| レイヤ | 記述する内容 |
|---|---|
| **Foundations** | すべてのレイヤに共通するメタ文法と型（随伴性、時間尺度、刺激、文脈） |
| **Operant** | 三項随伴性: 比率・時隔・時間・分化強化・複合・累進比率の各スケジュール、嫌悪性制御（Sidman 型回避、弁別回避、逃避、反応コスト）、状態を持つスケジュール（パーセンタイル、調整、連動）、試行型の手続き（見本合わせ、go/no-go）、制限時間・タイムアウト・強化遅延 |
| **Respondent** | 二項（CS-US）随伴性: `Pair.*`、`Extinction`、`CSOnly`、`USOnly`、`Contingency`、`TrulyRandom`、`ExplicitlyUnpaired`、`Compound`、`Serial`、`ITI`、`Differential` |
| **Composed** | オペラントとレスポンデントの部品を組み合わせた手続き（条件性抑制、Pavlov 型–道具的転移、オートシェイピング、省略など） |
| **Experiment** | 複数フェーズのデザイン。フェーズと文脈をプログラムの一部として書けます |
| **Annotation** | Method 節の区分（Subjects、Apparatus、Procedure、Measurement）に沿ったメタデータ（`@reinforcer`、`@sd`、`@species`、`@apparatus` など） |

より複雑な Pavlov 型の手続き（阻止、隠蔽、潜在制止、リニューアル、復位、機会設定など）は、姉妹パッケージ [contingency-respondent-dsl](https://github.com/OperantKit/contingency-respondent-dsl) で定義されています。

## このリポジトリの中身

- `spec/en/`、`spec/ja/`: 各レイヤの形式仕様（理論、文法、プリミティブ、設計の根拠）
- `schema/`: 各レイヤの EBNF 文法と、構文解析の結果を表す JSON Schema
- `conformance/`: テストケース（入力テキストと、期待される構文解析の結果またはエラー）
- `docs/en/`、`docs/ja/`: 利用者向けの文書
- `scripts/`: EBNF 文法から Langium と Tree-sitter の文法を作る変換スクリプト

パーサは別のパッケージにあります。

- **contingency-dsl-py** — Python のリファレンスパーサ（唯一のリファレンス実装）

## 文書

- [構文ガイド](docs/ja/syntax-guide.md): 記法を順を追って説明します
- [構文例](docs/ja/syntax-examples.md): すべてのレイヤの例
- [ユースケース](docs/ja/use-cases.md): 各構文が何のためにあるか（文献つき）
- [アノテーション](docs/ja/annotations.md): `@reinforcer`、`@punisher`、`@sd`、`@cs`、`@us`、`@species`、`@apparatus` などのメタデータのキーワード
- [論文例](docs/ja/paper-examples.md): 公刊された研究をこの記法で書いたもの
- [ツーリング](docs/ja/tooling.md): Tree-sitter と Langium の文法
- 仕様: [アーキテクチャ](spec/ja/architecture.md)、[設計思想](spec/ja/design-philosophy.md)、[オペラント文法](spec/ja/operant/grammar.md)、[レスポンデント文法](spec/ja/respondent/grammar.md)、[基盤文法](spec/ja/foundations/grammar.md)

## 適合テスト

`conformance/` には 57 個の JSON ファイルに 1,065 件のテストケースがあり、そのうち 370 件はエラーを期待するケースです。各ケースは入力と、期待される構文解析の結果またはエラーの組なので、どの言語のパーサも同じ入力で確かめられます。形式とディレクトリ構成は [conformance/README.md](conformance/README.md) に書かれています。

Python パーサのテストは、隣に置いた `contingency-dsl` の clone からケースを読みます。

```bash
git clone https://github.com/OperantKit/contingency-dsl
git clone https://github.com/OperantKit/contingency-dsl-py
cd contingency-dsl-py
pip install -e '.[test]'
pytest tests/test_conformance.py
```

## 制限

- contingency-dsl-py は、ここで定義されたすべての構文を受け付けるわけではありません。同梱されているアノテーション拡張は 6 つで、Composed の例で使うレスポンデント用のアノテーション（`@cs`、`@us`）はここで定義されていますが、それらの拡張では受け付けられません。
- `conformance/foundations/` にはケースがありません。既存の字句のテストはオペラントのスケジュールのキーワードを含むため、`conformance/operant/` に置かれています（[理由](conformance/foundations/README.md)）。

## 開発に参加する人へ

`dist/`（生成した Langium と Tree-sitter の文法）は git で管理していません。`schema/**/grammar.ebnf` から作り直します。

```bash
./scripts/gen-langium.sh      # dist/langium/contingency-dsl.langium
./scripts/gen-treesitter.sh   # dist/tree-sitter/grammar.js
```

この README と `README.md` の `python` ブロックは、すべて `scripts/check_readme_examples.py` で実行されます。AI のコーディングエージェント向けの説明は [AGENTS.md](AGENTS.md) にあります。

## 引用とライセンス

このリポジトリを引用するときは [CITATION.cff](CITATION.cff) を使ってください。MIT License です。[LICENSE](LICENSE) を参照してください。
