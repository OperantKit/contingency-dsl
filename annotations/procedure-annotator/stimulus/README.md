# procedure-annotator/stimulus — Stimulus Identity Sub-Annotator

**Parent annotator:** [procedure-annotator](../README.md) (JEAB category: Procedure)

## Status: Schema Design

## Role within procedure-annotator

The `stimulus` sub-annotator declares the **identity and function** of stimuli
used in the experimental procedure (reinforcers, discriminative stimuli,
second-order brief stimuli). Together with the sibling `temporal`
sub-annotator, it composes the `procedure-annotator` module which maps to the
JEAB-aligned **Procedure** category (see
[design-philosophy.md §4.1](../../../spec/ja/design-philosophy.md)).

Note: `@operandum` was previously owned by this sub-annotator but moved to
[apparatus-annotator](../../apparatus-annotator/README.md) on 2026-04-12 to
align with JEAB Apparatus conventions.

## Keywords

| Keyword | Purpose | Example |
|---|---|---|
| @reinforcer | 強化子の同定・分類（基本形） | `@reinforcer("food", type="unconditioned")` |
| @sd | 弁別刺激の同定 | `@sd("red_light", component=1)` |
| @brief | 二次スケジュールの短時間刺激 | `@brief("light", duration=2)` |

**注記:** `@operandum`（反応装置の同定）は以前この sub-annotator に属していたが、
2026-04-12 に **apparatus-annotator** へ移管された。操作体（レバー、キー等）は
JEAB Method 節の Apparatus セクションで記述されるのが伝統的であり、その慣習に
合わせた再分類である。詳細は
[spec/annotation-design.md §3.6](../../../spec/ja/annotation-design.md) を参照。

## Keyword Aliases — `@reinforcer` / `@punisher` / `@consequentStimulus`

`@reinforcer` には 2 つの等価な type alias が用意されている。3 つのキーワードは
**AST レベルで同一のノードに collapse される** が、source 上では実験者の意図を
明示的に区別できる。`@reinforcer` が基本形（primary form）であり、行動分析学の
標準的な用語として最も確立されているため、通常はこれを使用する。

| Keyword | 用途 | 例 |
|---|---|---|
| `@reinforcer` | **基本形 (primary)** — 強化子の宣言（標準） | `@reinforcer("food")` |
| `@punisher` | alias — 罰子としての使用意図を明示 | `@punisher("shock", intensity="0.5mA")` |
| `@consequentStimulus` | alias — 理論的に中立な表記 | `@consequentStimulus("tone", duration=2)` |

### 等価性の保証

```
FR3 @reinforcer("shock")         -- equivalent
FR3 @punisher("shock")           -- equivalent
FR3 @consequentStimulus("shock") -- equivalent
```

3 者は AST 上で同じ `Reinforcer(stimulus="shock", label=...)` ノードに
変換される。`label` フィールドは source の表記を保持するが、等価性判定では
**pragmatic hint** として扱われ、semantic 等価性に影響しない。

### 設計根拠

Radical behaviorism の立場では reinforcer / punisher は **機能的（効果による
事後的）定義** を持つため、a priori にラベル付けすることには批判がある。
しかし本 DSL は **手続き記述言語** であり、実験者の意図を記述するものである。
「この刺激を罰子として使う意図で提示する」という宣言は手続き的に正当であり、
論文コンパイル時に Methods セクションの文言選択に使用できる。

基本形（primary form）が `@reinforcer` である理由:
- **EAB 文献で最も確立された用語**。行動分析学の中核概念は「強化」であり、
  強化子の宣言は実験記述の出発点である。
- 既存の stimulus-annotator 実装がこの keyword を中心に構築されている
- `@punisher` / `@consequentStimulus` は後発の拡張であり、alias として
  実装コストが最小

### 用語選択の注記

「基本形」という表現は `primary form` または `base form` の訳語として用いる。
`canonical form` は、プログラミング/型理論から借用した用語で JEAB 文献の
普遍的術語ではないため、本文書では避ける。

## Boundary Justification

**この annotation がないと理論的議論ができないか: NO**

- `FI 10` だけでスキャロップは議論できる。
- `Conc(VI 30, VI 30)` だけでマッチング法則は議論できる。
- この sub-annotator は「何が強化子か」「どの弁別刺激か」を宣言するが、
  スケジュールの数学的性質には影響しない。

**この annotation が DSL 内にあるべき理由:**

- 実験を実行するには強化子と反応装置の対応付けが必要。
- 条件性強化子の backup chain は referential integrity を持つ（検証可能）。
- 論文コンパイル時に reinforcer の記述が Methods section に直接反映される。

## Inclusion Criteria

- 刺激の **同一性**（identity）に関する宣言であること。
- 刺激の **機能**（function as SD, reinforcer, etc.）の宣言であること。

## Exclusion Criteria

- 刺激の **学習履歴**（associative history）→ これは runtime state であり DSL 宣言ではない。
- 刺激の **物理的仕様**（LED の波長、音のデシベル）→ [apparatus-annotator](../../apparatus-annotator/README.md) の責務。
- 刺激の **時間的構造**（呈示時間、ISI）→ sibling sub-annotator [temporal](../temporal/README.md) の責務。
- **反応装置の同定**（`@operandum`）→ [apparatus-annotator](../../apparatus-annotator/README.md) (2026-04-12 移管)

## Dependencies

なし（他の annotator を requires しない）。

## Python Implementation Reference

`apps/experiment/contingency-annotator/src/contingency_annotator/procedure_annotator/stimulus/`
