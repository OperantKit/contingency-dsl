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
この目標を達成するため、**Foundations + Operant + Respondent 文法の
安定性を最重要視し、破壊的変更を必要としない設計を追求する**（詳細は §2
および §8 を参照）。

## 2. 経験的に安定な基礎 — 科学的カテゴリによる六層構造

実験的行動分析の歴史は、多少の理論解釈や刺激解釈の違いはあれど、
**三項随伴性の基礎と強化スケジュールはこれまで破綻することなく、学派として
安定な基礎を成してきた**。この経験的に観察される安定性を、DSL の設計に反映する。

ただしこの安定性は **経験的観察に基づく現在の状態** であり、絶対的な保証では
ない。学派自体が将来崩壊する可能性も原理的にはあり、その場合には基盤層にも
例外的な変更が必要となりうる。本 DSL は「現在のところ最も安定な層」を
基盤として固定するのであって、「永久不変の真理」を主張するものではない。

本 DSL は **抽象的な技術軸ではなく科学的カテゴリ** によって構造化される。
主たる利用者は実験的行動分析（EAB）の研究者および学生であり、主たる
カバー範囲は JEAB に掲載される手続きである。したがって operant 手続きが
中心的な分量を占め、respondent 手続きは必要最低限にとどめ、それ以上の
深さは拡張パッケージ（`contingency-respondent-dsl`）に委譲する。

本 DSL は次の **六層構造** を取る:

| 層 | 内容 | 変化の許容度 |
|---|---|---|
| **Foundations（paradigm-neutral 形式基盤）** | CFG/LL(2) 形式文法、contingency 型論（contingent vs non-contingent、二項 vs 三項）、時間スケール、刺激型付け（SD, SΔ, CS, US, Sr+, Sr−）、valence 軸（appetitive/aversive）、context。基準はパース時にリテラル値で確定。CFG + 非TC。 | 破壊的変更は原則として避ける（例外は §8 参照） |
| **Operant（三項随伴性: SD-R-SR）** | 伝統分類（ratio / interval / time / differential / compound / progressive）による強化スケジュール、stateful operant スケジュール（Percentile, Adjusting, Interlocking）、trial-based operant スケジュール（MTS, Go/NoGo）。パラメータは宣言的（リテラル値またはランタイム算出）。 | §8.1 additive 手順 + §2.1 admission gate（stateful / trial-based の拡張について） |
| **Respondent（二項随伴性: CS-US）** | 最低限の Pavlovian primitives: `Pair.{ForwardDelay, ForwardTrace, Simultaneous, Backward}`、`Extinction`、`CSOnly`、`USOnly`、`Contingency(p_us_given_cs, p_us_given_no_cs)`、`TrulyRandom`、`ExplicitlyUnpaired`、`Compound`、`Serial`、`ITI`、`Differential(cs+, cs−)`。3rd-party 追加のための Tier-A 級 extension point を含む（§5）。この最低限を超える深さは `contingency-respondent-dsl` に委譲。 | Additive only；新 primitive は §2.1 admission 基準を満たす必要がある |
| **Composed（operant × respondent）** | operant ベースラインと respondent ペアリングを組み合わせた合成手続き: conditioned suppression (CER)、Pavlovian-to-Instrumental Transfer (PIT)、autoshaping、omission（negative automaintenance）、two-process theory。operant + respondent 文法だけでは表現できない合成手続きが追加対象。 | Additive；既存の合成手続きは意味的に変更しない |
| **Experiment（宣言的フェーズ構造）** | 多フェーズ実験デザイン。Core の ScheduleExpr ノードを、宣言的なフェーズ変更基準（Stability, FixedSessions, PerformanceCriterion 等）とともに順序付きフェーズに編成する。JEAB 慣習に準拠: 共有アノテーションはフェーズ間で継承、フェーズ単位で override 可。Phase と Context は first-class 構成素。`schema/experiment/` 参照。 | Additive（新 Criterion 型の追加可）。他層のスキーマは変更しない |
| **Annotation（metadata、program-scoped）** | 拡張理論・詳細手続き・解釈依存の付加情報。標準カテゴリは JEAB Method 節に準拠（Subjects / Apparatus / Procedure / Measurement）。拡張（例: `@cs`, `@us`, `@iti`, `@cs_interval` を提供する `respondent-annotator`、`@model(RW/PH/TD)` を提供する `learning-models-annotator`）は `annotations/extensions/` 配下。 | 理論の発展・衰退に追従して自由に増減。program-scoped |

**Foundations**、**Operant**、**Respondent**、**Composed**、**Experiment** は
いずれも**全プログラム共通**の共有語彙である。Operant 層内部の構造的
区別は維持される: リテラル基準の operant スケジュール（`FR 5`: 基準 =
5反応）、ランタイム状態から算出される基準を持つ operant スケジュール
（`Pctl(IRT, 50)`: 基準 = 直近 IRT 分布の中央値）、operant trial-based
スケジュール。詳細は §2.1 を参照。

**Annotation**（`respondent-annotator` などの拡張を含む）は **program-scoped**
で、各プログラムが独自の registry を定義・採用・拒否できる。Annotation
層に加えて、**Respondent 文法への 3rd-party 拡張** も respondent extension
point（§5）を通じてサポートされる。本プロジェクトにおける代表例は、
higher-order conditioning、blocking、overshadowing、latent inhibition、
renewal、reinstatement などの Tier-B primitive を提供する伴走パッケージ
`contingency-respondent-dsl` である。

### 2.1 Operant.Stateful 昇格ゲート

`operant/stateful/` サブ層は、**学派で確立された**が強化基準の評価に
ランタイム状態を必要とする三項随伴性スケジュールを収容する。Operant
層の他の部分と同じく全プログラム共通の共有語彙であるが、評価に関する
静的決定可能性はリテラル基準の Operant スケジュールの完全な決定可能性
とは異なる。

**Operant 層内部の構造的区別:**

| 性質 | Operant.Literal (`operant/schedules/`) | Operant.Stateful (`operant/stateful/`) |
|---|---|---|
| 構文 | CFG | CFG |
| パラメータ | リテラル値（パース時確定） | リテラル値（パース時確定） |
| 強化基準 | リテラル値と比較 | ランタイム状態から算出した値と比較 |
| 構造的等価性 | 決定可能 | 決定不能（分布依存） |
| 通用範囲 | 全プログラム共通 | 全プログラム共通 |

**Admission gate:** スケジュールが Operant.Stateful に昇格するためには、
(1) 以下の学派確立基準を充足し、
(2) 全パラメータが宣言的（パース時にリテラル値で確定）であることが必要。

学派確立基準:
- **N1（命名された手続き）:** 複数の独立した研究グループが同一の名称を使用。
- **N2（一次文献）:** 再現可能な精度の操作的定義を含む査読付き出版物が存在。
- **N3（時間的持続）:** 初出から 20 年以上経過し、非重複の 2 デカード以上で出版物あり。
- **証拠スコア ≥ 3/5:** (E1) JEAB/JABA 掲載、(E2) EAB/ABA 文脈での研究室横断再現、
  (E3) 教科書記載、(E4) パラメトリック研究 or 理論的統合、
  (E5) ヒト被験者対象の応用/翻訳的使用。

**昇格プロセス:** スケジュールを Operant.Stateful に昇格させる際は、以下の手順に従う。

1. **提案:** 昇格候補を RFC として spec/ja/ に提出する。RFC には
   (a) 対象スケジュールの操作的定義、(b) N1-N3 + E1-E5 の充足根拠（引用付き）、
   (c) パラメータが宣言的であることの確認、(d) 提案する構文（grammar 追記案）を含める。
2. **査読:** プロジェクトオーナーが RFC を承認する。判断に迷う場合は
   eab-researcher エージェントに学派確立基準の充足度を検証させ、
   pl-theorist エージェントに構文の文法的整合性を検証させる。
3. **実装:** 承認後、`schema/operant/stateful/grammar.ebnf` への生成規則追加、
   ast-schema.json への AST ノード追加、Python / Rust 両実装のパーサ更新を
   §8.1 の additive 手順に従って行う。
4. **記録:** 昇格を本節の構成素テーブルに追記し、§5.7 の候補リストから除去する。

**現在の Operant.Stateful 構成素:**

| スケジュール | 初出 | 基準 = f(?) |
|---|---|---|
| Percentile (`Pctl`) | Platt (1973); Galbicka (1994) | f(反応履歴) |
| Adjusting (`Adj`) | Blough (1958); Mazur (1987) | f(試行結果) |
| Interlocking | Ferster & Skinner (1957) | f(経過時間、連続関数) |

## 3. 使い手の構造

使い手は層によって異なる。この区別を混同してはならない。

### 3.1 DSL の使い手

**研究者・学生・そして「共通言語として利用する者」すべて。**

`FR 5`, `Chain(FR 5, FI 30-s)`, `Conc(VI 30-s, VI 60-s)` のような記述は、
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

Annotation は DSL の補足機構として、実験手続きに関する付加情報を担う。
本節では annotation のカテゴリ体系、およびカテゴリが「推奨分類」であって
強制ではないという原則を定める。

Annotation 層自身も拡張可能である。下記の 4 つの JEAB カテゴリ annotator に
加え、`annotations/extensions/` にはこれら 4 カテゴリに収まらない annotator
パッケージが配置される。本 DSL プロジェクトは次の 2 つの拡張を同梱する:

- **`respondent-annotator`**（新設） — `@cs`、`@us`、`@iti`、`@cs_interval`
  を提供し、合成 operant × respondent 手続きが respondent 層 primitive の
  最小形式で表現される場合にも注釈できるようにする。§5 および
  `annotations/extensions/respondent-annotator.md` 参照。
- **`learning-models-annotator`** — `@model(RW/PH/TD)` を提供し、schedule 式を
  連合学習モデル仕様と関連付ける。

### 4.1 推奨カテゴリ体系（JEAB Method 節に準拠）

Annotation は以下のカテゴリに分類することを推奨する。カテゴリ名は JEAB の
Method 節の伝統的区分（Subjects / Apparatus / Procedure）に準拠し、
行動分析学の読み手が馴染みのある構造を保つ。Measurement は測定基準の
独立性を担保するため別カテゴリとして分離する。

| カテゴリ | 推奨 annotator | 対象 | 主な目的 |
|---|---|---|---|
| **Procedure** | `procedure-annotator` (stimulus + temporal + context sub-annotators) | 手続きの記述 | (1) 暗黙的な手続きの明文化, (2) 二つの手続きの等価性判定の支援, (3) DSL と実験プログラムの相互変換に必要な条件の補足 |
| **Subjects** | `subjects-annotator` | 被験体 | 被験体履歴・確立操作・絶食水準・種・状態の記述。現在の随伴性が同一でも行動が異なる要因を記録する。 |
| **Apparatus** | `apparatus-annotator` | 装置・物理実装 | Chamber・operandum・HW 仕様・タイミング許容誤差・物理量の束縛等、DSL の抽象を物理世界に接地させる情報。 |
| **Measurement** | `measurement-annotator` | 測定基準 | 安定性基準・基底率・phase 終了条件・dependent measures 等、Core の随伴性効果を *いつ・どう読み取るか* を規定する情報。 |

Annotator 名と JEAB カテゴリは **1:1 で対応** する
（[annotation-design.md §3.7](annotation-design.md) 参照）。annotator 名を
見れば属するカテゴリが即座にわかる。JEAB 4 カテゴリに収まらない annotator は
`annotations/extensions/` 配下に置かれる。

Procedure カテゴリの 3 目的（明文化・等価性判定・相互変換補足）は、本 DSL が
当初から annotation に求めてきた中核的役割であり、他カテゴリはこれを
補完する位置付けにある。

### 4.2 カテゴリは *推奨分類* であって強制ではない

§4.1 のカテゴリ体系は DSL プロジェクトから公開される **推奨分類** である。
DSL 文法はカテゴリの存在を知らず、annotation の実際のカテゴリ判定は
annotation registry と各プログラム（runtime / interpreter）が行う。

したがって **カテゴリの追加・削除・無視・再定義は、DSL 文法の変更を
伴わない**。この性質により:

- ある 3rd-party プログラムが「環境条件は外部で管理するので DSL 側では
  扱わない」と決めた場合、Apparatus カテゴリの annotation を黙って
  無視する実装が可能である。DSL 文法は一切変更不要。
- 別の研究グループが独自のカテゴリ（例: 派生的関係・臨床分類等）を
  定義して自身のプログラムに載せることが可能である。本家 DSL の改訂を
  待つ必要はない。
- 対立理論を扱うプログラムは、既存カテゴリを再解釈または置換できる。

このアーキテクチャにより、**DSL 文法の破壊や再生成なしに、プログラム
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

3. **カテゴリ拡張に文法側の制約はない。**
   3rd-party は自由に新カテゴリを定義し、既存カテゴリを無視または
   再定義できる。拡張のために DSL 文法の改訂を要求する仕組みは
   用意しない。annotation の重複や両立性の責任は、それを受け取る
   プログラム側が負う。

### 4.4 推奨分類に含まれない領域（拡張可能性の例示）

JEAB Method 節の構造に直接対応しないが、将来的に 3rd-party によって
拡張されうる領域を例示する。以下は **形式的予約ではなく、拡張可能性の
例示** である。§4.2 の原則により、これらはいずれも DSL 文法の変更なしに
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

## 5. 文法レベル拡張点 — Schedule Extension と Respondent Extension

DSL は **文法レベルの拡張点を 2 つ** 提供する: Operant 層内部の
Schedule Extension と、Respondent 層内部の Respondent extension point
である。いずれも Annotation 層（§4.2）と同じ program-scoped closure
原則に従うが、metadata レベルではなく文法レベルで動作する。

### 5.1 Schedule Extension — 未標準化・ユーザー定義の operant schedule 構成素

Annotation 層は **metadata**（手続きに付加する情報）を扱う層である。
Operant.Stateful admission gate（§2.1）は、学派で確立された
**状態依存基準を持つ三項随伴性スケジュール** を扱う。しかし operant
実験手続きには、これらの層に収まらない **schedule 構造そのものの拡張**
が必要なものも存在する。代表例:

- **Conjugate reinforcement** — 反応量に比例して強化子が連続的に提示される。
  反応と強化の関係が離散的な schedule event ではない。§2.1 の学派確立
  基準 E2（研究室横断再現）が未充足。
- **研究室独自のスケジュール** — 未標準化のため §2.1 の命名基準（N1）や
  時間的持続基準（N3）を充足しない構成素。
- **パラメータが計算式のスケジュール** — パラメータ値自体がリテラルで
  なく式であるスケジュール。

この「Operant.Literal にも Operant.Stateful にも属さず、かつ
annotation でもない」構成素を収容するため、DSL は Operant 層内部に
**Schedule Extension 点** を定義する。

### 5.2 Schedule Extension の位置付け

| 層 | 役割 | closure | 例 |
|---|---|---|---|
| Operant.Literal (`operant/schedules/`) | 不変の schedule 基盤（リテラル基準） | 全プログラム共通 | `FR 5`, `Conc(VI 30-s, VI 60-s)`, `Chain(FR 5, FI 30-s)` |
| Operant.Stateful (`operant/stateful/`) | 確立された状態依存基準のスケジュール | 全プログラム共通 | `Pctl(IRT, 50)`, `Adj(start=FR 1, step=2)` |
| **Schedule Extension**（Operant 文法レベル） | 未標準化・ユーザー定義の operant schedule 構成素 | program-scoped | 研究室独自スケジュール、conjugate reinforcement |
| Annotation | metadata | program-scoped | `@reinforcer`, `@species`, `@chamber` |

Schedule Extension は annotation と並ぶ **第 2 の program-scoped 拡張次元**
だが、役割が異なる:

- **Annotation** は schedule 式に付加情報を載せる（metadata）
- **Schedule Extension** は operant schedule 式そのものの **新 construct を
  追加する**（grammar-level）

### 5.3 Schedule Extension の性質

1. **Operant 文法は不変のまま**
   Schedule Extension は Operant の文法生成規則を追加する形で実現されるが、
   既存ルールを書き換えない。新 extension をロードしないプログラムでは
   その構成素は未知語として parse error になる。

2. **Program-scoped closure**
   各プログラム（runtime / interpreter）は自身の extension registry を持つ。
   プログラム A が `Percentile` を解釈できても、プログラム B は解釈できない
   場合がある。両プログラムとも Operant 部分は同一の parser で処理できる。

3. **静的検証の境界**
   Operant 層内の schedule 構造は完全に静的検証可能（reachability,
   dead code 等）。Schedule Extension は各 extension モジュールが自身の
   検証規則を提供する。Operant + 特定プログラムの extension registry の
   組で、決定可能な静的検証範囲が定まる。

4. **TC 境界の保護**
   Schedule Extension モジュールが TC 近傍の機能（動的計算、状態、履歴）を
   導入することは許容される。**Foundations + Operant 層が TC を持ち込まない**
   ことが重要であり、extension 層への TC 機能の委譲は方針と整合する。

5. **等価性判定は extension の責務**
   同一 Schedule Extension 構成素の等価性（例: 2 つの `Percentile` 式が等価か）
   は extension モジュールが判定ルールを提供する。core 側の等価性規則は
   extension 構成素に対して適用されない。

### 5.4 Respondent Extension Point

Respondent 層（`respondent/`）には §2 に列挙した Tier-A Pavlovian
primitive のみを置く: `Pair.{ForwardDelay, ForwardTrace, Simultaneous,
Backward}`、`Extinction`、`CSOnly`、`USOnly`、
`Contingency(p_us_given_cs, p_us_given_no_cs)`、`TrulyRandom`、
`ExplicitlyUnpaired`、`Compound`、`Serial`、`ITI`、
`Differential(cs+, cs−)`。これ以上の深い Pavlovian 手続き空間
（blocking、overshadowing、latent inhibition、conditioned inhibition、
reinstatement、renewal、spontaneous recovery、counterconditioning、
occasion-setting など）はこの最小集合の外に配置し、伴走パッケージ
`contingency-respondent-dsl` に委譲する。

Respondent 層の文法を書き換えずにこの委譲を可能にするため、
`respondent/grammar.md` は専用の extension point を定義する:

```ebnf
RespondentExpr ::=
      CoreRespondentPrimitive           (* Tier A, §2 *)
    | ExtensionRespondentPrimitive       (* 3rd-party, program-scoped *)

ExtensionRespondentPrimitive ::=
      Identifier "(" ArgList? ")"        (* respondent registry で解決 *)
```

Respondent extension point の性質は Schedule Extension の §5.3 を
鏡映する:

1. **Respondent 文法は不変のまま。** extension はルールを追加するのみで
   書き換えない。
2. **Program-scoped closure。** 各プログラムの respondent registry が
   どの extension primitive を認識するかを決める。
3. **静的検証の境界。** Tier-A primitive は完全に静的検証可能であり、
   extension primitive は自身のルールを提供する。
4. **TC 境界の保護。** extension はランタイム状態を消費してよいが、
   Respondent 層自体は TC を持ち込まない。
5. **等価性判定は extension の責務。**

### 5.5 Annotation / Schedule Extension / Respondent Extension の境界

どの拡張点を使うかの判定基準:

| 問い | Annotation | Schedule Extension | Respondent extension |
|---|---|---|---|
| 手続きの structure を変えるか | No（metadata のみ） | Yes（新 operant-schedule 構成素） | Yes（新 CS–US primitive） |
| 三項随伴性（SD-R-SR）に関わるか | 参照することはある | Yes | No — 二項（CS-US） |
| §2.1 の学派確立基準を充足しているか | （該当しない — metadata は昇格対象外） | No（充足すれば Operant.Stateful 昇格候補） | （該当しない — respondent の深さは `contingency-respondent-dsl` に委譲） |
| 既存 Operant 式の評価結果を変えるか | No | Yes | （該当しない — respondent 式に対する操作） |
| Source の構文位置 | 式に後置（`FR 5 @name(...)`） | operant-式そのものの形（`Name(...)`） | respondent-式そのものの形（`Name(...)`） |

Percentile schedule は「DRL の閾値を動的に計算」し、**operant schedule 式の
評価結果を変える**ため annotation では扱えない。Schedule Extension 点
の構成素として属する。

Blocking 手続きは新しい **CS–CS→US 構造関係** を導入する; これは
respondent 文法の構成素であり、Respondent extension point に属し、
Schedule Extension にも Annotation 層にも属さない。

一方 `@reinforcer("food")` は schedule の評価には影響しない metadata の
付加であり、Annotation 層に属する。

### 5.6 3rd-party による拡張

プログラムはいずれの extension point でも自由に拡張モジュールを作成・
ロード・省略できる:

- ある研究室が独自の `TitrationSchedule(...)`（Schedule Extension）を
  定義してプログラムに組み込む
- 別の研究室が全く異なる設計の `AdaptiveFR(...)` を定義する
- 伴走パッケージ `contingency-respondent-dsl` が Respondent extension
  point 経由で `Blocking(...)`、`Overshadow(...)`、
  `LatentInhibition(...)`、`Renewal(...)`、`Reinstatement(...)` 等を
  登録する
- 基本的な実験のみ行うプログラムは extension を一切ロードしない

いずれも DSL 文法の変更は不要である。§4.2 の program-scoped closure 原則が、
Operant 層と Respondent 層の両方について文法レベルにまで拡張されている
と考えればよい。

### 5.7 本 DSL プロジェクトが現状提供しない拡張候補

本 DSL プロジェクトは当面 Schedule Extension を **自ら提供しない**。
Percentile および Adjusting は §2.1 の学派確立基準充足により
Operant.Stateful に昇格した。残る Schedule Extension 候補:

- `conjugate-extension` — Rovee-Collier 系の連続強化手続き（昇格基準 E2
  未充足）
- `yoked-extension` — Yoked 統制手続き（Church, 1964）。被験体間の強化
  パラメータ参照を要するため、単一プログラムスコープの Operant では表現
  できない。social-annotator 等の multi-subject 拡張層で対応する。

これらの候補は admission 時に §8.1 の additive extension 手順に従う。
admission 自体はバージョン更新を意味しない。

`contingency-respondent-dsl` が提供する Respondent 拡張候補（Tier B）
には、second-order conditioning、sensory preconditioning、blocking、
overshadowing、latent inhibition、conditioned inhibition /
feature-negative discrimination、occasion-setting、US preexposure
effect、reinstatement、renewal（ABA / ABC / AAB）、spontaneous
recovery、counterconditioning、overexpectation、super-conditioning、
contextual extinction、retrospective revaluation / backward blocking、
mediated conditioning、conditioned taste aversion、Pavlovian stimulus
generalization、reconsolidation interference、Pavlovian partial
reinforcement extinction、peak procedure、contextual fear
conditioning、inhibition of delay、summation / retardation test が
含まれる。

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
- Foundations + Operant + Respondent 文法の堅牢性を確保し、これ以降の
  破壊的変更を不要にする。
- Python / Rust 両実装が同じ仕様から駆動される体制を確立する。

### 7.2 後回しにできること

以下は DSL の基盤が堅牢であれば、いつでも着手できる。
基盤確立が先で、これらは優先度を下げる:

- 「`FR 5` と書いたらシミュレータがデータを吐く」等のランタイム統合
- 論文の図の再現パイプライン
- 学生向け教材・チュートリアル

## 8. 破壊的変更の回避と例外条件

Foundations + Operant + Respondent 文法に対する破壊的変更は **原則として
避ける**。ただし §2 で述べた通り、これらの層の安定性は経験的観察に
基づくものであり、絶対的な保証ではない。したがって例外条件を明示的に
認める。

### 8.1 通常時の手順 — Additive-only 方針

1. 新たな実験手続きを表現する必要が生じた場合、次の順で検討する
   （最初に該当するものを採用する）:
   a. **Annotation 層** — metadata 層、§4
   b. **Schedule Extension**（operant 層の拡張、§5.1–5.3）または
      **Respondent extension point**（respondent 層の拡張、§5.4） —
      手続きが構造的に属する層を選ぶ
   c. **`composed/` への admission** — operant × respondent の合成手続き
      であって `composed/` の admission 基準（`architecture.md` 参照）
      を満たすもの
   d. **新しい Operant または Respondent primitive の追加** — 最終手段
      であり、§2.1 の学派確立基準に従う
2. いずれの追加も **additive only**（既存の構文・意味を変更しない）と
   する。

### 8.2 例外として破壊的変更が許される条件

次のいずれかに該当する場合、破壊的変更を検討してよい:

- **学派的基礎の崩壊**: 三項随伴性、二項随伴性、または強化スケジュールの
  概念そのものが、将来の理論的発展によって成立しないと判明した場合。
- **文法の重大な誤り**: 現在の文法が、表現しようとしている行動分析学的
  概念を正しく反映できていないと判明した場合。
- **追加では原理的に吸収不能**: Annotation、Schedule Extension、
  Respondent extension point、`composed/` への admission、additive-only
  な primitive 追加のいずれでも表現できない構造的問題が発見された場合。

### 8.3 破壊的変更時の義務

破壊的変更が避けられないと判断された場合:

1. git コミットメッセージに変更を記録し、§8.2 のいずれの条件に該当するか、
   および旧構造・新構造を明示する。当リポジトリは現時点で外部公開
   チェックポイントを持たない（git remote 未設定）; git 履歴が正式な記録である。
2. 変換ツールを同時に提供し、直前の設計で書かれた DSL を新しい設計に
   機械的に移行可能にする。
3. 本文書および正典 spec ツリーをそれに応じて更新する。

---

## 本文書と他 spec との関係

本文書は「設計の *なぜ*」を述べる上位文書であり、以下の spec 群の上位に位置する:

- [evaluation-criteria.md](evaluation-criteria.md) — 設計判断を評価する 6 軸（本文書から導出）
- [grammar.ebnf](../../grammar.ebnf) — DSL 文法
- [ast-schema.json](../../ast-schema.json) — 抽象構文木のスキーマ
- [annotation-design.md](annotation-design.md) — Annotation 境界原則と AnnotationModule Protocol
- [validation-modes.md](validation-modes.md) — Tier × Mode による検証体系
- [representations/DESIGN.md](../../representations/DESIGN.md) — 代替座標系の設計

いずれかの spec が本文書と矛盾する場合、**本文書が正典として優先する**。
矛盾を発見した場合は該当 spec を改訂するか、本文書との関係を注記すること。

---

## Provenance

本文書は 2026-04-12 にプロジェクトオーナーから述べられた設計意図を、
その場で直接文章化したものである。文言は原発話を極力保存する方針で
編集されており、解釈の追加は最小限にとどめている。
