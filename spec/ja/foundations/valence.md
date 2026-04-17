# valence（誘発価）— 食欲的 vs 嫌悪的

> contingency-dsl 基盤層の一部。食欲的／嫌悪的軸を、刺激型とは独立の直交的属性として定義する。

---

## 1. valence の軸

**定義 1（食欲的, appetitive）.** 被験体が呈示を獲得しようとして作業する（あるいは、その除去を回避しようとして作業する）ような刺激。標準例: 餌、水、性的に受容的な同種個体、社会的注目（食欲的に動機づけられた被験体において）。

**定義 2（嫌悪的, aversive）.** 被験体が呈示を回避・逃避・終結させようとして作業する（あるいは、その除去を産出しようとして作業する）ような刺激。標準例: 電撃、大音、強光、社会的注目（嫌悪的に動機づけられた被験体において、文脈的な判断）。

valence は、孤立した刺激の属性ではなく、特定の被験体と状態に相対的な **機能的** 属性である。餌は食欲制限下のラットに対しては食欲的であり、飽食したラットに対しては無関係でありうる（Catania, 2013, 第 3 章）。DSL は実験者が判定した valence を注釈レベルで記録する。DSL はそれを予測しない。

## 2. 刺激型との直交性

valence は `stimulus-typing.md` で定義される刺激型格子と直交である。どの刺激型スロットも両方の valence を許容する。

| 型 | 食欲的な例 | 嫌悪的な例 |
|---|---|---|
| US | 餌ペレット | 電撃 |
| CS | 餌を予告する音 | 電撃を予告する音 |
| SD | 餌のための比率を合図する光 | 回避機会を合図する光 |
| Sr+ / Sr− / 罰子 | 餌（Sr+） | 電撃（罰子、あるいは除去により Sr−） |

## 3. オペラントの四象限

valence と操作（呈示 / 除去）の組み合わせは、オペラントの 4 象限を生む（`stimulus-typing.md §5` 参照）。

|  | 呈示 | 除去 |
|---|---|---|
| **食欲的** | 正の強化 | 負の罰 |
| **嫌悪的** | 正の罰 | 負の強化 |

象限は (a) 刺激の valence、および (b) スケジュールの結果操作により決定される。DSL 表層文法は、コンビネータまたは注釈（`Overlay(baseline, punisher)` vs 裸の `VI 60-s`、あるいは `@reinforcer` vs `@punisher`）を介して *操作* を明示化する。*valence* は刺激注釈で指定される（`@reinforcer("shock")` はデフォルトの慣習と明示的に矛盾しており、リンターで警告されるべきである）。

## 4. オペラント層における嫌悪的統制

オペラント層では、嫌悪的統制プリミティブが 2 つ一級として存在する。

- **`Sidman(SSI, RSI)`** — 自由オペラント回避（Sidman, 1953）。`operant/schedules/compound.md` あるいは同等箇所を参照。
- **`DiscriminatedAvoidance(CSUSInterval, ITI, mode, ...)`** — 試行ベースの回避（Solomon & Wynne, 1953）。

加えて、罰は `Overlay` コンビネータおよび `Conc` 上の `PUNISH(...)` 指示子で表現される。完全な集合は `operant/grammar.md` を参照。

## 5. レスポンデント層における valence

レスポンデント・プリミティブ（`Pair.*`, `Contingency(...)` 等）それ自体は valence をエンコードしない。US の valence は `@us` 注釈を通じて記録される。古典的恐怖条件づけ（嫌悪的 US）と食欲的条件づけ（食欲的 US）は同一のレスポンデント層文法を共有し、異なるのは US に付与される注釈のみである。

## 6. valence が基盤的である理由

valence はパラダイムを横断する。

- CER（条件づけられた抑制）のような合成手続きは、テスト時に CS が嫌悪的であることを要求する（Estes & Skinner, 1941）。CS の valence はオペラント・ベースラインで直接操作されず、レスポンデント対提示によって付与される。
- PIT は、オペラント・ベースラインとレスポンデント対提示が互換な valence を用いることを要求する（正の PIT では食欲的-食欲的、恐怖増強スタートル変種では嫌悪的-嫌悪的）。

valence はオペラント・レスポンデント・合成の各層にまたがるため、特定のパラダイムではなく基盤層に属する。

## 参考文献

- Catania, A. C. (2013). *Learning* (5th ed.). Sloan.
- Estes, W. K., & Skinner, B. F. (1941). Some quantitative properties of anxiety. *Journal of Experimental Psychology*, 29(5), 390–400. https://doi.org/10.1037/h0062283
- Sidman, M. (1953). Two temporal parameters of the maintenance of avoidance behavior by the white rat. *Journal of Comparative and Physiological Psychology*, 46(4), 253–261. https://doi.org/10.1037/h0060730
- Solomon, R. L., & Wynne, L. C. (1953). Traumatic avoidance learning: Acquisition in normal dogs. *Psychological Monographs: General and Applied*, 67(4), 1–19. https://doi.org/10.1037/h0093649
