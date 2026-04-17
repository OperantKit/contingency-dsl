# respondent-annotator — レスポンデント手続きのための注釈拡張

> contingency-dsl 注釈層（Ψ）の一部。レスポンデント・プリミティブおよび合成オペラント × レスポンデント手続きをホストするフェーズにメタデータを付与する 4 つのレスポンデント関連注釈 — `@cs`, `@us`, `@iti`, `@cs_interval` — を文書化する。この拡張は contingency-dsl プロジェクトに同梱されるが、4 つの JEAB 準拠カテゴリ（Subjects / Apparatus / Procedure / Measurement）の外に位置するため `annotations/extensions/` 配下に置かれる。

**関連文書:**
- [注釈設計](../design.md) — 注釈層アーキテクチャとレジストリ意味論。
- [境界決定](../boundary-decision.md) — コア vs 注釈分類のための Q1〜Q3 テスト。
- [スキーマ形式](../schema-format.md) — 注釈スキーマ・メタフォーマット（対応 JSON Schema ファイル用）。
- [テンプレート](../template.md) — 注釈者提案テンプレート。
- [レスポンデント文法](../../respondent/grammar.md) — 下記で参照される Tier A レスポンデント・プリミティブ。
- [レスポンデント・プリミティブ](../../respondent/primitives.md) — 注釈対象プリミティブの操作的定義。

---

## 1. ステータス

**ステータス:** Schema Design（Ψ 再構成の一部として導入）。対応する JSON Schema ファイル `schema/annotations/extensions/respondent-annotator.schema.json` は Phase Ψ-4 スキーマ再構成で作成予定である。それまで、本 Markdown 仕様が設計の権威的記述である。

## 2. カテゴリ

この annotator は **Extension** カテゴリ（`annotations/extensions/`）に属し、4 つの JEAB 準拠カテゴリのいずれにも属さない。レスポンデント固有の刺激およびタイミングのメタデータは、Procedure / Apparatus / Measurement カテゴリを横断する: `@cs` と `@us` は刺激情報を担う（Apparatus と Procedure の間）。`@iti` と `@cs_interval` はタイミング情報を担う（Procedure と Measurement の間）。これら 4 つを単一の Extension annotator 下に置くことで、レスポンデント・メタデータの整合性を保ち、4 つの主要カテゴリに対する 1:1 annotator-カテゴリ対応規則（design-philosophy §4.1）を保存する。

## 3. キーワード

| キーワード | 目的 | 例 |
|---|---|---|
| `@cs` | CS（条件刺激）メタデータ | `@cs(label="tone", duration=10-s, modality="auditory")` |
| `@us` | US（無条件刺激）メタデータ | `@us(label="shock", intensity="0.5mA", delivery="unsignaled")` |
| `@iti` | ジッター付き試行間隔メタデータ | `@iti(distribution="exponential", mean=60-s, jitter=10-s)` |
| `@cs_interval` | CS 呈示時間窓 | `@cs_interval(cs_onset=0-s, cs_offset=10-s)` |

## 4. 注釈ごとの仕様

### 4.1 `@cs(label, duration, modality)`

**付与先.** 任意の `Phase` またはレスポンデント式（`ScheduleExpr` / `RespondentExpr`）に付与可能。`PhaseSequence.shared_annotations` から標準のキーワード上書き規則を通じて継承される。

**パラメータ.**
- `label` — 文字列; レスポンデント・プリミティブで用いられる CS 識別子（例: `"tone"`, `"light"`）。対応する `Pair.*`, `Extinction`, `CSOnly`, `Compound`, `Serial`, `Differential` プリミティブで用いられる `cs` 参照と一致せねばならない。
- `duration` — 値; 名目 CS 持続。`Pair.ForwardDelay` の `cs_duration` 引数が存在する場合はこれを（可読性のため冗長に）再現する。自身で `cs_duration` 引数を持たないレスポンデント・プリミティブでは必須。
- `modality` — 文字列; CS の感覚モダリティ（例: `"auditory"`, `"visual"`, `"olfactory"`, `"tactile"`）。

**境界決定の根拠（`annotations/boundary-decision.md §2` の Q1〜Q3）.**
- Q1（レスポンデント・プリミティブの理論的特性を議論するために必須か）: **No.** レスポンデント・プリミティブの操作的定義（例: `Pair.ForwardDelay`）は CS モダリティの知識を必要としない。時間構造はモダリティから独立である。
- Q2（評価意味論を変えるか）: **No.** `modality` を `"auditory"` から `"visual"` に変えても、構文木や評価結果は変わらない。
- Q3（文法レベルで必須か）: **No.** 異なるプログラムは `modality` を省略する（例: 汎用パーサ）こともあれば、要求する（例: 装置検証パイプライン）こともある。文法はこの選択から独立である。

3 つの答えがすべて **No** であり、境界テストにより `@cs` が注釈候補として確認される。

**Tier A プリミティブとの関係.** `@cs` は `Pair.*`, `Extinction`, `CSOnly`, `Compound`, `Serial`, `Differential` の `cs` パラメータにメタデータを加える。プリミティブがすでに CS 持続パラメータを持つ場合（例: `Pair.ForwardDelay` の `cs_duration`）、`@cs` の `duration` 属性は冗長な可読性補助である。プリミティブが権威ある情報を持つ。

**例.**
```
Phase(
  label = "Acquisition",
  schedule = Pair.ForwardDelay(tone, shock, isi=10-s, cs_duration=10-s)
)
@cs(label="tone", duration=10-s, modality="auditory")
@us(label="shock", intensity="0.5mA", delivery="unsignaled")
```

### 4.2 `@us(label, intensity, delivery)`

**付与先.** 任意の `Phase` またはレスポンデント式に付与可能。標準の上書き規則を通じて継承される。

**パラメータ.**
- `label` — 文字列; 対応するプリミティブで用いられる `us` 参照と一致する US 識別子。
- `intensity` — 文字列または値; US 強度指定（例: `"0.5mA"`, `"45mg_pellet"`, `"3s_access"`）。
- `delivery` — 文字列; US 呈示モード。推奨される列挙: `"unsignaled"`, `"signaled"`, `"response_contingent"`, `"cancelled_on_cs_response"`。列挙は文法で強制されない。プログラムは拡張してよい。

**境界決定の根拠.**
- Q1: No. レスポンデント・プリミティブは文法レベルで US 強度指定から独立に作動する。
- Q2: No. 強度値を変えても構文木構造は変わらない。
- Q3: No. プログラムは `intensity` を必須とするかどうかを決めてよい。

**Tier A プリミティブとの関係.** `@us` は US 参照を保持する任意のレスポンデント・プリミティブ（`Pair.*`, `USOnly`, `Differential`）の `us` パラメータにメタデータを加える。US がオペラント文脈で指定されながらパヴロフ型学習を駆動する合成層手続き（CER, PIT）でも有用である。

**例.**
```
@us(label="shock", intensity="0.5mA", delivery="unsignaled")
```

### 4.3 `@iti(distribution, mean, jitter)`

**付与先.** `Phase` または `PhaseSequence`（共有継承）に付与可能。試行ベースのレスポンデント・ブロックにも付与可能。

**パラメータ.**
- `distribution` — 文字列; `"fixed"`, `"uniform"`, `"exponential"` のいずれか（`ITI` プリミティブの分布ファミリと一致）。
- `mean` — 値; 平均 ITI 持続。
- `jitter` — 値; 平均周りの ITI 変動の範囲または標準偏差。`jitter=0` はジッターなしを意味する。

**`ITI` プリミティブとの区別.** `ITI(distribution, mean)` プリミティブ（レスポンデント R13）は **構造要素** である: これはレスポンデント手続きが試行間隔を含むことを宣言し、その分布を指定する。`@iti(distribution, mean, jitter)` 注釈は **メタデータ** であり、ジッター情報を加え、（可読性のため冗長に）分布と平均を記録する。境界は `boundary-decision.md §2` に従う:

- フェーズに ITI が存在するなら、構造的宣言はプリミティブ（`ITI(...)`）に属する。
- ジッターを記録する必要があるなら、注釈がその追加詳細を担う。
- ジッターが無関係なら、プリミティブ単独で十分である。

**境界決定の根拠.**
- Q1: No. ジッターはプリミティブの操作的定義には参加しない。
- Q2: No. ジッター大きさの変更は構文木を変えない。
- Q3: No. 多くのプログラムはジッター・メタデータを必要としない。

**例.**
```
@iti(distribution="exponential", mean=60-s, jitter=10-s)
```

### 4.4 `@cs_interval(cs_onset, cs_offset)`

**付与先.** `Pair` プリミティブ（`Pair.ForwardDelay`, `Pair.ForwardTrace`, `Pair.Simultaneous`, `Pair.Backward`）およびこれらのプリミティブをホストするフェーズに付与可能。

**パラメータ.**
- `cs_onset` — 値; 試行開始を基準とした CS onset 時刻（通常は `0-s`）。
- `cs_offset` — 値; 試行開始を基準とした CS offset 時刻。

**目的.** 装置検証や自然言語の Method / Procedure セクションへのコンパイル用に、CS 呈示窓を明示化する。`Pair.ForwardDelay(cs, us, isi, cs_duration)` が展開されると、CS 窓は `[0, cs_duration]` である。`@cs_interval` は同じ窓を読者に優しい形で記録する。`Pair.ForwardTrace` では、`@cs_interval` は CS 窓が `cs_offset = cs_duration` で終わり、US 窓が `cs_offset + trace_interval` で始まることを明確化する。

**境界決定の根拠.**
- Q1: No. 時間窓はすでにプリミティブのパラメータに符号化されている。
- Q2: No. `@cs_interval` の追加・削除は構文木構造を変えない。
- Q3: No. すべてのプログラムが読者向けの CS 窓を必要とするわけではない。

**例.**
```
Pair.ForwardDelay(tone, shock, isi=10-s, cs_duration=15-s)
@cs_interval(cs_onset=0-s, cs_offset=15-s)
```

## 5. 階層分類

Phase B の階層分類（`boundary-decision.md §3`）に従う:

| 注釈 | Tier 1（デフォルト／情報的） | Tier 2（製作時必須） | Tier 3（出版時必須） |
|---|---|---|---|
| `@cs` | `duration`, `modality` はしばしばデフォルト | 装置検証が有効なら `label` 必須 | 論文では `label`, `modality` が期待される |
| `@us` | `intensity`, `delivery` はしばしばデフォルト | HW 設定には `intensity` 必須 | 論文では `intensity`, `delivery` が期待される |
| `@iti` | `jitter` はしばしばデフォルト／情報的 | （製作時要件なし） | 論文では `distribution`, `mean`, `jitter` が期待される |
| `@cs_interval` | 情報的 | （製作時要件なし） | （オプション; プリミティブと冗長） |

プログラムは自身のモード（開発／製作／出版）に応じた階層方針を選ぶ。DSL 文法は階層割り当てを強制しない。

## 6. レスポンデント拡張ポイントとの関係

respondent-annotator はレスポンデント拡張ポイント（`respondent/grammar.md §4`）とは **別個** である:

- **レスポンデント拡張ポイント** — 新たなレスポンデント・**プリミティブ** を追加する（構造的文法拡張）。`contingency-respondent-dsl` で Tier B 手続き（ブロッキング、影かけ、更新 等）に用いられる。
- **respondent-annotator**（本ファイル） — 文法を変更せずに既存 Tier A プリミティブに **メタデータ** を加える。

構造的関係を導入する現象（例: 新規配置の直列合成 CS）は、この annotator ではなく拡張ポイントに属する。境界決定テスト（Q1〜Q3）がこの区別を形式化する。

## 7. 対応 JSON Schema

これら 4 つの注釈のための権威スキーマは以下に置かれる:

```
schema/annotations/extensions/respondent-annotator.schema.json
```

このファイルは `annotations/schema-format.md` で定義される注釈スキーマ・メタフォーマットに従う。作成は Phase Ψ-4 スキーマ再構成で予定されている。スキーマ・ファイルが存在するまで、本 Markdown が概念設計について権威を持つ。

## 8. 実働例 — 完全な CER 符号化

```
PhaseSequence(
  shared_annotations = [
    @subjects(species="rat", n=8),
    @apparatus(chamber="operant_chamber_1"),
    @iti(distribution="exponential", mean=120-s, jitter=30-s)
  ],
  phases = [
    Phase(
      label = "Baseline",
      schedule = VI 60-s,
      criterion = Stability(window_sessions=5, max_change_pct=10, measure="rate")
    ),
    Phase(
      label = "CER_Training",
      schedule = VI 60-s,
      phase_annotations = [
        @cs(label="tone", duration=60-s, modality="auditory"),
        @us(label="shock", intensity="0.5mA", delivery="unsignaled"),
        @cs_interval(cs_onset=0-s, cs_offset=60-s)
      ],
      criterion = FixedSessions(count=10)
    )
  ]
)
```

共有 `@iti` は両フェーズに継承される。Baseline フェーズは CS / US メタデータを持たない（必要ないため）。CER_Training フェーズは `@cs`, `@us`, `@cs_interval` を加える。合成手続きは `composed/conditioned-suppression.md` で文書化される。本例は respondent-annotator がそれを補強する方法を示す。
