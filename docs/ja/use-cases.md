# ユースケース

> contingency-dsl が何を可能にし、各構成がなぜ必要なのかを実例で示す。
> 構文の詳細は [syntax-guide.md](syntax-guide.md)、形式理論は [operant/theory.md](../../spec/ja/operant/theory.md) を参照。

> **用語ノート: 被験体 vs 有機体** — 本文書では以下の使い分けに従う。
> - **被験体**（subject）: 手続き・実験計画の記述（例:「被験体は CS-US 間隔中に反応することで US を回避できる」）
> - **有機体**（organism）: 行動原理・理論的記述（例:「有機体が多段階の随伴性をどう学習するかを研究できない」）

---

## 1. 基本的なオペラント実験

**シナリオ:** ハトのキーペック実験で標準的な FR 5 スケジュールを使用する。

```
FR 5
```

**何をするか:** 5回目のキーペックごとに食物を提示する。

**なぜ必要か:** FR は最も単純な比率スケジュール。高く安定した反応率と特徴的な強化後休止（post-reinforcement pause）を生成する（Ferster & Skinner, 1957, Ch. 3）。全ての強化スケジュール研究の基礎。

---

## 2. 切替遅延付き並立スケジュール

**シナリオ:** 2つの VI スケジュール間の選好を測定する（マッチング法則の標準手続き）。

```
Conc(VI 30-s, VI 60-s, COD=2-s)
```

**何をするか:** 2つの反応キーが同時に利用可能。左キーは VI 30-s、右キーは VI 60-s で動作する。キーを切り替えた後、新しいキーで強化が利用可能になるまで 2秒の切替遅延（COD）が必要。

**なぜ COD が重要か:** COD なしでは、高速なキー切り替えが両方の選択肢の取得強化率を人為的に引き上げ、マッチング法則が記述する強化率と反応配分の秩序ある関係を歪める（Herrnstein, 1961）。並立 VI-VI 配置で COD を省略することは手続き的な懸念事項である。DSL はリンター警告（`MISSING_COD`）を発し、明示的な `COD` 指定を推奨する。`COD=0-s`（統制条件用）は受理され、警告を抑制する。COD を省略した場合、ランタイムデフォルトは `COD=0-s` となる。

**引用:**
- Herrnstein, R. J. (1961). Relative and absolute strength of response as a function of frequency of reinforcement. *JEAB*, *4*, 267-272. https://doi.org/10.1901/jeab.1961.4-267
- Baum, W. M. (1974). On two types of deviation from the matching law. *JEAB*, *22*, 231-242. https://doi.org/10.1901/jeab.1974.22-231

**注意: 並立比率スケジュールにおける COD の効果.** COD がマッチング感受性に与える効果はスケジュール型に依存する。並立 VI VI では COD の増加がマッチングを改善する傾向がある（アンダーマッチングの減少; Shull & Pliskoff, 1967）。一方、並立比率スケジュール（VR/FR）では COD の増加が感受性を*低下*させる（Bellow & Lattal, 2023）。DSL はいかなる `Conc` 式にも COD を許可する — これは手続き記述としては正しい — が、並立 VI での慣習的な直観が並立比率配置には通用しないことに留意されたい。

- Shull, R. L., & Pliskoff, S. S. (1967). Changeover delay and concurrent schedules: Some effects on relative performance measures. *JEAB*, *10*(6), 517–527. https://doi.org/10.1901/jeab.1967.10-517
- Bellow, D. T., & Lattal, K. A. (2023). Choice dynamics in concurrent ratio schedules of reinforcement. *JEAB*, *119*(2), 337–355. https://doi.org/10.1002/jeab.828

---

## 3. 連鎖スケジュールによる条件性強化研究

**シナリオ:** コンポーネント移行時の刺激変化（スケジュール成分間の弁別刺激の移行）が条件性強化子として機能するかを検証する。

```
Chain(FR 5, FI 30-s)
```

**何をするか:** ハトはまず S^D-1（例: 赤色キーライト）の下で FR 5（初期リンク）を完了する。完了すると S^D-2（例: 緑色キーライト）に変化し、FI 30-s（終端リンク）に移行する。FI 30-s 完了で食物が提示される。

**なぜ必要か:** FR 5→FI 30-s 移行時の刺激変化は条件性強化子として機能する — 食物への接近を知らせるからだ。Kelleher & Fry (1962) は、刺激-食物距離関係の一貫性が条件性強化力を決定することを示した。連鎖なしでは、有機体が多段階の随伴性をどう学習するかを研究できない。

**タンデム（`Tand`）との対比:**
```
Tand(FR 5, FI 30-s)   -- 同じ随伴性だが刺激変化なし
```
Jwaideh (1973) は、刺激変化を除去した場合（Tand）に強化後休止が短縮し条件性強化の証拠が弱まることを示した — 刺激変化が活性成分であることの直接的証拠。

**引用:**
- Kelleher, R. T., & Fry, W. T. (1962). Stimulus functions in chained fixed-interval schedules. *JEAB*, *5*, 167-173. https://doi.org/10.1901/JEAB.1962.5-167
- Jwaideh, A. R. (1973). Responding under chained and tandem fixed-ratio schedules. *JEAB*, *19*(2), 259. https://doi.org/10.1901/jeab.1973.19-259

---

## 4. 行動薬理学のための二次スケジュール

**シナリオ:** 2時間セッションで低頻度の薬物投与下で安定したコカイン自己投与行動を維持する。

```
FI 600-s(FR 10)
```

**何をするか:** ラットは FR 10 ユニット（10回のレバー押しで1ユニット）を繰り返し完了する。各ユニット完了時に brief stimulus（短時間の刺激提示 — 通常は条件性強化子として機能する。例: 薬物注入と対提示された2秒間のライト）が提示される。FI 600秒（10分）間隔が経過し、次の FR 10 ユニットが完了すると、コカイン注入が行われる。

**なぜ必要か:** 薬物自己投与研究では以下が必要:

1. **低頻度の薬物投与** — 頻繁すぎる投与は薬理学的効果を飽和させ、行動分析を不可能にする
2. **セッション全体を通じた安定した反応** — 条件性強化子なしでは、長い強化間間隔で行動が崩壊する
3. **構造化された行動パターン** — ユニットレベルのスキャロッピングが動機づけ操作の効果に関する時間的ダイナミクスを明らかにする。単純な FR や FI ではこれが見えない

二次スケジュールはこれら3つの問題を全て解決する。brief stimulus が条件性強化子として機能し、低頻度の一次強化エピソード間のギャップを架橋する。Kelleher (1966) は、60分に1回という疎な強化（30 × FI 2-min）でも、brief stimulus のみで各 FI コンポーネントに秩序あるスキャロップ反応が維持されることを実証した。

**なぜ Tand ではだめなのか:**
```
Tand(FI 600-s, FR 10)   -- これは等価ではない
```
`Tand(FI 600-s, FR 10)` の意味: 600秒待機し、その後 FR 10 を1回完了する。有機体は600秒の待機中に何もしない。対照的に `FI 600-s(FR 10)` では、間隔中ずっと FR 10 ユニットを活発に完了し続け、行動の時間的パターンに関するデータを産出する。

**引用:**
- Kelleher, R. T. (1966). Conditioned reinforcement in second-order schedules. *JEAB*, *9*, 475. https://doi.org/10.1901/jeab.1966.9-475
- Goldberg, S. R. (1973). Comparable behavior maintained under fixed-ratio and second-order schedules of food presentation, cocaine injection or d-amphetamine injection in the squirrel monkey. *Journal of Pharmacology and Experimental Therapeutics*, *186*(1), 18-30.

---

## 5. 多元スケジュールによる行動的コントラスト

**シナリオ:** 一方の文脈での強化変更が他方の文脈の行動に影響することを示す。

```
Mult(VI 60-s, VI 60-s)     -- フェーズ 1: 両成分で等しいスケジュール
Mult(VI 60-s, EXT)       -- フェーズ 2: 成分 2 を消去に変更
```

**何をするか:** 2つの成分が交替する（異なるキー色で弁別される）。フェーズ 1 では両方 VI 60-s。フェーズ 2 で成分 2 を EXT に切り替える。予測: 成分 1 のスケジュールは変更されていないにもかかわらず、成分 1 の反応率が*増加*する — これが行動的コントラスト（Reynolds, 1961）。

**なぜ必要か:** 多元スケジュールは弁別性制御と強化効果を分離する。弁別刺激（異なるキー色）がどのスケジュールが効力中かを有機体に知らせる。弁別なし（Mix）ではコントラスト効果が弱い/消失する — 刺激-スケジュール相関が必要であることの証拠。

**引用:**
- Reynolds, G. S. (1961). Behavioral contrast. *JEAB*, *4*(1), 57-71. https://doi.org/10.1901/jeab.1961.4-57

---

## 6. DRL によるタイミング研究

**シナリオ:** 時間弁別能力の検証 — 有機体は反応間に少なくとも 20秒待てるか?

```
DRL 20-s
```

**何をするか:** 反応間時間（IRT）が 20秒以上の場合にのみ強化。早すぎる反応はタイマーをリセットする。

**なぜ必要か:** DRL は要求値付近にピークを持つ IRT 分布を産出し、有機体が時間間隔を弁別できることを示す。ピークの精度が有機体のタイミング精度を反映する（Richards et al., 1993）。

**Limited Hold を付加する場合:**
```
DRL 20-s LH 5-s
```
反応は前回の反応から 20秒後〜25秒後の間に行わなければならない。早すぎても遅すぎても強化なし。時間窓が狭まり、より精密なタイミング能力が検出できる（Kramer & Rilling, 1970）。

**引用:**
- Richards, R. W., Sabol, T. J., & Seiden, L. S. (1993). DRL interresponse-time distributions. *JEAB*, *60*, 361. https://doi.org/10.1901/jeab.1993.60-361
- Kramer, T. J., & Rilling, M. (1970). Differential reinforcement of low rates: A selective critique. *Psychological Bulletin*, *74*(4), 225-254. https://doi.org/10.1037/h0029813

---

## 7. 累進比率による強化子効力評価

**シナリオ:** 有機体が強化子のためにどれだけ「懸命に」働くかを測定する（ブレイクポイント分析）。

```
PR(hodos)
```

**何をするか:** 強化ごとに比率要件が増加: 1, 2, 4, 6, 9, 12, 15, 20, 25, ...（Hodos, 1961）。有機体が基準期間にわたって反応を停止するまでセッションが継続する（ブレイクポイント）。

**なぜ必要か:** ブレイクポイントは強化子効力の定量的指標。高価値の強化子ほど高いブレイクポイントを産出する。行動薬理学では、PR ブレイクポイントで異なる薬物用量の強化力を比較する。

**引用:**
- Hodos, W. (1961). Progressive ratio as a measure of reward strength. *Science*, *134*(3483), 943-944. https://doi.org/10.1126/science.134.3483.943
- Richardson, N. R., & Roberts, D. C. S. (1996). Progressive ratio schedules in drug self-administration studies in rats. *Psychopharmacology*, *128*(4), 327-335. https://doi.org/10.1007/s002130050138

---

## 8. Sidman 自由オペラント回避

**シナリオ:** 負の強化によって維持される回避行動の測定。反応が次の電撃（shock）を延期する手続き。

```
Sidman(SSI=20-s, RSI=5-s)
  @punisher("shock", intensity="0.5mA")
  @operandum("lever")
```

**何をするか:** 反応がない場合、20 秒ごとに電撃が発生する（SSI = Shock-Shock Interval）。レバー押し反応ごとに次の電撃が 5 秒後に延期される（RSI = Response-Shock Interval）。形式的には `next_shock = max(last_shock + SSI, last_response + RSI)`。十分訓練されたラットは反応を維持し続け、反応間間隔を RSI より少し短く保つ。

**なぜ存在するか:** Sidman (1953) は、明示的な warning 刺激なしでも時間的随伴性だけで回避行動が維持されることを示した。これは嫌悪制御・不安モデル・行動薬理における負の強化研究の基礎手続きとなった。Sidman 回避は強化スケジュール F/V/R × R/I/T マトリクスでは表現できない — **2 つの独立した時間パラメータ** と反応随伴的な再スケジュール規則を持つため、専用の primitive が必要。

**Alias の等価性:** `@punisher` は実験者の意図を明示するために使用するが、`@reinforcer` も等価な alias:

```
Sidman(SSI=20-s, RSI=5-s) @reinforcer("shock", intensity="0.5mA")  -- 等価
```

両形式は同じ AST ノードに解決される。

**他スケジュールとの合成:** Sidman は任意の複合コンビネータに入れられる。例えば連鎖スケジュールのリンクとして（de Waard, Galizio, & Baron, 1979）:

```
Chain(FR 10 @reinforcer("food"),
      Sidman(SSI=20-s, RSI=5-s) @punisher("shock"))
```

**参考文献:**
- Sidman, M. (1953). Two temporal parameters of the maintenance of avoidance behavior by the white rat. *Journal of Comparative and Physiological Psychology*, *46*(4), 253-261. https://doi.org/10.1037/h0060730
- Hineline, P. N. (1977). Negative reinforcement and avoidance. In W. K. Honig & J. E. R. Staddon (Eds.), *Handbook of operant behavior* (pp. 364-414). Prentice-Hall.
- de Waard, R. J., Galizio, M., & Baron, A. (1979). Chained schedules of avoidance. *JEAB*, *32*(3), 399-407. https://doi.org/10.1901/jeab.1979.32-399

---

## 9. Lag スケジュールによるオペラント変動性

**シナリオ:** 反応の変動性を直接強化する手続き — 被験体が直前と異なる反応パターンを
生成することを強化する。応用場面（ASD の言語療法、創造性研究）と基礎研究
（operant variability、Neuringer の研究プログラム）で使用される。

```
Lag(5, length=8)
  @reinforcer("grain")
  @operandum("left_key") @operandum("right_key")
```

**何をするか:** 被験体は 2 キー上で 8-peck の系列（LLLLLLLL, LLLLLLLR, ...,
RRRRRRRR の 256 通り）を生成する。現在の系列が直前 5 系列のいずれとも異なる場合
にのみ強化される（Page & Neuringer, 1985）。訓練が進んだハトは Lag 50 でほぼ
ランダムに近い系列分布を生成し（Experiment 3）、**variability それ自体が
オペラント次元として強化可能**であることを示した。

**なぜ存在するか:** Page & Neuringer (1985) は、強化随伴性が反応の変動性を
直接制御可能であることを示し、Schwartz (1980) の「variability は強化で制御
できない」という結論を覆した。これはオペラント変動性研究の基盤手続きとなり、
ASD のステレオタイプ低減（Miller & Neuringer, 2000）、自閉症マンド訓練
（Lee, McComas, & Jawor, 2002）、創造性研究に応用された。

**応用研究での簡易形式:** 個別反応の variability（例: マンド訓練）では、
`length` を省略する — default=1 として機能する:

```
Lag 5
  @reinforcer("praise+token")
  @target("varied mand across requests")
```

この形式では、個別反応（マンド、タクト、レバー押し）を単位として、直前 5 個の
反応と異なる反応のみを強化する。

**統制条件としての Lag 0:** `Lag 0` は合法で CRF と意味論的に等価。「variability
要求あり」 vs 「variability 許容」の条件を比較する実験（Page & Neuringer の
Experiment 5 yoked control）での明示的な統制として有用:

```
Mult(Lag(5, length=8), Lag 0)    -- variability vs no-variability baseline
```

**Mult との合成:** Neuringer の研究プログラムでは、variability 訓練と CRF
ベースラインまたは固定パターンを交替させるパターンがよく使われる:

```
Mult(Lag(5, length=8), CRF, BO=5-s)
  @sd("red_light", component=1)
  @sd("green_light", component=2)
  @reinforcer("grain")
```

**参考文献:**
- Page, S., & Neuringer, A. (1985). Variability is an operant. *Journal of Experimental Psychology: Animal Behavior Processes*, *11*(3), 429-452. https://doi.org/10.1037/0097-7403.11.3.429
- Neuringer, A. (2002). Operant variability: Evidence, functions, and theory. *Psychonomic Bulletin & Review*, *9*(4), 672-705. https://doi.org/10.3758/BF03196324
- Miller, N., & Neuringer, A. (2000). Reinforcing variability in adolescents with autism. *JABA*, *33*(2), 151-165. https://doi.org/10.1901/jaba.2000.33-151
- Lee, R., McComas, J. J., & Jawor, J. (2002). The effects of differential and lag reinforcement schedules on varied verbal responding by individuals with autism. *JABA*, *35*(4), 391-402. https://doi.org/10.1901/jaba.2002.35-391

---

## 10. 弁別回避

**シナリオ:** 警告信号（CS）が嫌悪刺激（US）に先行する試行ベースの回避手続き。
被験体は CS-US 間隔中に反応することで US を回避できる。恐怖条件づけ、不安研究、
嫌悪制御の研究で使用される。

> **キーワード:** `DiscriminatedAvoidance`（短縮形: `DiscrimAv`）

```
DiscriminatedAvoidance(CSUSInterval=10-s, ITI=3-min, mode=response_terminated, MaxShock=2-min)
  @punisher("shock", intensity="1.0mA")
  @sd("light", modality="visual")
  @species("dog")
```

**何をするか:** 光 CS が呈示される。イヌが 10 秒以内にバリアを跳び越えれば電撃
は回避される（回避試行）。10秒以内に反応しなければ電撃が開始され、イヌが跳ぶ
まで継続する（逃避試行）。2分の安全カットオフあり。次の CS は現在の CS 提示から
3分後に出現する。

**なぜ存在するか:** Solomon & Wynne (1953) は、弁別回避が極めて持続的な行動を
生成することを示した — イヌは数百回の消去試行後も回避し続けた。このパラダイムは、
不安・恐怖症・臨床集団における回避行動の持続性を理解する基盤である。

**固定時間変種:** 逃避不可能な短い US（例: 0.5秒のパルス電撃）を使う手続き:

```
DiscriminatedAvoidance(CSUSInterval=10-s, ITI=3-min, mode=fixed, ShockDuration=0.5-s)
  @punisher("shock", intensity="0.5mA")
```

**Chain との合成:** 食物強化の比率を完了すると弁別回避成分に遷移する連鎖スケジュール:

```
Chain(FR 10 @reinforcer("food"),
      DiscrimAv(CSUSInterval=10-s, ITI=3-min, mode=response_terminated))
```

**参考文献:**
- Solomon, R. L., & Wynne, L. C. (1953). Traumatic avoidance learning: Acquisition in normal dogs. *Psychological Monographs: General and Applied*, 67(4), 1-19. https://doi.org/10.1037/h0093649

---

## 11. 罰の重畳（Punishment Overlay）

**シナリオ:** 強化スケジュールで維持されているオペラント行動に対する反応随伴性罰の
効果を研究する。ベースラインの強化は継続しながら、罰を重畳する。

```
Overlay(VI 60-s, FR 1)
  @reinforcer("food")
  @punisher("shock", intensity="0.5mA")
```

**何をするか:** 食物強化が VI 60-s で配分される。同時に、全ての反応（FR 1）が短い
電撃を生じる。両方の随伴性が同じ反応ストリームに作用する。これにより、罰なし
ベースライン率に対して罰がどの程度反応を抑制するかを観察できる。

**なぜ存在するか:** Azrin & Holz (1966) は罰研究の標準パラダイムを確立した:
強化スケジュールで反応を維持し、さまざまな強度やスケジュールの罰を重畳する。
これにより罰パラメータと反応抑制の機能的関係が明らかになり、ベースラインが
「抑制すべき行動」を担保する。

**間欠的罰:** 全反応を罰する必要はない:

```
Overlay(VI 60-s, VI 30-s)
  @reinforcer("food")
  @punisher("shock", intensity="0.5mA")
```

**並立ベースラインへの罰の重畳:** マッチング法則準備に罰を重畳:

```
Overlay(Conc(VI 60-s, VI 180-s, COD=2-s), FR 1)
  @reinforcer("food")
  @punisher("shock", intensity="0.5mA")
```

**切替反応のみへの罰（Todorov, 1971）:** 並立 VI VI ベースラインで、切替反応
のみを罰する:

```
Overlay(Conc(VI 30-s, VI 60-s, COD=2-s), FR 1, target=changeover)
  @reinforcer("food")
  @punisher("shock", intensity="0.5mA")
```

オペラント反応そのものは罰せず、切替行動への嫌悪効果を分離する。

**方向非対称罰（PUNISH directive）:** 実験者が各切替方向に異なる罰子を
適用したい場合（例: 高頻度側から低頻度側への切替を強く罰する）:

```
Conc(VI 30-s, VI 60-s, COD=2-s,
     PUNISH(1->2)=FR 1, PUNISH(2->1)=FR 1)
  @reinforcer("food")
  @punisher("shock", intensity="0.5mA")
```

各罰子スケジュールに強度アノテーションを付与することで、非対称罰強度
（Todorov, 1971, 実験 1）を直接表現できる。

**成分特異的罰（de Villiers, 1980）:** 特定の成分上の全反応を罰し、他方は罰しない:

```
Conc(VI 30-s, VI 60-s, COD=2-s, PUNISH(1)=VI 30-s)
  @reinforcer("food")
  @punisher("shock", intensity="0.5mA")
```

de Villiers (1980) はこのパラダイムで並立 VI VI における罰の減算モデルを
競合抑制モデルと比較検証した。

**参考文献:**
- Azrin, N. H., & Holz, W. C. (1966). Punishment. In W. K. Honig (Ed.), *Operant behavior: Areas of research and application* (pp. 380-447). Appleton-Century-Crofts.
- Critchfield, T. S., Paletz, E. M., MacAleese, K. R., & Newland, M. C. (2003). Punishment in human choice: Direct or competitive suppression? *JEAB*, 80(1), 1-27. https://doi.org/10.1901/jeab.2003.80-1
- de Villiers, P. A. (1980). Toward a quantitative theory of punishment. *JEAB*, 33(1), 15-25. https://doi.org/10.1901/jeab.1980.33-15
- Farley, J. (1980). Reinforcement and punishment effects in concurrent schedules: A test of two models. *JEAB*, 33(3), 311-326. https://doi.org/10.1901/jeab.1980.33-311
- Todorov, J. C. (1971). Concurrent performances: Effect of punishment contingent on the switching response. *JEAB*, 16(1), 51-62. https://doi.org/10.1901/jeab.1971.16-51

---

## 12. Percentile Schedule による shaping（Operant.Stateful）

**シナリオ:** パーセンタイルスケジュールによるレバー押し IRT の shaping — 自動的 shaping の定量的基盤 (Galbicka, 1994)。

```
@species("Rattus norvegicus") @n(4)
@deprivation(hours=23, target="food")
Pctl(IRT, 50, window=20) @reinforcer("food pellets")
```

**動作:** 直近 20 反応の IRT 中央値以下のレバー押しを強化する。ラットの IRT が短くなるにつれ閾値も自動的に追従し、実験者の手動介入なしに shaping 圧力が持続する。

**Pctl と DRL の使い分け:**

| スケジュール | 基準 | 適応 | 用途 |
|---|---|---|---|
| `DRL 5-s` | 5 秒に固定 | なし | 既存の時間弁別の維持 |
| `Pctl(IRT, 50)` | 直近 IRT の中央値 | あり | IRT を短縮/延長する方向に shaping |

**複合構文例:**

```
-- 多元スケジュール: shaping 期 vs 消去統制
Mult(Pctl(IRT, 50), EXT, BO=5-s)

-- 名前付き束縛で可読性向上（注: `shaping` は予約語になったため別名を使う）
let pctl_sched = Pctl(IRT, 50, window=20)
Mult(pctl_sched, EXT)
```

**核心的洞察:** 単一の `Pctl(IRT, 50)` だけで shaping が成立する — 適応的閾値が分布の連続的シフトを保証する。段階的な rank 変更（50→40→30）は shaping 速度の制御であり、contingency-core のフェーズ遷移で記述する。

**典拠:**
- Platt, J. R. (1973). Percentile reinforcement. In G. H. Bower (Ed.), *The psychology of learning and motivation* (Vol. 7, pp. 271–296). Academic Press.
- Galbicka, G. (1994). Shaping in the 21st century. *JABA*, *27*(4), 739–760. https://doi.org/10.1901/jaba.1994.27-739

---

## 13. Interleave 付きパラメトリック用量反応（実験層）

**シナリオ:** 各テスト用量の後に baseline 復帰期間を挟む薬物自己投与の用量反応研究 — 行動薬理学 JEAB 論文の正準的な構造（例: John & Nader, 2016）。6 つの単位用量を順次テストし、各ペアの間で動物は固定の参照用量に 3 セッション以上、安定するまで戻る。

```
@species("rhesus monkey") @n(4)
@apparatus(chamber="primate-test", operandum="lever")

phase Recovery:
  sessions >= 3
  stable(visual)
  FI 600-s(FR 30)
  @reinforcer("cocaine", dose="0.1mg/kg")

progressive DoseResponse:
  steps dose = [0.003, 0.01, 0.03, 0.1, 0.3, 0.56]
  interleave Recovery
  sessions >= 5
  stable(visual)
  FI 600-s(FR 30)
  @reinforcer("cocaine", dose="{dose}mg/kg")
```

**この実験の動作:**
- `phase Recovery` は progressive_decl より **前** に宣言する（前方参照禁止 — 制約 74）
- `interleave` で参照されているため、`Recovery` は **template**（制約 76）となり、timeline には standalone で現れない
- `interleave Recovery` は既定の **intercalate** 意味論: 各用量条件の後（最後を含む）に Recovery の clone が挿入される
- 展開結果は 12 phase（6 用量 + 6 recovery）— 論文 Method「*each dose was followed by a return to baseline*」と完全一致
- clone された recovery は Recovery の `@reinforcer("cocaine", dose="0.1mg/kg")` annotation を verbatim で持つ（アノテーション局所性、theory.md 定義 16 性質 4）。progressive_decl 側の `{dose}` placeholder は clone に流入しない

**展開された phase 列:**

```
DoseResponse_1, Recovery_after_DoseResponse_1,
DoseResponse_2, Recovery_after_DoseResponse_2,
DoseResponse_3, Recovery_after_DoseResponse_3,
DoseResponse_4, Recovery_after_DoseResponse_4,
DoseResponse_5, Recovery_after_DoseResponse_5,
DoseResponse_6, Recovery_after_DoseResponse_6
```

**意義:** `interleave` がなければ、ユーザはスケジュールと大半の annotation が同一の 12 個の `phase` 宣言を手書きすることになり、論文 Method と DSL の 1:1 対応が崩れる。`interleave` 句は DSL を簡潔に保ちつつ、実験デザインの構造的忠実性を保存する。

**バリエーション:**
- `interleave Recovery no_trailing` — **intersperse** 意味論に切り替え（最後の用量の後に recovery を入れない）。phase 数 = 11。
- `interleave Recovery` の後に `interleave Probe` — gap block は宣言順に両方の phase を含む。各テスト条件の後に recovery + probe 試行を挟むデザインに有用。

**参考文献:**
- John, W. S., & Nader, M. A. (2016). Dose-response procedures for cocaine self-administration in rhesus monkeys. *Journal of the Experimental Analysis of Behavior*（スタイル参照）.
- Sidman, M. (1960). *Tactics of scientific research*. Basic Books.（被験体内パラメトリックデザインの基礎的論考）

---

## 14. 複合的な実験プログラム

**シナリオ:** 一方の成分で並立配置、他方で連鎖手続きを使う2成分多元スケジュール。プログラムレベルのデフォルト付き。

```
COD = 2-s
LH = 10-s

let choice_component = Conc(VI 30-s, VI 60-s)
let chain_component = Chain(FR 10, FI 30-s)
Mult(choice_component, chain_component)
```

**何をするか:**
- 成分 1（S^D-1）: 並立 VI 30-s VI 60-s + COD 2秒 — 有機体が2つの選択肢間で反応を配分する
- 成分 2（S^D-2）: 連鎖 FR 10→FI 30-s — まず10回反応を完了、次に約30秒待って食物
- 成分は弁別刺激の変化を伴って交替
- 全スケジュールに 10秒の limited hold が適用
- `let` 束縛が複数行プログラムの可読性を確保

**なぜ重要か:** 実際の実験は複数のスケジュール型を組み合わせる。DSL の合成可能性により、行動分析学文献に記述されるあらゆる配置を表現できる。名前付き束縛が複雑な設計を読みやすく保つ。

---

## 15. レスポンデント単独手続き（独立したパヴロフ型条件づけ）

**シナリオ:** オペラント反応のない純粋なパヴロフ型手続き — EAB では稀だが代表的（例: 恐怖条件づけ、唾液条件づけ、味覚嫌悪学習のベースライン）。

```
Phase(
  name = "pavlovian_acquisition",
  respondent = Pair.ForwardDelay(tone, shock, isi=10-s, cs_duration=10-s),
  criterion = FixedSessions(n=8)
)
  @species("rat") @n(8)
  @cs(label="tone", duration=10-s, modality="auditory")
  @us(label="shock", intensity="0.5mA", delivery="unsignaled")
  @iti(distribution="exponential", mean=120-s)
```

**何をするか:** 前向き遅延パヴロフ条件づけを 8 セッション。条件反応（例: フリージング）は装置固有のビデオ解析パイプラインで測定。DSL は随伴性と CS/US/ITI メタデータを記録する。

**存在理由:** レスポンデント単独手続きは二項 CS-US 随伴性の最も単純な表現である。合成手続き（CER、PIT、オートシェイピング）が後に活用するベースライン連合を確立する。EAB 論文がオペラント・ベースラインを測定プラットフォームとして用いる場合でも、レスポンデント条件づけの原理が解釈を支える。

**研究課題別の代替レスポンデント primitive:**

```
TrulyRandom(tone, shock, p=0.2)              -- Rescorla (1967) 統制
ExplicitlyUnpaired(tone, shock, min_separation=30-s)
                                              -- Ayres et al. (1975) 精密化統制
Contingency(p_us_given_cs=0.6, p_us_given_no_cs=0.4)
                                              -- 随伴性空間の任意点
Differential(tone_plus, tone_minus, shock)   -- A+/B− 弁別
```

**引用:**
- Pavlov, I. P. (1927). *Conditioned reflexes* (G. V. Anrep, Trans.). Oxford University Press.
- Rescorla, R. A. (1967). Pavlovian conditioning and its proper control procedures. *Psychological Review*, *74*(1), 71-80. https://doi.org/10.1037/h0024109

---

## 16. 合成手続き: オペラント・ベースライン + CER

**シナリオ:** 条件性抑制 (CER) — 食物系オペラント・ベースラインと嫌悪系パヴロフ型オーバーレイを組み合わせる典型的合成手続き。CS 前ベースラインに対する CS 中の反応抑制がパヴロフ型連合を定量する。

```
PhaseSequence(
  Phase(
    name = "baseline",
    operant = VI 60-s,
    criterion = Stability(window=5, tolerance=0.10)
  ),
  Phase(
    name = "cer_training",
    operant = VI 60-s,
    respondent = Pair.ForwardDelay(tone, shock, isi=60-s, cs_duration=60-s),
    criterion = FixedSessions(n=10)
  )
)
  @cs(label="tone", duration=60-s, modality="auditory")
  @us(label="shock", intensity="0.5mA", delivery="unsignaled")
```

**何をするか:** VI 60-s ベースラインを安定まで到達させ、続いてパヴロフ型オーバーレイを重畳する。オペラント・スケジュールは CS 中も動作し続け、変化するのは嫌悪系 CS-shock 随伴性のみ。

**なぜ罰でなく合成か?** US は**オペラント反応から独立に**提示される（パヴロフ型、二項）のであって、**反応随伴的に**提示される（オペラント罰、三項）のではない。この構造的区別が分類を決める: CER は `composed/` に、罰は `operant/` に属する（`Overlay` と `PUNISH` 参照）。

**PIT 変種** — パヴロフと道具的訓練が独立で、転移テストを含む:

```
PhaseSequence(
  Phase(name="pavlovian_training",
        respondent=Pair.ForwardDelay(tone, food, isi=10-s, cs_duration=10-s)),
  Phase(name="instrumental_training",
        operant=VI 60-s),
  Phase(name="transfer_test",
        operant=EXT,
        respondent=CSOnly(tone, trials=8))
)
  @cs(label="tone", duration=10-s, modality="auditory")
  @us(label="food", intensity="45mg_pellet", delivery="signaled")
```

**引用:**
- Estes, W. K., & Skinner, B. F. (1941). Some quantitative properties of anxiety. *Journal of Experimental Psychology*, *29*(5), 390-400. https://doi.org/10.1037/h0062283
- Annau, Z., & Kamin, L. J. (1961). The conditioned emotional response as a function of intensity of the US. *Journal of Comparative and Physiological Psychology*, *54*(4), 428-432. https://doi.org/10.1037/h0042199
- Estes, W. K. (1948). Discriminative conditioning. II. Effects of a Pavlovian conditioned stimulus upon a subsequently established operant response. *Journal of Experimental Psychology*, *38*(2), 173-177. https://doi.org/10.1037/h0057525

---

## 17. `@cs` / `@us` 注釈によるスケジュール式の拡張

**シナリオ:** respondent-annotator を用いて、セッション内の別のパヴロフ手続きと刺激を共有する既存オペラント・スケジュールに CS/US メタデータを付加する。CS ラベル、そのモダリティ、US 強度を明示化することで、オペラント・スケジュールの文法を変えずに再現性と装置検証を高める。

```
Mult(VI 30-s, EXT, BO=5-s)
  @sd("tone", component=1)
  @cs(label="tone", duration=60-s, modality="auditory")
  @us(label="food", intensity="45mg_pellet", delivery="signaled")
  @iti(distribution="fixed", mean=30-s, jitter=0)
```

**何をするか:** トーンが VI 30-s 成分を合図する多元スケジュールに `@cs` / `@us` / `@iti` メタデータを付加する。`@sd` と `@cs` は**同一物理刺激**を 2 つの観点で記述する — オペラント注釈は弁別刺激として、レスポンデント注釈はモダリティと持続時間を持つ CS として。

**なぜ両方の注釈?** 単一のトーン刺激はオペラント反応の S^D として**および**パヴロフ連合の CS として機能しうる。DSL はいずれの解釈も優先しない。ソース内で両ラベルを明示することで (a) 装置の物理パラメータを必要とする装置検証パイプラインを支え、(b) 同一刺激をオペラント・レスポンデント両視点から記述する Methods セクションへのコンパイルを支える。

**使用時期:**
- スケジュールがパヴロフ解釈にも関連する刺激ラベル付けを持つ
- 装置検証パイプラインが CS 持続時間／モダリティ／US 強度を必要とする
- 出版パイプラインが読者向けの CS/US 窓指定を必要とする

**使用しない時期:**
- レスポンデント解釈のないピュア・オペラント手続き — `@sd` のみを用いる
- ピュア・レスポンデント手続き — `@cs` / `@us` のみを用い、`@sd` は不要

**引用:**
- Rescorla, R. A., & Solomon, R. L. (1967). Two-process learning theory: Relationships between Pavlovian conditioning and instrumental learning. *Psychological Review*, *74*(3), 151-182. https://doi.org/10.1037/h0024475

---

## 18. レスポンデント拡張ポイント — Core を変えずに Tier B primitive を追加する

**シナリオ:** 研究プログラムがブロッキング (Kamin, 1969)、潜在制止 (Lubow & Moore, 1959)、更新 (Bouton & Bolles, 1979) など、Core DSL が提供しない Tier B レスポンデント手続きを表現する必要がある。レスポンデント拡張ポイントは、同梱パッケージ `contingency-respondent-dsl` または任意の第三者 registry が、contingency-dsl 文法を変えずにこれらの primitive を追加することを可能にする。

**拡張ポイントの動作.** `respondent/grammar.md` が宣言するのは:

```ebnf
RespondentExpr ::=
      CoreRespondentPrimitive        -- Tier A (Pair.*, Extinction, CSOnly 等)
    | ExtensionRespondentPrimitive    -- 第三者、プログラム境域

ExtensionRespondentPrimitive ::=
      Identifier "(" ArgList? ")"     -- レスポンデント registry で解決
```

プログラムは識別子と拡張 primitive の対応を保つ registry をロードする。parser はそれらの識別子をレスポンデント式として受理し、未登録の識別子は当該プログラムのスコープ内で parse error となる。

**例 — `contingency-respondent-dsl` の registry をロード:**

```
-- プログラムが contingency-respondent-dsl registry をロードする宣言は
-- プログラム構成ファイルまたは CLI フラグに置く（DSL ソースには置かない）

PhaseSequence(
  Phase(name="phase_1",
        respondent = Pair.ForwardDelay(noise, shock, isi=10-s, cs_duration=10-s)),
  Phase(name="phase_2_blocking",
        respondent = Blocking(added_cs=tone,
                              established_cs=noise,
                              us=shock))
)
```

ここで `Blocking(...)` は `contingency-respondent-dsl` が提供する**拡張 primitive** であり、Tier A レスポンデント文法には属さない。Core 文法は変更不要。プログラムの registry が `Blocking` を構造的意味論に解決する。

**潜在制止、更新、その他の Tier B 手続きも同様:**

```
LatentInhibition(cs=tone, pre_exposure_trials=40)
Renewal(training_context=A, extinction_context=B, test_context=A)
Reinstatement(cs=tone, us=shock)
SpontaneousRecovery(cs=tone, recovery_interval=24h)
```

**拡張ポイントが重要な理由:**
- **Core 文法は不変.** Tier B 手続きの追加は contingency-dsl の文法・schema・conformance fixture の編集を要さない。
- **プログラム境域の閉包.** 異なるラボが異なる拡張 registry を提供でき衝突しない。Tier A のみをロードするプログラムも完全にパースできる。
- **静的検証の境界.** Tier A primitive は Core で完全に静的検証可能。拡張 primitive は自身の検証規則を提供する。

**レスポンデント層と拡張ポイントの使い分け:**

| 状況 | 使用先 |
|---|---|
| 前向き／痕跡／同時／後向きペアリング、随伴性空間、差別条件づけ | **Tier A primitive**（Core） |
| ITI 構造、消去、CS 単独／US 単独提示 | **Tier A primitive**（Core） |
| ブロッキング、オーバーシャドーイング、潜在制止、条件性制止 | **レスポンデント拡張**（`contingency-respondent-dsl` 経由） |
| 更新、復元、自発的回復、対抗条件づけ | **レスポンデント拡張**（`contingency-respondent-dsl` 経由） |
| いずれの層にも未登録の新しい構造的 CS-US 関係 | **レスポンデント拡張**（カスタム registry） |

**respondent-annotator との区別.** respondent-annotator (`@cs`、`@us`、`@iti`、`@cs_interval`) は既存 primitive に**メタデータ**を付加する。レスポンデント拡張ポイントは自身の文法を持つ**新しい primitive**を追加する。両者は直交する機構である: 注釈は parse tree を変えないが、拡張は変える。

**引用:**
- Kamin, L. J. (1969). Predictability, surprise, attention, and conditioning. In B. A. Campbell & R. M. Church (Eds.), *Punishment and aversive behavior* (pp. 279-296). Appleton-Century-Crofts.
- Lubow, R. E., & Moore, A. U. (1959). Latent inhibition: The effect of nonreinforced pre-exposure to the conditional stimulus. *Journal of Comparative and Physiological Psychology*, *52*(4), 415-419. https://doi.org/10.1037/h0046700
- Bouton, M. E., & Bolles, R. C. (1979). Contextual control of the extinction of conditioned fear. *Learning and Motivation*, *10*(4), 445-466. https://doi.org/10.1016/0023-9690(79)90057-2

---

## まとめ: 各構成が可能にすること

| 構成 | 何を可能にするか | なければ |
|------|----------------|---------|
| `Conc` | 選好測定、マッチング法則 | 選択配分を研究できない |
| `Chain` / `Tand` | 多段階随伴性、条件性強化 | 単一段階スケジュールに限定 |
| `Mult` / `Mix` | 刺激制御、行動的コントラスト | 弁別と強化を分離できない |
| `XX(YY)` 二次 | 疎な強化維持、薬物自己投与 | 低強化率で行動が崩壊 |
| `DRL` / `DRH` / `DRO` | IRT 制御、タイミング、省略訓練 | 時間的特性を強化できない |
| `LH` | 時間的利用可能窓 | 無制限の反応機会がデータを歪める |
| `PR` | 強化子効力測定 | 定量的ブレイクポイント指標がない |
| `COD` / `FRCO` | クリーンな並立データ | 高速切替による強化率の人為的引き上げ |
| `Sidman` | 自由オペラント回避、嫌悪制御 | 無弁別回避手続きを表現できない |
| `DiscrimAv` | 弁別回避、恐怖条件づけ、不安研究 | 試行ベースの CS 予告回避を表現できない |
| `Overlay` | 罰の重畳、反応抑制研究 | 維持行動への罰を表現できない |
| `Lag` | オペラント変動性、ASD ステレオタイプ低減、創造性研究 | 反応の variability を直接強化できない |
| `Pctl` | 自動 shaping、適応的分化強化、臨床的 shaping | 手動 shaping のみ。定量的基準なし |
| `let` | 可読な複雑プログラム | 読めないネスト式 |
| `phase` / `progressive` / `shaping` | 多フェーズ実験デザイン（A-B-A 反転、パラメトリック研究、Skinner 反応形成） | セッション間構造を宣言的に表現できない |
| `interleave` | 用量反応・強化子量・介在 baseline デザイン（論文 Method と 1:1） | 大半の本体が同一の 2N 個 phase を手書き |
| `Pair.ForwardDelay` / `Pair.Backward` / ... | パヴロフ型（二項）手続き、恐怖／食物系条件づけ | レスポンデント随伴性を表現できない |
| `Contingency(p, q)` / `TrulyRandom` / `ExplicitlyUnpaired` | Rescorla (1967) 随伴性空間の統制手続き | 随伴性空間形式化を表現できない |
| `Differential(cs+, cs−, us)` | A+/B− パヴロフ弁別 | 対比 CS 訓練を表現できない |
| 合成手続き（`phase` ブロック内のオペラント／レスポンデント primitive + `@omission` / `@avoidance` 注釈） | CER / PIT / オートシェイピング / 省略 | オペラント × レスポンデント合成を表現できない |
| `@cs` / `@us` / `@iti` / `@cs_interval` | 任意 primitive への CS/US メタデータ（Procedure/Apparatus/Measurement 横断） | 読者向けの CS/US 窓を記録できない |
| レスポンデント拡張ポイント | Tier B 手続き（ブロッキング、オーバーシャドーイング、更新、…）を `contingency-respondent-dsl` 経由で追加 | Tier B 手続きに Core 文法変更が必要になる |

---

## 参照文献（追加）

- Catania, A. C. (2013). *Learning* (5th ed.). Sloan Publishing.
- Cooper, J. O., Heron, T. E., & Heward, W. L. (2020). *Applied behavior analysis* (3rd ed.). Pearson.
- Ferster, C. B., & Skinner, B. F. (1957). *Schedules of reinforcement*. Appleton-Century-Crofts.
