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

## §2. Adjusting Schedule — `Adj`（計画中）

Blough, D. S. (1958). *JEAB*, *1*(1), 31–43.
Mazur, J. E. (1987). In Commons et al. (Eds.), *Quantitative analyses of behavior* (Vol. 5, pp. 55–73).

構文設計は未着手。`.local/planning/` の設計草案を参照。

## §3. Interlocking Schedule（計画中）

Ferster, C. B., & Skinner, B. F. (1957). *Schedules of reinforcement*.

構文設計は未着手。`.local/planning/` の設計草案を参照。
