# 論文と実験 — 複数実験を含む刊行物

> contingency-dsl 実験層の一部。`Experiment` ラッパ（label + body）と、単一刊行物に現れる 1 つ以上の Experiment をまとめる `Paper` ラッパを定義する。本ファイルは人間向けの仕様である。対応する JSON Schema は `schema/experiment/experiment.schema.json` にある。

**関連文書:**
- [実験 / フェーズ列](phase-sequence.md) — 単一実験の内部の多相 body。
- [実験 / 文脈](context.md) — 実験 body 内の一級の文脈。
- [実験 / 基準](criteria.md) — PhaseSequence body で用いる相変化基準。
- [オペラント文法](../operant/grammar.md) — Experiment body に現れるオペラント産出規則。

---

## 1. 根拠

典型的な JEAB 論文は単一の手続きではない。Catania & Reynolds (1968) は 6 実験、Mazur (2005) は 4 実験、Blough (1972) は 4 実験を含む。各実験は独自の Subjects、独自の Apparatus、独自の Procedure を持つ。1 つの実験を記述する注釈は次の実験へ一般化しない。したがって実験層は、論文内部の境界（「Experiment 1」「Experiment 2」等）を一級構成要素へ昇格させる。これにより、プログラムは論文の恣意的な断片ではなく論文全体の内容を表現できる。

`Paper` は `Experiment` ノードの順序付き列である。各 `Experiment` は単一の設計（単一スケジュール実験なら `Program`、多相実験なら `PhaseSequence`）を人間可読な label のもとに包む。注釈は Experiment 境界を越えない。論文全体の被験体記述は文法の一部ではなく、必要な注釈は各 Experiment 内で繰り返して記述する。

## 2. `Experiment` 構成要素

```
Experiment(
  label = <string>,
  body  = <Program> | <PhaseSequence>
)
```

`label` は、原論文で用いられる人間可読な実験識別子である: "Experiment 1"、"Experiment 2a"、"Study 3" 等。label は読者向けメタデータであり、文法の静的検証には関与しない。

`body` は `Program`（単一スケジュール設計、`foundations/grammar.md §2` 参照）または `PhaseSequence`（多相設計、`phase-sequence.md` 参照）のいずれかである。選択は、当該実験の Procedure セクションが単一スケジュールを記述するか、複数の相と遷移基準を記述するかに依存する。body は上位の Paper から注釈を継承しない — 実験が必要とするすべての注釈（Subjects、Apparatus、Procedure、Measurement）は body 内に明示的に現れる必要がある。

## 3. `Paper` 構成要素

```
Paper(
  experiments = [Experiment1, Experiment2, ..., ExperimentN]
)
```

`Paper` は最低 1 つの Experiment を持つ。単一実験の刊行物は、裸の `Program` / `PhaseSequence` として表現してもよいし、1 Experiment の `Paper` として表現してもよい。両者は内容的には等価だが枠組みが異なる。実験 label を報告したり experiments を反復したりするツールは `Paper` 形式を好み、単一手続きのみを実行するツールは裸形式を好む。

`experiments` は順序付きである。この順序は刊行物内部の順序（"Experiment 1" が "Experiment 2" に先行する）を反映し、実行順序ではない。実験が label 順に実施されることも、label が数値的に連続していることも文法は要求しない — "Experiment 1" から "Experiment 3" へ飛ぶ論文もこの層では整形式である（意味論的リンターは警告を出してもよい）。

## 4. 共有注釈と実験別上書き

Paper は `shared_annotations` を持ち、これは各 Experiment に継承される。各 Experiment body も自身の注釈を持ち、キーワード単位で共有注釈を上書きする。継承規則は `PhaseSequence.shared_annotations` 対 フェーズ別注釈と対称である:

- Paper レベルの `@subjects(species="pigeon")` は、自身で `@subjects(...)` を宣言しないすべての Experiment に継承される。
- 自身の `@subjects(...)` を宣言した Experiment は自身の値を用いる。その Experiment でのみ Paper レベルの既定値は使われない。
- Paper レベルに存在しない注釈キーワードを Experiment が追加した場合、その Experiment にのみ追加される。

これは JEAB の慣習を反映する: 論文内のすべての実験が同じ被験体と同じ装置を用いる場合、Method セクションは記述を "General Method" 前置きへまとめることが多い。いずれかの実験が逸脱する場合（別のハト、別のチャンバー等）、その Method セクションは差分のフィールドのみ再宣言する。DSL は同パターンを表現する: 共通部分を Paper レベルで、差分を Experiment レベルで書く。

共通事項が無い場合は `Paper.shared_annotations` を空にし、各 Experiment body が独立に注釈を宣言する。`PhaseSequence` 構成要素が**単一実験内**の注釈共有を担うのに対し、`Paper` 構成要素は同じパターンを**実験をまたぐ**共有へ拡張する。

## 5. 他層との関係

`Paper` と `Experiment` は純粋に実験層のラッパである。新たなオペラント、レスポンデント、合成手続きは導入しない。`Experiment.body` はオペラント層、レスポンデント層、合成層によって解決される。実験層に固有なのは多相協調（`PhaseSequence` 経由）と多実験協調（`Paper` 経由）のみである。

`Paper` 入力を受け取る下流ツールは、典型的には `experiments` を反復し、各 `Experiment.body` を展開して適切な層固有コンパイラへディスパッチする。単一手続きのみを受け取るツールは、最初の Experiment を展開するか、明示的な Experiment 選択子を要求する。

## 6. 既存スキーマとの関係

本仕様の機械可読な正準形は `schema/experiment/experiment.schema.json` にある。同スキーマは `Experiment` と `Paper` の厳密な JSON 形式を定義する（`Paper.experiments` の最小要素数、`Experiment.body` の Program / PhaseSequence 間の one-of ディスパッチ等の制約詳細を含む）。本ファイルは対応する人間向けの散文版であり、概念設計について権威的で、スキーマはシリアライズ形式について権威的である。

## 7. DSL サーフェス構文

文法（`schema/operant/grammar.ebnf`）は 3 つのトップレベル形式を定義する:

```
file            ::= paper | experiment_body | program
paper           ::= program_annotation* experiment_decl+
experiment_decl ::= "experiment" experiment_label ":" experiment_body
experiment_body ::= program_annotation* (phase_decl | progressive_decl | shaping_decl)+
```

`experiment_label` は upper-ident（`Experiment1`）または digit-ident（`1`, `2a`, `3_pilot`）のいずれかを取る。これは JEAB の "Experiment 1"、"Experiment 2a" 等の慣習に一致する。フェーズ label も同じ 2 形式を許容する。

### 7.1 単一実験・単一スケジュール（`program` 形式）

```
@subjects(species="pigeon", n=4)
@apparatus(chamber="operant_chamber_A")

VI 30-s
```

### 7.2 単一実験・多相（`experiment_body` 形式）

```
@subjects(species="rat", n=8)
@apparatus(chamber="operant_chamber_1")

phase Baseline:
  sessions >= 20
  stable(cv, threshold=10%, window=5)
  VI 60-s

phase Reversal_1:
  stable(cv, threshold=10%, window=5)
  VI 120-s

phase Reversal_2:
  VI 60-s
```

### 7.3 複数実験を含む論文（`paper` 形式）

Paper レベル注釈は各 Experiment に継承される。Experiment 内の注釈は、その Experiment のみ Paper レベル注釈を上書きする。

```
@subjects(species="pigeon", n=4)
@apparatus(chamber="chamber_A")

experiment 1:
  VI 30-s

experiment 2:
  phase Baseline:
    stable(cv, threshold=10%, window=5)
    VI 60-s

  phase Extinction:
    sessions = 5
    EXT

  phase Recovery:
    VI 60-s
```

両実験とも Paper レベルの `@subjects(species="pigeon", n=4)` と `@apparatus(chamber="chamber_A")` を継承する。Experiment 1 は単一スケジュール body、Experiment 2 は 3 相 body。Paper レベルの注釈は一度だけ書かれ、各実験で繰り返す必要はない。

### 7.4 実験別上書き

被験体や装置が実験間で異なる場合、該当する実験がその注釈を再宣言する。他の実験は Paper レベルの既定値を使い続ける。

```
@subjects(species="pigeon", n=4)

experiment 1:
  @apparatus(chamber="chamber_A")
  VI 30-s

experiment 2a:
  @subjects(species="pigeon", n=6)    -- Paper レベルの n=4 を上書き
  @apparatus(chamber="chamber_B")
  VI 60-s

experiment 2b:
  @apparatus(chamber="chamber_B")     -- Paper レベルの @subjects を継承
  VI 120-s
```

Experiment 2a は被験体数が異なるため `@subjects` を再宣言する。Experiment 2b は Paper レベルの `@subjects` をそのまま継承する。ここでの実験 label は `"1"`、`"2a"`、`"2b"` — `digit_ident` が許容する数字始まり label である。

### 7.5 単一実験の論文（ラッパ省略）

実験がちょうど 1 つしかない論文は、裸の `experiment_body` 形式と意味論的に等価である。ラッパは省略してよい。以下の 2 つのファイルは等価な AST を生成する（1 つ目は裸の Program、2 つ目は 1 実験の Paper でその body は同じ Program）:

```
-- 裸形式 (program)
@subjects(species="rat", n=8)

VI 60-s
```

```
-- ラッパ形式 (1 実験の paper)
@subjects(species="rat", n=8)

experiment 1:
  VI 60-s
```

実験 label を報告するツールはラッパ形式を好み、単一手続きのみを実行するツールはいずれも受け入れる。

## 参考文献

- Catania, A. C., & Reynolds, G. S. (1968). A quantitative analysis of the responding maintained by interval schedules of reinforcement. *Journal of the Experimental Analysis of Behavior*, 11(3, Pt.2), 327–383. https://doi.org/10.1901/jeab.1968.11-s327
