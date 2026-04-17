# アノテーション・ガイド

> スケジュール式に実験メタデータを付加する方法。
> アノテーションシステムの設計については [annotations/design.md](../../spec/ja/annotations/design.md) を参照。

---

## 設計チェックポイントにおける annotator の層

注釈システムは 2 階層構成:

1. **JEAB 準拠の 4 推奨 annotator** — `procedure-annotator`、`subjects-annotator`、`apparatus-annotator`、`measurement-annotator`。いずれも JEAB Method 節の見出しと 1:1 対応する。
2. **拡張 annotator**（`annotations/extensions/` 配下）— 4 カテゴリに属さない annotator。本プロジェクトは 2 つを同梱する:
   - `respondent-annotator` — `@cs`、`@us`、`@iti`、`@cs_interval`。レスポンデント primitive および合成手続きの CS/US メタデータを記述する。
   - `learning-models-annotator` — `@model(RW)`、`@model(PH)`、`@model(TD)`。スケジュール式を連合学習モデルと関連づける。

すべての annotator は直積（Cartesian product）で合成可能（Operant 層の規則）。注釈キーワードは互いに素である。

---

## アノテーションとは

アノテーションは、スケジュール式に付加する**オプショナルなメタデータ**。実験を*実行*するために必要な情報（何が強化子か、どのレバーか、どの種か）を宣言するが、スケジュールの*理論的性質*は変更しない。

```
FI 10                          -- 理論的に完結。スキャロップの議論はこれで可能。
FI 10 @reinforcer("pellet")    -- 何が提示されるかが明確になった。
      @operandum("left_lever") -- どこで反応するかが明確になった。
      @subject(species="rat")  -- 誰が被験体かが明確になった。
```

**核心原則:** `FI 10` は常にそれ単体で valid。アノテーションは加法的であり、決して必須ではない。

### 二層スコーピング

アノテーションはプログラム内の2つのレベルに配置できる:

1. **プログラムレベル** — パラメータ宣言（`COD`, `LH` 等）より前。セッション全体のデフォルト: 被験体条件、装置、時間パラメータ。
2. **スケジュールレベル** — 特定のスケジュール式に付加。随伴性ごとの詳細（どのオペランダム、どの弁別刺激）や、プログラムレベルのデフォルトの上書き。

これは科学論文の構造に対応する: **Subjects** と **Apparatus** は **Procedure** の詳細よりも先に記述される。

```
-- プログラムレベル: セッション全体のデフォルト
@species("rat")
@strain("Long-Evans")
@chamber("med-associates", model="ENV-007")
@clock(unit="s")

COD = 2-s

Conc(VI 30-s, VI 60-s)
  @operandum("left_lever", component=1)   -- スケジュールレベル: 成分ごと
  @operandum("right_lever", component=2)
```

同一のアノテーションキーワードが両レベルに現れた場合、スケジュールレベルの値がプログラムレベルのデフォルトを上書きする。

### 漸進的付加と Validation Mode

同じスケジュール式が、理論から出版まで段階的に情報を蓄える。各段階は **validation mode** に対応し、その時点で必要な情報のみを検証する:

| 文脈 | 式 | Validation Mode | Tier |
|------|-----|----------------|------|
| 理論議論 | `FR 5` | `parse` | Tier 0 のみ |
| シミュレーション | + `@clock(unit="s")` `@algorithm(...)` | `dev` | Tier 0-1 |
| 物理実験 | + `@hardware("teensy41")` `@session_end(...)` `@response(...)` `@operandum(...)` | `production` | Tier 0-2 |
| 論文出版 | + `@species(...)` `@strain(...)` `@chamber(...)` `@n(...)` | `publication` | Tier 0-3 |

**核心の保証:** `FR 5` 単体は*すべての*モードで常に通る。parser はアノテーションを決して要求しない。`production` と `publication` の validator が、作業段階に応じて段階的に厳格な要求を課す。

授業での議論のために `FR 5` を書く学生は `@species` や `@response` に遭遇しない。物理装置を接続するとき（Tier 2）、Methods セクションを生成するとき（Tier 3）に初めてそれらの要求が自然に現れる。

Tier と Mode の完全な仕様は [validation-modes.md](../../spec/ja/annotations/validation-modes.md) を参照。

---

## 4つの推奨アノテータ（JEAB 4 カテゴリに対応）

contingency-dsl プロジェクトは、JEAB Method 節の伝統的な 4 区分（Procedure /
Subjects / Apparatus / Measurement）と **1:1 で対応する 4 つの推奨アノテータ**
を提供する。アノテータ名は JEAB 見出しと一致するように選ばれている。

| JEAB カテゴリ | Annotator | Keywords |
|---|---|---|
| Procedure | `procedure-annotator` (stimulus + temporal + context sub) | `@reinforcer`, `@sd`, `@brief`, `@clock`, `@warmup`, `@algorithm`, `@iti`, `@post_blackout`, `@context` |
| Subjects | `subjects-annotator` | `@species`, `@strain`, `@deprivation`, `@history`, `@n` |
| Apparatus | `apparatus-annotator` | `@chamber`, `@operandum`, `@interface`, `@hardware` (alias: `@hw`), `@feeder` |
| Measurement | `measurement-annotator` | `@session_end`, `@baseline`, `@steady_state` |

これらは DSL プロジェクトが提示する推奨集合であり、プログラム（runtime /
interpreter）は自由に採用・拡張・置換できる（詳細は
[design-philosophy.md §4.2](../../spec/ja/design-philosophy.md) を参照）。

### 1. procedure-annotator/stimulus — どの刺激が関与するか?

刺激の**同一性と機能**を宣言する。

| キーワード | 目的 | 例 |
|-----------|------|-----|
| `@reinforcer` | 強化子の宣言（基本形） | `@reinforcer("food", type="unconditioned", access_duration=3)` |
| `@sd` | 弁別刺激の同定 | `@sd("red_light", component=1)` |
| `@brief` | 二次スケジュールの短時間刺激 | `@brief("light", duration=2)` |

**`@reinforcer` の別名:** `@punisher` と `@consequentStimulus` は `@reinforcer` の
等価な alias。実験者の意図を source に明示したい場合に使用する（例:
`FR 3 @punisher("shock")`）。AST レベルでは 3 者とも同一ノードに collapse され、
等価性判定に影響しない。詳細は
[annotations/design.md §3.5](../../spec/ja/annotations/design.md) を参照。

**例: 成分を同定した並立スケジュール**

```
Conc(VI 30-s, VI 60-s, COD=2-s)
  @operandum("left_lever", component=1)
  @operandum("right_lever", component=2)
  @reinforcer("sucrose", concentration="10%", duration=3)
  @sd("red_light", component=1)
  @sd("green_light", component=2)
```

**これにより可能になること:**
- 各 `Conc` 成分にオペランダムが割り当てられているか検証できる（参照整合性）
- コンパイル結果: *「2つの反応レバーが利用可能であった。左レバー（赤色光）は VI 30秒、右レバー（緑色光）は VI 60秒で動作した。強化子は 10%ショ糖溶液への3秒間アクセスであった。」*

**`@reinforcer` の `access_duration` パラメータ:** 強化子アクセス時間（ホッパーが上昇位置にある秒数、ペレットへのアクセス時間）は強化子の属性として `@reinforcer` が所有する。Ferster & Skinner (1957) は 4 秒のホッパーアクセスを標準としたが、スケジュール表記には含めなかった。この暗黙パラメータを明示することで再現性を保証する。

**ここに属さないもの:**
- 刺激の物理的仕様（LED 波長、音のデシベル）→ apparatus-annotator
- セッションレベルの時間構造（ITI、ウォームアップ、ブラックアウト）→ procedure-annotator/temporal
- 強化子提示装置の物理的制約（minimum IRI）→ apparatus-annotator（`@feeder`）
- 条件性刺激の学習履歴 → ランタイム状態であり宣言ではない

**引用:**
- Kelleher, R. T. (1966). Conditioned reinforcement in second-order schedules. *JEAB*, *9*, 475. https://doi.org/10.1901/jeab.1966.9-475（条件性強化子として機能する brief stimulus）

---

### 2. procedure-annotator/temporal — 時間はどう構造化されるか?

再現性に影響する**セッションレベルの時間パラメータ**を宣言する。

| キーワード | 目的 | 例 |
|-----------|------|-----|
| `@clock` | 時間単位の宣言 | `@clock(unit="s")` |
| `@warmup` | セッション前のウォームアップ期間 | `@warmup(duration=60)` |
| `@algorithm` | スケジュール値生成アルゴリズム | `@algorithm("fleshler-hoffman", n=12)` |
| `@iti` | 試行間間隔（Inter-Trial Interval） | `@iti(duration=10)` |
| `@post_blackout` | 強化後ブラックアウト（強化子アクセス終了後の非活性期間） | `@post_blackout(duration=2)` |

注: `@blackout` と `@cod` は当初 temporal annotation として提案されたが、随伴性構造に直接影響するため**コア文法にキーワード引数として昇格済み**（`BO=5-s`, `COD=2-s`）。

**例: 完全な時間仕様の VI スケジュール**

```
VI 30-s
  @clock(unit="s")
  @algorithm("fleshler-hoffman", n=12, seed=42)
  @warmup(duration=60)
  @iti(duration=10)
  @post_blackout(duration=2)
```

**これにより可能になること:**
- 完全な再現性: 別のラボが seed から同一の VI 値系列を生成可能
- コンパイル結果: *「変動間隔 30秒スケジュール（Fleshler & Hoffman, 1962; リスト長 = 12）を使用した。セッションは、強化が利用不可能な 60秒のウォームアップ期間の後に開始した。各強化の後、2秒間のブラックアウトが挿入された。」*

**なぜ `@algorithm` が重要か:** Fleshler-Hoffman 分布の `VI 30` と等差数列の `VI 30` では強化間間隔が異なる。スケジュール表記だけ（`VI 30-s`）では曖昧 — `@algorithm` がこれを再現性のために解決する。

**`@iti` と `@post_blackout` の設計根拠:** ITI と強化後ブラックアウトはスケジュールの随伴性構造を変えない（境界テスト: `@iti` なしで FI スキャロップを議論できるか → YES）。しかし、セッションの時間構造としてメソッド記述と再現に不可欠であり、@warmup と同列のセッション時間パラメータである。

**ここに属さないもの:**
- 強化子のアクセス時間 → procedure-annotator/stimulus（`@reinforcer` の `access_duration` パラメータ）
- 最小強化間間隔（minimum IRI）→ apparatus-annotator（`@feeder` の `min_cycle` パラメータ）。装置の物理的回復時間であり、セッション時間構造ではない
- セッション日数（何日目か）→ セッション・メタデータ
- 装置の応答遅延 → apparatus-annotator

**引用:**
- Fleshler, M., & Hoffman, H. S. (1962). A progression for generating variable-interval schedules. *JEAB*, *5*(4), 529-530. https://doi.org/10.1901/jeab.1962.5-529

---

### 3. procedure-annotator/context — 環境文脈は何か?

フェーズまたはスケジュールが実施される**環境文脈**を宣言する。renewal（ABA/ABC/AAB）デザインおよび文脈的制御の研究に不可欠。

| キーワード | 目的 | 例 |
|-----------|------|-----|
| `@context` | 環境文脈の識別子 | `@context("A")`, `@context("B", cues="黒白ストライプ+ペパーミント")` |

**例: ABA renewal デザイン（Broomer & Bouton, 2022）**

```
@species("rat") @strain("Wistar")
@reinforcer("food", type="pellet")

phase ResponseTraining:
  sessions = 6
  RI30s
  @context("A")

phase Punishment:
  sessions = 4
  Overlay(RI30s, VI90s)
  @context("B")

phase RenewalTest:
  sessions = 1
  EXT
  @context("A")
  @session_end(rule="time", time=10min)
```

**これにより可能になること:**
- renewal パラダイムの中核である文脈操作を明示的に記述できる
- コンパイル結果: *「反応訓練は文脈 A で実施した。罰手続きは文脈 B で実施した。renewal テストは文脈 A で実施した。」*

**例: no_schedule フェーズと文脈曝露**

```
phase MagazineTraining:
  sessions = 1
  no_schedule
  @context("A")
  @context("B")
```

`no_schedule` フェーズはオペラント随伴性を含まない（例: 反応非依存的な餌の提示、Pavlov 型再評価、馴化）。`@context` アノテーションは手続きが実施される場所を記述する。

**ここに属さないもの:**
- 文脈の物理的仕様（チャンバー寸法、床材）→ apparatus-annotator
- 文脈中に呈示される刺激特徴 → procedure-annotator/stimulus（`@sd`）

**引用:**
- Bouton, M. E. (2002). Context, ambiguity, and unlearning: Sources of relapse after behavioral extinction. *Biological Psychiatry*, *52*(10), 976-986. https://doi.org/10.1016/S0006-3223(02)01546-9

---

### 4. subjects-annotator — 被験体は誰か?

被験体の**生物学的条件と動機づけ操作（MO）**を宣言する。

| キーワード | 目的 | 例 |
|-----------|------|-----|
| `@species` | 種の宣言 | `@species("rat")` |
| `@strain` | 系統の宣言 | `@strain("Long-Evans")` |
| `@deprivation` | 確立操作の宣言 | `@deprivation(hours=22, target="food")` |
| `@history` | 実験経験歴 | `@history("naive")` |
| `@n` | 個体数 | `@n(6)` |

**例: 標準的なラットのオペラント実験**

```
FR 5
  @species("rat")
  @strain("Long-Evans")
  @deprivation(hours=22, target="food")
  @history("naive")
  @n(8)
```

**これにより可能になること:**
- コンパイル結果: *「被験体は8匹の実験ナイーブな雄性 Long-Evans ラットであり、22時間の食物遮断により自由摂食体重の 85%に維持された。」*
- 実験間比較: 種、遮断水準でフィルタリング

**`@deprivation` は確立操作（EO）である:**
行動分析学の用語では、食物遮断は食物の強化効力を増大させ食物探索行動を喚起する確立操作（Michael, 1982）。このアノテーションは動機づけ操作（MO; Laraway et al., 2003）を手続き的宣言として捉える — 内的状態の帰属ではない。

**ここに属さないもの:**
- 内的状態の帰属（「不安レベル」「動機づけ水準」）→ メンタリスト用語。`@deprivation` や `@history` を代わりに使用
- 反応トポグラフィ（「左手でレバーを押した」）→ 行動データであり宣言ではない
- 群分け/カウンターバランス → 実験デザイン・メタデータ

---

### 5. apparatus-annotator — どの装置を使うか?

実験を実行する**物理的装置**を宣言する。

| キーワード | 目的 | 例 |
|-----------|------|-----|
| `@chamber` | 実験チャンバーのモデル | `@chamber("med-associates", model="ENV-007")` |
| `@interface` | HW インターフェース | `@interface("serial", port="/dev/ttyUSB0")` |
| `@hardware` | 物理ハードウェアバックエンド | `@hardware("teensy41")` — シミュレーション時は省略 |
| `@feeder` | 強化子提示装置の物理仕様 | `@feeder("pellet_dispenser", min_cycle=0.5)` |

**例: 物理実験のセットアップ**

```
Conc(VI 30-s, VI 60-s, COD=2-s)
  @chamber("med-associates", model="ENV-007")
  @hardware("teensy41")
  @interface("serial", port="/dev/ttyACM0", baud=115200)
```

`@hw` は `@hardware` の省略形 alias であり、AST レベルでは同一ノードに変換される。詳細は [annotations/design.md §3.5](../../spec/ja/annotations/design.md) を参照。

**これにより可能になること:**
- experiment-io / contingency-bench のターゲット選択
- コンパイル結果: *「セッションは Med Associates（ENV-007）オペラントチャンバーで実施し、Teensy 4.1 マイコンとシリアル接続でインターフェースした。」*
- `@hardware` を省略するとシミュレーションモード（デフォルトで virtual）

**`@feeder` の設計根拠:** 最小強化間間隔（minimum IRI）はペレットディスペンサーや液体ディッパーの物理的回復時間に由来するハードウェア制約であり、随伴性の理論的性質やセッションの時間構造とは独立。同一スケジュールでも装置が異なれば min_cycle は異なる。Apparatus section に自然に記述される情報である。

**ここに属さないもの:**
- 反応装置の論理名（"left_lever"）→ apparatus-annotator（`@operandum`）
- 測定された応答遅延/ジッタ → contingency-bench の出力であり宣言ではない
- ソフトウェアの設定（ログパス、出力ディレクトリ）→ DSL の範囲外

---

## 拡張 annotator

`annotations/extensions/` 配下の拡張 annotator は JEAB 4 カテゴリに属さない annotator。本プロジェクトは同梱するが推奨集合には含まれず、プログラム（runtime / interpreter）が自由に採用・省略できる。

### E1. respondent-annotator — CS/US/ITI/cs_interval メタデータ

Procedure / Apparatus / Measurement の各カテゴリをまたいで付加される**レスポンデント手続きのメタデータ**を宣言する。Tier A レスポンデント primitive（[syntax-guide.md](syntax-guide.md) レベル 4.5 参照）および合成手続き（CER、PIT、オートシェイピング、省略）に用いる。

| キーワード | 目的 | 例 |
|-----------|------|-----|
| `@cs` | 条件刺激 (CS) のメタデータ | `@cs(label="tone", duration=10-s, modality="auditory")` |
| `@us` | 無条件刺激 (US) のメタデータ | `@us(label="shock", intensity="0.5mA", delivery="unsignaled")` |
| `@iti` | ITI 分布 + ジッター | `@iti(distribution="exponential", mean=60-s, jitter=10-s)` |
| `@cs_interval` | CS 提示時間窓 | `@cs_interval(cs_onset=0-s, cs_offset=10-s)` |

**`@cs(label, duration, modality)`** は CS 引数を持つ任意のレスポンデント primitive（`Pair.*`、`Extinction`、`CSOnly`、`Compound`、`Serial`、`Differential`）に付加する。`label` は内包する primitive の `cs` 参照と一致させる必要がある。`modality` は感覚モダリティを列挙する（`"auditory"`、`"visual"`、`"olfactory"`、`"tactile"`）。

**`@us(label, intensity, delivery)`** は US 引数にメタデータを付加する。`delivery` の推奨列挙値: `"unsignaled"`、`"signaled"`、`"response_contingent"`、`"cancelled_on_cs_response"`。最後の値は省略手続きで用いる。

**`@iti(distribution, mean, jitter)`** は、`ITI(distribution, mean)` primitive とは**別の**メタデータ注釈である（primitive は構造的宣言）。注釈はジッター情報を付加し、primitive は構造的 ITI を宣言する。ジッターが不要なら primitive 単独で十分。

**`@cs_interval(cs_onset, cs_offset)`** は CS 提示窓を明示する。`Pair.ForwardDelay` の `cs_duration` と重複するが、読者向けの可読化と装置検証のための補助情報として用いる。

**例: CER の完全記述**

```
Phase(
  name = "cer_training",
  operant = VI 60-s,
  respondent = Pair.ForwardDelay(tone, shock, isi=60-s, cs_duration=60-s)
)
  @cs(label="tone", duration=60-s, modality="auditory")
  @us(label="shock", intensity="0.5mA", delivery="unsignaled")
  @iti(distribution="exponential", mean=120-s, jitter=30-s)
  @cs_interval(cs_onset=0-s, cs_offset=60-s)
```

**境界テストの根拠.** いずれも Q1-Q3 コア対注釈テストをすべて No でパスする: レスポンデント primitive の理論的性質はモダリティ／強度／ジッター／可読化窓と独立；これらの値を変えても parse tree は変化しない；プログラムごとに必須扱いか任意扱いかを決められる。したがって注釈であり文法構成要素ではない。詳細は [respondent-annotator 仕様](../../spec/ja/annotations/extensions/respondent-annotator.md) を参照。

**ここに属さないもの:**
- 構造的な CS-US 関係（forward-delay、forward-trace、backward、simultaneous、contingency space）→ レスポンデント primitive（Tier A）
- 新しいレスポンデント手続きで構造関係を導入するもの（ブロッキング、オーバーシャドーイング、潜在制止 等）→ レスポンデント拡張ポイント（`contingency-respondent-dsl`）、この annotator には属さない

**引用:**
- Pavlov, I. P. (1927). *Conditioned reflexes: An investigation of the physiological activity of the cerebral cortex* (G. V. Anrep, Trans.). Oxford University Press.
- Rescorla, R. A. (1967). Pavlovian conditioning and its proper control procedures. *Psychological Review*, *74*(1), 71–80. https://doi.org/10.1037/h0024109

---

### E2. learning-models-annotator — 連合学習モデルの指定

スケジュール式またはフェーズに関連づける**連合学習モデル**を宣言する。(a) 手続きを解釈するモデルを明示したい解説・チュートリアル・教材、および (b) 実行時に具体的モデル実装を選択するシミュレーション・パイプラインで用いる。

| キーワード | 目的 | 例 |
|-----------|------|-----|
| `@model(RW)` | Rescorla-Wagner (1972) 誤差修正モデル | `Pair.ForwardDelay(tone, shock, isi=10-s) @model(RW)` |
| `@model(PH)` | Pearce-Hall (1980) 注意変調モデル | `Pair.ForwardDelay(tone, shock, isi=10-s) @model(PH)` |
| `@model(TD)` | Temporal-difference 学習（Sutton & Barto, 1998） | `Pair.ForwardDelay(tone, shock, isi=10-s) @model(TD)` |

**モデル概要:**

- **RW（Rescorla & Wagner, 1972）**. 誤差修正学習: ΔV = αβ(λ − ΣV)。連合強度の更新は予測と得られた US との差分に比例する。ブロッキング、オーバーシャドーイング、条件性制止の基盤モデル。
- **PH（Pearce & Hall, 1980）**. 注意変調変種: CS の連合可能性 α は US が驚きである時に増加し、予測が的中する時に減少する。潜在制止や消去現象のうち RW が説明できないものを説明する。
- **TD（Sutton & Barto, 1998）**. 時間差分学習: 各時間ステップを状態として扱い、連続する予測の差分から学習する。報酬予測誤差の行動的記述と神経科学的記述を橋渡しするモデル。

**現状.** `learning-models-annotator` は**設計意図**としてここに記録する。対応する仕様書（`spec/ja/annotations/extensions/learning-models-annotator.md`）と JSON Schema は後続フェーズでの整備を予定。当該ファイルが整備されるまでは、本節に記載したキーワード集と意味論が正典として機能する。

**境界テストの根拠.** Q1: レスポンデント primitive の理論的性質議論にモデルが必須か? **No** — primitive の操作的定義はモデル非依存。Q2: `@model(...)` が parse tree または評価結果を変えるか? **No**。Q3: モデルは文法レベルで必須か? **No** — ほとんどのプログラムはモデルを選択せず DSL を利用する。全て No、注釈として分類される。

**引用:**
- Pearce, J. M., & Hall, G. (1980). A model for Pavlovian learning: Variations in the effectiveness of conditioned but not of unconditioned stimuli. *Psychological Review*, *87*(6), 532–552. https://doi.org/10.1037/0033-295X.87.6.532
- Rescorla, R. A., & Wagner, A. R. (1972). A theory of Pavlovian conditioning: Variations in the effectiveness of reinforcement and nonreinforcement. In A. H. Black & W. F. Prokasy (Eds.), *Classical conditioning II: Current research and theory* (pp. 64–99). Appleton-Century-Crofts.
- Sutton, R. S., & Barto, A. G. (1998). *Reinforcement learning: An introduction*. MIT Press.

---

## アノテーションの合成: 完全な例

並立 VI-VI 実験のフルアノテーション・プログラム（スコーピングレベル別に整理）:

```
-- Subjects（プログラムレベル）
@species("rat")
@strain("Sprague-Dawley")
@deprivation(hours=23, target="food")
@history("naive")
@n(6)

-- Apparatus（プログラムレベル）
@chamber("med-associates", model="ENV-007")
@hardware("teensy41")
@feeder("pellet_dispenser", min_cycle=0.5)

-- セッションパラメータ（プログラムレベル）
@clock(unit="s")
@algorithm("fleshler-hoffman", n=12, seed=42)
@warmup(duration=300)
@iti(duration=10)
@post_blackout(duration=2)
@reinforcer("sucrose", concentration="10%", access_duration=3)

-- スケジュールパラメータ
COD = 2-s
LH = 10-s

let left = VI 30-s
let right = VI 60-s
Conc(left, right)
  @operandum("left_lever", component=1)   -- スケジュールレベル
  @operandum("right_lever", component=2)  -- スケジュールレベル
  @sd("red_light", component=1)           -- スケジュールレベル
  @sd("green_light", component=2)         -- スケジュールレベル
```

プログラムレベルのアノテーション（Subjects, Apparatus, Session）は論文 Method セクションの構造に対応する。スケジュールレベルのアノテーションは随伴性ごとの詳細を記述する。

この単一の DSL ソースから以下にコンパイル可能:
- **Python ランタイム**（contingency-py + annotator）
- **Rust ランタイム**（contingency-rs）
- **MedPC 構文**（既存の MedPC 装置）
- **論文 Methods セクション**（自然言語）

---

## カスタムアノテーションの作成

ドメイン固有のアノテーション（ABA 臨床系、OBM 社会系、行動薬理系 等）は
DSL プロジェクトの推奨集合には含まれない。これらは次の 2 通りで追加できる:

1. **DSL プロジェクトの推奨集合への追加を提案する**
   - `spec/ja/annotation-template.md` をコピー
   - 境界テストに回答（[annotations/design.md](../../spec/ja/annotations/design.md) §2 参照）
   - プロジェクトのレビューを経て推奨 registry に追加

2. **プログラム独自の registry として構築する**
   - 各プログラム（runtime / interpreter）は自身の registry を自由に定義できる
   - DSL プロジェクトのレビューを経る必要はない
   - Core DSL 文法は変更不要

どちらの経路を選ぶかは、その annotation が DSL プロジェクト全体の推奨集合に
含める価値があるかどうかで判断する（詳細は
[design-philosophy.md §4.2](../../spec/ja/design-philosophy.md) を参照）。

**境界テスト（簡易版）:** `@X` を除去するとスケジュールの理論的議論が
不完全になるなら、それはアノテーションではなくコア文法に属する可能性がある
（design-philosophy §8 の制約下でのみ Core への追加を検討）。

---

## 参照文献

- Fleshler, M., & Hoffman, H. S. (1962). A progression for generating variable-interval schedules. *JEAB*, *5*(4), 529-530. https://doi.org/10.1901/jeab.1962.5-529
- Kelleher, R. T. (1966). Conditioned reinforcement in second-order schedules. *JEAB*, *9*, 475. https://doi.org/10.1901/jeab.1966.9-475
- Michael, J. (1982). Distinguishing between discriminative and motivational functions of stimuli. *JABA*, *15*(1), 149-155. https://doi.org/10.1901/jaba.1982.15-149
