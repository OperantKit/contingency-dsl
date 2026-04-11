# ユースケース

> contingency-dsl が何を可能にし、各構成がなぜ必要なのかを実例で示す。
> 構文の詳細は [syntax-guide.md](syntax-guide.md)、形式理論は [theory.md](../../spec/ja/theory.md) を参照。

---

## 1. 基本的なオペラント実験

**シナリオ:** ハトのキーペック実験で標準的な FR5 スケジュールを使用する。

```
FR5
```

**何をするか:** 5回目のキーペックごとに食物を提示する。

**なぜ必要か:** FR は最も単純な比率スケジュール。高く安定した反応率と特徴的な強化後休止（post-reinforcement pause）を生成する（Ferster & Skinner, 1957, Ch. 3）。全ての強化スケジュール研究の基礎。

---

## 2. 切替遅延付き並行スケジュール

**シナリオ:** 2つの VI スケジュール間の選好を測定する（マッチング法則の標準手続き）。

```
Conc(VI30s, VI60s, COD=2s)
```

**何をするか:** 2つの反応キーが同時に利用可能。左キーは VI 30s、右キーは VI 60s で動作する。キーを切り替えた後、新しいキーで強化が利用可能になるまで 2秒の切替遅延（COD）が必要。

**なぜ COD が重要か:** COD なしでは、高速なキー切り替えが両方の選択肢の取得強化率を人為的に膨張させ、マッチング法則が記述する強化率と反応配分の秩序ある関係を破壊する（Herrnstein, 1961）。並行 VI-VI 配置で COD を省略することは手続き的な懸念事項である。DSL はリンター警告（`MISSING_COD`）を発し、明示的な `COD` 指定を推奨する。`COD=0s`（統制条件用）は受理され、警告を抑制する。COD を省略した場合、ランタイムデフォルトは `COD=0s` となる。

**引用:**
- Herrnstein, R. J. (1961). Relative and absolute strength of response as a function of frequency of reinforcement. *JEAB*, *4*, 267-272. https://doi.org/10.1901/jeab.1961.4-267
- Baum, W. M. (1974). On two types of deviation from the matching law. *JEAB*, *22*, 231-242. https://doi.org/10.1901/jeab.1974.22-231

---

## 3. 連鎖スケジュールによる条件性強化研究

**シナリオ:** コンポーネント移行時の刺激変化が条件性強化子として機能するかを検証する。

```
Chain(FR5, FI30s)
```

**何をするか:** ハトはまず S^D-1（例: 赤色キーライト）の下で FR5（初期リンク）を完了する。完了すると S^D-2（例: 緑色キーライト）に変化し、FI 30s（終端リンク）に移行する。FI 30s 完了で食物が提示される。

**なぜ必要か:** FR5→FI30 移行時の刺激変化は条件性強化子として機能する — 食物への接近を知らせるからだ。Kelleher & Fry (1962) は、刺激-食物距離関係の一貫性が条件性強化力を決定することを示した。連鎖なしでは、有機体が多段階の随伴性をどう学習するかを研究できない。

**Tand との対比:**
```
Tand(FR5, FI30s)   -- 同じ随伴性だが刺激変化なし
```
Jwaideh (1973) は、刺激変化を除去した場合（Tand）に強化後休止が短縮し条件性強化の証拠が弱まることを示した — 刺激変化が活性成分であることの直接的証拠。

**引用:**
- Kelleher, R. T., & Fry, W. T. (1962). Stimulus functions in chained fixed-interval schedules. *JEAB*, *5*, 167-173. https://doi.org/10.1901/JEAB.1962.5-167
- Jwaideh, A. R. (1973). Responding under chained and tandem fixed-ratio schedules. *JEAB*, *19*(2), 259. https://doi.org/10.1901/jeab.1973.19-259

---

## 4. 行動薬理学のための二次スケジュール

**シナリオ:** 2時間セッションで低頻度の薬物投与下で安定したコカイン自己投与行動を維持する。

```
FI600(FR10)
```

**何をするか:** ラットは FR10 ユニット（10回のレバー押しで1ユニット）を繰り返し完了する。各ユニット完了時に brief stimulus（例: 薬物注入と対提示された2秒間のライト）が提示される。FI 600秒（10分）間隔が経過し、次の FR10 ユニットが完了すると、コカイン注入が行われる。

**なぜ必要か:** 薬物自己投与研究では以下が必要:

1. **低頻度の薬物投与** — 頻繁すぎる投与は薬理学的効果を飽和させ、行動分析を不可能にする
2. **セッション全体を通じた安定した反応** — 条件性強化子なしでは、長い強化間間隔で行動が崩壊する
3. **構造化された行動パターン** — ユニットレベルのスキャロッピングが動機づけのダイナミクスを明らかにする。単純な FR や FI ではこれが見えない

二次スケジュールはこれら3つの問題を全て解決する。brief stimulus が条件性強化子として機能し、低頻度の一次強化エピソード間のギャップを架橋する。Kelleher (1966) は、60分に1回という疎な強化（30 × FI 2min）でも、brief stimulus のみで各 FI コンポーネントに秩序あるスキャロップ反応が維持されることを実証した。

**なぜ Tand ではだめなのか:**
```
Tand(FI600, FR10)   -- これは等価ではない
```
`Tand(FI600, FR10)` の意味: 600秒待機し、その後 FR10 を1回完了する。有機体は600秒の待機中に何もしない。対照的に `FI600(FR10)` では、間隔中ずっと FR10 ユニットを活発に完了し続け、行動の時間的パターンに関するデータを産出する。

**引用:**
- Kelleher, R. T. (1966). Conditioned reinforcement in second-order schedules. *JEAB*, *9*, 475. https://doi.org/10.1901/jeab.1966.9-475
- Goldberg, S. R. (1973). Comparable behavior maintained under fixed-ratio and second-order schedules of food presentation, cocaine injection or d-amphetamine injection in the squirrel monkey. *Journal of Pharmacology and Experimental Therapeutics*, *186*(1), 18-30.

---

## 5. 多元スケジュールによる行動的コントラスト

**シナリオ:** 一方の文脈での強化変更が他方の文脈の行動に影響することを示す。

```
Mult(VI60s, VI60s)     -- フェーズ 1: 両成分で等しいスケジュール
Mult(VI60s, EXT)       -- フェーズ 2: 成分 2 を消去に変更
```

**何をするか:** 2つの成分が交替する（異なるキー色で弁別される）。フェーズ 1 では両方 VI 60s。フェーズ 2 で成分 2 を EXT に切り替える。予測: 成分 1 のスケジュールは変更されていないにもかかわらず、成分 1 の反応率が*増加*する — これが行動的コントラスト（Reynolds, 1961）。

**なぜ必要か:** 多元スケジュールは弁別性制御と強化効果を分離する。弁別刺激（異なるキー色）がどのスケジュールが効力中かを有機体に知らせる。弁別なし（Mix）ではコントラスト効果が弱い/消失する — 刺激-スケジュール相関が必要であることの証拠。

**引用:**
- Reynolds, G. S. (1961). Behavioral contrast. *JEAB*, *4*(1), 57-71. https://doi.org/10.1901/jeab.1961.4-57

---

## 6. DRL によるタイミング研究

**シナリオ:** 時間弁別能力の検証 — 有機体は反応間に少なくとも 20秒待てるか?

```
DRL20s
```

**何をするか:** 反応間時間（IRT）が 20秒以上の場合にのみ強化。早すぎる反応はタイマーをリセットする。

**なぜ必要か:** DRL は要求値付近にピークを持つ IRT 分布を産出し、有機体が時間間隔を弁別できることを示す。ピークの精度が有機体のタイミング精度を反映する（Richards et al., 1993）。

**Limited Hold を付加する場合:**
```
DRL20s LH5s
```
反応は前回の反応から 20秒後〜25秒後の間に行わなければならない。早すぎても遅すぎても強化なし。時間窓が狭まり、より精密なタイミング能力が検出できる（Kramer & Rilling, 1970）。

**引用:**
- Richards, R. W., Sabol, T. J., & Seiden, L. S. (1993). DRL interresponse-time distributions. *JEAB*, *60*, 361. https://doi.org/10.1901/jeab.1993.60-361
- Kramer, T. J., & Rilling, M. (1970). Differential reinforcement of low rates: A selective critique. *Psychological Bulletin*, *74*(4), 225-254. https://doi.org/10.1037/h0029813

---

## 7. 累進比率による動機づけ評価

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

**シナリオ:** 負の強化によって維持される回避行動の測定。反応が次の shock を postpone する手続き。

```
Sidman(SSI=20s, RSI=5s)
  @punisher("shock", intensity="0.5mA")
  @operandum("lever")
```

**何をするか:** 反応がない場合、20 秒ごとに shock が発生する（SSI = Shock-Shock Interval）。レバー押し反応ごとに次の shock が 5 秒後に postpone される（RSI = Response-Shock Interval）。形式的には `next_shock = max(last_shock + SSI, last_response + RSI)`。十分訓練されたラットは反応を維持し続け、反応間間隔を RSI より少し短く保つ。

**なぜ存在するか:** Sidman (1953) は、明示的な warning 刺激なしでも時間的随伴性だけで回避行動が維持されることを示した。これは嫌悪制御・不安モデル・行動薬理における負の強化研究の基礎手続きとなった。Sidman 回避は強化スケジュール F/V/R × R/I/T マトリクスでは表現できない — **2 つの独立した時間パラメータ** と反応随伴的な再スケジュール規則を持つため、専用の primitive が必要。

**Alias の等価性:** `@punisher` は実験者の意図を明示するために使用するが、`@reinforcer` も等価な alias:

```
Sidman(SSI=20s, RSI=5s) @reinforcer("shock", intensity="0.5mA")  -- 等価
```

両形式は同じ AST ノードに解決される。

**他スケジュールとの合成:** Sidman は任意の複合コンビネータに入れられる。例えば連鎖スケジュールのリンクとして（de Waard, Galizio, & Baron, 1979）:

```
Chain(FR10 @reinforcer("food"),
      Sidman(SSI=20s, RSI=5s) @punisher("shock"))
```

**参考文献:**
- Sidman, M. (1953). Two temporal parameters of the maintenance of avoidance behavior by the white rat. *Journal of Comparative and Physiological Psychology*, *46*(4), 253-261. https://doi.org/10.1037/h0060730
- Hineline, P. N. (1977). Negative reinforcement and avoidance. In W. K. Honig & J. E. R. Staddon (Eds.), *Handbook of operant behavior* (pp. 364-414). Prentice-Hall.
- de Waard, R. J., Galizio, M., & Baron, A. (1979). Chained schedules of avoidance. *JEAB*, *32*(3), 399-407. https://doi.org/10.1901/jeab.1979.32-399

---

## 9. 複合的な実験プログラム

**シナリオ:** 一方の成分で並行配置、他方で連鎖手続きを使う2成分多元スケジュール。プログラムレベルのデフォルト付き。

```
COD = 2s
LH = 10s

let choice_component = Conc(VI30s, VI60s)
let chain_component = Chain(FR10, FI30s)
Mult(choice_component, chain_component)
```

**何をするか:**
- 成分 1（S^D-1）: 並行 VI30 VI60 + COD 2秒 — 有機体が2つの選択肢間で反応を配分する
- 成分 2（S^D-2）: 連鎖 FR10→FI30 — まず10回反応を完了、次に約30秒待って食物
- 成分は弁別刺激の変化を伴って交替
- 全スケジュールに 10秒の limited hold が適用
- `let` 束縛が複数行プログラムの可読性を確保

**なぜ重要か:** 実際の実験は複数のスケジュール型を組み合わせる。DSL の合成可能性により、行動分析学文献に記述されるあらゆる配置を表現できる。名前付き束縛が複雑な設計を読みやすく保つ。

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
| `COD` / `FRCO` | クリーンな並行データ | 高速切替による強化率膨張 |
| `Sidman` | 自由オペラント回避、嫌悪制御 | 無弁別回避手続きを表現できない |
| `let` | 可読な複雑プログラム | 読めないネスト式 |

---

## 参照文献（追加）

- Catania, A. C. (2013). *Learning* (5th ed.). Sloan Publishing.
- Cooper, J. O., Heron, T. E., & Heward, W. L. (2020). *Applied behavior analysis* (3rd ed.). Pearson.
- Ferster, C. B., & Skinner, B. F. (1957). *Schedules of reinforcement*. Appleton-Century-Crofts.
