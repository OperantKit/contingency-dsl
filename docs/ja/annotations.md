# アノテーション・ガイド

> スケジュール式に実験メタデータを付加する方法。
> アノテーションシステムの設計については [annotation-design.md](../../spec/annotation-design.md) を参照。

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

COD = 2s

Conc(VI30s, VI60s)
  @operandum("left_lever", component=1)   -- スケジュールレベル: 成分ごと
  @operandum("right_lever", component=2)
```

同一のアノテーションキーワードが両レベルに現れた場合、スケジュールレベルの値がプログラムレベルのデフォルトを上書きする。

### 漸進的付加

同じスケジュール式が、理論から出版まで段階的に情報を蓄える:

| 文脈 | 式 | 必要なアノテーション |
|------|-----|-------------------|
| 理論的議論 | `FI 10` | なし |
| シミュレーション | `@clock(unit="s")` + `FI 10 @algorithm("fleshler-hoffman")` | temporal |
| 物理実験 | `@species(...)` `@chamber(...)` + `FI 10 @operandum(...) @reinforcer(...)` | 4種全て |
| 論文出版 | 上記全て | 完全 — Methods セクションにコンパイル可能 |

---

## 4つの推奨アノテータ

contingency-dsl プロジェクトは、実験手続きの普遍的な4次元をカバーする
**推奨アノテータ**を提供する。これらは DSL プロジェクトが提示する推奨集合で
あり、プログラム（runtime / interpreter）は自由に採用・拡張・置換できる
（詳細は [design-philosophy.md §4.2](../../spec/ja/design-philosophy.md) を参照）。

### 1. stimulus-annotator — どの刺激が関与するか?

刺激の**同一性と機能**を宣言する。

| キーワード | 目的 | 例 |
|-----------|------|-----|
| `@reinforcer` | 強化子の宣言（基本形） | `@reinforcer("food", type="unconditioned")` |
| `@sd` | 弁別刺激の同定 | `@sd("red_light", component=1)` |
| `@operandum` | 反応装置の同定 | `@operandum("left_lever")` |
| `@brief` | 二次スケジュールの短時間刺激 | `@brief("light", duration=2)` |

**`@reinforcer` の別名:** `@punisher` と `@consequentStimulus` は `@reinforcer` の
等価な alias。実験者の意図を source に明示したい場合に使用する（例:
`FR3 @punisher("shock")`）。AST レベルでは 3 者とも同一ノードに collapse され、
等価性判定に影響しない。詳細は
[annotation-design.md §3.5](../../spec/annotation-design.md) を参照。

**例: 成分を同定した並行スケジュール**

```
Conc(VI30s, VI60s, COD=2s)
  @operandum("left_lever", component=1)
  @operandum("right_lever", component=2)
  @reinforcer("sucrose", concentration="10%", duration=3)
  @sd("red_light", component=1)
  @sd("green_light", component=2)
```

**これにより可能になること:**
- 各 `Conc` 成分にオペランダムが割り当てられているか検証できる（参照整合性）
- コンパイル結果: *「2つの反応レバーが利用可能であった。左レバー（赤色光）は VI 30秒、右レバー（緑色光）は VI 60秒で動作した。強化子は 10%ショ糖溶液への3秒間アクセスであった。」*

**ここに属さないもの:**
- 刺激の物理的仕様（LED 波長、音のデシベル）→ apparatus-annotator
- 呈示時間（刺激持続時間、ISI）→ temporal-annotator
- 条件性刺激の学習履歴 → ランタイム状態であり宣言ではない

**引用:**
- Kelleher, R. T. (1966). Conditioned reinforcement in second-order schedules. *JEAB*, *9*, 475. https://doi.org/10.1901/jeab.1966.9-475（条件性強化子としての brief stimulus）

---

### 2. temporal-annotator — 時間はどう構造化されるか?

再現性に影響する**セッションレベルの時間パラメータ**を宣言する。

| キーワード | 目的 | 例 |
|-----------|------|-----|
| `@clock` | 時間単位の宣言 | `@clock(unit="s")` |
| `@warmup` | セッション前のウォームアップ期間 | `@warmup(duration=60)` |
| `@algorithm` | スケジュール値生成アルゴリズム | `@algorithm("fleshler-hoffman", n=12)` |

注: `@blackout` と `@cod` は当初 temporal-annotator に提案されたが、随伴性構造に直接影響するため**コア文法にキーワード引数として昇格済み**（`BO=5s`, `COD=2s`）。

**例: 完全な時間仕様の VI スケジュール**

```
VI30s
  @clock(unit="s")
  @algorithm("fleshler-hoffman", n=12, seed=42)
  @warmup(duration=60)
```

**これにより可能になること:**
- 完全な再現性: 別のラボが seed から同一の VI 値系列を生成可能
- コンパイル結果: *「変動間隔 30秒スケジュール（Fleshler & Hoffman, 1962; リスト長 = 12）を使用した。セッションは、強化が利用不可能な 60秒のウォームアップ期間の後に開始した。」*

**なぜ `@algorithm` が重要か:** Fleshler-Hoffman 分布の `VI 30` と等差数列の `VI 30` では強化間間隔が異なる。スケジュール表記だけ（`VI30s`）では曖昧 — `@algorithm` がこれを再現性のために解決する。

**ここに属さないもの:**
- 強化子の呈示時間 → stimulus-annotator（`@reinforcer` の duration パラメータ）
- セッション日数（何日目か）→ セッション・メタデータ
- 装置の応答遅延 → apparatus-annotator

**引用:**
- Fleshler, M., & Hoffman, H. S. (1962). A progression for generating variable-interval schedules. *JEAB*, *5*(4), 529-530. https://doi.org/10.1901/jeab.1962.5-529

---

### 3. subject-annotator — 被験体は誰か?

被験体の**生物学的条件と動機づけ条件**を宣言する。

| キーワード | 目的 | 例 |
|-----------|------|-----|
| `@species` | 種の宣言 | `@species("rat")` |
| `@strain` | 系統の宣言 | `@strain("Long-Evans")` |
| `@deprivation` | 確立操作の宣言 | `@deprivation(hours=22, target="food")` |
| `@history` | 実験経験歴 | `@history("naive")` |
| `@n` | 個体数 | `@n(6)` |

**例: 標準的なラットのオペラント実験**

```
FR5
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
行動分析学の用語では、食物遮断は食物の強化効力を増大させ食物探索行動を喚起する確立操作（Michael, 1982）。このアノテーションは動機づけ変数を手続き的宣言として捉える — 内的状態の帰属ではない。

**ここに属さないもの:**
- 内的状態の帰属（「不安レベル」「動機づけ水準」）→ メンタリスト用語。`@deprivation` や `@history` を代わりに使用
- 反応トポグラフィ（「左手でレバーを押した」）→ 行動データであり宣言ではない
- 群分け/カウンターバランス → 実験デザイン・メタデータ

---

### 4. apparatus-annotator — どの装置を使うか?

実験を実行する**物理的装置**を宣言する。

| キーワード | 目的 | 例 |
|-----------|------|-----|
| `@chamber` | 実験チャンバーのモデル | `@chamber("med-associates", model="ENV-007")` |
| `@interface` | HW インターフェース | `@interface("serial", port="/dev/ttyUSB0")` |
| `@hw` | ハードウェアバックエンド | `@hw("teensy41")` or `@hw("virtual")` |

**例: 物理実験のセットアップ**

```
Conc(VI30s, VI60s, COD=2s)
  @chamber("med-associates", model="ENV-007")
  @hw("teensy41")
  @interface("serial", port="/dev/ttyACM0", baud=115200)
```

**これにより可能になること:**
- experiment-io / contingency-bench のターゲット選択
- コンパイル結果: *「セッションは Med Associates（ENV-007）オペラントチャンバーで実施し、Teensy 4.1 マイコンとシリアル接続でインターフェースした。」*
- `@hw("virtual")` でハードウェアなしのシミュレーション・バックエンドを選択

**ここに属さないもの:**
- 反応装置の論理名（"left_lever"）→ stimulus-annotator（`@operandum`）
- 測定された応答遅延/ジッタ → contingency-bench の出力であり宣言ではない
- ソフトウェアの設定（ログパス、出力ディレクトリ）→ DSL の範囲外

---

## アノテーションの合成: 完全な例

並行 VI-VI 実験のフルアノテーション・プログラム（スコーピングレベル別に整理）:

```
-- Subjects（プログラムレベル）
@species("rat")
@strain("Sprague-Dawley")
@deprivation(hours=23, target="food")
@history("naive")
@n(6)

-- Apparatus（プログラムレベル）
@chamber("med-associates", model="ENV-007")
@hw("teensy41")

-- セッションパラメータ（プログラムレベル）
@clock(unit="s")
@algorithm("fleshler-hoffman", n=12, seed=42)
@warmup(duration=300)
@reinforcer("sucrose", concentration="10%", duration=3)

-- スケジュールパラメータ
COD = 2s
LH = 10s

let left = VI30s
let right = VI60s
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
   - `spec/annotation-template.md` をコピー
   - 境界テストに回答（[annotation-design.md](../../spec/annotation-design.md) §2 参照）
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
