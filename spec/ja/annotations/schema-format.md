# Annotation Schema Format — 言語非依存メタDSL

> **Status:** Stable
>
> 本文書は **Annotation Schema Format** を定義する。annotation keyword の
> パラメータ・型・制約・スコープを言語非依存に記述するスキーマ言語である。
>
> design.md §1 および §7.1 で指摘されていた「メタDSL 未定義」
> 問題を解決する。

---

## 1. 目的

Annotation Schema Format は annotation keyword 定義の
**single source of truth** として機能する。すべての実装言語
（Python, Rust, Kotlin 等）が同じスキーマファイルを読み取り、
等価な `AnnotationModule` 実装を生成する。

### 設計判断: JSON Schema 拡張

本フォーマットは [JSON Schema 2020-12](https://json-schema.org/draft/2020-12/schema)
に DSL 固有の拡張を載せた形式を採る。代替案（EBNF 拡張、独自スキーマ DSL）
ではなくこれを選択した理由:

1. **既存エコシステム** — Python (`jsonschema`), Rust (`jsonschema-rs`),
   Kotlin (`json-schema-validator`) に成熟したバリデータライブラリが存在
2. **一貫性** — DSL の AST が既に JSON Schema を使用
3. **ツーリング** — LSP 補完、lint、ドキュメント生成が標準ツールで実現可能
4. **低い採用コスト** — 新しいパーサやジェネレータの実装が不要

DSL 固有の拡張プロパティ（`keywords`, `scope`, `positional`,
`required_if`, `forbidden_if`, `aliases`, `errors`）は標準 JSON Schema
バリデータが無視するため、ファイルは有効な JSON Schema 文書のまま
DSL セマンティクスも保持する。

---

## 2. 用語

| 用語 | 定義 |
|---|---|
| **Annotator** | annotation keyword の集合を所有する名前付きモジュール。JEAB Method 節のカテゴリと 1:1 対応（design-philosophy §3.7） |
| **Keyword** | 個別の annotation 名（例: `reinforcer`, `session_end`）。DSL ソースでは `@keyword(...)` として出現 |
| **位置引数 (Positional)** | annotation の最初の無名引数: `@species("rat")`。keyword あたり最大 1 個 |
| **キーワード引数 (Keyword arg)** | 名前付き引数: `@session_end(rule="first", time=60min)`。0 個以上 |
| **Scope** | annotation の出現位置: `program`（セッション全体のデフォルト）または `schedule`（特定のスケジュール式に付加） |
| **Registry** | 特定のプログラム（runtime/interpreter）がロードする annotator の集合。design-philosophy §4.2 により program-scoped |
| **スキーマファイル** | 本仕様に準拠し、1 つの annotator を定義する JSON ファイル |

---

## 3. ファイル規約

### 3.1 配置

```
schema/annotations/<annotator-name>.schema.json
```

Sub-annotator を持つ場合（例: procedure-annotator）:

```
schema/annotations/procedure-stimulus.schema.json
schema/annotations/procedure-temporal.schema.json
```

Extension annotator（JEAB 4 カテゴリ外）:

```
schema/annotations/extensions/<name>.schema.json
```

### 3.2 命名

- ファイル名は kebab-case: `procedure-stimulus.schema.json`
- `.schema.json` サフィックスが必須
- ファイル名（サフィックス除去後）は `title` フィールドと一致すること

### 3.3 エンコーディング

UTF-8、BOM なし。標準 JSON（末尾カンマ・コメント不可）。

---

## 4. トップレベル構造（メタスキーマ）

すべてのスキーマファイルは以下のトップレベルプロパティを含まなければならない:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://operantkit.dev/contingency-dsl/schema/annotations/<name>.schema.json",
  "title": "<annotator-name>",
  "description": "<one-line purpose>",
  "category": "<JEAB category>",
  "version": "<semver>",
  "status": "<lifecycle>",
  "keywords": { ... }
}
```

### プロパティ定義

| プロパティ | 型 | 必須 | 説明 |
|---|---|---|---|
| `$schema` | string | YES | 常に `"https://json-schema.org/draft/2020-12/schema"` |
| `$id` | string (URI) | YES | このスキーマの正規 URI |
| `title` | string | YES | Annotator 名。ファイル名（`.schema.json` 除去後）と一致 |
| `description` | string | YES | 1 行の説明 |
| `category` | string | YES | JEAB カテゴリ: `"Procedure"`, `"Subjects"`, `"Apparatus"`, `"Measurement"`, `"Extension"` |
| `sub_annotator` | string | NO | カテゴリ内の sub-annotator 名（例: `"stimulus"`, `"temporal"`） |
| `version` | string | YES | このスキーマのセマンティックバージョン |
| `status` | string | YES | ライフサイクル段階（§4.1 参照） |
| `keywords` | object | YES | Keyword 定義（§5 参照） |
| `future_keywords` | array of strings | NO | 計画中だが未定義の keyword 名 |

### 4.1 ライフサイクル段階

| Status | 意味 |
|---|---|
| `Proposed` | Keyword 候補と境界が提案済み。パラメータスキーマは未定義 |
| `Schema Design` | パラメータスキーマ定義済み。境界の正当化が文書化済み |
| `Stable` | スキーマ凍結。破壊的変更は原則回避 |

来歴は括弧内に記載可。

---

## 5. Keyword 定義

`keywords` 内の各エントリは keyword 名（string）を keyword 定義
オブジェクトにマッピングする。

```json
"reinforcer": {
  "description": "Reinforcer identification and classification.",
  "scope": ["program", "schedule"],
  "positional": { "type": "string", "required": true, "description": "Stimulus identity" },
  "params": { ... },
  "aliases": ["punisher", "consequentStimulus"],
  "alias_note": "All three collapse to the same AST node.",
  "errors": { ... },
  "reference": "Skinner, B. F. (1938). The behavior of organisms. Appleton-Century-Crofts."
}
```

### プロパティ定義

| プロパティ | 型 | 必須 | 説明 |
|---|---|---|---|
| `description` | string | YES | この annotation が宣言するもの |
| `scope` | array of strings | YES | 許可されるスコープ: `"program"`, `"schedule"`, またはその両方 |
| `positional` | object or null | YES | 位置引数の定義（§5.1）。keyword-only なら `null` |
| `params` | object | YES | キーワード引数の定義（§6）。なければ空 `{}` |
| `aliases` | array of strings | NO | 別名 keyword（§8） |
| `alias_note` | string | NO | alias の動作説明 |
| `errors` | object | NO | エラーコード定義（§9） |
| `reference` | string or null | YES | APA 形式の引用。単一の正典参照がなければ `null` |

### 5.1 位置引数

`positional` フィールドは annotation の引数リストの最初に現れる
無名引数を記述する。

`positional` が `null` でない場合:

| プロパティ | 型 | 必須 | 説明 |
|---|---|---|---|
| `type` | string | YES | 値の型（§7） |
| `required` | boolean | YES | 位置引数が必須か |
| `description` | string | NO | 値が表すもの |

`positional` が `null` の場合、その keyword はキーワード引数のみを受け付ける（`params` も空であれば、引数なしで使用される）。

**DSL 表面構文マッピング:**

```
@species("rat")                    → positional = "rat"
@session_end(rule="first", ...)    → positional なし（keyword-only）
@chamber("med-associates", model="ENV-007")  → positional + キーワード引数
```

---

## 6. パラメータ定義

`params` 内の各エントリはパラメータ名をパラメータ定義オブジェクトに
マッピングする。

```json
"time": {
  "type": "time_value",
  "required_if": { "rule": ["first", "time_only"] },
  "forbidden_if": { "rule": ["reinforcers_only"] },
  "description": "Maximum session duration"
}
```

### プロパティ定義

| プロパティ | 型 | 必須 | デフォルト | 説明 |
|---|---|---|---|---|
| `type` | string | YES | — | 値の型（§7） |
| `required` | boolean | NO | `false` | 無条件に必須か |
| `required_if` | object | NO | — | 条件付き必須（§6.1） |
| `forbidden_if` | object | NO | — | 条件付き禁止（§6.1） |
| `enum` | array | NO | — | 許可される値の完全リスト |
| `minimum` | number | NO | — | 最小値（inclusive）。`number` / `integer` 型に適用 |
| `default` | any | NO | — | 省略時のデフォルト値 |
| `default_expr` | string | NO | — | 別パラメータの値から導出されるデフォルト（§6.2） |
| `description` | string | YES | — | パラメータが表すもの |

### 6.1 条件付き制約: `required_if` / `forbidden_if`

同一 keyword 内の別パラメータの値に依存する要件を表現する。

**スキーマ:**

```json
"required_if": { "<param_name>": ["<value1>", "<value2>", ...] }
"forbidden_if": { "<param_name>": ["<value1>", "<value2>", ...] }
```

**意味論:**

- `required_if`: `<param_name>` の値がリスト内のいずれかであれば、
  このパラメータは**必須**。
- `forbidden_if`: `<param_name>` の値がリスト内のいずれかであれば、
  このパラメータは**指定禁止**（指定するとエラー）。

**例**（`measurement.schema.json` より）:

```json
"time": {
  "type": "time_value",
  "required_if": { "rule": ["first", "time_only"] },
  "forbidden_if": { "rule": ["reinforcers_only"] }
}
```

意味:
- `rule="first"` または `rule="time_only"` のとき、`time` は必須。
- `rule="reinforcers_only"` のとき、`time` は指定禁止。

**制約:**
- `required_if` と `forbidden_if` のリストは重複してはならない（同一値が
  両方の配列に同時に現れてはならない）。
- 同一 keyword 定義内のパラメータのみ参照可能
- 1 パラメータあたり `required_if` と `forbidden_if` は各 1 つまで

### 6.2 導出デフォルト: `default_expr`

あるパラメータのデフォルト値が同一 keyword 内の別パラメータの値である
場合に使用する。

```json
"min_sessions": {
  "type": "integer",
  "minimum": 1,
  "default_expr": "window_sessions",
  "description": "Minimum total sessions before stability check"
}
```

意味: `min_sessions` が省略された場合、その値は `window_sessions` の値に
デフォルトされる。

**制約:**
- `default_expr` は同一 keyword の `params` 内に存在する別パラメータの名前を
  含む文字列。
- `default` と `default_expr` は排他的（同時指定不可）。
- 参照先パラメータは同一 keyword の `params` 内に必ず定義されていなければ
  ならない。

---

## 7. 型語彙

DSL grammar の `annotation_val` プロダクション（grammar.ebnf §4.7）に
対応する型識別子を定義する。

| 型識別子 | DSL 表面構文 | JSON 表現 | Grammar プロダクション |
|---|---|---|---|
| `"string"` | `"quoted text"` | JSON string | `string_literal` |
| `"number"` | `3.14` | JSON number | `number` |
| `"integer"` | `42` | JSON integer | `number`（意味論: 小数点なし） |
| `"time_value"` | `60min`, `30s`, `2000ms` | JSON number（秒に正規化） | `time_value` → `number time_unit` |
| `"object"` | `{key1=val1, key2=val2}` | JSON object | `annotation_object` |
| `"array<T>"` | `[val1, val2, ...]` | JSON array | `annotation_array` |

### 7.0 `array<T>` と `object`（構造化値）

Additive grammar 拡張（design-philosophy §8.1）として追加。対応する
grammar プロダクション `annotation_array` / `annotation_object`
は [grammar.ebnf](../../../schema/foundations/grammar.ebnf)（注釈付与セクション）に定義。

**`array<T>`** — 要素型 T の順序付き均一配列。T は本型語彙の任意の識別子
（`object` を含む）を取れる:

- `array<string>` — 文字列配列（例: `["AB", "BC"]`）
- `array<integer>` — 整数配列（例: `[1, 2, 3]`）
- `array<time_value>` — 時間値配列（例: `["3s", "150ms"]`）
- `array<object>` — オブジェクト配列（例: `[{role="probe", count=15}, ...]`）

**`object`** — ident → 値の写像。キーは `ident` プロダクション（英数字 +
アンダースコア）に従う。値は任意の `annotation_val` を取れるため
任意深度のネストが可能。

**後方互換:** 型識別子 `"array_of_string"` は `"array<string>"` の alias
として維持する（構造化値拡張以前に作成された schema — 例:
`procedure-stimulus.schema.json` の `relations` / `_variadic_named` —
との後方互換のため）。新規 schema は `"array<string>"` を使用すること。

### 7.1 `time_value` の正規化

DSL ソースでは時間値は明示的な単位（`s`, `ms`, `min`）を伴う。
AST およびスキーマ検証では**秒**に正規化した JSON number として扱う。
元の単位は正規化後に破棄される。

| ソース | 正規化値 |
|---|---|
| `60min` | `3600` |
| `30s` | `30` |
| `2000ms` | `2` |

プログラムは別の正規化規約を採用してよい。ただし本スキーマ形式は秒を正典単位として
仮定する。

### 7.2 `integer` と `number`

どちらも grammar の `number` プロダクションに対応する。区別は意味論的:

- `integer`: 小数点を含んではならない。カウント・インデックス等の離散量
- `number`: 小数点を含んでよい。持続時間・パーセンテージ等の連続量

### 7.3 型の拡張

型語彙は DSL grammar の `annotation_val` プロダクションに対応する。
以降の拡張は `grammar.ebnf` と本仕様の additive な同時更新を要する。

**サポート済み**:
- `array<T>` による任意型の配列（§7.0）
- `object` によるネストオブジェクト（§7.0）

**`annotation_val` が現時点でサポートしない**もの:
- スケジュール式への参照（整数インデックスまたは識別子による参照は
  validator レベルではサポート済みだが、型としてのファーストクラス化は未実装）
- ブールリテラル（`true` / `false`）

これらが必要になった場合、`annotation_val` への additive 拡張
（design-philosophy §8.1）と本仕様の型識別子追加が必要となる。

---

## 8. エイリアス

keyword は alias（同一 AST ノードに collapse する代替名）を宣言してよい。

### 意味論

1. すべての alias は AST レベルで primary keyword と**厳密に等価**
2. ソース上の keyword 名は `label` フィールドとして保持されるが、
   等価性判定では無視される
3. プログラムの registry は alias を全採用・primary のみ採用・
   独自追加のいずれも可能

### 制約

- Alias 名は他の keyword 名（同一 annotator 内および推奨 annotator 間）
  と衝突してはならない
- Primary keyword は `keywords` のキーとして記載される。
  Alias は `aliases` 配列に記載される

理論的根拠は design.md §3.5 を参照。

---

## 9. エラーコード

keyword は検証失敗時に実装が使用すべきエラーコードを宣言してよい。

```json
"errors": {
  "SESSION_END_MISSING_PARAM": "rule=first requires both time and reinforcers",
  "SESSION_END_INVALID_COMBO": "rule=time_only forbids reinforcers"
}
```

### 規約

- エラーコード名は UPPER_SNAKE_CASE
- keyword 名（大文字化）をプレフィックスとし、keyword 間の衝突を避ける
- 値は人間が読めるエラーメッセージテンプレート
- 実装はこれらのコード（またはスーパーセット）を使用しなければならない

---

## 10. スコープの意味論

`scope` 配列は annotation が DSL ソースのどこに出現できるかを宣言する。

| Scope | DSL 上の位置 | 意味論 |
|---|---|---|
| `"program"` | `param_decl*` / `binding*` / `schedule` の前 | セッション全体のデフォルト |
| `"schedule"` | `schedule` 式の後 | その式に付加。program-level を上書き |

**スコープ解決**（grammar.ebnf §4.7 より）:

```
resolve(key, S) = S.annotations[key]  if key in S.annotations
                  program.annotations[key]  otherwise
```

`scope: ["program", "schedule"]` の keyword は両レベルに出現できる。
schedule-level の annotation は、その式についてのみ program-level の
デフォルトを上書きする。

`scope: ["program"]` の keyword を schedule レベルで使うのは SemanticError。
`scope: ["schedule"]` の keyword を program レベルで使うのも SemanticError。

---

## 11. Registry 構築プロトコル

**registry** とは、特定のプログラムが認識する annotator の集合である。
registry はプログラム単位（design-philosophy §4.2）でスコープされる。

### 11.1 スキーマファイルからランタイム registry へ

```
schema/annotations/*.schema.json
    ↓  スキーマローダ（言語別）
AnnotationRegistry（ランタイムオブジェクト）
    ↓  パーサ統合
パーサが @keyword(...) を registry に対して検証
```

各実装言語のスキーマローダは:

1. 設定されたスキーマディレクトリから `*.schema.json` を読み取る
2. 各ファイルを本仕様（§4 メタスキーマ）に対して検証する
3. keyword → validator のマッピングを構築する
4. alias → primary keyword のマッピングを登録する
5. `validate(keyword, args) → Result` インターフェースを公開する

### 11.2 3rd-party registry

3rd-party のプログラムは本フォーマットで独自の registry を構築する:

- DSL プロジェクトの推奨スキーマファイル（全部または部分）を採用する
- 自身のスキーマファイル（同一フォーマット）を追加する
- 推奨 annotator を無視・置換する

すべての registry が同一スキーマフォーマットを共有するため、スキーマレベル
での相互運用性が保証される。registry A で妥当な DSL ソースは、registry B
のスキーマに対しても照合して互換性を判定できる。

### 11.3 Composite registry

プログラムは複数のスキーマファイルから自身の registry を合成してよい。
合成時の規則:

- スキーマファイル間で keyword 名の衝突はエラー（同一 annotator 内の
  alias → primary マッピングを除く）
- カテゴリメタデータは情報的であり、検証には影響しない

---

## 12. grammar.ebnf との関係

Annotation Schema Format は grammar.ebnf とは**異なるレイヤ**で機能する:

| 関心事 | 管轄 |
|---|---|
| Annotation **構文** (`@name(args)`) | grammar.ebnf §4.7 |
| Annotation **名前と引数スキーマ** | 本仕様 |
| Annotation **名前解決**（既知 vs 未知） | プログラム registry |

grammar.ebnf は annotation の構文形を以下のように定義する:

```ebnf
annotation       ::= "@" annotation_name ("(" annotation_args ")")?
annotation_val   ::= string_literal | time_value | number
```

本仕様は **どの `annotation_name` 値が存在するか** と
**それぞれが受け付ける引数形** を定義する。文法は意図的に開かれており
（任意の `annotation_name` が構文的に妥当）、スキーマは特定プログラムの
registry が名前と引数を検証するために使う意味論層を提供する。

---

## 13. 適合性要件

### スキーマファイルに対して

スキーマファイルが**適合**であるためには:

1. 有効な JSON であること
2. §4 の必須トップレベルプロパティをすべて含むこと
3. すべての keyword 定義が §5 の必須プロパティを含むこと
4. すべてのパラメータ定義が §6 の必須プロパティを含むこと
5. すべての `type` 値が §7 の型語彙に含まれること
6. `required_if` / `forbidden_if` のリストが重複しないこと
7. `default` と `default_expr` が排他的であること
8. `default_expr` が同一 keyword 内の既存パラメータを参照すること

### 実装に対して

実装が**適合**であるためには:

1. 任意の適合スキーマファイルをロードできること
2. ロードしたスキーマに対して annotation を検証すること
3. 検証失敗時に指定されたエラーコードを使用すること
4. §10 に従いスコープ解決を実装すること
5. `time_value` を秒に正規化すること（または規約を文書化すること）
6. alias を AST 上で primary keyword と等価に扱うこと

---

## 14. 現在の適合スキーマ

以下のスキーマファイルが本仕様に適合する:

| スキーマファイル | カテゴリ | Keywords | Status |
|---|---|---|---|
| `procedure-stimulus.schema.json` | Procedure | `reinforcer`, `sd`, `brief` | Schema Design |
| `procedure-temporal.schema.json` | Procedure | `clock`, `warmup`, `algorithm` | Schema Design |
| `procedure-trial-structure.schema.json` | Procedure | `trial_mix` (types: peak, reinstatement, temporal_bisection) | Proposed |
| `subjects.schema.json` | Subjects | `species`, `strain`, `deprivation`, `history`, `n` | Schema Design |
| `apparatus.schema.json` | Apparatus | `chamber`, `operandum`, `interface`, `hardware` | Schema Design |
| `measurement.schema.json` | Measurement | `session_end`, `baseline`, `steady_state` | Schema Design |

合計: 6 アノテーションスキーマファイル、18 keyword、JEAB 4 カテゴリ完全カバー。

注: `schema/experiment/` ディレクトリには多フェーズ実験デザイン用の構造スキーマ（`phase-sequence.schema.json`, `experiment.schema.json`）が別途存在する。これらはアノテーションスキーマではなく、Core AST 型とアノテーションを `$ref` で参照する構造スキーマである。

---

## 他の仕様との関係

本文書は [design-philosophy.md](../design-philosophy.md) に従属する:

- §4.2（program-scoped closure）が registry 構成を統治
- §4.3（カテゴリ中立的等価性）がカテゴリ意味論を統治
- §6（言語非依存性）が本仕様の動機
- §8（破壊的変更ポリシー）がスキーマ進化を統治

本文書の同格文書:

- [annotations/design.md](design.md) — annotation 境界原則と annotator 所有ポリシー
- [annotations/validation-modes.md](validation-modes.md) — tier × mode 検証

---

## Provenance

本仕様は 5 つの annotator スキーマファイルから事実上生まれた
de facto スキーマフォーマットを形式化したものである。
検討された代替案のうち Option (b) — JSON Schema 拡張 — として採択された。
