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

## 5. 条件性情動反応 (CER)

**論文:** Estes, W. K., & Skinner, B. F. (1941). Some quantitative properties of anxiety. *Journal of Experimental Psychology*, *29*(5), 390-400. https://doi.org/10.1037/h0062283

**デザイン:** 食物系オペラント・ベースライン（レバー押しに対する VI 強化）を安定性まで確立する。その後、パヴロフ型 CS-shock ペアリングを重畳する: CS 提示中、CS 終了時に反応に関わらず無信号ショックを提示する。CS 提示中の反応抑制（CS 前ベースラインとの比）が従属変数となる。

**主要 DSL 機能:** 合成層（オペラント × レスポンデント）、`Pair.ForwardDelay`、`@cs`、`@us`、`PhaseSequence`、`Stability`

```
-- Estes & Skinner (1941) — 条件性情動反応
@species("rat") @n(12)
@deprivation("80% free-feeding weight")
@reinforcer("food", type="pellet")

PhaseSequence(
  Phase(
    name = "baseline",
    operant = VI 60-s,
    criterion = Stability(window=5, tolerance=0.10)
  ),
  Phase(
    name = "cer_training",
    operant = VI 60-s,
    respondent = Pair.ForwardDelay(tone, shock, isi=60-s, cs_duration=60-s),
    criterion = FixedSessions(n=10)
  )
)
@cs(label="tone", duration=60-s, modality="auditory")
@us(label="shock", intensity="0.5mA", delivery="unsignaled")
@iti(distribution="exponential", mean=120-s, jitter=30-s)
```

**注記:**
- US 提示はパヴロフ型（反応非依存）であり、これが CER を罰から構造的に区別する。
- オペラント・ベースラインとパヴロフ型オーバーレイは同一 `Phase` 内で共存する。両随伴性が同時に作用するためである。
- 合成仕様の全体は [composed/conditioned-suppression.md](../../spec/ja/composed/conditioned-suppression.md) を参照。

---

## 6. オペラント・ベースラインでの抑制比 (Annau & Kamin, 1961)

**論文:** Annau, Z., & Kamin, L. J. (1961). The conditioned emotional response as a function of intensity of the US. *Journal of Comparative and Physiological Psychology*, *54*(4), 428-432. https://doi.org/10.1037/h0042199

**デザイン:** 抑制比指標 `SR = B / (A + B)`（A は CS 前区間の反応数、B は CS 中の反応数）を用いた CER のパラメトリック検証。ショック強度の異なる 5 群を比較。

**主要 DSL 機能:** 合成層、抑制比測定アノテーション、`progressive` によるパラメトリック・フェーズ展開

```
-- Annau & Kamin (1961) — ショック強度パラメトリック CER
@species("rat") @strain("Sprague-Dawley") @n(30)
@deprivation("80% free-feeding weight")
@reinforcer("food", type="pellet")

phase Baseline:
  sessions = 10
  stable(visual, window=5)
  VI 150-s
  @operandum("lever")

progressive SuppressionAcquisition:
  steps intensity = ["0.28mA", "0.49mA", "0.85mA", "1.55mA", "2.91mA"]
  sessions = 10
  VI 150-s
  respondent = Pair.ForwardDelay(tone, shock, isi=180-s, cs_duration=180-s)
  @operandum("lever")
  @cs(label="tone", duration=180-s, modality="auditory")
  @us(label="shock", intensity="{intensity}", delivery="unsignaled")
  @dependent_measure(variables=["suppression_ratio"],
                     suppression_ratio={method="annau_kamin",
                                        pre_cs_window=180-s,
                                        cs_window=180-s})
```

**注記:**
- `@dependent_measure` アノテーションで抑制比手続きと A / B 窓を明示する。再現性のため必要。
- `progressive` は 5 つのフェーズ（強度別）に展開し、ベースライン構造を保ったまま各強度を設定する。
- Annau & Kamin の知見: 抑制比の獲得は US 強度の段階的関数であり、強いショックほど抑制が急峻かつ深い。

---

## 7. ハトのキーつつきオートシェイピング (Brown & Jenkins, 1968)

**論文:** Brown, P. L., & Jenkins, H. M. (1968). Auto-shaping of the pigeon's key-peck. *Journal of the Experimental Analysis of Behavior*, *11*(1), 1-8. https://doi.org/10.1901/jeab.1968.11-1

**デザイン:** 実験ナイーブなハトにキー光 CS とグレイン US の前向きパヴロフ型ペアリングを呈示する。オペラント反応随伴性は設定されず、グレイン提示にキーつつきは不要である。少数試行内にハトは点灯したキーをつつき始める — パヴロフ型の創発反応。

**主要 DSL 機能:** 合成層（オートシェイピングをオペラント × レスポンデント配置として記述）、局在的 CS を持つ `Pair.ForwardDelay`、`@cs` モダリティ注釈

```
-- Brown & Jenkins (1968) — ハトのキーつつきオートシェイピング
@species("pigeon") @n(36)
@deprivation("80% free-feeding weight")
@chamber("picture-frame", dimensions="30x30x30cm")
@reinforcer("food", type="grain", duration=4-s)

Phase(
  name = "autoshaping_training",
  respondent = Pair.ForwardDelay(key_light, food, isi=8-s, cs_duration=8-s),
  criterion = FixedSessions(n=10)
)
@cs(label="key_light", duration=8-s, modality="visual")
@us(label="food", intensity="4s_access", delivery="unsignaled")
@iti(distribution="uniform", mean=60-s, jitter=30-s)
```

**注記:**
- オペラント production は出現しない。創発キーつつきはパヴロフ型で、測定アノテーション（図示せず）経由で記録する。
- CS は**局在的**（特定チャンバー操作体に紐づく）。これがサイン・トラッキングをゴール・トラッキングから区別する。
- オートシェイピングを Operant ではなく Composed に置く根拠は [composed/autoshaping.md](../../spec/ja/composed/autoshaping.md) を参照。

---

## 8. ネガティブ自動維持／省略 (Williams & Williams, 1969)

**論文:** Williams, D. R., & Williams, H. (1969). Auto-maintenance in the pigeon: Sustained pecking despite contingent non-reinforcement. *Journal of the Experimental Analysis of Behavior*, *12*(4), 511-520. https://doi.org/10.1901/jeab.1969.12-511

**デザイン:** Brown & Jenkins のオートシェイピングの改変版で、パヴロフ型ペアリングはそのまま、CS 提示中のキーつつきが当該試行の予定 US を直ちに打ち消す。つつきがオペラントなら省略随伴性下で消去するはずだが、パヴロフ型であれば強化子を失いつつも持続するはずである。

**主要 DSL 機能:** 合成層、反応→US キャンセル随伴性、オートシェイピングとの比較

```
-- Williams & Williams (1969) — ネガティブ自動維持
@species("pigeon") @n(16)
@deprivation("80% free-feeding weight")
@reinforcer("food", type="grain", duration=4-s)

PhaseSequence(
  Phase(
    name = "autoshaping_acquisition",
    respondent = Pair.ForwardDelay(key_light, food, isi=8-s, cs_duration=8-s),
    criterion = FixedSessions(n=5)
  ),
  Phase(
    name = "omission_contingency",
    respondent = Pair.ForwardDelay(key_light, food, isi=8-s, cs_duration=8-s),
    operant_constraint = Overlay(EXT, cancel_us_on_response=true),
    criterion = FixedSessions(n=40)
  )
)
@cs(label="key_light", duration=8-s, modality="visual")
@us(label="food", intensity="4s_access", delivery="cancelled_on_cs_response")
```

**注記:**
- `@us delivery="cancelled_on_cs_response"` で随伴性を命名し、`operant_constraint` フィールドが反応→US キャンセルの構造項を表現する。
- Williams & Williams (1969) は省略随伴性下で約 40 セッションにわたって大部分の強化子を失いつつもつつきが持続することを示した — これがオートシェイピング反応に対するパヴロフ型（非オペラント）制御の実証的根拠である。
- 仕様全体は [composed/omission.md](../../spec/ja/composed/omission.md) を参照。

---

## 9. パヴロフ-道具的転移 (PIT)

**論文:** Estes, W. K. (1948). Discriminative conditioning. II. Effects of a Pavlovian conditioned stimulus upon a subsequently established operant response. *Journal of Experimental Psychology*, *38*(2), 173-177. https://doi.org/10.1037/h0057525; Lovibond, P. F. (1983). Facilitation of instrumental behavior by a Pavlovian appetitive conditioned stimulus. *Journal of Experimental Psychology: Animal Behavior Processes*, *9*(3), 225-247. https://doi.org/10.1037/0097-7403.9.3.225

**デザイン:** 三相構造。(1) パヴロフ訓練: オペラント反応のない状態で CS-US ペアリング。(2) 道具的訓練: CS 曝露なしで US を強化子としてオペラント反応を訓練。(3) 転移テスト: オペラント反応が利用可能な状態で CS を提示（通常は消去下）。CS 中とマッチ非-CS 区間のオペラント反応率の変化で転移効果を定量する。

**主要 DSL 機能:** 合成層、独立訓練履歴を持つ `PhaseSequence`、消去テスト、テストフェーズ用 `CSOnly`

```
-- Estes (1948) / Lovibond (1983) — パヴロフ-道具的転移
@species("rat") @n(16)
@deprivation("22h food deprivation")
@reinforcer("food", type="pellet", magnitude="45mg")

PhaseSequence(
  Phase(
    name = "pavlovian_training",
    respondent = Pair.ForwardDelay(tone, food, isi=10-s, cs_duration=10-s),
    criterion = FixedSessions(n=8)
  ),
  Phase(
    name = "instrumental_training",
    operant = VI 60-s,
    criterion = Stability(window=5, tolerance=0.10)
  ),
  Phase(
    name = "transfer_test",
    operant = EXT,
    respondent = CSOnly(tone, trials=8),
    criterion = FixedSessions(n=1)
  )
)
@cs(label="tone", duration=10-s, modality="auditory")
@us(label="food", intensity="45mg_pellet", delivery="signaled")
@iti(distribution="exponential", mean=90-s)
```

**注記:**
- 三相は**別セッション**（または明確に分離されたブロック）で実施される。`PhaseSequence` 構文がこれを保証する。
- 転移テストではオペラント・スケジュールを `EXT` に置き、ベースライン強化ゼロの下で CS 効果を読み取る。
- 一般型 PIT と結果特異型 PIT の区別は [composed/pit.md](../../spec/ja/composed/pit.md) を参照。

---

## まとめ

| 例 | 主要構文 | 研究領域 |
|---|---|---|
| Brown et al. (2020) | `Conc`, `phase`, `sessions` | リサージェンス / トランスレーショナル |
| McLean et al. (2012) | `Mult`, `sessions >=`, `stable()` | 行動的慣性 / パラメトリック |
| Craig et al. (2015) | `Mult`, `BO`, `@baseline`, `@algorithm` | 行動的慣性 / 質量蓄積 |
| Broomer & Bouton (2022) | `Overlay`, `@context`, `@punisher` | リニューアル / 嫌悪制御 |
| Estes & Skinner (1941) | `Pair.ForwardDelay`, `@cs`, `@us`, composed | CER / 嫌悪系パヴロフ |
| Annau & Kamin (1961) | `progressive`, 抑制比, composed | CER パラメトリック / 強度 |
| Brown & Jenkins (1968) | `Pair.ForwardDelay`, オペラントなし, composed | オートシェイピング / サイン・トラッキング |
| Williams & Williams (1969) | operant_constraint, 省略, composed | ネガティブ自動維持 |
| Estes (1948) / Lovibond (1983) | `PhaseSequence`, `CSOnly`, composed | パヴロフ-道具的転移 |

---

## 引用文献

- Annau, Z., & Kamin, L. J. (1961). The conditioned emotional response as a function of intensity of the US. *Journal of Comparative and Physiological Psychology*, *54*(4), 428-432. https://doi.org/10.1037/h0042199
- Azrin, N. H., & Holz, W. C. (1966). Punishment. In W. K. Honig (Ed.), *Operant behavior: Areas of research and application* (pp. 380-447). Appleton-Century-Crofts.
- Broomer, S. T., & Bouton, M. E. (2022). Renewal of operant behavior following punishment or extinction in different contexts. *Learning & Behavior*, *51*(3), 262-273. https://doi.org/10.3758/s13420-022-00543-1
- Brown, P. L., & Jenkins, H. M. (1968). Auto-shaping of the pigeon's key-peck. *Journal of the Experimental Analysis of Behavior*, *11*(1), 1-8. https://doi.org/10.1901/jeab.1968.11-1
- Brown, T. L., Greer, B. D., Craig, A. R., Roane, H. S., & Shahan, T. A. (2020). Resurgence following differential reinforcement of alternative behavior implemented with and without extinction. *JEAB*, *113*(2), 449-467. https://doi.org/10.1002/jeab.590
- Craig, A. R., Cunningham, P. E., & Shahan, T. A. (2015). Behavioral momentum and accumulation of behavioral mass. *JEAB*, *103*(3), 437-449. https://doi.org/10.1002/jeab.145
- Estes, W. K. (1948). Discriminative conditioning. II. Effects of a Pavlovian conditioned stimulus upon a subsequently established operant response. *Journal of Experimental Psychology*, *38*(2), 173-177. https://doi.org/10.1037/h0057525
- Estes, W. K., & Skinner, B. F. (1941). Some quantitative properties of anxiety. *Journal of Experimental Psychology*, *29*(5), 390-400. https://doi.org/10.1037/h0062283
- Lovibond, P. F. (1983). Facilitation of instrumental behavior by a Pavlovian appetitive conditioned stimulus. *Journal of Experimental Psychology: Animal Behavior Processes*, *9*(3), 225-247. https://doi.org/10.1037/0097-7403.9.3.225
- McLean, A. P., Grace, R. C., & Nevin, J. A. (2012). Response strength in extreme multiple schedules. *JEAB*, *97*(1), 51-70. https://doi.org/10.1901/jeab.2012.97-51
- Rescorla, R. A., & Solomon, R. L. (1967). Two-process learning theory: Relationships between Pavlovian conditioning and instrumental learning. *Psychological Review*, *74*(3), 151-182. https://doi.org/10.1037/h0024475
- Williams, D. R., & Williams, H. (1969). Auto-maintenance in the pigeon: Sustained pecking despite contingent non-reinforcement. *Journal of the Experimental Analysis of Behavior*, *12*(4), 511-520. https://doi.org/10.1901/jeab.1969.12-511
- McLean, A. P., Grace, R. C., & Nevin, J. A. (2012). Response strength in extreme multiple schedules. *JEAB*, *97*(1), 51-70. https://doi.org/10.1901/jeab.2012.97-51
