# 合成スケジュール — Conc, Chain, Tand, Mult, Mix, Alt, Conj

> contingency-dsl オペラント層の一部。アトミック・オペラント格子上の 7 つの合成スケジュール・コンビネータ（並行・連鎖・タンデム・多元・混合・交替・連言配置）を定義する。連言スケジュールは、合成スケジュールの一変種としてここに含める（Herrnstein & Morse, 1958）。

---

## 1. 分類

合成スケジュールは、アトミック・スケジュール上の構造化された代数を成す。以下の 3 つの独立な意味論的次元に沿って分類する（完全な導出は `operant/theory.md §2.1` 参照）。

- **トポロジー** — 並列、逐次、交替。
- **弁別可能性** — 遷移を弁別刺激（SD）が信号化するかどうか。
- **満足論理** — OR（選言）、AND（連言）、独立、逐次、または文脈切替。

| スケジュール | 略記 | トポロジー | 弁別可能性 | 論理 | 操作手段 |
|---|---|---|---|---|---|
| Concurrent | Conc | 並列 | N/A（分離） | 独立 | 複数 |
| Alternative | Alt | 並列 | N/A | OR | 単一 |
| Conjunctive | Conj | 並列 | N/A | AND | 単一 |
| Chained | Chain | 逐次 | 弁別あり | 逐次 | 単一 |
| Tandem | Tand | 逐次 | 弁別なし | 逐次 | 単一 |
| Multiple | Mult | 交替 | 弁別あり | 文脈切替 | 単一 |
| Mixed | Mix | 交替 | 弁別なし | 文脈切替 | 単一 |

Chain/Tand および Mult/Mix は、同一トポロジー下の弁別あり／弁別なしの対である。

## 2. 代数的性質（要約）

定理、証明、健全な書換規則を伴う完全な代数は `operant/theory.md §2.2` にある。主要な性質:

- **交換性.** `Conc`, `Alt`, `Conj` は交換的である。`Chain`, `Tand`, `Mult`, `Mix` は非交換的である（逐次／交替の順序が意味を持つ）。
- **結合性.** 7 つすべてが N 項合成に平坦化できる。
- **単位元.** `Alt(S, EXT) ≡ S`, `Conj(S, CRF) ≡ S`, `Chain(CRF, S) ≡ S`。
- **零元.** `Conj(S, EXT) ≡ EXT`, `Alt(S, CRF) ≡ CRF`。
- **非分配性.** 括弧付けは構造的に有意であり、分配法則は適用されない。

## 3. 並行 — Conc

2 つ以上のスケジュールが異なる操作手段上で同時に作動する。被験体は自由に反応を配分し、各操作手段は固有の随伴性を維持する。

```
Conc(VI 30-s, VI 60-s, COD=2-s)
```

**切り替え遅延（COD; Catania, 1966）および固定比切り替え（FRCO; Hunter & Davison, 1985）** は `Conc` の構造パラメータである。

- `COD=Xs` — 操作手段の切り替え後、新たな操作手段上で強化子が利用可能になるまでの最小時間。
- `FRCO=N` — 切り替え後、新たな操作手段上で強化子が得られるまでに必要な最小反応数 N。

方向性 COD は非対称な切り替えコストを可能にする（Pliskoff, 1971; Williams & Bell, 1999）。

```
Conc(VI 30-s, VI 60-s, COD(1->2)=2-s, COD(2->1)=5-s)
```

COD/FRCO の完全な仕様、方向性意味論、base+override 規則については `operant/theory.md §2.4` を参照。

**標準参照:**
- Catania, A. C. (1966). Concurrent performances: Reinforcement interaction and response independence. *Journal of the Experimental Analysis of Behavior*, 9(5), 573–588. https://doi.org/10.1901/jeab.1966.9-573
- Herrnstein, R. J. (1961). Relative and absolute strength of response as a function of frequency of reinforcement. *Journal of the Experimental Analysis of Behavior*, 4(3), 267–272. https://doi.org/10.1901/jeab.1961.4-267
- Hunter, I., & Davison, M. (1985). Determination of a behavioral transfer function. *Journal of the Experimental Analysis of Behavior*, 43(1), 43–59. https://doi.org/10.1901/jeab.1985.43-43
- Shull, R. L., & Pliskoff, S. S. (1967). Changeover delay and concurrent schedules. *Journal of the Experimental Analysis of Behavior*, 10(6), 517–527. https://doi.org/10.1901/jeab.1967.10-517
- Findley, J. D. (1958). Preference and switching under concurrent scheduling. *Journal of the Experimental Analysis of Behavior*, 1(2), 123–144. https://doi.org/10.1901/jeab.1958.1-123

## 4. 連鎖 — Chain とタンデム — Tand

逐次コンビネータ: 1 つのスケジュール（リンク）を完了すると次のリンクへ制御が遷移する。最終リンクの強化が配置を終える。

- **Chain**: 各リンクは異なる弁別刺激（SD）と対応付けられる。SD の変化が遷移を信号化する。
- **Tand**: SD の変化は遷移を信号化しない。リンクは単一の刺激文脈を共有する。

```
Chain(FR 5, FI 30-s)       -- SD_A で FR 5、続いて SD_B で FI 30-s
Tand(VR 20, DRL 5-s)       -- SD 変化なしで VR 20 の後に DRL 5-s
```

表示レベルでは、`Chain` と `Tand` は同一の遷移構造を共有する。弁別可能性の違いはスケジュール機械の外部にある環境変数である（`operant/theory.md §2.13.4` 参照）。

**標準参照:**
- Ferster, C. B., & Skinner, B. F. (1957). *Schedules of reinforcement*. Appleton-Century-Crofts.（第 11〜12 章）
- Kelleher, R. T., & Fry, W. (1962). Stimulus functions in chained fixed-interval schedules. *Journal of the Experimental Analysis of Behavior*, 5(2), 167–173. https://doi.org/10.1901/jeab.1962.5-167
- Autor, S. M. (1969). The strength of conditioned reinforcers as a function of frequency and probability of reinforcement. In D. P. Hendry (Ed.), *Conditioned reinforcement* (pp. 127–162). Dorsey Press.

## 5. 多元 — Mult と混合 — Mix

交替コンビネータ: 要素は交替し、遷移は（被験体による現要素の満足ではなく）環境により制御される。

- **Mult**: 各要素は異なる SD と対応付けられる。行動コントラスト研究で用いられる。
- **Mix**: 要素は SD 変化なしで交替する。

```
Mult(VI 30-s, EXT, BO=5-s)       -- 要素間 5 秒ブラックアウト付き多元
Mix(FR 5, FR 10, BO=3-s)         -- ブラックアウト付き混合、弁別なし
```

**ブラックアウト（BO）** は要素間の反応非依存な暗期であり、`Conc` における COD の役割と構造的に対称である。BO 仕様は `operant/theory.md §2.5` を参照。

**標準参照:**
- Ferster, C. B., & Skinner, B. F. (1957). *Schedules of reinforcement*. Appleton-Century-Crofts.（第 13〜14 章）
- Reynolds, G. S. (1961). Behavioral contrast. *Journal of the Experimental Analysis of Behavior*, 4(1), 57–71. https://doi.org/10.1901/jeab.1961.4-57

## 6. 交替 — Alt

選言的並列コンビネータ: 最初に満足された要素が強化を引き起こし、その後すべての要素がリセットされる。

```
Alt(FR 10, FI 5-min)             -- FR 10 または FI 5-min が満たされれば強化
```

代数的に: `Alt(S, EXT) ≡ S`（単位元）、`Alt(S, CRF) ≡ CRF`（零元）。

## 7. 連言 — Conj（Herrnstein-Morse の連言 FR FI を含む）

連言的並列コンビネータ: 強化には **すべての** 要素が同時に満足されることが必要である。

```
Conj(FR 5, FI 30-s)              -- FR 5 AND FI 30-s の両方が満たされれば強化
```

**Herrnstein-Morse (1958) の連言 FR FI** は、1 つの FR 要素と 1 つの FI 要素に適用された `Conj` の特殊事例である。これは contingency-dsl の独立プリミティブではない。FR 引数と FI 引数を持つ `Conj` コンビネータがまさにこの配置を表現する。

```
Conj(FR 5, FI 30-s)              -- 連言 FR 5 FI 30（Herrnstein & Morse, 1958）
```

代数的に: `Conj(S, CRF) ≡ S`（単位元）、`Conj(S, EXT) ≡ EXT`（零元）。

## 8. 2 次スケジュール

2 次スケジュールは、2 つのアトミック・スケジュールを階層的役割に合成する — 内部単位スケジュールの完了を外部全体スケジュールが数える（Kelleher, 1966）。

```
FR 5(FI 30-s)      -- 各 FI 30 完了を 1 単位として扱い、5 単位後に強化
```

完全な仕様、短時間刺激要件（`@brief` 注釈）、`Repeat` への FR 全体スケジュールの等価性については `operant/theory.md §2.11` を参照。

## 9. 入れ子合成

すべてのコンビネータは再帰的に合成可能である。

```
Conc(Chain(FR 5, VI 60-s), Alt(FR 10, FT 30-s))
```

DSL 文法は任意の入れ子深さをサポートする。型システムは、すべての合成式がアトミックな葉で終端することを保証する（`foundations/theory.md §5` 参照）。

## 10. エラーと警告

| コード | 条件 | 重大度 |
|---|---|---|
| `COMPOUND_TOO_FEW_ARGS` | 位置引数が 2 個未満の合成 | SemanticError |
| `MISSING_COD` | COD 指定のない `Conc(VI, VI)` | WARNING |
| `INVALID_KEYWORD_ARG` | 特定のコンビネータ上の未知のキーワード | SemanticError |
| `DUPLICATE_KEYWORD_ARG` | 同じキーワードが 2 回出現 | SemanticError |

完全なレジストリは `conformance/operant/errors.json` を参照。

## 参考文献

各節のインライン参照を参照。合成スケジュール関連の追加文献:

- Autor, S. M. (1969). §4 参照。
- Ferster, C. B., & Skinner, B. F. (1957). *Schedules of reinforcement*. Appleton-Century-Crofts.
- Herrnstein, R. J. (1961). §3 参照。
- Herrnstein, R. J., & Morse, W. H. (1958). §7 参照。
- Kelleher, R. T. (1966). Conditioned reinforcement in second-order schedules. *Journal of the Experimental Analysis of Behavior*, 9(5), 475–485. https://doi.org/10.1901/jeab.1966.9-475
- Kelleher, R. T., & Fry, W. (1962). §4 参照。
- Shull, R. L., & Pliskoff, S. S. (1967). §3 参照。
- Findley, J. D. (1958). §3 参照。
