# バージョニング戦略

> [contingency-dsl spec](architecture.md) の一部。DSL バージョン管理、アノテータ機能発見、後方互換性保証、および設計変更ログを定義する。

**Status:** Draft (2026-04-14; 2026-04-17 更新)
**Addresses:** EXTENSION_RULES_REVIEW §3.7 —「バージョニング戦略の欠如」

---

## 0. 設計変更ログ

本節は DSL アーキテクチャに対する設計変更のログである。バージョン宣言
とは区別される: 当リポジトリは現時点で git remote が設定されておらず、
バージョン番号は公開されていない。各エントリは **設計チェックポイント**
であって、バージョン更新ではない。

### 2026-04-17 — Ψ 再編（設計チェックポイント、バージョン更新ではない）

**背景。** 以前の Core / Core-Stateful / Core-TrialBased という命名は、
形式構造の軸と科学的カテゴリを混同させていた。Ψ は科学的カテゴリ
（foundations / operant / respondent / composed / experiment /
annotations）によって再編し、Skinner (1938) の operant と Pavlov
(1927) の respondent の区別をディレクトリレベルで反映する。また
Rescorla & Solomon (1967) の two-process 理論を第一級姉妹
（`composed/`）として収容可能にする。Experiment 層と Context は
第一級となり、将来の renewal / reinstatement 手続きを respondent
extension point 経由で表現できるようにする。

**範囲。** `spec/{en,ja}/`, `schema/`, `conformance/`, `dist/`,
`docs/{en,ja}/` にまたがるディレクトリ再編に加え、Tier B respondent
手続き（blocking、overshadowing、latent inhibition、renewal、
reinstatement、spontaneous recovery、counterconditioning、
occasion-setting などを含む）をカバーする新規パッケージ
`operantkit/apps/core/contingency-respondent-dsl` を新設する。

**層対応表（旧 → 新）。**

| 旧 | 新 |
|---|---|
| `Core` | `Operant.Literal`（`operant/schedules/`） |
| `Core-Stateful` | `Operant.Stateful`（`operant/stateful/`） |
| `Core-TrialBased` | `Operant.TrialBased`（`operant/trial-based/`） |
| （Core / Experiment に暗黙） | `Foundations`（paradigm-neutral 形式基盤） |
| （不在） | `Respondent`（二項 CS-US primitive + extension point） |
| （不在） | `Composed`（operant × respondent: CER, PIT, autoshaping, omission, two-process） |
| `Experiment` | `Experiment`（第一級化、Context を含む） |
| `Annotation` | `Annotation`（`extensions/respondent-annotator` を含む） |

**バージョン更新ではない。** 当リポジトリは git remote が未設定であり、
バージョン宣言は公開まで保留される。本エントリは design-philosophy.md
§8.3（正典に対する非 additive 変更の理由記録義務）の権限で、設計
チェックポイントとして記録される。

**関連作業。**

- `annotations/extensions/respondent-annotator` を新設し、`@cs`,
  `@us`, `@iti`, `@cs_interval` を提供
- `respondent/grammar.md` に Respondent extension point
  （`ExtensionRespondentPrimitive`）を新設; Operant 層の既存の
  Schedule Extension 点と並置
- Tier A respondent primitive を design-philosophy §2 と
  `respondent/primitives.md` に列挙: `Pair.{ForwardDelay,
  ForwardTrace, Simultaneous, Backward}`, `Extinction`, `CSOnly`,
  `USOnly`, `Contingency(p_us_given_cs, p_us_given_no_cs)`,
  `TrulyRandom`, `ExplicitlyUnpaired`, `Compound`, `Serial`, `ITI`,
  `Differential(cs+, cs−)`

---

## 1. 問題定義

DSL は `AnnotationModule.version`（semver）を定義し、`schema-format.md` は各アノテータスキーマに `"version"` フィールドを要求している。しかし以下の機構が存在しない:

1. DSL ソースレベルでの破壊的変更検出
2. 適合性テストの version pin
3. Tier 分類のバージョン管理
4. アノテータ v1.0 向けに書かれた DSL ソースが v1.0 で暗黙に壊れることの防止

バージョニング戦略がなければ、暗黙の互換性仮定が蓄積し、アノテータの進化に伴い破綻する。

---

## 2. 設計アプローチ: 機能発見（Capability Discovery）

明示的バージョンプラグマではなく **機能発見** を採用する。理由:

- バージョンプラグマ（`#[dsl_version = "1.0"]`）はボイラープレートを生み、省略時のデフォルト挙動が曖昧になる
- semver の diamond dependency 問題が複数アノテータ間で発生する
- 機能発見は **宣言的**: ソース自体が使用するキーワード/機能により必要なものを宣言する。レジストリがロード済みアノテータでそれらを充足できるか検証する

### 2.1 核心原則

> DSL ソースファイルの必要機能は、その内容の静的解析により完全に決定される。レジストリは、ロード済みアノテータがそれらの機能を互換バージョンで提供しているか検査する。

つまり:

- `FR5` 単体ではアノテータ不要 — 機能集合は空
- `FR5 @reinforcer("sucrose")` は `procedure.stimulus >= 1.0` を要求
- `@species("rat") FR5 @reinforcer("sucrose")` は `procedure.stimulus >= 1.0` AND `subjects >= 1.0` を要求

---

## 3. 機能識別子

### 3.1 形式

```
<category>[.<sub_annotator>] @ >= <major>.<minor>
```

例:

| 機能 ID | 意味 |
|---|---|
| `procedure.stimulus@>=1.0` | procedure-annotator の stimulus サブアノテータ v1.0 以上 |
| `procedure.temporal@>=1.0` | procedure-annotator の temporal サブアノテータ v1.0 以上 |
| `subjects@>=1.0` | subjects-annotator v1.0 以上 |
| `apparatus@>=1.0` | apparatus-annotator v1.0 以上 |
| `measurement@>=1.0` | measurement-annotator v1.0 以上 |

### 3.2 スキーマからの導出

各アノテータスキーマ（`*.schema.json`）は `category`、`sub_annotator`（任意）、`version` を既に宣言している。機能 ID は機械的に導出される:

```
capability_id = category + ("." + sub_annotator if sub_annotator else "") + "@>=" + version
```

### 3.3 バージョン意味論

アノテータバージョンは DSL 固有の解釈を持つ semver に従う:

| 変更種別 | バージョンバンプ | 例 |
|---|---|---|
| 新しいオプションキーワードの追加 | MINOR | measurement-annotator に `@baseline` を追加 |
| 既存キーワードへの新しい必須パラメータ | MAJOR | `@reinforcer` が `modality` を必須化 |
| キーワードの削除・改名 | MAJOR | `@sd` を `@discriminative_stimulus` に改名 |
| パラメータ型の変更 | MAJOR | `@clock(resolution)` が string → number |
| デフォルト値の変更（意味的影響あり） | MAJOR | `@session_end(rule)` のデフォルト `"first"` → `"last"` |
| 記述/ドキュメントのみ | PATCH | `@species` の説明文更新 |
| エラーコードの追加（新しいバリデーション） | MINOR | 新エラー `E_STRAIN_UNKNOWN` |

---

## 4. 機能解析

### 4.1 静的解析関数

```python
def analyze_capabilities(source: str) -> frozenset[str]:
    """DSL ソースが要求する機能集合を抽出する。

    アノテーション使用箇所をスキャンし、各アノテーションキーワードを
    レジストリのスキーマに基づきアノテータ（category.sub_annotator）に
    マッピングする。
    """
    ...
```

### 4.2 例

```python
source = """
@species("rat")
@deprivation("food", hours=23)
@reinforcer("sucrose", magnitude="0.1ml")
@chamber("med-associates", model="ENV-007")
VI 30s @clock(resolution="1ms")
"""

required = analyze_capabilities(source)
# → frozenset({
#     "subjects@>=1.0",
#     "procedure.stimulus@>=1.0",
#     "procedure.temporal@>=1.0",
#     "apparatus@>=1.0",
# })
```

### 4.3 レジストリ検証

```python
@dataclass(frozen=True)
class AnnotationRegistry:

    @staticmethod
    def build(*annotators: AnnotationModule) -> "AnnotationRegistry":
        """レジストリを生成する。以下の場合 ValueError:
        - 2 つのアノテータが同一キーワードを主張（disjointness 違反）
        - アノテータの requires 集合が未充足（依存性違反）
        """
        ...

    def validate_capabilities(self, required: frozenset[str]) -> None:
        """要求された全機能がロード済みアノテータにより充足されるか検査する。

        Raises:
            MissingCapabilityError: アノテータが未ロードまたはバージョン不足
        """
        ...
```

### 4.4 エラー報告

```
MissingCapabilityError: DSL source requires 'subjects@>=1.0' but no
subjects-annotator is loaded. Either:
  1. Add SubjectsAnnotator() to the registry, or
  2. Remove @species/@strain/@deprivation annotations from the source.

VersionTooLowError: DSL source requires 'procedure.stimulus@>=1.1'
(keyword @reinforcer with param 'modality' introduced in v1.0),
but loaded procedure-annotator provides stimulus v1.0.
```

---

## 5. DSL コアバージョン

DSL コア文法自体もバージョンを持つ。これはアノテータバージョンとは独立。

### 5.1 コアバージョンスコープ

| コンポーネント | 現バージョン | バージョン管理主体 |
|---|---|---|
| 基本文法 (grammar.ebnf) | 1.0 | DSL コアバージョン |
| コンビネータ (Conc, Alt, Chain, ...) | 1.0 | DSL コアバージョン |
| アノテーション構文 (`@name(args)`) | 1.0 | DSL コアバージョン |
| 個別アノテータスキーマ | アノテータ毎 | アノテータバージョン (§3) |
| バリデーションモード | 1.0 | DSL コアバージョン |
| 表現系 (T-tau 等) | 表現毎 | 表現バージョン |

### 5.2 オプションのソースヘッダ

明示的バージョン固定（opt-in、必須ではない）:

```
#[dsl = "1.0"]

@species("rat")
FR5 @reinforcer("sucrose")
```

存在する場合、パーサはその文法バージョンが宣言バージョンと互換であるか検証する。不在の場合、パーサは自身のバージョン（最新）を使用する — これがインタラクティブ/教育用途でのデフォルト。

---

## 6. 適合性テストのバージョニング

### 6.1 テストスイート構造

```
conformance/
├── foundations/
├── operant/
│   ├── stateful/
│   └── trial-based/
├── respondent/
├── composed/
├── experiment/
├── annotations/
│   ├── procedure-stimulus/
│   ├── subjects/
│   └── ...
└── compatibility.yaml  # バージョン互換性マトリクス
```

### 6.2 互換性マトリクス

```yaml
# conformance/compatibility.yaml
operant:
  - checkpoint: "Ψ"
    test_suite: conformance/operant/
  - checkpoint: "Ψ+additive"
    test_suite: conformance/operant/
    backward_compatible_with: "Ψ"

annotators:
  procedure.stimulus:
    - checkpoint: "Ψ"
      test_suite: conformance/annotations/procedure-stimulus/
    - checkpoint: "Ψ+additive"
      test_suite: conformance/annotations/procedure-stimulus/
      backward_compatible_with: "Ψ"
      migration: migrations/procedure-stimulus-Ψ-to-Ψ-additive.md
```

### 6.3 CI 強制

`compatibility.yaml` 内の `backward_compatible_with` を宣言する各バージョンエントリは、参照バージョンの全テストスイートに合格しなければならない。CI が互換性マトリクスを実行し、マイナーバージョンバンプが後方互換性を破壊していないことを検証する。

---

## 7. Tier バージョン管理

`validation-modes.md` の Tier 分類（Tier 1-4）は DSL の成熟に伴い変更されうる。当初 Tier 4（Extension）だったキーワードが普遍的に必要と判明すれば Tier 3（Publication）に昇格されうる。

### 7.1 Tier 変更ポリシー

| 変更 | 影響 | 要件 |
|---|---|---|
| 昇格 (Tier 4 → 3, 3 → 2) | 非破壊 — 上位モードでバリデーションが厳格化 | アノテータの MINOR バージョンバンプ |
| 降格 (Tier 2 → 3, 3 → 4) | 潜在的破壊 — 必須だったアノテーションがオプションに | アノテータの MAJOR バージョンバンプ |
| 任意 Tier での新キーワード | 既存ソースに非破壊 | MINOR バージョンバンプ |
| キーワード削除 | 破壊的 | MAJOR バージョンバンプ |

### 7.2 Tier 履歴

各アノテータスキーマは `tier_history` フィールドを含むべき（SHOULD）:

```json
{
  "keywords": {
    "reinforcer": {
      "tier": 3,
      "tier_history": [
        { "version": "1.0", "tier": 3 },
        { "version": "0.9", "tier": 4 }
      ]
    }
  }
}
```

---

## 8. マイグレーションガイド

MAJOR バージョンバンプ時は、以下のパスにマイグレーションガイドを提供しなければならない（MUST）:

```
migrations/<annotator>-<old>-to-<new>.md
```

各マイグレーションガイドは以下を含むこと:

1. **破壊的変更**: 非互換な変更の網羅リスト
2. **自動修正**: 機械的なソース変換が存在する場合、それ（またはスクリプト）を提供
3. **手動レビュー**: 人間の判断を要する変更
4. **適合性差分**: 追加されたテストケース、廃止されたテストケース

---

## 9. まとめ

| 機構 | 目的 | 適用タイミング |
|---|---|---|
| 機能発見 (§4) | 不足/旧版アノテータのロード時検出 | 毎回のパース |
| オプション `#[dsl = "X.Y"]` ヘッダ (§5.2) | 明示的コアバージョン固定 | opt-in |
| 適合性マトリクス (§6) | CI 強制の後方互換性 | 毎回の CI 実行 |
| Tier 履歴 (§7.2) | Tier 分類の進化追跡 | スキーマ更新時 |
| マイグレーションガイド (§8) | 人間可読なアップグレードパス | MAJOR バンプ時 |
