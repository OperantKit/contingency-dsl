# 論文記載例

> JEAB 論文の Method セクションを contingency-dsl で完全に翻訳した例。
> 実際の実験が多フェーズ DSL プログラムにどう対応するかを示す。
> 構文の詳細は [syntax-guide.md](syntax-guide.md)、個別構文の例は [use-cases.md](use-cases.md) を参照。

> **用語ノート: 被験体 vs 有機体** — 本文書では以下の使い分けに従う。
> - **被験体**（subject）: 手続き・実験計画の記述（例:「被験体は左レバーで反応した」）
> - **有機体**（organism）: 行動原理・理論的記述（例:「有機体が多段階の随伴性をどう学習するかを研究できない」）

---

## 1. リサージェンス: ABA デザイン

**論文:** Brown, T. L., Greer, B. D., Craig, A. R., Roane, H. S., & Shahan, T. A. (2020). Resurgence following differential reinforcement of alternative behavior implemented with and without extinction. *JEAB*, *113*(2), 449-467. https://doi.org/10.1002/jeab.590

**デザイン:** 3 フェーズの ABA リサージェンスデザイン。ベースラインで並立スケジュール上の標的反応を確立し、DRA で代替強化源を導入し、消去で全ての強化を停止して標的反応のリサージェンスを検証する。

**示される DSL 機能:** `phase`, `sessions`, `Conc`, プログラムレベル annotation

### 多フェーズファイル

```
-- Brown, Greer, Craig et al. (2020) JEAB 113(2), 449-467
-- Resurgence following DRA with and without extinction
-- Group: DRA Without Extinction

@species("rat") @strain("Long-Evans") @n(5)
@deprivation("80% free-feeding weight")
@chamber("Med-Associates", dimensions="30x24x21cm")
@reinforcer("food", type="pellet", magnitude="45mg", duration=3s)

phase Baseline:
  sessions = 25

  Conc(
    VI 60-s @operandum("left-lever") @sd("stimulus-light"),
    EXT     @operandum("right-lever")
  )

phase DRA:
  sessions = 14

  Conc(
    VI 60-s @operandum("target-lever") @sd("stimulus-light"),
    VI 15-s @operandum("nose-poke") @sd("yellow-LED"),
    COD=3-s
  )

phase ExtinctionTest:
  sessions = 5

  Conc(
    EXT @operandum("target-lever") @sd("stimulus-light"),
    EXT @operandum("nose-poke") @sd("yellow-LED")
  )
```

### 分割ファイル

各フェーズを独立したプログラムとして記述することもできる:

**brown2020_baseline.cdsl:**
```
-- Brown et al. (2020) — Phase 1: Baseline
@species("rat") @strain("Long-Evans") @n(5)
@reinforcer("food", type="pellet", magnitude="45mg", duration=3s)

Conc(
  VI 60-s @operandum("left-lever") @sd("stimulus-light"),
  EXT     @operandum("right-lever")
)
```

**brown2020_dra.cdsl:**
```
-- Brown et al. (2020) — Phase 2: DRA Without Extinction
@species("rat") @strain("Long-Evans") @n(5)
@reinforcer("food", type="pellet", magnitude="45mg", duration=3s)

Conc(
  VI 60-s @operandum("target-lever") @sd("stimulus-light"),
  VI 15-s @operandum("nose-poke") @sd("yellow-LED"),
  COD=3-s
)
```

**brown2020_extinction.cdsl:**
```
-- Brown et al. (2020) — Phase 3: Extinction Test
@species("rat") @strain("Long-Evans") @n(5)

Conc(
  EXT @operandum("target-lever") @sd("stimulus-light"),
  EXT @operandum("nose-poke") @sd("yellow-LED")
)
```

---

## 2. 行動的慣性: 変化抵抗

**論文:** McLean, A. P., Grace, R. C., & Nevin, J. A. (2012). Response strength in extreme multiple schedules. *JEAB*, *97*(1), 51-70. https://doi.org/10.1901/jeab.2012.97-51

**デザイン:** 極端な強化率比を持つ多元スケジュール。各条件で安定したベースラインを確立し（最低 20 セッション + 5 セッションにわたる視覚的安定性）、プレフィーディングによる変化への抵抗を検証する。条件間で成分間の強化率比を変動させる。

**示される DSL 機能:** `sessions >=`, `stable()`, `Mult`, `@session_end`, `@clock`

```
-- McLean, Grace, & Nevin (2012) JEAB 97(1), 51-70
-- Response strength in extreme multiple schedules

@species("pigeon") @n(4)
@deprivation("85% ad-lib weight")
@chamber("custom", dimensions="32x34x34cm")
@reinforcer("food", type="grain", duration=3s)
@clock(resolution=50ms)
@session_end(rule="time", time=120min)

-- 条件の順序は被験体ごとに異なる（カウンターバランス）。
-- このファイルは被験体 P5 の系列を記述。

phase Condition1:
  sessions >= 20
  stable(visual, window=5)

  Mult(
    RI 40-s @sd("red") @reinforcer("food"),
    RI 40-s @sd("green") @reinforcer("food")
  )

phase RTC_Test1:
  sessions = 5
  -- prefeeding: 20g, 30g, 30g, 40g, 40g

  Mult(
    RI 40-s @sd("red") @reinforcer("food"),
    RI 40-s @sd("green") @reinforcer("food")
  )

phase Condition2:
  sessions >= 20
  stable(visual, window=5)

  Mult(
    RI 20-s @sd("red") @reinforcer("food"),
    RI 160-s @sd("green") @reinforcer("food")
  )

phase RTC_Test2:
  sessions = 5

  Mult(
    RI 20-s @sd("red") @reinforcer("food"),
    RI 160-s @sd("green") @reinforcer("food")
  )

-- ... （追加条件は簡潔のため省略）
```

**注記:**
- `sessions >= 20` は最低セッション数を指定する。実際のセッション数は安定性に依存する。
- `stable(visual, window=5)` は 5 セッションにわたる視覚的安定性がフェーズ遷移の要件であることを宣言する。具体的なアルゴリズムは実験者がランタイムで決定する。
- 被験体間の条件順序のカウンターバランスは DSL のスコープ外。

---

## 3. 行動的慣性: 質量蓄積

**論文:** Craig, A. R., Cunningham, P. E., & Shahan, T. A. (2015). Behavioral momentum and accumulation of behavioral mass. *JEAB*, *103*(3), 437-449. https://doi.org/10.1002/jeab.145

**デザイン:** 多元 VI 30-s VI 120-s。7 条件でスケジュール-刺激連合のセッション数を変動させる（1, 2, 3, 5, 20 セッション）。各条件の後に 5 セッションの消去テストを実施。

**示される DSL 機能:** `Mult`, `BO`, `@baseline`, `@algorithm`, フェーズレベル annotation

```
-- Craig, Cunningham, & Shahan (2015) JEAB 103(3), 437-449
-- Behavioral momentum and mass accumulation

@species("pigeon") @n(8)
@deprivation("80% free-feeding weight")
@reinforcer("food", type="pigeon-checkers", duration=1.5s)
@algorithm("fleshler-hoffman")

-- 条件 1: 20 セッションブロック
phase Baseline_C1:
  sessions = 40  -- 2 ブロック × 20 セッション

  Mult(
    VI 30-s @sd("color-A"),
    VI 120-s @sd("color-B"),
    BO=30-s
  )
  @session_end(rule="time", time=30min)
  @baseline(component_duration=3min, components_per_session=10, alternation="strict")

phase Extinction_C1:
  sessions = 5

  Mult(
    EXT @sd("color-A"),
    EXT @sd("color-B"),
    BO=30-s
  )
  @session_end(rule="time", time=30min)

-- 条件 2: 5 セッションブロック
phase Baseline_C2:
  sessions = 40

  Mult(
    VI 30-s @sd("color-A"),
    VI 120-s @sd("color-B"),
    BO=30-s
  )

phase Extinction_C2:
  sessions = 5

  Mult(
    EXT @sd("color-A"),
    EXT @sd("color-B"),
    BO=30-s
  )

-- ... （条件 3-7 も同様）
```

**注記:**
- `BO=30-s` はブラックアウト（成分間インターバル）を指定する。`component_duration` とは異なる。
- `@baseline(...)` はセッション構造のメタデータ（成分持続時間、交替パターン）を提供する。
- 同一スケジュールを持つフェーズの繰り返しは、フェーズ再利用のための `use` キーワードの動機となる（syntax guide 参照）。

---

## 4. 罰後のリニューアル

**論文:** Broomer, S. T., & Bouton, M. E. (2022). Renewal of operant behavior following punishment or extinction in different contexts. *Learning & Behavior*, *51*(3), 262-273. https://doi.org/10.3758/s13420-022-00543-1

**デザイン:** 罰と消去を比較する ABA リニューアルデザイン。文脈 A で反応訓練、文脈 B で罰（または消去）、その後両文脈でテスト。文脈変更が罰された行動を復活させるかを検証する。

**示される DSL 機能:** `Overlay`, `@context`, `@punisher`, `@session_end`

```
-- Broomer & Bouton (2022) Learn Behav 51(3), 262-273
-- Renewal after punishment vs extinction (Exp 1a)

@species("rat") @strain("Wistar") @n(32)
@deprivation("80% free-feeding weight")
@reinforcer("food", type="pellet", magnitude="45mg")

phase MagazineTraining:
  sessions = 1  -- 各文脈につき

  EXT  -- RT 30-s（反応非依存的ペレット提示）
  @context("A") @context("B")  -- 両文脈

phase ResponseTraining:
  sessions = 6

  RI 30-s @operandum("lever")
  @context("A")
  @session_end(rule="time", time=30min)

phase Punishment:
  sessions = 4

  Overlay(
    RI 30-s @reinforcer("food"),
    VI 90-s @punisher("shock", intensity="0.5mA", duration=0.5s)
  ) @operandum("lever")
  @context("B")

phase RenewalTest:
  sessions = 1

  EXT @operandum("lever")
  @session_end(rule="time", time=10min)
  -- 文脈 A と文脈 B の両方でテスト（順序はカウンターバランス）
```

**注記:**
- `Overlay(RI 30-s, VI 90-s)` は維持された強化に罰を重畳する — 罰研究の定義的特徴（Azrin & Holz, 1966）。
- `@context("A")` / `@context("B")` は環境文脈をアノテートする。リニューアルデザインにおける決定的な独立変数。
- テストフェーズは両文脈で実施される。テスト順序のカウンターバランスは DSL のスコープ外。

---

## まとめ

| 例 | 主要構文 | 研究領域 |
|---|---|---|
| Brown et al. (2020) | `Conc`, `phase`, `sessions` | リサージェンス / トランスレーショナル |
| McLean et al. (2012) | `Mult`, `sessions >=`, `stable()` | 行動的慣性 / パラメトリック |
| Craig et al. (2015) | `Mult`, `BO`, `@baseline`, `@algorithm` | 行動的慣性 / 質量蓄積 |
| Broomer & Bouton (2022) | `Overlay`, `@context`, `@punisher` | リニューアル / 嫌悪制御 |

---

## 引用文献

- Azrin, N. H., & Holz, W. C. (1966). Punishment. In W. K. Honig (Ed.), *Operant behavior: Areas of research and application* (pp. 380-447). Appleton-Century-Crofts.
- Broomer, S. T., & Bouton, M. E. (2022). Renewal of operant behavior following punishment or extinction in different contexts. *Learning & Behavior*, *51*(3), 262-273. https://doi.org/10.3758/s13420-022-00543-1
- Brown, T. L., Greer, B. D., Craig, A. R., Roane, H. S., & Shahan, T. A. (2020). Resurgence following differential reinforcement of alternative behavior implemented with and without extinction. *JEAB*, *113*(2), 449-467. https://doi.org/10.1002/jeab.590
- Craig, A. R., Cunningham, P. E., & Shahan, T. A. (2015). Behavioral momentum and accumulation of behavioral mass. *JEAB*, *103*(3), 437-449. https://doi.org/10.1002/jeab.145
- McLean, A. P., Grace, R. C., & Nevin, J. A. (2012). Response strength in extreme multiple schedules. *JEAB*, *97*(1), 51-70. https://doi.org/10.1901/jeab.2012.97-51
