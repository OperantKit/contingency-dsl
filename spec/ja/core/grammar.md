# 形式文法

> [contingency-dsl 理論文書](theory.md)の一部。DSL の文脈自由文法（BNF）を定義する。

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
                  | "PR" | "Repeat"
                  | "hodos" | "exponential" | "linear"
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

<compound>      ::= <combinator> "(" <arg_list> ")"
<combinator>    ::= "Conc" | "Alt" | "Conj"
                  | "Chain" | "Tand"
                  | "Mult" | "Mix"
                  | "Overlay"
<arg_list>      ::= <positional_args> ("," <keyword_arg>)*
<positional_args> ::= <schedule> ("," <schedule>)+
<keyword_arg>   ::= <kw_name> "=" <value>
<kw_name>       ::= "COD" | "ChangeoverDelay"
                   | "FRCO" | "FixedRatioChangeover"

<modifier>      ::= <dr_mod> | <pr_mod> | <repeat> | <lag_mod>
<dr_mod>        ::= ("DRL" | "DRH" | "DRO") <ws>? <value>
<pr_mod>        ::= "PR" ("(" <pr_opts> ")")?
<pr_opts>       ::= <pr_step> ("," <pr_param>)*
<pr_step>       ::= "hodos" | "exponential" | "linear"
<pr_param>      ::= "start" "=" <number>
                  | "increment" "=" <number>
<repeat>        ::= "Repeat" "(" <number> "," <schedule> ")"
<lag_mod>       ::= "Lag" <ws>? <number>
                  | "Lag" "(" <number> ("," <lag_kw_arg>)* ")"
<lag_kw_arg>    ::= "length" "=" <number>

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

-- 罰の重畳（§2.10）
Overlay(VI 60-s, FR 1)                              -- VI 60 ベースラインに全反応罰
Overlay(Conc(VI 60-s, VI 180-s, COD=2-s), FR 1)        -- 並立ベースラインに罰の重畳

-- let 束縛（マクロ展開）
let baseline = VI 60-s
let probe = Conc(VI 30-s, VI 60-s)
Conc(baseline, probe)
```

---

