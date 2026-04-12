# contingency-dsl Validation Modes — Design Document

## Status: Revised (2026-04-12)

本文書は [design-philosophy.md](design-philosophy.md) §4 を前提とする。
両者が矛盾する場合は **design-philosophy.md が正典として優先する**。

本文書に記載する Tier × Mode モデルは、**DSL プロジェクトが提示する検証体系の
一例** であり、同時に Python リファレンス実装がどのような validator を
提供するかの仕様でもある。design-philosophy §4.2 の program-scoped closure
原則に従い、各プログラム（runtime / interpreter）は本モデルを採用・拡張・
置換する自由を持つ。本文書の記述は **強制ではなく推奨** である。

関連文書:
- [ja/design-philosophy.md](design-philosophy.md) §4 — Annotation 層の構造とカテゴリ（正典）
- [annotation-design.md](annotation-design.md) — 推奨 annotator とその境界原則
- [en/architecture.md](../en/architecture.md) §4.7 — annotation architecture
- [grammar.ebnf](../../grammar.ebnf) — 形式文法

---

## 1. 問題の所在

### 1.1 3種類の「必要性」の混在

ある annotation が「必要」である、という主張には性質の異なる 3 種類が
混在している。単一の必須/任意の二値判定ではこれらを区別できない:

| 種類 | 意味 | 欠落時に起こること |
|---|---|---|
| **実行必要性 (Execution)** | これがないとプログラムが動作しない | シミュレーション・実験が進行不能 |
| **公刊必要性 (Publication)** | 論文化・査読に必要 | 実行はできるが論文が accept されない |
| **分析必要性 (Analysis)** | データ解釈・統計分析に必要 | 実行はできるが分析結果が曖昧 |

### 1.2 二値判定が引き起こす具体的問題

**問題 A: 単一必須/任意判定の不十分性**

例えば `@session_end` について考える。これは物理実機で実験を実行するときは
「無いと止まらない」ので必須だが、理論的議論や virtual シミュレーションでは
全く不要である。単一の「必須/任意」フラグではこの文脈依存性を表現できず、
「どの状況で必須になるか」という情報が落ちる。

同様に `@species` は論文化時には必須だが、実行時には不要である。
これも単一フラグでは扱えない。

design-philosophy §4.2 の **program-scoped closure** 原則により、必須性は
プログラムごとに異なる。本文書はこの原則を具体化する一例として、Python
リファレンス実装が採用する 4 段階の tier と 4 モードの validator を提案する。

**問題 B: 学生の参入障壁**

```
FR 5                          -- 議論のためだけなら十分
Conc(VI 30-s, VI 60-s, COD=2-s)     -- 選択手続きの学習
```

この最小記述で議論できることが DSL の魅力だが、もし `@response(force_min=0.15)` や
`@session_end(time=60min)` を文法レベルで必須化すると、既に実験装置がラボにある
学生が「テストが通らず実験の提案が進まない」状況になる。

**核心の洞察**:
> **DSL は議論ツールとしての最小性と、実行ツールとしての厳密性の両方を担う必要があるが、
> これらは異なる「モード」で実現されるべきである**

---

## 2. 設計原則: 文法は permissive、validator は strict

Rust の型システム（parser は寛容、borrow checker は厳格）や
TypeScript の `--strict` モード、ESLint の rule set と同じ構造を採用する。

```
parse(src)                        → 文法的に正しいか (Tier 0 のみ)
lint(src, mode="dev")             → 開発モードで動くか (Tier 0-1)
lint(src, mode="production")      → 実機で動くか     (Tier 0-2)
lint(src, mode="publication")     → 論文化できるか   (Tier 0-3)
```

**4つの保証:**
1. **文法レベルの強制は最小限**: `FR 5` 単独で常に parse 成功
2. **下位 tier は上位 tier に影響されない**: publication linter の要求は dev mode に出ない
3. **モードは累積的・単調**: publication mode は dev mode の全要求を含む
4. **エラーメッセージは tier を示す**: どのモードで発動したかユーザーに明示

---

## 3. 4層の Requirement Tier

### Tier 0 — Core Grammar

**parse 自体が成立するために必要な要素。文法的要件。**

| 例 | 説明 |
|---|---|
| `FR 5` | atomic schedule |
| `Conc(VI 30-s, VI 60-s, COD=2-s)` | compound schedule + keyword args |
| `let x = VI 60-s \n Chain(x, FR 10)` | let bindings + compound |
| `LH = 10-s` | program-level parameter declaration |

**省略時の挙動**: parse error。これは文法で強制される。
**該当文書**: [grammar.ebnf](../../grammar.ebnf) の BNF 生成規則

### Tier 1 — Defaulted Execution Parameters

**実行時に値が必要だが、sensible default で補完できるパラメータ。**

| 例 | デフォルト | 根拠 |
|---|---|---|
| `@clock(unit="s")` | `"s"` | ratio schedules は dimensionless、interval/time は秒 |
| `@algorithm("fleshler-hoffman")` | Fleshler-Hoffman (1962) | 事実上の lab standard |
| `@hardware("virtual")` | `"virtual"` | default バックエンド |
| `@random(seed=<current_time>)` | 現在時刻 | 非再現でも実行は可能 |

**省略時の挙動**: validator が default を使って動作。warning なし。
**該当 annotator**: temporal, apparatus（一部）

### Tier 2 — Production Requirements

**`@hardware` が virtual 以外（physical HW）のとき必須となる要素。**
**シミュレーション（`@hardware("virtual")`）では不要。**

| 要素 | 根拠 |
|---|---|
| `@session_end(rule, time, reinforcers)` | セッション終了条件なしでは物理実験が止まらない |
| `@response(force_min, duration_min, irt_min, trigger)` | 物理 operandum では反応定義が動作の前提 |
| `@logging(resolution, events)` | データ収集なしでは実験に意味がない |
| `@hardware("teensy41")` 等の具体 HW | simulation から physical への切替 |
| `@operandum("left_lever", ...)` | 物理装置の identity |
| `@interface("serial", port=...)` | 物理接続情報 |

**省略時の挙動**:
- `mode="dev"`（virtual HW 想定）では無視
- `mode="production"`（physical HW 想定）では **production error**

**依存条件**: `@hardware` の値により発動/非発動が決まる（Tier は動的）

### Tier 3 — Publication Requirements

**論文化・査読・再現にのみ必要な要素。実験実行には一切不要。**

| 要素 | 論文セクション |
|---|---|
| `@species("rat")` | Subjects |
| `@strain("Long-Evans")` | Subjects |
| `@deprivation(hours=22, target="food")` | Subjects |
| `@history("naive")` | Subjects |
| `@pretraining(magazine=2, lever=3)` | Subjects / Procedure |
| `@n(6)` | Subjects |
| `@chamber("med-associates", model="ENV-007")` | Apparatus |
| `@reinforcer("sucrose", concentration="10%")` の詳細 | Procedure |
| `@context(houselight, masker)` | Apparatus / Procedure |
| `@ethics(irb, consent, assent)` | (Ethics statement) |
| `@ioa(method, percent)` | (Reliability) |

**省略時の挙動**:
- `mode="dev"`, `mode="production"` では無視
- `mode="publication"` では **publication error**

**該当 annotator**: subject, apparatus（詳細）, ethics（将来）

### Tier の独立性

**重要**: Tier は「必要性の種類」であり「重要度の順序」ではない。

- Tier 3 (`@species`) は Tier 2 (`@session_end`) より「重要度が低い」わけではない
- 論文化フェーズでは Tier 3 要素がないと論文が書けない
- 実験実行フェーズでは Tier 2 要素がないと実験が動かない
- **各フェーズで「その時点で必要なもの」だけを要求する**のが validation mode の役割

---

## 4. 4つの Validation Mode

### 4.1 mode="parse" — 文法検証のみ

```python
parse("FR 5")                 # OK
parse("Conc(VI 30-s, VI 60-s)")  # OK (COD 省略は semantic warning のみ)
parse("@species(\"rat\")")   # 依然として parse OK（annotation 受理）
```

- **対象**: Tier 0
- **用途**: 構文学習、理論議論、教材、単体テスト
- **エラー**: parse error, semantic error のみ
- **警告**: なし

### 4.2 mode="dev" — 開発/シミュレーション

```python
lint("FR 5", mode="dev")
# → OK (warning: no @hardware specified, assuming @hardware("virtual"))

lint("Conc(VI 30-s, VI 60-s, COD=2-s) @hardware(\"virtual\")", mode="dev")
# → OK
```

- **対象**: Tier 0-1
- **用途**: 学生の学習、理論検証、シミュレーション実行、CI テスト
- **前提**: `@hardware("virtual")` またはデフォルト（virtual 扱い）
- **エラー**: parse/semantic error
- **警告**: Tier 1 の defaulted 要素が未指定なら info 出力（エラーにしない）
- **例**: `FR 5` 単体でシミュレーション実行可能

### 4.3 mode="production" — 実機実行

```python
lint("FR 5 @hardware(\"teensy41\")", mode="production")
# → ERROR: @session_end required for physical HW
# → ERROR: @response required for physical HW
# → ERROR: @logging required for physical HW
# → ERROR: @operandum required for physical HW
```

- **対象**: Tier 0-2
- **用途**: 実機実験のゲートキーパー、実験前の最終検証
- **発動条件**: `@hardware` が virtual 以外のとき自動発動
- **エラー**: Tier 2 要素の欠落
- **警告**: Tier 3 要素の欠落（publication で困る旨）

**§8 で示した「必須化」要求はここで実現される**。parser は拒否しないが、
物理実機を繋いだ瞬間に validator が止める。

### 4.4 mode="publication" — 論文コンパイル

```python
lint(src, mode="publication")
# → ERROR: @species required for Methods section
# → ERROR: @strain required for Methods section
# → ERROR: @deprivation required for Methods section
# → ERROR: @chamber required for Apparatus section
# → ERROR: @n required for Subjects section
```

- **対象**: Tier 0-3
- **用途**: 論文 Methods セクション自動生成、preregistration 提出、supplement 公開
- **エラー**: Tier 3 要素の欠落
- **出力**: DSL ソース + validation pass で APA Methods section を生成可能

---

## 5. モードの単調性と学生の経路

### 5.1 累積性の保証

```
parse ⊆ dev ⊆ production ⊆ publication
```

上位モードが受理するプログラムは必ず下位モードでも受理される。
下位モードで通るプログラムが上位モードで落ちることは許容する。

### 5.2 Progressive Enrichment の形式化

現在 [docs/en/annotations.md](../../docs/en/annotations.md) に非形式的に記述されている
"progressive enrichment" を validation mode の観点から形式化する:

| 段階 | DSL ソース | 通るモード |
|---|---|---|
| 理論議論 | `FR 5` | parse |
| 学生の学習 | `Conc(VI 30-s, VI 60-s, COD=2-s)` | parse, dev |
| シミュレーション | 上記 + `@clock(unit="s")` + `@algorithm(...)` | parse, dev |
| 実機実験準備 | 上記 + `@hardware("teensy41")` + `@session_end(...)` + `@response(...)` + `@operandum(...)` + `@logging(...)` | parse, dev, production |
| 論文投稿 | 上記 + `@species` + `@strain` + `@deprivation` + `@chamber` + `@n` | parse, dev, production, publication |

### 5.3 学生の典型的経路

```
ステップ 1: 議論
  ユーザー: "FR 5 と FI 10 の違いが知りたい"
  DSL: FR 5 / FI 10-s
  モード: parse ✓

ステップ 2: 選択手続き
  ユーザー: "並立 VI-VI を見たい"
  DSL: Conc(VI 30-s, VI 60-s, COD=2-s)
  モード: parse ✓, dev ✓（virtual で回せる）

ステップ 3: シミュレーション
  ユーザー: "シミュレーションを走らせたい"
  DSL: 上記 + @algorithm("fleshler-hoffman", seed=42)
  モード: dev ✓

ステップ 4: 実機接続
  ユーザー: "Teensy に繋ぎたい"
  DSL: @hardware("teensy41") を追加
  モード: production ✗
  エラー:
    - @session_end: physical HW requires explicit termination rule
    - @response: physical HW requires force/IRT specification
    - @operandum: physical HW requires operandum identity
    - @logging: physical HW requires logging specification
  → 学生はここで初めて「実機を動かすのに何が必要か」を強制的に学ぶ

ステップ 5: 実験実行
  DSL: 上記 + @session_end + @response + @operandum + @logging
  モード: production ✓

ステップ 6: 論文化
  ユーザー: "Methods セクションを生成したい"
  モード: publication ✗
  エラー:
    - @species, @strain, @deprivation, @chamber, @n が未指定
  → 学生は論文フェーズで初めて publication-level を要求される
```

**この経路の設計上の保証:**
- ステップ 1-3 で Tier 2, 3 の存在を学生は知る必要がない
- Tier は「使いたくなった段階」で自然に登場する
- 議論・学習・シミュレーションでは DSL は最小限のまま

---

## 6. annotation-design.md との整合

### 6.1 境界テストと Tier の関係

annotation-design.md §2 の境界テスト（Q1-Q3）が **Core vs Annotation** を判定する。
3 問の具体的な内容は §2 の唯一の定義に従い、本文書では再掲しない。
本節の Tier 分類は、§2 が「annotation 候補」と判定した後に
**特定プログラム（この Python リファレンス実装）内で** どのモードで
要求されるかを決定する。両者は責任範囲が異なる。

本 Python リファレンス実装が採用する意思決定フロー:

```
前提: annotation-design.md §2 の境界テスト (Q1-Q3) で
「Core 昇格を検討」ではなく「Annotation 候補」と判定済み
（YES → grammar.ebnf を design-philosophy §8 の制約下で改訂）
  ↓
Tier 分類 (本文書)
  T-A: @X は defaulted パラメータか? (例: @clock unit)
    YES → Tier 1
    NO  → ↓
  T-B: @X は physical HW 接続時に要求されるか? (例: @session_end)
    YES → Tier 2 (production で必須)
    NO  → ↓
  T-C: @X は論文化フェーズで要求されるか? (例: @species)
    YES → Tier 3 (publication で必須)
    NO  → Tier 1 (参考用メタデータ)
```

**注意:** 上記 Tier 分類は本 Python リファレンス実装の validator が従う
ルールである。別のプログラムが別の tier 分類を採用することは
design-philosophy §4.2 により許容される。

### 6.2 annotation-design.md §8 既存提案の再分類

annotation-design.md §8 で列挙されたプログラムレベル拡張を tier で再分類する:

| 現 §8 提案 | 再分類後の Tier |
|---|---|
| `@session_end` | **Tier 2** (production) — §8 の主張はここで実現 |
| `@response(force, IRT)` | **Tier 2** (production) |
| `@logging` | **Tier 2** (production) |
| `@clock(unit)` | **Tier 1** (defaulted, s) |
| `@clock(precision, sampling, sync)` | **Tier 2** (production) |
| `@random(seed)` | **Tier 1** (defaulted, current time) |
| `@timeout` | **Tier 2** (production, conditional) |
| `@session_onset` | **Tier 2** (production) |
| `@reinforcer(clock_resume)` | **Tier 2** (production) |
| `@species`, `@strain` | **Tier 3** (publication) |
| `@deprivation`, `@history`, `@n` | **Tier 3** (publication) |
| `@pretraining` | **Tier 3** (publication) |
| `@chamber(model)` | **Tier 3** (publication) |
| `@context(houselight)` | **Tier 2** (production, physical apparatus) |
| `@drug`, `@phase`, `@preparation` | **Tier 3** (publication) + `@phase` は Tier 2 |
| `@pr_breakpoint` | **Tier 2** (production) |
| `@ioa`, `@ethics`, `@function` | **Tier 3** (publication) |

### 6.3 §2 の原則維持

「annotation は直交的メタデータであり、評価意味論を変えない」という §2 の核心原則は
validation mode 導入後も**維持される**。変わるのは、
「要求レベルが複数段階に分岐する」という拡張のみ。

- parser は依然として annotation を optional として受理
- annotation の有無は schedule 式の数学的性質を変えない
- validator (tier-aware) が mode に応じて要求を発動する

---

## 7. Layer Responsibility Matrix

§8.4 の責務分離を validation mode と tier の観点から再整理する:

### 7.1 4つのレイヤー

| レイヤー | 役割 | 永続化単位 |
|---|---|---|
| **DSL (contingency-dsl)** | 実験計画の静的構造 (Tier 0-3) | `*.dsl` ファイル |
| **session-recorder** | 実行時ログと実測値 | `*.jsonl` イベントログ |
| **experiment-io** | ハードウェア抽象と event code | HW ドライバ + マッピング |
| **manifest** | 実験計画の外部メタデータ | `study.yaml` / `manifest.yaml` |

### 7.2 項目別責務

| 項目 | レイヤー | 理由 |
|---|---|---|
| schedule expression | DSL (Tier 0) | 文法の中核 |
| `@hardware`, `@clock`, `@random` | DSL (Tier 1) | 実行パラメータ |
| `@session_end`, `@response`, `@operandum`, `@logging` | DSL (Tier 2) | 実機実行の宣言 |
| `@species`, `@strain`, `@chamber(model)` | DSL (Tier 3) | 論文化メタデータ |
| `session_id`, `timestamp` | session-recorder | 実行時アーティファクト |
| 実測 IRT, 実測強化間間隔 | session-recorder | runtime 測定値 |
| calibration 実測値 | session-recorder | 実行時測定 |
| calibration 期待値 | DSL (`@hardware(expected=...)`) | 計画の一部 |
| event code マッピング | experiment-io | HW 抽象の責務 |
| software versions | session-recorder (manifest 埋め込み) | 古びるため DSL に書かない |
| `experiment_id`, `subject_id` | **manifest** (DSL の外) | 「誰が」「どの試行か」は計画構造ではない |
| `institution`, `grant`, `preregistration` | manifest | 実験計画ではない |
| `irb_number`, `iacuc_number` | manifest (opaque) | 監査証跡 |
| `schedule vs obtained` 保証 | DSL schema (宣言) + recorder (記録義務) | 両方の存在を強制 |

### 7.3 再現性単位原則の再定式化

> **「次回も同じ実験ができるか」は DSL、「今回何が起きたか」は recorder**

を tier 化すると:

- **Tier 0-2**: 「次回も同じ実験を実機で動かすために必要な情報」
- **Tier 3**: 「次回も同じ論文を書けるために必要な情報」
- **session-recorder**: 「今回何が起きたかの記録」
- **manifest**: 「誰が・いつ・どの試行かの外部メタデータ」

### 7.4 `experiment_id` / `subject_id` を DSL に置かない理由

annotation-design.md §8.4 で提案された
「`subject_id`, `experiment_id` は DSL」という分類は、
この document で **manifest 層へ移す**ことを提案する:

- DSL は **実験計画の構造** を定義する（"どういう実験か"）
- 「誰が・どの試行か」は計画の**適用**（"誰にこの計画を使うか"）であり、
  計画そのものではない
- 同一の DSL ファイルを複数の被験体・複数の日に適用可能にするには、
  `subject_id` / `experiment_id` / `date` は外部 manifest に分離する必要がある

```yaml
# manifest.yaml
experiment: dose-response-cocaine
protocol: sessions/fr5_baseline.dsl
subjects:
  - id: R12
    date: 2026-04-11
  - id: R15
    date: 2026-04-12
```

DSL ファイルは複数の実行インスタンスに**再利用可能**になる。
これは「再現性の単位」設計原則とも整合する（DSL が "同じ実験" を定義し、
manifest が "どの試行か" を定義する）。

---

## 8. 実装ノート

### 8.1 validator API の概形

```python
from contingency_dsl import parse, validate

# Tier 0 のみ
ast = parse("FR 5")

# Tier 0-1
validate(ast, mode="dev")

# Tier 0-2: @hardware の値により Tier 2 要求が発動
validate(ast, mode="production")

# Tier 0-3
validate(ast, mode="publication")
```

戻り値は診断メッセージのリスト。各メッセージは tier, severity, message を持つ。

### 8.2 Tier 2 の動的発動

`@hardware` が `"virtual"` なら Tier 2 要素は緩和される:

```python
# これは production mode でも通る（virtual HW なので）
validate(parse('FR 5 @hardware("virtual")'), mode="production")
# → OK (Tier 2 要素は virtual では要求されない)

# これは production mode で落ちる
validate(parse('FR 5 @hardware("teensy41")'), mode="production")
# → ERROR: @session_end required (Tier 2)
# → ERROR: @response required (Tier 2)
```

### 8.3 モードの独立性テスト

**不変条件:**
```python
for mode in ["parse", "dev", "production", "publication"]:
    for src in ALL_VALID_MINIMAL_SRCS:
        assert validate(parse(src), mode=mode).ok
```

`FR 5` のような最小例は**全モードで通る**ことを保証する
（全 mode で Tier 0 のみを要求するプログラムは常に OK）。

### 8.4 エラーメッセージの tier 表示

```
error[E-tier2]: @session_end is required for physical HW
  --> session.dsl:1:1
  |
1 | FR 5 @hardware("teensy41")
  |     ^^^^^^^^^^^^^^^ physical HW specified here
  |
  = note: this requirement is active in mode="production"
  = note: to skip this check, use @hardware("virtual") or mode="dev"
  = help: add @session_end(rule="first", time=60min, reinforcers=60)
```

tier, mode, 回避方法をエラーメッセージに明示する（Rust の diagnostic 形式を参考）。

---

## 9. 未解決の設計課題

### 9.1 Tier の動的性

`@hardware` の値により Tier 2 発動/非発動が変わる機構は単純だが、
他にも動的 tier が必要か検討する:

- `@phase("extinction")` のとき `@reinforcer` は不要になるか?
- Multiple schedule のとき `@sd` が必須化するか?

### 9.2 Tier の所有

- Tier 分類は annotation 自身が宣言する（自己記述）のか?
- それとも external tier registry を作るのか?

メタDSL（annotation-design.md §7）導入時にこの決定を行う。

### 9.3 mode の階層の柔軟性

`"dev"`, `"production"`, `"publication"` 以外のモードが必要か:
- `"teaching"` — Tier 0 のみ、警告もなし（教材用）
- `"simulation_precise"` — dev と production の中間
- `"preregistration"` — publication より厳しく pre-analysis plan まで要求

将来の拡張は mode の set を増やすことで対応可能（単調性が保たれる限り）。

### 9.4 Warning vs Error の境界

Tier 1 の警告と Tier 2 のエラーの境界は固定か、ユーザー設定可能か。
ESLint のような rule set の有効化/無効化を許すか。

---

## 10. 参照

- Sidman, M. (1960). *Tactics of scientific research*. Basic Books.
- Baron, A., & Perone, M. (1998). Experimental design and analysis in the laboratory study of human operant behavior. In K. A. Lattal & M. Perone (Eds.), *Handbook of research methods in human operant behavior* (pp. 45-91). Plenum.
- Fleshler, M., & Hoffman, H. S. (1962). A progression for generating variable-interval schedules. *JEAB*, 5(4), 529-530. https://doi.org/10.1901/jeab.1962.5-529
- annotation-design.md §2（境界テスト）, §6（二層スコーピング）, §8（プログラムレベル拡張）
- en/architecture.md §4.7（annotation architecture）
- docs/en/annotations.md / docs/ja/annotations.md（Progressive Enrichment の非形式的記述）