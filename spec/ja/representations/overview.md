# 代替表現

> [contingency-dsl 理論文書](theory.md)の一部。形式仕様の詳細は [`representations/t-tau/README.md`](../../representations/t-tau/README.md) 参照。

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

3×3 格子と T-tau の関係は、**デカルト座標と極座標**の関係に類似する。同一の空間の2つの表現であり、それぞれ異なる性質を透明にする。

**変換定義域（部分写像）.** T-tau は Interval スケジュールと Time スケジュールをカバーするが、Ratio スケジュールは含まない。Ratio スケジュールは応答数の関数として強化を定義するが、この次元は応答率（従属変数）を仮定しなければ時間に変換できない。この境界は型レベルで強制される。

| 格子 | → T-tau | 備考 |
|------|---------|------|
| FI(t), FT(t) | TTau(T=t, τ=t) | FI/FT が縮退（応答要求の区別が消失） |
| VI(t), VT(t) | TTau(T=t, τ=t) | 分布形状が消失 |
| RI(t), RT(t) | TTau(T=t, τ=t) | 分布型が消失 |
| FR(n), VR(n), RR(n) | **型エラー** | 応答数 ∉ 時間領域 |

**逆変換** には明示的な曖昧性解消が必要: `domain`（Interval vs. Time）と `distribution`（Fixed, Variable, Random）を呼び出し側が提供しなければならない。T-tau はこれらの次元をエンコードしないためである。

**duty_cycle < 1.0 の場合（τ < T）.** サイクルより短い時間窓を持つ場合、Limited Hold（§1.6）に構造的に対応する。逆写像は `Schedule LH(τ)` を生成する。ただし、Schoenfeld & Cole は τ をサイクル開始時に配置するのに対し、Ferster-Skinner 伝統の LH は基準充足後に窓を開くため、この位置的差異により厳密な等価ではなく構造的近似である。

**LH との関係.** §1.6 で述べた通り、T-tau と LH は本質的に異なる: T-tau はクロック駆動の周期的サイクル、LH はイベントトリガー型。`duty_cycle = 1.0` の T-tau には LH の対応物はない。

**Ratio スケジュールの近似変換.** 分離レイヤーとして、明示的な IRT（inter-response time）仮定を受け取り近似的な T-tau 座標を生成する関数を提供する。結果は `TTauApprox` 型（`TTauParams` とは別型）として型付けされ、定義と遂行データの暗黙的混同を防止する。

完全な形式仕様と適合テストは `representations/t-tau/README.md` を参照。

**参考文献:**
- Schoenfeld, W. N., & Cole, B. K. (1972). *Stimulus schedules: The t-τ systems*. Harper & Row.
- Schoenfeld, W. N., & Cole, B. K. (1975). What is a "schedule of reinforcement"? *Pavlovian Journal of Biological Science*, 10(1), 5–13. https://doi.org/10.1007/BF03000622
