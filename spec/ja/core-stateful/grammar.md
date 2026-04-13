# Core-Stateful 文法

> contingency-dsl 仕様の一部。Core-Stateful 層の文法生成規則を記述する。
>
> 正式な EBNF は [schema/core-stateful/grammar.ebnf](../../../schema/core-stateful/grammar.ebnf) を参照。
> アーキテクチャ上の位置付けは [design-philosophy.md §2.1](../design-philosophy.md) を参照。

---

## 概要

Core-Stateful スケジュールは Core 文法の `modifier` 生成規則に統合される:

```ebnf
modifier ::= dr_mod | pr_mod | repeat | lag_mod
           | pctl_mod                    -- Core-Stateful
```

全 Core-Stateful 生成規則は Core と同じ CFG 構造に従う。
差異は意味論のみ: Core-Stateful の基準はランタイム状態から算出される。

---

## §1. Percentile Schedule — `Pctl`

Platt, J. R. (1973). Percentile reinforcement. In G. H. Bower (Ed.),
*The psychology of learning and motivation* (Vol. 7, pp. 271–296).

Galbicka, G. (1994). Shaping in the 21st century. *JABA*, *27*(4), 739–760.
https://doi.org/10.1901/jaba.1994.27-739

### 構文

```
Pctl(IRT, 50)                            -- 最小形
Pctl(IRT, 25, window=30)                 -- window 指定
Pctl(latency, 75, window=50, dir=above)  -- 全パラメータ指定
```

### パラメータ

| パラメータ | 位置 | 型 | 必須 | デフォルト | 説明 |
|---|---|---|---|---|---|
| `target` | positional 1 | 列挙型 | ✅ | — | 反応次元: `IRT`, `latency`, `duration`, `force`, `rate` |
| `rank` | positional 2 | 整数 0–100 | ✅ | — | 百分位閾値 |
| `window` | keyword | 正整数 | — | 20 | 分布算出に使用する直近反応数 |
| `dir` | keyword | 列挙型 | — | `"below"` | 強化方向: `"below"` or `"above"` |

### 意味論

R = [r_{n-m+1}, ..., r_n] を target 次元の直近 m 反応の値とする。
p_k = percentile(R, rank) とする。

```
dir=below:  reinforce(r_{n+1}) ⟺ r_{n+1} ≤ p_k
dir=above:  reinforce(r_{n+1}) ⟺ r_{n+1} ≥ p_k
```

**初期状態:** window 分の反応が蓄積されるまで全反応を強化（CRF 相当）。
Platt (1973) の原典手続きに準拠。

### DRL/DRH との関係

Percentile は DRL/DRH の一般化（動的閾値 vs 固定閾値）。両者は文法に併存する:

- `DRL 5s` — 固定基準、Core（静的、等価性判定可能）
- `Pctl(IRT, 50)` — 動的基準、Core-Stateful（等価性はランタイム依存）

### 意味論的制約

| コード | 条件 | 深刻度 |
|---|---|---|
| `PCTL_INVALID_RANK` | rank が [0, 100] の整数でない | SemanticError |
| `PCTL_INVALID_WINDOW` | window ≤ 0 or 非整数 | SemanticError |
| `PCTL_UNKNOWN_TARGET` | target が列挙値にない | SemanticError |
| `PCTL_INVALID_DIR` | dir が `"below"` / `"above"` でない | SemanticError |
| `PCTL_UNEXPECTED_TIME_UNIT` | rank に時間単位が付いている | SemanticError |
| `DUPLICATE_PCTL_KW_ARG` | keyword 引数の重複 | SemanticError |
| `PCTL_EXTREME_RANK` | rank == 0 or 100 | WARNING |
| `PCTL_SMALL_WINDOW` | window < 5 | WARNING |
| `PCTL_LARGE_WINDOW` | window > 100 | WARNING |

---

## §2. Adjusting Schedule — `Adj`

Blough, D. S. (1958). A method for obtaining psychophysical thresholds
from the pigeon. *JEAB*, *1*(1), 31–43. https://doi.org/10.1901/jeab.1958.1-31

Mazur, J. E. (1987). An adjusting procedure for studying delayed
reinforcement. In M. L. Commons et al. (Eds.), *Quantitative analyses
of behavior* (Vol. 5, pp. 55–73). Erlbaum.

Richards, J. B., Mitchell, S. H., de Wit, H., & Seiden, L. S. (1997).
Determination of discount functions in rats with an adjusting-amount
procedure. *JEAB*, *67*(3), 353–366. https://doi.org/10.1901/jeab.1997.67-353

### 構文

```
Adj(delay, start=10s, step=1s)                     -- 最小形
Adj(delay, start=10s, step=2s, min=0s, max=120s)   -- 境界値付き
Adj(ratio, start=5, step=2)                        -- adjusting-ratio
Adj(amount, start=3, step=1, min=1, max=10)        -- adjusting-amount
Adjusting(delay, start=10s, step=1s)               -- 冗長形
```

### パラメータ

| パラメータ | 位置 | 型 | 必須 | デフォルト | 説明 |
|---|---|---|---|---|---|
| `target` | positional 1 | 列挙型 | ✅ | — | 調整対象: `delay`, `ratio`, `amount` |
| `start` | keyword | 値 | ✅ | — | 初期パラメータ値 |
| `step` | keyword | 値 | ✅ | — | 1 ステップの調整量（加算的） |
| `min` | keyword | 値 | — | なし | 下限値 |
| `max` | keyword | 値 | — | なし | 上限値 |

### 調整対象の次元

| Target | 調整対象 | 次元 | 暗黙の基本随伴性 | 典拠 |
|---|---|---|---|---|
| `delay` | 強化遅延 | 時間（単位必須） | CRF + 調整される遅延 | Mazur (1987) |
| `ratio` | 反応比率要件 | 無次元（整数） | Adjusting FR | Ferster & Skinner (1957) |
| `amount` | 強化子の量 | 無次元（ランタイム解釈） | CRF + 調整される量 | Richards et al. (1997) |

### 意味論

```
P(t): 試行 t における調整パラメータ値
P(0) = start

各強化（またはブロック完了）後:
  「増加」基準充足:  P(t+1) = clamp(P(t) + step, min, max)
  「減少」基準充足:  P(t+1) = clamp(P(t) - step, min, max)
  それ以外:          P(t+1) = P(t)
```

増加/減少の方向決定規則は**ランタイムに委譲**される。
DSL はパラメータ構造を宣言し、調整アルゴリズム（例: Mazur の 4 試行
ブロック多数決）はランタイムの実装詳細とする。VI の値生成における
`@algorithm("fleshler-hoffman")` と同じ方針。

### 統合ポイント

Adj は `base_schedule` を拡張する（`modifier` ではない）。
強化基準を修飾するのではなく、独立した随伴性構造を定義するため。
Pctl が `modifier` を拡張するのとは異なる。

```ebnf
base_schedule ::= ... | adj_schedule
```

### PR との関係

| | PR(linear, start=1, increment=5) | Adj(ratio, start=5, step=2) |
|---|---|---|
| 変化方向 | 単調増加のみ | 双方向（行動依存） |
| 変化規則 | 決定論的（毎回固定量増加） | 行動依存（直前の遂行に基づく） |
| 収束 | なし（breakpoint まで増加） | あり（無差別点に収束） |
| 層 | Core（非 TC） | Core-Stateful（ランタイム状態依存） |

### 意味論的制約

| コード | 条件 | 深刻度 |
|---|---|---|
| `MISSING_ADJ_PARAM` | `start` または `step` 未指定 | SemanticError |
| `ADJ_UNKNOWN_TARGET` | target が列挙値にない | SemanticError |
| `ADJ_NONPOSITIVE_START` | start ≤ 0 | SemanticError |
| `ADJ_NONPOSITIVE_STEP` | step ≤ 0 | SemanticError |
| `ADJ_TIME_UNIT_REQUIRED` | `delay` target で時間単位なし | SemanticError |
| `ADJ_UNEXPECTED_TIME_UNIT` | `ratio`/`amount` target で時間単位あり | SemanticError |
| `ADJ_INVALID_BOUNDS` | min ≥ max | SemanticError |
| `ADJ_START_OUT_OF_BOUNDS` | start が [min, max] の範囲外 | SemanticError |
| `ADJ_RATIO_NOT_INTEGER` | `ratio` target で非整数値 | SemanticError |
| `DUPLICATE_ADJ_KW_ARG` | keyword 引数の重複 | SemanticError |
| `ADJ_UNBOUNDED_DELAY` | `delay` target で `max` 未指定 | WARNING |
| `ADJ_LARGE_STEP` | step > start | WARNING |
| `ADJ_ZERO_MIN_DELAY` | `delay` target で min=0 | WARNING |
| `ADJ_SUBUNIT_RATIO` | `ratio` target で min < 1 | WARNING |

---

## §3. Interlocking Schedule — `Interlock`

Ferster, C. B., & Skinner, B. F. (1957). *Schedules of reinforcement*.
Appleton-Century-Crofts.

Berryman, R., & Nevin, J. A. (1962). Interlocking schedules of
reinforcement. *JEAB*, *5*(2), 213–223.
https://doi.org/10.1901/jeab.1962.5-213

Powers, R. B. (1968). Clock-delivered reinforcers in conjunctive and
interlocking schedules. *JEAB*, *11*(5), 579–586.
https://doi.org/10.1901/jeab.1968.11-579

### 構文

```
Interlock(R0=300, T=10min)       -- F&S 1957 原典例
Interlock(R0=16, T=80s)          -- Powers (1968) 条件
Interlocking(R0=250, T=5min)     -- 冗長形
```

### パラメータ

| パラメータ | 位置 | 型 | 必須 | デフォルト | 説明 |
|---|---|---|---|---|---|
| `R0` | keyword | 正整数 | ✅ | — | 初期比率要件（強化直後の要求反応数） |
| `T` | keyword | 時間値 | ✅ | — | 時間窓。経過時間 = T で比率要件が 1（CRF）に達する |

### 意味論

比率要件と間隔要件が連動し、強化後の経過時間に応じて比率要件が
線形に減少する。

```
R(t) = max(1, ⌈R0 × (1 − t/T)⌉)

t = 0:   R(0) = R0  （最大比率）
t = T:   R(T) = 1   （CRF — 最初の 1 反応で強化）
強化時:  t₀ ← 現在時刻（リセット）
```

行動的含意:
- 高速反応 → 高い比率要件に直面（時間が少ししか経過していない）
- 低速反応 → 低い比率要件で強化（時間が経過している）
- 無反応で T 経過 → 最初の 1 反応で強化（CRF 相当）
- 各強化でリセット（非累積的）

### 統合ポイント

Adj と同様に `base_schedule` を拡張する:

```ebnf
base_schedule ::= ... | interlock_schedule
```

### Conjunctive / Alternative との関係

| スケジュール | 強化論理 | パラメータの性質 |
|---|---|---|
| Conjunctive | AND（両要件充足） | 固定 |
| Alternative | OR（いずれか充足） | 固定 |
| **Interlocking** | **連動**（一方が他方を修飾） | **時間関数で変動、強化でリセット** |

### Core-Stateful 内の分類

Interlocking は Core-Stateful で唯一の**決定論的**スケジュール。
Pctl と Adj は被験体の行動に適応するが、Interlocking の基準は
経過時間のみの関数であり、行動とは独立に変化する。

| ランタイム状態 | スケジュール | 性質 |
|---|---|---|
| 反応履歴（直近 m 反応の分布） | Pctl | 適応的 |
| 試行結果（直前の遂行） | Adj | 適応的 |
| **経過時間（連続関数）** | **Interlock** | **決定論的** |

### 命名衝突の解決

DSL における "Interlocking" は Ferster & Skinner (1957) のスケジュールを指す。
Glenn (2004) の "Interlocking Behavioral Contingencies"（メタ随伴性理論）は
衝突回避のためアノテーション `@ibc` を使用する。

### 意味論的制約

| コード | 条件 | 深刻度 |
|---|---|---|
| `MISSING_INTERLOCK_PARAM` | `R0` または `T` 未指定 | SemanticError |
| `INTERLOCK_INVALID_R0` | R0 ≤ 0 or 非整数 | SemanticError |
| `INTERLOCK_UNEXPECTED_TIME_UNIT` | R0 に時間単位が付いている | SemanticError |
| `INTERLOCK_NONPOSITIVE_T` | T ≤ 0 | SemanticError |
| `INTERLOCK_TIME_UNIT_REQUIRED` | T に時間単位なし | SemanticError |
| `DUPLICATE_INTERLOCK_KW_ARG` | keyword 引数の重複 | SemanticError |
| `INTERLOCK_TRIVIAL_RATIO` | R0 == 1（実質 FT） | WARNING |
| `INTERLOCK_LARGE_RATIO` | R0 > 500 | WARNING |
