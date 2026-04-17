# 文脈（context）— 一級オブジェクトとしての時間的・空間的・刺激的文脈

> contingency-dsl 基盤層の一部。文脈を基盤的構成要素として定義し、`contingency-respondent-dsl` 拡張パッケージで予定されている更新（renewal）、再発（reinstatement）、文脈駆動レスポンデント手続きを支える。

---

## 1. 文脈とは何か

**定義 1（文脈）.** 文脈とは、試行・セッション・フェーズの間を通じて有効であり続けるが、随伴性の対象刺激そのものではない環境条件の集合である。随伴性（二項または三項）は文脈 *の中で* 作動し、文脈自身が CR や Sr+ を直接産出することはない。

Bouton（2004, §2）は現代的見解を明確化している。すなわち、文脈は連合の要素として参加するのではなく、学習された連合の想起を調整する。CS–US 対提示が文脈 B で消去され、元の文脈 A でテストされたとき、反応が更新される（ABA renewal）。文脈の役割は曖昧さの解消であり、連合的ではない。

## 2. 3 つの文脈カテゴリ

DSL は 3 つの文脈カテゴリを認識する。

| カテゴリ | 例 | パラメータ化 |
|---|---|---|
| **時間的文脈** | 時刻、セッション番号、経過セッション時間 | `@context(time=...)`, フェーズ順序 |
| **空間的文脈** | チャンバー、部屋、装置識別子 | `@context(location=...)`, `@apparatus` |
| **刺激的文脈** | 環境音、ハウスライト、嗅覚手がかり | `@context(cue=...)`, 背景刺激 |

文脈は 1 つ以上のカテゴリにわたる座標の集合によって指定される。どれかの座標が異なれば、2 つの文脈は異なる。

## 3. 一級オブジェクトとしての文脈

文脈は 2 つの意味で一級である。

1. **基盤レベルの型.** 文脈は DSL の型格子における名前付き実体である。式は文脈識別子を参照でき、注釈は特定の文脈にスコープ付けできる。
2. **実験層の構成要素.** フェーズは自身の文脈を宣言でき、相変化基準は文脈変化を参照できる。フェーズレベルの具体文法は `experiment/context.md` を参照。

この両建て配置（基盤型 + 実験層構成要素）は、文脈が振る舞いを駆動するような手続き、すなわち Bouton（2004）の更新計画（ABA / ABC / AAB）、再発手続き（Rescorla & Heth, 1975）、occasion-setting 準備（Holland, 1983）を支えるために必要である。

## 4. 文脈 vs 弁別刺激

文脈と弁別刺激（SD）は形式的に区別可能である。

- **SD** は、その存在が特定の反応が強化されるタイミングを合図する刺激である。SD は三項随伴性 `(SD, R, SR)` の一部であり、その統制は差異的である。
- **文脈** は、そもそも随伴性が適用される条件を設定する。文脈統制は反応を差異的に選択するのではなく、随伴性全体の想起を調整する。

この区別は操作的には微妙である。持続的に維持された弁別刺激は文脈として機能しうる。DSL の規約: 刺激が随伴性内で反応率を差異的に統制するときは SD（`@sd`）として、どの随伴性が想起されるかを調整するときは文脈（`@context`）としてラベル付けする。リンターは区別が不明瞭な場合に助言的警告を発しうるが、文法的な強制制約は設けない。

## 5. 現在フェーズにおけるスコープ（現在）

現在の設計チェックポイントにおいて、基盤層は文脈の **型** のみを固定する。文脈依存レスポンデント手続き（renewal, reinstatement, occasion setting）の具体文法は `contingency-respondent-dsl`（Tier B 拡張パッケージ）にあり、この基盤的定義に依拠する。

`experiment/context.md` は、多相計画で文脈を宣言するためのフェーズレベル構文を規定する。これが現行 DSL プログラムが ABA・ABC・AAB 構造を表現するための機構である。

## 6. この層で **定義しない** もの

- **文脈類似性指標**（文脈 B は文脈 A にどれほど類似しているか?）。そのような指標は行動的／理論的なものであり、DSL レベルではない。
- 装置注釈からの **自動的な文脈抽出**。文脈は明示的に宣言せねばならない。
- **被験体間の文脈共有**（一方の被験体の文脈が他方のものを決定するような配置）。これは `contingency-core` の関心事である。

## 参考文献

- Bouton, M. E. (2004). Context and behavioral processes in extinction. *Learning & Memory*, 11(5), 485–494. https://doi.org/10.1101/lm.78804
- Bouton, M. E., & Bolles, R. C. (1979). Contextual control of the extinction of conditioned fear. *Learning and Motivation*, 10(4), 445–466. https://doi.org/10.1016/0023-9690(79)90057-2
- Holland, P. C. (1983). Occasion-setting in Pavlovian feature positive discriminations. In M. L. Commons, R. J. Herrnstein, & A. R. Wagner (Eds.), *Quantitative analyses of behavior: Discrimination processes* (Vol. 4, pp. 183–206). Ballinger.
- Rescorla, R. A., & Heth, C. D. (1975). Reinstatement of fear to an extinguished conditioned stimulus. *Journal of Experimental Psychology: Animal Behavior Processes*, 1(1), 88–96. https://doi.org/10.1037/0097-7403.1.1.88
