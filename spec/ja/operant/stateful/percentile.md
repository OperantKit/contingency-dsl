# Percentile スケジュール — `Pctl`

> contingency-dsl Operant.Stateful 下位層の一部。基準 = f(反応履歴)。反応履歴依存の分化強化。

---

## 1. 起源

- Platt, J. R. (1973). Percentile reinforcement. In G. H. Bower (Ed.), *The psychology of learning and motivation* (Vol. 7, pp. 271–296).
- Galbicka, G. (1994). Shaping in the 21st century: Moving percentile schedules into applied settings. *Journal of Applied Behavior Analysis*, 27(4), 739–760. https://doi.org/10.1901/jaba.1994.27-739

Percentile は DRL/DRH の一般化であり、固定閾値ではなく **動的（適応的）** 閾値を持つ。時刻 `t+1` の基準は、反応次元（IRT, latency, duration, force, rate）の最近値の分布から計算される。

## 2. 承認ゲート

`Pctl` は `spec/en/design-philosophy.md §2.1` の学問的確立基準（N1/N2/N3、証拠 E1〜E5）の下で Operant.Stateful に資格を有する。このスケジュールは命名されており、一次文献（Platt, 1973; Galbicka, 1994）を持ち、時間的持続性（50 年以上）を示し、JEAB/JABA 誌への掲載、研究室間再現、教科書掲載を有する。すべてのパラメータは宣言的である。

## 3. 構文

```
Pctl(IRT, 50)                            -- 最小形
Pctl(IRT, 25, window=30)                 -- 窓指定あり
Pctl(latency, 75, window=50, dir=above)  -- 完全指定
```

## 4. パラメータ

| パラメータ | 位置 | 型 | 必須 | デフォルト | 説明 |
|---|---|---|---|---|---|
| `target` | 位置 1 | enum | YES | — | 反応次元: `IRT`, `latency`, `duration`, `force`, `rate` |
| `rank` | 位置 2 | 整数 0〜100 | YES | — | percentile 閾値 |
| `window` | キーワード | 正整数 | NO | 20 | 分布に用いる直近反応数 |
| `dir` | キーワード | enum | NO | `"below"` | 強化方向: `"below"` または `"above"` |

## 5. 意味論

`R = [r_{n-m+1}, ..., r_n]` を target 次元の直近 `m` 個の値とする（`m = window`）。`p_k = percentile(R, rank)` とする。

```
dir=below:  reinforce(r_{n+1}) ⟺ r_{n+1} ≤ p_k
dir=above:  reinforce(r_{n+1}) ⟺ r_{n+1} ≥ p_k
```

**初期状態.** `window` 回の反応が発せられるまで、すべての反応は強化される（CRF 等価）。これは Platt (1973) に従う。

## 6. DRL / DRH との関係

Percentile は DRL/DRH の動的閾値への一般化である。両者ともに文法中に残される。

- `DRL 5-s` — 固定基準、Operant.Literal（静的、決定可能な等価性）— `operant/schedules/differential.md` を参照。
- `Pctl(IRT, 50)` — 動的基準、Operant.Stateful（ランタイム依存の等価性）。

## 7. 統合点

`Pctl` は、オペラント文法の `modifier` 産出規則を拡張する（`operant/grammar.md §1.3` 参照）。修飾子が許容されるどの場所にも現れうる — 単独、または `Tand` や `Conj` を介した格子スケジュールとの合成。

## 8. 意味制約

| コード | 条件 | 重大度 |
|---|---|---|
| `PCTL_INVALID_RANK` | `rank` が `[0, 100]` の整数でない | SemanticError |
| `PCTL_INVALID_WINDOW` | `window ≤ 0` または非整数 | SemanticError |
| `PCTL_UNKNOWN_TARGET` | `target` が列挙にない | SemanticError |
| `PCTL_INVALID_DIR` | `dir` が `"below"` または `"above"` でない | SemanticError |
| `PCTL_UNEXPECTED_TIME_UNIT` | `rank` が時間単位を伴う | SemanticError |
| `DUPLICATE_PCTL_KW_ARG` | キーワード引数の重複 | SemanticError |
| `PCTL_EXTREME_RANK` | `rank == 0` または `rank == 100` | WARNING |
| `PCTL_SMALL_WINDOW` | `window < 5` | WARNING |
| `PCTL_LARGE_WINDOW` | `window > 100` | WARNING |

## 9. 応用的使用

シェイピング・プリミティブの `method=percentile` 形式（`operant/grammar.md §3.8.4`）は、`Pctl(...)` と安定性基準の組み合わせへと脱糖衣される。Galbicka (1994) は、研究者が被験体の現在の反応分布への自動的な適応を望み、手動で固定閾値を調整することを避けたい場合の、臨床的シェイピングへの応用を記述している。

## 参考文献

§1 を参照。追加の背景:
- Alleman, H. D., & Platt, J. R. (1973). Differential reinforcement of interresponse times with controlled probability of reinforcement per response. *Learning and Motivation*, 4(1), 40–73. https://doi.org/10.1016/0023-9690(73)90036-2
