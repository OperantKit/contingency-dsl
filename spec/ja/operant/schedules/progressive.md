# Progressive Ratio（PR）および Progressive-Interval スケジュール

> contingency-dsl オペラント層の一部。パラメータ自身が、呈示された強化子の数でインデックスされる決定論的ステップ関数に従って変化するメタスケジュール。

---

## 1. スコープ

**Progressive スケジュール** とは、固定されたステップ関数に従って、パラメータが連続する強化子にわたって増加する（原理的には減少する）スケジュールである。標準的なメンバーは Hodos (1961) により導入された **Progressive Ratio（PR）** である。Progressive-interval 変種も同じ設計論理に従う（Hodos & Kalman, 1963）。

```
PR(step : ℕ → ℕ) = FR(step(n)) where n は各強化後にインクリメント
```

PR は **スケジュール関手** である — ステップ関数を FR スケジュールの列に写す。

## 2. 構文

DSL は 2 つの構文形式を提供する。

```
-- 短縮形: ステップサイズ n の算術進行
PR 5                                   -- Jarmolowicz & Lattal (2010)
                                       -- PR(linear, start=5, increment=5) に展開
                                       -- FR 5, FR 10, FR 15, ... を生成

-- 明示形: ステップ関数の完全な制御
PR(hodos)                              -- Hodos (1961) ステップ進行
PR(linear, start=1, increment=5)       -- 算術進行
PR(exponential)                        -- 指数進行
PR(geometric, start=1, ratio=2)        -- 幾何進行（倍増）
```

数値も括弧付きオプションも伴わない裸の `PR` はパースエラーである。

## 3. ステップ関数

| ステップ形式 | 例 | 進行 |
|---|---|---|
| `hodos` | `PR(hodos)` | Hodos (1961) 原版の不規則ステップ系列 |
| `linear`, `start=a`, `increment=d` | `PR(linear, start=5, increment=5)` | `a, a+d, a+2d, ...` |
| `exponential` | `PR(exponential)` | 強化ごとの指数的増加 |
| `geometric`, `start=a`, `ratio=r` | `PR(geometric, start=1, ratio=2)` | `a, a·r, a·r², ...` |

算術進行と幾何進行は質的に異なる反応率関数を生成する。文献にはデフォルトのステップ関数についての合意は存在しない（Killeen et al., 2009; Stafford & Branch, 1998）。DSL は明示的な指定を要求する — 裸の `PR` は許容されない。

## 4. 破断点（breakpoint）

**破断点** とは、それを超えると被験体が反応を停止する比率値であり、創発的な行動測度であって DSL パラメータではない。歴史的に、破断点は「最大効果的比率」（Pmax）と同義として扱われてきたが、この混同はますます問題視されつつある（Lambert et al., 2026）。DSL は手続き的構造のみを記録し、破断点の推定は解析層に属する。

## 5. Progressive-Interval

Progressive-interval スケジュールは類似の論理に従う: 時隔パラメータが連続する強化子にわたってステップ関数により増加する。これらは PR より文献で一般的ではなく、FI に適用される同一のステップ関数構文で対応される。

```
-- Progressive FI (Hodos & Kalman, 1963) 風配置は現在、
-- スケジュールレベルのプリミティブではなく、実験層の
-- `progressive` 宣言を通じて表現される。セッション間の
-- パラメータ進行は experiment/phase-sequence.md を参照。
```

これは意図的な設計上の決定である。Progressive Ratio プリミティブはスケジュールレベルに固定される。PR はセッション *内* で作動する（比率は強化ごとにインクリメントする）のに対し、progressive-interval の訓練計画は通常セッション間で作動するため、実験層で表現される。

## 6. 2 次 Progressive Ratio

`PR` は単位スケジュールと合成可能であり、各 PR ステップが単位完了を数える 2 次配置を生成する。

```
PR(linear, start=5, increment=5)         -- 個別反応上の 1 次 PR
                                        -- （セッション 1..N: 5, 10, 15, ...）
```

2 次 PR（`PR_n(Unit)`）は、`SecondOrder` 構成（`operant/theory.md §2.11`）と PR 意味論の組み合わせで表現可能である。

## 7. エラーと警告

| コード | 条件 | 重大度 |
|---|---|---|
| `PR_MISSING_STEP` | 数値も括弧オプションも伴わない裸の `PR` | SemanticError |
| `PR_NONPOSITIVE_START` | `start ≤ 0` | SemanticError |
| `PR_NONPOSITIVE_INCREMENT` | `increment ≤ 0` | SemanticError |
| `PR_NONPOSITIVE_RATIO` | geometric で `ratio ≤ 0` | SemanticError |
| `PR_UNKNOWN_STEP` | ステップキーワードが `{hodos, linear, exponential, geometric}` に含まれない | SemanticError |

完全なレジストリは `conformance/operant/errors.json` を参照。

## 8. PR vs Adjusting（Adj）

| | PR(linear, start=1, increment=5) | Adj(ratio, start=5, step=2) |
|---|---|---|
| 方向 | 単調増加のみ | 双方向（行動依存） |
| 変化規則 | 決定論的（強化ごとに固定増分） | 行動依存（最近のパフォーマンス） |
| 収束 | なし（破断点まで増加） | あり（無差異点） |
| 層 | Operant.Literal（schedules/） | Operant.Stateful（stateful/） |

Adjusting の対応物は `operant/stateful/adjusting.md` を参照。区別基準: PR のステップ関数は決定論的で、強化数のみをインデックスとする。Adj のステップは最近の試行結果に条件付けされる。

## 9. 設計上の決定

PR は、退化した `Tand(FR 5, FR 10, FR 15, ...)` ではなく、一級修飾子として DSL に導入された。理由は以下の通り。

1. ステップ関数の抽象化は手続き的に既約である — 研究者は個別の比率値ではなく「比率がどう成長するか」を指定する。
2. 文献標準の表記（`PR 5`, `PR(hodos)`）は直接パースできる必要がある。
3. 破断点は PR プリミティブに結び付く従属測度である。プリミティブを保存することは解析的ブリッジを保存する。

ステップ関数が明示的でなければならない理由の歴史的議論は `docs/en/design-rationale.md §2` を参照。

## 参考文献

- Hodos, W. (1961). Progressive ratio as a measure of reward strength. *Science*, 134(3483), 943–944. https://doi.org/10.1126/science.134.3483.943
- Hodos, W., & Kalman, G. (1963). Effects of increment size and reinforcer volume on progressive ratio performance. *Journal of the Experimental Analysis of Behavior*, 6(3), 387–392. https://doi.org/10.1901/jeab.1963.6-387
- Jarmolowicz, D. P., & Lattal, K. A. (2010). On distinguishing progressive increasing response requirements for reinforcement. *The Behavior Analyst*, 33(1), 119–125. https://doi.org/10.1007/BF03392206
- Killeen, P. R., Posadas-Sanchez, D., Johansen, E. B., & Thrailkill, E. A. (2009). Progressive ratio schedules of reinforcement. *Journal of Experimental Psychology: Animal Behavior Processes*, 35(1), 35–50. https://doi.org/10.1037/a0012497
- Stafford, D., & Branch, M. N. (1998). Effects of step size and break-point criterion on progressive-ratio performance. *Journal of the Experimental Analysis of Behavior*, 70(2), 123–138. https://doi.org/10.1901/jeab.1998.70-123
