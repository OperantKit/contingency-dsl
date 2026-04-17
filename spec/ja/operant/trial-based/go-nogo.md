# Go/No-Go 弁別 — `GoNoGo`

> contingency-dsl Operant.TrialBased 下位層の一部。離散試行の継時弁別手続き。各試行で SD または SΔ が呈示され、被験体は反応窓の間に反応が生じるかどうかで採点される。

---

## 1. 起源

- Skinner, B. F. (1938). *The behavior of organisms: An experimental analysis*. Appleton-Century-Crofts.
- Terrace, H. S. (1963). Discrimination learning with and without "errors." *Journal of the Experimental Analysis of Behavior*, 6(1), 1–27. https://doi.org/10.1901/jeab.1963.6-1
- Dinsmoor, J. A. (1995a). Stimulus control: Part I. *The Behavior Analyst*, 18(1), 51–68.
- Nevin, J. A. (1969). Signal detection theory and operant behavior. *Journal of the Experimental Analysis of Behavior*, 12(3), 475–480. https://doi.org/10.1901/jeab.1969.12-475

## 2. 構文

```
GoNoGo(responseWindow=5s, consequence=CRF, ITI=10s)             -- 最小形
GoNoGo(responseWindow=5s, consequence=CRF, incorrect=FT10s,
       ITI=10s)                                                  -- 誤答指定
GoNoGo(responseWindow=5s, consequence=CRF, incorrect=EXT,
       falseAlarm=FT10s, ITI=15s)                                -- SDT スタイル
```

## 3. パラメータ

| パラメータ | 位置 | 型 | 必須 | デフォルト | 説明 |
|---|---|---|---|---|---|
| `responseWindow` | キーワード | 時間値 | YES | — | 反応機会の持続 |
| `consequence` | キーワード | スケジュール | YES | — | ヒット（Go + 反応）に対するオペラント・スケジュール |
| `incorrect` | キーワード | スケジュール | NO | `EXT` | 誤答（miss + フォールバックとしての false-alarm）に対するオペラント・スケジュール |
| `falseAlarm` | キーワード | スケジュール | NO | = `incorrect` | NoGo 誤答に対するオペラント・スケジュール（false alarm 時は `incorrect` を上書き） |
| `ITI` | キーワード | 時間値 | YES | — | 試行間隔 |

すべてのパラメータはキーワード限定である（位置引数なし）。

## 4. 試行状態機械

GoNoGo 試行は 4 状態の有限状態機械である。

```
         ┌──────────────────────────────────────┐
         │                                      │
         ▼                                      │
    ┌──────────┐                                │
    │ STIMULUS │  ← SD または SΔ 呈示            │
    └──────────┘    responseWindow 開始           │
         │                                      │
    ┌────┴────┐                                 │
    │         │                                 │
 response  window_expires                       │
    │         │                                 │
    ▼         ▼                                 │
┌──────────────┐                                │
│   EVALUATE   │                                │
└──────────────┘                                │
    │      │                                    │
 correct  incorrect                             │
    │      │                                    │
    ▼      ▼                                    │
┌──────────────┐                                │
│ CONSEQUENCE  │                                │
└──────────────┘                                │
         │                                      │
         ▼                                      │
    ┌─────────┐                                 │
    │   ITI   │─────────────────────────────────┘
    └─────────┘
```

状態: `Q = {STIMULUS, EVALUATE, CONSEQUENCE, ITI}`、初期 `q₀ = STIMULUS`、終端 `F = {ITI}`。

試行構造:

```
1. 刺激呈示               （SD または SΔ、単一刺激）
2. 反応窓                 （responseWindow 持続）
   ├─ 反応発生           → response=true で EVALUATE
   └─ 窓満了             → response=false で EVALUATE
3. 評価（2×2 結果行列）
   ├─ Go + 反応          → HIT               → consequence を実行
   ├─ Go + 反応なし      → MISS              → incorrect を実行
   ├─ NoGo + 反応        → FALSE ALARM       → falseAlarm を実行
   └─ NoGo + 反応なし    → CORRECT REJECTION → EXT（暗黙）
4. 試行間隔               （ITI 持続、すべての刺激オフ）
5. → 次試行
```

## 5. 2×2 結果行列

|  | 反応あり | 反応なし |
|---|---|---|
| **Go (SD)** | HIT → `consequence` | MISS → `incorrect` |
| **NoGo (SΔ)** | FALSE ALARM → `falseAlarm` | CORRECT REJECTION → EXT |

正しい拒否は常に EXT を生じる（計画された結果なし）。これは、反応を正しく withhold することに明示的な結果が伴わない標準 Go/No-Go 手続きを反映する（Dinsmoor, 1995a）。

## 6. 結果の非対称性

標準 Go/No-Go 手続きには本質的な結果非対称性が存在する: ヒットは強化されるが、正しい拒否には計画された結果がない。これは、すべての正答が同一の `consequence` スケジュールを受ける MTS とは対照的である。

この非対称性は **手続き的なものであり、設計上の制限ではない**。正しい拒否は SΔ 中の反応の *不在* によって定義される — 強化すべき反応が存在しない。正しい拒否を強化するには異なる随伴性（例: 試行内 DRO）が必要となる。これは別個の手続きであり将来の拡張として予約される。

`falseAlarm` パラメータは、false alarm が miss と異なる結果を受ける一般的な変種（通常はタイムアウト; Nevin, 1969）を許容する。これは、2 種類の誤答に差異的結果を与えることで反応バイアスを操作する signal-detection-theory 配置をモデル化する。

## 7. 結果パラメータ

`consequence`, `incorrect`, `falseAlarm` は MTS の結果パラメータと同一の制限に従う。

| 適切な選択 | 説明 |
|---|---|
| `CRF` / `FR 1` | すべてのヒットを強化（最も一般的） |
| `EXT` | フィードバックなし（プローブ試行、正しい拒否のデフォルト） |
| `FT 10-s` | タイムアウト（通常は `falseAlarm` または `incorrect` 用） |
| `VR 3` | 間欠強化（維持相） |

## 8. Signal Detection Theory 配置

`falseAlarm` パラメータは、SDT スタイルの非対称結果配置を可能にする（Nevin, 1969; Davison & Tustin, 1978）。

```
-- Nevin (1969) スタイル: false alarm → タイムアウト、miss → 消去
GoNoGo(responseWindow=5s, consequence=CRF, incorrect=EXT,
       falseAlarm=FT10s, ITI=15s)
```

2×2 結果行列は SDT 測度に直接対応する。

| SDT 測度 | 定義 |
|---|---|
| Hit rate | `P(response | Go stimulus)` |
| False alarm rate | `P(response | NoGo stimulus)` |
| 感度（log d） | Go と NoGo の弁別可能性 |
| バイアス（log b） | 反応ないし withhold する全体的傾向 |

これらは解析層で計算される導出行動測度であり、DSL パラメータではない。

## 9. 注釈

Go/No-Go は刺激指定と試行列パラメータのために注釈を用いる。

```
-- 刺激指定
@sd("tone", frequency=4000, duration=1s)
@s_delta("light", intensity=50)
@go_ratio(0.7)
GoNoGo(responseWindow=5s, consequence=CRF, incorrect=EXT,
       falseAlarm=FT10s, ITI=15s)

-- 無誤弁別（Terrace, 1963）
@fading(method="stimulus", steps=10)
GoNoGo(responseWindow=5s, consequence=CRF, ITI=10s)
```

## 10. 合成使用

```
-- 多元スケジュール: GoNoGo を消去と交替
Mult(GoNoGo(responseWindow=5s, consequence=CRF, ITI=10s), EXT)

-- 連鎖: FR5 の後に弁別試行
Chain(FR5, GoNoGo(responseWindow=5s, consequence=CRF, ITI=10s))

-- let 束縛: 訓練 vs プローブ
let training = GoNoGo(responseWindow=5s, consequence=CRF,
                       incorrect=EXT, falseAlarm=FT10s, ITI=15s)
let probe = GoNoGo(responseWindow=5s, consequence=EXT, ITI=15s)
Mult(training, probe)
```

## 11. Limited Hold との互換性

**GoNoGo + LH:** 意味論的に冗長である — `responseWindow` がすでに反応機会の持続を定義している。GoNoGo 上の LH はリンター WARNING を発する。LH < responseWindow の場合、LH が実効反応窓となる。

```
GoNoGo(responseWindow=5s, consequence=CRF, ITI=10s) LH 3-s   -- WARNING
```

## 12. 自由オペラント弁別との関係

Go/No-Go と `Mult(schedule, EXT)` は、異なる反応機会構造を用いて同じ継時弁別を実装する。

| | Go/No-Go | Mult(VI, EXT) |
|---|---|---|
| **反応機会** | 離散試行（1 試行あたり 1 反応） | 自由オペラント（連続） |
| **従属変数** | 正確性（ヒット率、FA 率） | 反応率 |
| **行動コントラスト** | 適用外（ベースライン率なし） | Reynolds (1961) |
| **SDT 解析** | 自然（2×2 行列） | 率から確率への変換が必要 |
| **DSL 表現** | `GoNoGo(...)` | `Mult(VI 30-s, EXT)` |

DSL はこれらを明示的に分離する。離散試行の継時弁別には `GoNoGo(...)`、自由オペラントの継時弁別には `Mult(schedule, EXT)` を用いる。

## 13. responseWindow パラメータ

`responseWindow` は GoNoGo の **構造パラメータ** であり、MTS における `comparisons` に類似する。

| | MTS | GoNoGo |
|---|---|---|
| **構造パラメータ** | `comparisons`（整数 ≥ 2） | `responseWindow`（ℝ⁺ × TimeUnit） |
| **それが定義するもの** | 選択代替肢の数 | 反応機会の持続 |
| **それがないと** | 選択タスクが成立しない | miss / CR の判定不能 |
| **Domain** | 無次元カウント | 時間持続 |

`responseWindow` がなければ、Go/No-Go 試行には STIMULUS 状態の定義された終端が無い — 「まだ反応していない」を「miss」や「正しい拒否」から原理的に区別する方法が存在しない。

## 14. 意味制約

| コード | 条件 | 重大度 |
|---|---|---|
| `GONOGO_NONPOSITIVE_RESPONSE_WINDOW` | `responseWindow ≤ 0` | SemanticError |
| `GONOGO_RESPONSE_WINDOW_TIME_UNIT_REQUIRED` | 時間単位を伴わない `responseWindow` | SemanticError |
| `MISSING_GONOGO_PARAM` | `responseWindow`, `consequence`, `ITI` のいずれかが省略 | SemanticError |
| `GONOGO_NONPOSITIVE_ITI` | `ITI ≤ 0` | SemanticError |
| `GONOGO_ITI_TIME_UNIT_REQUIRED` | 時間単位を伴わない `ITI` | SemanticError |
| `GONOGO_INVALID_CONSEQUENCE` | `consequence` / `incorrect` / `falseAlarm` が合成スケジュール | SemanticError |
| `GONOGO_RECURSIVE_CONSEQUENCE` | `consequence` / `incorrect` / `falseAlarm` が試行ベース・スケジュール | SemanticError |
| `DUPLICATE_GONOGO_KW_ARG` | キーワード引数の重複 | SemanticError |
| `GONOGO_SHORT_RESPONSE_WINDOW` | `responseWindow < 500ms` | WARNING |
| `GONOGO_LONG_RESPONSE_WINDOW` | `responseWindow > 60s` | WARNING |
| `GONOGO_NO_REINFORCEMENT` | `consequence=EXT` | WARNING |
| `GONOGO_SHORT_ITI` | `ITI < 1s` | WARNING |
| `GONOGO_LH_REDUNDANT` | `GoNoGo` に `LH` が適用された | WARNING |
| `GONOGO_FALSE_ALARM_WITHOUT_INCORRECT` | `falseAlarm` を指定して `incorrect` を省略 | WARNING |

## 15. 自由オペラント vs 離散試行の境界

Operant.Literal および Operant.Stateful のスケジュールは **自由オペラント** 反応機会を想定する。被験体は任意の時点で標的反応を発することができ、スケジュールは反応の連続ストリームを基準に照らして評価する。従属変数は反応率である（Skinner, 1938）。

Operant.TrialBased のスケジュール（MTS と GoNoGo）は **離散試行** 反応機会を想定する。実験者が構造化された刺激配置を呈示し、被験体は試行あたり一つだけの選択または Go／反応なし決定を発し、スケジュールはその決定を正答基準に照らして評価する。従属変数は正確性である。

この区別は手続き的なものであり、行動的なものではない — 実験者が配置するものを記述するのであって、被験体がすることを記述するのではない。平行する試行状態機械の議論は `operant/trial-based/mts.md §6` を参照。

## 16. 修飾子の非互換性

自由オペラント修飾子（DRL, DRH, DRO, Pctl, Lag）は試行ベース・スケジュールとは意味論的に非互換である。各修飾子は試行ベース手続きには存在しない自由オペラント反応ストリームの性質を仮定するからである。

- **DRL/DRH/Pctl** は連続ストリームからの反応間時間（IRT）を要求する。試行ベース手続きでは、「反応間の時間」は実験者制御事象（ITI, STIMULUS 状態）を含む構造化された時隔であり、IRT ではない。
- **DRO** は指定持続中の標的反応の不在を要求する。試行ベース手続きでは、ITI, SAMPLE, CONSEQUENCE 状態中は標的反応が *不可能* である — 反応不在は被験体の行動ではなく手続きによって強制される。
- **Lag** は直前の n 反応と異なる反応を強化する。MTS では正しい比較が見本で決定され、変動性要件ではない。MTS 正答基準との衝突が生じる。

コンビネータ（`Conc`, `Mult`, `Chain` 等）は試行ベース・スケジュールと併用可能である。これらは異なるレベルで作動する — スケジュールを相互に配置するのであり、スケジュールの反応ストリーム内で作動するのではない。

```
TRIAL_BASED_MODIFIER_INCOMPATIBLE:
  試行ベース・スケジュールに直接修飾子が適用された
```

## 参考文献

インライン参照を参照。追加の背景:

- Davison, M. C., & Tustin, R. D. (1978). The relation between the generalized matching law and signal-detection theory. *Journal of the Experimental Analysis of Behavior*, 29(2), 331–336. https://doi.org/10.1901/jeab.1978.29-331
- Reynolds, G. S. (1961). Behavioral contrast. *Journal of the Experimental Analysis of Behavior*, 4(1), 57–71. https://doi.org/10.1901/jeab.1961.4-57
