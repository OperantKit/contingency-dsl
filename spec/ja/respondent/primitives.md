# レスポンデント・プリミティブ — Tier A 仕様（R1〜R14）

> contingency-dsl レスポンデント層の一部。14 個の Tier A パヴロフ型プリミティブの操作的定義、パラメータ意味論、引用、例示的 DSL 用例。文法産出規則は `grammar.md`、理論的動機は `theory.md` を参照。拡張ポイントのプリミティブ（Tier B）は姉妹パッケージ `contingency-respondent-dsl` を参照。

---

## 構成

各プリミティブは以下を規定する:
- **標準的な DSL 綴り** — 文法レベルの形式。
- **操作的定義** — CS/US タイミング関係を正確に述べる。
- **パラメータ意味論** — 各引数が何を制御するか。
- **例** — 1 行の DSL 用例。
- **一次引用** — APA 7 形式、DOI 付き。
- **関連プリミティブ** — 他の Tier A 構成要素との関係。

---

## R1. `Pair.ForwardDelay(cs, us, isi, cs_duration)`

**操作的定義.** CS onset が生じる。`isi - cs_duration` の遅延（もしくは重複区間）の後、CS が存在したまま US が始まる。両者は同時に終了するか、CS が US offset の直前に終了する。前方遅延条件づけは標準的なパヴロフ型配置である: CS と US は **時間的に重なり**、CS onset が US onset に先行する。

**パラメータ意味論.**
- `cs` — 条件刺激の識別子または文字列ラベル。
- `us` — 無条件刺激の識別子または文字列ラベル。
- `isi` — CS onset から US onset までの刺激間時隔。
- `cs_duration` — CS の全持続。`cs_duration > isi` のとき CS と US は重なる。`cs_duration = isi` のとき CS offset = US onset（trace interval = 0 のトレース条件づけとの境界）。

**例.**
```
Pair.ForwardDelay(tone, shock, isi=10-s, cs_duration=15-s)
```

**一次引用.** Pavlov, I. P. (1927). *Conditioned reflexes: An investigation of the physiological activity of the cerebral cortex* (G. V. Anrep, Trans.). Oxford University Press.

**関連プリミティブ.** `cs_duration = isi` のとき R2（`Pair.ForwardTrace`）との境界（trace interval = 0）。随伴性空間の `(p=1, q=0)` 角に対応する（R8 参照）。

---

## R2. `Pair.ForwardTrace(cs, us, trace_interval)`

**操作的定義.** CS onset と offset が US onset に先行し、CS offset と US onset の間に持続 `trace_interval` の **トレース・ギャップ** があり、その間はどちらの刺激も存在しない。被験体は CR 獲得のためにトレース・ギャップを架橋せねばならない。

**パラメータ意味論.**
- `cs`, `us` — CS と US のラベル。
- `trace_interval` — CS offset から US onset までの空区間の持続。

**例.**
```
Pair.ForwardTrace(tone, food, trace_interval=5-s)
```

**一次引用.**
- Pavlov, I. P. (1927). *Conditioned reflexes*. Oxford University Press.
- Ellison, G. D. (1964). Differential salivary conditioning to traces. *Journal of Comparative and Physiological Psychology*, 57(3), 373–380. https://doi.org/10.1037/h0043484

**関連プリミティブ.** R1（前方遅延）と厳密に区別されるのは `trace_interval > 0` のとき。トレース条件づけは、同等の CS-US 時隔で遅延条件づけより弱い CR を生じるのが典型的である（Ellison, 1964）。

---

## R3. `Pair.Simultaneous(cs, us)`

**操作的定義.** CS onset が US onset と一致する（`isi = 0`）。CS と US は同時に、しばしば同一持続で呈示される。

**パラメータ意味論.**
- `cs`, `us` — CS と US のラベル。

**例.**
```
Pair.Simultaneous(light, airpuff)
```

**一次引用.** Rescorla, R. A. (1980). Simultaneous and successive associations in sensory preconditioning. *Journal of Experimental Psychology: Animal Behavior Processes*, 6(3), 207–216. https://doi.org/10.1037/0097-7403.6.3.207

**関連プリミティブ.** `isi = 0` で R1 との理論的境界。同時条件づけは前方遅延より弱い顕在的 CR を生じるのが典型的であるが、感覚前条件づけや訓練後テストで検出可能な CS-US 連合を生成する（Rescorla, 1980）。

---

## R4. `Pair.Backward(us, cs, isi)`

**操作的定義.** US onset が CS onset に先行する。標準手続きでは、US offset が CS onset の前に置かれ、`isi` で分離される。時間順に合わせるため、引数リストでは US 参照が最初に現れる。

**パラメータ意味論.**
- `us`, `cs` — US と CS のラベル（時間順に従い US が先）。
- `isi` — US offset から CS onset までの持続。

**例.**
```
Pair.Backward(shock, tone, isi=2-s)
```

**一次引用.** Spetch, M. L., Wilkie, D. M., & Pinel, J. P. J. (1981). Backward conditioning: A reevaluation of the empirical evidence. *Psychological Bulletin*, 89(1), 163–175. https://doi.org/10.1037/0033-2909.89.1.163

**関連プリミティブ.** 後方条件づけは、標準パラメータ下では興奮子ではなく **条件性抑制子** として機能することが多い（Spetch et al., 1981）。R1（前方遅延）との対比。

---

## R5. `Extinction(cs)`

**操作的定義.** 獲得履歴（典型的には `Pair.ForwardDelay` またはこれに類する）の後、CS は US なしで単独で呈示され、CR が減衰する。消去は元の連合を消去しない。それは文脈に感受性な抑制的連合を加える（Bouton, 2004）。

**パラメータ意味論.**
- `cs` — CS ラベル。先行訓練履歴は囲う `PhaseSequence` から継承される。フェーズ文脈外の裸の `Extinction(cs)` は、プログラムがデフォルトを定義しない限り意味的に不正である。

**例.**
```
Phase(name="acquisition", schedule=Pair.ForwardDelay(tone, shock, isi=10-s, cs_duration=15-s)),
Phase(name="extinction", schedule=Extinction(tone))
```

**一次引用.**
- Pavlov, I. P. (1927). *Conditioned reflexes*. Oxford University Press.
- Bouton, M. E. (2004). Context and behavioral processes in extinction. *Learning & Memory*, 11(5), 485–494. https://doi.org/10.1101/lm.78804

**関連プリミティブ.** R6（`CSOnly`）とは異なる — R6 はフェーズ非依存であり、先行獲得を前提としない。文脈感受性な消去特性に依存する現象（更新、再発、自発回復）はレスポンデント拡張ポイントに委譲される。

---

## R6. `CSOnly(cs, trials)`

**操作的定義.** CS は単独で `trials` 回呈示される。R5 と異なり、`CSOnly` はフェーズ非依存であり先行獲得を前提としない。ベースライン曝露（例: 潜在抑制手続きの前曝露フェーズ）やテスト・プローブに適する。

**パラメータ意味論.**
- `cs` — CS ラベル。
- `trials` — CS 単独呈示回数。

**例.**
```
Phase(name="pre_exposure", schedule=CSOnly(tone, trials=40))
```

**一次引用.** Lubow, R. E., & Moore, A. U. (1959). Latent inhibition: The effect of nonreinforced pre-exposure to the conditional stimulus. *Journal of Comparative and Physiological Psychology*, 52(4), 415–419. https://doi.org/10.1037/h0046700

**関連プリミティブ.** R5（`Extinction`）とはフェーズ非依存であることで異なる。命名された手続きとしての潜在抑制は Tier B であり `contingency-respondent-dsl` に属する。`CSOnly` はそのような手続きの構築元となる Tier A プリミティブである。

---

## R7. `USOnly(us, trials)`

**操作的定義.** US は CS なしに `trials` 回単独で呈示される。US 前曝露手続き、US への馴化、または統制条件として用いられる。

**パラメータ意味論.**
- `us` — US ラベル。
- `trials` — US 単独呈示回数。

**例.**
```
Phase(name="us_habituation", schedule=USOnly(shock, trials=20))
```

**一次引用.** Randich, A., & LoLordo, V. M. (1979). Associative and nonassociative theories of the UCS preexposure phenomenon. *Psychological Bulletin*, 86(3), 523–548. https://doi.org/10.1037/0033-2909.86.3.523

**関連プリミティブ.** US 前曝露効果（Tier B）は、`USOnly` に続く標準獲得フェーズから構築される。Tier A プリミティブは US 単独曝露自体のみを符号化する。

---

## R8. `Contingency(p_us_given_cs, p_us_given_no_cs)`

**操作的定義.** Rescorla (1967) 随伴性空間の任意の点をパラメータ化する。第一引数は `P(US | CS)`、第二引数は `P(US | ¬CS)` である。CS と US の事象ストリームは、これら 2 つの条件付き確率が十分長いセッションにわたって近似されるように生成される。引数順序は文法レベルで固定されており（CS 条件付きが先）、順列変更できない。

**パラメータ意味論.**
- `p_us_given_cs` — CS 呈示中／直後の US 確率、[0, 1]。
- `p_us_given_no_cs` — 試行間隔（CS なし）中の US 確率、[0, 1]。

**例.**
```
Contingency(0.9, 0.1)     -- 強い正の随伴性
Contingency(0.5, 0.5)     -- 対角線上（truly random）
Contingency(0.0, 0.3)     -- 負の随伴性（US は CS なしでのみ生じる）
```

**一次引用.**
- Rescorla, R. A. (1967). Pavlovian conditioning and its proper control procedures. *Psychological Review*, 74(1), 71–80. https://doi.org/10.1037/h0024109
- Rescorla, R. A. (1968). Probability of shock in the presence and absence of CS in fear conditioning. *Journal of Comparative and Physiological Psychology*, 66(1), 1–5. https://doi.org/10.1037/h0025984

**関連プリミティブ.** R9（`TrulyRandom`）は対角 `Contingency(p, p)` の糖衣である。R10（`ExplicitlyUnpaired`）は時間分離制約付きで `Contingency(0, q)` を精緻化する。Pair プリミティブ（R1〜R4）は `(1, 0)` 角付近の構造的特殊化である。

---

## R9. `TrulyRandom(cs, us)`

**操作的定義.** 随伴性空間の対角線上の点 `Contingency(p, p)` の構文糖衣であり、`P(US | CS) = P(US | ¬CS)` である。この配置の下では、CS は US についての予測情報を持たない。Rescorla (1967) はこれを CS-US 連合主張に対する正しい統制条件として提案した。

**パラメータ意味論.**
- `cs`, `us` — CS と US のラベル。
- オプション `p` キーワード引数（文法 §2.3 参照）は共有確率を指定する。デフォルトのプログラム・スコープ挙動はプログラムのレスポンデント・レジストリで規定される。

**例.**
```
TrulyRandom(tone, shock)
TrulyRandom(tone, shock, p=0.2)
```

**一次引用.** Rescorla, R. A. (1967). Pavlovian conditioning and its proper control procedures. *Psychological Review*, 74(1), 71–80. https://doi.org/10.1037/h0024109

**関連プリミティブ.** R8 の特殊事例。R10（`ExplicitlyUnpaired`）とは異なる: truly-random は CS 中または近傍での US 発生を禁じない。2 つの条件付き確率を等しくするだけである。

---

## R10. `ExplicitlyUnpaired(cs, us, min_separation)`

**操作的定義.** `Contingency(0, p)` に追加の時間制約を課す: US は試行間隔中のみに配置され、すべての US はすべての CS から最低 `min_separation` 分離される。このより厳格な統制は、truly-random 手続きへの批判に対応して導入された（Ayres, Benedict, & Witcher, 1975）。

**パラメータ意味論.**
- `cs`, `us` — CS と US のラベル。
- `min_separation` — CS 事象と US 事象の間の最小時間分離。典型的には秒で表現される。

**例.**
```
ExplicitlyUnpaired(tone, shock, min_separation=30-s)
```

**一次引用.**
- Rescorla, R. A. (1967). Pavlovian conditioning and its proper control procedures. *Psychological Review*, 74(1), 71–80. https://doi.org/10.1037/h0024109
- Ayres, J. J. B., Benedict, J. O., & Witcher, E. S. (1975). Systematic manipulation of individual events in a truly random control in rats. *Journal of Comparative and Physiological Psychology*, 88(1), 97–103. https://doi.org/10.1037/h0076200

**関連プリミティブ.** `p_us_given_cs = 0` を持つ R8 の精緻化。R9（`TrulyRandom`）とは `min_separation` 制約により異なる。この制約は偶発的短レイテンシ CS-US 共起を防ぐ。

---

## R11. `Compound(cs_list, mode=Simultaneous)`

**操作的定義.** 複数の CS が同時に呈示される。デフォルト `Simultaneous` モードでは、`cs_list` 中のすべての CS が onset と offset を共有する。他モードは拡張であり、Tier A では定義されない。

**パラメータ意味論.**
- `cs_list` — 2 つ以上の CS ラベル。
- `mode` — onset 協調モード。デフォルトは `Simultaneous`。他モードはレスポンデント拡張ポイントに属する。

**例.**
```
Compound([tone, light])                          -- デフォルトは mode=Simultaneous
Compound([tone, light], mode=Simultaneous)       -- 明示
```

**一次引用.** Rescorla, R. A., & Wagner, A. R. (1972). A theory of Pavlovian conditioning: Variations in the effectiveness of reinforcement and nonreinforcement. In A. H. Black & W. F. Prokasy (Eds.), *Classical conditioning II: Current research and theory* (pp. 64–99). Appleton-Century-Crofts.

**関連プリミティブ.** US との対提示（囲うフェーズレベル注釈を介す、あるいは合成 CS を許容する `Pair.*` 構成に埋め込む）は、ブロッキング、影かけ、関連 Tier B 手続きの基盤を成す。

**オペラント `Compound` との名称衝突.** オペラント層 AST（`schema/operant/ast.schema.json#/$defs/Compound`）は同じ識別子 `Compound` をスケジュール結合子（`Conc`, `Chain`, `Tand`, `Mult`, `Mix`, `Alt`, `Conj`）として用いる。両者は `"type": "Compound"` にシリアライズされるため、AST 判別子のみでは層の帰属を決定できない。両層を受け入れる消費側は payload 形状で分岐する必要がある: `{"combinator", "components"}` はオペラント Compound、`{"cs_list"}` はこのレスポンデント Compound を示す。この規則は各スキーマの `$comment` にも反映されている。

---

## R12. `Serial(cs_list, isi)`

**操作的定義.** CS は時間順で、CS 間時隔 `isi` を伴って呈示される。`Compound` と異なり、`Serial` は `mode` 引数を受け付けない — 直列性はすでに時間的順序を含意する。

**パラメータ意味論.**
- `cs_list` — 2 つ以上の CS ラベル、呈示順。
- `isi` — 連続する CS offset と onset の間の CS 間時隔。

**例.**
```
Serial([light, tone], isi=3-s)
```

**一次引用.** Rescorla, R. A. (1972). Informational variables in Pavlovian conditioning. In G. H. Bower (Ed.), *The psychology of learning and motivation* (Vol. 6, pp. 1–46). Academic Press. https://doi.org/10.1016/S0079-7421(08)60383-7

**関連プリミティブ.** 直列合成刺激は、Tier B の一部の feature-positive および feature-negative 手続きを含む、直列順序パヴロフ型配置の構造的基盤である。

---

## R13. `ITI(distribution, mean)`

**操作的定義.** 連続する CS-US または CS 単独試行の間の試行間隔。ITI は I/T 比を介した CR 獲得率の構造的決定因である（Gibbon & Balsam, 1981; Gallistel & Gibbon, 2000）。

**パラメータ意味論.**
- `distribution` — `fixed`, `uniform`, `exponential` のいずれか。
- `mean` — 平均 ITI 持続。

**例.**
```
ITI(exponential, mean=60-s)
ITI(fixed, mean=30-s)
```

**一次引用.**
- Gibbon, J., & Balsam, P. (1981). Spreading association in time. In C. M. Locurto, H. S. Terrace, & J. Gibbon (Eds.), *Autoshaping and conditioning theory* (pp. 219–253). Academic Press.
- Gallistel, C. R., & Gibbon, J. (2000). Time, rate, and conditioning. *Psychological Review*, 107(2), 289–344. https://doi.org/10.1037/0033-295X.107.2.289

**関連プリミティブ.** `@iti(distribution, mean, jitter)` 注釈（`annotations/extensions/respondent-annotator.md` 参照）と区別される: プリミティブは構造要素、注釈はジッターのメタデータを追加する。ジッターが無関係な場合、プリミティブ単独で十分である。

---

## R14. `Differential(cs_positive, cs_negative, us)`

**操作的定義.** 2 つの CS が対比的に訓練される: `cs_positive` はすべての強化試行で US と対提示される。`cs_negative` はすべての非強化試行で US なしで呈示される。この手続きはパヴロフ型弁別を確立する（CS+ に CR、CS− に CR なしまたは減弱 CR）。

**パラメータ意味論.**
- `cs_positive` — US と対提示される CS。
- `cs_negative` — US なしで呈示される CS。
- `us` — 強化試行で用いる US。完全形では明示される。短形式 `Differential(cs_positive, cs_negative)` はこれを省略し、囲う `@us` 注釈から推論する。

**例.**
```
Differential(tone_plus, tone_minus, shock)   -- 完全形
Differential(tone_plus, tone_minus)          -- 短形式; US は @us 注釈から
```

**一次引用.**
- Pavlov, I. P. (1927). *Conditioned reflexes*. Oxford University Press.
- Mackintosh, N. J. (1974). *The psychology of animal learning*. Academic Press.

**関連プリミティブ.** Tier A の根拠: R1（`Pair.ForwardDelay`）と R6（`CSOnly`）の合成として対比的意図を符号化することは、`cs_positive` と `cs_negative` が結合的に変えられているという実験者意図シグナルを失う。JEAB および関連誌は分化条件づけを一般的な手続きとして用いる。これを Tier A に昇格することで、拡張パッケージ設計における境界的ケースを避ける。feature-positive / feature-negative 変種および条件性抑制手続き（Rescorla, 1969）は Tier B に留まる。

---

## Tier A / Tier B 境界の要約

上記の Tier A 集合は、「随伴性空間（Rescorla, 1967）形式主義が直接命名する、または統制として要する基礎的レスポンデント手続きをカバーする」という意図の下で閉じている。操作的定義が **試行またはフェーズにまたがる構造的関係** を加える手続き（例: ブロッキングは合成 CS を伴う先行獲得フェーズを要する、更新は文脈変化を要する）は Tier B に置かれ、レスポンデント拡張ポイント（`contingency-respondent-dsl`）に委譲される。

---

## 集約参考文献

- Ayres, J. J. B., Benedict, J. O., & Witcher, E. S. (1975). Systematic manipulation of individual events in a truly random control in rats. *Journal of Comparative and Physiological Psychology*, 88(1), 97–103. https://doi.org/10.1037/h0076200
- Bouton, M. E. (2004). Context and behavioral processes in extinction. *Learning & Memory*, 11(5), 485–494. https://doi.org/10.1101/lm.78804
- Ellison, G. D. (1964). Differential salivary conditioning to traces. *Journal of Comparative and Physiological Psychology*, 57(3), 373–380. https://doi.org/10.1037/h0043484
- Gallistel, C. R., & Gibbon, J. (2000). Time, rate, and conditioning. *Psychological Review*, 107(2), 289–344. https://doi.org/10.1037/0033-295X.107.2.289
- Gibbon, J., & Balsam, P. (1981). Spreading association in time. In C. M. Locurto, H. S. Terrace, & J. Gibbon (Eds.), *Autoshaping and conditioning theory* (pp. 219–253). Academic Press.
- Lubow, R. E., & Moore, A. U. (1959). Latent inhibition: The effect of nonreinforced pre-exposure to the conditional stimulus. *Journal of Comparative and Physiological Psychology*, 52(4), 415–419. https://doi.org/10.1037/h0046700
- Mackintosh, N. J. (1974). *The psychology of animal learning*. Academic Press.
- Pavlov, I. P. (1927). *Conditioned reflexes: An investigation of the physiological activity of the cerebral cortex* (G. V. Anrep, Trans.). Oxford University Press.
- Randich, A., & LoLordo, V. M. (1979). Associative and nonassociative theories of the UCS preexposure phenomenon. *Psychological Bulletin*, 86(3), 523–548. https://doi.org/10.1037/0033-2909.86.3.523
- Rescorla, R. A. (1967). Pavlovian conditioning and its proper control procedures. *Psychological Review*, 74(1), 71–80. https://doi.org/10.1037/h0024109
- Rescorla, R. A. (1968). Probability of shock in the presence and absence of CS in fear conditioning. *Journal of Comparative and Physiological Psychology*, 66(1), 1–5. https://doi.org/10.1037/h0025984
- Rescorla, R. A. (1969). Pavlovian conditioned inhibition. *Psychological Bulletin*, 72(2), 77–94. https://doi.org/10.1037/h0027760
- Rescorla, R. A. (1972). Informational variables in Pavlovian conditioning. In G. H. Bower (Ed.), *The psychology of learning and motivation* (Vol. 6, pp. 1–46). Academic Press. https://doi.org/10.1016/S0079-7421(08)60383-7
- Rescorla, R. A. (1980). Simultaneous and successive associations in sensory preconditioning. *Journal of Experimental Psychology: Animal Behavior Processes*, 6(3), 207–216. https://doi.org/10.1037/0097-7403.6.3.207
- Rescorla, R. A., & Wagner, A. R. (1972). A theory of Pavlovian conditioning: Variations in the effectiveness of reinforcement and nonreinforcement. In A. H. Black & W. F. Prokasy (Eds.), *Classical conditioning II: Current research and theory* (pp. 64–99). Appleton-Century-Crofts.
- Spetch, M. L., Wilkie, D. M., & Pinel, J. P. J. (1981). Backward conditioning: A reevaluation of the empirical evidence. *Psychological Bulletin*, 89(1), 163–175. https://doi.org/10.1037/0033-2909.89.1.163
