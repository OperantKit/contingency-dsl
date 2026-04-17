# 代替表現

> [contingency-dsl 理論文書](../operant/theory.md)の一部。形式仕様の詳細は [`t-tau.md`](t-tau.md) を参照。

---

## 1. T-tau 座標系

3×3 格子（Distribution × Domain）は強化スケジュール空間の唯一の形式化ではない。Schoenfeld & Cole (1972) は **T-tau 体系** を提案した。これは時間ベースのパラメタ化であり、スケジュールを周期的サイクルとして表現する。

**定義.** T-tau 表現は時間依存スケジュールを以下のようにパラメタ化する:

```
TTauParams := (T: ℝ⁺, τ: ℝ⁺)  ただし  0 < τ ≤ T
duty_cycle := τ / T  ∈ (0, 1]
```

- **T** — サイクル全体の長さ（秒）。
- **τ** — 各サイクル内の強化可能時間窓（秒）。
- **duty_cycle** — 強化密度の基本パラメータ。

3×3 格子と T-tau の関係は、**デカルト座標と極座標**の関係に類似する。同一空間の 2 つの表現であり、それぞれ異なる性質を透明にする。

### 1.1 変換定義域（部分写像）

T-tau は Interval スケジュールと Time スケジュールをカバーするが、Ratio スケジュールは含まない。Ratio スケジュールは応答数の関数として強化を定義するが、この次元は応答率（生体の振る舞い、すなわち従属変数）を仮定しなければ時間に変換できない。応答率はスケジュールのパラメータではない。この境界は型レベルで強制される。

| 格子 | → T-tau | 備考 |
|------|---------|------|
| FI(t), FT(t) | TTau(T=t, τ=t) | FI/FT が縮退（応答要求の区別が消失） |
| VI(t), VT(t) | TTau(T=t, τ=t) | 分布形状が消失 |
| RI(t), RT(t) | TTau(T=t, τ=t) | 分布型が消失 |
| FR(n), VR(n), RR(n) | **型エラー** | 応答数 ∉ 時間領域 |

### 1.2 逆変換と曖昧性解消

逆変換には明示的な曖昧性解消が必要である。呼び出し側は `domain`（Interval vs. Time）と `distribution`（Fixed, Variable, Random）を提供しなければならない。T-tau はこれらの次元をエンコードしないためである。

### 1.3 duty_cycle < 1.0 の場合（τ < T）

サイクルより短い時間窓を持つ場合、Limited Hold（[operant/theory.md §1.6](../operant/theory.md)）に構造的に対応する。逆写像は `Schedule LH τ` を生成する。ただし、Schoenfeld & Cole は τ をサイクル開始時に配置するのに対し、Ferster-Skinner 伝統の LH は基準充足後に窓を開くため、この位置的差異により厳密な等価ではなく構造的近似である。

### 1.4 LH との関係

表面的な類似にもかかわらず、T-tau と LH は本質的に異なる（[operant/theory.md §1.6](../operant/theory.md) 参照）。T-tau はクロック駆動で周期的なサイクル、LH はイベントトリガー型の窓である。`duty_cycle = 1.0` の T-tau には LH の対応物はない — サイクル全体が利用可能だからである。

### 1.5 Ratio スケジュールの近似変換

分離レイヤーとして、明示的な IRT（inter-response time）仮定を受け取り近似的な T-tau 座標を生成する関数を提供する。結果は `TTauApprox` 型（`TTauParams` とは別型）として型付けされ、定義と遂行データの暗黙的混同を防止する。

### 1.6 寄与: 文献横断の手続き比較

T-tau パラメタ化された手続きを 3×3 格子に変換することで、研究者は異なる記法の下で過去の実験が手続き的に類似したスケジュールを使用していたかを同定できる。逆に、格子で定義されたスケジュールを T-tau 座標に表現することで duty-cycle ベースの分析が可能になる。この双方向写像は、従来は手作業で誤りやすかった文献横断比較を体系化する。

---

## 参考文献

- Schoenfeld, W. N., & Cole, B. K. (1972). *Stimulus schedules: The t-τ systems*. Harper & Row.
- Schoenfeld, W. N., & Cole, B. K. (1975). What is a "schedule of reinforcement"? *Pavlovian Journal of Biological Science*, 10(1), 5–13. https://doi.org/10.1007/BF03000622
