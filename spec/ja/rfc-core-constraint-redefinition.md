# RFC: Core 制約の再定義 — 「CFG + 非TC」から「CFG + パラメータ宣言的」へ

> **Status:** Superseded (2026-04-13)
>
> **本 RFC は RFC_CORE_STATEFUL_2026-04-13.md により superseded された。**
> 本 RFC が提起した問題（Pctl/Adj が共有語彙であるべき）は、Core の制約を
> 再定義するのではなく、Core-Stateful 層を additive に追加することで解決された。
> 本 RFC §2 の分析（宣言と計算の区別）は後継 RFC に継承されている。
>
> 以下は元の Draft テキストをそのまま保存したものである。

---

## 1. 問題

### 1.1 現行の制約

design-philosophy.md §5.1 は、Percentile schedule 等を Core から除外する
根拠として次の論理を用いている:

> TC 近傍（動的計算・状態保持・履歴参照が必要）の性質を持つため、
> Core DSL の CFG / 非 TC 方針にもそのまま組み込むことはできない。

現行の定式化:

```
Core = CFG 構文 + 非TC 意味論
```

> **CFG（文脈自由文法, Context-Free Grammar）とは:**
> Chomsky 階層の Type-2 に位置する形式文法。生成規則の左辺が
> 単一の非終端記号に限定されるため、「文脈に依存しない」置換規則で
> 言語を定義する。プッシュダウンオートマトンで認識可能であり、
> 入れ子構造（括弧の対応、再帰的な式の構成）を扱える。
> BNF / EBNF はこの文法クラスを記述する標準的な表記法である。
> contingency-dsl では grammar.ebnf の全生成規則がこのクラスに準拠し、
> 再帰下降パーサにより O(n) 時間で構文解析が完了する。
>
> — Chomsky, N. (1956). Three models for the description of language.
> *IRE Transactions on Information Theory*, *2*(3), 113-124.
> — Hopcroft, J. E., Motwani, R., & Ullman, J. D. (2006).
> *Introduction to automata theory, languages, and computation* (3rd ed.). Pearson.
>
> **非TC（非チューリング完全, non-Turing-complete）とは:**
> 任意のチューリング機械を模倣できない計算体系。チューリング完全な
> 体系（Python, Rust 等の汎用言語）では停止問題が決定不能であり、
> 「このプログラムは有限時間で終了するか」を一般的に判定できない。
> 非TC にとどめることで、スケジュール式の到達可能性（強化子を
> 生じうるか）、死コード検出、構造的等価性判定など、実験者にとって
> 重要な性質の検証が決定可能になる。表現力と検証可能性の
> トレードオフにおいて、検証可能性を優先する設計選択である。
>
> — Turing, A. M. (1936). On computable numbers, with an application to
> the Entscheidungsproblem. *Proceedings of the London Mathematical Society*,
> *s2-42*(1), 230-265. https://doi.org/10.1112/plms/s2-42.1.230
> — Sipser, M. (2012). *Introduction to the theory of computation* (3rd ed.). Cengage.

### 1.2 矛盾

この制約は design-philosophy.md 自身の以下の要件と矛盾する:

**§1（最上位目的）:**
> 現在までの（特に行動分析学の）すべての実験手続きを、正確に DSL 上で
> 表現できるようにする。

**§3.1（Core の使い手）:**
> FR5, Chain(FR5, FI30), Conc(VI30s, VI60s) のような記述は、
> 行動分析学を学んだ人間が読み書きできる共通記法として機能しなければならない。

**§2（経験的に安定な基礎）:**
> 三項随伴性の基礎と強化スケジュールはこれまで破綻することなく、
> 学派として安定な基礎を成してきた。

Percentile schedule（Platt, 1973; Galbicka, 1994）は 50 年以上の歴史を持つ
確立された強化スケジュールであり、実験家の間では FR / FI / VI 等と同列に
議論される。これを Schedule Extension（program-scoped = 方言）に分類することは:

1. §1 の「すべての実験手続き」の共通表現を達成できない
2. §3.1 の「共通記法」としての通用範囲を狭める
3. §2 の「経験的に安定な基礎」に含まれるべきものを除外している

### 1.3 懸念される帰結

動的スケジュールが共通言語から除外されることで:

- 理論的に美しくないとして設計に入らない
- 設計に入っていないために共通言語として扱いにくい
- 会話頻度が減り研究の議論・比較が阻害される

これは DSL が「学術的堅牢性を保ちつつ、理論の発展・衰退に追従する」
（§2）という目的に反する。

---

## 2. 分析: 「非TC」制約の再検討

### 2.1 Core の既存スケジュールも動的評価を必要とする

| スケジュール | パラメータ | 評価時の動的処理 |
|---|---|---|
| FR 5 | 5（静的） | 反応カウント |
| FI 30s | 30s（静的） | タイマー |
| DRL 5s | 5s（静的） | IRT の時間測定と比較 |
| Pctl(IRT, 50) | IRT, 50（静的） | IRT 分布の百分位算出 |
| Adj(start=FR1, step=2) | FR1, 2（静的） | パラメータの動的調整 |

すべてのスケジュールで**パラメータはパース時に確定**している。
動的なのは**評価時の処理**であり、Core と Extension の間に
「静的 vs 動的」の断絶は**パラメータ宣言のレベルには存在しない**。

### 2.2 実際の差異は「評価の計算量」であり「構文の性質」ではない

- FR 5: カウンタをインクリメントして 5 と比較 → O(1)
- DRL 5s: 現在時刻と最終反応時刻の差を算出 → O(1)
- Pctl(IRT, 50): IRT のヒストリから百分位を算出 → O(n) 〜 O(n log n)

計算量は異なるが、**構文（パラメータの宣言形式）は同一の性質**を持つ。
CFG で記述可能な点も同一。

### 2.3 「非TC」が実際に保護していたもの

Core の「非TC」制約が保護しようとしていたのは:

1. **構文の決定可能性** — パーサが確実に停止する → CFG で達成（変更なし）
2. **パラメータの静的検証** — 型・範囲を compile time に検証できる → パラメータが宣言的であれば達成
3. **スケジュール構造の静的比較** — 2 式が構造的に等価か判定できる → パラメータが宣言的であれば達成

これらはいずれも「パラメータが宣言的」という制約で保護可能であり、
「評価が非TC」まで要求する必要がない。

---

## 3. 提案

### 3.1 Core の制約を再定義する

```
現行: Core = CFG 構文 + 非TC 意味論
提案: Core = CFG 構文 + パラメータが宣言的（リテラル値で静的に指定される）
```

**「パラメータが宣言的」の定義:**
スケジュール構成素のすべてのパラメータが、パース時に確定するリテラル値
（数値・文字列・列挙型・他のスケジュール式への参照）で指定されること。
パラメータ自体が実行時に計算される式であってはならない。

### 3.2 Core / Extension の新境界

| | Core | Extension |
|---|---|---|
| 基準 | 学派で確立 + パラメータが宣言的 | 未標準化 or パラメータが計算式 |
| 通用範囲 | 全プログラム共通 | program-scoped |
| 例 | FR, FI, DRL, Pctl, Adj, Conj | 研究室独自スケジュール, UserDefined |
| 静的検証 | パラメータの型・範囲を検証可 | Extension module が規則を提供 |

### 3.3 Extension に残るもの

Schedule Extension 層は「動的スケジュールの受け皿」から
「未標準化・ユーザー定義構成素の受け皿」に役割が変わる:

- 研究室独自のスケジュール構成素
- パラメータが計算式で指定されるスケジュール
- 標準化の合意に至っていない実験的構成素

---

## 4. design-philosophy.md への改訂箇所

本提案が採択された場合、以下の箇所を改訂する:

### 4.1 §2 の表

| 層 | 変更内容 |
|---|---|
| Core | 「破壊的変更は原則として避ける」→ 変更なし |
| Schedule Extension | 「動的・TC 近傍の schedule 構成素」→「未標準化・ユーザー定義の schedule 構成素」 |
| Annotation | 変更なし |

### 4.2 §5.1 の論理

「TC 近傍の性質を持つため Core に組み込めない」を撤回し、
「パラメータが宣言的か否か」および「学派で確立されているか」を
Core/Extension 境界の基準とする。

### 4.3 §5.2 の位置付け表

Schedule Extension の役割を「動的・TC 近傍」から
「未標準化・ユーザー定義」に変更。

### 4.4 §5.4 の境界判定

「動的な計算・状態保持を要するか」を境界基準から除外し、
「パラメータが宣言的か」「学派で確立された構成素か」に置換。

### 4.5 §5.6 の候補リスト

percentile-extension / adjusting-extension / conjugate-extension を
Extension 候補から Core 追加候補に移動。

### 4.6 grammar.ebnf への追加

`base_schedule` に additive に生成規則を追加。具体的な構文は別途議論。

---

## 5. 未解決の論点

- [ ] Pctl / Adj / Conj の具体的な構文（パラメータシグネチャ）
- [ ] 「学派で確立」の判断基準（年数? 引用数? JEAB 掲載? 教科書記載?）
- [ ] Core に昇格させる際の査読プロセス
- [ ] 既存の §5.3.5（等価性判定は extension の責務）を Core 内でどう扱うか
  — Pctl 同士の等価性は Core 規則で判定すべきか

---

## 参照

- design-philosophy.md §1, §2, §3.1, §5.1–5.6, §8.1
- Platt, J. R. (1973). Percentile reinforcement: Paradigms for experimental
  analysis of response shaping. In G. H. Bower (Ed.), *The psychology of
  learning and motivation* (Vol. 7, pp. 271–296). Academic Press.
- Galbicka, G. (1994). Shaping in the 21st century: Moving percentile
  schedules into applied settings. *Journal of Applied Behavior Analysis*,
  *27*(4), 739–760. https://doi.org/10.1901/jaba.1994.27-739
