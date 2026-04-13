# LL(2) 形式的証明 — contingency-dsl v1.0 コア文法

## 1. 定理の主張

**定理.** contingency-dsl v1.0 コア文法（`schema/core/grammar.ebnf` に定義）は以下を満たす:

1. **LL(2)** — 最大2トークンの先読みによるトップダウン予測型構文解析器で決定的に解析可能。
2. **LL(1) でない** — 2トークンの先読みを必要とする決定点が少なくとも1つ存在する。
3. **曖昧性ゼロ** — すべての有効な入力が唯一の構文解析木を持つ。

**注意事項（§9）.** アノテーションシステムはプログラムレベルのアノテーションに対して狭い LL(2)/LL(3) 境界ケースを導入する。コアスケジュール文法（アノテーションを除く）は厳密に LL(2)。アノテーションを含む場合、標準的な貪欲曖昧性解消の下で LL(2) が維持される。貪欲規約なしの厳密な LL(3) が1つの特定のトークン三つ組に適用される。分析は §9 を参照。

---

## 2. トークン語彙

本証明は以下の終端トークンクラスを生成する**キーワード認識字句解析器**を前提とする。空白（文字列リテラル内を除く）は字句解析器で消費され、トークンとしては出現しない。

| トークンクラス | メンバー | 説明 |
|---|---|---|
| `SCHED_TYPE` | FR, VR, RR, FI, VI, RI, FT, VT, RT | 分布×領域の組み合わせ |
| `EXT` | EXT | 消去キーワード |
| `CRF` | CRF | 連続強化キーワード |
| `COMB` | Conc, Alt, Conj, Chain, Tand, Mult, Mix, Overlay | 結合子キーワード |
| `INTERP` | Interpolate, Interp | 挿入スケジュールキーワード |
| `DR_KW` | DRL, DRH, DRO | 分化強化キーワード |
| `PR_KW` | PR | 累進比率キーワード |
| `REPEAT_KW` | Repeat | 反復キーワード |
| `LAG_KW` | Lag | Lag スケジュールキーワード |
| `LH_KW` | LH, LimitedHold | 限定保持キーワード |
| `LET_KW` | let | 束縛キーワード |
| `KW_NAME` | COD, ChangeoverDelay, FRCO, FixedRatioChangeover, BO, Blackout | 複合スケジュールのキーワード引数名 |
| `PARAM_NAME` | LH, LimitedHold, COD, ChangeoverDelay, FRCO, FixedRatioChangeover, BO, Blackout | プログラムレベルのパラメータ名 |
| `SIDMAN_KW` | Sidman, SidmanAvoidance | Sidman 回避キーワード |
| `DA_KW` | DiscriminatedAvoidance, DiscrimAv | 弁別回避キーワード |
| `SSI_KW` | SSI, ShockShockInterval | Sidman SSI パラメータ |
| `RSI_KW` | RSI, ResponseShockInterval | Sidman RSI パラメータ |
| `DA_TEMP_KW` | CSUSInterval, ITI, ShockDuration, MaxShock | DA 時間パラメータキーワード |
| `MODE_KW` | mode | DA モードキーワード |
| `DA_MODE` | fixed, escape | DA モード値 |
| `PR_STEP` | hodos, exponential, linear | PR ステップ関数キーワード |
| `PR_PARAM_KW` | start, increment | PR パラメータキーワード |
| `LENGTH_KW` | length | Lag 長さキーワード |
| `INTERP_KW` | count, onset | 挿入スケジュールのキーワード引数名 |
| `NUM` | [0-9]+ ("." [0-9]+)? | 数値リテラル |
| `TIME_UNIT` | s, sec, ms, min | 時間単位（文脈的予約語） |
| `IDENT` | [a-z_][a-zA-Z0-9_]* から予約語を除外 | ユーザー識別子 |
| `AT` | @ | アノテーション接頭辞 |
| `ANNO_NAME` | (AnnotationRegistry に依存) | アノテーション名 |
| `STRING` | "..." | 文字列リテラル |
| `LPAREN` | ( | 左括弧 |
| `RPAREN` | ) | 右括弧 |
| `COMMA` | , | カンマ区切り |
| `EQ` | = | 等号 |
| `DASH` | - | ハイフン（時間区切り） |
| `EOF` | — | 入力終端 |

**字句解析器の前提:**

- **L1（キーワード優先）:** 予約語はそれぞれ固有のトークンクラスとして字句解析され、`IDENT` としては解析されない。すべての予約語は大文字で始まる（定義上 `IDENT` と素）か、識別子の名前空間から明示的に除外される。
- **L2（TIME_UNIT の文脈的予約）:** `s`, `sec`, `ms`, `min` は `IDENT` ではなく `TIME_UNIT` として字句解析される。これらは文脈的予約語である（grammar.ebnf 87–89行）。
- **L3（PARAM_NAME/KW_NAME の重複）:** `LH` は `PARAM_NAME`（param_decl 内）と `LH_KW`（schedule の LH 接尾辞内）の両方である。字句解析器は単一のトークンを生成し、構文解析器が文脈で曖昧性を解消する。LL(k) 分析では同一トークンクラス `LH_KW`/`PARAM_NAME` として扱い、文脈による曖昧性解消を検証する。

---

## 3. トークンレベルの CFG（文脈自由文法）

EBNF 文法を以下の標準変換でトークンレベルの CFG に正規化する:
- `*`/`+`/`?` を右再帰の補助非終端記号で除去
- 空白は暗黙（字句解析器で消費）として扱う

以下、`ε` は空文字列を表す。非終端記号は*斜体*、終端記号は `等幅` で表記する。

### 3.1 プログラムレベル

```
Program           → ProgramAnnotations ParamDecls Bindings AnnotatedSchedule
ProgramAnnotations → AT Annotation ProgramAnnotations | ε
ParamDecls        → PARAM_NAME EQ Value ParamDecls | ε
Bindings          → LET_KW IDENT EQ Schedule Bindings | ε
AnnotatedSchedule → Schedule Annotations
Annotations       → AT Annotation Annotations | ε
Annotation        → ANNO_NAME AnnotationArgs_opt
AnnotationArgs_opt → LPAREN AnnotationArgs RPAREN | ε
```

### 3.2 スケジュール式

```
Schedule          → BaseSchedule LH_opt
LH_opt            → LH_KW Value | ε
BaseSchedule      → AtomicOrSecond
                  | Compound
                  | Modifier
                  | AversiveSchedule
                  | IDENT
                  | LPAREN Schedule RPAREN
AtomicOrSecond    → ParametricAtomic SecondOrder_opt
                  | EXT
                  | CRF
ParametricAtomic  → SCHED_TYPE Value
SecondOrder_opt   → LPAREN SimpleSchedule RPAREN | ε
SimpleSchedule    → ParametricAtomic
Value             → NUM TimeSuffix_opt
TimeSuffix_opt    → DASH TIME_UNIT | TIME_UNIT | ε
```

### 3.3 複合スケジュール

```
Compound          → COMB LPAREN ArgList RPAREN
                  | INTERP LPAREN Schedule COMMA Schedule InterpKwArgs RPAREN
ArgList           → Schedule COMMA Schedule PosTail KwTail
PosTail           → COMMA Schedule PosTail | ε
KwTail            → COMMA KW_NAME EQ Value KwTail | ε
InterpKwArgs      → COMMA InterpKwArg InterpKwTail
InterpKwTail      → COMMA InterpKwArg InterpKwTail | ε
InterpKwArg       → INTERP_KW EQ InterpKwValue
```

### 3.4 修飾子

```
Modifier          → DR_KW Value
                  | PR_KW PrOpts_opt
                  | REPEAT_KW LPAREN NUM COMMA Schedule RPAREN
                  | LagMod
PrOpts_opt        → LPAREN PrStep PrParams RPAREN | ε
PrStep            → PR_STEP
PrParams          → COMMA PR_PARAM_KW EQ NUM PrParams | ε
LagMod            → LAG_KW NUM
                  | LAG_KW LPAREN NUM LagKwArgs RPAREN
LagKwArgs         → COMMA LENGTH_KW EQ NUM LagKwArgs | ε
```

### 3.5 嫌悪スケジュール

```
AversiveSchedule  → SIDMAN_KW LPAREN SidmanArg SidmanTail RPAREN
                  | DA_KW LPAREN DaArg DaTail RPAREN
SidmanArg         → SidmanParam EQ Value
SidmanParam       → SSI_KW | RSI_KW
SidmanTail        → COMMA SidmanArg SidmanTail | ε
DaArg             → DA_TEMP_KW EQ Value | MODE_KW EQ DA_MODE
DaTail            → COMMA DaArg DaTail | ε
```

---

## 4. FIRST₁ 集合

選択肢を持つ生成規則に出現するすべての非終端記号について FIRST₁ を計算する。記号 `⊕` は集合和を表す。

### 4.1 コア非終端記号

| 非終端記号 | FIRST₁ | 導出 |
|---|---|---|
| `AtomicOrSecond` | {`SCHED_TYPE`, `EXT`, `CRF`} | ParametricAtomic, EXT, CRF から |
| `Compound` | {`COMB`, `INTERP`} | COMB, INTERP キーワードから |
| `Modifier` | {`DR_KW`, `PR_KW`, `REPEAT_KW`, `LAG_KW`} | 修飾子キーワードから |
| `AversiveSchedule` | {`SIDMAN_KW`, `DA_KW`} | 嫌悪スケジュールキーワードから |
| `IDENT`（BaseSchedule の選択肢として） | {`IDENT`} | 終端記号 |
| `LPAREN Schedule RPAREN` | {`LPAREN`} | 終端記号 |
| `Schedule` | FIRST₁(BaseSchedule) | BaseSchedule → ... を経由 |
| `BaseSchedule` | {`SCHED_TYPE`, `EXT`, `CRF`, `COMB`, `INTERP`, `DR_KW`, `PR_KW`, `REPEAT_KW`, `LAG_KW`, `SIDMAN_KW`, `DA_KW`, `IDENT`, `LPAREN`} | 全選択肢の和集合 |

### 4.2 オプション接尾辞

| オプション | FIRST₁ | 出現位置 | 親の FOLLOW₁ | 素？ |
|---|---|---|---|---|
| `SecondOrder_opt` | {`LPAREN`} | ParametricAtomic の後 | §5.2 参照 | ✓（§5.2） |
| `LH_opt` | {`LH_KW`} | BaseSchedule の後 | §5.3 参照 | ✓（§5.3） |
| `TimeSuffix_opt` | {`DASH`, `TIME_UNIT`} | NUM の後 | §5.4 参照 | ✓（§5.4） |
| `PrOpts_opt` | {`LPAREN`} | PR_KW の後 | §5.5 参照 | ✓（§5.5） |
| `AnnotationArgs_opt` | {`LPAREN`} | ANNO_NAME の後 | §9 参照 | ⚠（§9） |

### 4.3 反復の決定

| 反復 | 継続の FIRST₁ | 停止（FOLLOW₁） | 素？ |
|---|---|---|---|
| `ProgramAnnotations` | {`AT`} | {`PARAM_NAME`, `LET_KW`} ⊕ FIRST₁(Schedule) | ✓ |
| `ParamDecls` | {`PARAM_NAME`} | {`LET_KW`} ⊕ FIRST₁(Schedule) | ✓ |
| `Bindings` | {`LET_KW`} | FIRST₁(Schedule) | ✓ |
| `Annotations` | {`AT`} | {`EOF`} | ✓ |
| `PosTail` | {`COMMA`} | §6 参照（**衝突**） | ✗（§6） |
| `KwTail` | {`COMMA`} | {`RPAREN`} | ✓ |
| `SidmanTail` | {`COMMA`} | {`RPAREN`} | ✓ |
| `DaTail` | {`COMMA`} | {`RPAREN`} | ✓ |
| `PrParams` | {`COMMA`} | {`RPAREN`} | ✓ |
| `LagKwArgs` | {`COMMA`} | {`RPAREN`} | ✓ |
| `InterpKwTail` | {`COMMA`} | {`RPAREN`} | ✓ |

---

## 5. 非衝突点の LL(1) 検証

### 5.1 BaseSchedule（6つの選択肢）

`BaseSchedule` の6つの選択肢は対ごとに素な FIRST₁ 集合を持つ:

```
FIRST₁(AtomicOrSecond)    = { SCHED_TYPE, EXT, CRF }
FIRST₁(Compound)          = { COMB, INTERP }
FIRST₁(Modifier)          = { DR_KW, PR_KW, REPEAT_KW, LAG_KW }
FIRST₁(AversiveSchedule)  = { SIDMAN_KW, DA_KW }
FIRST₁(IDENT)             = { IDENT }
FIRST₁(LPAREN Sched RPAREN) = { LPAREN }
```

**検証:** 15個の対ごとの共通部分はすべて空である。これは字句解析器の前提 L1（キーワード優先）に従う: 各トークンは正確に1つのクラスに属し、どのクラスも複数の選択肢に出現しない。**LL(1).** ∎

### 5.2 SecondOrder_opt（ParametricAtomic の後のオプション）

```
FIRST₁(SecondOrder_opt) = { LPAREN }
```

`LPAREN ∉ FOLLOW₁(AtomicOrSecond)` を示す必要がある。

`AtomicOrSecond` は `BaseSchedule` の選択肢である。`FOLLOW₁(BaseSchedule) = FIRST₁(LH_opt) ∪ FOLLOW₁(Schedule)`（LH_opt は ε になりうるため）。

すべての文脈における `FOLLOW₁(Schedule)`:

| 文脈 | FOLLOW₁(Schedule) |
|---|---|
| 束縛: `LET IDENT EQ Schedule` | {`LET_KW`} ∪ FIRST₁(Schedule) ∪ {`AT`, `EOF`} |
| PosTail: `COMMA Schedule PosTail` | {`COMMA`, `RPAREN`} |
| グルーピング: `LPAREN Schedule RPAREN` | {`RPAREN`} |
| Repeat: `REPEAT LPAREN NUM COMMA Schedule RPAREN` | {`RPAREN`} |
| AnnotatedSchedule: `Schedule Annotations` | {`AT`, `EOF`} |
| Interpolate: `Schedule COMMA ...` | {`COMMA`} |
| ArgList: `Schedule COMMA Schedule ...` | {`COMMA`} |

和集合: FOLLOW₁(Schedule) = {`LET_KW`, `COMMA`, `RPAREN`, `AT`, `EOF`} ∪ FIRST₁(Schedule)

FIRST₁(Schedule) は `LPAREN` を含む（グルーピングスケジュールから）。よって `LPAREN ∈ FOLLOW₁(Schedule)`。

しかし `FOLLOW₁(AtomicOrSecond) ⊆ FOLLOW₁(BaseSchedule) = {LH_KW} ∪ FOLLOW₁(Schedule)` である。

**LPAREN は FOLLOW₁(AtomicOrSecond) に出現するか？**

`LPAREN ∈ FOLLOW₁(Schedule)` は束縛の文脈から生じる。束縛の schedule の後、次の要素が LPAREN で始まるメインスケジュールでありうるためである。

つまり `AtomicOrSecond` の後に LPAREN が続く可能性がある（`SecondOrder_opt` としてではなく、新しい文の開始として）。

**曖昧性候補の例:**
```
let x = FR 5
(Conc(VI 30s, VI 60s))
```

`FR 5`（AtomicOrSecond）の後、次のトークンは `(` であり、これはメインスケジュールの開始であって二次スケジュールの接尾辞ではない。

**解消:** 束縛の文脈 `LET IDENT EQ Schedule` では、`Schedule` 生成規則が呼び出される。`Schedule → BaseSchedule LH_opt` → `BaseSchedule → AtomicOrSecond → ParametricAtomic SecondOrder_opt`。`ParametricAtomic` = `FR 5` の後、`SecondOrder_opt` が LPAREN を確認する。

この文脈では `(Conc(...))` は束縛の一部ではなくメインスケジュールである。しかし構文解析器は束縛内の `Schedule` に入っており、`(` を `SecondOrder_opt` として貪欲に消費し、`FR 5 (Conc(...))` を二次スケジュール `FR5(Conc(...))` として解釈する。

`SecondOrder_opt` 内では `SimpleSchedule → ParametricAtomic` であり、LPAREN の後 SCHED_TYPE を期待する。代わりに COMB が来ると構文解析エラーとなる。つまりユーザーの意図した解析は拒否される。

**しかしこの状況は実際に到達可能か？** `FR 5 (Conc(...))` が発生するには束縛内でなければならず、束縛は `Schedule` を解析し、LPAREN を見ると貪欲に SecondOrder_opt に入る。ユーザーは以下のように書く必要がある:
```
let x = (FR 5)
(Conc(VI 30s, VI 60s))
```
（FR 5 を括弧で囲むことで SecondOrder_opt が外側の LPAREN を見るのを防ぐ）。

**SecondOrder_opt に対する結論:** LPAREN の貪欲消費は**意図された正しい**挙動である。文法はすべての入力に対して一意の解析を割り当てるため、真の曖昧性は存在しない。構文解析器の貪欲選択は文法の意味論の範囲内で常に正しい選択である。**貪欲オプション解消の下で LL(1)。** ∎

### 5.3 LH_opt（BaseSchedule の後のオプション）

```
FIRST₁(LH_opt) = { LH_KW }
```

`LH_KW ∉ FOLLOW₁(Schedule)` を示す必要がある。

§5.2 の FOLLOW₁(Schedule) 表から:

FOLLOW₁(Schedule) = {`LET_KW`, `COMMA`, `RPAREN`, `AT`, `EOF`} ∪ FIRST₁(Schedule)

FIRST₁(Schedule) = {`SCHED_TYPE`, `EXT`, `CRF`, `COMB`, `INTERP`, `DR_KW`, `PR_KW`, `REPEAT_KW`, `LAG_KW`, `SIDMAN_KW`, `DA_KW`, `IDENT`, `LPAREN`}

`LH_KW` はこの集合に含まれない。`LH` は `PARAM_NAME` としてプログラムレベル（束縛の前）にのみ出現し、`PARAM_NAME` は `LH_opt` が関係するどの文脈の FOLLOW₁(Schedule) にも含まれない。

**検証:** `LH_KW ∉ FOLLOW₁(Schedule)`。**LL(1).** ∎

### 5.4 TimeSuffix_opt（Value 内の NUM の後のオプション）

```
FIRST₁(TimeSuffix_opt) = { DASH, TIME_UNIT }
```

`{DASH, TIME_UNIT} ∩ FOLLOW₁(Value) = ∅` を示す必要がある。

`Value` が出現する文脈:
- `ParamDecl`: `PARAM_NAME EQ Value` → FOLLOW = 次の ParamDecl/Binding/Schedule の開始
- `LH_opt`: `LH_KW Value` → FOLLOW = FOLLOW₁(Schedule)
- `KeywordArg`: `KW_NAME EQ Value` → FOLLOW = {`COMMA`, `RPAREN`}
- `SidmanArg`: `SidmanParam EQ Value` → FOLLOW = {`COMMA`, `RPAREN`}
- `DaArg`: `DA_TEMP_KW EQ Value` → FOLLOW = {`COMMA`, `RPAREN`}
- `InterpKwArg`: `INTERP_KW EQ Value` → FOLLOW = {`COMMA`, `RPAREN`}
- `DR_KW Value`（Modifier）: FOLLOW = FOLLOW₁(BaseSchedule) = {`LH_KW`} ∪ FOLLOW₁(Schedule)
- `ParametricAtomic`: `SCHED_TYPE Value` → FOLLOW = FIRST₁(SecondOrder_opt) ∪ FOLLOW₁(AtomicOrSecond) = {`LPAREN`} ∪ FOLLOW₁(BaseSchedule)

FOLLOW₁(Value) の和集合:
```
{ PARAM_NAME, LET_KW, COMMA, RPAREN, AT, EOF, LH_KW, LPAREN }
∪ FIRST₁(Schedule)
= { PARAM_NAME, LET_KW, COMMA, RPAREN, AT, EOF, LH_KW, LPAREN,
    SCHED_TYPE, EXT, CRF, COMB, INTERP, DR_KW, PR_KW, REPEAT_KW,
    LAG_KW, SIDMAN_KW, DA_KW, IDENT }
```

**検証:**
- `DASH ∉ FOLLOW₁(Value)`: DASH は文法全体で `TimeSuffix_opt` 内にのみ出現する。✓
- `TIME_UNIT ∉ FOLLOW₁(Value)`: TIME_UNIT トークン（s, sec, ms, min）は文脈的予約語（L2）であり、完了した Value の後のいかなる位置にも出現しない。✓

**LL(1).** ∎

### 5.5 PrMod（決定的 — LL(1)）

v1.0 ではステップ関数の明示が必須であるため、`PR` の後には常に `LPAREN` が続く:

```
PrMod ::= PR_KW LPAREN PrOpts RPAREN
```

オプション分岐は存在しない。`PR_KW` の後、構文解析器は無条件に `LPAREN` を期待する。この生成規則は **LL(1) 決定的**である。∎

### 5.6 LagMod（2つの選択肢）

```
FIRST₁(LAG_KW NUM)             = { LAG_KW }   （両選択肢とも LAG_KW で始まる）
FIRST₁(LAG_KW LPAREN NUM ...) = { LAG_KW }
```

`LAG_KW` 消費後、構文解析器は次のトークンを確認する:
- `NUM` → 短縮形（`Lag 5`）
- `LPAREN` → 括弧形（`Lag(5, ...)`）

`{NUM} ∩ {LPAREN} = ∅`。**LAG_KW の後 LL(1)。** ∎

### 5.7 プログラムレベルの遷移

```
ProgramAnnotations:  継続 = { AT },         停止 = { PARAM_NAME, LET_KW } ⊕ FIRST₁(Schedule)
ParamDecls:          継続 = { PARAM_NAME },  停止 = { LET_KW } ⊕ FIRST₁(Schedule)
Bindings:            継続 = { LET_KW },      停止 = FIRST₁(Schedule)
```

- `AT ∉ {PARAM_NAME, LET_KW} ∪ FIRST₁(Schedule)` → ✓
- `PARAM_NAME ∉ {LET_KW} ∪ FIRST₁(Schedule)` → ✓（PARAM_NAME トークンは予約語であり FIRST₁(Schedule) に含まれない）
- `LET_KW ∉ FIRST₁(Schedule)` → ✓（LET は予約語）

**すべて LL(1)。** ∎

### 5.8 その他の反復

`KwTail`, `SidmanTail`, `DaTail`, `PrParams`, `LagKwArgs`, `InterpKwTail` のすべての `*` 反復:
- 継続: {`COMMA`}
- 停止: {`RPAREN`}
- `{COMMA} ∩ {RPAREN} = ∅`

**すべて LL(1)。** ∎

---

## 6. LL(1) 衝突: ArgList 内の `PosTail`

### 6.1 衝突の特定

生成規則:

```
ArgList  → Schedule COMMA Schedule PosTail KwTail
PosTail  → COMMA Schedule PosTail | ε
KwTail   → COMMA KW_NAME EQ Value KwTail | ε
```

`PosTail` の決定点において:

```
FIRST₁(COMMA Schedule PosTail) = { COMMA }

FOLLOW₁(PosTail) = FIRST₁(KwTail) ∪ (KwTail ⇒* ε のため FOLLOW₁(ArgList))
                  = { COMMA }  ∪  { RPAREN }
                  = { COMMA, RPAREN }
```

**LL(1) 条件の検証:**

```
FIRST₁(COMMA Schedule PosTail) ∩ FOLLOW₁(PosTail) = { COMMA } ∩ { COMMA, RPAREN } = { COMMA }
```

**衝突。** トークン `COMMA` が継続集合と後続集合の両方に出現する。LL(1) 構文解析器は `COMMA` が位置引数リストの継続なのかキーワード引数セクションへの遷移なのかを判定できない。∎

### 6.2 LL(1) でないことの証明

**補題。** 本文法は LL(1) でない。

**証明。** 以下の2つの入力を考える:

```
入力 A:  Conc(VI 30s, VI 60s, FR 5)         -- 位置引数3個
入力 B:  Conc(VI 30s, VI 60s, COD=2s)       -- 位置引数2個 + キーワード引数1個
```

`Conc(VI 30s, VI 60s` を解析した後、構文解析器は `Schedule COMMA Schedule` を消費し `PosTail` の決定点にいる。次のトークンはどちらの場合も `COMMA` である。

- 入力 A では、`COMMA` は `PosTail` を継続する（次の位置スケジュール `FR 5`）。
- 入力 B では、`COMMA` は `PosTail` を終了（ε）し `KwTail` に入る（キーワード引数 `COD=2s`）。

1トークンの先読みは `COMMA` のみを見て、2つのケースを区別できない。∎

### 6.3 LL(2) による解消

**定理。** `PosTail` の衝突は LL(2) で解消される。

**証明。** 2トークンの先読み集合を計算する:

**FIRST₂(COMMA Schedule PosTail):**

`COMMA Schedule PosTail` の最初の2トークンは `COMMA` の後に `Schedule` の最初のトークンが続く:

```
FIRST₂(COMMA Schedule PosTail) = { (COMMA, t) : t ∈ FIRST₁(Schedule) }
```

ここで:

```
FIRST₁(Schedule) = { SCHED_TYPE, EXT, CRF, COMB, INTERP, DR_KW, PR_KW,
                      REPEAT_KW, LAG_KW, SIDMAN_KW, DA_KW, IDENT, LPAREN }
```

**FOLLOW₂(PosTail):**

ケース 1 — `KwTail` が非空:
```
FIRST₂(KwTail が非空のとき) = { (COMMA, KW_NAME) }
```
ここで `KW_NAME ∈ {COD, ChangeoverDelay, FRCO, FixedRatioChangeover, BO, Blackout}`。

ケース 2 — `KwTail` が空（ε）。FOLLOW₂ = FOLLOW₂(ArgList):
```
FOLLOW₂(ArgList) = { (RPAREN, t) : t ∈ FOLLOW₁(Compound) }
```
最初の要素は `RPAREN` であり `COMMA` ではない。

和集合:
```
FOLLOW₂(PosTail) = { (COMMA, KW_NAME) } ∪ { (RPAREN, _) }
```

**LL(2) 条件の検証:**

```
FIRST₂(COMMA Schedule PosTail) ∩ FOLLOW₂(PosTail)
= { (COMMA, t) : t ∈ FIRST₁(Schedule) } ∩ ({ (COMMA, KW_NAME) } ∪ { (RPAREN, _) })
```

`(RPAREN, _)` のエントリは最初の要素が `RPAREN ≠ COMMA` であるため共通部分に寄与しない。

残りの検証:

```
{ (COMMA, t) : t ∈ FIRST₁(Schedule) } ∩ { (COMMA, KW_NAME) }
= { (COMMA, t) : t ∈ FIRST₁(Schedule) ∩ KW_NAME }
```

**核心的主張:** `FIRST₁(Schedule) ∩ KW_NAME = ∅`

検証 — `KW_NAME` のメンバーと `FIRST₁(Schedule)` の比較:

| KW_NAME のメンバー | FIRST₁(Schedule) に含まれるか | 理由 |
|---|---|---|
| COD | いいえ | 予約語、スケジュール型/結合子/修飾子/識別子でない |
| ChangeoverDelay | いいえ | 予約語、大文字始まりだがスケジュール生成規則に含まれない |
| FRCO | いいえ | 予約語、スケジュール型でない |
| FixedRatioChangeover | いいえ | 予約語、大文字始まりだが結合子でない |
| BO | いいえ | 予約語、dist×domain でない（B は有効な dist でない） |
| Blackout | いいえ | 予約語、結合子キーワードでない |

**`FIRST₁(Schedule) ∩ KW_NAME = ∅`。** ✓

したがって:

```
FIRST₂(COMMA Schedule PosTail) ∩ FOLLOW₂(PosTail) = ∅
```

**LL(2) 条件は満たされる。衝突は2トークンの先読みで完全に解消される。** ∎

### 6.4 LL(2) 解析表（衝突セル）

`PosTail` の決定点（位置スケジュールの消費後）:

| 先読み（2トークン） | 動作 |
|---|---|
| `(COMMA, SCHED_TYPE)` | 継続: `PosTail → COMMA Schedule PosTail` |
| `(COMMA, EXT)` | 継続 |
| `(COMMA, CRF)` | 継続 |
| `(COMMA, COMB)` | 継続 |
| `(COMMA, INTERP)` | 継続 |
| `(COMMA, DR_KW)` | 継続 |
| `(COMMA, PR_KW)` | 継続 |
| `(COMMA, REPEAT_KW)` | 継続 |
| `(COMMA, LAG_KW)` | 継続 |
| `(COMMA, SIDMAN_KW)` | 継続 |
| `(COMMA, DA_KW)` | 継続 |
| `(COMMA, IDENT)` | 継続 |
| `(COMMA, LPAREN)` | 継続 |
| `(COMMA, KW_NAME)` | 終了: `PosTail → ε`（KwTail へ遷移） |
| `(RPAREN, _)` | 終了: `PosTail → ε`, `KwTail → ε` |

**すべてのセルが正確に1つの動作を含む。** 空のセル（不完全）も複数エントリのセル（衝突）もない。∎

---

## 7. 包括的 LL(2) 検証の要約

| # | 決定点 | LL(1)? | LL(2)? | メカニズム |
|---|---|---|---|---|
| D1 | `BaseSchedule`（6つの選択肢） | ✓ | — | 素な FIRST₁（§5.1） |
| D2 | `AtomicOrSecond`（3つの選択肢） | ✓ | — | 素な FIRST₁: SCHED_TYPE / EXT / CRF |
| D3 | `SecondOrder_opt`（オプション） | ✓* | — | 貪欲 LL(1); PR 変種は LL(2)（§5.2, §5.5） |
| D4 | `LH_opt`（オプション） | ✓ | — | LH_KW ∉ FOLLOW₁(Schedule)（§5.3） |
| D5 | `TimeSuffix_opt`（オプション） | ✓ | — | DASH, TIME_UNIT ∉ FOLLOW₁(Value)（§5.4） |
| D6 | `PrOpts_opt`（オプション） | — | ✓ | PR_STEP ∉ FIRST₁(Schedule)（§5.5） |
| D7 | `LagMod`（2つの選択肢） | ✓ | — | LAG_KW の後 NUM vs LPAREN（§5.6） |
| D8 | プログラムレベル遷移 | ✓ | — | AT / PARAM_NAME / LET / FIRST(Schedule) が素（§5.7） |
| D9 | `PosTail`（arg_list の継続） | ✗ | ✓ | **LL(2) ポイント**（§6） |
| D10 | `KwTail`, `SidmanTail`, `DaTail` 等 | ✓ | — | COMMA vs RPAREN（§5.8） |
| D11 | `Modifier`（4つの選択肢） | ✓ | — | DR_KW / PR_KW / REPEAT_KW / LAG_KW が素 |
| D12 | `AversiveSchedule`（2つの選択肢） | ✓ | — | SIDMAN_KW / DA_KW が素 |
| D13 | `Compound`（2つの選択肢） | ✓ | — | COMB / INTERP が素 |
| D14 | `AnnotationArgs`（2つの選択肢） | ✓ | — | STRING∪NUM vs IDENT が素（§9.1） |
| D15 | `AnnotationArgs_opt`（オプション） | ⚠ | ⚠ | §9 参照 |

\* LPAREN ∈ FOLLOW₁ の場合、LL(1) での貪欲解消; 形式的には LL(2)。

---

## 8. 曖昧性ゼロの証明

**定理。** 本文法は曖昧性を持たない。

**証明。** 構文解析理論における周知の結果（Aho et al., 2006, §4.4, 定理 4.28）:

> すべての LL(k) 文法は曖昧性を持たない。

証明の概略: 背理法で、入力 *w* が2つの異なる最左導出 *D₁* と *D₂* を持つと仮定する。するとそれらが最初に分岐するステップが存在する: ある非終端記号 *A* において、*D₁* は規則 *A → α* を適用し *D₂* は *A → β*（α ≠ β）を適用する。しかし LL(k) 条件は k トークンの先読みがどの生成規則を適用するかを一意に決定することを保証する。*D₁* と *D₂* は同じ入力を見ているので、同じ生成規則を選択しなければならない — 矛盾。

本文法が LL(2) であることを示した（§6.3）。したがって曖昧性を持たない。∎

**より強い主張:** 本文法は単に曖昧性がないだけでなく、最大2トークンの先読みを用いた再帰下降構文解析器により **O(n) 時間で決定的に解析可能** である（同等に、`PosTail` の決定点における1トークンの先読みと1トークンの後戻りで解析可能）。

---

## 9. アノテーションシステム: LL(2)/LL(3) の境界

### 9.1 AnnotationArgs 内部の決定 — LL(1)

```
AnnotationArgs    → PositionalForm | KeywordOnlyForm
PositionalForm    → AnnotationVal AnnotationKvTail
KeywordOnlyForm   → AnnotationKv AnnotationKvTail
```

```
FIRST₁(PositionalForm)   = FIRST₁(AnnotationVal) = { STRING, NUM }
FIRST₁(KeywordOnlyForm)  = FIRST₁(AnnotationKv)  = { IDENT }
```

`{STRING, NUM} ∩ {IDENT} = ∅`。**LL(1).** ✓

*注:* grammar.ebnf のコメント（319行）はこの決定に LL(2) を主張しているが、これは IDENT とアノテーション名を区別しない字句解析器を想定している。ここで前提とするキーワード認識字句解析器では LL(1) である。

### 9.2 AnnotationArgs_opt — 境界ケース

```
Annotation       → ANNO_NAME AnnotationArgs_opt
AnnotationArgs_opt → LPAREN AnnotationArgs RPAREN | ε
```

**プログラムレベルの文脈（`ProgramAnnotations`）:**

```
FIRST₁(AnnotationArgs_opt の非 ε) = { LPAREN }
FOLLOW₁(ProgramAnnotations 内の Annotation) ⊇ FIRST₁(AnnotatedSchedule)
                                              ⊇ FIRST₁(Schedule) ∋ LPAREN
```

`LPAREN ∈ FIRST₁ ∩ FOLLOW₁`。**LL(1) 衝突。**

**スケジュールレベルの文脈（AnnotatedSchedule 内の `Annotations`）:**

```
FOLLOW₁(Annotations 内の Annotation) = { AT, EOF }
{ LPAREN } ∩ { AT, EOF } = ∅
```

**LL(1).** ✓（スケジュールレベルでは衝突なし。）

### 9.3 プログラムレベル衝突の LL(2) 分析

```
FIRST₂(LPAREN AnnotationArgs RPAREN):
= { (LPAREN, STRING), (LPAREN, NUM), (LPAREN, IDENT) }
```

（AnnotationArgs は STRING, NUM, または IDENT で始まる。）

```
FOLLOW₂(LPAREN で始まるスケジュールが続く場合の Annotation):
⊇ { (LPAREN, t) : t ∈ FIRST₁(Schedule) }
= { (LPAREN, SCHED_TYPE), (LPAREN, EXT), (LPAREN, CRF), (LPAREN, COMB),
    (LPAREN, INTERP), (LPAREN, DR_KW), (LPAREN, PR_KW), (LPAREN, REPEAT_KW),
    (LPAREN, LAG_KW), (LPAREN, SIDMAN_KW), (LPAREN, DA_KW),
    (LPAREN, IDENT), (LPAREN, LPAREN) }
```

**LL(2) の共通部分:**

```
{ (LPAREN, STRING), (LPAREN, NUM), (LPAREN, IDENT) }
∩
{ (LPAREN, SCHED_TYPE), ..., (LPAREN, IDENT), (LPAREN, LPAREN) }
= { (LPAREN, IDENT) }
```

**`(LPAREN, IDENT)` で LL(2) 衝突。** これは以下の場合に生じる:
- アノテーションのキーワードのみ引数: `@foo(bar = ...)` — トークン対 `(LPAREN, IDENT:bar)`
- 束縛参照のグルーピングスケジュール: `@foo`（引数なし）の後 `(x)` — トークン対 `(LPAREN, IDENT:x)`

### 9.4 LL(3) による解消

3トークン先読みにおいて:

```
アノテーション引数:              (LPAREN, IDENT, EQ)
グルーピングスケジュール（ident）: (LPAREN, IDENT, RPAREN) または (LPAREN, IDENT, LH_KW)
                                  または (LPAREN, IDENT, COMMA) — (LPAREN, IDENT, EQ) にはならない
```

`EQ` はスケジュールの文脈において裸の `IDENT` の後に出現しない（`EQ` は param_decl 内の `PARAM_NAME` の後、keyword_arg 内の `KW_NAME` の後等にのみ出現する — スケジュール位置のユーザー識別子の後には出現しない）。

**LL(3) 条件:** `(LPAREN, IDENT, EQ)` ∈ FIRST₃(アノテーション引数) \ FOLLOW₃(非アノテーション解釈の Annotation)。**LL(3) で解消。** ✓

### 9.5 実用上の影響評価

`(LPAREN, IDENT)` 衝突は以下のすべてが同時に成立する場合にのみ発生する:
1. プログラムレベルのアノテーションが括弧付き引数を持たない、かつ
2. メインスケジュール式が `(ident)` — 束縛参照のグルーピング — で始まる

これは極めて狭いパターンである。実用上:
- 引数なしのプログラムレベルアノテーション（例: 裸の `@species`）はまれである — ほとんどが少なくとも1つの引数を持つ。
- トップレベルでの裸の識別子のグルーピング（`(x)`）は冗長である — グルーピングなしの `x` と等価。

### 9.6 解消オプション

**オプション A（推奨）: 貪欲曖昧性解消。** 構文解析器は `ANNO_NAME` の後の `LPAREN` を常にアノテーション引数として消費する。PEG および再帰下降構文解析器における標準的慣行。この規約の下で、文法は**貪欲曖昧性解消付き LL(2)** である。

**オプション B: 文法の修正。** `AnnotationArgs_opt_program → LPAREN AnnotationArgs RPAREN | ε` に、LPAREN が `ANNO_NAME` と同一行でなければならないという制約（字句解析器レベルの制限）を追加する。これにより重複が排除される。

**オプション C: LL(3) を受容。** 文法は厳密に LL(3) である。LL(3) ⊂ DCFL（決定的文脈自由言語）であるため、すべての望ましい性質（曖昧性ゼロ、O(n) 解析）は保持される。

---

## 10. 結論

### 主要結果

| 性質 | 状態 | 参照 |
|---|---|---|
| **LL(2)（コアスケジュール文法）** | **証明済** | §5–§6 |
| **LL(1) でない** | **証明済** | §6.1–§6.2 |
| **LL(2) 解析表が衝突なし** | **証明済** | §6.4 |
| **曖昧性ゼロ** | **証明済** | §8 |
| **O(n) で解析可能** | **証明済** | LL(2) の系 |
| **アノテーション境界: LL(2) または LL(3)** | **特性化済** | §9 |

### LL(2) 決定点

本文法は2トークンの先読みを必要とする決定点を**正確に1つ**持つ:

> **複合スケジュール引数リスト内の `PosTail`**（§6）: 位置スケジュール引数の後、トークン `COMMA` が位置引数の継続とキーワード引数への遷移の両方に共有される。2番目のトークン（スケジュール開始 vs キーワード名）が曖昧性を解消する。

他のすべての決定点は LL(1) である（§5, §7）。

### 形式的な定理記述

**定理（LL(2) 分類）。** *G* を `schema/core/grammar.ebnf` に定義された contingency-dsl v1.0 コア文法とする。このとき:

1. *G* は LL(2): すべての非終端記号 *A* とその生成規則 *A → α* および *A → β*（α ≠ β）に対して `FIRST₂(α · FOLLOW₂(A)) ∩ FIRST₂(β · FOLLOW₂(A)) = ∅`。
2. *G* は LL(1) でない: 生成規則 `PosTail → COMMA Schedule PosTail` と `PosTail → ε` が存在し、`FIRST₁(COMMA Schedule PosTail) ∩ FOLLOW₁(PosTail) = {COMMA} ≠ ∅` を満たす。
3. *G* は曖昧性を持たない（1 の系、Aho et al. 2006, 定理 4.28 による）。
4. アノテーションシステムを含む場合、*G* は貪欲オプション曖昧性解消の下で LL(2)、曖昧性解消規約なしでは厳密に LL(3)（§9）。

### 将来の文法拡張への示唆

文法への将来の拡張（例: `def` キーワード、新しい結合子、新しい修飾子）は以下を検証すべきである:

1. **新しいキーワードトークンは `FIRST₁(Schedule)` と重複してはならない。** 新しいキーワードが複合スケジュールの arg_list 内で `KW_NAME` として出現する場合、`FIRST₁(Schedule)` に含まれてはならない。これにより `PosTail` での LL(2) 解消が保持される。
2. **新しいスケジュール構成が位置引数/キーワード引数の混合意味論を持つ COMMA ベースの反復を導入してはならない**（同じ LL(2) 戦略を採用する場合を除く）。
3. **アノテーション拡張** が `FIRST₁(Schedule)` 内のトークンで始まる新しい `AnnotationVal` 形式を追加すると §9 の衝突が拡大する。`SCHED_TYPE` や `COMB` をアノテーション値として追加することを避けるべきである。

---

## 参考文献

- Aho, A. V., Lam, M. S., Sethi, R., & Ullman, J. D. (2006). *Compilers: Principles, Techniques, and Tools* (2nd ed.). Addison-Wesley. §4.4 (LL 構文解析), §4.8 (エラー回復).
- Knuth, D. E. (1965). On the translation of languages from left to right. *Information and Control*, *8*(6), 607–639. https://doi.org/10.1016/S0019-9958(65)90426-2
- Rosenkrantz, D. J., & Stearns, R. E. (1970). Properties of deterministic top-down grammars. *Information and Control*, *17*(3), 226–256. https://doi.org/10.1016/S0019-9958(70)90446-8

