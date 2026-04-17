# 時隔（反応非依存）スケジュール — FT, VT, RT

> contingency-dsl オペラント層の一部。反応非依存（非随伴的）の強化スケジュール。被験体が反応するかどうかに関わらず、時間基準で強化子が呈示される。

---

## 1. スコープ

これらのスケジュールは、3×3 アトミック分類（`operant/theory.md §1.1`）の Time 列を成す。パラメータ `t` は時間持続を指定する。強化は時間経過時に **反応から独立に** 呈示される（Zeiler, 1968; Lattal, 1972）。

| スケジュール | Distribution | 意味論 | 標準参照 |
|---|---|---|---|
| **FT(t)** | Fixed | `t` 秒ごとに強化子が呈示される | Zeiler (1968); Herrnstein & Morse (1957) |
| **VT(t)** | Variable | 平均 `t` の可変時隔で強化子が呈示される（Fleshler-Hoffman） | Zeiler (1968) |
| **RT(t)** | Random | 平均 `t` の無作為時隔で強化子が呈示される | Lachter, Cole, & Schoenfeld (1971) |

## 2. 操作的定義

### 2.1 FT — 固定時間

被験体の行動に関わらず、`t` 秒ごとに強化子が呈示される。反応要件はない。

```
FT 30-s     -- 30 秒ごとに強化子、反応非依存
```

特徴的な行動パターン: 反応非依存にもかかわらず正の加速（スキャロッピング）が観察される（Herrnstein & Morse, 1957; Zeiler, 1968）。これは、時間的規則性のみでオペラント随伴性なしにスキャロップ・パターンを生成しうる標準的デモンストレーションの一つである。

表示: `⟦Atomic(Fixed, Time, t)⟧`（`operant/theory.md §2.13.3` 参照）。反応事象は状態遷移や結果に影響しない。

### 2.2 VT — 変動時間

平均 `t` の Fleshler-Hoffman (1962) 系列からドローされた可変時隔で強化子が呈示される。

```
VT 60-s     -- 平均 60 秒、反応非依存
```

行動パターン: FT とは異なる定常または不規則な反応（Zeiler, 1968）。条件によっては、VT は従来の消去よりも緩やかな反応減衰を生成する（Lattal, 1972）。この非対称性は強化遅延研究で活用される。

### 2.3 RT — 無作為時間

強化子 onset は平均 onset 間隔 `t` の Poisson 過程に従う。VT とは異なり、RT は完全に無記憶である。

```
RT 60-s     -- Poisson 分布呈示、平均 60 秒
```

経験的には、RT は FT/VT ほど一般的に用いられない。最も近い標準例は Lachter, Cole, & Schoenfeld (1971)。

## 3. Time vs Interval — 反応非依存性

Time スケジュールは格子の **非随伴的** 列である。反応に関わらず強化子が呈示される。Interval スケジュール（FI, VI, RI; `operant/schedules/interval.md` 参照）は随伴的であり、時隔経過後の最初の反応が強化される。この区別は基盤的である — `foundations/contingency-types.md §1` を参照。

## 4. 迷信的強化

Skinner (1948) の「迷信」実験は FT 類似の手続きを用い、反応非依存の強化が迷信的強化を通じて特異的な反応トポグラフィを維持しうることを示した。したがって、Time スケジュールは中核の 3×3 格子と並んで、迷信的強化文献の中心である。

## 5. 反応非依存の強化遅延

タンデム `FT` は、非リセット型の信号化されない遅延の標準的形式化である（Sizemore & Lattal, 1978）。

```
Tand(VI 60-s, FT 5-s)        -- VI 満足後、反応に関わらず 5 秒待機
```

強化遅延の完全な扱いは `operant/theory.md §1.7` を参照。

## 6. Time スケジュールを含む合成

Time スケジュールは、すべての合成コンビネータに参加する（`operant/schedules/compound.md` 参照）。

```
Conc(VI 30-s, VT 60-s)          -- 並行の随伴的 vs 非随伴的比較
Mult(VI 60-s, VT 60-s)          -- Lachter (1971) 型の rate-matched 要素
Chain(FR 5, FT 30-s)            -- 連鎖された比率 → 時間リンク
```

Time スケジュールは反応非依存であるため、しばしば **対照条件** として機能し、反応随伴性の効果を測定する基準となる（Herrnstein & Morse, 1957; Rachlin & Baum, 1972）。

## 7. エラーと警告

| コード | 条件 | 重大度 |
|---|---|---|
| `ATOMIC_NONPOSITIVE_VALUE` | `t ≤ 0` | SemanticError |
| `ATOMIC_TIME_UNIT_REQUIRED` | 時間単位を伴わない時間スケジュール | SemanticError |

完全なレジストリは `conformance/operant/errors.json` を参照。

## 8. 設計上の決定

FT と VT は Catania (2013) および Zeiler (1968) によって形式的な Domain として標準化された。DSL は Time を、反応要件をゼロにした Interval の退化事例としてではなく、一級の Domain として扱う。これは手続き的事実を反映している。FT と VT は異なる行動パターンを生成し（Zeiler, 1968）、別個の実験的役割（対照条件、迷信的強化研究、遅延配置）を占める。

## 参考文献

- Catania, A. C. (2013). *Learning* (5th ed.). Sloan.
- Fleshler, M., & Hoffman, H. S. (1962). A progression for generating variable-interval schedules. *Journal of the Experimental Analysis of Behavior*, 5(4), 529–530. https://doi.org/10.1901/jeab.1962.5-529
- Herrnstein, R. J., & Morse, W. H. (1957). Some effects of response-independent positive reinforcement on maintained operant behavior. *Journal of Comparative and Physiological Psychology*, 50(5), 461–467. https://doi.org/10.1037/h0048673
- Lachter, G. D., Cole, B. K., & Schoenfeld, W. N. (1971). Some temporal parameters of non-contingent reinforcement. *Journal of the Experimental Analysis of Behavior*, 16(2), 207–217. https://doi.org/10.1901/jeab.1971.16-207
- Lattal, K. A. (1972). Response-reinforcer independence and conventional extinction after fixed-interval and variable-interval schedules. *Journal of the Experimental Analysis of Behavior*, 18(1), 133–140. https://doi.org/10.1901/jeab.1972.18-133
- Rachlin, H., & Baum, W. M. (1972). Effects of alternative reinforcement: Does the source matter? *Journal of the Experimental Analysis of Behavior*, 18(2), 231–241. https://doi.org/10.1901/jeab.1972.18-231
- Sizemore, O. J., & Lattal, K. A. (1978). Unsignalled delay of reinforcement in variable-interval schedules. *Journal of the Experimental Analysis of Behavior*, 30(2), 169–175. https://doi.org/10.1901/jeab.1978.30-169
- Skinner, B. F. (1948). 'Superstition' in the pigeon. *Journal of Experimental Psychology*, 38(2), 168–172. https://doi.org/10.1037/h0055873
- Zeiler, M. D. (1968). Fixed and variable schedules of response-independent reinforcement. *Journal of the Experimental Analysis of Behavior*, 11(4), 405–414. https://doi.org/10.1901/jeab.1968.11-405
