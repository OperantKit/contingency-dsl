# 構文ガイド

> contingency-dsl の構文を段階的に解説する。基本スケジュールから高度な構成まで。
> 形式文法（BNF）は [foundations/grammar.md](../../spec/ja/foundations/grammar.md)、[operant/grammar.md](../../spec/ja/operant/grammar.md)、[respondent/grammar.md](../../spec/ja/respondent/grammar.md) を参照。
>
> ## 層構造マップ
>
> DSL は科学的カテゴリで階層化される。本ガイドもこの階層に沿って構成する:
>
> | 層 | 解説位置 |
> |---|---|
> | **基盤 (Foundations)** — パラダイム中立な形式基盤 | 原子構文・リテラル型を通じて暗黙的に全体で扱う |
> | **オペラント (Operant)** — 三項随伴性 SD-R-SR | レベル 1〜4（原子、複合、修飾、二次スケジュール） |
> | **Operant.Stateful** — 実行時計算基準 | レベル 3 の Percentile Schedule |
> | **Operant.TrialBased** — 離散試行スケジュール | `spec/ja/operant/trial-based/` 参照 |
> | **レスポンデント (Respondent)** — 二項随伴性 CS-US（Tier A） | レベル 4.5 のレスポンデント primitives |
> | **合成手続き (Composed)** — オペラント × レスポンデント | レベル 4.6 の合成手続き |
> | **実験層 (Experiment)** — 宣言的フェーズ構造 | レベル 6 の実験層 |
> | **注釈 (Annotation)** — プログラム境域メタデータ | [annotations.md](annotations.md) 参照 |

---

## レベル 1: 原子スケジュール

全ての基本。**2文字の型プレフィクス** + **値** で構成される。

```
FR 5          -- 固定比率 5: 5回反応ごとに強化
VI 30-s        -- 変動間隔 30秒: 平均 30秒間隔後の最初の反応を強化
             --   （Fleshler-Hoffman 分布で値を生成）
FT 10-s        -- 固定時間 10秒: 行動に依存せず 10秒ごとに強化子提示
```

### 3 × 3 グリッド

1文字目が**分布**（値の選び方）、2文字目が**領域**（値が何を測るか）を指定する:

|              | R (Ratio — 反応数) | I (Interval — 時間＋反応) | T (Time — 時間のみ) |
|--------------|-------------------|-------------------------|-------------------|
| **F** (Fixed)    | FR 5  | FI 30-s  | FT 10-s  |
| **V** (Variable) | VR 20 | VI 60-s  | VT 15-s  |
| **R** (Random)   | RR 10 | RI 45-s  | RT 20-s  |

特殊な2つ:
```
CRF          -- 連続強化（= FR 1）: 全ての反応を強化
EXT          -- 消去: いかなる反応も強化しない
```

### 表記バリエーション

以下は全て**同一**のスケジュールを指す:

```
VI 60-s      -- JEAB 現代標準形式（推奨）
VI 60-sec    -- JEAB 旧式論文（1960-70年代）
VI 60 s      -- 空白区切り単位（JEAB 1986, 2012）
VI 60 sec    -- 空白区切り単位（Ferster & Skinner, 1957）
VI 60-min    -- 分単位（長間隔、例: VI 1-min）
VI 60 min    -- 分単位、空白区切り
VI 60s       -- 単位密着形式（区切りなし）
VI60s        -- 密着形式（単位付き）
VI60         -- 密着形式（単位暗黙）
VI 60        -- 空白区切り、単位なし（Ferster & Skinner, 1957）
```

---

## レベル 2: 複合スケジュール

2つ以上のスケジュールを**コンビネータ**で組み合わせる。構文は常に `Combinator(schedule, schedule, ...)`。

### 並立型コンビネータ

```
Conc(VI 30-s, VI 60-s, COD=2-s)    -- 並立: 2つのスケジュールが同時に利用可能
                               --   COD（切替遅延）は Conc で必須
Alt(FR 10, FI 5-min)              -- 代替: どちらかが先に完了すれば強化（OR 論理）
Conj(FR 5, FI 30-s)               -- 連立: 両方の条件を満たして強化（AND 論理）
```

### 逐次型コンビネータ

> **刺激変化**（stimulus change）: スケジュール成分間の弁別刺激の移行を指す。

```
Chain(FR 5, FI 30-s)              -- 連鎖: FR 5 完了 → 刺激変化 → FI 30 完了 → 強化
Tand(VR 20, DRL 5-s)              -- タンデム: 連鎖と同じだが刺激変化なし
```

### 交替型コンビネータ

```
Mult(FR 5, EXT)                 -- 多元: FR 5 と EXT が刺激変化を伴って交替
Mix(FR 5, FR 10)                 -- 混合: 同上だが刺激変化なし
```

### ネスト

コンビネータは自由に入れ子にできる:

```
Conc(Chain(FR 5, VI 60-s), Alt(FR 10, FT 30-s), COD=2-s)
```

### 罰の重畳

```
Overlay(VI 60-s, FR 1)                              -- 全反応に罰
Overlay(Conc(VI 30-s, VI 60-s, COD=2-s), FR 1,
        target=changeover)                          -- 切替反応のみに罰
                                                    --   （Todorov, 1971）

-- 反応クラス特異的罰: Conc の PUNISH directive
Conc(VI 30-s, VI 60-s, COD=2-s, PUNISH(1->2)=FR 1, PUNISH(2->1)=FR 1)
                                                    -- 方向非対称罰
Conc(VI 30-s, VI 60-s, COD=2-s, PUNISH(changeover)=FR 1)
                                                    -- 全 changeover 方向（短縮形）
Conc(VI 30-s, VI 60-s, COD=2-s, PUNISH(1)=VI 30-s)     -- 成分特異的罰
                                                    --   （de Villiers, 1980）
```

### 複合スケジュールのキーワード引数

| キーワード | 対象コンビネータ | 形式 | 役割 |
|---|---|---|---|
| `COD` | Conc | `COD=2-s`（スカラー）または `COD(1->2)=2-s`（方向指定） | 切替遅延（Catania, 1966） |
| `FRCO` | Conc | `FRCO=3` | 切替固定比（Hunter & Davison, 1985） |
| `BO` | Mult, Mix | `BO=5-s` | 成分間の暗転（Reynolds, 1961） |
| `count` | Interpolate | `count=16` | 挿入ブロックの強化回数 |
| `onset` | Interpolate | `onset=3-min` | 挿入開始までの時間 |
| `target` | Overlay | `target=changeover` / `target=all` | 反応クラス targeting（v1.y） |
| `PUNISH(...)` | Conc | `PUNISH(changeover)=S` / `PUNISH(x->y)=S` / `PUNISH(n)=S` | 反応クラス特異的罰（v1.y） |

---

## レベル 3: 修飾子

### 分化強化

```
DRL 5-s        -- 低率分化強化: IRT ≥ 5秒の場合のみ強化（ゆっくり反応）
DRH 2-s        -- 高率分化強化: IRT ≤ 2秒の場合のみ強化（速い反応）
DRO 10-s       -- 他行動分化強化: 標的行動なしで 10秒経過で強化
```

### Lag スケジュール（オペラント変動性）

現在の反応が直前 *n* 回の反応と異なる場合にのみ強化する（Page & Neuringer, 1985）:

```
Lag 5                   -- 直前 5 反応すべてと異なれば強化
Lag(5, length=8)        -- 8 反応系列を比較単位とする
Lag 0                   -- variability 要求なし（CRF と等価）
```

`Lag 1` は臨床で最も一般的な形式（例: マンド変動性訓練）。optional な `length` パラメータは反応単位のサイズを指定: `length=1`（デフォルト）は個別反応、`length=8` は Page & Neuringer (1985) の 8 反応系列。

複合スケジュールとの合成:

```
Mult(Lag(5, length=8), CRF, BO=5-s)   -- variability vs ベースライン
Conj(Lag 1, FR 3)                      -- 変動的かつ 3 反応ごとに強化
```

### 累進比率

```
PR(hodos)                       -- Hodos (1961) ステップ関数
PR(linear, start=1, increment=5) -- 線形: 1, 6, 11, 16, ...
PR(exponential)                 -- 指数関数: Richardson & Roberts (1996)
PR(geometric, start=1, ratio=2) -- 幾何級数: 1, 2, 4, 8, 16, ...
```

### Percentile Schedule（Operant.Stateful）

被験体の行動に基準が適応する分化強化手続き:

```
Pctl(IRT, 50)                            -- IRT 中央値以下を強化
Pctl(IRT, 25, window=30)                 -- 25 百分位以下、30 反応ウィンドウ
Pctl(latency, 75, window=50, dir=above)  -- 潜時の 75 百分位以上を強化
Pctl(force, 90, window=15, dir=above)    -- 力の 90 百分位以上を強化
Pctl(duration, 10, window=20)            -- 短い持続時間（10 百分位以下）
```

DRL/DRH（固定閾値）と異なり、Pctl は被験体の直近の反応分布から基準を算出する。
**shaping（逐次接近法）**の定量的基盤 (Galbicka, 1994)。

パラメータ: `target`（反応次元）、`rank`（0–100 百分位）、`window`（デフォルト 20）、`dir`（`below`/`above`、デフォルト `below`）。

### Limited Hold（時間的利用可能制約）

**後置修飾子** — 強化が利用可能な時間窓を制限する:

```
FI 30-s LH 10-s                    -- FI 30秒 + 10秒の利用可能窓
Conc(VI 30-s LH 5-s, VI 60-s LH 10-s, COD=2-s) -- 成分ごとに個別の LH
```

---

## レベル 4: 二次スケジュール ⚠️

> **用語ノート: 成分・ユニット・リンク** — 本 DSL では複合スケジュール内の位置を指す3つの用語を区別する。
> - **成分**（component）: `Conc` / `Mult` 内の各位置（例: `Conc(VI 30-s, VI 60-s)` の左右）
> - **ユニット**（unit）: 二次スケジュール内で繰り返される反応パターン（例: `FI 120-s(FR 10)` の `FR 10`）
> - **リンク**（link）: `Chain` / `Tand` 内の逐次位置（例: `Chain(FR 5, FI 30-s)` の初期リンクと終端リンク）

**初見で最も混乱しやすい構文。** 関数呼び出しのように見えるが、全く異なる意味を持つ。

```
FI 120-s(FR 10)      -- 二次スケジュール（second-order schedule）
```

### これは何を意味するか

`FI 120-s(FR 10)` の意味:

> 「FR 10 の完了を1つの *unit（単位）* として扱い、120秒が経過した後の最初の unit 完了で強化する」

これは「FI 120 に引数 FR 10 を渡す」という意味では**ない**。括弧内は、被験体が繰り返し遂行する **unit スケジュール** である。

### 構文の読み方

```
FI 120-s(FR 10)
│     │
│     └── unit: 間隔内で繰り返されるパターン
│         （10回反応で1ユニット完了）
│
└── overall: ユニット完了をいつ強化するかを制御するスケジュール
    （120秒経過後の最初のユニット完了 = 食物）
```

### 動作の流れ（ステップバイステップ）

```
時間 →
|── FR 10 ──| brief |── FR 10 ──| brief |── FR 10 ──| brief |── FR 10 ──| 食物
                                                              ↑
                                                    FI 120秒経過 + unit 完了
```

1. 被験体は FR 10（10回反応で1ユニット）を**繰り返し**遂行する
2. 各ユニット完了時に **brief stimulus**（短時間刺激 — 通常は条件性強化子として機能する）が提示されうる
3. 120秒が経過し **かつ** 次の FR 10 ユニットが完了 → 一次強化子（食物）
4. サイクルが再開する

### なぜ Tand ではだめなのか

`Tand(FI 120-s, FR 10)` は**別の手続き**を意味する:

| | `Tand(FI 120-s, FR 10)` | `FI 120-s(FR 10)` |
|---|---|---|
| FI 間隔の間 | 待機（反応不要） | **FR 10 ユニットを繰り返し遂行** |
| FR 10 は何回? | 1回のみ（FI 経過後） | 複数回（間隔中ずっと） |
| brief stimulus | なし（タンデム = 刺激変化なし） | 各ユニット完了時に提示 |
| 行動パターン | FI スキャロップ → FR ラン | FI 内に**ユニット単位のスキャロップ**が形成 |

二次スケジュールでは、brief stimulus が条件性強化子として機能し、非常に疎（低頻度）な一次強化の下でも行動を維持できる。Tand ではこれが不可能。

### その他の例

```
FR 5(FI 30-s)       -- FI 30秒の unit を5回完了で強化
                  --   （最短 150秒、各 unit で FI スキャロップ）
VI 60-s(FR 20)      -- FR 20 unit を繰り返し、平均 60秒後の unit 完了で強化
FR 10(FR 5)        -- FR 5 unit を10回完了で強化
                  --   （合計50反応だが、5回 × 10バーストの構造）
```

### どこで使われるか

二次スケジュールは以下の研究領域で不可欠:

- **行動薬理学**: 疎な強化下での薬物自己投与（Kelleher, 1966）
- **条件性強化研究**: どの刺激が行動を維持するかの検証（Malagodi et al., 1973）
- **長時間セッション実験**: 低頻度の一次強化で数時間にわたる安定した行動維持

---

## レベル 4.5: レスポンデント primitives（Tier A）

> 二項随伴性 (CS-US)。**レスポンデント**層に属し、オペラント・スケジュールと並置される。Rescorla (1967) の随伴性空間 (contingency space) が直接指定する手続きとその統制手続きのみを Tier A として収録する。Tier B（ブロッキング、オーバーシャドーイング、潜在制止、更新、復元など）は拡張パッケージ `contingency-respondent-dsl` に委任する。正式な操作的定義は [respondent/primitives.md](../../spec/ja/respondent/primitives.md) を参照。

### Pair primitives（R1〜R4）

```
Pair.ForwardDelay(tone, shock, isi=10-s, cs_duration=15-s)
                                       -- CS 点灯 → CS 継続 → US 点灯（オーバーラップ）
                                       --   Pavlov (1927)
Pair.ForwardTrace(tone, food, trace_interval=5-s)
                                       -- CS 消灯 → 痕跡間隔 → US 点灯
Pair.Simultaneous(light, airpuff)      -- CS 点灯 = US 点灯（isi = 0）
Pair.Backward(shock, tone, isi=2-s)    -- US 先行、続いて CS
                                       --   しばしば条件性制止子として機能
```

### Extinction、CS 単独、US 単独（R5〜R7）

```
Extinction(tone)                 -- 獲得後、CS 単独（文脈感受性; Bouton, 2004）
CSOnly(tone, trials=40)           -- フェーズ非依存な CS 単独提示
USOnly(shock, trials=20)          -- US 単独（馴化／前曝露）
```

### 随伴性空間（R8〜R10）

```
Contingency(p_us_given_cs=0.9, p_us_given_no_cs=0.1)
                                  -- Rescorla (1967) 随伴性空間の任意点
Contingency(0.0, 0.3)             -- 負の随伴性（CS 非提示時のみ US）
TrulyRandom(tone, shock)          -- 対角線上: P(US|CS) = P(US|¬CS)
TrulyRandom(tone, shock, p=0.2)   -- 共有確率を明示
ExplicitlyUnpaired(tone, shock, min_separation=30-s)
                                  -- Contingency(0, p) + 時間分離制約
                                  --   （Ayres, Benedict, & Witcher, 1975）
```

### Compound、Serial、ITI（R11〜R13）

```
Compound([tone, light])                       -- 同時提示複合 CS
Compound([tone, light], mode=Simultaneous)    -- mode 明示
Serial([light, tone], isi=3-s)                -- 系列複合（時間順序）
ITI(exponential, mean=60-s)                   -- 構造的試行間間隔
ITI(fixed, mean=30-s)
```

`ITI(distribution, mean)` primitive は構造的宣言であり、別途 `@iti(distribution, mean, jitter)` 注釈でジッター情報を付与できる（[annotations.md](annotations.md) 参照）。

### 差別条件づけ（R14）

```
Differential(tone_plus, tone_minus, shock)   -- A+/B−（完全形）
Differential(tone_plus, tone_minus)          -- 短縮形（US は @us 注釈から推論）
```

`Differential` は CS+ / CS− の対比訓練のための Tier A primitive（Pavlov, 1927; Mackintosh, 1974）。条件性制止手続きや feature-positive / feature-negative の変種（Rescorla, 1969）は Tier B に留まる。

### 引数順序の規約

- `Pair.ForwardDelay`、`Pair.ForwardTrace`、`Pair.Simultaneous` では CS が US に先行する。
- `Pair.Backward(us, cs, isi)` では US が CS に先行し、引数順序は開始時刻順に従う。
- `Contingency(p_us_given_cs, p_us_given_no_cs)` では CS 条件つき確率が常に先頭。この順序は文法レベルで固定され、可換にできない。

---

## レベル 4.6: 合成手続き

> **合成手続き (Composed)** はオペラント・ベースラインとレスポンデント（パヴロフ型）成分を組み合わせる。単独の Operant / Respondent 文法では表現できない構造を持つため、独立した最上位層（`composed/`）に置かれる。正式仕様は [composed/conditioned-suppression.md](../../spec/ja/composed/conditioned-suppression.md)、[composed/pit.md](../../spec/ja/composed/pit.md)、[composed/autoshaping.md](../../spec/ja/composed/autoshaping.md)、[composed/omission.md](../../spec/ja/composed/omission.md) を参照。

### 条件性抑制 (CER)

```
Phase(
  name = "cer_training",
  operant = VI 60-s,
  respondent = Pair.ForwardDelay(tone, shock, isi=60-s, cs_duration=60-s),
  criterion = Stability(window=5, tolerance=0.10)
)
@cs(label="tone", duration=60-s, modality="auditory")
@us(label="shock", intensity="0.5mA", delivery="unsignaled")
```

食物系オペラント・ベースライン (VI 60-s) とパヴロフ型オーバーレイが同一フェーズに共存する。US 提示は反応非依存（パヴロフ型）であり、これが CER を罰から構造的に区別する。Estes & Skinner (1941); Annau & Kamin (1961)。

### パヴロフ-道具的転移 (PIT)

```
PhaseSequence(
  Phase(name="pavlovian_training",
        respondent=Pair.ForwardDelay(tone, food, isi=10-s, cs_duration=10-s)),
  Phase(name="instrumental_training",
        operant=VI 60-s),
  Phase(name="transfer_test",
        operant=EXT,
        respondent=CSOnly(tone, trials=8))
)
```

パヴロフ訓練と道具的訓練は明示的に**独立**に行われる。転移テストではオペラント・スケジュールを消去下に置き、CS 効果のみを測定する。Estes (1948); Rescorla & Solomon (1967); Lovibond (1983)。

### オートシェイピング／サイン・トラッキング

```
Phase(
  name = "autoshaping_training",
  respondent = Pair.ForwardDelay(key_light, food, isi=8-s, cs_duration=8-s),
  criterion = FixedSessions(n=10)
)
@cs(label="key_light", duration=8-s, modality="visual")
@us(label="food", intensity="3s_access", delivery="unsignaled")
```

オペラント随伴性は一切設定されないが、出現するキーつつきはパヴロフ型である（Brown & Jenkins, 1968）。

### 省略（ネガティブ自動維持）

```
@us(label="food", delivery="cancelled_on_cs_response")

phase omission_training:
  sessions = 10
  Pair.ForwardDelay(key_light, food, isi=8-s, cs_duration=8-s) @omission(response="key_peck", during="cs")
```

CS 提示中の反応が当該試行の予定 US をキャンセルする。`@omission(response, during)` 注釈をパヴロフ型 primitive に付与してキャンセル規則を宣言し、アナライザ／実行器のパスが実行時にこれを解釈する。この負の反応-結果随伴性にもかかわらず反応が維持されることが、オートシェイピングに対するパヴロフ型（非オペラント）制御の実証的根拠となる（Williams & Williams, 1969）。

---

## レベル 5: プログラムレベル機能

### 名前付き束縛

スケジュールに名前を付けて可読性を向上させる:

```
let baseline = VI 60-s
let probe = Conc(VI 30-s, VI 60-s, COD=2-s)
Mult(baseline, probe)
```

名前は解析時に展開される（マクロ置換）。変更可能な状態は導入されない。

### プログラムレベルのデフォルト

全ての該当構成に適用されるパラメータを設定:

```
LH = 10-s
COD = 2-s
Conc(VI 30-s, VI 60-s)     -- COD=2-s を継承、各成分に LH=10-s が適用
```

ローカル指定がデフォルトを上書きする:

```
LH = 10-s
Conc(VI 30-s LH 5-s, VI 60-s, COD=2-s)  -- VI 30 は LH=5-s、VI 60 はデフォルトの LH=10-s
```

---

## レベル 6: 実験層（多フェーズ）

セッション間デザイン（A-B-A 反転、用量反応、パラメトリック研究）には、`phase`、`progressive`、`shaping` の各宣言を使う。`progressive` は Sidman 意味のパラメータ漸進（セッション間）、`shaping` は Skinner 意味のセッション内反応形成を表す。

### Phase 宣言

`phase` は phase 変化基準（セッション数または安定性）を持つ名前付きプログラム:

```
phase Baseline:
  sessions = 25
  Conc(VI 30-s, VI 60-s, COD=2-s)

phase Reversal:
  sessions >= 10
  stable(visual)
  use Baseline      -- Baseline のスケジュール式を再利用
```

### Progressive Training（パラメトリック漸進）

`progressive` は番号付き `phase` 宣言列に脱糖される。FI 漸進訓練、用量反応、強化子量研究などに有用（Sidman, 1960; Zeiler, 1977）:

```
progressive FI_Training:
  steps v = [2, 4, 8, 12, 18]
  sessions >= 3
  stable(visual)
  FI {v}-s LH 3-s
```

`FI_Training_1, …, FI_Training_5` に展開され、`{v}` placeholder は steps リストの値で置換される。

### Shaping（Skinner 流の反応形成）

`shaping` は連続近似によるセッション内反応形成を宣言する（Skinner, 1953; Catania, 2013）。`method` により脱糖先が変わる:

```
-- method=artful（既定）: 人間実行による連続近似
shaping KeyPeckShaping:
  target = "KeyPeck"
  method = artful
  approximations = ["orient", "approach", "contact", "peck"]
  -- CRF + @procedure("shape", ...) + ExperimenterJudgment criterion に脱糖

-- method=percentile: Platt (1973) / Galbicka (1994) に基づく自動化
shaping LeverForceShaping:
  target = "LeverPress"
  method = percentile
  dimension = force
  percentile_rank = 50
  stable(visual)
  -- Phase with Pctl(force, 50, window=20) schedule に脱糖

-- method=staged: 事前列挙された段階
shaping LeverPressShaping:
  target = "LeverPress"
  method = staged
  stages = [CRF, DRH 2-s, DRH 1-s]
  sessions >= 3
  -- 各 stage を phase とする progressive_decl に脱糖
```

`target` フィールドは必須（Galbicka の "clearly define the terminal response" ルールを強制）。

### Interleave（Recovery / 介在 baseline）

`interleave R` 句を `progressive_decl` に追加すると、生成された各 phase ペアの間に事前宣言された phase `R` の clone が挿入される。既定の意味論は **intercalate**（最後の phase の後にも clone が追加される）。`no_trailing` で intersperse に切り替え可能。

```
phase Recovery:                       -- progressive_decl より前に宣言（前方参照禁止）
  sessions >= 3
  stable(visual)
  FI 600-s(FR 30)
  @reinforcer("cocaine", dose="0.1mg/kg")

progressive DoseResponse:
  steps dose = [0.003, 0.01, 0.03, 0.1, 0.3, 0.56]
  interleave Recovery                 -- intercalate（既定）
  sessions >= 5
  stable(visual)
  FI 600-s(FR 30)
  @reinforcer("cocaine", dose="{dose}mg/kg")
```

`phase Recovery` 宣言は **template** となり、timeline には standalone で現れない。代わりに 6 つの clone（`Recovery_after_DoseResponse_1` … `Recovery_after_DoseResponse_6`）が 6 つの用量条件と交互に配置され、計 12 phase が得られる — John & Nader (2016) JEAB Method「*each dose was followed by a return to baseline*」と 1:1 で一致する。

複数の `interleave` 行は宣言順に gap block を構成する:

```
progressive DR:
  steps v = [2, 4, 8]
  interleave Recovery
  interleave Probe        -- gap = [Recovery_clone, Probe_clone]
  ...
```

---

## クイックリファレンス: 構文パターン一覧

| パターン | 種類 | 例 | 意味 |
|---------|------|-----|------|
| `XX##` | 原子 | `FR 5` | 固定比率 5 |
| `Comb(S, S, ...)` | 複合 | `Conc(VI 30-s, VI 60-s, COD=2-s)` | 並立スケジュール |
| `DRx##` | 修飾子 | `DRL 5-s` | 分化強化 |
| `Lag ##` | 修飾子 | `Lag 5` | 変動性要求 (Page & Neuringer, 1985) |
| `S LH##` | Limited Hold | `FI 30-s LH 10-s` | 時間的利用可能窓 |
| `XX##(YY##)` | **二次** | `FI 120-s(FR 10)` | Overall(Unit) |
| `let x = S` | 束縛 | `let a = VI 60-s` | 名前付きスケジュール |
| `Repeat(n, S)` | 糖衣構文 | `Repeat(3, FR 10)` | = `Tand(FR 10, FR 10, FR 10)` |
| `phase Name: ... S` | 実験 | `phase Baseline: sessions = 25 VI 60-s` | 基準付き名前付き phase |
| `progressive Name: steps x = [...] S({x})` | 実験 | `progressive FI: steps v=[2,4,8] FI {v}-s` | パラメトリック phase 漸進 |
| `shaping Name: target="X" method=artful` | 実験 | `shaping KeyPeck: target="KeyPeck" approximations=["orient","peck"]` | Skinner 流反応形成（CRF + @procedure + ExperimenterJudgment に脱糖） |
| `interleave R [no_trailing]` | 実験 | `interleave Recovery` | R-clone を間に挿入（intercalate 既定） |

---

## 参照文献

- Ferster, C. B., & Skinner, B. F. (1957). *Schedules of reinforcement*. Appleton-Century-Crofts.
- Fleshler, M., & Hoffman, H. S. (1962). A progression for generating variable-interval schedules. *JEAB*, *5*(4), 529-530. https://doi.org/10.1901/jeab.1962.5-529
- Kelleher, R. T. (1966). Conditioned reinforcement in second-order schedules. *JEAB*, *9*, 475. https://doi.org/10.1901/jeab.1966.9-475
- Kelleher, R. T., & Gollub, L. R. (1962). A review of positive conditioned reinforcement. *JEAB*, *5*(S4), 543-597. https://doi.org/10.1901/jeab.1962.5-s543
- Malagodi, E. F., DeWeese, J., & Johnston, J. M. (1973). Second-order schedules. *JEAB*, *20*(3), 447-461. https://doi.org/10.1901/jeab.1973.20-447
- Page, S., & Neuringer, A. (1985). Variability is an operant. *JEAP*, *11*(3), 429-452. https://doi.org/10.1037/0097-7403.11.3.429
- Catania, A. C. (2013). *Learning* (5th ed.). Sloan Publishing.
