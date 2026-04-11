# stimulus-annotator — Stimulus Identity Dimension

## Status: Schema Design

## Keywords

| Keyword | Purpose | Example |
|---|---|---|
| @reinforcer | 強化子の同定・分類 | `@reinforcer("food", type="unconditioned")` |
| @sd | 弁別刺激の同定 | `@sd("red_light", component=1)` |
| @operandum | 反応装置の同定 | `@operandum("left_lever")` |
| @brief | 二次スケジュールの短時間刺激 | `@brief("light", duration=2)` |

## Boundary Justification

**この annotation がないと理論的議論ができないか: NO**

- `FI 10` だけでスキャロップは議論できる。
- `Conc(VI 30, VI 30)` だけでマッチング法則は議論できる。
- stimulus-annotator は「どのレバーを」「何が強化子か」を宣言するが、
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
- 刺激の **物理的仕様**（LED の波長、音のデシベル）→ apparatus-annotator の責務。
- 刺激の **時間的構造**（呈示時間、ISI）→ temporal-annotator の責務。

## Dependencies

なし（他の annotator を requires しない）。

## Python Implementation Reference

`apps/experiment/contingency-annotator/src/contingency_annotator/stimulus_annotator/`
