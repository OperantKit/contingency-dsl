# オペラント文法 — 三項随伴性（SD–R–SR）

> contingency-dsl オペラント層（Ψ）の一部。オペラント固有の EBNF 産出規則を定義する: `ScheduleExpr`、コンビネータ群（Conc, Alt, Conj, Chain, Tand, Mult, Mix, Overlay）、修飾子（DRL, DRH, DRO, PR, Lag, Repeat）、限定子（LH, TO, ResponseCost）、嫌悪的スケジュール（Sidman, DiscriminatedAvoidance）。パラダイム中立なメタ文法は `foundations/grammar.md` で定義される。スケジュールクラスごとの仕様は `operant/schedules/{ratio,interval,time,differential,compound,progressive}.md` に置く。状態依存および試行ベースの下位層は `operant/stateful/` および `operant/trial-based/` にある。

**関連文書:** [LL(2) 形式的証明](../foundations/ll2-proof.md) — FIRST₁/FIRST₂/FOLLOW₂ 集合、LL(2) 構文解析表、曖昧性のなさの証明。オペラント文法の LL(2) 決定点はちょうど 1 つのみ（合成の `arg_list` 内の `PosTail`）であり、他のすべての決定点は LL(1) である。

---

## 1. オペラント固有の産出規則

`foundations/grammar.md` のパラダイム中立骨格を踏まえ、オペラント層は `<expr>` を `<schedule>` に特殊化する。

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
                                   (("TO" | "Timeout") "(" <timeout_args> ")")?
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
```

`<dist><domain>` プレフィックスは 3×3 のアトミック・スケジュール格子（FR, VR, RR, FI, VI, RI, FT, VT, RT）を生成し、`operant/schedules/{ratio, interval, time}.md` で特殊化される。`EXT` と `CRF` は境界事例（消去および連続強化。`operant/theory.md §1.3` 参照）。

### 1.1 予約キーワード集合（オペラント層）

```bnf
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
                  | "TO" | "Timeout"
                  | "duration" | "reset_on_response" | "contingent_response"
                  | "true" | "false"
                  | "Overlay"
                  | "target" | "changeover" | "all"
                  | "PUNISH"
                  | "Interpolate" | "Interp"
                  | "count" | "onset"
```

`def` は基盤層により予約されており、オペラント層はこの予約を継承する。

### 1.2 合成産出規則

```bnf
<compound>      ::= <combinator> "(" <arg_list> ")"
                  | <interpolate>
<combinator>    ::= "Conc" | "Alt" | "Conj"
                  | "Chain" | "Tand"
                  | "Mult" | "Mix"
                  | "Overlay"
<arg_list>      ::= <positional_args> ("," <keyword_arg>)*
<positional_args> ::= <schedule> ("," <schedule>)+
<keyword_arg>   ::= <scalar_kw_arg> | <directional_kw_arg>
                  | <overlay_kw_arg> | <punish_directive>
<scalar_kw_arg> ::= <kw_name> "=" <value>
<directional_kw_arg> ::= <kw_name> "(" <dir_ref> "->" <dir_ref> ")" "=" <value>
<dir_ref>       ::= <number> | <ident>
<kw_name>       ::= "COD" | "ChangeoverDelay"
                   | "FRCO" | "FixedRatioChangeover"
                   | "BO"  | "Blackout"

<overlay_kw_arg> ::= "target" "=" <target_value>
<target_value>  ::= "changeover" | "all"

<punish_directive> ::= "PUNISH" "(" <punish_target> ")" "=" <schedule>
<punish_target>    ::= "changeover"
                     | <dir_ref> "->" <dir_ref>
                     | <dir_ref>
```

コンビネータごとの意味論は `operant/schedules/compound.md` で規定される。修飾子ごとの意味論はスケジュールクラス別ファイル（`ratio.md`, `interval.md`, `time.md`, `differential.md`, `progressive.md`）で規定される。

### 1.3 修飾子産出規則

```bnf
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
```

DR 修飾子は `operant/schedules/differential.md` で詳述される。PR は `operant/schedules/progressive.md` で詳述される。`Repeat` は構文糖衣である（§3 参照）。`Lag` はオペラント変動性の修飾子である（Page & Neuringer, 1985）。

### 1.4 限定子および嫌悪的スケジュールの産出規則

```bnf
<timeout_args>  ::= <timeout_kwarg> ("," <timeout_kwarg>)*
<timeout_kwarg> ::= "duration" "=" <value>
                  | "reset_on_response" "=" <boolean>
                  | "contingent_response" "=" <label_ref>
<boolean>       ::= "true" | "false"
<label_ref>     ::= <ident> | <number>

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

Sidman 自由オペラント回避および DiscriminatedAvoidance は、嫌悪的統制の一級プリミティブである（`operant/theory.md §2.7–§2.9` 参照）。

## 2. 表記の柔軟性

オペラント文法は、行動分析文献の慣習に合致する複数の表記形式をサポートする。

```
VI 60-s      -- JEAB 現代標準（推奨）
VI 60-sec    -- JEAB 旧論文（1960〜70 年代）
VI 60 s      -- 空白区切り単位（JEAB 1986, 2012）
VI 60 sec    -- 空白区切り単位（Ferster & Skinner, 1957）
VI 60-min    -- 分単位（例: VI 1-min）
VI 60 min    -- 分単位、空白区切り
VI 60s       -- 連結単位（区切りなし）
VI60s        -- 単位付きコンパクト
VI60         -- コンパクト（単位は暗黙）
VI 60        -- 空白区切り、単位なし（Ferster & Skinner, 1957）
VI(60)       -- Python コンストラクタ形式
```

すべて同一の `VariableInterval(target_time=60.0)` に解決される。構文解析器は 2 文字の `<dist><domain>` プレフィックスを読み、任意の空白をスキップし、`<value>` を読む。

## 3. 構文糖衣

**`Repeat(n, S)`** は n 重タンデム合成の構文糖衣である。

```
Repeat(n, S) ≡ Tand(S, S, ..., S)
                    └── n 個のコピー ──┘
```

DSL の計算能力を増加させない。構文解析器は解析時に let を含まない構文木へ展開する。代数的性質は `operant/theory.md §2.2.3` で証明される。

## 4. デュアル API

DSL は 2 つの等価なインターフェースを提供する。

**A. テキスト DSL（設定ファイル、ドキュメント）:**
```python
from contingency_dsl import parse
schedule = parse("Conc(VI 30-s, VI 60-s)")
```

**B. Python コンストラクタ（プログラマティックな合成）:**
```python
from contingency_dsl import FR, VI, Conc, Chain, Tand, Repeat
schedule = Conc(VI(30), VI(60))
nested = Conc(Chain(FR(5), VI(60)), FR(10))
repeated = Tand(Repeat(3, FR(10)), VI(60))
```

Python コンストラクタ API は OperantKit の `ScheduleBuilder.swift` パターン（`FR(5)`, `Conc(...)`, `Alt(...)`, `Chain(...)`）を踏襲する。

## 5. 例

```
-- アトミックスケジュール（operant/schedules/{ratio,interval,time}.md 参照）
FR 5                                   -- Fixed Ratio 5
VI 30-s                                -- Variable Interval 30 秒
RR 20                                  -- Random Ratio 20
EXT                                    -- 消去
CRF                                    -- 連続強化（= FR 1）

-- 合成スケジュール（operant/schedules/compound.md 参照）
Conc(VI 30-s, VI 60-s, COD=2-s)        -- 並行 VI 30-s VI 60-s、COD 2 秒
Chain(FR 5, FI 30-s)                   -- 連鎖 FR 5 → FI 30
Alt(FR 10, FI 5-min)                   -- 交替 FR 10 または FI 5-min
Conj(FR 5, FI 30-s)                    -- 連言 FR 5 AND FI 30
Tand(VR 20, DRL 5-s)                   -- タンデム VR 20 → DRL 5
Mult(FR 5, EXT)                        -- 多元 FR 5/EXT
Mix(FR 5, FR 10)                       -- 混合 FR 5/FR 10

-- 修飾子（operant/schedules/{differential,progressive}.md 参照）
DRL 5-s                                -- 低頻度他行動分化強化
DRO 10-s                               -- 他行動分化強化
PR(hodos)                              -- Progressive Ratio（Hodos ステップ）
PR(linear, start=1, increment=5)       -- Progressive Ratio（線形ステップ）

-- Limited Hold（時間的利用可能性制約）
FI 30-s LH 10-s                        -- FI 30-s、10 秒ホールド付き（Ferster & Skinner, 1957）
VI 60-s LH 5-s                         -- VI 60-s、5 秒ホールド付き

-- 切り替え遅延および固定比切り替え
Conc(VI 30-s, VI 60-s, COD=2-s)        -- 切り替え遅延 2 秒（Herrnstein, 1961）
Conc(VI 30-s, VI 60-s, FRCO=5)         -- 固定比切り替え 5（Hunter & Davison, 1985）

-- Sidman 自由オペラント回避
Sidman(SSI=20-s, RSI=5-s)              -- Sidman (1953)

-- 弁別回避
DiscriminatedAvoidance(CSUSInterval=10-s, ITI=3-min, mode=escape)       -- Solomon & Wynne (1953)

-- 罰のオーバーレイ
Overlay(VI 60-s, FR 1)                 -- VI 60 ベースライン上の全反応を罰
Overlay(Conc(VI 30-s, VI 60-s, COD=2-s), FR 1,
        target=changeover)             -- 切り替えのみ罰（Todorov, 1971）
```

## 6. エラー回復

オペラント固有のエラーコードは `conformance/operant/errors.json` に記載される。エラー回復方針自身（panic-mode、同期トークン、マルチエラー報告）はパラダイム中立であり、`foundations/grammar.md §7` で規定される。

## 7. 実験層拡張

多相実験計画（フェーズ列、漸進的訓練、シェイピング）は、オペラント文法を加法的に拡張する。文法は `experiment/phase-sequence.md`、相変化基準は `experiment/criteria.md` を参照。

## 参考文献

- Ferster, C. B., & Skinner, B. F. (1957). *Schedules of reinforcement*. Appleton-Century-Crofts.
- Herrnstein, R. J. (1961). Relative and absolute strength of response as a function of frequency of reinforcement. *Journal of the Experimental Analysis of Behavior*, 4(3), 267–272. https://doi.org/10.1901/jeab.1961.4-267
- Hunter, I., & Davison, M. (1985). Determination of a behavioral transfer function. *Journal of the Experimental Analysis of Behavior*, 43(1), 43–59. https://doi.org/10.1901/jeab.1985.43-43
- Page, S., & Neuringer, A. (1985). Variability is an operant. *Journal of Experimental Psychology: Animal Behavior Processes*, 11(3), 429–452. https://doi.org/10.1037/0097-7403.11.3.429
- Sidman, M. (1953). Two temporal parameters of the maintenance of avoidance behavior by the white rat. *Journal of Comparative and Physiological Psychology*, 46(4), 253–261. https://doi.org/10.1037/h0060730
- Skinner, B. F. (1938). *The behavior of organisms*. Appleton-Century.
- Solomon, R. L., & Wynne, L. C. (1953). Traumatic avoidance learning: Acquisition in normal dogs. *Psychological Monographs: General and Applied*, 67(4), 1–19. https://doi.org/10.1037/h0093649
- Todorov, J. C. (1971). Concurrent performances: Effect of punishment contingent on the switching response. *Journal of the Experimental Analysis of Behavior*, 16(1), 51–62. https://doi.org/10.1901/jeab.1971.16-51
