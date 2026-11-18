# 依存の型 — 反応→刺激、刺激→刺激、時間→刺激、条件つき確率

> contingency-dsl 基盤層の一部。DSL のすべての手続きを組み立てる、パラダイム中立な依存の型を定義する。載せるのは、今ある構成子が使っている型だけである。役割の名前 (強化子、弁別刺激、CS、US 等) はここでは使わない。各パラダイム層が、これらの型の中の位置にそれぞれの別名を付ける。

---

## 1. 随伴的 vs 非随伴的

**定義 1 (随伴的配置).** 刺激の呈示の確率が、先行する事象 (反応または刺激) の発生に依存するとき、その配置を *随伴的* であるという。形式的には、`P(presentation | antecedent) ≠ P(presentation | ¬antecedent)`。

**定義 2 (非随伴的配置).** 刺激の呈示の確率が先行事象から独立であるとき、その配置を *非随伴的* であるという。すなわち、`P(presentation | antecedent) = P(presentation | ¬antecedent)`。

オペラント層において、標準的な非随伴的スケジュールは **時隔スケジュール** (FT, VT, RT) であり、反応に関わらず時間基準で刺激が呈示される (Zeiler, 1968; Lattal, 1972)。レスポンデント層において、標準的な非随伴的統制は **TrulyRandom** であり、1 つ目の刺激の有無に関わらず 2 つ目の刺激の確率が同じになる特殊例 `Contingency(p, p)` である (Rescorla, 1967)。

**この区別が基盤的である理由.** 非随伴的配置は自明な対照条件ではない。それらは系統的な行動効果 (Skinner, 1948) を生成し、随伴的配置が定義される経験的基準点として機能する。DSL は反応非依存プリミティブ (FT/VT/RT、TrulyRandom) を退化事例ではなく一級の式として扱う。

## 2. 4 つの依存の型

依存とは、`B` が刺激の onset または offset ([刺激](stimulus-typing.md)) であるようなパラダイム中立な随伴性 `(A, B, P)` ([基盤の定義 2](theory.md)) である。DSL は、`A` が何かで区別される 4 つの型を使う。

| 依存の型 | パラダイム中立な言い方 | その型を使う構成子 |
|---|---|---|
| 反応→刺激 | 反応が刺激の呈示 (またはその取りやめ・先送り) を決める | 比率・間隔のスケジュール、`Overlay`、`Sidman`、`DiscriminatedAvoidance`、`Escape`、`@omission`、`@avoidance` |
| 刺激→刺激 | ある刺激の onset・offset が、時間関係つきで別の刺激の呈示を決める | `Pair.*`、`Serial`、`Chain` の連鎖の切り替わり、`DiscriminatedAvoidance` の `CSUSInterval` |
| 時間→刺激 | 時間の経過だけが刺激の呈示を決める | `FT`、`VT`、`RT`、`ITI`、`USOnly`、`CSOnly` |
| 条件つき確率 | 上の 3 つに確率を掛けたもの。ある事象の有無で呈示の確率が違う | `Contingency(p, q)`、`TrulyRandom`、`ExplicitlyUnpaired`、`RR` |

1 つの手続きは、1 つの式の中で複数の依存の型を組み合わせてよい。この表に新しい依存の型を足すのは、それを使う構成子と一緒のときだけである。

## 3. 二項随伴性と三項随伴性

二項随伴性と三項随伴性は、上の依存の特定の形に対するパラダイム層の名前である。

- **二項随伴性** — レスポンデント層が、刺激→刺激の依存 (多くは条件つき確率を伴う) に付ける名前。[レスポンデント理論 §0〜§2](../respondent/theory.md) で定義する。
- **三項随伴性** — オペラント層が、別の刺激が出ている間に成り立つ反応→刺激の依存に付ける名前。[オペラント理論「別名としての刺激の役割」](../operant/theory.md) で定義する。

## 4. 別々の語彙としてのオペラント層とレスポンデント層

DSL はオペラント層とレスポンデント層を姉妹の語彙として保つ (`architecture.md §4.1` および `design-philosophy.md §2` を参照)。理由は歴史的なものである。Pavlov (1927)／Skinner (1938) の区別は、ほぼ 1 世紀にわたり分野の安定した境界であり続けてきた (Catania, 2013)。DSL は既存文献の慣習を尊重する。どちらの語彙も §2 の依存の型から組み立てられる。

## 5. 高階関係および派生関係

高階関係 (関係フレーム、刺激等価類、派生刺激関係; Sidman, 1971; Hayes et al., 2001) は、contingency-dsl の基盤型では **ない**。これらは特定の訓練手続き (最も顕著には MTS) が生み出す行動的帰結であり、随伴性プリミティブではない。DSL は手続きを規定し、関係は観察される。

## 参考文献

- Catania, A. C. (2013). *Learning* (5th ed.). Sloan.
- Hayes, S. C., Barnes-Holmes, D., & Roche, B. (Eds.). (2001). *Relational frame theory: A post-Skinnerian account of human language and cognition*. Kluwer Academic/Plenum.
- Lattal, K. A. (1972). Response-reinforcer independence and conventional extinction after fixed-interval and variable-interval schedules. *Journal of the Experimental Analysis of Behavior*, 18(1), 133–140. https://doi.org/10.1901/jeab.1972.18-133
- Lattal, K. A. (1995). Contingency and behavior analysis. *Mexican Journal of Behavior Analysis*, 21, 47–73.
- Pavlov, I. P. (1927). *Conditioned reflexes: An investigation of the physiological activity of the cerebral cortex* (G. V. Anrep, Trans.). Oxford University Press.
- Rescorla, R. A. (1967). Pavlovian conditioning and its proper control procedures. *Psychological Review*, 74(1), 71–80. https://doi.org/10.1037/h0024109
- Sidman, M. (1971). Reading and auditory-visual equivalences. *Journal of Speech and Hearing Research*, 14(1), 5–13. https://doi.org/10.1044/jshr.1401.05
- Skinner, B. F. (1938). *The behavior of organisms*. Appleton-Century.
- Skinner, B. F. (1948). 'Superstition' in the pigeon. *Journal of Experimental Psychology*, 38(2), 168–172. https://doi.org/10.1037/h0055873
- Zeiler, M. D. (1968). Fixed and variable schedules of response-independent reinforcement. *Journal of the Experimental Analysis of Behavior*, 11(4), 405–414. https://doi.org/10.1901/jeab.1968.11-405
