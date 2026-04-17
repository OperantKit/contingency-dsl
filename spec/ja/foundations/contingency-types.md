# 随伴性の型 — 随伴的 vs 非随伴的、二項 vs 三項

> contingency-dsl 基盤層（Ψ）の一部。DSL をパラダイム層へ分割する基盤的な型区別を定義する。学術論考ではなく、仕様全体を通じて用いられる標準定義をここで固定する。

---

## 1. 随伴的 vs 非随伴的

**定義 1（随伴的配置）.** 結果の発生確率が、先行する事象（通常は反応または刺激）の発生に依存するとき、その配置を *随伴的* であるという。形式的には、`P(consequence | antecedent) ≠ P(consequence | ¬antecedent)`。

**定義 2（非随伴的配置）.** 結果の発生確率が先行事象から独立であるとき、その配置を *非随伴的*（反応非依存）であるという。すなわち、`P(consequence | antecedent) = P(consequence | ¬antecedent)`。

オペラント層において、標準的な非随伴的スケジュールは **時隔スケジュール**（FT, VT, RT）であり、反応に関わらず時間基準で強化子が呈示される（Zeiler, 1968; Lattal, 1972）。レスポンデント層において、標準的な非随伴的統制は **TrulyRandom** であり、`P(US | CS) = P(US | ¬CS)` となる特殊例 `Contingency(p, p)` である（Rescorla, 1967）。

**この区別が基盤的である理由.** 非随伴的配置は自明な対照条件ではない。それらは系統的な行動効果（迷信的強化; Skinner, 1948）を生成し、随伴的配置が定義される経験的基準点として機能する。DSL は反応非依存プリミティブ（FT/VT/RT、TrulyRandom）を退化事例ではなく一級の式として扱う。

## 2. 二項随伴性（CS–US）

**定義 3（二項随伴性）.** 二項随伴性とは、条件刺激（CS）と無条件刺激（US）の間の確率的関係である。標準的なパラメータ化は Rescorla（1967）の随伴性空間である。

```
two_term_contingency = (p_us_given_cs, p_us_given_no_cs)
```

座標系は 2 軸を持つ。

- **X 軸:** `P(US | CS)` — CS を所与としたときの US の確率。
- **Y 軸:** `P(US | ¬CS)` — CS が不在のときの US の確率。

標準的な 4 領域:

| 領域 | 操作的意味 | プリミティブ |
|---|---|---|
| `(p, 0)`（`p > 0`） | 興奮性 CS–US 対提示 | `Pair.*` 系 |
| `(0, q)`（`q > 0`） | 制止性（明示的非対提示） | `ExplicitlyUnpaired` |
| `(p, p)`（対角線上） | truly random、随伴性ゼロ | `TrulyRandom` |
| `(p, q)`（一般点） | 一般随伴性点 | `Contingency(p, q)` |

二項随伴性は **レスポンデント** 層（`respondent/grammar.md`, `respondent/theory.md`）の領域である。原形式化は Pavlov（1927）、現代的な随伴性空間の枠組みは Rescorla（1967, 1968）を参照。

## 3. 三項随伴性（SD–R–SR）

**定義 4（三項随伴性）.** 三項随伴性とは、弁別刺激（SD）、反応（R）、結果（SR）の間の関係である。

```
three_term_contingency = (SD, R, SR)
  where
    SD  : 弁別刺激 — R が SR を生むタイミングを合図する
    R   : オペラント反応クラス
    SR  : 結果（Sr+, Sr−, 罰子）
```

操作的読解: *SD の存在下で、反応 R が結果 SR を生む*。これはオペラント分析の基本単位である（Skinner, 1938; 1953）。

三項随伴性は **オペラント** 層（`operant/grammar.md`, `operant/theory.md`）の領域である。強化スケジュール、状態依存オペラント手続き、試行ベースのオペラント手続きはすべて、三項随伴性の特定の形を表現する。

## 4. 層境界としての二項 vs 三項

DSL は二項／三項の区別を主要な層境界として扱う（`architecture.md §4.1` および `design-philosophy.md §2` を参照）。理由は以下の通り。

1. **構造的理由.** 2 つの関係はアリティが異なり（2 vs 3）、標準パラメータ化も異なる（`(p_us_given_cs, p_us_given_no_cs)` vs `(SD, R, SR)`）。共通の「パラダイム」ノードの下に入れ子にすることは、人為的なパラメータ化を強いる。
2. **歴史的理由.** Pavlov（1927）／Skinner（1938）の区別は、ほぼ 1 世紀にわたり分野の安定した境界であり続けてきた（Catania, 2013）。DSL は既存文献の慣習を尊重する。
3. **合成可能性.** 両者を組み合わせる手続き（CER, PIT, 自動形成, 省略手続き）は、レスポンデントまたはオペラントの部分事例ではなく、`composed/` 層に一級住人として属する。

## 5. 高階関係および派生関係

高階関係（関係フレーム、刺激等価類、派生刺激関係; Sidman, 1971; Hayes et al., 2001）は、contingency-dsl の基盤型では **ない**。これらは特定の訓練手続き（最も顕著には MTS）が生み出す行動的帰結であり、随伴性プリミティブではない。DSL は手続きを規定し、関係は観察される。

## 参考文献

- Catania, A. C. (2013). *Learning* (5th ed.). Sloan.
- Hayes, S. C., Barnes-Holmes, D., & Roche, B. (Eds.). (2001). *Relational frame theory: A post-Skinnerian account of human language and cognition*. Kluwer Academic/Plenum.
- Lattal, K. A. (1972). Response-reinforcer independence and conventional extinction after fixed-interval and variable-interval schedules. *Journal of the Experimental Analysis of Behavior*, 18(1), 133–140. https://doi.org/10.1901/jeab.1972.18-133
- Lattal, K. A. (1995). Contingency and behavior analysis. *Mexican Journal of Behavior Analysis*, 21, 47–73.
- Pavlov, I. P. (1927). *Conditioned reflexes: An investigation of the physiological activity of the cerebral cortex* (G. V. Anrep, Trans.). Oxford University Press.
- Rescorla, R. A. (1967). Pavlovian conditioning and its proper control procedures. *Psychological Review*, 74(1), 71–80. https://doi.org/10.1037/h0024109
- Rescorla, R. A. (1968). Probability of shock in the presence and absence of CS in fear conditioning. *Journal of Comparative and Physiological Psychology*, 66(1), 1–5. https://doi.org/10.1037/h0025984
- Sidman, M. (1971). Reading and auditory-visual equivalences. *Journal of Speech and Hearing Research*, 14(1), 5–13. https://doi.org/10.1044/jshr.1401.05
- Skinner, B. F. (1938). *The behavior of organisms*. Appleton-Century.
- Skinner, B. F. (1948). 'Superstition' in the pigeon. *Journal of Experimental Psychology*, 38(2), 168–172. https://doi.org/10.1037/h0055873
- Skinner, B. F. (1953). *Science and human behavior*. Macmillan.
- Zeiler, M. D. (1968). Fixed and variable schedules of response-independent reinforcement. *Journal of the Experimental Analysis of Behavior*, 11(4), 405–414. https://doi.org/10.1901/jeab.1968.11-405
