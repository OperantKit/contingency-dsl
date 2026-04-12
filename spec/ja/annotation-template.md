# example-annotator — アノテーションテンプレート

## 目的

**DSL プロジェクトの推奨レジストリ**に新しい annotator を提案するためのテンプレート。
このディレクトリをコピーし、各セクションを記入すること。

[design-philosophy.md §4.2](design-philosophy.md) に基づき、サードパーティの
プログラムはこのテンプレートに従わず独自のレジストリを構築できる。
本テンプレートは DSL プロジェクトの推奨セットへの採用を目指す annotator 向けである。

---

## ステータス

`[ Proposed | Schema Design | Stable ]`

---

## カテゴリ

JEAB 準拠の推奨カテゴリのうち、この annotator はどれに属するか。1つ選択:

- [ ] **Procedure** — スケジュール記述、等価性、変換の補完
- [ ] **Subjects** — 被験体の履歴、確立操作、状態
- [ ] **Apparatus** — チャンバー、オペランダム、HW バインディング、タイミング契約
- [ ] **Measurement** — 定常状態、ベースライン、フェーズロジック、従属変数仕様
- [ ] **Extension** — 臨床、派生的、来歴、ドメイン固有
      （新カテゴリの場合は正当化が必要）

---

## キーワード

| キーワード | 目的 | 例 |
|---|---|---|
| @example_key | この annotation が宣言する内容 | `@example_key("value", param=42)` |

---

## 境界の正当化

**この annotation がないと理論的議論ができないか: YES / NO**

- （スケジュールの理論的性質がこの annotation を必要としない理由を説明）

**この annotation が DSL 内にあるべき理由:**

- （DSL 内にあることで何が検証可能・コンパイル可能・再現可能になるか説明）

---

## 包含基準

- この annotator に*属する*もの（1つの次元、明確に記述）

## 除外基準

- ここには*属さない*もの、および代わりにどこに置くべきか

---

## 境界レビューチェックリスト

新しいキーワード `@X` を提案する際に記入すること:

```markdown
### 1. Core independence (§2 境界テスト)
以下は annotation-design.md §2 の Q1-Q3 に対応する。
§2 の記述が正本であり、本チェックリストが食い違った場合は §2 に従う。
- [ ] Q1: `@X` なしで schedule の理論的性質（FI スキャロップ等）を議論できるか → YES なら annotation OK
- [ ] Q2: `@X` は schedule 式の評価意味論を変えるか → NO なら annotation OK
- [ ] Q3: `@X` は Core 文法レベルで必須と主張できるか（registry 非依存で DSL spec 全体で必須と言えるか） → NO なら annotation OK
      (昇格が妥当な場合は design-philosophy §8 の制約下でのみ可)

### 2. カテゴリ適合性
- [ ] `@X` は選択したカテゴリ（Procedure / Subjects / Apparatus / Measurement / 拡張）と整合するか
- [ ] `@X` はこの annotator の次元に属するか
- [ ] `@X` は既存 keywords と意味的に一貫するか
- [ ] 他の推奨 annotator の keywords と衝突しないか

### 3. 推奨の必要性
- [ ] DSL 外（コメント・外部ファイル）では不十分か
- [ ] コンパイル対象（論文・コード生成・検証）に利益があるか
- [ ] 3rd-party 限定ではなく、DSL プロジェクトの推奨集合に含める価値があるか

### 4. ドメイン専門家の承認
- [ ] EAB: 基礎研究の観点から妥当
- [ ] (domain): 関連ドメインの観点から妥当
- [ ] PLT: 言語設計の観点から一貫
```

---

## 依存関係

この annotator が必要とする他の annotator（もしあれば）。なるべく依存なしが望ましい。

---

## 実装リファレンス

実装の所在（例: `apps/experiment/contingency-annotator/src/contingency_annotator/<name>_annotator/`）。

注: サードパーティのプログラムは、リファレンス実装を使用せずに
このスキーマに準拠した独自の annotator を実装できる。
