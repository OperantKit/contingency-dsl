# フェーズ列 — 一級の多相実験計画

> contingency-dsl 実験層の一部。`PhaseSequence` 構成要素、`Phase` 要素とその注釈継承規則、`no_schedule` フェーズ変種、および設計を動機づける JEAB 準拠の Method セクション慣習を定義する。本ファイルは人間向けの仕様である。対応する JSON Schema は `schema/experiment/phase-sequence.schema.json` にある。

**関連文書:**
- [実験 / 論文](paper.md) — 複数実験刊行物のための Experiment / Paper ラッパ。
- [実験 / 文脈](context.md) — 一級の文脈と、フェーズ配列との相互作用。
- [実験 / 基準](criteria.md) — 相変化基準（`Stability`, `FixedSessions`, `PerformanceCriterion`, `CumulativeReinforcements`, `ExperimenterJudgment`）。
- [レスポンデント・プリミティブ](../respondent/primitives.md) — フェーズに現れるレスポンデント・プリミティブ。
- [オペラント文法](../operant/grammar.md) — フェーズに現れるオペラント産出規則。
- [合成 / PIT](../composed/pit.md) — 標準的な多相合成手続き。

---

## 1. 根拠

JEAB 論文および関連 EAB 出版物は、実験手続きを Procedure セクションでフェーズごとに記述する: 獲得相に続く消去相、ベースラインに続く処置と反転、等。個別の随伴性はフェーズの時間的順序や相変化基準の宣言的性質を捉えない。実験層はこの多相構造を一級構成要素へ昇格させる。

`PhaseSequence` は順序付きのフェーズ列であり、各フェーズは自身のスケジュール（オペラント）および／またはレスポンデント式と、オプショナルな相変化基準を持つ。最終フェーズは終端である — その完了で実験が終わるため基準を持たない。

## 2. `PhaseSequence` 構成要素

```
PhaseSequence(
  shared_annotations = [...],           -- 各フェーズに継承される
  shared_param_decls = [...],            -- 各フェーズに継承される
  phases = [Phase1, Phase2, ..., PhaseN]
)
```

`PhaseSequence` は最低 2 つのフェーズを持つ。単相実験は裸の `Program` に過ぎない（`foundations/grammar.md §2` 参照）。

### 2.1 共有 vs フェーズ別注釈

JEAB Method セクションは、通常、Procedure の冒頭で Subjects と Apparatus を一度記述し、その後各フェーズを逐次記述する。DSL はこの慣習を反映する。

- **共有注釈**（Subjects、Apparatus、一般的な Procedure）は `PhaseSequence` に付与され、各フェーズに継承される。
- **フェーズ別注釈**（フェーズ固有の Procedure 詳細、フェーズ固有の Measurement）は個別の `Phase` ノードに付与され、同じ注釈名が共有と両方に現れる場合はキーワード単位で上書きする。

継承は単純なキーワードレベルの上書きである: 共有レベルが `@context(location="room_A")` を定義し、フェーズが `@context(location="room_B")` を定義する場合、フェーズは `room_B` を用いる。フェーズが共有対応物なしに `@renewal_test` を追加した場合、そのフェーズのみに追加される。

### 2.2 `no_schedule` フェーズ変種

一部のフェーズにはオペラント随伴性がない。パヴロフ型再評価、文脈曝露、馴化、特定の回復介入は、計画された反応-結果関係なしに刺激を呈示するか、文脈条件を作動させる。DSL はこれを `Phase.schedule = null` を許容することで表現する。

```
Phase(
  label = "context_exposure",
  schedule = null,                        -- オペラント随伴性なし
  phase_annotations = [@context(location="room_B")],
  criterion = FixedSessions(count=3)
)
```

レスポンデント式は依然として付与できる。注釈（`@cs`, `@us`, `@context`）は依然として刺激呈示を記述できる。`null` はオペラント層の不在のみを示すものであり、事象の不在を意味しない。

## 3. `Phase` 要素

```
Phase(
  label = <string>,
  schedule = <ScheduleExpr> | <RespondentExpr> | null,
  phase_annotations = [...],
  phase_param_decls = [...],
  criterion = <Criterion>?         -- 終端フェーズでは不在
)
```

`label` は、JEAB Procedure セクションで用いられる人間可読のフェーズ名である: Acquisition, Extinction, Reversal, Renewal Test, Baseline, Treatment, Probe 等。ラベルは読者のためのメタデータであり、文法の静的検証には参加しない。

`schedule` はオペラント `ScheduleExpr`（例: `VI 60-s`）、レスポンデント式（例: `Pair.ForwardDelay(tone, shock, isi=10-s, cs_duration=15-s)`）、または合成層が許容する合成式でありうる。各フェーズは単一のスケジュール本体を持つ。CER 様の手続き（オペラント・ベースラインとパヴロフ型オーバーレイの組合せ）は、単一フェーズに 2 本のスケジュールを並走させるのではなく、フェーズの並び（ベースライン → ペアリング → テスト）として符号化される。標準的な符号化は `../composed/conditioned-suppression.md` を参照。

`criterion` は非終端フェーズでは必須であり、終端フェーズでは不在である。基準カタログは `criteria.md` を参照。

## 4. 相変化基準の構文

各非終端フェーズは、実験が次フェーズへ移行する方法を指定する。

```
criterion = Stability(window_sessions=5, max_change_pct=10, measure="rate")
criterion = FixedSessions(count=10)
criterion = PerformanceCriterion(measure="rate", threshold=1.0, op="<", window_sessions=3)
criterion = CumulativeReinforcements(count=300)
criterion = ExperimenterJudgment
```

基準は宣言的でありスキーマに列挙される。プログラムは関連する測度をセッションにわたって追跡して基準を評価し、基準が真に解決されたときフェーズを進める。正確な意味論は `criteria.md` を参照。

## 5. JEAB 慣習への注記

1. **共有 → フェーズ別のキーワードによる上書き.** DSL 規約（`phase_annotations` が `shared_annotations` をキーワード単位で上書きする）は JEAB Procedure セクションの読解順序と一致する: まず一般的な Subjects / Apparatus / Procedure、次に各フェーズの固有事項。
2. **定常状態論理がデフォルト.** Sidman (1960) は、相変化は可能な限り固定セッション数ではなく行動自体 — 定常状態の安定性 — に基づくべきだと論じる。したがって JEAB 基礎研究では `Stability` が最も一般的な基準であり、`FixedSessions` は安定性が目標でない消去・プローブ／テスト・フェーズに留保される。
3. **終端フェーズには基準がない.** 実験の終わりは、終端フェーズに到達することで定義され、そのフェーズの基準で定義されるのではない。
4. **注釈カテゴリは JEAB Method 見出しに従う.** DSL の注釈カテゴリ — Subjects, Apparatus, Procedure, Measurement — は共有注釈のデフォルトである。フェーズ別注釈は通常 Procedure を上書きし、時には Measurement も上書きする。Subjects と Apparatus はほぼ常に共有レベルに留まる。

## 6. 既存スキーマとの関係

本仕様の機械可読な権威形式は `schema/experiment/phase-sequence.schema.json` にある。このスキーマは、制約詳細（最小セッション数、測度列挙、演算子列挙）を含む `PhaseSequence`、`Phase`、すべての `Criterion` 変種の正確な JSON 形状を定義する。本ファイルは人間向けの散文対応物であり、概念設計について権威を持つ。スキーマは正確なシリアル化形式について権威を持つ。

## 7. 例 — 単純な反転計画

```
PhaseSequence(
  shared_annotations = [
    @subjects(species="rat", n=8),
    @apparatus(chamber="operant_chamber_1")
  ],
  phases = [
    Phase(
      label = "Baseline",
      schedule = VI 60-s,
      criterion = Stability(window_sessions=5, max_change_pct=10, measure="rate")
    ),
    Phase(
      label = "Reversal_1",
      schedule = VI 120-s,
      criterion = Stability(window_sessions=5, max_change_pct=10, measure="rate")
    ),
    Phase(
      label = "Reversal_2",
      schedule = VI 60-s         -- 終端; 基準なし
    )
  ]
)
```

これは Method セクションの記述「被験体はオペラント・チャンバー 1 で VI 60-s ベースラインで訓練された 8 匹のラットであった。反応が安定した後（連続 5 セッションで 10% 以内）、スケジュールは VI 120-s に変更された。安定後、スケジュールは VI 60-s に戻された」を符号化する。

## 参考文献

- Sidman, M. (1960). *Tactics of scientific research*. Basic Books.
