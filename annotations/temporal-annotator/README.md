# temporal-annotator — Session Temporal Dimension

## Status: Proposed

## Keywords (Candidates)

| Keyword | Purpose | Example |
|---|---|---|
| @clock | 時間単位の宣言 | `@clock(unit="s")` |
| ~~@blackout~~ | ~~ブラックアウト期間~~ | **Moved to core grammar (v1.1)** — BO は Mult/Mix の keyword argument に昇格。COD の先例と同じ。Issue #28 参照 |
| @warmup | セッション開始前のウォームアップ | `@warmup(duration=60)` |
| @algorithm | スケジュール値生成アルゴリズム | `@algorithm("fleshler-hoffman", n=12)` |
| ~~@cod~~ | ~~切り替え遅延~~ | **Moved to core grammar (v1.1)** — see below |

## Boundary Justification

**この annotation がないと理論的議論ができないか: NO**

- `VI 30` だけで反応率の議論ができる。
- 時間単位 (s/ms/min) はコア grammar.ebnf の `time_unit` で既にサポート。
- temporal-annotator はセッションレベルの時間構造を宣言する。

**この annotation が DSL 内にあるべき理由:**

- 異なる実験装置間で同一の時間構造を保証するために必要。
- @algorithm は再現性の核心（Fleshler-Hoffman vs arithmetic VI は結果に影響する）。
- 論文コンパイル時に時間パラメータが Methods section に直接反映される。

## Inclusion Criteria

- セッションの **時間的構造** に関する宣言であること。
- **どの時間をどう測るか** の宣言であること。

## Exclusion Criteria

- 強化子の **呈示時間** → stimulus-annotator (@brief) or @reinforcer の duration param。
- 被験体の **履歴的時間**（何日目のセッションか）→ subject-annotator or session metadata。
- 装置の **応答遅延**（レバー接触から信号到達まで） → apparatus-annotator。

## Open Questions

- `@algorithm` は temporal-annotator に属するか? VI/VR の値生成アルゴリズムは
  「時間」というより「分布」の次元。独立した annotator (distribution-annotator?) の候補。
- ~~`@cod` は temporal-annotator か?~~ **Resolved (v1.1):** COD はコア文法の
  Conc キーワード引数に移動済み: `Conc(VI30s, VI60s, COD=2s)`。
  COD は随伴性の定義的パラメータであり、セッションレベルの時間メタデータではない
  (Herrnstein, 1961)。Issue #9 参照。
- ~~`@blackout` は temporal-annotator か?~~ **Resolved (v1.1):** BO はコア文法の
  Mult/Mix キーワード引数に移動済み: `Mult(FR5, EXT, BO=5s)`。
  BO の持続時間は成分間の行動的コントラスト（Reynolds, 1961）と連合的独立性
  （Bouton, 2004）に直接影響する構造的パラメータであり、COD と同じ論理で
  コア文法に属する。Issue #28 参照。

## Dependencies

なし。
