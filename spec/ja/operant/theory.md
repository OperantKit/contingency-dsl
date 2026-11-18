# オペラント理論 — 三項随伴性 (SD–R–SR)

## 要旨

本文書は contingency-dsl のオペラント層を形式化する。すなわち、三項随伴性 (SD–R–SR) 下での強化スケジュールの代数的分類である。すべての単純強化スケジュールは 2 つの独立次元 — Distribution (分布) と Domain (領域) — の積として表現可能であり、3×3 のアトミック・スケジュール格子を生成することを示す。7 つのコンビネータ (Concurrent, Alternative, Conjunctive, Chained, Tandem, Multiple, Mixed) 上に、交換性・結合性・単位元・零元を含む代数的性質を形式的に特徴付けた合成代数を定義する。表示意味論 (§2.13) は、各スケジュール式を Mealy 機械風のスケジュール機械へ写すものであり、意味的等価性についての合成的推論を可能にし、表示的定義と操作的定義を結ぶ adequacy 定理を確立する。Part III は、多相オペラント計画のための実験層を導入する。

パラダイム中立の内容 (CFG/LL(2) 骨格、随伴性の一般的定義、非 TC 主張、型安全性定理の抽象的言明) は基盤層に置く。

- [foundations/grammar.md](../foundations/grammar.md) — パラダイム中立な CFG/LL(2) 骨格およびメタ文法
- [foundations/theory.md](../foundations/theory.md) — 随伴性の一般的定義、決定性、非 TC
- [foundations/contingency-types.md](../foundations/contingency-types.md) — 二項 vs 三項の区別
- [foundations/ll2-proof.md](../foundations/ll2-proof.md) — LL(2) 構文解析表および証明
- [grammar.md](grammar.md) — オペラント固有の EBNF 産出規則
- [implementation.md](implementation.md) — Python 型マッピング、レガシー評価
- [../architecture.md](../architecture.md) — 六層アーキテクチャ、計算可能性、注釈システム
- [../representations/overview.md](../representations/overview.md) — 代替座標系 (T-tau)

---

## 日本語読者への注記

本文書は形式的内容 (定理、証明、表示意味論、代数則、adequacy 定理) が大部分を占める。数式、ラムダ計算表記、代数則、Mealy 機械の定義、Python 擬似コードなどは英語版と完全に一致する必要があり、散文翻訳のみでは冗長になる。したがって本 JA 版では **全体構成の見取り図と各節の要約のみを提供** し、具体的な定理・証明・コードは正規版である [`../../en/operant/theory.md`](../../en/operant/theory.md) を参照する方針とする。

---

## 別名としての刺激の役割

基盤層は、刺激を名前と物理的属性で定義し ([刺激](../foundations/stimulus-typing.md))、パラダイム中立な依存の型を定義する ([依存の型 §2](../foundations/contingency-types.md))。オペラント層の役割の名前は、それらの依存の型の中の位置に対する別名である。別名は位置を越える意味を足さない。刺激が行動に何をするかは言わない。

**三項随伴性.** 別の刺激が出ている間に成り立つ反応→刺激の依存に対するオペラント層の名前で、`(SD, R, SR)` と書く。SD が出ている間に、反応 R が刺激の呈示 SR を生む (Skinner, 1938; 1953)。強化スケジュール、状態依存のオペラント手続き、試行ベースのオペラント手続きは、どれもその特定の形を表す。

| 別名 | 記号 | パラダイム中立な依存の型の中の位置 |
|---|---|---|
| 正の強化子 | Sr+ | 反応→刺激の依存によって呈示される刺激 |
| 負の強化子 | Sr− | 反応→刺激の依存によって除去・取りやめ・先送りされる刺激 |
| 罰子 | — | `Overlay` または `PUNISH` 指令で組まれた反応→刺激の依存によって呈示される刺激 |
| 弁別刺激 | SD, `S^D` | 反応→刺激の依存が有効な間に出ている刺激 |
| S-デルタ | SΔ, `S^Δ` | その反応→刺激の依存が有効でない間に出ている刺激 |

**SD と SΔ は注釈レベル.** SD と SΔ は `@sd` と `@s_delta` でオペラントのスケジュール式に付ける。CFG にプリミティブの構成子としては現れない。三項随伴性は (スケジュール式, `@sd` 注釈) の組で具体化される。注釈は `procedure-annotator/stimulus` モジュール (`@sd`, `@s_delta`, `@reinforcer`) が提供する。

```
Mult(VI 30-s @sd("tone"), EXT @s_delta("light"))
```

オペラント層は、刺激→刺激と時間→刺激の依存も自分の語彙で持つ (`Chain` の連鎖の切り替わり、`FT`・`VT`・`RT`)。

### 注記: オペラントの伝統による効果の定義と valence

この注記は、オペラントの伝統が役割を行動への効果でどう定義するかを記す。上の別名の定義の一部ではなく、この伝統の読みであり、DSL はこれを検査しない。

- **効果の定義.** この伝統は、正の強化子を呈示により R を増やす結果 (Skinner, 1953)、負の強化子を除去により R を増やす結果 (Sidman, 1953)、罰子を呈示により R を減らす結果 (Azrin & Holz, 1966)、SD を反応が強化されるときを合図する刺激、SΔ を強化されないときを合図する刺激 (Skinner, 1938) と定義する。
- **valence (誘発価).** この伝統は、被験体がその呈示を得ようと (またはその除去を避けようと) 働く刺激を *食欲的*、被験体がそれを避け・逃れ・終わらせようと (またはその除去を生じさせようと) 働く刺激を *嫌悪的* と呼ぶ。この読みでの valence は、被験体とその状態に相対的な機能的属性であり、孤立した刺激の属性ではない。餌は食物を遮断されたラットには食欲的で、飽和したラットには無関係でありうる (Catania, 2013, Ch. 3)。DSL は valence を記録しない。どの注釈の schema にも valence の引数は無い。
- **4 象限.** valence と操作 (呈示または除去) を組み合わせると、この伝統の 4 象限になる。DSL は *操作* をコンビネータまたは注釈で明示する (`Overlay(baseline, punisher)` と裸の `VI 60-s`、`@reinforcer` と `@punisher`)。手続きがどの象限に入るかはこの伝統の読みであり、構文解析時には強制しない。

|  | 呈示 | 除去 |
|---|---|---|
| **食欲的** | 正の強化 (Sr+) | 負の罰 |
| **嫌悪的** | 正の罰 | 負の強化 (Sr−) |

- **嫌悪性制御.** オペラント層には、この伝統が嫌悪性制御に分類する一級のプリミティブが 2 つある。`Sidman(SSI, RSI)` — フリーオペラント回避 (Sidman, 1953; §2.7) — と `DiscriminatedAvoidance(CSUSInterval, ITI, mode, ...)` — 試行ベースの回避 (Solomon & Wynne, 1953; §2.9)。罰は `Overlay` コンビネータと `Conc` の `PUNISH(...)` 指令で表す (§2.10)。

---

## Part I: アトミック・スケジュール分類 — 積型 Distribution × Domain

### 1.1 2 つの独立次元

すべての単純強化スケジュールは 2 つの独立次元の積として表現できる。Ferster & Skinner (1957) の原分類で暗黙的、OperantKit フレームワークのビットパックされた `ScheduleType` (Mizutani, 2018) で明示的となったこの洞察は、形式化可能である。

**定義 (強化スケジュール型).** 強化スケジュール型 `ScheduleType` は積型 `Distribution × Domain` として定義される。ここで:

- `Distribution ∈ {Fixed, Variable, Random}` — 強化間の間隔の確率分布
- `Domain ∈ {Ratio, Interval, Time}` — 強化を駆動する次元

この 3×3 格子が、9 個のアトミック・スケジュール (FR, VR, RR, FI, VI, RI, FT, VT, RT) を生成する。

### 1.2〜1.6 詳細

§1.2 Distribution 次元、§1.3 Domain 次元、§1.4 境界事例 (EXT, CRF)、§1.5 アトミック分類の完全性、§1.6 LH (Limited Hold) 伝播 — 完全な定理・証明・コードは英語版を参照。

---

## Part II: 合成代数 — 合成スケジュール・コンビネータ

### 概要

オペラント層は 7 つの合成コンビネータを定義する。

| 記号 | 名称 | 意味論の概要 |
|---|---|---|
| `Conc` | Concurrent (並行) | 複数スケジュールが同時に利用可能 |
| `Alt` | Alternative (交替) | 強化後に制御権が切り替わる |
| `Conj` | Conjunctive (連言) | すべての要件を同時に満たす必要 |
| `Chain` | Chained (連鎖) | 弁別刺激付きで順次進行 |
| `Tand` | Tandem (タンデム) | 弁別刺激なしで順次進行 |
| `Mult` | Multiple (多元) | 弁別刺激付きで時間的に切り替わる |
| `Mix` | Mixed (混合) | 弁別刺激なしで時間的に切り替わる |

### 詳細

各コンビネータの操作的定義、代数的性質 (交換性、結合性、単位元、零元)、強化後休止の挙動、切り替え遅延 (COD, FRCO) の取扱い、罰のオーバーレイ、Sidman 回避、弁別回避、自由オペラント逃避 (Escape)、Progressive Ratio の統合、表示意味論 (Mealy 機械)、adequacy 定理 — 完全版は英語版 §2.1〜§2.13 を参照。

**嫌悪スケジュール (§2.7／§2.7b／§2.9) の要約:**

- **Sidman 自由オペラント回避** (`Sidman`, §2.7): SSI (Shock-Shock Interval) と RSI (Response-Shock Interval) の 2 温度パラメータ。`next_shock(t) = max(last_shock + SSI, last_response + RSI)`。反応が*将来*のショックを延期する (Sidman, 1953)。
- **自由オペラント逃避** (`Escape`, §2.7b): 連続嫌悪刺激が基線で提示され、各反応が刺激を SafeDuration だけ停止させる。任意の `MaxShock` が無反応時の安全カットオフを与える。Sidman の reset-delay 論理とは質的に異なるため、first-class primitive として独立 AST ノードを持つ (Dinsmoor, 1977; Dinsmoor & Hughes, 1956)。
- **弁別回避** (`DiscrimAv`, §2.9): CS (警告刺激) が CSUSInterval 後に US を予告する試行ベース手続き。`mode=fixed` は固定 `ShockDuration`、`mode=response_terminated` は反応が進行中の US を終了させる (Solomon & Wynne, 1953)。

**命名規約:** AST 中の文字列値は 2 つの lexically 交わらない規約に従う。`kind` (ノード型判別子) は PascalCase のプリミティブ名を取る (`"Sidman"`, `"DiscrimAv"`, `"Escape"`)。パラメータ enum 値は snake_case を取る (DiscrimAv mode の `"fixed"`, `"response_terminated"`、TimeUnit の `"s"`, `"ms"`, `"min"` 等)。両者の文字列はケース変異下でも共有しないため、`ast.kind == "Escape"` (自由オペラント Escape プリミティブ) と `ast.params.mode == "response_terminated"` (DiscrimAv の response-terminated モード) は混同し得ない。初期仕様では `mode="escape"` (小文字) を用いていたが、`kind="Escape"` との大文字小文字違いの衝突を避けるため `"response_terminated"` にリネームした。

### 2.13 表示意味論 (重要)

§2.13 では、各スケジュール式 `E` に対し、Mealy 機械風スケジュール機械 `⟦E⟧` への写像を定義する。これにより、観測トレース上での意味的等価性 `≡` が形式的に定義可能となる。完全な定義と adequacy 定理 (表示的意味論と操作的意味論の一致) は英語版を参照。

---

## Part III: 実験層 — 多相合成

### 概要

実験層は、オペラント・スケジュールに対する多相的な配置 (ベースライン、訓練、テスト) を表現する構文と意味論を提供する。相変化基準 (固定時間、固定試行数、安定性基準、パフォーマンス基準)、相間状態保持、漸進的訓練 (シェイピング)、相間比較可能性などを扱う。詳細は英語版 Part III および `experiment/phase-sequence.md`, `experiment/criteria.md`, `experiment/context.md` を参照。

---

## 解釈の注記 — オペラントの伝統による自動形成と省略手続きの読み

手続きの文書 `composed/autoshaping.md` と `composed/omission.md` は、配置と観察だけを記す。レスポンデントの伝統によるそれらの読みは [レスポンデント理論 §6](../respondent/theory.md) にある。この節は、同じ手続きについてのオペラントの伝統の読みを書く場所である。まだ書いていない。読みは一次資料の引用とともにだけここに足す。

---

## 非目標 / スコープ外

- ランタイム挙動のシミュレーション (`contingency-core` の関心事)
- 連続空間上の動作 (現行 DSL は離散事象ベース)
- 被験体間のヨーク機構 (`experiment-core` 層で扱う)

---

## 参考文献

完全な参考文献リストは英語版 `../en/operant/theory.md` の References セクションを参照。中核となる参照は以下。

- Azrin, N. H., & Holz, W. C. (1966). Punishment. In W. K. Honig (Ed.), *Operant behavior: Areas of research and application* (pp. 380-447). Appleton-Century-Crofts.
- Baum, W. M. (1974). On two types of deviation from the matching law: Bias and undermatching. *Journal of the Experimental Analysis of Behavior*, 22(1), 231–242. https://doi.org/10.1901/jeab.1974.22-231
- Catania, A. C. (2013). *Learning* (5th ed.). Sloan.
- Ferster, C. B., & Skinner, B. F. (1957). *Schedules of reinforcement*. Appleton-Century-Crofts.
- Fleshler, M., & Hoffman, H. S. (1962). A progression for generating variable-interval schedules. *Journal of the Experimental Analysis of Behavior*, 5(4), 529–530. https://doi.org/10.1901/jeab.1962.5-529
- Herrnstein, R. J. (1961). Relative and absolute strength of response as a function of frequency of reinforcement. *Journal of the Experimental Analysis of Behavior*, 4(3), 267–272. https://doi.org/10.1901/jeab.1961.4-267
- Mizutani, Y. (2018). OperantKit: A Swift framework for reinforcement schedule simulation [Computer software]. GitHub. https://github.com/YutoMizutani/OperantKit
- Pierce, B. C. (2002). *Types and programming languages*. MIT Press.
- Sidman, M. (1953). Two temporal parameters of the maintenance of avoidance behavior by the white rat. *Journal of Comparative and Physiological Psychology*, *46*(4), 253–261. https://doi.org/10.1037/h0060730
- Skinner, B. F. (1938). *The behavior of organisms*. Appleton-Century.
- Skinner, B. F. (1953). *Science and human behavior*. Macmillan.
- Solomon, R. L., & Wynne, L. C. (1953). Traumatic avoidance learning: Acquisition in normal dogs. *Psychological Monographs: General and Applied*, 67(4), 1-19. https://doi.org/10.1037/h0093649
