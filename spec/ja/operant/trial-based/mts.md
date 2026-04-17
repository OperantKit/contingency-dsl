# Matching-to-Sample — `MTS`

> contingency-dsl Operant.TrialBased 下位層の一部。離散試行の条件性弁別手続き。被験体に見本刺激が呈示され、続いて比較刺激が呈示される。被験体は同一性基準または任意性基準の下、見本と合致する比較刺激を選択せねばならない。

---

## 1. 起源

- Cumming, W. W., & Berryman, R. (1965). The complex discriminated operant: Studies of matching-to-sample and related problems. In D. I. Mostofsky (Ed.), *Stimulus generalization* (pp. 284–330). Stanford University Press.
- Sidman, M. (1971). Reading and auditory-visual equivalences. *Journal of Speech and Hearing Research*, 14(1), 5–13. https://doi.org/10.1044/jshr.1401.05
- Sidman, M., & Tailby, W. (1982). Conditional discrimination vs. matching-to-sample: An expansion of the testing paradigm. *Journal of the Experimental Analysis of Behavior*, 37(1), 5–22. https://doi.org/10.1901/jeab.1982.37-5
- Blough, D. S. (1959). Delayed matching in the pigeon. *Journal of the Experimental Analysis of Behavior*, 2(2), 151–160. https://doi.org/10.1901/jeab.1959.2-151

## 2. 構文

```
MTS(comparisons=3, consequence=CRF, ITI=5s)                       -- 最小形
MTS(comparisons=3, consequence=CRF, incorrect=EXT, ITI=5s)        -- 誤答指定
MTS(comparisons=2, consequence=CRF, incorrect=FT5s, ITI=10s, type=identity)
                                                                   -- 完全指定
MTS(comparisons=3, consequence=CRF, ITI=5s, delay=5s)              -- DMTS
MTS(comparisons=3, consequence=CRF, ITI=5s, correction=true)       -- 訂正
MTS(comparisons=3, consequence=CRF, ITI=5s, delay=2s, correction=3) -- DMTS + 上限付き訂正
```

## 3. パラメータ

| パラメータ | 位置 | 型 | 必須 | デフォルト | 説明 |
|---|---|---|---|---|---|
| `comparisons` | キーワード | 正整数 ≥ 2 | YES | — | 試行あたりの比較刺激数 |
| `consequence` | キーワード | スケジュール | YES | — | 正反応に対するオペラント・スケジュール |
| `incorrect` | キーワード | スケジュール | NO | `EXT` | 誤反応に対するオペラント・スケジュール |
| `ITI` | キーワード | 時間値 | YES | — | 試行間隔 |
| `type` | キーワード | enum | NO | `"arbitrary"` | マッチング型: `"identity"` または `"arbitrary"` |
| `delay` | キーワード | 時間値 ≥ 0 | NO | `0s` | 見本 offset と比較 onset の間の保持時間。`delay=0s` は同時 MTS に等価、`delay>0` は DMTS（Blough, 1959）となる。 |
| `correction` | キーワード | boolean / 正整数 / `"repeat_until_correct"` | NO | `false` | 訂正手続き（Harrison, 1970）。`true` / `"repeat_until_correct"` は正答まで同一試行を繰り返す。正整数 `N` は再試行を `N` 回に制限する。 |

すべてのパラメータはキーワード限定である（位置引数なし）。

## 4. マッチング型

| Type | 正答の定義 | 参照 |
|---|---|---|
| `identity` | 見本と物理的に同一な比較を選択 | Cumming & Berryman (1965) |
| `arbitrary` | 見本と同じ刺激クラスに属する比較を選択 | Sidman (1971); Sidman & Tailby (1982) |

`type=arbitrary` の場合、クラス所属は `@stimulus_classes` 注釈で定義される（MTS プリミティブ自体では定義しない）。

## 5. 結果パラメータ

`consequence` と `incorrect` は、構文的には任意のオペラント `schedule` 式を受け付けるが、意味制約により制限される（合成および再帰的な試行ベース・スケジュールは拒否される）。典型的な選択:

| 適切な選択 | 説明 |
|---|---|
| `CRF` / `FR 1` | すべての正反応を強化（最も一般的） |
| `EXT` | フィードバックなし（プローブ試行） |
| `VR 3` | 間欠強化（部分強化） |
| `FT 5-s` | タイムアウト（通常は `incorrect` 用） |

## 6. 試行状態機械

MTS 試行は 5 状態の有限状態機械である。

```
         ┌──────────────────────────────────────────────┐
         │                                              │
         ▼                                              │
    ┌─────────┐     ┌────────────┐     ┌──────────┐    │
    │ SAMPLE  │────▶│ COMPARISON │────▶│ EVALUATE │    │
    └─────────┘     └────────────┘     └──────────┘    │
                                         │      │      │
                                    correct  incorrect  │
                                         │      │      │
                                         ▼      ▼      │
                                  ┌─────────────────┐   │
                                  │   CONSEQUENCE   │   │
                                  └────────┬────────┘   │
                                           │            │
                                           ▼            │
                                       ┌───────┐       │
                                       │  ITI  │───────┘
                                       └───────┘
```

状態集合: `Q = {SAMPLE, COMPARISON, EVALUATE, CONSEQUENCE, ITI}`、初期 `q₀ = SAMPLE`、終端 `F = {ITI}`。

試行構造:

```
1. 見本呈示
2. [delay > 0 の場合: 見本 offset → delay 秒 → 比較 onset]（DMTS）
3. 比較呈示             （comparisons 個の刺激、位置はランダム化）
4. 反応                 （被験体が 1 つの比較を選択）
5. 結果
   ├─ 正答   → consequence スケジュールを実行
   └─ 誤答   → incorrect スケジュールを実行
6. [訂正が有効な場合: correction_spec に従って試行を繰り返す]
7. 試行間隔             （ITI 持続、すべての刺激オフ）
8. → 次試行
```

正答の定義:

```
type=identity:   correct ⟺ response_stimulus == sample_stimulus
type=arbitrary:  correct ⟺ class(response_stimulus) == class(sample_stimulus)
```

## 7. DMTS（遅延）

`delay > 0` のとき、見本 offset の後に保持時間が挿入される（Delayed Matching-to-Sample; Blough, 1959）。保持時間中は見本が除去され、比較刺激はまだ呈示されない（標準 DMTS）。`delay=0s` は形式的に同時 MTS と等価である（既存の振る舞い）。明示的に書くことは意図の文書化である。

出版されたパラメトリック範囲は通常 0〜60 秒である（Grant, 1975; White, 1985）。`delay > 60s` は WARNING `MTS_LONG_DELAY` を発する。

## 8. 訂正手続き

誤反応時の扱いを宣言的に制御する（Harrison, 1970; Saunders & Green, 1999）。

```
correction=false                    → 誤答時に次試行へ進む（デフォルト）
correction=true                     → 正答まで同一試行を繰り返す
correction="repeat_until_correct"   → correction=true へ脱糖衣（冪等）
correction=N（整数 N ≥ 1）          → 最大 N 回繰り返してから進む
```

位置バイアスのリスク（Dube & McIlvane, 1996）に留意すること。Sidman の伝統では、等価性テスト試行は通常、訂正なし・分化強化なしで行う。`delay > 0` と `correction=true` / `"repeat_until_correct"` を組み合わせることは保持手続きと獲得手続きを混同させるため、WARNING `DMTS_WITH_CORRECTION` を発する。

## 9. AST 表現（正規化）

`delay` と `correction` は以下の規則で AST に具現化される。

| 表層構文 | AST |
|---|---|
| `delay` 省略 | `delay` / `delay_unit` フィールドなし |
| `delay=0s` | `delay: 0.0, delay_unit: "s"`（意図マーカー） |
| `delay=Xu`（X>0） | `delay: X, delay_unit: "u"` |
| `correction` 省略 | `correction` フィールドなし |
| `correction=false` | `correction: { mode: "disabled" }` |
| `correction=true` | `correction: { mode: "unlimited" }` |
| `correction="repeat_until_correct"` | `correction: { mode: "unlimited" }`（`true` と同一 AST、脱糖衣） |
| `correction=N`（N≥1） | `correction: { mode: "bounded", limit: N }` |

**省略形と明示形は AST レベルで区別可能である**（ラウンドトリップ保存のため）。ただし**ランタイム上は行動的に等価である**。下流の消費者（シミュレータ、リンター、ビジュアライザ）はこれらを同一として扱わねばならない（MUST）。

### 後方互換性

拡張前のプログラム `P`（`delay` も `correction` も含まない）に対して、現在のパーサは拡張前のパーサと同一の AST を生成する。`mts_kw_arg` 拡張は加法的である。拡張前の代替は `P` のトークン列に逐語的に一致し、新たな産出規則は `P` からは到達不能である。

### 警告発行順

単一の MTS 式に複数の警告が該当する場合、定義順（W1 → W2 → W3 → W4 → W5 → W7 → W8 → W9 → W1b）ですべて発行される。抑制や優先順位規則は適用されない。リンターはレポートで警告をグループ化してよい（MAY）が、いずれも捨ててはならない（MUST NOT）。

## 10. 刺激等価性と注釈

MTS は刺激等価性研究の手続き基盤である（Sidman, 1971）。DSL は関心事を分離する。

- **MTS プリミティブ** — 試行構造（呈示 → 選択 → 結果 → ITI）
- **注釈** — 刺激内容、クラス関係、訓練／テスト相、習得基準

```
-- 訓練相: AB 関係
@stimulus_classes(A=["A1","A2","A3"], B=["B1","B2","B3"])
@training(relations=["AB"], criterion=90, consecutive_blocks=2)
MTS(comparisons=3, consequence=CRF, incorrect=FT3s, ITI=5s)

-- テスト相: BA 対称性テスト
@stimulus_classes(A=["A1","A2","A3"], B=["B1","B2","B3"])
@testing(relations=["BA"], probe_ratio=1.0)
MTS(comparisons=3, consequence=EXT, ITI=5s)
```

訓練とテストは **同一の MTS プリミティブ** を用い、結果スケジュールと注釈のみが異なる。

### 追加注釈

セッション構造とプローブ混合方針については、`measurement-annotator` から 2 つのキーワードを用いる。

- **`@session(trials=N)`** / **`@session(blocks=K, block_size=M)`** — 試行ベースのセッション構造。JEAB Method セクションの「セッションあたり 72 試行」パターンを直接表現する。`annotations/measurement-annotator/README.md` の `@session` 節を参照。
- **`@probe_policy(baseline_reinforced, probe_ratio, interspersed, order)`** — 等価性テスト用の強く定義されたプローブ／ベースライン試行混合方針（Fields et al., 1997）。同 README の `@probe_policy` 節を参照。

例（Arntzen 2012 + Fields 1997 の推奨設定）:

```
@session(blocks=6, block_size=12)
@probe_policy(baseline_reinforced=true, probe_ratio=0.5)
@stimulus_classes(A=["A1","A2","A3"], B=["B1","B2","B3"])
@testing(relations=["BA"])
MTS(comparisons=3, consequence=CRF, ITI=5s)
```

## 11. 合成使用

```
-- 多元スケジュール: MTS を消去と交替
Mult(MTS(comparisons=3, consequence=CRF, ITI=5s), EXT)

-- 連鎖: FR5 の後に MTS 試行
Chain(FR5, MTS(comparisons=3, consequence=CRF, ITI=5s))

-- let 束縛
let ab_training = MTS(comparisons=3, consequence=CRF, incorrect=FT3s, ITI=5s)
let ba_test = MTS(comparisons=3, consequence=EXT, ITI=5s)
Mult(ab_training, ba_test)
```

## 12. Limited Hold との互換性

**MTS + LH:** LH は COMPARISON 状態内で反応窓を制約する。被験体が LH 持続内に比較を選択しない場合、試行は終了し `incorrect` が実行される。標準 MTS 手続き。

```
MTS(comparisons=3, consequence=CRF, ITI=5s) LH 10-s
```

| コード | 条件 | 重大度 |
|---|---|---|
| `MTS_LONG_LH` | MTS に `LH > 5min` | WARNING |

## 13. 意味制約

| コード | 条件 | 重大度 |
|---|---|---|
| `MTS_INVALID_COMPARISONS` | `comparisons < 2` または非整数 | SemanticError |
| `MTS_COMPARISONS_TIME_UNIT` | `comparisons` が時間単位を伴う | SemanticError |
| `MISSING_MTS_PARAM` | `consequence` または `ITI` が省略 | SemanticError |
| `MTS_NONPOSITIVE_ITI` | `ITI ≤ 0` | SemanticError |
| `MTS_ITI_TIME_UNIT_REQUIRED` | 時間単位を伴わない `ITI` | SemanticError |
| `MTS_INVALID_TYPE` | `type` が `"identity"` または `"arbitrary"` でない | SemanticError |
| `MTS_INVALID_CONSEQUENCE` | `consequence` が合成スケジュール | SemanticError |
| `MTS_RECURSIVE_CONSEQUENCE` | `consequence` が試行ベース・スケジュール | SemanticError |
| `DUPLICATE_MTS_KW_ARG` | キーワード引数の重複 | SemanticError |
| `MTS_INVALID_DELAY` | `delay < 0` | SemanticError |
| `MTS_DELAY_TIME_UNIT_REQUIRED` | 時間単位を伴わない `delay` | SemanticError |
| `MTS_CORRECTION_LIMIT_NONPOSITIVE` | `correction=N` で `N ≤ 0` | SemanticError |
| `MTS_INVALID_CORRECTION` | `correction` が boolean / 正整数 / `"repeat_until_correct"` のいずれでもない | SemanticError |
| `MTS_MANY_COMPARISONS` | `comparisons > 9` | WARNING |
| `MTS_TWO_COMPARISONS_WEAK`（W1b） | `comparisons = 2` — reject-control のみで 100% 正答となり select-control が検出不能になりうる（Sidman, 1987; Carrigan & Sidman, 1992） | WARNING |
| `MTS_NO_REINFORCEMENT` | `consequence=EXT` | WARNING |
| `MTS_IDENTITY_WITH_CLASSES` | `type=identity` に `@stimulus_classes` | WARNING |
| `MTS_ARBITRARY_WITHOUT_CLASSES` | `@stimulus_classes` のない `type=arbitrary` | WARNING |
| `MTS_SHORT_ITI` | `ITI < 1s` | WARNING |
| `DMTS_WITH_CORRECTION` | `delay > 0` かつ `correction=true` / `"repeat_until_correct"` | WARNING |
| `MTS_LONG_DELAY` | `delay > 60s` | WARNING |

## 14. DSL が表現しないもの

DSL は以下を表現しない。

1. **創発的関係**（反射性、対称性、推移性）— これらは MTS 訓練 *後* に観察される行動的帰結であり、手続き仕様ではない。
2. **派生刺激関係**（Hayes et al., 2001）— 等価性の根底にある *過程* に関する理論的構成。
3. **機能の転移** — 刺激クラス間で観察される行動現象。

これらは `operant/theory.md §2.6` で確立された手続き-効果境界に従う意図的な省略である。*DSL は手続きを規定する — 実験者が配置するもの。DSL は効果を予測しない — 有機体がすること。*

## 参考文献

インライン参照を参照。追加の背景:

- Carrigan, P. F., & Sidman, M. (1992). Conditional discrimination and equivalence relations: A theoretical analysis of control by negative stimuli. *Journal of the Experimental Analysis of Behavior*, 58(1), 183–204. https://doi.org/10.1901/jeab.1992.58-183
- Dube, W. V., & McIlvane, W. J. (1996). Implications of stimulus control topography analysis for emergent stimulus classes. In T. R. Zentall & P. M. Smeets (Eds.), *Stimulus class formation in humans and animals* (pp. 197–218). Elsevier.
- Fields, L., Adams, B. J., Buffington, D. M., Yang, W., & Verhave, T. (1997). Response transitions across and within testing trials: An ignored simultaneous discrimination. *Journal of the Experimental Analysis of Behavior*, 66(2), 323–339.
- Harrison, J. M. (1970). Effects of stimulus control procedures on discrimination learning. *Journal of the Experimental Analysis of Behavior*, 14(3), 345–351.
- Hayes, S. C., Barnes-Holmes, D., & Roche, B. (Eds.). (2001). *Relational frame theory: A post-Skinnerian account of human language and cognition*. Kluwer Academic/Plenum.
- Saunders, K. J., & Green, G. (1999). A discrimination analysis of training-structure effects on stimulus equivalence outcomes. *Journal of the Experimental Analysis of Behavior*, 72(1), 117–137. https://doi.org/10.1901/jeab.1999.72-117
- Sidman, M. (1987). Two choices are not enough. *Behavior Analysis*, 22(1), 11–18.
