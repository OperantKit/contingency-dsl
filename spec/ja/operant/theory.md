# オペラント理論 — 三項随伴性（SD–R–SR）

## 要旨

本文書は contingency-dsl のオペラント層を形式化する。すなわち、三項随伴性（SD–R–SR）下での強化スケジュールの代数的分類である。すべての単純強化スケジュールは 2 つの独立次元 — Distribution（分布）と Domain（領域）— の積として表現可能であり、3×3 のアトミック・スケジュール格子を生成することを示す。7 つのコンビネータ（Concurrent, Alternative, Conjunctive, Chained, Tandem, Multiple, Mixed）上に、交換性・結合性・単位元・零元を含む代数的性質を形式的に特徴付けた合成代数を定義する。表示意味論（§2.13）は、各スケジュール式を Mealy 機械風のスケジュール機械へ写すものであり、意味的等価性についての合成的推論を可能にし、表示的定義と操作的定義を結ぶ adequacy 定理を確立する。Part III は、多相オペラント計画のための実験層を導入する。

パラダイム中立の内容（CFG/LL(2) 骨格、随伴性の一般的定義、非 TC 主張、型安全性定理の抽象的言明）は基盤層に置く。

- [foundations/grammar.md](../foundations/grammar.md) — パラダイム中立な CFG/LL(2) 骨格およびメタ文法
- [foundations/theory.md](../foundations/theory.md) — 随伴性の一般的定義、決定性、非 TC
- [foundations/contingency-types.md](../foundations/contingency-types.md) — 二項 vs 三項の区別
- [foundations/ll2-proof.md](../foundations/ll2-proof.md) — LL(2) 構文解析表および証明
- [grammar.md](grammar.md) — オペラント固有の EBNF 産出規則
- [implementation.md](implementation.md) — Python 型マッピング、レガシー評価
- [../architecture.md](../architecture.md) — Ψ 六層アーキテクチャ、計算可能性、注釈システム
- [../representations/overview.md](../representations/overview.md) — 代替座標系（T-tau）

---

## 日本語読者への注記

本文書は形式的内容（定理、証明、表示意味論、代数則、adequacy 定理）が大部分を占める。数式、ラムダ計算表記、代数則、Mealy 機械の定義、Python 擬似コードなどは英語版と完全に一致する必要があり、散文翻訳のみでは冗長になる。したがって本 JA 版では **全体構成の見取り図と各節の要約のみを提供** し、具体的な定理・証明・コードは正規版である [`../../en/operant/theory.md`](../../en/operant/theory.md) を参照する方針とする。

---

## Part I: アトミック・スケジュール分類 — 積型 Distribution × Domain

### 1.1 2 つの独立次元

すべての単純強化スケジュールは 2 つの独立次元の積として表現できる。Ferster & Skinner（1957）の原分類で暗黙的、OperantKit フレームワークのビットパックされた `ScheduleType`（Mizutani, 2018）で明示的となったこの洞察は、形式化可能である。

**定義（強化スケジュール型）.** 強化スケジュール型 `ScheduleType` は積型 `Distribution × Domain` として定義される。ここで:

- `Distribution ∈ {Fixed, Variable, Random}` — 強化間の間隔の確率分布
- `Domain ∈ {Ratio, Interval, Time}` — 強化を駆動する次元

この 3×3 格子が、9 個のアトミック・スケジュール（FR, VR, RR, FI, VI, RI, FT, VT, RT）を生成する。

### 1.2〜1.6 詳細

§1.2 Distribution 次元、§1.3 Domain 次元、§1.4 境界事例（EXT, CRF）、§1.5 アトミック分類の完全性、§1.6 LH（Limited Hold）伝播 — 完全な定理・証明・コードは英語版を参照。

---

## Part II: 合成代数 — 合成スケジュール・コンビネータ

### 概要

オペラント層は 7 つの合成コンビネータを定義する。

| 記号 | 名称 | 意味論の概要 |
|---|---|---|
| `Conc` | Concurrent（並行） | 複数スケジュールが同時に利用可能 |
| `Alt` | Alternative（交替） | 強化後に制御権が切り替わる |
| `Conj` | Conjunctive（連言） | すべての要件を同時に満たす必要 |
| `Chain` | Chained（連鎖） | 弁別刺激付きで順次進行 |
| `Tand` | Tandem（タンデム） | 弁別刺激なしで順次進行 |
| `Mult` | Multiple（多元） | 弁別刺激付きで時間的に切り替わる |
| `Mix` | Mixed（混合） | 弁別刺激なしで時間的に切り替わる |

### 詳細

各コンビネータの操作的定義、代数的性質（交換性、結合性、単位元、零元）、強化後休止の挙動、切り替え遅延（COD, FRCO）の取扱い、罰のオーバーレイ、Sidman 回避、弁別回避、Progressive Ratio の統合、表示意味論（Mealy 機械）、adequacy 定理 — 完全版は英語版 §2.1〜§2.13 を参照。

### 2.13 表示意味論（重要）

§2.13 では、各スケジュール式 `E` に対し、Mealy 機械風スケジュール機械 `⟦E⟧` への写像を定義する。これにより、観測トレース上での意味的等価性 `≡` が形式的に定義可能となる。完全な定義と adequacy 定理（表示的意味論と操作的意味論の一致）は英語版を参照。

---

## Part III: 実験層 — 多相合成

### 概要

実験層は、オペラント・スケジュールに対する多相的な配置（ベースライン、訓練、テスト）を表現する構文と意味論を提供する。相変化基準（固定時間、固定試行数、安定性基準、パフォーマンス基準）、相間状態保持、漸進的訓練（シェイピング）、相間比較可能性などを扱う。詳細は英語版 Part III および `experiment/phase-sequence.md`, `experiment/criteria.md`, `experiment/context.md` を参照。

---

## 非目標 / スコープ外

- ランタイム挙動のシミュレーション（`contingency-core` の関心事）
- 連続空間上の動作（現行 DSL は離散事象ベース）
- 被験体間のヨーク機構（`experiment-core` 層で扱う）

---

## 参考文献

完全な参考文献リストは英語版 `../en/operant/theory.md` の References セクションを参照。中核となる参照は以下。

- Baum, W. M. (1974). On two types of deviation from the matching law: Bias and undermatching. *Journal of the Experimental Analysis of Behavior*, 22(1), 231–242. https://doi.org/10.1901/jeab.1974.22-231
- Catania, A. C. (2013). *Learning* (5th ed.). Sloan.
- Ferster, C. B., & Skinner, B. F. (1957). *Schedules of reinforcement*. Appleton-Century-Crofts.
- Fleshler, M., & Hoffman, H. S. (1962). A progression for generating variable-interval schedules. *Journal of the Experimental Analysis of Behavior*, 5(4), 529–530. https://doi.org/10.1901/jeab.1962.5-529
- Herrnstein, R. J. (1961). Relative and absolute strength of response as a function of frequency of reinforcement. *Journal of the Experimental Analysis of Behavior*, 4(3), 267–272. https://doi.org/10.1901/jeab.1961.4-267
- Mizutani, Y. (2018). OperantKit: A Swift framework for reinforcement schedule simulation [Computer software]. GitHub. https://github.com/YutoMizutani/OperantKit
- Pierce, B. C. (2002). *Types and programming languages*. MIT Press.
- Skinner, B. F. (1938). *The behavior of organisms*. Appleton-Century.
