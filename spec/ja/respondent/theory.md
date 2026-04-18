# レスポンデント理論 — 二項随伴性（CS–US）

> contingency-dsl レスポンデント層の一部。二項随伴性を三項（オペラント）随伴性とは異なる形式オブジェクトとして定義し、レスポンデント文法の意味論的ターゲットとしての Rescorla (1967, 1968) 随伴性空間を導入する。反応強化に訴えない獲得と消去を議論し、条件反応（CR）獲得の構造的決定因として試行間隔（ITI）を位置づける。

**関連文書:**
- [レスポンデント文法](grammar.md) — EBNF 産出規則と拡張ポイント。
- [レスポンデント・プリミティブ](primitives.md) — R1〜R14 の操作的定義。
- [基盤理論](../foundations/theory.md) — パラダイム中立な随伴性の定義。
- [随伴性の型](../foundations/contingency-types.md) — 二項 vs 三項の型付け。

---

## 1. 別個の形式オブジェクトとしての二項随伴性

Skinner (1938) は **オペラント**（三項）と **レスポンデント**（二項）の随伴性の間に構造的区別を引いた。三項随伴性は `P(Sr+ | R, SD)` という関係を指定する。ここで弁別刺激 `SD` の存在下で発せられた反応 `R` に強化子が続く。二項随伴性は `P(US | CS)` という関係を指定する。ここで条件刺激 `CS` の存在が、統計的意味で、無条件刺激 `US` の生起と差分的に相関する。両者は共通の上位関係のパラメータ化ではない — 反応 `R` はレスポンデント配置には *不在* であり、この不在は自明ではなく構造的である。

しばしばある誤読は、二項随伴性を反応位置が消去された「退化した」三項随伴性として扱う。この誤読は CS を `SD` 役割に、CR をオペラント `R` に倒壊させる。この倒壊を退ける 3 つの論点:

1. **CR は誘発されるのであり、発せられるのではない.** Pavlov (1927) において、訓練後の唾液分泌は CS により誘発される。それは結果によって将来の確率が調整される行動ではない。一方、オペラント反応は発せられ、それに続く結果によって選択される（Skinner, 1938）。
2. **US は被験体の行動に無条件である.** 標準的なパヴロフ型配置において、US は被験体が反応するかどうかに関わらず呈示される。US 呈示のために反応が *要求される*（または禁止される）とき、その配置はもはや純粋な二項随伴性ではない — それは合成的なオペラント × レスポンデント手続きとなる（`composed/omission.md`, `composed/autoshaping.md` 参照）。
3. **意味論的ターゲットは反応強度ではなく CS の予告性である.** Rescorla (1967, 1968) は、CR が獲得するためには CS が統計的意味で US を *予告* せねばならない — `P(US | CS) ≠ P(US | ¬CS)` — ことを確立した。レスポンデント層の意味論的通貨は、反応-強化子随伴性ではなく CS-US 随伴性である。

したがって、contingency-dsl のレスポンデント文法（`grammar.md §2`）は `PairExpr`, `ContingencyExpr`, `ExtinctionExpr` 等のための固有の産出規則を持ち、オペラント産出規則に還元されない。二項随伴性と三項随伴性が共有するのはパラダイム中立の基盤層のみである（`foundations/contingency-types.md`）。

---

## 2. Rescorla 随伴性空間

Rescorla (1967, 1968) は、パヴロフ型獲得の決定的因子が単なる CS-US 対提示数ではなく、**CS 所与時と非 CS 所与時の US 確率の差** であることを示した。2 つの確率が 2 次元平面を定義する:

- `p = P(US | CS)` — CS 呈示中またはその直後の US 確率。
- `q = P(US | ¬CS)` — 試行間隔中（CS なし）の US 確率。

contingency-dsl Tier A プリミティブ `Contingency(p, q)` はこの平面を直接パラメータ化する。他のあらゆる Tier A パヴロフ型配置は特定の領域または点に対応する:

| 領域 / 点 | プリミティブ | 説明 |
|---|---|---|
| `(1, 0)` 角 | `Pair.ForwardDelay(cs, us, ...)` | 標準的な前方対提示: CS が生じたときのみ US が生じる。 |
| 対角 `p = q` | `TrulyRandom(cs, us)` | CS-US の統計的独立: `P(US | CS) = P(US | ¬CS)`。 |
| `p = 0` 軸（`q > 0`） | `ExplicitlyUnpaired(cs, us, min_separation)` | 明示的時間分離を伴う負の随伴性。 |
| `(0, 0)` 原点 | `Extinction(cs)`（獲得後） | US が一切呈示されず、CR が減衰する。 |
| CS-only 試行での `p = 0, q = 0` | `CSOnly(cs, trials)` | ベースライン／前曝露（獲得前に適用された場合は潜在抑制手続き）。 |

文法は `Contingency(p_us_given_cs, p_us_given_no_cs)` の引数順序を固定する — CS 条件付き優先、¬CS 条件付き続く — ことで、構文木が曖昧性のない意味論を保持するようにする。順序は文法レベルで順列変更不可能である。

### 2.1 `Contingency(p, q)` が Tier A でなければならない理由

随伴性空間の定式化は、現代のレスポンデント条件づけの基礎である。角 `(1, 0)`（前方対提示）と原点 `(0, 0)`（消去）のみを表現できる DSL は、Rescorla (1967, 1968) の古典的デモンストレーション — `Pair.ForwardDelay` と `TrulyRandom` が CS-US 共起頻度は同一でありながら CR 獲得において経験的に異なる — を符号化できない。したがって、`Contingency(p, q)` を Tier A 集合の外に置くことは、現代レスポンデント理論の基礎的結果を DSL が表現できないことを意味する。

### 2.2 統制手続きとしての `TrulyRandom` と `ExplicitlyUnpaired`

Rescorla (1967) は、「truly random」統制手続き（`p = q`）と「explicitly unpaired」統制手続き（`p = 0, q > 0`、時間分離付き）が経験的に区別可能であり、CS-US 連合主張に対する正しいベースラインであると論じた。Ayres, Benedict, and Witcher (1975) は直接比較を提供した。両統制は、構文木で可視となるべき明確な *実験者意図* を符号化するため、利便性のラッパーとしてではなく命名されたプリミティブとして Tier A に保持される（R9 と R10）。

---

## 3. 反応強化に訴えない獲得と消去

条件反応（CR）獲得は、CS と US の差分的相関（すなわち統計的意味での CS 予告性: `P(US | CS) − P(US | ¬CS)`）の関数である。Rescorla–Wagner モデル（Rescorla & Wagner, 1972）はこれを誤差駆動の連合強度として形式化する: CS が存在する各試行で `ΔV_CS = α_CS β_US (λ - ΣV)`。このモデルは獲得率が `p - q` に依存し、`p` のみには依存しないことを予測する（Rescorla, 1968 が確認）。

**レスポンデント消去**（Pavlov, 1927; Bouton, 2004）は、CS を US なしで呈示した場合の CR の減衰である。レスポンデント消去をオペラント消去と区別する 3 つの特徴:

1. **元の学習は消去されない.** Bouton (2004) は、獲得履歴が消去を通じて持続する証拠をレビューしている: 自発回復（保持時間後の CR 回復）、更新（文脈変化時の CR 回復）、再発（非信号化 US 呈示後の CR 回復）はいずれも、消去が元の連合を上書きするのではなく新たな抑制的連合を加えることを示す。
2. **意味論的フレームは反応強度ではなく CS 予告性.** オペラント消去はゼロ強化スケジュール下での反応率減衰として記述できるが、レスポンデント消去は CS が US を予告しなくなったときの CR の大きさの減衰である。両者は減衰曲線で似て見えるが、異なる経験的対象を指す。
3. **文脈依存性が顕著である.** CR は発せられるのではなく誘発されるため、消去中に存在する文脈刺激は被験体が学ぶものの一部となる（Bouton & Bolles, 1979）。レスポンデント層は、`experiment/context.md` の一級 Context 構成要素と `@context` 注釈を介してこれに対応する。

contingency-dsl では、消去は獲得相に続くフェーズに埋め込まれた `Extinction(cs)` で表現される。文脈感受性を要する現象（更新、再発、自発回復）はレスポンデント拡張ポイントを介して `contingency-respondent-dsl` に委譲される。

---

## 4. 試行間隔と I/T 比

試行間隔（ITI）は、単なる手続き的詳細ではなく、CR 獲得の構造的決定因である。Gibbon and Balsam (1981) は、自動形成における CR 獲得率が **I/T 比** — 平均試行間隔持続 `I` と平均試行（CS）持続 `T` の比 — で予測されることを示した。`I/T` が大きいとき獲得は速く、`I/T` が 1 に近いとき獲得は遅いか失敗する。

Gallistel and Gibbon (2000) はこれを Rate Estimation Theory（RET）に一般化した: 被験体は文脈中の US 発生率に対する CS 中の US 発生率を推定し、これらの推定の比が閾値を越えたとき CR onset が生じる。RET の下で、`I/T` はこの率比計算の観測可能な類似物である。

レスポンデント層への 2 つの含意:

1. **ITI はプリミティブレベルで指定可能でなければならない.** Tier A は `ITI(distribution, mean)`（R13）を含む。ITI を指定する能力がなければ、DSL は経験的予測が `I/T` に依存する手続きを符号化できない。
2. **ITI は構造要素であり、注釈ではない.** 注釈（`annotations/extensions/respondent-annotator.md`）は既存構造にメタデータを追加するが、構造を構成しない。`@iti` 注釈は、プリミティブレベル ITI（平均と分布族）と直交するジッター情報を提供する。ジッターが無関係な場合、プリミティブ `ITI(...)` で十分である。ジッターを記録せねばならない場合、`@iti(distribution, mean, jitter)` が囲うフェーズを注釈する。

役割分担は以下の通り:
- **プリミティブ `ITI(distribution, mean)`** — 構造要素。
- **注釈 `@iti(distribution, mean, jitter)`** — ジッターを記録する（再現性のためオプションで分布と平均も冗長に記録する）メタデータ・オーバーレイ。

一般原則については `annotations/boundary-decision.md §2`（Q1〜Q3）を参照: 構成要素を省略することが手続きの構造を変えるなら、それはプリミティブである。既存構造を注釈するだけなら、それは注釈である。

---

## 5. 合成層との関係

4 つの合成手続き（`composed/conditioned-suppression.md`, `composed/pit.md`, `composed/autoshaping.md`, `composed/omission.md`）は、オペラント・スケジュールとレスポンデント配置を組み合わせる。各々の場合、レスポンデント構成要素は本層の Tier A プリミティブであり、オペラント構成要素は `operant/schedules/` のスケジュールである。理論的統合は `composed/two-process-theory.md` で明示され、Rescorla–Solomon (1967) の 2 過程説明と、合成手続きの統一的理論枠組みとしてのその役割が要約される。

本層は合成手続きそのものを定義しない。それらが依拠するレスポンデント語彙を提供するのが本層である。

---

## 参考文献

- Ayres, J. J. B., Benedict, J. O., & Witcher, E. S. (1975). Systematic manipulation of individual events in a truly random control in rats. *Journal of Comparative and Physiological Psychology*, 88(1), 97–103. https://doi.org/10.1037/h0076200
- Bouton, M. E. (2004). Context and behavioral processes in extinction. *Learning & Memory*, 11(5), 485–494. https://doi.org/10.1101/lm.78804
- Bouton, M. E., & Bolles, R. C. (1979). Contextual control of the extinction of conditioned fear. *Learning and Motivation*, 10(4), 445–466. https://doi.org/10.1016/0023-9690(79)90057-2
- Gallistel, C. R., & Gibbon, J. (2000). Time, rate, and conditioning. *Psychological Review*, 107(2), 289–344. https://doi.org/10.1037/0033-295X.107.2.289
- Gibbon, J., & Balsam, P. (1981). Spreading association in time. In C. M. Locurto, H. S. Terrace, & J. Gibbon (Eds.), *Autoshaping and conditioning theory* (pp. 219–253). Academic Press.
- Pavlov, I. P. (1927). *Conditioned reflexes: An investigation of the physiological activity of the cerebral cortex* (G. V. Anrep, Trans.). Oxford University Press.
- Rescorla, R. A. (1967). Pavlovian conditioning and its proper control procedures. *Psychological Review*, 74(1), 71–80. https://doi.org/10.1037/h0024109
- Rescorla, R. A. (1968). Probability of shock in the presence and absence of CS in fear conditioning. *Journal of Comparative and Physiological Psychology*, 66(1), 1–5. https://doi.org/10.1037/h0025984
- Rescorla, R. A., & Solomon, R. L. (1967). Two-process learning theory: Relationships between Pavlovian conditioning and instrumental learning. *Psychological Review*, 74(3), 151–182. https://doi.org/10.1037/h0024475
- Rescorla, R. A., & Wagner, A. R. (1972). A theory of Pavlovian conditioning: Variations in the effectiveness of reinforcement and nonreinforcement. In A. H. Black & W. F. Prokasy (Eds.), *Classical conditioning II: Current research and theory* (pp. 64–99). Appleton-Century-Crofts.
- Skinner, B. F. (1938). *The behavior of organisms*. Appleton-Century.
