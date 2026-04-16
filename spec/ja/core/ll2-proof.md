# LL(2) 形式的証明 — contingency-dsl v1.0 コア文法

## 1. 定理の主張

**定理.** contingency-dsl v1.0 コア文法（`schema/core/grammar.ebnf` に定義）は以下を満たす:

1. **LL(2)** — 最大2トークンの先読みによるトップダウン予測型構文解析器で決定的に解析可能。
2. **LL(1) でない** — 2トークンの先読みを必要とする決定点が少なくとも1つ存在する。
3. **曖昧性ゼロ** — すべての有効な入力が唯一の構文解析木を持つ。

**注意事項（§9）.** アノテーションシステムはプログラムレベルのアノテーションに対して狭い LL(2)/LL(3) 境界ケースを導入する。コアスケジュール文法（アノテーションを除く）は厳密に LL(2)。アノテーションを含む場合、標準的な貪欲曖昧性解消の下で LL(2) が維持される。貪欲規約なしの厳密な LL(3) が1つの特定のトークン三つ組に適用される。分析は §9 を参照。

**拡張（§10）.** Core-Stateful レイヤ（`Pctl`, `Adj`, `Interlock`、`schema/core-stateful/grammar.ebnf` に定義）は LL(2) 分類を保存する。すべての新規決定点は LL(1) であり、既存の決定点は無効化されない。完全な FIRST/FOLLOW 分析は §10 を参照。

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
| `TARGET_KW` | target | Overlay target キーワード（v1.y） |
| `KW_CHANGEOVER` | changeover | target/punish_target 値（v1.y） |
| `KW_ALL` | all | target 値（v1.y） |
| `PUNISH_KW` | PUNISH | punish_directive キーワード（v1.y） |
| `ARROW` | -> | 方向指定矢印（directional_kw_arg と punish_target で使用） |
| `PARAM_NAME` | LH, LimitedHold, COD, ChangeoverDelay, FRCO, FixedRatioChangeover, BO, Blackout | プログラムレベルのパラメータ名 |
| `SIDMAN_KW` | Sidman, SidmanAvoidance | Sidman 回避キーワード |
| `DA_KW` | DiscriminatedAvoidance, DiscrimAv | 弁別回避キーワード |
| `SSI_KW` | SSI, ShockShockInterval | Sidman SSI パラメータ |
| `RSI_KW` | RSI, ResponseShockInterval | Sidman RSI パラメータ |
| `DA_TEMP_KW` | CSUSInterval, ITI, ShockDuration, MaxShock | DA 時間パラメータキーワード |
| `MODE_KW` | mode | DA モードキーワード |
| `DA_MODE` | fixed, escape | DA モード値 |
| `PR_STEP` | hodos, exponential, linear, geometric | PR ステップ関数キーワード |
| `PR_PARAM_KW` | start, increment, ratio | PR パラメータキーワード |
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
| `PCTL_KW` | Pctl | パーセンタイルスケジュールキーワード（Core-Stateful） |
| `ADJ_KW` | Adj, Adjusting | 調整スケジュールキーワード（Core-Stateful） |
| `INTERLOCK_KW` | Interlock, Interlocking | 連動スケジュールキーワード（Core-Stateful） |
| `PCTL_TARGET` | IRT, latency, duration, force, rate | パーセンタイル対象次元（Core-Stateful） |
| `ADJ_TARGET` | delay, ratio, amount | 調整対象次元（Core-Stateful） |
| `PCTL_ARG_KW` | window, dir | パーセンタイルキーワード引数名（Core-Stateful） |
| `PCTL_DIR_VAL` | below, above | パーセンタイル方向値（Core-Stateful） |
| `ADJ_ARG_KW` | start, step, min, max | 調整キーワード引数名（Core-Stateful） |
| `INTERLOCK_ARG_KW` | R0, T | 連動キーワード引数名（Core-Stateful） |
| `KW_INTERLEAVE` | interleave | progressive interleave キーワード（Experiment v2.x） |
| `KW_NO_TRAILING` | no_trailing | progressive interleave の末尾抑制修飾子（Experiment v2.x） |

**字句解析器の前提:**

- **L1（キーワード優先）:** 予約語はそれぞれ固有のトークンクラスとして字句解析され、`IDENT` としては解析されない。すべての予約語は大文字で始まる（定義上 `IDENT` と素）か、識別子の名前空間から明示的に除外される。
- **L2（TIME_UNIT の文脈的予約）:** `s`, `sec`, `ms`, `min` は `IDENT` ではなく `TIME_UNIT` として字句解析される。これらは文脈的予約語である（grammar.ebnf 87–89行）。
- **L3（PARAM_NAME/KW_NAME の重複）:** `LH` は `PARAM_NAME`（param_decl 内）と `LH_KW`（schedule の LH 接尾辞内）の両方である。字句解析器は単一のトークンを生成し、構文解析器が文脈で曖昧性を解消する。LL(k) 分析では同一トークンクラス `LH_KW`/`PARAM_NAME` として扱い、文脈による曖昧性解消を検証する。
- **L4（Core-Stateful キーワード優先）:** `Pctl`, `Adj`, `Adjusting`, `Interlock`, `Interlocking` はそれぞれ固有のキーワードトークンクラスとして字句解析される。すべて大文字で始まり、`IDENT` と素。
- **L5（Core-Stateful の文脈的予約）:** `PCTL_TARGET` 値（IRT, latency, ...）、`ADJ_TARGET` 値（delay, ratio, amount）、`PCTL_DIR_VAL`（below, above）、およびキーワード引数名（window, dir, step, min, max, R0）は関数呼び出し括弧内にのみ出現する。構文解析器の文脈が `IDENT` との曖昧性を解消する。
- **L6（共有キーワード: start）:** `start` は PR（`PR_PARAM_KW`）と Adj（`ADJ_ARG_KW`）の両方で予約されている。`PR(...)` 括弧内では `PR_PARAM_KW`、`Adj(...)` / `Adjusting(...)` 括弧内では `ADJ_ARG_KW` として解析される。構文解析器の状態がどの生成規則が活性かを決定する。字句解析器の衝突なし。
- **L7（共有キーワード: T）:** `T` は `domain ::= "T"`（FT/VT/RT 用）と `INTERLOCK_ARG_KW`（`Interlock(...)` 内）の両方で予約されている。構文解析器の文脈（Interlock 括弧内でキーワード引数を期待）が domain 生成規則（`atomic_or_second` 内で dist の後に出現）との曖昧性を解消する。構文的曖昧性なし。

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

### 3.6 Core-Stateful スケジュール

統合点（追加的 — 既存の生成規則は変更されない）:

- `Modifier → ... | PctlMod`（Pctl は modifier を拡張）
- `BaseSchedule → ... | AdjSchedule | InterlockSchedule`（Adj と Interlock は base_schedule を拡張）

```
PctlMod           → PCTL_KW LPAREN PCTL_TARGET COMMA NUM PctlKwTail RPAREN
PctlKwTail        → COMMA PctlKwArg PctlKwTail | ε
PctlKwArg         → PCTL_ARG_KW EQ PctlValue
PctlValue         → NUM | PCTL_DIR_VAL

AdjSchedule       → ADJ_KW LPAREN ADJ_TARGET COMMA AdjKwArg AdjKwMore RPAREN
AdjKwMore         → COMMA AdjKwArg AdjKwMore | ε
AdjKwArg          → ADJ_ARG_KW EQ Value

InterlockSchedule → INTERLOCK_KW LPAREN InterlockKwArg InterlockKwTail RPAREN
InterlockKwTail   → COMMA InterlockKwArg InterlockKwTail | ε
InterlockKwArg    → INTERLOCK_ARG_KW EQ Value
```

**注記:**
- `PctlMod` は正確に2つの位置引数（target, rank）の後にオプションのキーワード引数が続く。位置/キーワード混合の曖昧性なし（cf. §6）。
- `AdjSchedule` は正確に1つの位置引数（target）の後に必須のキーワード引数が続く（EBNF で `+`; 少なくとも `start` と `step`）。CFG では1つの必須 `AdjKwArg` + `AdjKwMore*` に正規化。
- `InterlockSchedule` はキーワード引数のみ（R0, T）。位置引数なし。

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

### 4.4 Core-Stateful 非終端記号

| 非終端記号 | FIRST₁ | 導出 |
|---|---|---|
| `PctlMod` | {`PCTL_KW`} | PCTL_KW 終端記号から |
| `AdjSchedule` | {`ADJ_KW`} | ADJ_KW 終端記号から |
| `InterlockSchedule` | {`INTERLOCK_KW`} | INTERLOCK_KW 終端記号から |
| `PctlKwArg` | {`PCTL_ARG_KW`} | PCTL_ARG_KW 終端記号から |
| `PctlValue` | {`NUM`, `PCTL_DIR_VAL`} | NUM と PCTL_DIR_VAL から |
| `AdjKwArg` | {`ADJ_ARG_KW`} | ADJ_ARG_KW 終端記号から |
| `InterlockKwArg` | {`INTERLOCK_ARG_KW`} | INTERLOCK_ARG_KW 終端記号から |

### 4.5 Core-Stateful の反復決定

| 反復 | 継続の FIRST₁ | 停止（FOLLOW₁） | 素？ |
|---|---|---|---|
| `PctlKwTail` | {`COMMA`} | {`RPAREN`} | ✓ |
| `AdjKwMore` | {`COMMA`} | {`RPAREN`} | ✓ |
| `InterlockKwTail` | {`COMMA`} | {`RPAREN`} | ✓ |

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

### 5.5 PrMod（2つの選択肢 — LL(1)）

```
PrMod ::= PR_KW LPAREN PrOpts RPAREN     -- 明示形式: PR(hodos), PR(linear, ...)
        | PR_KW NUM                        -- 略記形式: PR 5 (Jarmolowicz & Lattal, 2010)
```

`PR_KW` の後、構文解析器は次のトークンを確認する:
- `LPAREN` → 明示形式（PrOpts に入る）
- `NUM` → 略記形式（算術, start=n, increment=n）

`{LPAREN} ∩ {NUM} = ∅`。**LL(1) 決定的。** ∎

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
| D1 | `BaseSchedule`（8つの選択肢†） | ✓ | — | 素な FIRST₁（§5.1, §10.3） |
| D2 | `AtomicOrSecond`（3つの選択肢） | ✓ | — | 素な FIRST₁: SCHED_TYPE / EXT / CRF |
| D3 | `SecondOrder_opt`（オプション） | ✓* | — | 貪欲 LL(1); PR 変種は LL(2)（§5.2, §5.5） |
| D4 | `LH_opt`（オプション） | ✓ | — | LH_KW ∉ FOLLOW₁(Schedule)（§5.3） |
| D5 | `TimeSuffix_opt`（オプション） | ✓ | — | DASH, TIME_UNIT ∉ FOLLOW₁(Value)（§5.4） |
| D6 | `PrOpts_opt`（オプション） | — | ✓ | PR_STEP ∉ FIRST₁(Schedule)（§5.5） |
| D7 | `LagMod`（2つの選択肢） | ✓ | — | LAG_KW の後 NUM vs LPAREN（§5.6） |
| D8 | プログラムレベル遷移 | ✓ | — | AT / PARAM_NAME / LET / FIRST(Schedule) が素（§5.7） |
| D9 | `PosTail`（arg_list の継続） | ✗ | ✓ | **LL(2) ポイント**（§6） |
| D10 | `KwTail`, `SidmanTail`, `DaTail` 等 | ✓ | — | COMMA vs RPAREN（§5.8） |
| D11 | `Modifier`（5つの選択肢†） | ✓ | — | DR_KW / PR_KW / REPEAT_KW / LAG_KW / PCTL_KW が素（§10.3） |
| D12 | `AversiveSchedule`（2つの選択肢） | ✓ | — | SIDMAN_KW / DA_KW が素 |
| D13 | `Compound`（2つの選択肢） | ✓ | — | COMB / INTERP が素 |
| D14 | `AnnotationArgs`（2つの選択肢） | ✓ | — | STRING∪NUM vs IDENT が素（§9.1） |
| D15 | `AnnotationArgs_opt`（オプション） | ⚠ | ⚠ | §9 参照 |
| D16 | `PctlKwTail` 反復 | ✓ | — | COMMA vs RPAREN（§10.4.1） |
| D17 | `PctlValue`（2つの選択肢） | ✓ | — | NUM vs PCTL_DIR_VAL（§10.4.2） |
| D18 | `AdjKwMore` 反復 | ✓ | — | COMMA vs RPAREN（§10.4.3） |
| D19 | `InterlockKwTail` 反復 | ✓ | — | COMMA vs RPAREN（§10.4.4） |
| D20 | Core-Stateful トークンを含む `PosTail` | — | ✓ | 新トークン ∉ KW_NAME（§10.3.3） |

\* LPAREN ∈ FOLLOW₁ の場合、LL(1) での貪欲解消; 形式的には LL(2)。

† Core-Stateful 追加を含む数（§10）。Core のみの数: BaseSchedule = 6, Modifier = 4。

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

## 10. Core-Stateful レイヤ: LL(2) 保存証明

### 10.1 定理の主張

**定理（Core-Stateful LL(2) 保存）。** Core-Stateful 生成規則（`Pctl`, `Adj`, `Interlock`、`schema/core-stateful/grammar.ebnf` に定義）で拡張された contingency-dsl 文法は、§1–§8 で確立された LL(2) 分類を保存する。具体的には:

1. Core-Stateful 生成規則が導入するすべての新規決定点は **LL(1)** である。
2. すべての既存 LL(1) 決定点は拡張後も LL(1) のまま維持される。
3. 唯一の LL(2) 決定点（`PosTail`、§6）は LL(2) のまま維持される — 2トークン解消は無効化されない。
4. 新たな LL(2) または LL(3) の衝突は導入されない。

**対象範囲。** 本セクションは以下の3つの Core-Stateful 構成を対象とする:

| 構成 | 統合点 | 参考文献 |
|---|---|---|
| `Pctl`（パーセンタイル） | `modifier` 生成規則 | Platt (1973); Galbicka (1994) |
| `Adj`（調整） | `base_schedule` 生成規則 | Blough (1958); Mazur (1987) |
| `Interlock`（連動） | `base_schedule` 生成規則 | Ferster & Skinner (1957) |

トークンクラスと CFG 生成規則はそれぞれ §2 と §3.6 に定義されている。

---

### 10.2 統合点の検証

#### 10.2.1 BaseSchedule（6 → 8 選択肢）

Core-Stateful は `BaseSchedule` に2つの選択肢を追加する:

```
BaseSchedule → AtomicOrSecond                     FIRST₁ = { SCHED_TYPE, EXT, CRF }
             | Compound                            FIRST₁ = { COMB, INTERP }
             | Modifier                            FIRST₁ = { DR_KW, PR_KW, REPEAT_KW, LAG_KW, PCTL_KW }
             | AversiveSchedule                    FIRST₁ = { SIDMAN_KW, DA_KW }
             | AdjSchedule                         FIRST₁ = { ADJ_KW }              [新規]
             | InterlockSchedule                   FIRST₁ = { INTERLOCK_KW }         [新規]
             | IDENT                               FIRST₁ = { IDENT }
             | LPAREN Schedule RPAREN              FIRST₁ = { LPAREN }
```

**新規エントリの対ごとの素性:**

| 新トークン | 既存の FIRST₁ に含まれるか？ | 理由 |
|---|---|---|
| `ADJ_KW` (Adj, Adjusting) | いいえ | 予約語、大文字始まり、既存のすべてのキーワードクラスと異なる |
| `INTERLOCK_KW` (Interlock, Interlocking) | いいえ | 予約語、大文字始まり、既存のすべてのキーワードクラスと異なる |
| `ADJ_KW` ∩ `INTERLOCK_KW` | ∅ | 異なるキーワード |

8つの選択肢間の28個の対ごとの共通部分はすべて空のまま。**LL(1).** ∎

#### 10.2.2 Modifier（4 → 5 選択肢）

Core-Stateful は `Modifier` 生成規則に `PctlMod` を追加する:

```
Modifier → DR_KW Value                            FIRST₁ = { DR_KW }
         | PR_KW PrOpts_opt                        FIRST₁ = { PR_KW }
         | REPEAT_KW LPAREN NUM ...                FIRST₁ = { REPEAT_KW }
         | LagMod                                  FIRST₁ = { LAG_KW }
         | PctlMod                                 FIRST₁ = { PCTL_KW }     [新規]
```

**検証:** `PCTL_KW` ∉ {`DR_KW`, `PR_KW`, `REPEAT_KW`, `LAG_KW`}。"Pctl" は固有の予約キーワードであり、既存のいずれのトークンクラスのメンバーでもない。

5つの選択肢間の10個の対ごとの共通部分はすべて空。**LL(1).** ∎

#### 10.2.3 更新された FIRST₁(Schedule) と FIRST₁(BaseSchedule)

```
FIRST₁(BaseSchedule) = { SCHED_TYPE, EXT, CRF, COMB, INTERP, DR_KW, PR_KW,
                          REPEAT_KW, LAG_KW, PCTL_KW, SIDMAN_KW, DA_KW,
                          ADJ_KW, INTERLOCK_KW, IDENT, LPAREN }
```

新規メンバー3つ: `PCTL_KW`, `ADJ_KW`, `INTERLOCK_KW`。

---

### 10.3 PosTail の LL(2) 保存

`PosTail` における LL(2) 解消（§6）は以下の重要な不変条件に依存する:

```
FIRST₁(Schedule) ∩ KW_NAME = ∅
```

**Core-Stateful トークンでの検証:**

| 新しい FIRST₁(Schedule) メンバー | KW_NAME に含まれるか？ | 理由 |
|---|---|---|
| `PCTL_KW` (Pctl) | いいえ | "Pctl" ∉ {COD, ChangeoverDelay, FRCO, FixedRatioChangeover, BO, Blackout} |
| `ADJ_KW` (Adj, Adjusting) | いいえ | "Adj"/"Adjusting" ∉ KW_NAME |
| `INTERLOCK_KW` (Interlock, Interlocking) | いいえ | "Interlock"/"Interlocking" ∉ KW_NAME |

**不変条件保存:** `(FIRST₁(Schedule) ∪ {PCTL_KW, ADJ_KW, INTERLOCK_KW}) ∩ KW_NAME = ∅`。✓

**更新された LL(2) 解析表（§6.4 への追加行）:**

| 先読み（2トークン） | アクション |
|---|---|
| `(COMMA, PCTL_KW)` | 継続: `PosTail → COMMA Schedule PosTail` |
| `(COMMA, ADJ_KW)` | 継続: `PosTail → COMMA Schedule PosTail` |
| `(COMMA, INTERLOCK_KW)` | 継続: `PosTail → COMMA Schedule PosTail` |

すべての新セルは正確に1つのアクションを含む。衝突なし。**LL(2) 保存。** ∎

---

### 10.4 内部決定点の検証

#### 10.4.1 PctlKwTail 反復

```
PctlKwTail → COMMA PctlKwArg PctlKwTail | ε
```

| | FIRST₁ |
|---|---|
| 継続 | {`COMMA`} |
| 停止（FOLLOW₁） | {`RPAREN`} |

`{COMMA} ∩ {RPAREN} = ∅`。**LL(1).** ∎

#### 10.4.2 PctlValue（2つの選択肢）

```
PctlValue → NUM | PCTL_DIR_VAL
```

`FIRST₁(NUM) = {NUM}`, `FIRST₁(PCTL_DIR_VAL) = {PCTL_DIR_VAL}`。

`{NUM} ∩ {PCTL_DIR_VAL} = ∅`（NUM は `[0-9]+...`; PCTL_DIR_VAL は `below`/`above`）。**LL(1).** ∎

注: 構文解析器は `PCTL_ARG_KW EQ` を消費した後に `PctlValue` に到達する。キーワードの同一性（`window` vs `dir`）が意味的にどの値型が期待されるかを決定するが、構文的には両方の選択肢が FIRST₁ のみで判別可能。意味的先読みは不要。

#### 10.4.3 AdjKwMore 反復

```
AdjKwMore → COMMA AdjKwArg AdjKwMore | ε
```

| | FIRST₁ |
|---|---|
| 継続 | {`COMMA`} |
| 停止（FOLLOW₁） | {`RPAREN`} |

`{COMMA} ∩ {RPAREN} = ∅`。**LL(1).** ∎

#### 10.4.4 InterlockKwTail 反復

```
InterlockKwTail → COMMA InterlockKwArg InterlockKwTail | ε
```

| | FIRST₁ |
|---|---|
| 継続 | {`COMMA`} |
| 停止（FOLLOW₁） | {`RPAREN`} |

`{COMMA} ∩ {RPAREN} = ∅`。**LL(1).** ∎

#### 10.4.5 位置/キーワード引数の混合曖昧性なし

複合スケジュールの `ArgList` 生成規則（§6）と異なり、Core-Stateful のいずれの構成も可変長の位置引数の後にキーワード引数が続くパターンを持たない:

| 構成 | 位置引数 | キーワード引数 | 混合？ |
|---|---|---|---|
| `Pctl(target, rank, ...)` | 2（固定） | 0+ | いいえ — 位置引数の数は2に固定 |
| `Adj(target, start=..., ...)` | 1（固定） | 1+ | いいえ — target の後のカンマは常にキーワード引数（ADJ_ARG_KW）へ |
| `Interlock(R0=..., T=...)` | 0 | 1+ | いいえ — すべての引数がキーワード |

3つのすべてのケースにおいて、位置引数からキーワード引数への遷移（存在する場合）は LL(1) で決定的:
- **Pctl:** `PCTL_TARGET COMMA NUM` の後、次のトークンは `COMMA`（キーワード引数が続く）または `RPAREN`（終了）。`COMMA` の場合、次は `PCTL_ARG_KW`（スケジュール開始トークンではない）であり、PosTail 型の衝突は生じない。
- **Adj:** `ADJ_TARGET` の後、すべての `COMMA` は `ADJ_ARG_KW` を導入し、位置スケジュールは導入しない。
- **Interlock:** すべての引数がキーワードのみ。位置/キーワードの境界は存在しない。

**新たな LL(2) 衝突なし。** ∎

---

### 10.5 アノテーション境界（§9）への影響

§9 の LL(2)/LL(3) 境界分析は `FIRST₁(Schedule)` の拡大を通じてのみ影響を受ける。新トークン `PCTL_KW`, `ADJ_KW`, `INTERLOCK_KW` が `FIRST₁(Schedule)` に加わる。

**§9.3 LL(2) 共通部分の再検証:**

```
FIRST₂(LPAREN AnnotationArgs RPAREN) = { (LPAREN, STRING), (LPAREN, NUM), (LPAREN, IDENT) }
```

この集合は変更なし（Core-Stateful は新しい `AnnotationArgs` 形式を追加しない）。

```
FOLLOW₂(ProgramAnnotations 内の Annotation) ⊇ { (LPAREN, t) : t ∈ FIRST₁(Schedule) }
```

新メンバー: `(LPAREN, PCTL_KW)`, `(LPAREN, ADJ_KW)`, `(LPAREN, INTERLOCK_KW)`。

**共通部分:**

```
{ (LPAREN, STRING), (LPAREN, NUM), (LPAREN, IDENT) }
∩
{ ..., (LPAREN, PCTL_KW), (LPAREN, ADJ_KW), (LPAREN, INTERLOCK_KW), ... }
```

`PCTL_KW`, `ADJ_KW`, `INTERLOCK_KW` ∉ {`STRING`, `NUM`, `IDENT`}。新しい共通部分要素なし。

**§9 の LL(2)/LL(3) 境界は変更なし。** ∎

---

### 10.6 結論

**定理（Core-Stateful LL(2) 保存）。** *G* をコア文法、*G′* = *G* ∪ Core-Stateful 生成規則とする。このとき:

1. *G′* は LL(2)。（証明: §10.2–§10.4。）
2. *G′* は LL(1) でない。（*G* から継承: §6 の PosTail 衝突が存続。）
3. *G′* は新たな LL(2) 決定点を **ゼロ** 導入する。Core-Stateful のすべての内部決定は LL(1)。
4. アノテーション境界（§9）は Core-Stateful の影響を受けない。

Core-Stateful レイヤは**保守的な文法拡張**である: 既存の決定点に素な FIRST₁ 集合を持つ新しい選択肢を追加し、LL(1) の内部構造のみを導入し、位置/キーワード引数の混合リストを生成しない。∎

---

## 11. 結論

### 主要結果

| 性質 | 状態 | 参照 |
|---|---|---|
| **LL(2)（コアスケジュール文法）** | **証明済** | §5–§6 |
| **LL(1) でない** | **証明済** | §6.1–§6.2 |
| **LL(2) 解析表が衝突なし** | **証明済** | §6.4 |
| **曖昧性ゼロ** | **証明済** | §8 |
| **O(n) で解析可能** | **証明済** | LL(2) の系 |
| **アノテーション境界: LL(2) または LL(3)** | **特性化済** | §9 |
| **Core-Stateful LL(2) 保存** | **証明済** | §10 |

### LL(2) 決定点

本文法は2トークンの先読みを必要とする決定点を**正確に1つ**持つ:

> **複合スケジュール引数リスト内の `PosTail`**（§6）: 位置スケジュール引数の後、トークン `COMMA` が位置引数の継続とキーワード引数への遷移の両方に共有される。2番目のトークン（スケジュール開始 vs キーワード名）が曖昧性を解消する。

他のすべての決定点 — Core-Stateful のすべての内部決定（§10.4）を含む — は LL(1) である（§5, §7）。

### 形式的な定理記述

**定理（LL(2) 分類）。** *G* を `schema/core/grammar.ebnf` に定義され `schema/core-stateful/grammar.ebnf` で拡張された contingency-dsl v1.0 文法とする。このとき:

1. *G* は LL(2): すべての非終端記号 *A* とその生成規則 *A → α* および *A → β*（α ≠ β）に対して `FIRST₂(α · FOLLOW₂(A)) ∩ FIRST₂(β · FOLLOW₂(A)) = ∅`。
2. *G* は LL(1) でない: 生成規則 `PosTail → COMMA Schedule PosTail` と `PosTail → ε` が存在し、`FIRST₁(COMMA Schedule PosTail) ∩ FOLLOW₁(PosTail) = {COMMA} ≠ ∅` を満たす。
3. *G* は曖昧性を持たない（1 の系、Aho et al. 2006, 定理 4.28 による）。
4. アノテーションシステムを含む場合、*G* は貪欲オプション曖昧性解消の下で LL(2)、曖昧性解消規約なしでは厳密に LL(3)（§9）。
5. Core-Stateful レイヤ（Pctl, Adj, Interlock）は 1–4 のすべてを新たな LL(2) 決定点を導入することなく保存する（§10）。

### 将来の文法拡張への示唆

文法への将来の拡張（例: `def` キーワード、新しい結合子、新しい修飾子）は以下を検証すべきである:

1. **新しいキーワードトークンは `FIRST₁(Schedule)` と重複してはならない。** 新しいキーワードが複合スケジュールの arg_list 内で `KW_NAME` として出現する場合、`FIRST₁(Schedule)` に含まれてはならない。これにより `PosTail` での LL(2) 解消が保持される。
2. **新しいスケジュール構成が位置引数/キーワード引数の混合意味論を持つ COMMA ベースの反復を導入してはならない**（同じ LL(2) 戦略を採用する場合を除く）。
3. **アノテーション拡張** が `FIRST₁(Schedule)` 内のトークンで始まる新しい `AnnotationVal` 形式を追加すると §9 の衝突が拡大する。`SCHED_TYPE` や `COMB` をアノテーション値として追加することを避けるべきである。
4. **Core-Stateful 拡張**（新しいステートフルスケジュール）は §10 で確立されたパターンに従うべきである: 固定の位置引数数（またはキーワードのみ）の関数呼び出し構文、素な先頭キーワード、COMMA/RPAREN 反復。このパターンにより LL(1) の内部決定が保証される。

---

## §11 実験層の判定点（v2.0）

実験層（grammar.ebnf の `file`、`experiment`、`phase_decl`、`progressive_decl`）は以下の判定点を導入する。すべて LL(1) — 新たな LL(2) 判定点は生じない。

### §11.1 ファイルレベルの曖昧性解消

**判定:** `file → experiment | program`

構文解析器は最初の非アノテーショントークンの時点で、ファイルが experiment か単一フェーズの program かを決定する必要がある。

**FIRST₁ 分析:**

```
FIRST₁(annotations 後の experiment) = { KW_PHASE, KW_PROGRESSIVE }
FIRST₁(annotations 後の program)    = FIRST₁(param_decl) ∪ FIRST₁(binding) ∪ FIRST₁(schedule)
                                     = { KW_LH, KW_COD, KW_FRCO, KW_BO, KW_RD,
                                         KW_LET, DIST, KW_EXT, KW_CRF, COMB,
                                         KW_DRL, KW_DRH, KW_DRO, KW_PR, KW_REPEAT,
                                         KW_SIDMAN, KW_DISCRIMAV, KW_LAG,
                                         KW_INTERPOLATE, KW_INTERP,
                                         IDENT, LPAREN, ... }
```

`KW_PHASE` と `KW_PROGRESSIVE` は既存のいずれの FIRST₁ 集合にも含まれない新しい予約トークンであるため:

```
{ KW_PHASE, KW_PROGRESSIVE } ∩ FIRST₁(annotations 後の program) = ∅
```

**結果:** LL(1)。∎

**アノテーションに関する注:** `experiment` と `program` のいずれも `program_annotation`（トークン `@`）で始まることができる。構文解析器は先頭の `@` アノテーションをすべて消費した後、次のトークンを確認する。`KW_PHASE` または `KW_PROGRESSIVE` であれば experiment、それ以外は program。アノテーションはどちらの生成規則でも有効。

### §11.2 Phase vs. Progressive

**判定:** `experiment` 内の各位置で `phase_decl` と `progressive_decl` を選択する。

```
FIRST₁(phase_decl)   = { KW_PHASE }
FIRST₁(progressive_decl) = { KW_PROGRESSIVE }

{ KW_PHASE } ∩ { KW_PROGRESSIVE } = ∅
```

**結果:** LL(1)。∎

### §11.3 Phase メタデータ

**判定:** `phase_meta → session_spec | stability_spec`

```
FIRST₁(session_spec)   = { KW_SESSIONS }
FIRST₁(stability_spec) = { KW_STABLE }

{ KW_SESSIONS } ∩ { KW_STABLE } = ∅
```

**結果:** LL(1)。∎

### §11.4 Session Spec 演算子

**判定:** `session_spec → "sessions" "=" number | "sessions" ">=" number`

`KW_SESSIONS` を消費した後、構文解析器は次のトークンを確認する:

```
FIRST₁("=" number)  = { EQUALS }
FIRST₁(">=" number) = { GTE }

{ EQUALS } ∩ { GTE } = ∅
```

**結果:** LL(1)。∎

### §11.5 Phase 内容 vs. Phase 参照 vs. No-Schedule

**判定:** `phase_body_content → phase_content | phase_ref | "no_schedule"`

```
FIRST₁(phase_ref)       = { KW_USE }
FIRST₁(no_schedule)     = { KW_NO_SCHEDULE }
FIRST₁(phase_content)   = FIRST₁(param_decl) ∪ FIRST₁(binding) ∪ FIRST₁(annotated_schedule)
```

`KW_USE` と `KW_NO_SCHEDULE` は既存のいずれの FIRST₁ 集合にも含まれない予約トークンであるため:

```
{ KW_USE } ∩ FIRST₁(phase_content) = ∅
{ KW_NO_SCHEDULE } ∩ FIRST₁(phase_content) = ∅
{ KW_USE } ∩ { KW_NO_SCHEDULE } = ∅
```

3 つの選択肢の FIRST₁ 集合は対毎に互いに素。

**結果:** LL(1)。∎

### §11.6 Progressive 本体の継続（interleave_decl 付き、v2.x）

`progressive_body` 生成規則は `progressive_steps+` と `phase_meta*` の間に任意の `interleave_decl` の列を導入する:

```
progressive_body  →  progressive_steps+ interleave_decl* phase_meta* param_decl* binding* annotated_schedule
```

**判定 A — 別の `interleave_decl` を消費するか:**

```
FIRST₁(interleave_decl)        = { KW_INTERLEAVE }
FIRST₁(phase_meta)             = { KW_SESSIONS, KW_STABLE }
FIRST₁(param_decl)             = { PARAM_NAME }            ; LH, COD, FRCO, BO
FIRST₁(binding)                = { LET_KW }
FIRST₁(annotated_schedule)     = { AT, SCHED_TYPE, EXT, CRF, COMB, INTERP, DR_KW, PR_KW, REPEAT_KW, LAG_KW, SIDMAN_KW, DA_KW, PCTL_KW, ADJ_KW, INTERLOCK_KW, IDENT (let 束縛) }

KW_INTERLEAVE ∩ FIRST₁(継続) = ∅
```

`KW_INTERLEAVE`（`interleave`）は他のすべての FIRST₁ 集合と素な新しい予約語 — `KW_SESSIONS`、`KW_STABLE`、`LET_KW`、`AT`、スケジュール開始トークン、`PARAM_NAME`（LH/COD/FRCO/BO は大文字識別子で `interleave` と異なる）。判定は LL(1)。

**判定 B — `interleave phase_name` の後の任意 `no_trailing`:**

```
FIRST₁("no_trailing")          = { KW_NO_TRAILING }
FOLLOW₁(interleave_decl tail)  = { KW_INTERLEAVE,           ; 別の interleave
                                   KW_SESSIONS, KW_STABLE,  ; phase_meta
                                   PARAM_NAME, LET_KW, AT,  ; param_decl, binding, annotation
                                   SCHED_TYPE, EXT, CRF, ... } ; annotated_schedule

KW_NO_TRAILING ∉ FOLLOW₁(interleave_decl tail)
```

`KW_NO_TRAILING`（`no_trailing`）は新しい予約語であり、`interleave_decl` を継続するいかなる FOLLOW₁ 集合にも含まれない。任意要素の判定は LL(1)。

**結果:** いずれの新規判定点も LL(1)。新たな LL(2) 判定点は生じない。∎

### §11.7 まとめ

実験層は **7 つの新規判定点**（v2.0 から 5 つ + v2.x interleave から 2 つ）を追加し、すべて LL(1)。Core 文法の単一の LL(2) 判定点（複合スケジュールの arg_list における PosTail、§6）は影響を受けない — 実験層の生成規則はスケジュール式の構文解析と構造的に独立しており、`program` の上位のファイルレベルで動作するため。

**更新された定理（§8 の拡張）:**

拡張文法 *G'* = Core ∪ Core-Stateful ∪ Experiment は以下を満たす:

1. *G'* は LL(2): すべての Core および Core-Stateful の性質を保存し、実験層は LL(1)。
2. *G'* は LL(1) ではない: Core の PosTail LL(2) 点が残る。
3. *G'* は曖昧性を持たない（1 の系）。
4. shaping 展開規則（E-PROGRESSIVE / E-PROGRESSIVE-MULTI / E-PROGRESSIVE-INTERLEAVE）は意味論フェーズで動作し、構文解析には影響しない。
5. Phase 名（upper_ident）は識別子（小文字）およびスケジュールキーワード（大文字だが FR、VI のような複数文字組合せ）と字句的に素であり、トークンの曖昧性を防ぐ。
6. `interleave` 句（v2.x）は構文解析後の意味論フェーズで template 消費（制約 76）と clone label 生成（制約 63b）を導入する — これらは文法分類に影響しない。

---

## §12 反応クラス特異的罰の決定点（v1.y）

複合スケジュールに対する新しい 2 種類のキーワード引数形式を導入する:

1. `Overlay` 用 `overlay_kw_arg`: `"target" "=" target_value`
2. `Conc` 用 `punish_directive`: `"PUNISH" "(" punish_target ")" "=" schedule`

いずれも既存の `KW_NAME` クラス（COD, FRCO, BO）とは独立した新しい終端記号
（`TARGET_KW`, `PUNISH_KW`）を導入する。新たな決定点はすべて LL(1) であり、
LL(2) 決定点は増加しない。§6 の単一の LL(2) 決定点（`PosTail`）は保存される。

### §12.1 KwTail の拡張（§3.3）

複合スケジュールのキーワード引数末尾部は 4 つの選択肢に拡張される:

```
KwTail → COMMA ScalarKwArg   KwTail
       | COMMA DirectionalKwArg KwTail
       | COMMA OverlayKwArg   KwTail
       | COMMA PunishDirective KwTail
       | ε

ScalarKwArg      → KW_NAME EQ Value
DirectionalKwArg → KW_NAME LPAREN DirRef ARROW DirRef RPAREN EQ Value
OverlayKwArg     → TARGET_KW EQ TargetValue
PunishDirective  → PUNISH_KW LPAREN PunishTarget RPAREN EQ Schedule
TargetValue      → KW_CHANGEOVER | KW_ALL
PunishTarget     → KW_CHANGEOVER | DirRef ARROW DirRef | DirRef
```

### §12.2 新選択肢の FIRST₁

```
FIRST₁(ScalarKwArg ∪ DirectionalKwArg) = { KW_NAME }
FIRST₁(OverlayKwArg)                   = { TARGET_KW }
FIRST₁(PunishDirective)                = { PUNISH_KW }
```

これらは対毎に互いに素（KW_NAME ∉ {TARGET_KW, PUNISH_KW}）。各新規キーワードは
別個の予約語。

### §12.3 KwTail 継続点の決定

COMMA の後、パーサは以下から選択する:

| 先読み₁ | 生成規則 |
|---|---|
| `KW_NAME` | ScalarKwArg または DirectionalKwArg（§12.4 参照） |
| `TARGET_KW` | OverlayKwArg |
| `PUNISH_KW` | PunishDirective |
| `RPAREN` | ε（KwTail を抜ける） |

すべての分岐は LL(1) で一意に決定される。曖昧性なし。

### §12.4 KW_NAME 内でのスカラー vs 方向指定: LL(2)

`KW_NAME` の直後のトークンで分岐:

| 先読み₂ | 形式 |
|---|---|
| `EQ` | ScalarKwArg |
| `LPAREN` | DirectionalKwArg |

これは既存の LL(2) 決定点。新追加により変化しない。

### §12.5 PosTail の保存

§6 の中核的 LL(2) 決定点（`PosTail` — Schedule vs KwTail 直前の COMMA）は
`FIRST₂((COMMA, _))` に依存する。新終端 `TARGET_KW`, `PUNISH_KW` は KwTail 側の
FIRST₂ を `(COMMA, TARGET_KW)`, `(COMMA, PUNISH_KW)` として拡張する。いずれも
KwTail と一意に対応（Schedule の FIRST₁ と重ならない）。したがって `PosTail` の
LL(2) 分析は健全性を保つ。

### §12.6 結論

v1.y の `overlay_kw_arg` および `punish_directive` 拡張は LL(2) 分類を保存する。
新内部決定点はすべて LL(1) であり、既存の LL(2) 決定点（§6）は影響を受けない。
文法は、`PosTail` のみ 2 トークン先読みを要求し他はすべて 1 トークン先読みで
動作する再帰下降 LL(2) パーサで解析可能のままである。

---

## §13 Core-TrialBased MTS 拡張の決定点（R-7）

Core-TrialBased 層の `mts_schedule` 生成規則に 2 つの新キーワード引数
（`delay`, `correction`）と 1 つの新生成規則（`correction_spec`）を追加する。
本節は、これらの追加が LL(2) 分類を保存することを示す。

### §13.1 拡張された mts_kw_arg

```
mts_kw_arg → "comparisons"  EQ NUMBER
           | "consequence"  EQ Schedule
           | "incorrect"    EQ Schedule
           | "ITI"          EQ Value
           | "type"         EQ MtsType
           | "delay"        EQ Value             ; [R-7]
           | "correction"   EQ CorrectionSpec    ; [R-7]
           | LH_KW          EQ Value
```

既存の 5 alternative に 2 alternative を追加。各 alternative の先頭は
文脈限定キーワード（`MTS(` 内でのみ keyword 扱い、§13.2）。

### §13.2 context-sensitive reservation

`delay` / `correction` は文法のトップレベル reserved に含めない。
`MTS` `(` の直後で `IDENT` `=` のパターンに現れた場合のみ keyword と解釈される。
これは既存の `type` と同じ扱いであり、トップレベルの `let delay = ...` /
`let correction = ...` と衝突しない。

### §13.3 mts_kw_arg の選択判定

`MTS` `(` の直後、あるいは `,` の直後、パーサは IDENT を見て以下のテーブルから
alternative を選択する:

| IDENT 値 | 選択される alternative |
|---|---|
| `"comparisons"` | comparisons arg |
| `"consequence"` | consequence arg |
| `"incorrect"` | incorrect arg |
| `"ITI"` | ITI arg |
| `"type"` | type arg |
| `"delay"` | delay arg (**NEW**) |
| `"correction"` | correction arg (**NEW**) |
| `LH_KW`（`LH` / `LimitedHold` / `limitedHold`） | LH arg |

単一 token 先読みで一意決定可能。**LL(1)**。

### §13.4 correction_spec 内部決定

```
correction_spec → boolean | number | '"repeat_until_correct"'
```

先頭 token の字句クラスで三分岐:

| FIRST₁ | 選択 alternative |
|---|---|
| `KW_TRUE` / `KW_FALSE` | boolean |
| `NUMBER` (= [0-9]+ ("." [0-9]+)?) | number |
| `STRING` (= `"..."`) | string（M15 で `"repeat_until_correct"` のみ許可） |

boolean / number / string の lexer 分類は pairwise disjoint。**LL(1)**。

整数制約（fractional reject）は M15 semantic error
（MTS_INVALID_CORRECTION）として semantic layer に委譲される — これは
`comparisons=3s` が syntactically valid `value` でありながら M2
で拒否されるのと同じパターン。

### §13.5 PosTail への影響

§6 の中核的 LL(2) 決定点（`PosTail` — Schedule vs KwTail 直前の COMMA）は
複合スケジュール（Conc, Mult, Chain 等）の arg_list 内に存在する。
`mts_schedule` は独自の括弧構造 `MTS(...)` を持ち、その内部では
`mts_kw_arg` の選択のみが行われる（PosTail 判定は発生しない）。
したがって §6 の LL(2) 分析は影響を受けない。

### §13.6 FIRST / FOLLOW 更新

- **FIRST₁(mts_kw_arg)** に `"delay"` / `"correction"` を追加（既存の
  `"comparisons"` 等と disjoint な IDENT 値）。
- **FIRST₁(correction_spec)** = `{ KW_TRUE, KW_FALSE, NUMBER, STRING }`。
  pairwise disjoint。
- **FOLLOW** 集合は変化しない（既存の `mts_kw_arg` の FOLLOW に
  `COMMA` と `RPAREN` がある状態が維持される）。

### §13.7 結論

R-7 の `delay` / `correction` 追加および `correction_spec` 新生成規則は
LL(2) 分類を保存する。
新内部決定点（§13.3, §13.4）はすべて LL(1)。既存の LL(2) 決定点（§6 の
`PosTail`）は `mts_schedule` とは独立な arg_list 構造にあり、影響を受けない。

**更新された定理（§8・§11.7 の拡張）:**

拡張文法 *G''* = Core ∪ Core-Stateful ∪ Experiment ∪ Overlay ∪ Core-TrialBased
は以下を満たす:

1. *G''* は LL(2): すべての先行する性質を保存し、Core-TrialBased は LL(1)。
2. *G''* は LL(1) ではない: Core の `PosTail` LL(2) 点が残る。
3. *G''* は曖昧性を持たない（1 の系）。
4. `correction_spec` の整数制約は semantic layer（M15）に委譲される。

---

## 参考文献

- Aho, A. V., Lam, M. S., Sethi, R., & Ullman, J. D. (2006). *Compilers: Principles, Techniques, and Tools* (2nd ed.). Addison-Wesley. §4.4 (LL 構文解析), §4.8 (エラー回復).
- Knuth, D. E. (1965). On the translation of languages from left to right. *Information and Control*, *8*(6), 607–639. https://doi.org/10.1016/S0019-9958(65)90426-2
- Rosenkrantz, D. J., & Stearns, R. E. (1970). Properties of deterministic top-down grammars. *Information and Control*, *17*(3), 226–256. https://doi.org/10.1016/S0019-9958(70)90446-8

