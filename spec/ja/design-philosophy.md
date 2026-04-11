# contingency-dsl 設計理念

> **Status:** Authoritative design intent (2026-04-12)
>
> 本文書はプロジェクトオーナーから直接述べられた設計意図を、原発話を極力
> 保存する方針で文章化したものである。以降のすべての spec 改訂・annotation
> 追加・メタDSL 設計判断は、本文書に照らして整合性を検証されなければならない。

---

## 1. 最上位の目的

**現在までの（特に行動分析学の）すべての実験手続きを、正確に DSL 上で表現できるようにする。**

これが最上位のゴールであり、他のすべての設計判断はこの目標に奉仕する。

旧 OperantKit は、コアである強化スケジュールのプログラム的設計に苦戦し、
実験手続きとオブジェクト指向の整合性に悩みながら 3 回 1 から作り直されている。
本 DSL ではこの経験を踏まえ、**基本設計をより一層強固な基盤とし、破壊的変更が
起こらないようにする**ことを原則とする。

## 2. 経験的に安定な基礎 — Core / Schedule Extension / Annotation 三層構造

実験的行動分析の歴史は、多少の理論解釈や刺激解釈の違いはあれど、
**三項随伴性の基礎と強化スケジュールはこれまで破綻することなく、学派として
安定な基礎を成してきた**。この経験的に観察される安定性を、DSL の設計に反映する。

ただしこの安定性は **経験的観察に基づく現在の状態** であり、絶対的な保証では
ない。学派自体が将来崩壊する可能性も原理的にはあり、その場合には Core にも
例外的な変更が必要となりうる。本 DSL は「現在のところ最も安定な層」を Core
として固定するのであって、「永久不変の真理」を主張するものではない。

したがって本 DSL は次の **三層構造** を取る:

| 層 | 内容 | 変化の許容度 |
|---|---|---|
| **Core（経験的に安定）** | 三項随伴性・強化スケジュール・複合スケジュール・修飾子 | 破壊的変更は原則として避ける（例外は §8 参照） |
| **Schedule Extension（拡張 schedule 文法）** | 動的・TC 近傍の schedule 構成素（例: percentile, adjusting）。program-scoped で追加される新 schedule primitive | 各プログラムが自身の registry に extension module をロードすることで拡張 |
| **Annotation（metadata）** | 拡張理論・詳細手続き・解釈依存の付加情報 | 理論の発展・衰退に追従して自由に増減。program-scoped |

根底の安定な基礎を Core DSL として固定し、動的・TC 近傍の schedule 構成素を
Schedule Extension 層で、metadata 情報を Annotation 層でそれぞれ追加することで、
**学術的堅牢性を保ちつつ、理論の発展・衰退に追従できる** DSL を実現する。

Schedule Extension と Annotation はいずれも **program-scoped** で、各プログラムが
独自の registry を定義・採用・拒否できる。詳細は §4（Annotation）および §5
（Schedule Extension）を参照。

## 3. 使い手の構造

使い手は層によって異なる。この区別を混同してはならない。

### 3.1 Core DSL の使い手

**研究者・学生・そして「共通言語として利用する者」すべて。**

`FR5`, `Chain(FR5, FI30)`, `Conc(VI30s, VI60s)` のような記述は、
行動分析学を学んだ人間が読み書きできる共通記法として機能しなければならない。

### 3.2 Annotation 付き DSL の使い手

Annotation 付きの状態で DSL を **直接書き下ろせるようになることは、
本 DSL の目的ではない**（書き手は主に変換ツール、またはツールの補助下にある
人間である）。

一方で annotation 付き DSL は、**読まれる対象としては教育的価値が高い**。
特に、実験手続きを明示的に言語化することで、**学生に「この実験の従属変数は
何か」を明示する材料**として極めて重要な役割を持つ。暗黙的な前提が多い
行動分析学の実験手続きにおいて、annotation 付き DSL は論文本文だけでは
読み取りにくい実験デザインの構造を可視化する装置として機能する。

想定される使い手は、次の 2 系統に整理される:

1. **書き手（機械的変換の担い手）**
   追試や論証を目的として、論文に記載されたプログラムまたは DSL を
   変換する人、およびそのための変換ツール。
2. **読み手（人間）**
   - 学生 — 実験手続きの従属変数・独立変数・統制条件を読み取る学習者
   - 研究者 — 追試・査読・再現確認のために実験デザインを検証する読者

つまり annotation 付きの DSL は、**書き下ろしの教育対象ではないが、
読解の教育対象であり、同時に機械的な変換および検証の対象**でもある。

## 4. Annotation 層の構造とカテゴリ

Annotation は Core DSL の補足機構として、実験手続きに関する付加情報を担う。
本節では annotation のカテゴリ体系、およびカテゴリが「推奨分類」であって
強制ではないという原則を定める。

### 4.1 推奨カテゴリ体系（JEAB Method 節に準拠）

Annotation は以下のカテゴリに分類することを推奨する。カテゴリ名は JEAB の
Method 節の伝統的区分（Subjects / Apparatus / Procedure）に準拠し、
行動分析学の読み手が馴染みのある構造を保つ。Measurement は測定基準の
独立性を担保するため別カテゴリとして分離する。

| カテゴリ | 対象 | 主な目的 |
|---|---|---|
| **Procedure** | 手続きの記述 | (1) 暗黙的な手続きの明文化, (2) 二つの手続きの等価性判定の支援, (3) DSL と実験プログラムの相互変換に必要な条件の補足 |
| **Subjects** | 被験体 | 被験体履歴・確立操作・絶食水準・種・状態の記述。現在の随伴性が同一でも行動が異なる要因を記録する。 |
| **Apparatus** | 装置・物理実装 | Chamber・operandum・HW 仕様・タイミング許容誤差・物理量の束縛等、Core DSL の抽象を物理世界に接地させる情報。 |
| **Measurement** | 測定基準 | 定常性基準・基底率・phase 終了条件・dependent measures 等、Core の随伴性効果を *いつ・どう読み取るか* を規定する情報。 |

Procedure カテゴリの 3 目的（明文化・等価性判定・相互変換補足）は、本 DSL が
当初から annotation に求めてきた中核的役割であり、他カテゴリはこれを
補完する位置付けにある。

### 4.2 カテゴリは *推奨分類* であって強制ではない

§4.1 のカテゴリ体系は DSL プロジェクトから公開される **推奨分類** である。
Core DSL 文法はカテゴリの存在を知らず、annotation の実際のカテゴリ判定は
annotation registry と各プログラム（runtime / interpreter）が行う。

したがって **カテゴリの追加・削除・無視・再定義は、Core DSL の変更を
伴わない**。この性質により:

- ある 3rd-party プログラムが「環境条件は外部で管理するので DSL 側では
  扱わない」と決めた場合、Apparatus カテゴリの annotation を黙って
  無視する実装が可能である。Core DSL は一切変更不要。
- 別の研究グループが独自のカテゴリ（例: 派生的関係・臨床分類等）を
  定義して自身のプログラムに載せることが可能である。本家 DSL の改訂を
  待つ必要はない。
- 対立理論を扱うプログラムは、既存カテゴリを再解釈または置換できる。

このアーキテクチャにより、**Core DSL の破壊や再生成なしに、プログラム
拡張と対立理論の建立が可能**となる。これは §2 の「学術的堅牢性を保ちつつ
理論の発展・衰退に追従できる」要件を、実装レイヤで具体化したものである。

### 4.3 カテゴリ中立的プログラム等価性の原則

**原則:** カテゴリ分類は *組織化* のためのものであり、プログラム意味論の
一部ではない。ground truth は生成される実験プログラムそのものである。

この原則から次の帰結が得られる:

1. **同一 annotation が複数カテゴリに属し得る場合、生成プログラムが
   同一なら、どちらの分類も有効である。**
   例えば `@body_weight(80%)` を Subjects（確立操作としての絶食水準）と
   解釈するか、Procedure（セッション前操作）と解釈するかは、生成される
   実験プログラムが同一である限り問題とならない。学派による分類観の
   違いは許容される。

2. **重複や両立不能性の検出はプログラム側の責任である。**
   DSL 自身は annotation 間の論理的衝突を judge しない。各プログラムが
   自身のルールに照らして衝突を検出し、コンパイルエラーまたは
   パースエラーとして拒否する。これにより DSL は学派論争から中立を
   保てる。

3. **カテゴリ拡張に DSL 側の制約はない。**
   3rd-party は自由に新カテゴリを定義し、既存カテゴリを無視または
   再定義できる。拡張のために本家 DSL の改訂を要求する仕組みは
   用意しない。annotation の重複や両立性の責任は、それを受け取る
   プログラム側が負う。

### 4.4 推奨分類に含まれない領域（拡張可能性の例示）

JEAB Method 節の構造に直接対応しないが、将来的に 3rd-party によって
拡張されうる領域を例示する。以下は **形式的予約ではなく、拡張可能性の
例示** である。§4.2 の原則により、これらはいずれも Core DSL の変更なしに
定義可能である。

- **臨床関連** — FBA 結果、介入の臨床的分類ラベル（DRA / DRI / NCR 等）、
  社会的妥当性。応用行動分析の実務で必要となる場合がある。
- **派生的関係関連** — 派生的関係反応の事前予測、文脈手がかりの
  機能的役割（Crel / Cfunc）、Baseline / Probe / Test 区別。刺激等価性や
  関係フレーム理論を扱う手続きで必要となる場合がある。
- **Provenance メタデータ** — author・version・date・修正履歴等、
  手続きの外側にある文書管理情報。
- **ドメイン固有拡張** — 行動薬理・神経科学・社会的行動等、特定の
  研究領域が必要とする情報。

## 5. Schedule Extension 層 — 動的・TC 近傍の schedule 構成素

### 5.1 Annotation とは別次元の拡張機構

Annotation 層は **metadata**（手続きに付加する情報）を扱う層である。しかし
実験手続きには、metadata ではなく **schedule 構造そのものの拡張** が必要な
ものも存在する。代表例は次の通り:

- **Percentile schedules** (Platt, 1973; Galbicka, 1994) — 反応分布の Nth
  percentile を動的に算出し、それを下回る反応のみを強化する。閾値が
  schedule の一部として時々刻々変化する。
- **Adjusting schedules / titration** — 被験体の反応履歴に応じて schedule
  パラメータを動的に変化させる。遅延割引研究の indifference point 探索等で
  使用される。
- **Conjugate reinforcement** — 反応量に比例して強化子が連続的に提示される。
  反応と強化の関係が離散的な schedule event ではない。

これらは **metadata ではなく schedule 構造そのもの** であり、§4 の annotation
境界原則（§2 の「annotation はコアの意味を変えない」）に抵触する。一方で、
**TC 近傍**（動的計算・状態保持・履歴参照が必要）の性質を持つため、Core DSL の
CFG / 非 TC 方針にもそのまま組み込むことはできない。

この「Core に含められない、かつ annotation でもない」構成素を収容するため、
本 DSL は **Schedule Extension 層** を第 3 のレイヤーとして定義する。

### 5.2 Schedule Extension の位置付け

| 層 | 役割 | closure | 例 |
|---|---|---|---|
| Core | 不変の schedule 基盤 | 全プログラム共通 | `FR5`, `Conc(VI30, VI60)`, `Chain(FR5, FI30)` |
| **Schedule Extension** | schedule 文法の拡張（動的・TC 近傍） | program-scoped | `Percentile(target="IRT", n=50)`, `Adjusting(start=FR1, step="titrate")` |
| Annotation | metadata | program-scoped | `@reinforcer`, `@species`, `@chamber` |

Schedule Extension は annotation と並ぶ **第 2 の program-scoped 拡張次元**
だが、役割が異なる:

- **Annotation** は schedule 式に付加情報を載せる（metadata）
- **Schedule Extension** は schedule 式そのものの**新 construct を追加する**
  （grammar-level）

### 5.3 Schedule Extension の性質

1. **Core 文法は不変のまま**
   Schedule Extension は Core の文法生成規則を追加する形で実現されるが、
   Core 既存ルールを書き換えない。新 extension をロードしないプログラムでは
   その構成素は未知語として parse error になる。

2. **Program-scoped closure**
   各プログラム（runtime / interpreter）は自身の extension registry を持つ。
   プログラム A が `Percentile` を解釈できても、プログラム B は解釈できない
   場合がある。両プログラムとも Core 部分は同一の parser で処理できる。

3. **静的検証の境界**
   Core 内の schedule 構造は完全に静的検証可能（reachability, dead code 等）。
   Schedule Extension は各 extension モジュールが自身の検証規則を提供する。
   Core + 特定プログラムの extension registry の組で、決定可能な静的検証範囲が
   定まる。

4. **TC 境界の保護**
   Schedule Extension モジュールが TC 近傍の機能（動的計算、状態、履歴）を
   導入することは許容される。**Core が TC を持ち込まない** ことが重要であり、
   extension 層への TC 機能の委譲は方針と整合する。

5. **等価性判定は extension の責務**
   同一 Schedule Extension 構成素の等価性（例: 2 つの `Percentile` 式が等価か）
   は extension モジュールが判定ルールを提供する。Core 側の等価性規則は
   extension 構成素に対して適用されない。

### 5.4 Annotation との境界

「それは annotation か、Schedule Extension か」の判定基準:

| 問い | Annotation | Schedule Extension |
|---|---|---|
| 手続きの structure を変えるか | No（metadata のみ） | Yes（新 schedule 構成素） |
| 動的な計算・状態保持を要するか | No（静的宣言のみ） | Yes の場合が多い |
| Core 既存の schedule 式の評価結果を変えるか | No | Yes（新しい評価を導入する） |
| Source の構文位置 | 式に後置（`FR5 @name(...)`） | 式そのものの形（`Name(...)`） |

Percentile schedule は「DRL の閾値を動的に計算する」ものであり、**schedule 式の
評価結果を変える**ため annotation では扱えない。独自の構成素として Schedule
Extension 層に属する。

一方 `@reinforcer("food")` は、schedule の評価には影響しない metadata の
付加であり、annotation 層に属する。

### 5.5 3rd-party による拡張

プログラムは自由に Schedule Extension モジュールを作成・ロード・省略できる:

- ある研究室が独自の `TitrationSchedule(...)` を定義してプログラムに組み込む
- 別の研究室が全く異なる設計の `AdaptiveFR(...)` を定義する
- 基本的な実験のみ行うプログラムは extension を一切ロードしない

いずれも Core DSL の変更は不要である。design-philosophy §4.2 の
program-scoped closure 原則が、schedule 文法レベルにまで拡張されていると
考えればよい。

### 5.6 本 DSL プロジェクトの Schedule Extension 候補

本 DSL プロジェクトは当面 Schedule Extension を**提供しない**。将来的に
必要性が明確になれば推奨 extension モジュールとして整備する候補:

- `percentile-extension` — Platt (1973) / Galbicka (1994) の percentile schedules
- `adjusting-extension` — 遅延割引等の titration 手続き
- `conjugate-extension` — Rovee-Collier 系の連続強化手続き

これらはいずれも v1.0 Core 凍結後の追加候補であり、design-philosophy §8.1 の
additive extension 手順に従って追加する。

## 6. 実装言語戦略

**Python と Rust の両方を初期から並立実装する。**

- **Python:** 研究者・教育・分析パイプラインとの親和性
- **Rust:** HIL・タイミング保証・組み込み・速度

この二言語並立は、DSL が「特定ランタイムの方言」に堕ちることを防ぐ
構造的な歯止めとして機能する。単一の spec（grammar / AST schema /
annotation 定義）が両実装を駆動できなければならない。

**含意:** 言語非依存性（language independence）は本 DSL の実質的要件である。
Annotation の値表現を特定言語の型システムに依存させる設計は許容しない。

## 7. 近期ゴールと後回しにできること

### 7.1 近期ゴール

- **現行の実験手続きを理論上 DSL に記述できる**状態に到達する。
- Core 文法の堅牢性を確保し、これ以降の破壊的変更を不要にする。
- Python / Rust 両実装が同じ仕様から駆動される体制を確立する。

### 7.2 後回しにできること

以下は DSL の基盤が堅牢であれば、いつでも着手できる。
基盤確立が先で、これらは優先度を下げる:

- 「`FR5` と書いたらシミュレータがデータを吐く」等のランタイム統合
- 論文の図の再現パイプライン
- 学生向け教材・チュートリアル

## 8. 破壊的変更の回避と例外条件

Core 文法に対する破壊的変更は **原則として避ける**。ただし §2 で述べた通り、
Core の安定性は経験的観察に基づくものであり、絶対的な保証ではない。
したがって例外条件を明示的に認める。

### 8.1 通常時の手順

1. 新たな実験手続きを表現する必要が生じた場合、次の順で検討する:
   a. **Annotation 層で吸収できるか**（metadata 層、§4）
   b. **Schedule Extension 層で吸収できるか**（新 schedule 構成素、§5）
   c. Core 文法への追加を検討（最終手段）
2. Core への追加が必要な場合は **additive only**（既存の構文・意味を
   変更しない）とする。

### 8.2 例外として破壊的変更が許される条件

次のいずれかに該当する場合、破壊的変更を検討してよい:

- **学派的基礎の崩壊**: 三項随伴性または強化スケジュールの概念そのものが、
  将来の理論的発展によって成立しないと判明した場合。
- **Core 文法の重大な誤り**: 現在の Core 文法が、表現しようとしている
  行動分析学的概念を正しく反映できていないと判明した場合。
- **追加では原理的に吸収不能**: Annotation でも Schedule Extension でも
  additive only でも表現できない構造的問題が発見された場合。

### 8.3 破壊的変更時の義務

破壊的変更が避けられないと判断された場合:

1. メジャーバージョンを上げる。
2. 変換ツールを同時に提供し、旧バージョンで書かれた DSL を新バージョンに
   機械的に移行可能にする。
3. 変更の動機を本文書（§8.2 のいずれに該当するか）に照らして記録する。

---

## 本文書と他 spec との関係

本文書は「設計の *なぜ*」を述べる上位文書であり、以下の spec 群の上位に位置する:

- [grammar.ebnf](../../grammar.ebnf) — Core 文法
- [ast-schema.json](../../ast-schema.json) — 抽象構文木のスキーマ
- [annotation-design.md](../annotation-design.md) — Annotation 境界原則と AnnotationModule Protocol
- [validation-modes.md](../validation-modes.md) — Tier × Mode による検証体系
- [representations/DESIGN.md](../../representations/DESIGN.md) — 代替座標系の設計

いずれかの spec が本文書と矛盾する場合、**本文書が正典として優先する**。
矛盾を発見した場合は該当 spec を改訂するか、本文書との関係を注記すること。

---

## Provenance

本文書は 2026-04-12 にプロジェクトオーナーから述べられた設計意図を、
その場で直接文章化したものである。文言は原発話を極力保存する方針で
編集されており、解釈の追加は最小限にとどめている。
