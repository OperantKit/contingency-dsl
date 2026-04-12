# 構文ガイド

> contingency-dsl の構文を段階的に解説する。基本スケジュールから高度な構成まで。
> 形式文法（BNF）は [grammar.md](../../spec/ja/grammar.md) を参照。

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

---

## レベル 3: 修飾子

### 分化強化

```
DRL 5-s        -- 低率分化強化: IRT ≥ 5秒の場合のみ強化（ゆっくり反応）
DRH 2-s        -- 高率分化強化: IRT ≤ 2秒の場合のみ強化（速い反応）
DRO 10-s       -- 他行動分化強化: 標的行動なしで 10秒経過で強化
```

### 累進比率

```
PR(hodos)                       -- Hodos (1961) ステップ関数
PR(linear, start=1, increment=5) -- 線形: 1, 6, 11, 16, ...
PR(exponential)                 -- 指数的増加
```

### Percentile Schedule（Core-Stateful）

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
2. 各ユニット完了時に **brief stimulus**（条件性強化子）が提示されうる
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

## クイックリファレンス: 構文パターン一覧

| パターン | 種類 | 例 | 意味 |
|---------|------|-----|------|
| `XX##` | 原子 | `FR 5` | 固定比率 5 |
| `Comb(S, S, ...)` | 複合 | `Conc(VI 30-s, VI 60-s, COD=2-s)` | 並立スケジュール |
| `DRx##` | 修飾子 | `DRL 5-s` | 分化強化 |
| `S LH##` | Limited Hold | `FI 30-s LH 10-s` | 時間的利用可能窓 |
| `XX##(YY##)` | **二次** | `FI 120-s(FR 10)` | Overall(Unit) |
| `let x = S` | 束縛 | `let a = VI 60-s` | 名前付きスケジュール |
| `Repeat(n, S)` | 糖衣構文 | `Repeat(3, FR 10)` | = `Tand(FR 10, FR 10, FR 10)` |

---

## 参照文献

- Ferster, C. B., & Skinner, B. F. (1957). *Schedules of reinforcement*. Appleton-Century-Crofts.
- Fleshler, M., & Hoffman, H. S. (1962). A progression for generating variable-interval schedules. *JEAB*, *5*(4), 529-530. https://doi.org/10.1901/jeab.1962.5-529
- Kelleher, R. T. (1966). Conditioned reinforcement in second-order schedules. *JEAB*, *9*, 475. https://doi.org/10.1901/jeab.1966.9-475
- Kelleher, R. T., & Gollub, L. R. (1962). A review of positive conditioned reinforcement. *JEAB*, *5*(S4), 543-597. https://doi.org/10.1901/jeab.1962.5-s543
- Malagodi, E. F., DeWeese, J., & Johnston, J. M. (1973). Second-order schedules. *JEAB*, *20*(3), 447-461. https://doi.org/10.1901/jeab.1973.20-447
- Catania, A. C. (2013). *Learning* (5th ed.). Sloan Publishing.
