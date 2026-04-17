# 分化強化スケジュール — DRO, DRL, DRH, DRA, DRI

> contingency-dsl オペラント層の一部。反応数や経過時間ではなく、反応ストリームの時間的性質（反応間時間、反応不在）に基づいて強化をゲートする強化スケジュール。

---

## 1. スコープ

分化強化（DR）スケジュールは 3×3 アトミック格子と直交する。これらは **制約スケジュール** または **修飾子** であり、タンデムまたは連言配置を介して格子スケジュールと合成可能である。DSL は DRL/DRH/DRO を修飾子式として表現する（`operant/grammar.md §1.3` 参照）。DRA と DRI は並行配置上のパターンである。

```
DRConstraint ::= DRL(irt_min : ℝ⁺)        -- IRT ≥ 閾値
               | DRH(irt_max : ℝ⁺)        -- IRT ≤ 閾値
               | DRO(omission_time : ℝ⁺)  -- 指定持続中に反応なし
```

## 2. DRL — 低頻度他行動分化強化

**定義.** 反応間時間（IRT）が `t` 秒以上のとき、その反応が強化される。主な手続き的用途は、長い IRT を分化強化することで低い反応率を確立することである。

```
DRL 5-s              -- IRT ≥ 5 秒で強化可能
Tand(VR 20, DRL 5-s) -- タンデム合成: VR 20 カウント AND IRT ≥ 5 秒
```

単独の `DRL t` は `Tand(CRF, DRL t)` と意味論的に等価である: IRT 基準を満たすすべての反応が強化される（Ferster & Skinner, 1957, 第 8 章）。

標準参照:
- Ferster, C. B., & Skinner, B. F. (1957). *Schedules of reinforcement*. Appleton-Century-Crofts.（第 8 章: DRL の原形式化）
- Kramer, T. J., & Rilling, M. (1970). Differential reinforcement of low rates: A selective critique. *Psychological Bulletin*, 74(4), 225–254. https://doi.org/10.1037/h0029813

## 3. DRH — 高頻度他行動分化強化

**定義.** 反応間時間（IRT）が `t` 秒以下のとき、すなわちその反応が直前の反応から `t` 秒以内に生じたとき、その反応が強化される。高い反応率を確立するために用いられる。

```
DRH 2-s              -- IRT ≤ 2 秒で強化可能
```

## 4. DRO — 他行動分化強化

**定義.** 標的反応が `t` 秒間 *不在* であるとき、強化子が呈示される（Reynolds, 1961）。手続き的な名称は歴史的に誤解を招きやすい。効果は主に省略／消去の要素に依存し、「他」行動の強化そのものに依存しない。

```
DRO 10-s             -- 10 秒間標的反応なし → 強化
```

**「省略」解釈の根拠.** Mazaleski, Iwata, Vollmer, Zarcone, and Smith (1993) は強化と省略の要素を分離し、DRO の有効性が主として省略随伴性に依存することを示した。Rey, Betz, Sleiman, Kuroda, and Podlesnik (2020a, 2020b) はこの知見を再現し拡張した。Hronek and Kestner (2025) はさらに、DRO 下での commission と omission 誤りの非対称性を検討した。

**全区間 vs 可変瞬間 DRO.** Lindberg, Iwata, Kahng, and DeLeon (1999) は、DRO 手続きに対する 2×2 分類（全区間 vs 瞬間的、固定 vs 変動）を確立した。現行 DSL は固定全区間 DRO を表現する。2×2 分類は将来の追加的変更チェックポイントに繰り延べる。

標準参照:
- Reynolds, G. S. (1961). Behavioral contrast. *Journal of the Experimental Analysis of Behavior*, 4(1), 57–71. https://doi.org/10.1901/jeab.1961.4-57
- Mazaleski, J. L., Iwata, B. A., Vollmer, T. R., Zarcone, J. R., & Smith, R. G. (1993). Analysis of the reinforcement and extinction components in DRO contingencies with self-injury. *Journal of Applied Behavior Analysis*, 26(2), 143–156. https://doi.org/10.1901/jaba.1993.26-143
- Lindberg, J. S., Iwata, B. A., Kahng, S., & DeLeon, I. G. (1999). DRO contingencies: An analysis of variable-momentary schedules. *Journal of Applied Behavior Analysis*, 32(2), 123–136. https://doi.org/10.1901/jaba.1999.32-123
- Rey, C. N., Betz, A. M., Sleiman, A. A., Kuroda, T., & Podlesnik, C. A. (2020a). The role of adventitious reinforcement during differential reinforcement of other behavior: A systematic replication. *Journal of Applied Behavior Analysis*, 53(4), 2440–2449. https://doi.org/10.1002/jaba.678
- Rey, C. N., Betz, A. M., Sleiman, A. A., Kuroda, T., & Podlesnik, C. A. (2020b). Adventitious reinforcement during long-duration DRO exposure. *Journal of Applied Behavior Analysis*, 53(3), 1716–1733. https://doi.org/10.1002/jaba.697
- Hronek, L. M., & Kestner, K. M. (2025). A human-operant evaluation of commission and omission errors during differential reinforcement of other behavior. *Journal of Applied Behavior Analysis*. https://doi.org/10.1002/jaba.70003

## 5. DRA — 代替行動分化強化

**定義（DRA）.** 標的反応に対する消去と、指定された代替反応に対する強化。応用行動分析で一般的に用いられる臨床手続きである（Cooper, Heron, & Heward, 2020）。

DRO/DRL/DRH（時間パラメータで定義される単一操作手段の修飾子）とは異なり、DRA は本質的に **2 つ** の反応クラスにまたがる随伴性を規定する。スケジュールレベルでは、DRA は並行配置として表現可能である。

```
let dra = Conc(EXT, CRF)           -- 標的は消去、代替は連続強化
let dra_vi = Conc(EXT, VI 30-s)    -- 標的は消去、代替は VI 30
```

## 6. DRI — 非両立行動分化強化

**定義（DRI）.** DRA の特殊事例であり、代替行動が標的と物理的に非両立であるもの（Cooper, Heron, & Heward, 2020）。スケジュール構造は DRA と同一であり、区別はトポグラフィ的なもの（どの行動を代替とするか）である。

DRA と DRI は contingency-dsl における **文書化されたパターン** であり、プリミティブ・コンストラクタではない。トポグラフィ的区別は注釈層に委譲される（例: `extensions/clinical-annotator` の `@target`, `@replacement`）。

## 7. 合成

DR 修飾子は格子スケジュールおよびコンビネータと合成可能である。

```
Tand(VR 20, DRL 5-s)       -- 比率要件 AND IRT 要件
Mult(DRL 5-s, DRL 1-s)     -- 要素間で IRT 要件を交替
Chain(FR 5, DRO 10-s)      -- FR 5 の後に DRO 10
```

単独の DR 修飾子は暗黙の CRF ベースを伴うものとして解釈される: `DRL 5-s ≡ Tand(CRF, DRL 5-s)`（`operant/theory.md §1.4`）。

## 8. エラーと警告

| コード | 条件 | 重大度 |
|---|---|---|
| `DR_NONPOSITIVE_VALUE` | DRL/DRH/DRO で `t ≤ 0` | SemanticError |
| `DR_TIME_UNIT_REQUIRED` | 時間単位を伴わない DRL/DRH/DRO | SemanticError |

完全なレジストリは `conformance/operant/errors.json` を参照。

## 9. 設計上の決定

DR スケジュールは、**3×3 格子と直交するフィルタ／修飾子** としてモデル化される。格子への追加エントリではない。これらは Distribution × Domain とは異なる次元（IRT、反応不在）で作動する。この位置付けは DR の手続き的論理に合致しており、`Tand` や `Conj` を介した格子スケジュールとの簡潔な合成を許容する。形式的扱いは `operant/theory.md §1.4` を参照。

DRA と DRI は **DSL プリミティブではない** — 臨床注釈付きの並行パターンとして扱われる — これは、それらの定義属性（標的と代替のトポグラフィ的非両立性）が行動的なものであり、スケジュール構造的なものではないからである。`operant/theory.md §1.4`（DRA/DRI に関する注記）を参照。

## 参考文献

§2〜§4 のインライン参照を参照。追加の背景:

- Cooper, J. O., Heron, T. E., & Heward, W. L. (2020). *Applied behavior analysis* (3rd ed.). Pearson.
- Ferster, C. B., & Skinner, B. F. (1957). *Schedules of reinforcement*. Appleton-Century-Crofts.
