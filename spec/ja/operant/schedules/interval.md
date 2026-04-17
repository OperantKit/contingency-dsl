# 時隔スケジュール — FI, VI, RI

> contingency-dsl オペラント層の一部。時間に基づく強化スケジュールであり、時隔終了時点で反応要件を伴う。

---

## 1. スコープ

時隔スケジュールは、3×3 アトミック分類（`operant/theory.md §1.1`）の Interval 列を成す。パラメータ `t` は時間持続を指定する。強化は **時隔が経過した後の最初の反応** に随伴する — 時間要件と反応要件の連言である。

| スケジュール | Distribution | 意味論 | 標準参照 |
|---|---|---|---|
| **FI(t)** | Fixed | ちょうど `t` 秒経過後の最初の反応 | Ferster & Skinner (1957, 第 5 章) |
| **VI(t)** | Variable | 平均 `t` の可変時隔（Fleshler-Hoffman）後の最初の反応 | Ferster & Skinner (1957, 第 6 章); Fleshler & Hoffman (1962) |
| **RI(t)** | Random | 平均 `t` の無作為時隔（指数サンプリング）後の最初の反応 | Farmer (1963) |

## 2. 操作的定義

### 2.1 FI — 固定時隔

各強化の後、スケジュールはちょうど `t` 秒間待機する。`t` が経過した後の最初の反応が強化される。時隔中の反応は計画された効果を持たない。

```
FI 30-s     -- 30 秒後の最初の反応を強化
```

特徴的な行動パターン: 強化後休止を伴うスキャロップ反応または break-and-run 反応（Ferster & Skinner, 1957, 第 5 章）。

表示: `⟦Atomic(Fixed, Interval, t)⟧`（`operant/theory.md §2.13.3` 参照）。

### 2.2 VI — 変動時隔

各強化の後、スケジュールは平均 `t` 秒の Fleshler-Hoffman (1962) 系列からドローされた可変時隔を待機する。VI 生成器は以下を保証する。

- 平均時隔 = `t`
- 単位時間あたりの強化確率が（近似的に）一定
- 単一通過内で時隔値の重複なし

```
VI 60-s     -- 平均 60 秒時隔
VI 60 s     -- 同一スケジュール、空白区切り単位
VI 1-min    -- 分単位の等価表現
```

Fleshler-Hoffman (1962) アルゴリズムは JEAB 研究における VI 値生成の事実上の標準である。生成器は原論文で規定されている。実装は訂正された 12 時隔級数を使用するべきである。`procedure-annotator/temporal` の `@algorithm("fleshler-hoffman")` を参照。

### 2.3 RI — 無作為時隔

強化間時隔は平均 `t` の指数分布から独立にサンプルされる。VI とは異なり、RI は無記憶である。最終強化から時刻 `u` における強化確率は `u` に関わらず `1/t` である。

```
RI 60-s     -- 指数分布時隔、平均 60 秒
```

表示: `⟦Atomic(Random, Interval, t)⟧` はティックごとの Bernoulli サンプリングを用いる。

## 3. Interval vs Time — 反応要件

時隔スケジュール（FI, VI, RI）は **連言的** である: 時間 `t` の経過 (a) と反応 (b) の両方を要求する。時隔スケジュール（FT, VT, RT; `operant/schedules/time.md` 参照）は **反応非依存** である: 反応に関わらず時間閾値で強化子が呈示される。

この区別は Domain レベルで捉えられる: `Domain ∈ {Ratio, Interval, Time}`。

## 4. Limited Hold

時隔スケジュールは、時隔後の最初の反応が強化可能である時間窓を制限する **Limited Hold**（LH）限定子を一般に伴う。

```
FI 30-s LH 10-s      -- 時隔経過から 10 秒以内の最初の反応を強化
VI 60-s LH 5-s       -- VI 60、5 秒ホールド
```

LH の意味論は `operant/theory.md §1.6`、デフォルト伝播属性文法は §1.6.1、表層構文は `operant/grammar.md` を参照。

## 5. 時隔スケジュールを含む合成

時隔スケジュールは、すべての合成コンビネータに参加する（`operant/schedules/compound.md` 参照）。

```
Conc(VI 30-s, VI 60-s, COD=2-s)       -- 並行 VI-VI、マッチング法則の準備
Chain(FR 5, FI 30-s)                  -- 固定比率リンクに連鎖された固定時隔リンク
Mult(VI 30-s, EXT)                    -- 多元 VI-EXT（行動コントラスト・パラダイム）
```

**並行 VI-VI マッチング法則**（Herrnstein, 1961）は行動的帰結であり、DSL のパラメータではない。手続き-効果境界は `operant/theory.md §2.6` を参照。

## 6. 2 次時隔スケジュール

`FI t(Unit)` は、全体時隔と内部単位スケジュールを合成する（Kelleher, 1966）。

```
FI 300-s(FR 10)      -- 10 反応単位を 300 秒時隔でゲート
```

比率ベースの 2 次スケジュールとは異なり、時隔ベースの 2 次スケジュールは `Repeat` に **還元できない**。全体時隔は単位完了にまたがる時間構造を課す。`operant/theory.md §2.11.1` を参照。

## 7. エラーと警告

| コード | 条件 | 重大度 |
|---|---|---|
| `ATOMIC_NONPOSITIVE_VALUE` | `t ≤ 0` | SemanticError |
| `ATOMIC_INTERVAL_TIME_UNIT_REQUIRED` | 時間単位を伴わない時隔スケジュール | SemanticError |
| `MISSING_COD` | COD 指定のない `Conc(VI, VI)` | WARNING |

完全なレジストリは `conformance/operant/errors.json` を参照。

## 8. VI 値生成 — Fleshler-Hoffman アルゴリズム

Fleshler-Hoffman (1962) アルゴリズムは、単位時間あたりの反応確率が近似的に一定となるような VI 値系列を生成する。実装は原論文に文書化された訂正済み 12 値級数を使用するべきである。`contingency-py` および `contingency-rs` ランタイムパッケージは参照実装を提供する。Python マッピングは `implementation.md` を参照。

## 参考文献

- Farmer, J. (1963). Properties of behavior under random interval reinforcement schedules. *Journal of the Experimental Analysis of Behavior*, 6(4), 607–616. https://doi.org/10.1901/jeab.1963.6-607
- Ferster, C. B., & Skinner, B. F. (1957). *Schedules of reinforcement*. Appleton-Century-Crofts.
- Fleshler, M., & Hoffman, H. S. (1962). A progression for generating variable-interval schedules. *Journal of the Experimental Analysis of Behavior*, 5(4), 529–530. https://doi.org/10.1901/jeab.1962.5-529
- Herrnstein, R. J. (1961). Relative and absolute strength of response as a function of frequency of reinforcement. *Journal of the Experimental Analysis of Behavior*, 4(3), 267–272. https://doi.org/10.1901/jeab.1961.4-267
- Kelleher, R. T. (1966). Conditioned reinforcement in second-order schedules. *Journal of the Experimental Analysis of Behavior*, 9(5), 475–485. https://doi.org/10.1901/jeab.1966.9-475
