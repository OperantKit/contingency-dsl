# 実験層における文脈

> contingency-dsl 実験層の一部。フェーズレベル構成要素としての文脈を詳細化する: 時間的・空間的・刺激的文脈を命名してフェーズに付与することで、更新（renewal）、再発（reinstatement）、および文脈駆動レスポンデント手続きが姉妹パッケージ `contingency-respondent-dsl` で表現可能となる。基盤レベルの文脈定義は `foundations/context.md` に置く。本ファイルは実験層構文を規定する。

**関連文書:**
- [基盤 / 文脈](../foundations/context.md) — パラダイム中立な文脈型付け（時間的・空間的・刺激的）。
- [実験 / フェーズ列](phase-sequence.md) — 文脈を付与するフェーズレベル構成要素。
- [実験 / 論文](paper.md) — 文脈を含む body を格納する Experiment / Paper ラッパ。
- [レスポンデント理論](../respondent/theory.md) — 消去と更新にとって文脈が重要な理由。

---

## 1. 文脈が一級である理由

Bouton (2004) は、文脈が連合の要素として参加するのではなく学習された連合の想起を調整する証拠をレビューしている。CS–US 対提示がある文脈で消去され、異なる文脈でテストされるとき、CR は更新される（renewal 効果）。ある周囲条件下で学習された CS–US 随伴性は、それらの条件が変わると異なる振る舞いをする。

DSL が更新・再発・自発回復・文脈駆動準備を表現するためには、以下が可能でなければならない。

1. 文脈の **命名**（例: `A`, `B`、または `room_a`, `dark_chamber` のような記述的名前）。
2. 文脈の **フェーズへの付与**（フェーズがその文脈「内で」実行されるように）。
3. フェーズ間での文脈の **比較**（基準と注釈が文脈変化を参照できるように）。

姉妹パッケージ `contingency-respondent-dsl` はこの基盤を用いて Tier B 更新手続き（ABA, ABC, AAB）および再発を表現する。contingency-dsl 実験層はそれらの手続きを列挙しない。フェーズレベル構文を提供する。

## 2. フェーズ属性としての文脈

フェーズはプログラムが選んだ符号化に応じて、`@context` 注釈または専用の `context` フィールドを介して自身の文脈を指定できる。両形式とも許容される。

**注釈形式**（標準）:
```
Phase(
  label = "Acquisition",
  schedule = Pair.ForwardDelay(tone, shock, isi=10-s, cs_duration=15-s),
  phase_annotations = [@context(name="A", location="room_a")],
  criterion = FixedSessions(count=5)
)
```

**フィールド形式**（構造的）:
```
Phase(
  label = "Acquisition",
  schedule = Pair.ForwardDelay(tone, shock, isi=10-s, cs_duration=15-s),
  context = ContextA,
  criterion = FixedSessions(count=5)
)
```

注釈形式は、`phase-sequence.md §2.1` の JEAB 注釈継承規則に参加するため推奨される: `shared_annotations` レベルで宣言された `@context` は上書きされない限り各フェーズに継承される。フィールド形式は AST で構造的表現を好むプログラムのために提供される。両形式は意味論的に等価である。

## 3. 文脈カテゴリ座標

`foundations/context.md §2` に従い、文脈は 3 つの座標を持つ。

| カテゴリ | 注釈座標 | 例 |
|---|---|---|
| 時間的 | `time=`（時刻、セッション時隔） | `@context(time="morning")` |
| 空間的 | `location=`（チャンバー、部屋識別子） | `@context(location="room_a")` |
| 刺激的 | `cue=`（環境音、ハウスライト、匂い） | `@context(cue="house_light_off")` |

どれかの座標が異なれば、2 つの文脈は異なる。プログラムは、不一致を更新対象の文脈変化として解釈するか、ノイズレベルの差として解釈するかを決める。DSL は解釈ではなく座標のみを宣言する。

## 4. `@context` 注釈と `@iti` / `@cs` / `@us`

`@context` は `annotations/extensions/respondent-annotator.md` で定義されるレスポンデント注釈（`@cs`, `@us`, `@iti`, `@cs_interval`）と共存する。役割分担:

- `@context` — フェーズが実行される周囲条件。
- `@cs`, `@us` — CS と US 自身のメタデータ（文脈ではない）。
- `@iti` — ジッターを含む試行間隔のメタデータ。

すべてフェーズレベル（またはそれ以上）で付与され、共有／フェーズ別機構を通じて継承される。

## 5. 設計スコープ: このファイルが定義しないもの

本ファイルは文脈駆動手続きのための **基盤** を定義するが、手続き自身は列挙しない。具体的には:

- **ABA / ABC / AAB 更新** — Tier B、この基盤を用いて `contingency-respondent-dsl` で定義される。
- **再発** — Tier B、`contingency-respondent-dsl` で定義される。
- **自発回復** — Tier B（ただし文脈変化より保持時隔に関連）、`contingency-respondent-dsl` で定義される。
- **文脈的恐怖条件づけ** — Tier B、`contingency-respondent-dsl` で定義される。

ここで提供される基盤は、それらの拡張が文法を変更せずに DSL で手続きを記述するために最低限必要なものである。

## 6. 例 — 2 つの文脈での獲得／消去計画

```
PhaseSequence(
  shared_annotations = [
    @subjects(species="rat", n=8),
    @apparatus(chamber="chamber_1")
  ],
  phases = [
    Phase(
      label = "Acquisition",
      schedule = Pair.ForwardDelay(tone, shock, isi=10-s, cs_duration=15-s),
      phase_annotations = [@context(name="A", location="room_a")],
      criterion = FixedSessions(count=5)
    ),
    Phase(
      label = "Extinction",
      schedule = Extinction(tone),
      phase_annotations = [@context(name="B", location="room_b")],
      criterion = FixedSessions(count=5)
    ),
    Phase(
      label = "Test",
      schedule = CSOnly(tone, trials=8),
      phase_annotations = [@context(name="A", location="room_a")]      -- A に戻る
    )
  ]
)
```

これは 2 つの文脈にまたがる獲得／消去／テスト配置を符号化する — `contingency-respondent-dsl` が完全な診断的意味論を伴う ABA 更新手続きに詳細化する contingency-dsl レベルの基盤である。

## 参考文献

- Bouton, M. E. (2004). Context and behavioral processes in extinction. *Learning & Memory*, 11(5), 485–494. https://doi.org/10.1101/lm.78804
- Bouton, M. E., & Bolles, R. C. (1979). Contextual control of the extinction of conditioned fear. *Learning and Motivation*, 10(4), 445–466. https://doi.org/10.1016/0023-9690(79)90057-2
