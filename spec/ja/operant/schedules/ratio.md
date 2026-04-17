# 比率スケジュール — FR, VR, RR

> contingency-dsl オペラント層の一部。パラメータが反応数を指定する、反応ベースの強化スケジュール。

---

## 1. スコープ

比率スケジュールは、3×3 アトミック分類（`operant/theory.md §1.1`）の Ratio 列を成す。パラメータ `n` は強化に要する反応数を指定する。強化は反応依存・時間非依存である。

| スケジュール | Distribution | 意味論 | 標準参照 |
|---|---|---|---|
| **FR(n)** | Fixed | ちょうど `n` 反応ごとに強化子 | Ferster & Skinner (1957, 第 3 章) |
| **VR(n)** | Variable | 平均 `n` の Fleshler-Hoffman (1962) 非復元系列 | Ferster & Skinner (1957, 第 4 章) |
| **RR(n)** | Random | 反応ごとの平均 `n` の幾何的ドロー | Farmer (1963) |

## 2. 操作的定義

### 2.1 FR — 固定比率

`n` 番目の反応ごとに強化子が呈示される。パラメータは整数 `n ≥ 1`。

```
FR 5        -- 5 反応ごとに強化
FR 1 ≡ CRF  -- 連続強化（比率次元の同一元）
```

表示: `⟦Atomic(Fixed, Ratio, n)⟧`（`operant/theory.md §2.13.3` 参照）。

### 2.2 VR — 変動比率

平均が `n` に等しい可変反応数の後に強化子が呈示される。可変値は Fleshler-Hoffman (1962) 非復元系列からドローされ、以下を保証する。

- ドロー値の平均 = `n`
- 系列の単一通過内で値の重複なし
- 系列にわたる反応ごとの強化確率が一定

```
VR 20       -- 強化子あたり平均 20 反応
```

Fleshler-Hoffman 系列は Fleshler & Hoffman (1962) で規定される疑似乱数生成器である。生成器の設定については `procedure-annotator/temporal` の `@algorithm("fleshler-hoffman")` を参照。

### 2.3 RR — 無作為比率

反応ごとの強化確率が `1/n` であり、平均 `n` の幾何的な強化間反応数分布をもたらす。VR とは異なり、RR は各反応で独立にサンプルする（無記憶）。

```
RR 20       -- 各反応が確率 1/20 で強化される
```

表示: `⟦Atomic(Random, Ratio, n)⟧` は反応ごとの幾何的ドローを用いる。

## 3. VR vs RR — 決定的な区別

VR と RR は文献ではしばしば混同されるが、構造的に異なる。

| 性質 | VR | RR |
|---|---|---|
| サンプリング | 制約付き系列からの非復元 | 復元付き（無記憶） |
| 平均の保証 | 系列上での平均 = `n`（厳密） | 期待される平均 = `n`（大数の法則） |
| 典型的な行動 | 強化後休止を伴う高い定常反応率 | 特徴的休止を伴わない高い定常反応率 |
| 参照 | Fleshler & Hoffman (1962); Ferster & Skinner (1957) | Farmer (1963) |

DSL は型レベルで両者を区別する: `Distribution ∈ {Fixed, Variable, Random}`。

## 4. 強化後休止

比率スケジュールは、比率サイズに比例した特徴的な強化後休止を生成する（Ferster & Skinner, 1957, 第 3〜4 章）。休止は行動的帰結であり、DSL のパラメータではない。DSL はスケジュール構造のみを記録し、休止予測は解析層に属する。

## 5. 比率スケジュールを含む合成

比率スケジュールは `operant/schedules/compound.md` のコンビネータと自由に合成可能である。

```
Conc(FR 10, VR 20)                          -- 並行比率; compound.md §3 参照
Chain(FR 5, FI 30-s)                        -- FR の後に時隔（compound.md 参照）
Tand(VR 20, DRL 5-s)                        -- IRT 制約付きタンデム
```

**並行 VR-VR vs 並行 VI-VI の区別**（排他的選択 vs マッチング）は行動的帰結であり、DSL のパラメータではない。`operant/theory.md §2.6` を参照。

## 6. 2 次比率スケジュール

`FR n(Unit)` は、全体比率と内部単位スケジュールを合成する（Kelleher, 1966; Kelleher & Fry, 1962）。

```
FR 5(FI 30-s)       -- FI 30-s の単位完了 5 回で強化
```

比率ベースの 2 次スケジュールは、（短時間刺激が無い場合には）`n` 個の単位コピーのタンデムに等価である: `FR n(S) ≡ Repeat(n, S)`。`operant/theory.md §2.11.1` を参照。

## 7. エラーと警告

| コード | 条件 | 重大度 |
|---|---|---|
| `ATOMIC_NONPOSITIVE_VALUE` | `n ≤ 0` | SemanticError |
| `ATOMIC_RATIO_NON_INTEGER` | `n` が整数値でない | SemanticError |
| `ATOMIC_UNEXPECTED_TIME_UNIT` | 比率スケジュールに時間単位が伴う | SemanticError |

完全なレジストリは `conformance/operant/errors.json` を参照。

## 8. 設計上の決定

3×3 アトミック格子は Distribution と Domain を直交として扱う。積型による形式化は `operant/theory.md §1.1–§1.3` を参照。VR と RR の分離の根拠については `docs/en/design-rationale.md` を参照。

## 参考文献

- Farmer, J. (1963). Properties of behavior under random interval reinforcement schedules. *Journal of the Experimental Analysis of Behavior*, 6(4), 607–616. https://doi.org/10.1901/jeab.1963.6-607
- Ferster, C. B., & Skinner, B. F. (1957). *Schedules of reinforcement*. Appleton-Century-Crofts.
- Fleshler, M., & Hoffman, H. S. (1962). A progression for generating variable-interval schedules. *Journal of the Experimental Analysis of Behavior*, 5(4), 529–530. https://doi.org/10.1901/jeab.1962.5-529
- Kelleher, R. T. (1966). Conditioned reinforcement in second-order schedules. *Journal of the Experimental Analysis of Behavior*, 9(5), 475–485. https://doi.org/10.1901/jeab.1966.9-475
- Kelleher, R. T., & Fry, W. (1962). Stimulus functions in chained fixed-interval schedules. *Journal of the Experimental Analysis of Behavior*, 5(2), 167–173. https://doi.org/10.1901/jeab.1962.5-167
- Schoenfeld, W. N., & Cole, B. K. (1972). *Stimulus schedules: The t-τ systems*. Harper & Row.
