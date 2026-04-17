# Adjusting スケジュール — `Adj`

> contingency-dsl Operant.Stateful 下位層の一部。基準 = f(試行結果)。試行結果依存の双方向パラメータ調整。

---

## 1. 起源

- Blough, D. S. (1958). A method for obtaining psychophysical thresholds from the pigeon. *Journal of the Experimental Analysis of Behavior*, 1(1), 31–43. https://doi.org/10.1901/jeab.1958.1-31
- Mazur, J. E. (1987). An adjusting procedure for studying delayed reinforcement. In M. L. Commons et al. (Eds.), *Quantitative analyses of behavior* (Vol. 5, pp. 55–73). Erlbaum.
- Richards, J. B., Mitchell, S. H., de Wit, H., & Seiden, L. S. (1997). Determination of discount functions in rats with an adjusting-amount procedure. *Journal of the Experimental Analysis of Behavior*, 67(3), 353–366. https://doi.org/10.1901/jeab.1997.67-353

Adjusting スケジュールは、最近の試行結果に基づく双方向（増加／減少）のパラメータ適応を提供する。標準的な用途は、遅延割引の測定のための Mazur (1987) の adjusting-delay 手続きである。

## 2. 承認ゲート

`Adj` は `spec/en/design-philosophy.md §2.1` の下で Operant.Stateful に資格を有する。命名された手続きであり、一次文献（Blough, 1958; Mazur, 1987）を持ち、60 年以上の使用歴、広範な JEAB 掲載、遅延割引研究における研究室間再現、応用／翻訳的使用（ヒト選択実験）を有する。すべてのパラメータは宣言的である（ランタイムが調整方向を解釈するが、規則は解析時固定である）。

## 3. 構文

```
Adj(delay, start=10s, step=1s)                     -- 最小形
Adj(delay, start=10s, step=2s, min=0s, max=120s)   -- 境界付き
Adj(ratio, start=5, step=2)                        -- adjusting-ratio
Adj(amount, start=3, step=1, min=1, max=10)        -- adjusting-amount
Adjusting(delay, start=10s, step=1s)               -- 冗長なエイリアス
```

## 4. パラメータ

| パラメータ | 位置 | 型 | 必須 | デフォルト | 説明 |
|---|---|---|---|---|---|
| `target` | 位置 1 | enum | YES | — | 調整対象: `delay`, `ratio`, `amount` |
| `start` | キーワード | 値 | YES | — | 初期パラメータ値 |
| `step` | キーワード | 値 | YES | — | ステップごとの調整幅（加算） |
| `min` | キーワード | 値 | NO | なし | 調整後パラメータの下限 |
| `max` | キーワード | 値 | NO | なし | 調整後パラメータの上限 |

## 5. ターゲット次元

| Target | 調整対象パラメータ | 次元 | 暗黙のベース随伴性 | 参照 |
|---|---|---|---|---|
| `delay` | 強化遅延 | 時間（単位必須） | CRF + 調整遅延 | Mazur (1987) |
| `ratio` | 反応比率要件 | 無次元（整数） | Adjusting FR | Ferster & Skinner (1957) |
| `amount` | 強化子大きさ | 無次元（ランタイム解釈） | CRF + 調整大きさ | Richards et al. (1997) |

## 6. 意味論

```
P(t) を試行 t におけるパラメータ値とする。
P(0) = start.

各強化（または試行ブロック完了）後:
  「増加」基準が満たされた場合:  P(t+1) = clamp(P(t) + step, min, max)
  「減少」基準が満たされた場合:  P(t+1) = clamp(P(t) - step, min, max)
  いずれでもない場合:             P(t+1) = P(t)
```

**増加／減少方向規則** はランタイムに委譲される。DSL はパラメトリック構造を宣言し、調整アルゴリズム（例: Mazur の 4 試行ブロック多数決規則）はランタイム実装詳細である。これは VI 値生成における `@algorithm("fleshler-hoffman")` と同様の位置付けである。

## 7. 統合点

`Adj` は `modifier` ではなく `base_schedule` を拡張する。これは、Adj が強化基準を修飾するのではなく、独立した随伴性構造を定義するためである。これは `modifier` を拡張する `Pctl` とは異なる。

```ebnf
base_schedule ::= ... | adj_schedule
```

## 8. PR との関係

| | `PR(linear, start=1, increment=5)` | `Adj(ratio, start=5, step=2)` |
|---|---|---|
| 方向 | 単調増加のみ | 双方向（行動依存） |
| 変化規則 | 決定論的（強化ごとに固定増分） | 行動依存（最近のパフォーマンス） |
| 収束 | なし（破断点まで増加） | あり（無差異点） |
| 層 | Operant.Literal（schedules/progressive.md） | Operant.Stateful（本ファイル） |

区別基準: PR のステップ関数は強化数のみをインデックスとする。`Adj` は最近の試行結果に条件付けされる。

## 9. 意味制約

| コード | 条件 | 重大度 |
|---|---|---|
| `MISSING_ADJ_PARAM` | `start` または `step` が省略されている | SemanticError |
| `ADJ_UNKNOWN_TARGET` | `target` が列挙にない | SemanticError |
| `ADJ_NONPOSITIVE_START` | `start ≤ 0` | SemanticError |
| `ADJ_NONPOSITIVE_STEP` | `step ≤ 0` | SemanticError |
| `ADJ_TIME_UNIT_REQUIRED` | `delay` ターゲットで時間単位が欠如 | SemanticError |
| `ADJ_UNEXPECTED_TIME_UNIT` | `ratio` / `amount` ターゲットに時間単位 | SemanticError |
| `ADJ_INVALID_BOUNDS` | `min ≥ max` | SemanticError |
| `ADJ_START_OUT_OF_BOUNDS` | `start` が `[min, max]` の外 | SemanticError |
| `ADJ_RATIO_NOT_INTEGER` | `ratio` ターゲットで非整数値 | SemanticError |
| `DUPLICATE_ADJ_KW_ARG` | キーワード引数の重複 | SemanticError |
| `ADJ_UNBOUNDED_DELAY` | `max` を伴わない `delay` ターゲット | WARNING |
| `ADJ_LARGE_STEP` | `step > start` | WARNING |
| `ADJ_ZERO_MIN_DELAY` | `delay` ターゲットで `min=0` | WARNING |
| `ADJ_SUBUNIT_RATIO` | `ratio` ターゲットで `min < 1` | WARNING |

## 参考文献

一次ソースは §1 を参照。追加の背景:
- Ferster, C. B., & Skinner, B. F. (1957). *Schedules of reinforcement*. Appleton-Century-Crofts.
