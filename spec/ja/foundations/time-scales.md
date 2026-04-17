# 時間スケール — Trial, Session, Phase, ITI; モル vs 分子

> contingency-dsl 基盤層の一部。仕様全体で用いられる標準的な時間スケール語彙を固定する。パラダイム層はこれらの定義を再利用し、再定義はしない。

---

## 1. 構造的時間単位

DSL は、持続時間の順に配列された 4 つの構造的時間単位を認識する。

| 単位 | 定義 | パラメータ化場所 |
|---|---|---|
| **Tick** | 表示意味論で用いられる最小時間粒度（`Tick(t)` 事象はクロック進行を示す）。 | `operant/theory.md §2.13` |
| **Trial** | 開始と終了が定義された手続きの有界単位（例: レスポンデントにおける CS onset → ITI 終了、試行ベース・オペラントにおける sample → ITI 終了）。 | `operant/trial-based/*.md`, レスポンデント文法 |
| **Session** | 単一のスケジュール式下にある試行および／または自由オペラント時間の連続ブロック。 | `annotations/extensions/measurement-annotator`（`@session`, `@session_end`） |
| **Phase** | 共有されたスケジュール式と共有された相変化基準の下にある、1 つ以上のセッションからなる順序付きセグメント。 | `experiment/phase-sequence.md` |

完全な実験計画はフェーズの列である。各フェーズは 1 つ以上のセッションから成り、各セッションは（試行ベースのパラダイムでは）1 つ以上の試行から、あるいは（自由オペラント・パラダイムでは）連続した自由オペラント・ストリームから構成される。

## 2. 試行間隔（ITI）

**定義 1（ITI）.** 試行間隔とは、連続する 2 つの試行の間の時間である。*試行開始から次の試行開始まで* で測定される（あるいは、パラダイムの慣習に応じて、試行 *k* の終了と試行 *k+1* の開始の間の間隔として測定される）。

ITI は 2 つの役割で現れる。

- **プリミティブレベル**（レスポンデント層）: `ITI(distribution, mean)` は Tier A の構造プリミティブである。これは I/T 比（CS 持続時間と ITI の比）が条件反応の獲得速度の主要決定因であるためである（Gibbon & Balsam, 1981; Gallistel & Gibbon, 2000）。
- **注釈レベル**: `@iti(distribution, mean, jitter)`（`respondent-annotator` の一部）は分布的な精緻化（ジッター、サンプリング方法）を提供し、フェーズや試行ブロックに付与されうる。

プリミティブは構造パラメータ（分布、平均）のみを保持し、分布的精緻化は注釈の関心事である。両形式とも適合性テストにおいて同一の平均 ITI 行動変数に解決される。

## 3. モル vs 分子の時間スケール

実験行動分析には、確立された 2 つの時間スケール分析があり、DSL はどちらにも偏らずに対応せねばならない。

**定義 2（分子分析）.** 個々の反応とその即時結果のレベルでの分析。従属変数には、反応間時間（IRT）分布、強化後休止の持続時間、反応単位の選択パターンが含まれる。標準参照: Skinner（1938）, Herrnstein（1961）, Baum（1973）。

**定義 3（モル分析）.** 拡張された時間区間（セッション、フェーズ）にわたる集約的速度および確率のレベルでの分析。従属変数には、セッション反応率、マッチング法則比、全体的な選択比が含まれる。標準参照: Baum（2002, 2004）, Rachlin（1978）。

両分析は同一の手続きプリミティブ上で作動する。違いは、行動データストリームに適用される観測窓にある。DSL は基盤レベルで **モル／分子中立** である。

- スケジュール式（例: `VI 60-s`, `Conc(VI 30-s, VI 60-s)`）は、どちらのスケールでも分析可能な随伴性構造を記述する。
- `@session_end`, `@dependent_measure`, `@steady_state`（measurement-annotator）は、モルまたは分子のいずれの従属変数も指定できる。
- いかなる文法構成要素も、一方の分析を他方より特権化しない。

この中立性は構造的に重要である。DSL レベルで一方のスケールにコミットすれば、文献の半分を排除することになる。

## 4. 文法中の時間単位

時間位置の数値は、`{s, ms, min}` から明示的な単位サフィックスを伴う。時間位置の裸の数値は、パラダイム層の仕様に応じて、拒否される（strict モード）か、秒と仮定される（lint-warning モード）。時間単位の同一性は AST に保存される（`time_unit: "s" | "ms" | "min"`）ため、ラウンドトリップ・シリアライズは元の表記を再現する。

## 5. この層で **定義しない** もの

- **試行内タイミング**（刺激呈示レイテンシ、反応評価レイテンシ）はランタイムの関心事であり、DSL の関心事ではない。
- **実時間 vs 模擬時間** のクロック源は `procedure-annotator/temporal` における `@clock(...)` 注釈で付与され、基盤層には属さない。
- **フェーズ間の時間ワープ**（例: 圧縮リプレイ）は DSL のスコープ外である。

## 参考文献

- Baum, W. M. (1973). The correlation-based law of effect. *Journal of the Experimental Analysis of Behavior*, 20(1), 137–153. https://doi.org/10.1901/jeab.1973.20-137
- Baum, W. M. (2002). From molecular to molar: A paradigm shift in behavior analysis. *Journal of the Experimental Analysis of Behavior*, 78(1), 95–116. https://doi.org/10.1901/jeab.2002.78-95
- Baum, W. M. (2004). Molar and molecular views of choice. *Behavioural Processes*, 66(3), 349–359. https://doi.org/10.1016/j.beproc.2004.03.013
- Gallistel, C. R., & Gibbon, J. (2000). Time, rate, and conditioning. *Psychological Review*, 107(2), 289–344. https://doi.org/10.1037/0033-295X.107.2.289
- Gibbon, J., & Balsam, P. (1981). Spreading association in time. In C. M. Locurto, H. S. Terrace, & J. Gibbon (Eds.), *Autoshaping and conditioning theory* (pp. 219–253). Academic Press.
- Herrnstein, R. J. (1961). Relative and absolute strength of response as a function of frequency of reinforcement. *Journal of the Experimental Analysis of Behavior*, 4(3), 267–272. https://doi.org/10.1901/jeab.1961.4-267
- Rachlin, H. (1978). A molar theory of reinforcement schedules. *Journal of the Experimental Analysis of Behavior*, 30(3), 345–360. https://doi.org/10.1901/jeab.1978.30-345
- Skinner, B. F. (1938). *The behavior of organisms*. Appleton-Century.
