# Core-TrialBased 文法

> contingency-dsl 仕様の一部。Core-TrialBased 層の文法生成規則を記述する。
>
> 正式な EBNF は [schema/core-trial-based/grammar.ebnf](../../../schema/core-trial-based/grammar.ebnf) を参照。
> アーキテクチャ上の位置付けは [architecture.md §4.1](../architecture.md) を参照。

---

## 概要

Core-TrialBased スケジュールは Core 文法の `base_schedule` 生成規則に統合される:

```ebnf
base_schedule ::= ... | trial_based_schedule
```

Core-TrialBased スケジュールは Core / Core-Stateful と二つの独立した軸で区別される:

| 軸 | Core / Core-Stateful | Core-TrialBased |
|---|---|---|
| **反応機会の構造** | 自由オペラント（連続） | 離散試行 |
| **強化基準** | 反応数 / 時間 / 分布 | 刺激–反応マッチング |

### 構造的性質

1. **全プログラム共通** — program-scoped ではなく共有語彙
2. **CFG 構文** — 再帰下降 O(n) パーシング
3. **宣言的パラメータ** — 全パラメータがパース時に確定
4. **結果事象が明示的** — Core-TrialBased は `consequence` と `incorrect` を
   Core スケジュール式として受け取る。Core / Core-Stateful の暗黙的結果事象とは異なる

### Modifier との非互換性

Modifier（DRL, DRH, DRO, Pctl, Lag）は自由オペラント反応ストリームを前提とする。
離散試行スケジュールへの適用は SemanticError:

```
TRIAL_BASED_MODIFIER_INCOMPATIBLE:
  modifier が trial_based_schedule に直接適用された場合
```

Combinator（Conc, Mult, Chain 等）は構文的に許容。意味論的に不適切な
組み合わせは Linter WARNING で対処。

---

## §1. Matching-to-Sample — `MTS`

Cumming, W. W., & Berryman, R. (1965). The complex discriminated operant:
Studies of matching-to-sample and related problems. In D. I. Mostofsky
(Ed.), *Stimulus generalization* (pp. 284–330). Stanford University Press.

Sidman, M. (1971). Reading and auditory-visual equivalences. *Journal of
Speech and Hearing Research*, *14*(1), 5–13.
https://doi.org/10.1044/jshr.1401.05

Sidman, M., & Tailby, W. (1982). Conditional discrimination vs.
matching-to-sample. *JEAB*, *37*(1), 5–22.
https://doi.org/10.1901/jeab.1982.37-5

### 構文

```
MTS(comparisons=3, consequence=CRF, ITI=5s)                       -- 最小形
MTS(comparisons=3, consequence=CRF, incorrect=EXT, ITI=5s)        -- incorrect 指定
MTS(comparisons=2, consequence=CRF, incorrect=FT5s, ITI=10s, type=identity)
                                                                   -- 全パラメータ指定
```

### パラメータ

| パラメータ | 位置 | 型 | 必須 | デフォルト | 説明 |
|---|---|---|---|---|---|
| `comparisons` | keyword | 正整数 ≥ 2 | ✅ | — | 1 試行あたりの比較刺激数 |
| `consequence` | keyword | schedule | ✅ | — | 正答時の結果事象（Core スケジュール式） |
| `incorrect` | keyword | schedule | — | `EXT` | 誤答時の結果事象（Core スケジュール式） |
| `ITI` | keyword | 時間値 | ✅ | — | 試行間間隔 |
| `type` | keyword | 列挙型 | — | `"arbitrary"` | マッチング種別: `"identity"` or `"arbitrary"` |

全パラメータが keyword（positional 引数なし）。

### マッチング種別

| 種別 | 正答の定義 | 典拠 |
|---|---|---|
| `identity` | 見本と物理的に同一の比較刺激を選択 | Cumming & Berryman (1965) |
| `arbitrary` | 見本と同じ刺激クラスに属する比較刺激を選択 | Sidman (1971); Sidman & Tailby (1982) |

`type=arbitrary` の場合、クラス所属は `@stimulus_classes` アノテーションで定義する
（MTS primitive 自体では定義しない）。

### 結果事象パラメータ

`consequence` と `incorrect` は任意の Core `schedule` を構文上受け取るが、
意味制約で制限:

| 適切な値 | 説明 |
|---|---|
| `CRF` / `FR1` | 毎正答強化（最も一般的） |
| `EXT` | フィードバックなし（プローブ試行） |
| `VR3` | 間欠強化（部分強化） |
| `FT5s` | タイムアウト（通常 `incorrect` 用） |

### 試行構造（意味論）

```
1. 見本刺激提示
2. 比較刺激提示  （comparisons 個、位置ランダム化）
3. 反応           （被験体が比較刺激を 1 つ選択）
4. 結果事象
   ├─ 正答  → consequence スケジュールを実行
   └─ 誤答  → incorrect スケジュールを実行
5. 試行間間隔     （ITI、全刺激消去）
6. → 次の試行
```

正誤判定の定義:

```
type=identity:   correct ⟺ response_stimulus == sample_stimulus
type=arbitrary:  correct ⟺ class(response_stimulus) == class(sample_stimulus)
```

### 刺激等価性とアノテーション

MTS は刺激等価性研究（Sidman, 1971）の手続き的基盤。DSL は責務を分離する:

- **MTS primitive** — 試行構造（提示 → 選択 → 結果 → ITI）
- **アノテーション** — 刺激内容、クラス対応、訓練/テストフェーズ、mastery 基準

```
-- 訓練フェーズ: AB 関係
@stimulus_classes(A=["A1","A2","A3"], B=["B1","B2","B3"])
@training(relations=["AB"], criterion=90, consecutive_blocks=2)
MTS(comparisons=3, consequence=CRF, incorrect=FT3s, ITI=5s)

-- テストフェーズ: BA 対称性テスト
@stimulus_classes(A=["A1","A2","A3"], B=["B1","B2","B3"])
@testing(relations=["BA"], probe_ratio=1.0)
MTS(comparisons=3, consequence=EXT, ITI=5s)
```

訓練とテストで**同じ MTS primitive** を使用し、consequence と
アノテーションが異なる。

### 複合構文との組み合わせ

```
-- 多元スケジュール: MTS と消去を交替
Mult(MTS(comparisons=3, consequence=CRF, ITI=5s), EXT)

-- 連鎖: FR5 完了後に MTS 試行
Chain(FR5, MTS(comparisons=3, consequence=CRF, ITI=5s))

-- let binding
let ab_training = MTS(comparisons=3, consequence=CRF, incorrect=FT3s, ITI=5s)
let ba_test = MTS(comparisons=3, consequence=EXT, ITI=5s)
Mult(ab_training, ba_test)
```

### 意味論的制約

| コード | 条件 | 深刻度 |
|---|---|---|
| `MTS_INVALID_COMPARISONS` | comparisons < 2 or 非整数 | SemanticError |
| `MTS_COMPARISONS_TIME_UNIT` | comparisons に時間単位 | SemanticError |
| `MISSING_MTS_PARAM` | `consequence` or `ITI` 未指定 | SemanticError |
| `MTS_NONPOSITIVE_ITI` | ITI ≤ 0 | SemanticError |
| `MTS_ITI_TIME_UNIT_REQUIRED` | ITI に時間単位なし | SemanticError |
| `MTS_INVALID_TYPE` | type が `"identity"` / `"arbitrary"` でない | SemanticError |
| `MTS_INVALID_CONSEQUENCE` | consequence が compound schedule | SemanticError |
| `MTS_RECURSIVE_CONSEQUENCE` | consequence が trial_based_schedule | SemanticError |
| `DUPLICATE_MTS_KW_ARG` | keyword 引数の重複 | SemanticError |
| `MTS_MANY_COMPARISONS` | comparisons > 9 | WARNING |
| `MTS_NO_REINFORCEMENT` | consequence=EXT | WARNING |
| `MTS_IDENTITY_WITH_CLASSES` | type=identity で `@stimulus_classes` あり | WARNING |
| `MTS_ARBITRARY_WITHOUT_CLASSES` | type=arbitrary で `@stimulus_classes` なし | WARNING |
| `MTS_SHORT_ITI` | ITI < 1s | WARNING |

---

## §2. Go/No-Go 弁別 — `GoNoGo`

Skinner, B. F. (1938). *The behavior of organisms: An experimental
analysis*. Appleton-Century-Crofts.

Terrace, H. S. (1963). Discrimination learning with and without
"errors." *JEAB*, *6*(1), 1–27.
https://doi.org/10.1901/jeab.1963.6-1

Dinsmoor, J. A. (1995a). Stimulus control: Part I. *The Behavior
Analyst*, *18*(1), 51–68.

Nevin, J. A. (1969). Signal detection theory and operant behavior.
*JEAB*, *12*(3), 475–480.
https://doi.org/10.1901/jeab.1969.12-475

### 構文

```
GoNoGo(response_window=5s, consequence=CRF, ITI=10s)             -- 最小形
GoNoGo(response_window=5s, consequence=CRF, incorrect=FT10s,
       ITI=10s)                                                    -- incorrect 指定
GoNoGo(response_window=5s, consequence=CRF, incorrect=EXT,
       false_alarm=FT10s, ITI=15s)                                 -- SDT 型
```

### パラメータ

| パラメータ | 位置 | 型 | 必須 | デフォルト | 説明 |
|---|---|---|---|---|---|
| `response_window` | keyword | 時間値 | ✅ | — | 応答機会の持続時間 |
| `consequence` | keyword | schedule | ✅ | — | hit（Go + 応答）の結果事象 |
| `incorrect` | keyword | schedule | — | `EXT` | 誤答（miss + false alarm フォールバック）の結果事象 |
| `false_alarm` | keyword | schedule | — | = `incorrect` | NoGo 誤答専用の結果事象（`incorrect` を上書き） |
| `ITI` | keyword | 時間値 | ✅ | — | 試行間間隔 |

全パラメータが keyword（positional 引数なし）。

### 試行構造（意味論）

```
1. 刺激提示         （SD or SΔ、単一刺激）
2. 応答窓           （response_window の持続時間）
   ├─ 応答あり     → 応答=true で EVALUATE へ
   └─ 窓の終了     → 応答=false で EVALUATE へ
3. 評価（2×2 結果行列）
   ├─ Go + 応答     → HIT（正答）         → consequence を実行
   ├─ Go + 無応答   → MISS（オミッション） → incorrect を実行
   ├─ NoGo + 応答   → FALSE ALARM         → false_alarm を実行
   └─ NoGo + 無応答 → CORRECT REJECTION   → EXT（暗黙的、プログラムされた結果なし）
4. 試行間間隔       （ITI、全刺激消去）
5. → 次の試行
```

### 2×2 結果行列

|  | 応答あり | 応答なし |
|---|---|---|
| **Go (SD)** | HIT → `consequence` | MISS → `incorrect` |
| **NoGo (SΔ)** | FALSE ALARM → `false_alarm` | CORRECT REJECTION → EXT |

Correct rejection は常に EXT（プログラムされた結果なし）。標準的な Go/No-Go
手続きでは、正しい反応抑制に対して明示的な結果事象を伴わない（Dinsmoor, 1995a）。

### 結果事象パラメータ

`consequence`、`incorrect`、`false_alarm` は MTS の結果事象パラメータと
同じ制約に従う:

| 適切な値 | 説明 |
|---|---|
| `CRF` / `FR1` | 毎 hit 強化（最も一般的） |
| `EXT` | フィードバックなし（プローブ試行、correct rejection の既定） |
| `FT10s` | タイムアウト（通常 `false_alarm` / `incorrect` 用） |
| `VR3` | 間欠強化（維持フェーズ） |

### 信号検出理論的配置

`false_alarm` パラメータにより SDT 型の非対称結果配置が可能
（Nevin, 1969; Davison & Tustin, 1978）:

```
-- Nevin (1969) 型: false alarm → タイムアウト、miss → 消去
GoNoGo(response_window=5s, consequence=CRF, incorrect=EXT,
       false_alarm=FT10s, ITI=15s)
```

### アノテーション

```
-- 刺激仕様
@sd("tone", frequency=4000, duration=1s)
@s_delta("light", intensity=50)
@go_ratio(0.7)
GoNoGo(response_window=5s, consequence=CRF, incorrect=EXT,
       false_alarm=FT10s, ITI=15s)

-- errorless discrimination（Terrace, 1963）
@fading(method="stimulus", steps=10)
GoNoGo(response_window=5s, consequence=CRF, ITI=10s)
```

### 複合構文との組み合わせ

```
-- 多元スケジュール: GoNoGo と消去を交替
Mult(GoNoGo(response_window=5s, consequence=CRF, ITI=10s), EXT)

-- 連鎖: FR5 完了後に弁別試行
Chain(FR5, GoNoGo(response_window=5s, consequence=CRF, ITI=10s))

-- let binding: 訓練 vs プローブ
let training = GoNoGo(response_window=5s, consequence=CRF,
                       incorrect=EXT, false_alarm=FT10s, ITI=15s)
let probe = GoNoGo(response_window=5s, consequence=EXT, ITI=15s)
Mult(training, probe)
```

### 意味論的制約

| コード | 条件 | 深刻度 |
|---|---|---|
| `GONOGO_NONPOSITIVE_RESPONSE_WINDOW` | response_window ≤ 0 | SemanticError |
| `GONOGO_RESPONSE_WINDOW_TIME_UNIT_REQUIRED` | response_window に時間単位なし | SemanticError |
| `MISSING_GONOGO_PARAM` | `response_window`、`consequence`、`ITI` のいずれか未指定 | SemanticError |
| `GONOGO_NONPOSITIVE_ITI` | ITI ≤ 0 | SemanticError |
| `GONOGO_ITI_TIME_UNIT_REQUIRED` | ITI に時間単位なし | SemanticError |
| `GONOGO_INVALID_CONSEQUENCE` | consequence/incorrect/false_alarm が compound schedule | SemanticError |
| `GONOGO_RECURSIVE_CONSEQUENCE` | consequence/incorrect/false_alarm が trial_based_schedule | SemanticError |
| `DUPLICATE_GONOGO_KW_ARG` | keyword 引数の重複 | SemanticError |
| `GONOGO_SHORT_RESPONSE_WINDOW` | response_window < 500ms | WARNING |
| `GONOGO_LONG_RESPONSE_WINDOW` | response_window > 60s | WARNING |
| `GONOGO_NO_REINFORCEMENT` | consequence=EXT | WARNING |
| `GONOGO_SHORT_ITI` | ITI < 1s | WARNING |
| `GONOGO_LH_REDUNDANT` | LH が GoNoGo に適用 | WARNING |
| `GONOGO_FALSE_ALARM_WITHOUT_INCORRECT` | false_alarm 指定あり、incorrect 省略 | WARNING |
