# apparatus-annotator — Experimental Apparatus Dimension

## Status: Proposed

## Keywords (Candidates)

| Keyword | Purpose | Example |
|---|---|---|
| @chamber | 実験チャンバーのモデル | `@chamber("med-associates", model="ENV-007")` |
| @operandum | 反応装置（レバー、キー等）の同定 | `@operandum("left_lever", component=1)` |
| @interface | HW インターフェース | `@interface("serial", port="/dev/ttyUSB0")` |
| @hw | ハードウェアバックエンド | `@hw("teensy41")` or `@hw("virtual")` |

**注記:** `@operandum` は 2026-04-12 に stimulus-annotator から apparatus-annotator
へ移管された。操作体（response device）は物理的装置であり、JEAB Method 節の
伝統的区分では Apparatus セクションで記述される。`component=N` のように schedule
成分への割当を示す用法も、apparatus 情報の procedural な適用として自然。
詳細は [spec/annotation-design.md §3.6](../../spec/annotation-design.md) を参照。

## Boundary Justification

**この annotation がないと理論的議論ができないか: NO**

- FI のスキャロップはチャンバーのメーカーに依存しない。
- 装置情報は完全に理論的議論の外にある。

**この annotation が DSL 内にあるべき理由:**

- 異なる装置で同一実験を実行する際の等価性保証。
- experiment-io / contingency-bench のターゲット指定。
- 論文コンパイル時に Apparatus section に直接反映される。

## Inclusion Criteria

- 実験装置の **物理的仕様** に関する宣言。
- HW バックエンド（virtual / serial / HIL）の選択。

## Exclusion Criteria

- 装置の **応答精度**（ms 単位のジッタ）→ contingency-bench の測定対象であり宣言ではない。
- ソフトウェアの設定（ログレベル、出力ディレクトリ）→ DSL の範囲外。

## Open Questions

- @hw("virtual") はシミュレーション用途。apparatus-annotator に属するか、
  それとも実行環境の問題であり annotation ではないか。
- 装置情報はどこまで DSL に取り込むべきか。チャンバー寸法、照度、温度など
  物理環境パラメータは際限なく増える可能性がある。
  → DSL は装置の **同定** (identification) に留め、**仕様** (specification) は
  外部ファイル参照 (`@chamber("ENV-007", spec="chambers/env007.json")`) とすべきか。

## Dependencies

なし。
