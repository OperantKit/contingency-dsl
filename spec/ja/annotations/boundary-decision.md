# 境界判定木

> **Status:** Stable
>
> **Core vs. Annotation の境界テスト** とそれに続く **Tier 分類** の
> 単一情報源（single source of truth）。
> 他の文書（design.md, validation-modes.md, template.md）は判定ロジックを
> 重複記述せず、本ファイルを参照する。

---

## 1. 目的

新しい候補 `@X` が提案されたとき、2 つの判定を順に行う必要がある。

1. **Phase A — Core vs. Annotation**（DSL 仕様レベル、普遍的）
2. **Phase B — Tier 分類**（プログラムレベル、実装ごと）

Phase A はすべての実装に対して権威的である。Phase B は Python 参照実装が
従う規則であり、他のプログラムは design-philosophy §4.2 に従って異なる
Tier 分類を採用してよい。

---

## 2. Phase A — Core vs. Annotation（Q1–Q3）

```
Q1. @X はスケジュールの理論的性質（例: FI スキャロップ）を議論するために
    必要か？
    YES → Core 文法候補。アノテーションではなく Core への追加を検討せよ。
    NO  → Q2

Q2. @X はスケジュール式の評価意味論を変えるか？
    YES → スケジュール変種（Core 文法）。Core への追加を検討せよ。
    NO  → Q3

Q3. @X は Core 文法レベルで必須か — DSL 仕様全体にわたって普遍的に
    要求されるか、いかなるプログラムのレジストリからも独立に？
    YES → Core 文法候補（design-philosophy §8 の破壊的変更制約に従う）。
    NO  → アノテーション候補。Phase B へ進む。
```

### 危険なパターン

```
-- NG: アノテーションが Core 意味論を変える
FI 10 @mode("resetting")     -- これは FI 変種である → Core 文法

-- NG: Core 文法が特定のアノテーションを要求する
FI 10 requires @clock, @operandum    -- 文法にレジストリ依存を焼き込まない

-- OK: Core は独立、アノテーションは付加的
FI 10                        -- 妥当（任意のレジストリで）
FI 10 @clock(unit="s")       -- これも妥当（@clock を認識するレジストリで）
```

### Parse Error に関する注記

`@X` の不在が parse error を生じさせるかは **DSL 仕様レベルでは決定できない**。
これはプログラムのレジストリに依存する（design-philosophy §4.2）。
各プログラムは、自身のレジストリにおいて何が必須で何が任意かを定義する
責任を負う。

---

## 3. Phase B — Tier 分類（T-A–T-C）

前提条件: Phase A において、その要素が **アノテーション候補** と判定された
こと（3 質問すべてに NO/NO/NO で答えた状態）。

```
T-A. @X はデフォルト値を持つパラメータか？（例: @clock の unit はデフォルト "s"）
     YES → Tier 1（デフォルト付き）
     NO  → T-B

T-B. @X は物理ハードウェアが接続されたときに必須か？
     （例: @session_end）
     YES → Tier 2（プロダクションモードで必須）
     NO  → T-C

T-C. @X は出版段階で必須か？（例: @species）
     YES → Tier 3（出版モードで必須）
     NO  → Tier 1（情報的メタデータ）
```

### Tier 一覧

| Tier | 必須となる場面 | 例 |
|---|---|---|
| Tier 0 | 常時（Core 文法） | スケジュール式そのもの |
| Tier 1 | 必須化されない（デフォルト付き、または情報的） | `@clock(unit)`, `@random(seed)` |
| Tier 2 | プロダクションモード（物理 HW 接続時） | `@session_end`, `@response(force)` |
| Tier 3 | 出版モード（論文準備時） | `@species`, `@strain`, `@deprivation` |

---

## 4. 適用例

### 4.1 design.md §8 提案の再分類

| 提案 | Q1 | Q2 | Q3 | Phase A | T-A | T-B | T-C | Tier |
|---|---|---|---|---|---|---|---|---|
| `@session_end` | N | N | N | Annotation | N | Y | — | **Tier 2** |
| `@dependent_measure` | N | N | N | Annotation | N | N | Y | **Tier 3** |
| `@training_volume` | N | N | N | Annotation | N | N | Y | **Tier 3** |
| `@microstructure` | N | N | N | Annotation | N | N | Y | **Tier 3** |
| `@phase_end` | N | N | N | Annotation | N | N | Y | **Tier 3** |
| `@iri_window` | N | N | N | Annotation | N | N | Y | **Tier 3** |
| `@warmup_exclude` | N | N | N | Annotation | Y | — | — | **Tier 1** |
| `@response(force, IRT)` | N | N | N | Annotation | N | Y | — | **Tier 2** |
| `@logging` | N | N | N | Annotation | N | Y | — | **Tier 2** |
| `@clock(unit)` | N | N | N | Annotation | Y | — | — | **Tier 1** |
| `@clock(precision, sampling, sync)` | N | N | N | Annotation | N | Y | — | **Tier 2** |
| `@random(seed)` | N | N | N | Annotation | Y | — | — | **Tier 1** |
| `@timeout` | N | N | N | Annotation | N | Y | — | **Tier 2**（条件付き） |
| `@session_onset` | N | N | N | Annotation | N | Y | — | **Tier 2** |
| `@reinforcer(clock_resume)` | N | N | N | Annotation | N | Y | — | **Tier 2** |
| `@species`, `@strain` | N | N | N | Annotation | N | N | Y | **Tier 3** |
| `@deprivation`, `@history`, `@n` | N | N | N | Annotation | N | N | Y | **Tier 3** |
| `@pretraining` | N | N | N | Annotation | N | N | Y | **Tier 3** |
| `@chamber(model)` | N | N | N | Annotation | N | N | Y | **Tier 3** |
| `@context(houselight)` | N | N | N | Annotation | N | Y | — | **Tier 2** |
| `@drug`, `@preparation` | N | N | N | Annotation | N | N | Y | **Tier 3** |
| `@phase` | N | N | N | Annotation | N | N | Y | **Tier 3**（§5 参照） |
| `@pr_breakpoint` | N | N | N | Annotation | N | Y | — | **Tier 2** |
| `@ioa`, `@ethics`, `@function` | N | N | N | Annotation | N | N | Y | **Tier 3** |

### 4.2 境界テスト・テンプレート（新規提案用）

`@X` を提案する場合、以下を完成させること（[template.md](template.md)
も参照）。

```markdown
## 境界レビュー: @X → <annotator>

### Phase A: Core からの独立性
- [ ] Q1: スケジュールの理論的性質を @X 抜きで議論できるか？
      → YES なら annotation OK
- [ ] Q2: @X はスケジュール式の評価意味論を変えるか？
      → NO なら annotation OK
- [ ] Q3: @X は DSL 仕様全体にわたって普遍的に必須か、レジストリから独立に？
      → NO なら annotation OK

### Phase B: Tier 分類
- [ ] T-A: @X はデフォルト値を持つパラメータか？ → YES → Tier 1
- [ ] T-B: 物理 HW 接続時に必須か？ → YES → Tier 2
- [ ] T-C: 出版時に必須か？ → YES → Tier 3
- [ ] いずれにも該当しない → Tier 1（情報的）
```

---

## 5. 解決済み: `@phase` の分類

`@phase` は **プログラムレベル限定の情報的アノテーション（Tier 3）** である。

### 判定根拠

「同じ FR 1 でも acquisition 期と extinction 期では別の実験となる」という
Q2 への一見の緊張は、よく見れば解消する。**消去は `FR5` に
`@phase("extinction")` を付すことではなく、スケジュール自体を `EXT` に
変更することで表現する。**

```
-- 正: スケジュール自体が変わる
@phase("A1-baseline")       EXT
@phase("B1-treatment")      FR5 @reinforcer("pellet")
@phase("A2-reversal")       EXT
@phase("B2-replication")    FR5 @reinforcer("pellet")
```

`@phase` はスケジュール式の評価意味論を決して変えない（Q2 = NO）。
それは多セッション・データを整理するために実験計画期間にラベルを付ける。
スケジュール式単独で動作中の随伴性を符号化する。

### 境界テスト結果

| Q | 回答 | 理由 |
|---|---|---|
| Q1 | NO | `@phase` 抜きでスケジュール性質を議論できる |
| Q2 | **NO** | 消去は `EXT` であり、`FR5 + @phase("extinction")` ではない。評価意味論を決めるのはスケジュール式であり phase ラベルではない |
| Q3 | NO | 普遍的には要求されない。多くの単相研究には `@phase` が無い |

Phase B: T-A = NO, T-B = NO, T-C = YES → **Tier 3（出版）**。

### 制約

- `@phase` は **プログラムレベル限定** である。スケジュールレベルでの使用は
  `SemanticError: PHASE_ONLY_PROGRAM_LEVEL` となる。
- `@phase` は tier ルール動態のトリガとして機能してよい（例:
  `@phase("extinction")` は `@reinforcer` の Tier 2 要求を免除する）が、
  これはバリデータの問題であり、文法の問題ではない。

---

## 6. §2 原則の保存

中核原則 — 「アノテーションは評価意味論を変えない直交的メタデータである」
— は、tier 分類の導入後も **保存される**。tier システムはこの原則を、
「要求レベルはバリデーションモードに応じて複数段階に分岐する」という
拡張として加える。

- パーサは引き続きアノテーションを任意要素として受理する
- アノテーションの有無はスケジュール式の数学的性質を変えない
- tier 対応バリデータがモードに応じて要求を起動する

---

## 7. 参照

- [design.md](design.md) §2（元の境界テスト、現在は本ファイルへ委譲）
- [validation-modes.md](validation-modes.md) §6.1（元の tier 分類、
  現在は本ファイルへ委譲）
- [design-philosophy.md](../design-philosophy.md) §4.2（プログラムスコープの
  クロージャ）, §8（破壊的変更制約）
- [template.md](template.md)（アノテーション提案テンプレート）
