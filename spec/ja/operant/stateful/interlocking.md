# Interlocking スケジュール — `Interlock`

> contingency-dsl Operant.Stateful 下位層の一部。基準 = f(経過時間, 連続)。唯一の **決定論的** な Operant.Stateful スケジュール: 基準は経過時間の連続関数であり、被験体の行動には依存しない。

---

## 1. 起源

- Ferster, C. B., & Skinner, B. F. (1957). *Schedules of reinforcement*. Appleton-Century-Crofts.
- Berryman, R., & Nevin, J. A. (1962). Interlocking schedules of reinforcement. *Journal of the Experimental Analysis of Behavior*, 5(2), 213–223. https://doi.org/10.1901/jeab.1962.5-213
- Powers, R. B. (1968). Clock-delivered reinforcers in conjunctive and interlocking schedules. *Journal of the Experimental Analysis of Behavior*, 11(5), 579–586. https://doi.org/10.1901/jeab.1968.11-579

## 2. 承認ゲート

`Interlock` は `spec/en/design-philosophy.md §2.1` の下で Operant.Stateful に資格を有する。Ferster & Skinner (1957) の原形式化に Berryman & Nevin (1962) と Powers (1968) による再現が加わり、N1/N2/N3 を満たし、複数の証拠軸（E1 JEAB 掲載、E2 研究室間再現、E4 パラメトリック研究）を満たす。

## 3. 構文

```
Interlock(R0=300, T=10min)       -- Ferster & Skinner (1957) 原例
Interlock(R0=16, T=80s)          -- Powers (1968) 条件
Interlocking(R0=250, T=5min)     -- 冗長なエイリアス
```

## 4. パラメータ

| パラメータ | 位置 | 型 | 必須 | デフォルト | 説明 |
|---|---|---|---|---|---|
| `R0` | キーワード | 正整数 | YES | — | 初期比率要件（強化後） |
| `T` | キーワード | 時間値 | YES | — | 時間窓。`t = T` で比率要件が 1（CRF）に到達 |

## 5. 意味論

比率要件と時隔要件が連動する: 最後の強化からの経過時間とともに、比率要件は **線形に減少** する。

```
R(t) = max(1, ⌈R0 × (1 − t/T)⌉)

t = 0 で:  R(0) = R0   （最大比率）
t = T で:  R(T) = 1    （CRF — 最初の反応が強化される）
強化時:    t₀ ← current_time にリセット
```

行動的含意:

- 速い反応 → 高い比率要件（経過時間がわずか）
- 遅い反応 → 低い比率要件（経過時間が大きい）
- `T` の間に反応なし → 最初の反応が強化される（CRF 等価）
- 各強化時にクロックがリセット（非累積）

## 6. 統合点

`Adj` と同様に、`Interlock` は独立したスケジュール式として `base_schedule` を拡張する。

```ebnf
base_schedule ::= ... | interlock_schedule
```

## 7. Conjunctive / Alternative との関係

| スケジュール | 強化論理 | パラメータの性質 |
|---|---|---|
| Conjunctive | AND（両方の要件を満たす） | 固定 |
| Alternative | OR（どちらかの要件を満たす） | 固定 |
| **Interlocking** | **連動**（一方が他方を修飾する） | **時間関数、強化でリセット** |

## 8. Operant.Stateful 分類

`Interlock` は唯一の **決定論的** Operant.Stateful スケジュールである。`Pctl` と `Adj` は被験体の行動に適応するのに対し、`Interlock` の基準は行動から独立に、経過時間の連続関数のみで与えられる。

| ランタイム状態 | スケジュール | 性質 |
|---|---|---|
| 反応履歴（直近分布） | `Pctl` | 適応的 |
| 試行結果（直近パフォーマンス） | `Adj` | 適応的 |
| **経過時間（連続関数）** | **`Interlock`** | **決定論的** |

この分類は構造的に重要である。`Interlock` の決定性ゆえに、SEI 性質 P1〜P3（`architecture.md §4.1.1`）に反せず Operant.Stateful 下位層に置くことができる。基準規則は解析時に固定されており、現在の閾値のみが時間の決定論的関数として変化する。

## 9. 命名衝突の解決

DSL において「Interlocking」は Ferster & Skinner (1957) のスケジュールを指す。Glenn (2004) の「Interlocking Behavioral Contingencies」（メタ随伴性理論）は衝突を避けるため注釈 `@ibc` を使用する。`@ibc` 注釈は `annotations/extensions/social-annotator` に属する。

## 10. 意味制約

| コード | 条件 | 重大度 |
|---|---|---|
| `MISSING_INTERLOCK_PARAM` | `R0` または `T` が省略されている | SemanticError |
| `INTERLOCK_INVALID_R0` | `R0 ≤ 0` または非整数 | SemanticError |
| `INTERLOCK_UNEXPECTED_TIME_UNIT` | `R0` が時間単位を伴う | SemanticError |
| `INTERLOCK_NONPOSITIVE_T` | `T ≤ 0` | SemanticError |
| `INTERLOCK_TIME_UNIT_REQUIRED` | 時間単位を伴わない `T` | SemanticError |
| `DUPLICATE_INTERLOCK_KW_ARG` | キーワード引数の重複 | SemanticError |
| `INTERLOCK_TRIVIAL_RATIO` | `R0 == 1`（実質的に FT） | WARNING |
| `INTERLOCK_LARGE_RATIO` | `R0 > 500` | WARNING |

## 参考文献

一次ソースは §1 を参照。
