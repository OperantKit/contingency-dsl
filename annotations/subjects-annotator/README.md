# subjects-annotator — JEAB Subjects Category

## Status: Restructured (2026-04-12)

本 annotator は 2026-04-12 に `subject-annotator` から `subjects-annotator`
へ改名された。JEAB Method 節の伝統的見出し「Subjects」（複数形）と 1:1 で
一致させる annotator 再編の一環である（[annotation-design.md §3.7](../../spec/annotation-design.md)
参照）。

## Recommended Scope: Program-level

subjects-annotator のキーワードはすべて**プログラムレベル**（セッション全体のデフォルト）
として宣言することを推奨する。被験体条件はセッション内で不変の境界条件であり、
論文 Method セクションでは Subjects として Procedure の前に記述される
（Sidman, 1960; Ferster & Skinner, 1957）。

```
-- 推奨: プログラムレベル
@species("rat")
@strain("Long-Evans")
@deprivation(hours=22, target="food")
@history("naive")
@n(8)

FR5
  @operandum("left_lever")
```

構文的にはスケジュールレベルでも使用可能（上書き用途）。
ただし yoked control 等の複数被験体実験では、被験体は別セッションで実施されるため
通常は上書きの必要はない。

## Keywords (Candidates)

| Keyword | Purpose | Example |
|---|---|---|
| @species | 種の宣言 | `@species("rat")` |
| @strain | 系統の宣言 | `@strain("Long-Evans")` |
| @deprivation | 遮断操作 | `@deprivation(hours=22, target="food")` |
| @history | 実験経験歴 | `@history("naive")` or `@history("prior_FR_training")` |
| @n | 個体数 | `@n(6)` |

## Boundary Justification

**この annotation がないと理論的議論ができないか: NO**

- スケジュール理論は種に依存しない（matching law はハトでもラットでもヒトでも成立する）。
- 遮断操作は確立操作 (EO) の一形態であり、スケジュールの数学的性質ではない。

**この annotation が DSL 内にあるべき理由:**

- 実験の再現には被験体条件が不可欠。
- @deprivation は確立操作の記述であり、強化子の効力に直接関わる。
- 論文コンパイル時に Subjects section に直接反映される。
- 種特異的行動レパートリーが実験解釈に影響する場合がある
  （例: ラットのレバー押し vs ハトのキーつつき）。

## Inclusion Criteria

- 被験体の **生物学的条件**（種・系統・体重・齢）に関する宣言。
- 被験体の **動機づけ操作**（遮断・飽和）に関する宣言。
- 被験体の **経験的条件**（ナイーブ・事前訓練歴）に関する宣言。

## Exclusion Criteria

- 被験体の **内的状態の推定**（「不安レベル」「動機づけ水準」）→ メンタリスト用語。
  行動分析学では確立操作として記述する。
- 被験体の **反応トポグラフィ**（「左手でレバーを押した」）→ これはデータであり宣言ではない。
- 群分けやカウンターバランス → 実験デザインレベルの問題。session metadata。

## Open Questions

- @deprivation は subjects-annotator と procedure-annotator/temporal の境界にある
  （「22時間の遮断」は時間情報だが、被験体条件でもある）。
  → 被験体の確立操作として subjects-annotator に置くのが行動分析学的に自然。
- LLM 被験体 (ai-operant-box) の場合、@species は何になるか?
  → `@species("llm", model="claude-sonnet-4-6")` のような拡張が必要かもしれない。

## Dependencies

なし。
