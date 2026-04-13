# 設計根拠

本文書は DSL の設計判断が*なぜ*そうなったかを、実験文献への参照とともに説明する。`spec/` の規範的仕様を補完するものであり、仕様が文法が「何であるか」を述べるのに対し、本文書は「なぜそうであるか」を述べる。

---

## 1. DRO: 「他行動の強化」はなぜ誤称か

### 名称の問題

DRO は "Differential Reinforcement of Other behavior"（他行動の分化強化）の略称である。この名称は単純なメカニズムを示唆する: 標的行動が一定時間不在であれば、*何らかの他行動*が強化され、その代替行動が標的と競合して置換する。臨床家は数十年にわたりこの仮定のもとで実践してきた。

### 証拠が示すこと

Mazaleski, Iwata, Vollmer, Zarcone, and Smith (1993) は、自傷行為（SIB）を示す3名の個人を対象に DRO の2成分を分離した:

1. **強化成分** — SIB が一定時間不在のとき強化子を提供する
2. **消去成分** — SIB が発生したとき強化子を差し控える

3名中2名で、強化成分*単独*では無効であった。DRO が機能するには消去成分が必要であった。強化子の提供は必要でも十分でもなく、*差し控え*随伴性が機能していた。

Rey, Betz, Sleiman, Kuroda, and Podlesnik (2020a, 2020b) は DRO が「他行動」を偶発的に強化するかを直接検証した。他行動は DRO 初期に一過的に増加したが、長期セッションにわたって維持されなかった — 標的行動の抑制が持続しているにもかかわらず。DRO が代替行動の強化で機能するなら、代替行動は時間とともに強化されるはずである。そうはならなかった。

最新の Hronek and Kestner (2025) は実施エラーの非対称性を検証した。Commission error（標的行動後に誤って強化）は omission error（適格時に強化子を提供し忘れる）よりも DRO の有効性を著しく劣化させた。この非対称性は省略/消去説で予測されるが、代替強化説では予測されない。

### DSL への含意

現在の DSL は DRO を単一の時間パラメータ `DRO(omission_time)` で表現する。これは*省略随伴性*（標的反応が不在でなければならない持続時間）を捕捉する。名称 "DRO" は文献互換性のために保持するが、仕様はメカニズムが代替強化ではなく省略/消去であることを注記する。

Lindberg, Iwata, Kahng, and DeLeon (1999) は DRO を2つの直交次元で分解する 2×2 分類法を確立した:

|                | 固定インターバル | 変動インターバル |
|----------------|-----------------|-----------------|
| **全インターバル** | 伝統的 DRO: 標的がインターバル*全体*で不在 | VI-DRO: インターバル持続時間が変動 |
| **瞬時的** | インターバル終了時点のみ確認 | VM-DRO: 変動する時点で確認 |

現在の DSL は固定全インターバル DRO を実装する。完全な 2×2 分類法は v1.x に延期する。

### 参考文献

- Hronek, L. M., & Kestner, K. M. (2025). A human-operant evaluation of commission and omission errors during differential reinforcement of other behavior. *Journal of Applied Behavior Analysis*. https://doi.org/10.1002/jaba.70003
- Lindberg, J. S., Iwata, B. A., Kahng, S., & DeLeon, I. G. (1999). DRO contingencies: An analysis of variable-momentary schedules. *Journal of Applied Behavior Analysis*, *32*(2), 123-136. https://doi.org/10.1901/jaba.1999.32-123
- Mazaleski, J. L., Iwata, B. A., Vollmer, T. R., Zarcone, J. R., & Smith, R. G. (1993). Analysis of the reinforcement and extinction components in DRO contingencies with self-injury. *Journal of Applied Behavior Analysis*, *26*(2), 143-156. https://doi.org/10.1901/jaba.1993.26-143
- Rey, C. N., Betz, A. M., Sleiman, A. A., Kuroda, T., & Podlesnik, C. A. (2020a). The role of adventitious reinforcement during differential reinforcement of other behavior: A systematic replication. *Journal of Applied Behavior Analysis*, *53*(4), 2440-2449. https://doi.org/10.1002/jaba.678
- Rey, C. N., Betz, A. M., Sleiman, A. A., Kuroda, T., & Podlesnik, C. A. (2020b). Adventitious reinforcement during long-duration DRO exposure. *Journal of Applied Behavior Analysis*, *53*(3), 1716-1733. https://doi.org/10.1002/jaba.697

---

## 2. 累進比率（PR）: ステップ関数が必須である理由

### 問題

bare `PR` 文は、収集するデータの*種類*を変える選択を隠蔽する。2人の研究者を考える:

- **研究者 A** は `PR` と書き、`hodos`（算術: 1, 2, 3, 4, ...）を得る。反応率は線形に低下。Breakpoint は比率 47。
- **研究者 B** は同じ暗黙のデフォルトで `PR` と書く。しかし共同研究者は Richardson-Roberts 指数関数（1, 2, 4, 6, 9, 12, ...）を想定していた。Breakpoint は比率 95。

同じ薬物、同じ用量、同じ動物 — だが異なる breakpoint、異なる強化子効力の結論。暗黙のデフォルトが手続き上意味のある分岐を隠す。

### 文献が示すこと

**ステップ関数の形が反応率関数を変える。** Killeen, Posadas-Sanchez, Johansen, and Thrailkill (2009) はハトで算術と幾何プログレッションを直接比較した（実験1）。算術ステップでは反応率がコンポーネント比率にわたって*線形に*低下した。幾何ステップでは*負の加速度*で漸近線に向けて低下した。これは量的に異なるだけでなく — *質的に異なる関数形*である。

**Breakpoint はステップサイズに頑健だが他の指標はそうでない。** Stafford and Branch (1998) はハトで算術ステップサイズを変動させた。*最大完了比率*（breakpoint）はステップサイズの大きさに比較的非感受的であったが、*完了比率数*と*平均反応率*はステップサイズ増加とともに低下した。ステップ関数の選択がどの従属変数が有意義かを決定する。

**コンセンサスのあるデフォルトは存在しない。** 分野は収束していない:

| 伝統 | ステップ関数 | 典型的使用場面 |
|------|------------|--------------|
| Hodos (1961) | 算術（+定数） | PR 原著; 食餌強化 |
| Richardson & Roberts (1996) | 指数関数（5·e^(j/5) - 5） | 薬物自己投与; 単一セッション内で breakpoint に到達 |
| 線形 | カスタム start/increment の算術 | 柔軟; ヒトオペラント研究 |

### Breakpoint は Pmax ではない

行動薬理学での一般的仮定: 「PR breakpoint は動物がその薬物にいくら払う意思があるかを測定する。」これは PR を需要曲線経済学に写像し、Pmax（単位弾力性の価格）と alpha（本質的価値パラメータ）を対応させる。

Lambert et al. (2026, *JEAB*, n=96 障害のある成人) はこの写像を直接検証した:

- PR breakpoint は需要*強度*（Q₀ — ゼロ価格での消費量）と**相関した**
- PR breakpoint は需要*弾力性*（alpha）や *Pmax* とは**相関しなかった**

研究の問いが「この強化子はどれほど不可欠か?」（強度）であれば、PR breakpoint は有情報的である。問いが「どの価格で消費が弾力的になるか?」（Pmax）であれば、セッションをまたいだ系統的 FR 変動が必要であり、PR ではない。

### DSL の立場

DSL は `PR(hodos)`, `PR(linear, ...)`, `PR(exponential, ...)` の明示を要求する。これは意図的な摩擦である: 研究者にステップ関数へのコミットメントを強制し、スケジュール定義自体にそれを文書化させる。同僚がセッションファイルで `PR(exponential)` を読めば、プログレッション型は即座に可視的であり、ソフトウェアがどのデフォルトを仮定したかを確認する必要がない。

### 参考文献

- Bentzley, B. S., Fender, K. M., & Aston-Jones, G. (2013). The behavioral economics of drug self-administration: A review and new analytical approach for within-session procedures. *Psychopharmacology*, *226*(1), 113-125. https://doi.org/10.1007/s00213-012-2899-2
- Hodos, W. (1961). Progressive ratio as a measure of reward strength. *Science*, *134*(3483), 943-944. https://doi.org/10.1126/science.134.3483.943
- Killeen, P. R., Posadas-Sanchez, D., Johansen, E. B., & Thrailkill, E. A. (2009). Progressive ratio schedules of reinforcement. *Journal of Experimental Psychology: Animal Behavior Processes*, *35*(1), 35-50. https://doi.org/10.1037/a0012497
- Lambert, J. M., et al. (2026). Evaluating contributions of progressive ratio analysis to economic metrics of demand. *Journal of the Experimental Analysis of Behavior*. https://doi.org/10.1002/jeab.70077
- Richardson, N. R., & Roberts, D. C. S. (1996). Progressive ratio schedules in drug self-administration studies in rats. *Journal of Neuroscience Methods*, *66*(1), 1-11. https://doi.org/10.1016/0165-0270(95)00153-0
- Stafford, D., & Branch, M. N. (1998). Effects of step size and break-point criterion on progressive-ratio performance. *Journal of the Experimental Analysis of Behavior*, *70*(2), 123-138. https://doi.org/10.1901/jeab.1998.70-123

---

## 3. Lag: `length` が明示的である理由とオペラント次元論争

### パラメータの問題

Page and Neuringer (1985) が Lag スケジュールを導入した際、2キー・8ペック系列を使用した: ハトが左右のキーペックの文字列（例: LLRLRRLL）を8回産出し、その系列が直前 *n* 系列のいずれとも異なれば強化された。変動性の単位は8反応系列であった。

しかし後続の研究者は異なる系列長を選択した:

| 研究 | 系列長 | 種 |
|------|--------|---|
| Page & Neuringer (1985) | 8 | ハト |
| Abreu-Rodrigues, Lattal, & Santos (2005) | 4 | ハト |
| Ribeiro, Panetta, & Abreu-Rodrigues (2022) | 5 | ヒト |
| 応用 JABA 研究（Lee et al., 2002 等） | 1（個別反応） | ヒト |

標準は存在しない。可能なユニーク系列数は長さとともに指数的に増加し（2オペランダムで 2^k）、`length=4` で16通り、`length=8` で256通りとなる。Lag 5 要件は256通りでは容易に充足できるが16通りでは困難である。同じ `n` でも `length` によって行動的要求が異なる。

DSL が `length` の明示を要求する（省略時は応用研究の慣習に合わせ1をデフォルト）のはこのためである。デフォルトは利便性であり理論的コミットメントではない — そして theory.md は非標準性を文書化し、ユーザーが情報に基づく選択を行えるようにする。

### 変動性はオペラント次元か?

Lag スケジュールは強い主張に立脚する: *変動性そのもの*がオペラント次元である — 反応率や力と同様に、結果によって直接的に強化・弱化できる行動特性である。Page and Neuringer (1985) はこれを肯定した: Lag 随伴性は消去やスケジュール誘導効果では説明できない水準まで反応エントロピーを増加させた。

この主張には異論がある:

**Nergaard and Holth (2020)** は *Perspectives on Behavior Science* で体系的批判を展開した:

1. 強化遅延操作の下で変動性は*増加*する — 他のオペラント次元とは逆方向
2. 「反復の消去」がより節約的な説明: 反復された系列は非強化により消去され、変動的系列が消去法で残る
3. 系列レベルの U 値（標準的測度）が、強化が系列全体に操作しているのか個別反応に操作しているのかを不明瞭にしている可能性

Nergaard and Holth への正式な出版済み反論は見つかっていない。しかし:

**Reed (2023, *JEAB*)** は間接的な反証を提供した。ラット3実験で、シグナル付き強化（強化された反応を標識する短い刺激）が Lag-8 および DRLeast スケジュール下で変動性を*増加*させた。変動性要件がないスケジュールでは同じシグナルが変動性を*低下*させた。このパターン — シグナル操作が行動特性を他のオペラント次元と同じ方向に調整する — は変動性が直接強化されていることと整合する。

### DSL の立場

DSL は変動性が「真の」オペラント次元であるか否かについて立場を取らない。`Lag` は、基盤メカニズムに関わらず行動的効果が十分に文書化された手続きツールとして提供される。文法は中立である: Lag スケジュールが*何をするか*（直前 *n* 回と異なる系列を強化する）を定義するが、それが理論的に*何を意味するか*は定義しない。

これは DSL の一般的哲学と一致する: 仕様は随伴性配置を記述するのであり、行動メカニズムを記述するのではない。DRL パフォーマンスが「タイミング」なのか「カウンティング」なのか、DRO が「他行動の強化」なのか「省略訓練」なのか、Lag が「変動性の強化」なのか「反復の消去」なのか — これらは DSL が研究者に委ねる経験的問いである。

### 参考文献

- Galizio, A., Friedel, J. E., & Odum, A. L. (2020). An investigation of resurgence of reinforced behavioral variability in humans. *Journal of the Experimental Analysis of Behavior*, *114*(3), 381-393. https://doi.org/10.1002/jeab.637
- Nergaard, S. K., & Holth, P. (2020). A critical review of the support for variability as an operant dimension. *Perspectives on Behavior Science*, *43*(3), 579-603. https://doi.org/10.1007/s40614-020-00262-y
- Page, S., & Neuringer, A. (1985). Variability is an operant. *Journal of Experimental Psychology: Animal Behavior Processes*, *11*(3), 429-452. https://doi.org/10.1037/0097-7403.11.3.429
- Reed, P. (2023). Effect of signaled reinforcement on response variability. *Journal of the Experimental Analysis of Behavior*, *119*(2), 352-368. https://doi.org/10.1002/jeab.825
- Ribeiro, M. P., Panetta, N., & Abreu-Rodrigues, J. (2022). Effects of variability requirements on difficult sequence learning. *Journal of the Experimental Analysis of Behavior*, *118*(3), 442-461. https://doi.org/10.1002/jeab.798
