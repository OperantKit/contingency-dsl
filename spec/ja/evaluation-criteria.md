# contingency-dsl 評価基準

> **Status:** Normative (2026-04-14)
>
> 本文書は contingency-dsl の設計判断を評価する軸を定義する。
> [design-philosophy.md](design-philosophy.md) に従属し、
> そこに述べられた設計意図から各軸を導出する。

---

## 1. 目的

設計レビュー、仕様監査、拡張提案には「何をもって良い設計とみなすか」の
共有定義が必要である。明示的な基準がなければ、レビュアーは暗黙の選好に
頼ることになり、評価の再現性が失われる。

本文書は評価軸を固定し、以下を実現する:

- あらゆるレビュアー（人間・自動ツール）が同一の次元で提案を評価できる。
- 軸間のトレードオフが可視的・意図的になる。
- 軸自体が他の spec と同様のプロセス（バージョン管理、根拠の記録）で
  改訂可能である。

## 2. 評価軸

6 つの軸を採用する。各軸は [design-philosophy.md](design-philosophy.md) の
特定の節に根拠を持つ。

| # | 軸 | 定義 | design-philosophy の根拠 | 現在のクレーム |
|---|---|---|---|---|
| 1 | **形式的健全性** | 文法の決定性、型・意味論の well-definedness | §2（Ψ 六層: Foundations + Operant + Respondent 非TC、CFG、決定可能性） | Foundations + Operant + Respondent + Composed に渡って非TC; LL(1)/LL(2) 決定可能 |
| 2 | **言語非依存性** | 単一の spec が言語固有の仮定なしに複数実装を駆動できるか | §6（Python/Rust 並立実装） | 二言語戦略; メタ DSL 構想 |
| 3 | **段階的拡張性** | 新しい次元を追加しても既存の構成素やプログラムが壊れない | §2（Ψ 六層、Operant / Respondent 分離）, §4（program-scoped Annotation、respondent-annotator 拡張を含む）, §5（Schedule Extension + Respondent extension point） | Annotator plugin + Operant.Stateful admission + Schedule Extension + Respondent extension point（Tier B は `contingency-respondent-dsl` に委譲） |
| 4 | **教育的最小性** | 最も単純な有効プログラムが単一トークンで成立する; 複雑性は opt-in | §3.1（全ユーザー共通の記法としての DSL） | `FR 5` が parse/dev mode で完全なプログラム; respondent のみのプログラム（例: `Pair.ForwardDelay(cs, us)`）も単一トークンのプログラム |
| 5 | **研究的厳密性** | 実機・出版要件を黙って省略・取りこぼさない | §1（最上位の目的）, §7.1（近期ゴール） | production / publication validation mode; JEAB operant カバー率を優先; respondent Tier A は Rescorla (1967) contingency space をカバー |
| 6 | **概念境界の明瞭性** | annotation・schedule variant・coordinate change・paradigm（operant vs respondent vs composed）が原理的基準で区別される（ad hoc な慣習ではなく） | §2（Operant / Respondent / Composed 姉妹構造）, §4.3（カテゴリ中立的等価性）, §5.5（Annotation / Schedule Extension / Respondent extension 境界） | 境界テスト + §5.5 判定マトリクス + `composed/` admission 基準 |

## 3. 使い方

### 3.1 設計レビュー

spec 変更や拡張提案をレビューする際、各軸への影響を評価する。
ある軸を改善する代わりに別の軸を犠牲にする提案は、そのトレードオフを
明示しなければならない。

### 3.2 境界判定

新しい概念が Foundations、Operant（Literal / Stateful / TrialBased）、
Respondent、Composed、Schedule Extension、Respondent extension point、
Annotation のいずれに属するかを判定する際、6 軸でどの配置が最も高く
評価されるかを確認する。特に:

- 軸 1, 6 は概念の**所属層**（layer assignment、operant vs respondent
  paradigm の区別を含む）を制約する。
- 軸 3, 4 は**公開方法**（API surface）を制約する。
- 軸 2, 5 は**サポート範囲**（implementation scope）を制約する。

### 3.3 自動監査

仕様監査エージェント（例: adversarial-spec-auditor）は提案のスコアリング時に
これらの軸を参照すべきである。各軸はテスト可能な性質に対応する:

| 軸 | テスト可能な性質 |
|---|---|
| 形式的健全性 | 文法の決定性証明; 型システムの無矛盾性; 曖昧な生成規則の不在; Foundations + Operant + Respondent + Composed に渡って CFG / 非TC 性が成立する |
| 言語非依存性 | spec にホスト言語の型漏洩がない; AST スキーマが自己完結した JSON |
| 段階的拡張性 | annotation モジュール、Schedule Extension、Respondent extension の追加・削除が Foundations / Operant / Respondent 文法の変更を要しない |
| 教育的最小性 | 最短有効プログラムの長さ; 最も単純な例を parse するのに必要な概念の数（respondent のみのプログラムを含む） |
| 研究的厳密性 | JEAB Method 節カテゴリの網羅度; validation mode の完全性; respondent Tier A から Rescorla (1967) contingency space に到達可能 |
| 概念境界の明瞭性 | 各構成素が §5.5 判定マトリクス（Annotation vs Schedule Extension vs Respondent extension）を曖昧さなく通過する; operant / respondent / composed の割り当てが contingency 型（二項 vs 三項 vs 合成）から導出可能 |

## 4. 非目標

- 本文書は **スコアリング公式** や加重指標を定義しない。
  軸は分析の次元であり、採点ルーブリックではない。
- 本文書は **実装優先度** を規定しない。
  優先度は [design-philosophy.md §7](design-philosophy.md) が支配する。
- 本文書の軸は **網羅的ではない**。提案がこれらの軸の外にある懸念
  （例: パフォーマンス、エルゴノミクス）を持ち込む場合、その懸念は
  独自に評価し、反復的に発生するならば本文書への追加として提案すべきである。

---

## 他文書との関係

本文書は [design-philosophy.md](design-philosophy.md) に従属する。
ここで定義された軸が design-philosophy と矛盾する場合、design-philosophy が
優先し、本文書を改訂する。

本文書は以下から参照される:

- spec レビュアー・監査エージェント — 共有評価フレームワークとして。
- 拡張提案 — トレードオフを論証する次元として。
