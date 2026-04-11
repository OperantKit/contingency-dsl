# contingency-dsl Annotations — Design Document

## Status: Revised (2026-04-12)

本文書は [spec/ja/design-philosophy.md](ja/design-philosophy.md) §4 を前提とする。
両者が矛盾する場合は **design-philosophy.md が正典として優先する**。

関連文書:
- [ja/design-philosophy.md](ja/design-philosophy.md) §4 — Annotation 層の構造とカテゴリ（正典）
- [validation-modes.md](validation-modes.md) — 各プログラムにおける tier × mode 検証の設計例
- [grammar.ebnf](../grammar.ebnf) §4.7 — Annotation 構文とプログラムスコープ closure

---

## 1. 方針: 言語非依存な annotation schema

Annotation の意味定義は、特定の実装言語（Python / Rust / Kotlin 等）の
型システムに閉じ込めず、**言語非依存な schema 記述**として定義する。
これは design-philosophy §5（言語非依存性は実質的要件）の具体化である。

### 動機

1. **言語非依存性** — 同一の annotation schema を複数言語の実装が参照し、
   等価に解釈できる。
2. **実験の正準表現** — DSL ソース（Core + annotations）が実験手続きの
   single source of truth として機能する。
3. **論文コンパイル** — DSL ソースを自然言語の Method / Procedure セクションに
   コンパイルできる。曖昧性ゼロの再現可能な手続き記述。

### 「メタDSL」の位置付け — 一元定義ではない

旧版の本文書は「DSL プロジェクトが一元的にメタDSL を定義し、
すべての実装がそれに準拠する」という前提で書かれていた。
design-philosophy §4.2 以降、この前提は **撤回** されている:

- Annotation の schema は **プログラム（runtime / interpreter）が提供する
  registry** に属する。DSL spec 自身は「推奨」を提示するのみ。
- カテゴリ（Procedure / Subjects / Apparatus / Measurement 等）は
  **推奨分類** であり強制ではない。3rd-party は自由に新カテゴリを定義し、
  既存カテゴリを無視・再定義できる。
- したがって「メタDSL」という言葉が意味するのは、
  **「各プログラムの registry を記述するための言語非依存な schema 形式」** である。
  それ以上のものではない。

### 現状との関係

本 spec は、既存の `contingency-dsl-py` の `AnnotationModule` Protocol を
「**DSL プロジェクトが提供する Python リファレンス実装**」として位置付ける。
他言語実装は同等の schema 形式に従う限り自由に構築でき、Python 実装との
準拠関係は schema 記述によって担保される。

```
言語非依存 schema（推奨・参照）
    ↓ 各プログラムが実装
AnnotationModule (Python)  ← 参照実装
AnnotationModule (Rust)    ← 参照実装（将来）
3rd-party registry          ← 上記を無視して独自に構築してもよい
```

---

## 2. コア DSL と Annotation の境界原則

### 原則: annotation はコアの意味論を変えない

Annotation の有無で Core schedule 式の評価意味論が変わってはならない。
`FI 10` は `FI 10 @clock(unit="s")` と意味論的に等価であり、
後者は前者に情報を付加しているだけである。

```
FI 10                           -- 理論的に完結。スキャロップを議論できる
FI 10 @clock(unit="s")          -- 時間単位を明示。FI の性質は変わらない
FI 10 @clock(unit="s")          -- 実験を実行するには必要だが
      @operandum("left_lever")     FI 10 の性質の議論には不要
      @reinforcer("pellet")
      @subject(species="rat")
```

### 境界テスト（Core vs Annotation の判定）

提案された候補 `@X` に対し、以下の質問で Core 文法への昇格が必要か、
それとも annotation として扱えるかを判定する:

| # | 質問 | YES → | NO → |
|---|---|---|---|
| 1 | `@X` がないと schedule の理論的性質（FI スキャロップ等）を議論できないか | Core 文法の一部である。Annotation ではなく Core への追加を検討 | annotation 候補 |
| 2 | `@X` は schedule 式の評価意味論を変えるか | Core 文法の variant（例: FI-resetting）である。Core への追加を検討 | annotation 候補 |
| 3 | `@X` は Core 文法レベルで必須か（プログラムの registry に依存せず、DSL spec 全体で必須と主張できるか） | Core 文法への昇格を検討。ただし design-philosophy §7 により破壊的変更は原則回避 | annotation 候補 |

### 注記: 「Parse error になるか」は DSL レベルでは判定不能

旧版の境界テストには「`@X` がないとコアが parse error になるか → 設計誤り」
という第 4 問が含まれていた。これは design-philosophy §4.2 の
**program-scoped closure** 原則と整合しない:

- Parse error が発生するかどうかは **そのプログラムの registry** に依存する。
- DSL spec は特定のプログラムを前提とせず closure を定義しない。
- したがって「Core にとって parse error か」という問いは、ある registry を
  固定しない限り判定できない。

各プログラムが「自身の registry において何が必須で、何が optional か」を
定義する責務を負う。その具体例は [validation-modes.md](validation-modes.md)
の tier × mode モデルを参照。

### 危険パターン

```
-- NG: annotation がコアの意味を変える
FI 10 @mode("resetting")     -- これは FI の variant。コア文法の問題

-- NG: Core 文法が特定の annotation を要求する
FI 10 requires @clock, @operandum    -- registry 依存を文法に焼き込まない

-- OK: コアは独立、annotation は付加
FI 10                        -- valid (どの registry でも)
FI 10 @clock(unit="s")       -- also valid (registry が @clock を知っていれば)
```

---

## 3. Annotator の所有ポリシー

本 DSL プロジェクトは annotation の **推奨** 集合を提供する。各プログラムは
これを採用・拡張・置換する自由を持つ。

### DSL プロジェクトが提供するもの

| カテゴリ | 推奨 annotator | キーワード例 |
|---|---|---|
| **Procedure** | stimulus-annotator, temporal-annotator | `@reinforcer`, `@sd`, `@operandum`, `@brief`, `@clock`, `@warmup`, `@algorithm` |
| **Subjects** | subject-annotator | `@species`, `@strain`, `@deprivation`, `@history`, `@n` |
| **Apparatus** | apparatus-annotator | `@chamber`, `@interface`, `@hw` |
| **Measurement** | （将来、measurement-annotator） | `@session_end`, `@response`, `@logging` 等 |

カテゴリ分類は [design-philosophy.md](ja/design-philosophy.md#41-推奨カテゴリ体系jeab-method-節に準拠) §4.1 に準拠する。

### 3rd-party が自由にできること

- DSL プロジェクトの推奨 annotator を **そのまま採用する**
- 一部を **無視する**（例: 環境条件を外部管理するプログラムは Apparatus を使わない）
- 独自の **新カテゴリを定義する**（例: Clinical, Derivational, Pharmacology）
- 既存 annotator を **再解釈・置換する**（対立理論の実装）

いずれの場合も Core DSL の変更は不要である。

### 漸進的付加の原則

```
理論的議論:     FI 10
シミュレーション: FI 10 @clock(unit="s") @algorithm("fleshler-hoffman", n=12)
物理実験:       FI 10 @clock(unit="s") @algorithm(...) @operandum("left_lever")
                      @reinforcer("pellet") @subject(species="rat")
                      @chamber("med-associates", model="ENV-007")
論文出版:       上記すべて（supplement として DSL ソースを公開）
```

各層は **optional かつ additive**。`FI 10` はどのプログラムの registry でも valid
（その registry が Core を解釈できる限り）。

### 新しい annotation を定義するには

1. [annotation-template.md](annotation-template.md) をテンプレートとしてコピー
2. §2 の境界テストに回答し、Core ではなく annotation として妥当であることを示す
3. 対応するカテゴリ（Procedure / Subjects / Apparatus / Measurement / 拡張）を選ぶ
4. §4 のレビュー機構を経て、該当パッケージまたは独自 registry に追加

---

## 4. レビュー機構: DSL プロジェクト推奨 annotator の追加プロセス

本節は **DSL プロジェクトが推奨 annotator を追加する場合** のレビュー手順を定める。
3rd-party の独自 registry には本節の手続きは強制されない（各プロジェクトが
自身のレビュー手続きを決定する）。

### 問題: 推奨 annotator の追加時に何を検証するか

推奨候補が現れたとき、以下を判定する:

- Core 文法への昇格が必要か（§2 の境界テスト Q1, Q2）、annotation でよいか
- どの推奨カテゴリ（Procedure / Subjects / Apparatus / Measurement）に属するか
- 推奨 registry の既存 annotator と keyword 衝突しないか

### レビュー構造

```
Layer 1: 機械的検証（プログラム的）
    ├── keyword 衝突検出（推奨 registry 内での disjointness）
    ├── annotator 間の依存関係検証
    └── schema 構文検証

Layer 2: 境界テスト（構造化 markdown）
    ├── §2 の境界テスト 3 問に回答
    ├── 各 annotator の README.md に記述された inclusion/exclusion criteria
    └── → 人間 or LLM が回答可能な形式
```

### Layer 2: 境界テストマトリクス

新しい annotation keyword `@X` を annotator `A` に追加する提案があったとき、
以下の markdown テンプレートに回答する:

```markdown
## Boundary Review: @X → A

### 1. Core independence
- [ ] `@X` なしでスケジュールの理論的性質を議論できるか → YES なら annotation OK
- [ ] `@X` は schedule 式の評価結果を変えるか → NO なら annotation OK

### 2. Category fit
- [ ] `@X` は A が属するカテゴリ（Procedure / Subjects / Apparatus / Measurement）と整合するか
- [ ] `@X` は A の既存 keywords と意味的に一貫するか
- [ ] `@X` は推奨 registry 内の他の annotator の keywords と衝突しないか

### 3. Necessity for recommendation
- [ ] `@X` がカバーする情報は、DSL 外（コメント・外部ファイル）で十分ではないか
- [ ] `@X` を DSL 内で宣言することで、コンパイル対象（論文 / コード生成 / 検証）に利益があるか
- [ ] 3rd-party だけでなく、DSL プロジェクトの推奨集合に含める価値があるか

### 4. Domain expert sign-off
- [ ] EAB: 基礎研究の観点から妥当
- [ ] PLT: 言語設計の観点から一貫
```

---

## 5. コンパイルターゲット（将来ビジョン）  <!-- was §5 before §6 scoping insert -->

```
DSL source (with annotations)
    │
    ├──→ Python runtime    (contingency-py + annotator)
    ├──→ Rust runtime      (contingency-rs)
    ├──→ MedPC syntax      (existing MedPC equipment)
    ├──→ Arduino/Teensy    (experiment-io)
    ├──→ JSON interchange  (data exchange)
    └──→ Natural language  (paper Methods section)
```

### 論文コンパイルの例

入力:
```
VI 30 @clock(unit="s")
  @algorithm("fleshler-hoffman", n=12)
  @cod(duration=2)
  @reinforcer("sucrose", concentration="10%", duration=3)
```

出力（APA Methods section）:
> Responses were reinforced according to a variable-interval 30-s schedule
> (Fleshler & Hoffman, 1962; list length = 12) with a 2-s changeover delay.
> Each reinforcer delivery consisted of 3-s access to 10% sucrose solution.

---

## 6. 二層スコーピング: プログラムレベル vs スケジュールレベル

### 動機

科学論文の Method セクションは明確な階層構造を持つ:
**Subjects** → **Apparatus** → **Procedure** (Sidman, 1960; Ferster & Skinner, 1957)。
被験体条件や装置は実験セッション全体に適用される境界条件であり、
強化スケジュール（独立変数）より上位の概念である。

DSL でもこの構造を反映する: `@species("rat")` は `FR5` の修飾ではなく、
プログラム全体の前提条件として宣言されるべきである。
`LH = 10s` がプログラムレベルで宣言されるのと同様のパターン。

### 文法

```ebnf
program ::= program_annotation* param_decl* binding* annotated_schedule
program_annotation ::= annotation
annotated_schedule ::= schedule annotation*
```

LL(1) 判定: 次トークンが `@` → `program_annotation` を消費、それ以外 → `param_decl*` へ遷移。
曖昧性なし。`@` 構文はプログラムレベルとスケジュールレベルで共通。

### スコーピング意味論

```
resolve(key, S) = S.annotations[key]  if key ∈ S.annotations
                  program.annotations[key]  otherwise
```

- **プログラムレベル** = セッション全体のデフォルト
- **スケジュールレベル** = 特定の式への上書き
- **同一キーワードを両レベルで許可** — 例: `@reinforcer` をプログラムレベルでデフォルト設定し、
  選択手続きの特定成分でのみ上書き

### 推奨スコープ分類

| スコープ | アノテーション | 根拠 |
|---|---|---|
| **プログラムレベル（Subjects）** | `@species`, `@strain`, `@n`, `@history`, `@deprivation` | セッション内不変。被験体は境界条件 |
| **プログラムレベル（Apparatus）** | `@chamber`, `@hw`, `@interface` | 装置はセッション通じて固定 |
| **プログラムレベル（Session）** | `@clock`, `@warmup`, `@algorithm` | セッション時間パラメータ |
| **スケジュールレベル** | `@operandum`, `@sd`, `@brief` | 成分ごとに異なる（concurrent, multiple） |
| **両方（デフォルト+上書き）** | `@reinforcer` | 通常統一、選択手続きで異なる場合あり |

注: これは推奨分類であり、文法レベルでの制約ではない。任意の annotation keyword は
構文的には両レベルに出現可能。意味的制約はセマンティックパスで検証する。

### 意味的制約

- `@operandum(component=N)` をプログラムレベルに置く → `SemanticError: PROGRAM_ANNOTATION_COMPONENT`
  （成分インデクスはスケジュール文脈でのみ意味を持つ）
- プログラムレベルで成分固有パラメータを持つアノテーション → linter WARNING

### 完全な例

```
-- Subjects (program-level)
@species("rat")
@strain("Sprague-Dawley")
@deprivation(hours=23, target="food")
@history("naive")
@n(6)

-- Apparatus (program-level)
@chamber("med-associates", model="ENV-007")
@hw("teensy41")

-- Session parameters (program-level)
@clock(unit="s")
@algorithm("fleshler-hoffman", n=12, seed=42)
@warmup(duration=300)
@reinforcer("sucrose", concentration="10%", duration=3)

-- Schedule parameters (core grammar)
COD = 2s
LH = 10s

let left = VI30s
let right = VI60s
Conc(left, right)
  @operandum("left_lever", component=1)   -- schedule-level
  @operandum("right_lever", component=2)  -- schedule-level
  @sd("red_light", component=1)           -- schedule-level
  @sd("green_light", component=2)         -- schedule-level
```

### 設計根拠

**PL 理論的根拠:**
- `session { }` ブロック構文は既存文法に前例がなく過剰 — 位置による区別で十分
- `param_decl` に統合するのは boundary principle 違反（param_decl = コア意味論に影響、
  annotation = 直交メタデータ）
- Rust inner/outer attributes (`#![...]` vs `#[...]`) に近い設計だが、
  位置スコーピングの方が non-TC DSL には自然

**行動分析学的根拠:**
- 被験体 = 境界条件（Sidman, 1960 の steady-state design における baseline）
- スケジュール = 独立変数
- 因果構造をそのまま DSL の構文階層に写像する

---

## 7. 未解決の設計課題

### メタDSL の文法（形式）

Annotation schema を言語非依存に記述するための **形式** は未確定。候補:

1. **EBNF + 制約言語** — grammar.ebnf を拡張し、型と制約を宣言する
2. **JSON Schema ベース** — ast-schema.json の拡張として annotation schema を定義
3. **独自 DSL** — `annotation "reinforcer" { ... }` 形式

いずれを採用しても design-philosophy §4.2 の原則に従い、本 DSL プロジェクトは
**推奨** schema のみを提供し、各プログラムは自身の registry を独自に構築できる。

### annotation_name の検証責任

grammar.ebnf §4.7 が定める通り、annotation_name の検証は **プログラム側**
の responsibility である。DSL 文法は syntactic form（`@name(args)`）のみを
定義する。推奨 schema を採用するプログラムは推奨 keyword を、独自 registry を
持つプログラムは自身の keyword を検証する。

### annotator 間の依存関係の上限

annotator が他の annotator を requires できる（例: social-annotator →
stimulus-annotator）。依存チェーンの深さに上限を設けるべきかは、具体的な
推奨 annotator が増えてから判断する。

---

## 8. 推奨 annotator への拡張提案リスト（Draft）

### Status: Draft - awaiting review

本節は、DSL プロジェクトの **推奨** annotator に追加候補となる
annotation のリストである。複数の専門領域観点（EAB 基礎、行動薬理、
ABA 実務、再現性設計）から独立に挙がった候補を統合している。

> **重要な読み替え（2026-04-12 の design-philosophy 確定後）:**
>
> 本節の「必須」「必須化すべき」等の語は **DSL プロジェクト推奨集合への
> 組み込み推奨度** を表す。DSL 文法レベルで「必須」になるものは存在しない。
> 個々のプログラムの registry が自身のルールに従って必須か optional かを
> 決定する。具体例は [validation-modes.md](validation-modes.md) の
> tier × mode モデルを参照。
>
> 同じ annotation が、あるプログラムでは必須（tier 2）、別のプログラムでは
> optional、さらに別のプログラムでは未使用ということがあり得る。これは
> [design-philosophy.md §4.2](ja/design-philosophy.md#42-カテゴリは-推奨分類であって強制ではない) の必然的帰結である。

### 8.1 完全合意された追加提案（Core EAB Extensions）

EAB 基礎研究で必須の拡張:

#### 8.1.1 `@session_end` — セッション終了条件 **[必須]**

```
@session_end(rule="first", time=60min, reinforcers=60)
```

- `rule`: `"first"` (whichever first) | `"time_only"` | `"reinforcers_only"`
- Sidman (1960) の steady-state 推定と Baron & Perone (1998) の手続き記述標準
- **強い推奨**: プログラムレベルで必須化すべき

#### 8.1.2 `@response` — 反応トポグラフィ **[必須]**

```
@response(
  force_min=0.15,         -- newtons
  duration_min=0.05,      -- seconds
  irt_min=0.01,           -- debounce / response individuation
  trigger="onset"         -- "onset" | "offset"
)
```

- 「2つのラボで同じ `FR 10` が別実験になる」のを防ぐ
- force threshold は反応定義そのもの
- プログラムレベル（セッション内で不変）

#### 8.1.3 `@pretraining` — 手続き史（`@history` と分離）

```
@pretraining(
  magazine=2,             -- days
  lever=3,
  criterion="50 presses/session"
)
```

- 被験体史（`@history`）と手続き史は別次元
- Shaping / autoshaping の履歴

#### 8.1.4 `@context` — 刺激文脈

```
@context(
  houselight="on",
  iti_light="off",
  masker="white-noise-70dB"
)
```

- Renewal 研究（Bouton, 2004）で文脈定義が決定的
- プログラムレベル（セッション全体で一定）

#### 8.1.5 `@logging` — データ記録仕様

```
@logging(
  resolution="10ms",      -- time resolution
  events=["lever", "reinforcer", "sd"]
)
```

- 分子解析の前提
- 時間分解能の宣言は再現性の一部

#### 8.1.6 `@clock` 拡張 — 時間精度・同期

```
@clock(
  unit="s",
  precision="μs",         -- runtime measurement precision
  sampling=1000,          -- Hz (for continuous data)
  sync="PTP"              -- "PTP" | "NTP" | "trigger"
)
```

#### 8.1.7 `@random` — グローバル乱数 seed

```
@random(seed=42, scope="global")
```

- `@algorithm(seed=...)` はスケジュール値生成用
- `@random(seed=..., scope="global")` は counterbalance / stimulus order / その他全て
- 両者を分離して宣言可能にする

### 8.2 追加提案（JEAB 査読観点）

#### 8.2.1 `@session_onset` — スケジュール開始タイミング

```
@session_onset(
  clock_start="session_start",    -- "session_start" | "first_response"
  houselight="on",
  warmup_complete=true
)
```

- Multiple/chained schedule の inter-component interval 宣言

#### 8.2.2 `@reinforcer` 拡張 — 時間随伴性の精密化

```
@reinforcer(
  "sucrose",
  consumption_window=3s,
  clock_resume="post_consumption"  -- "delivery" | "availability" | "post_consumption"
)
```

- FI で interval 計測が reinforcer delivery の瞬間か、consumption 後かを明示
- JEAB 査読観点: interval の時間基準を書かない論文は査読で必ず指摘される

#### 8.2.3 `@scheduled` vs runtime `obtained` の区別

DSL は `@scheduled(VI=60)` を宣言するが、ランタイムは `obtained_rate` を記録する。
スキーマレベルで**両方の存在を保証**することで、
"VI 60-s the program" と "VI 60-s the subject's experience" の混同を防ぐ。

- DSL: intent の宣言のみ
- session-recorder: obtained の記録義務を schema で強制

#### 8.2.4 `@timeout` — 誤反応/エラー訂正

```
@timeout(duration=5s, stimuli_off=true, lever_retracted=false)
```

### 8.3 ドメイン特化拡張（個別 annotator）

#### 8.3.1 行動薬理学系 — `pharmacology-annotator`（新設）

```
@drug(
  name="cocaine",
  dose=0.5, unit="mg/kg",
  route="iv",              -- "ip" | "iv" | "sc" | "po"
  vehicle="saline",
  injection_volume=0.1,
  pre_session_interval=15min
)

@phase("reinstatement", trigger="cue")
                         -- "acquisition" | "maintenance"
                         -- | "extinction" | "reinstatement"

@preparation(
  implant="iv_catheter",
  location="jugular",
  patency_check="thiopental"
)

@pr_breakpoint(idle="10min")
```

- `@preparation` は `@history` から分離（catheter patency は session-level 変数）
- `@phase` は手続きの identity を決める（同じ FR1 でも acquisition/extinction は別実験）

#### 8.3.2 ABA 臨床系 — `subject-human`（`subject-animal` と分離）

倫理フレームワーク（IACUC vs IRB）が全く異なるため、**annotator を分離する**ことを推奨。

```
@client(
  age=5,
  vb_mapp(version="2.0", level=2, milestones_passed=42),
  communication_modality="PECS"    -- "vocal" | "PECS" | "SGD" | "sign"
)

@setting("clinic")                 -- "clinic" | "home" | "school" | "community"

@function(
  type="escape",
  evidence="functional_analysis"   -- "FA" | "indirect" | "descriptive"
)

@ioa(
  method="exact",                  -- "exact" | "partial" | "total"
  percent=85,
  sessions_pct=33                  -- % of sessions with IOA measured
)

@ethics(irb="IRB-2026-0042", consent=true, assent=true)
                                   -- opaque field, DSL 意味論に影響させない
```

**設計原則:**
- `@species`, `@strain`, `@deprivation` は subject-animal 専用
- `@client`, `@setting`, `@function`, `@ioa` は subject-human 専用
- 共通の中立フィールド（age 等）のみ subject-base に
- **介入合成（DRA+extinction）はスケジュール合成で表現**（プログラムレベルに書くと procedural fidelity 評価ができない）

### 8.4 セッション識別 — 実装/記録層との責務分離

再現性単位原則: **「次回も同じ実験ができるか」は DSL、「今回何が起きたか」は recorder**

| 項目 | 担当 | 理由 |
|---|---|---|
| `subject_id`, `experiment_id` | **DSL** | 実験計画の同定子 |
| `session_id`, `timestamp` | session-recorder | 実行時アーティファクト |
| software versions | session-recorder (manifest) | DSL に書くと古びる |
| event code mapping | experiment-io | HW 抽象の責務 |
| calibration 実測値 | session-recorder | 実行時測定 |
| calibration 期待値 | DSL (`@hw(expected=...)`) | 計画の一部 |

DSL 拡張提案:

```
@experiment(id="exp-001", subject_id="R12")
```

### 8.5 多セッション構造（論争点 — 未決）

**多セッション構造提案:**
```
program ABA_reversal {
  session A { baseline }
  session B { treatment }
  session A' { return_to_baseline }
}
```

**対立する観点（1 DSL = 1 procedure 維持派）:** 複数セッションは manifest 層で束ねる。

**折衷案:** `1 DSL file = 1 session` 原則を維持し、外部 `manifest.yaml` で複数 DSL を束ねる。
「再現性の単位」は manifest レベルで担保する。

```yaml
# manifest.yaml
experiment: dose-response-cocaine
sessions:
  - file: session_01_vehicle.dsl
    subject: R12
    date: 2026-04-11
  - file: session_02_0.5mg.dsl
  - file: session_03_1.0mg.dsl
```

### 8.6 DSL 範囲外で合意された項目

- **Steady-state criteria**: データ解析層の責務。DSL で判定すると「手続きと効果を混同」する。`@stability_target` を記述のみの optional field で置くことは許容。
- **Institution, grant number, preregistration ID**: 実験計画ではない。外部 `study.yaml` に分離。
- **Microdialysis / photometry 生データ** (行動薬理観点): `@coregister(stream="photometry")` 程度のフックのみ。
- **IRB/IACUC approval number**: opaque field で保持（DSL 意味論に影響させない）。

### 8.7 実装の優先順位

**Phase 1（最優先 — EAB 基礎研究で必須）:**
1. `@session_end` — 必須化すべき
2. `@response` — 必須化すべき
3. `@pretraining` — `@history` からの分離
4. `@context` — renewal 研究の前提
5. `@logging` + `@clock` 拡張

**Phase 2（再現性強化）:**
6. `@random` グローバル seed
7. `@session_onset` / `@reinforcer` clock_resume
8. `@scheduled` vs `obtained` スキーマ分離

**Phase 3（ドメイン特化 — 各アプリが所有）:**
9. `pharmacology-annotator`（`@drug`, `@phase`, `@preparation`, `@pr_breakpoint`）
10. `subject-human` annotator（`@client`, `@setting`, `@function`, `@ioa`, `@ethics`）

**Phase 4（未決）:**
11. 多セッション構造 vs manifest 層での束ね

### 8.8 次のステップ

1. Phase 1 の各アノテーションについて `spec/annotation-template.md` に従った
   境界テスト（§2 参照）への回答を作成
2. `subject-animal` と `subject-human` annotator の分離リファクタリング
3. `pharmacology-annotator` の新規 spec 作成
4. 実装前にもう一度各専門領域観点（JEAB、行動薬理、ABA、再現性設計）で cross-review を実施

### 8.9 参照

- Baron, A., & Perone, M. (1998). Experimental design and analysis in the laboratory study of human operant behavior. In K. A. Lattal & M. Perone (Eds.), *Handbook of research methods in human operant behavior* (pp. 45-91). Plenum.
- Bouton, M. E. (2004). Context and behavioral processes in extinction. *Learning & Memory*, 11(5), 485-494. https://doi.org/10.1101/lm.78804
- Lattal, K. A. (2010). Delayed reinforcement of operant behavior. *JEAB*, 93, 129-139. https://doi.org/10.1901/jeab.2010.93-129
- Sidman, M. (1960). *Tactics of scientific research*. Basic Books.
- Stokes, T. F., & Baer, D. M. (1977). An implicit technology of generalization. *JABA*, 10(2), 349-367. https://doi.org/10.1901/jaba.1977.10-349
