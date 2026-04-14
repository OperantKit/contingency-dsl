# 形式文法

> [contingency-dsl 理論文書](theory.md)の一部。DSL の文脈自由文法（BNF）を定義する。

**関連文書:** [LL(2) 形式的証明](ll2-proof.md) — FIRST₁/FIRST₂/FOLLOW₂ 集合、LL(2) 解析表、曖昧性ゼロの証明、Core-Stateful 保存証明。文法の LL(2) 判定点は複合スケジュール `arg_list` 内の `PosTail` のただ1箇所のみ。他の全判定点は LL(1)。

---

## Part III: 形式文法

### 3.1 設計原則

DSL の文法は4つの基準を満たす:

1. **表記的忠実性**: 行動分析学文献の慣習に合致する（`FR 5`, `conc VI 30 VI 60`）。
2. **曖昧性のない構文解析**: 全ての式が正確に1つの構文解析木を持つ。
3. **合成可能性**: 任意にネストされたスケジュール式を支持する。
4. **Python 埋め込み可能性**: 独立したテキスト形式としても Python コンストラクタ呼び出しとしても使用可能。

### 3.2 BNF 文法（基底 CFG）

```bnf
<program>       ::= <param_decl>* <binding>* <schedule>
<param_decl>    ::= <param_name> "=" <value>
<param_name>    ::= "LH" | "LimitedHold"
                  | "COD" | "ChangeoverDelay"
                  | "FRCO" | "FixedRatioChangeover"
                  | "BO"  | "Blackout"
                  | "RD"  | "ReinforcementDelay"
<binding>       ::= "let" <ident> "=" <schedule>

<schedule>      ::= <base_schedule> ("LH" <ws>? <value>)?
<base_schedule> ::= <atomic>
                  | <compound>
                  | <modifier>
                  | <aversive_schedule>
                  | <ident>
                  | "(" <schedule> ")"

<atomic>        ::= <dist><domain> <ws>? <value>
                  | "EXT"
                  | "CRF"
<dist>          ::= "F" | "V" | "R"
<domain>        ::= "R" | "I" | "T"
<ws>            ::= " "+
<value>         ::= <number> <time_unit>?
<time_unit>     ::= "s" | "ms" | "min"
<number>        ::= [0-9]+ ("." [0-9]+)?

<ident>         ::= [a-z_][a-zA-Z0-9_]*   -- <reserved> と一致してはならない
<reserved>      ::= "let" | "def"
                  | <dist><domain>
                  | "EXT" | "CRF"
                  | <combinator>
                  | "DRL" | "DRH" | "DRO" | "LH" | "LimitedHold"
                  | "COD" | "ChangeoverDelay"
                  | "FRCO" | "FixedRatioChangeover"
                  | "RD"  | "ReinforcementDelay"
                  | "BO"  | "Blackout"
                  | "PR" | "Repeat"
                  | "hodos" | "exponential" | "linear" | "geometric"
                  | "start" | "increment"
                  | "Sidman" | "SidmanAvoidance"
                  | "SSI" | "ShockShockInterval"
                  | "RSI" | "ResponseShockInterval"
                  | "Lag" | "length"
                  | "DiscriminatedAvoidance" | "DiscrimAv"
                  | "CSUSInterval" | "ITI" | "mode"
                  | "ShockDuration" | "MaxShock"
                  | "fixed" | "escape"
                  | "Overlay"
                  | "Interpolate" | "Interp"
                  | "count" | "onset"

<compound>      ::= <combinator> "(" <arg_list> ")"
                  | <interpolate>
<combinator>    ::= "Conc" | "Alt" | "Conj"
                  | "Chain" | "Tand"
                  | "Mult" | "Mix"
                  | "Overlay"
<arg_list>      ::= <positional_args> ("," <keyword_arg>)*
<positional_args> ::= <schedule> ("," <schedule>)+
<keyword_arg>   ::= <kw_name> "=" <value>
<kw_name>       ::= "COD" | "ChangeoverDelay"
                   | "FRCO" | "FixedRatioChangeover"
                   | "BO"  | "Blackout"

<modifier>      ::= <dr_mod> | <pr_mod> | <repeat> | <lag_mod>
<dr_mod>        ::= ("DRL" | "DRH" | "DRO") <ws>? <value>
<pr_mod>        ::= "PR" "(" <pr_opts> ")"
                  | "PR" <ws>? <number>
<pr_opts>       ::= <pr_step> ("," <pr_param>)*
<pr_step>       ::= "hodos" | "exponential" | "linear" | "geometric"
<pr_param>      ::= "start" "=" <number>
                  | "increment" "=" <number>
                  | "ratio" "=" <number>
<repeat>        ::= "Repeat" "(" <number> "," <schedule> ")"
<lag_mod>       ::= "Lag" <ws>? <number>
                  | "Lag" "(" <number> ("," <lag_kw_arg>)* ")"
<lag_kw_arg>    ::= "length" "=" <number>

<interpolate>   ::= ("Interpolate" | "Interp") "(" <schedule> "," <schedule>
                    ("," <interp_kw_arg>)+ ")"
<interp_kw_arg> ::= "count" "=" <number>
                  | "onset" "=" <value>

<aversive_schedule> ::= <sidman_avoidance>
                      | <discriminated_avoidance>
<sidman_avoidance>  ::= ("Sidman" | "SidmanAvoidance") "(" <sidman_arg> ("," <sidman_arg>)* ")"
<sidman_arg>        ::= <sidman_kw> "=" <value>
<sidman_kw>         ::= "SSI" | "ShockShockInterval"
                      | "RSI" | "ResponseShockInterval"
<discriminated_avoidance> ::= ("DiscriminatedAvoidance" | "DiscrimAv")
                              "(" <da_arg> ("," <da_arg>)* ")"
<da_arg>            ::= <da_temporal_kw> "=" <value>
                      | "mode" "=" <da_mode>
<da_temporal_kw>    ::= "CSUSInterval" | "ITI" | "ShockDuration" | "MaxShock"
<da_mode>           ::= "fixed" | "escape"
```

**識別子の命名制約。** 識別子は小文字 ASCII 英字またはアンダースコア（`[a-z_]`）で始まり、ASCII 英数字とアンダースコアの任意の組み合わせが続く。これにより DSL キーワードおよびスケジュール型プレフィクス（全て大文字始まり）と字句的に分離される。`<reserved>` 生成規則は、小文字キーワード（`let`, `def`, `hodos` 等）の識別子使用も防止する。`def` は将来使用のために予約されている（§4.4 参照）。

### 3.3 表記の柔軟性

文法は行動分析学文献の慣習に合わせて複数の表記形式をサポートする:

```
VI 60-s      -- JEAB 現代標準形式（推奨）
VI 60-sec    -- JEAB 旧式論文（1960-70年代）
VI 60 s      -- 空白区切り単位（JEAB 1986, 2012）
VI 60 sec    -- 空白区切り単位（Ferster & Skinner, 1957）
VI 60-min    -- 分単位（例: VI 1-min）
VI 60 min    -- 分単位、空白区切り
VI 60s       -- 単位密着形式（区切りなし）
VI60s        -- 密着形式（単位付き）
VI60         -- 密着形式（単位暗黙）
VI 60        -- 空白区切り、単位なし（Ferster & Skinner, 1957 原典）
VI(60)       -- Python コンストラクタ形式
```

全て同一の `VariableInterval(target_time=60.0)` に解決される。パーサは2文字の `<dist><domain>` プレフィクスを読み、任意の空白をスキップして `<value>` を読む。

### 3.4 構文糖衣

**`Repeat(n, S)`** は n 回の tandem 合成の構文糖衣である:

```
Repeat(n, S) ≡ Tand(S, S, ..., S)
                    └── n 個 ──┘
```

DSL の計算能力を増加させない。パーサが解析時に let-free な構文木に展開する。

**`let` 束縛** はマクロ展開（テキスト置換）である。束縛名は `<ident>` の制約を満たす必要がある: 小文字英字またはアンダースコアで始まり、`<reserved>` に含まれないこと。

```
let baseline = VI 60-s
let treatment = Conc(VI 30-s, EXT)
Conc(baseline, treatment)
```

は以下に展開される:

```
Conc(VI 60-s, Conc(VI 30-s, EXT))
```

`let` は変更可能な状態、クロージャ、再帰的定義を導入しない。展開後の結果は基底 CFG 内の let-free な構文木である。

**スコーピング規則。** `let` 束縛は以下の3つの意味論的制約に従う:

1. **シャドウイング禁止。** 各束縛名はプログラム内で一意でなければならない。重複名は静的エラーとする（例: `"束縛 'x' が重複しています（最初の定義: 行 N）"`）。
2. **前方参照禁止。** 束縛 `let x_k = e` において、`e` 内の全ての識別子は `{x_1, ..., x_{k-1}}`（先行する束縛で定義済みの識別子）に含まれなければならない。未定義または後方で定義される識別子の参照は静的エラーとする。帰結として、推移的な相互参照（例: `let a = b; let b = a`）も拒否される。
3. **トップレベル限定。** 束縛は `<program>` レベルにのみ出現する（`<program> ::= <binding>* <schedule>`）。`let` は複合式の内部に出現できない。

実装は、未使用の束縛（スケジュール式または後続の束縛で一度も参照されない束縛名）に対して警告を発することが推奨される（SHOULD）。

### 3.5 二重 API

v1.0 DSL は2つの等価なインターフェースを提供する:

**A. テキスト DSL（設定ファイル・文書向け）:**
```python
from contingency_dsl import parse
schedule = parse("Conc(VI 30-s, VI 60-s)")
```

**B. Python コンストラクタ（プログラム的合成）:**
```python
from contingency_dsl import FR, VI, Conc, Chain, Tand, Repeat
schedule = Conc(VI(30), VI(60))
nested = Conc(Chain(FR(5), VI(60)), FR(10))
repeated = Tand(Repeat(3, FR(10)), VI(60))
```

Python コンストラクタ API は OperantKit の `ScheduleBuilder.swift` のパターンを再現する: `FR(5)`, `Conc(...)`, `Alt(...)`, `Chain(...)`。

### 3.6 式の例

```
-- 原子スケジュール
FR 5                                   -- 固定比率 5
VI 30-s                                 -- 変動間隔 30 秒
RR 20                                  -- ランダム比率 20
EXT                                   -- 消去
CRF                                   -- 連続強化（= FR 1）

-- 複合スケジュール
Conc(VI 30-s, VI 60-s, COD=2-s)           -- 並立 VI 30-s VI 60-s + 切替遅延 2-s
Chain(FR 5, FI 30-s)                     -- 連鎖 FR 5 → FI 30
Alt(FR 10, FI 5-min)                     -- 選択 FR 10 | FI 5-min
Conj(FR 5, FI 30-s)                      -- 連言 FR 5 ∧ FI 30
Tand(VR 20, DRL 5-s)                     -- タンデム VR 20 → DRL 5
Mult(FR 5, EXT)                        -- 多元 FR 5/EXT
Mix(FR 5, FR 10)                        -- 混合 FR 5/FR 10

-- ネストされた合成
Conc(Chain(FR 5, VI 60-s), Alt(FR 10, FT 30-s))

-- 修飾子
DRL 5-s                                 -- 低率分化強化
DRO 10-s                                -- 他行動分化強化
PR(hodos)                             -- 累進比率（Hodos ステップ）
PR(linear, start=1, increment=5)      -- 累進比率（線形ステップ）

-- Repeat（構文糖衣）
Tand(Repeat(3, FR 10), VI 60-s)          -- FR 10 × 3 → VI 60

-- Limited Hold（後置修飾子）
FI 30-s LH 10-s                           -- FI 30 + LH 10（Ferster & Skinner, 1957 正典形式）
VI 60-s LH 5-s                            -- VI 60 + LH 5
DRL 3-s LH 8-s                            -- DRL 3 + LH 8（Kramer & Rilling, 1970）
Conc(VI 30-s LH 5-s, VI 60-s LH 10-s)        -- 並立: 成分ごとに個別 LH
Chain(FR 5, FI 30-s) LH 10-s              -- 複合スケジュール全体に LH

-- プログラムレベルの LH デフォルト（param_decl）
LH = 10-s
Conc(VI 30-s, VI 60-s, COD=2-s)
-- ↑ 各成分に個別適用: Conc(VI 30-s LH 10-s, VI 60-s LH 10-s, COD=2-s) と等価
-- ローカル指定が優先: Conc(VI 30-s LH 5-s, VI 60-s) では VI 30 は LH 5-s、VI 60 はデフォルト値

-- 切替遅延・固定比切替（§2.4）
Conc(VI 30-s, VI 60-s, COD=2-s)           -- 2秒の切替遅延（Herrnstein, 1961）
Conc(VI 30-s, VI 60-s, COD=0-s)           -- 明示的ゼロ遅延（統制条件）
Conc(VI 30-s, VI 60-s, FRCO=5)           -- 固定比切替 5 反応（Hunter & Davison, 1985）
Conc(VI 30-s, VI 60-s, COD=2-s, FRCO=5)   -- COD と FRCO の共存

-- Sidman 自由オペラント回避（§2.7）
Sidman(SSI=20-s, RSI=5-s)                              -- 基本形 (Sidman, 1953)
SidmanAvoidance(SSI=20-s, RSI=5-s)                     -- verbose alias
Sidman(ShockShockInterval=20-s, ResponseShockInterval=5-s) -- verbose parameter names
Chain(FR 10, Sidman(SSI=20-s, RSI=5-s))                 -- 連鎖スケジュールに回避リンク

-- Lag スケジュール、オペラント変動性（§2.8）
Lag 5                                                 -- Lag 5 略記形式、length=1 default
Lag(5)                                                -- 括弧形式の等価表現
Lag(5, length=8)                                      -- Page & Neuringer (1985) 8-peck sequence
Lag 0                                                 -- variability 要求なし（CRF と等価）
Mult(Lag(5, length=8), CRF)                           -- Lag vs CRF ベースラインの multiple schedule

-- プログラムレベルの COD デフォルト（全 Conc に適用）
-- COD = 2-s
-- Conc(VI 30-s, VI 60-s)               -- param_decl の COD=2-s を継承

-- 弁別回避（§2.9）
DiscriminatedAvoidance(CSUSInterval=10-s, ITI=3-min, mode=escape)       -- Solomon & Wynne (1953) 型
DiscriminatedAvoidance(CSUSInterval=10-s, ITI=3-min, mode=escape, MaxShock=2-min) -- 安全カットオフ付き
DiscriminatedAvoidance(CSUSInterval=10-s, ITI=3-min, mode=fixed, ShockDuration=0.5-s)  -- 固定 US
DiscrimAv(CSUSInterval=10-s, ITI=3-min, mode=escape)                    -- 短縮 alias

-- ブラックアウト（§2.5）
Mult(FR 5, EXT, BO=5-s)                            -- 成分間に 5 秒のブラックアウト
Mix(VI 30-s, VI 60-s, BO=3-s)                         -- 3 秒のブラックアウト（無弁別）

-- 強化遅延（§1.7; プログラムレベルの装置遅延）
-- RD = 500-ms
-- VI 60-s                                          -- 全強化子が 500 ms 遅延

-- 内挿スケジュール（Ferster & Skinner, 1957）
Interpolate(FI 15-min, FI 1-min, count=16)              -- FI 15 の背景に FI 1 で 16 強化を内挿
Interp(FI 15-min, FR 50, count=10, onset=3-min)         -- onset 遅延付き; Interp は短縮 alias

-- 罰の重畳（§2.10）
Overlay(VI 60-s, FR 1)                              -- VI 60 ベースラインに全反応罰
Overlay(Conc(VI 60-s, VI 180-s, COD=2-s), FR 1)        -- 並立ベースラインに罰の重畳

-- let 束縛（マクロ展開）
let baseline = VI 60-s
let probe = Conc(VI 30-s, VI 60-s)
Conc(baseline, probe)
```

### 3.7 エラー回復ポリシー

適合パーサは以下のエラー回復ポリシーに従わなければならない（MUST）:

**エラー報告要件（MUST）:**
- 少なくとも1つのエラーを、エラーコード・位置（行・列）・エラーカテゴリ（`LexError`・`ParseError`・`SemanticError`）とともに報告すること。
- エラーコードは `conformance/core/errors.json` で定義されたコードのいずれかと一致しなければならない（MUST）。

**複数エラー回復（SHOULD）:**
- パーサは **パニックモード回復**（Aho et al., 2006, §4.8.2）を実装すべきである（SHOULD）: エラー検出後、同期トークンに到達するまで入力トークンを読み飛ばし、解析を再開する。
- 同期トークン: `)`・`,`・改行（`\n`）・`EOF`。
- 検出した全エラーを位置順のリストとして報告する。

**部分 AST（MUST NOT）:**
- エラーが存在する場合、パーサは部分的な AST を返してはならない（MUST NOT）。エラー時の結果は AST なしのエラーリストとする。

**エラー上限（MAY）:**
- パーサは設定可能な最大エラー数（推奨デフォルト: 10）で停止してもよい（MAY）。これはカスケードエラーのノイズを防止するためである。

**根拠。** 単一エラーで停止する方式では、ユーザーはエラーを1つずつ修正することを強いられる。これは、1文字の誤りが後続の問題を覆い隠しうる DSL において許容されない。パニックモード回復は、句レベル回復やエラー生成規則回復の複雑さを避けつつ複数エラー報告を可能にする最も単純な戦略である（Aho et al., 2006, §4.8）。

### 3.8 実験層 — 多フェーズ文法（v2.0）

実験層は DSL を拡張し、多フェーズの実験デザイン — JEAB Method セクションが命名された条件の列と相変化基準として記述するセッション間構造 — を記述可能にする。この層は**追加的（additive）**である: `phase` または `shaping` 宣言を含まないファイルは単一フェーズの `program` として解析される（完全な後方互換性）。

**設計根拠。** セッション内の随伴性記述（Mechner, 1959; State Notation, Snapper et al., 1982）とセッション間の実験デザイン構造（A-B-A-B 記法, Cooper et al., 2020）を統一する既存の形式的表記法は存在しない。JEAB 論文はこの2つのレベルを Method セクションの別々の散文で記述する。実験層はこのギャップを、既存のスケジュール文法をフェーズ順序構造内に埋め込むことで橋渡しする。

#### 3.8.1 トップレベルの曖昧性解消

```bnf
<file>          ::= <experiment> | <program>
```

**LL(1) 判定:** 最初の非アノテーショントークンが `phase` または `shaping` であればファイルは `experiment`。それ以外は `program`。`phase` と `shaping` は `FIRST₁(Schedule)` に含まれない小文字予約語であるため、曖昧性は生じない。

#### 3.8.2 実験とフェーズ

```bnf
<experiment>    ::= <program_annotation>* (<phase_decl> | <shaping_decl>)+

<phase_decl>    ::= "phase" <phase_name> ":" <phase_body>
<phase_name>    ::= <upper_ident>
<phase_body>    ::= <phase_meta>* (<phase_content> | <phase_ref>) <annotation>*

<phase_meta>    ::= <session_spec> | <stability_spec>
<session_spec>  ::= "sessions" ("=" | ">=") <number>
<stability_spec> ::= "stable" "(" <stability_method> ("," <stability_param>)* ")"
<stability_method> ::= "visual" | "cv" | "relative-range" | "dual-criterion"
                     | "performance" | <ident>
<stability_param>  ::= <ident> "=" (<number> | <number> "%" | <string_literal> | <value>)

<phase_content> ::= <param_decl>* <binding>* <annotated_schedule>
<phase_ref>     ::= "use" <phase_name>
<upper_ident>   ::= [A-Z] [a-zA-Z0-9_]*
```

**意味論:**
- 最初の `phase`/`shaping` 宣言の前にある `program_annotation` は実験レベルのデフォルトを設定する。フェーズレベルのアノテーションが上書きする（Core のプログラムレベル vs スケジュールレベルと同じ解決規則）。
- `sessions = N` は固定セッション数を指定する。`sessions >= N` は安定性基準適用前の最低数を指定する。
- `use <PhaseName>` は参照先フェーズのスケジュール式をコピーする。前方参照は許可されない。

#### 3.8.3 Shaping（構文糖衣）

```bnf
<shaping_decl>  ::= "shaping" <phase_name> ":" <shaping_body>
<shaping_body>  ::= <shaping_steps>+ <phase_meta>* <param_decl>* <binding>* <annotated_schedule>
<shaping_steps> ::= "steps" <ident> "=" "[" <number_list> "]"
<number_list>   ::= <number> ("," <number>)*
```

`shaping` はフェーズ宣言の列に脱糖される。`Repeat(n, S)` → `Tand(S, ..., S)` と同じ戦略。スケジュール式とアノテーション値は `steps` 変数を参照する `{ident}` プレースホルダーを含むことができる。

**展開規則（E-SHAPING）:**

```
shaping Name:
  steps x = [v₁, v₂, ..., vₙ]
  <meta>
  <schedule_template({x})>

  ≡（以下に脱糖）

phase Name_1: <meta>  <schedule_template(v₁)>
phase Name_2: <meta>  <schedule_template(v₂)>
...
phase Name_n: <meta>  <schedule_template(vₙ)>
```

**複数変数展開（E-SHAPING-MULTI）:** 複数の `steps` 宣言がある場合、全リストの長さは同一でなければならない。変数はペアワイズで zip される: `(x₁, y₁), (x₂, y₂), ...`。

#### 3.8.4 使用例

**ABA 反転デザイン（Brown et al., 2020, JEAB）:**

```
@species("rat") @strain("Long-Evans") @n(5)
@reinforcer("food", type="pellet", magnitude="45mg", duration=3s)

phase Baseline:
  sessions = 25
  Conc(VI60s @operandum("target-lever"), EXT @operandum("inactive-lever"))

phase DRA:
  sessions = 14
  Conc(VI60s @operandum("target-lever"), VI15s @operandum("nose-poke"), COD=3s)

phase ExtinctionTest:
  sessions = 5
  Conc(EXT @operandum("target-lever"), EXT @operandum("nose-poke"))
```

**シェイピング漸進（Eckard & Kyonka, 2018, Behav Processes）:**

```
@species("mouse") @strain("C57BL/6J") @n(27)
@reinforcer("sucrose", concentration="15%")

shaping FI_Training:
  steps v = [2, 4, 8, 12, 18]
  sessions >= 3
  stable(visual)
  FI {v}s LH3s

phase Peak_Baseline:
  sessions = 25
  FI18s LH3s

phase DRL_Intervention:
  sessions = 38
  DRL18s

phase Peak_Retest:
  sessions = 25
  use Peak_Baseline
```

**パラメトリック用量反応（Rickard et al., 2009, JEAB）:**

```
@species("rat") @strain("Wistar") @n(15)
@session_end(rule="time", time=50min)

shaping DoseResponse:
  steps vol = [6, 12, 25, 50, 100, 200, 300]
  sessions = 30
  PR(exponential)
  @reinforcer("sucrose", concentration="0.6M", volume="{vol}ul")
```

#### 3.8.5 実験層の意味制約

| # | 制約 | エラーコード | レベル |
|---|---|---|---|
| 63 | フェーズ名の重複 | `DUPLICATE_PHASE_NAME` | SemanticError |
| 64 | 未定義の `use` 参照 | `UNDEFINED_PHASE_REF` | SemanticError |
| 65 | Shaping steps 長の不一致 | `SHAPING_STEPS_LENGTH_MISMATCH` | SemanticError |
| 66 | 空の shaping steps リスト | `SHAPING_EMPTY_STEPS` | SemanticError |
| 67 | 未定義の shaping プレースホルダー | `SHAPING_UNDEFINED_VARIABLE` | SemanticError |
| 68 | 実験レベルアノテーションスコーピング | （Core スコーピングを継承） | — |
| 69 | フェーズごとの session_spec 重複 | `DUPLICATE_SESSION_SPEC` | SemanticError |
| 70 | フェーズごとの stability_spec 重複 | `DUPLICATE_STABILITY_SPEC` | SemanticError |
| 71 | `sessions >= 0`（非正） | `SESSION_NONPOSITIVE` | SemanticError |
| 72 | `sessions = 0`（非正） | `SESSION_NONPOSITIVE` | SemanticError |

#### 3.8.6 LL(1) 検証

実験層の全判定点は LL(1):

| 判定点 | 先読み | トークン集合 |
|---|---|---|
| `file → experiment \| program` | 1 | `{phase, shaping}` vs その他全て |
| `(phase_decl \| shaping_decl)+` | 1 | `phase` vs `shaping` |
| `phase_meta → session_spec \| stability_spec` | 1 | `sessions` vs `stable` |
| `session_spec → "=" \| ">="` | 1 | `=` vs `>=` |
| `phase_content \| phase_ref` | 1 | `use` vs その他全て |

新しい LL(2) 判定点は導入されない。[LL(2) 形式的証明 §11](ll2-proof.md) を参照。

---

