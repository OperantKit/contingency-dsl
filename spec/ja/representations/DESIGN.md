# contingency-dsl Representations — Design Document

## Status: Draft (2026-04-11)

---

## 1. 方針: 代替座標系としての representation 定義

representation は、3×3 格子型体系（Distribution × Domain）と**同一の行動空間**を
異なるパラメタ化で記述する代替座標系である。

### annotations/ との区別

| 性質 | annotation | representation |
|------|------------|----------------|
| **核心** | 情報を付加する | 表現形式を変える |
| **コアの意味** | 変えない（直交的メタデータ） | 変える（座標変換） |
| **例** | `@reinforcer("pellet")` | `TTau(T=60, tau=30)` |
| **境界テスト §2** | "FI スキャロップの議論に不要" | "FI を T-tau で書き直す" |
| **省略時** | 情報が減る | 座標系がデフォルト（格子）に戻る |

annotation は `FI 10` に情報を**足す**。representation は `FI 10` を `TTau(T=10, τ=10)` に**書き換える**。
後者は評価意味論を変えるため、annotation の境界テスト（DESIGN.md §2 質問 #2）に反する。
よって representation は annotations/ とは独立した設計空間に属する。

### 動機

1. **理論的完全性** — Schoenfeld & Cole (1972) の T-tau、Catania の
   response-rate × reinforcement-rate 空間など、行動分析学には同一現象の
   複数の記述体系が存在する。DSL がこれらを形式的に接続できることは
   理論ツールとしての完全性を高める。
2. **文献横断検索** — T-tau で記述された手続きを格子型に変換し、
   Ferster & Skinner 分類で過去の実験と手続き的類似性を比較できる。
3. **言語非依存性** — 変換規則は DSL レベルで定義し、
   Python / Rust / Kotlin 等の任意のバックエンドで等価に実装できる。

---

## 2. 座標系拡張の境界原則

### 原則: representation は格子型体系との双方向変換を持つ代替パラメタ化である

representation `R` が満たすべき条件:

| # | 条件 | 根拠 |
|---|------|------|
| 1 | `R` は格子型体系と**同一の行動空間**の部分集合を記述する | 無関係な体系は representation ではない |
| 2 | 格子 → R の変換規則が**形式的に定義**されている | 曖昧な対応では変換テストが書けない |
| 3 | R → 格子の逆変換規則が定義されている（partial でもよい） | 双方向性がなければ座標系ではなく射影にすぎない |
| 4 | 変換が**情報を保存するか、保存しない場合は損失を明示する** | 暗黙の情報損失は理論的に不健全 |
| 5 | 変換の定義域（変換可能な Domain）が**型レベルで制約**されている | 不正な変換をコンパイル時に排除する |

### Partial mapping の許容

すべての representation が 3×3 格子の全 9 セルをカバーする必要はない。
T-tau は時間ベースであり、Ratio（応答数ベース）は定義域外となる。
これは欠陥ではなく、体系の正直な境界である。

変換関数が定義域外の入力を受けた場合は、**型エラー**として拒否する。
暗黙の近似変換は行わない（近似は分離された別レイヤーで明示的に提供する）。

---

## 3. 情報損失の分類

格子 → representation の変換で失われうる情報を以下に分類する。

| 損失カテゴリ | 例 | 対処 |
|---|---|---|
| **定義域外** | Ratio → T-tau | 型エラー（変換を拒否） |
| **次元の縮退** | FI ↔ FT が T-tau 上で同一表現 | 逆変換時に `domain` 引数を必須化 |
| **分布情報の縮退** | Variable と Random が T-tau 上で区別不能 | 逆変換時に `distribution` 引数を必須化 |
| **可逆** | FI(30) → TTau(T=30, τ=30) → FI(30) | 情報損失なし |

---

## 4. 近似変換レイヤー

定義域外の変換（例: FR → T-tau）を完全に禁止するのではなく、
**明示的に仮定を宣言する近似変換**を分離レイヤーとして提供する。

```python
# 型エラー（コア変換）
to_ttau(FR(5))  # → RatioScheduleError

# 近似変換（分離レイヤー — 仮定が型に刻まれる）
approximate_ttau(FR(5), irt=2.0)
# → TTauApprox(T=10, tau=10, assumption=IRTAssumption(irt=2.0))
```

近似変換の結果は `TTauApprox` 型であり、`TTauParams` とは区別される。
これにより:
- IRT（inter-response time）は**従属変数**であり、スケジュール定義の一部ではないことが型で明示される
- 近似結果を正確な変換結果と混同するコードはコンパイル時に検出できる

---

## 5. ディレクトリ構造

```
representations/
├── DESIGN.md               # このファイル — 座標系拡張の設計原則
└── t-tau/
    ├── README.md            # T-tau の形式的定義・変換規則
    └── conformance/         # 変換テスト（JSON）
        ├── to_ttau.json     # 格子 → T-tau
        ├── from_ttau.json   # T-tau → 格子
        ├── roundtrip.json   # ラウンドトリップ検証
        └── errors.json      # 定義域外・型エラーのテスト
```

将来、別の座標系（例: response-rate × reinforcement-rate 空間）を追加する場合は、
`representations/<name>/` として同じ構造で追加する。

---

## 6. レビュー機構

新しい representation を追加する場合、以下のレビューを経る:

| Layer | 内容 |
|-------|------|
| 1. 機械的検証 | 変換規則の形式的定義、conformance テスト JSON の存在 |
| 2. 理論的検証 | 行動空間の同一性、情報損失の明示、partial mapping の妥当性 |
| 3. ドメイン専門家 | eab-researcher（基礎理論）、quantitative-choice-theorist（定量的妥当性） |
