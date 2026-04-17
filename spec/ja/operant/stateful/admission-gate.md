# Operant.Stateful 承認ゲート

> ポインタ・ファイル。`operant/stateful/` 下位層の承認基準（学問的確立 N1/N2/N3、証拠 E1〜E5）は `spec/en/design-philosophy.md §2.1` で定義されている。本ファイルは、`operant/stateful/` ディレクトリから基準を重複させずに参照可能な入口を提供するために存在する。

---

## 承認基準の所在

承認ゲートの正規ソースは **`spec/en/design-philosophy.md §2.1`** であり、*Operant.Stateful 承認ゲート* と題されている。

この節は以下を規定する。

- Operant 層内の構造的区別（Operant.Literal vs Operant.Stateful）。
- (1) 学問的確立基準 N1/N2/N3、および (2) 宣言的パラメータを要する承認ゲート。
- 学問的確立基準: N1（命名された手続き）、N2（一次文献）、N3（時間的持続性、20 年以上、2 世代以上）。
- 証拠スコア基準（E1 JEAB/JABA 掲載、E2 研究室間再現、E3 教科書掲載、E4 パラメトリック研究もしくは理論的統合、E5 応用／翻訳的使用の 5 軸で 3/5 以上）。
- 4 段階の昇格プロセス（提案 → レビュー → 実装 → 記録）。
- 現行の Operant.Stateful 構成員（Percentile、Adjusting、Interlocking）。

## この下位層の使い方

`operant/stateful/` への新規スケジュールの昇格を提案する場合:

1. `spec/en/design-philosophy.md §2.1` を全文通読する。
2. 4 段階プロセスに従って RFC を準備する。
3. 承認後、既存 3 ファイル（`percentile.md`, `adjusting.md`, `interlocking.md`）のテンプレートに従って、`spec/en/operant/stateful/<name>.md` の下にスケジュール仕様ファイルを追加する。
4. `design-philosophy.md §2.1` の構成員表を更新する。

## このファイルが分離されている理由

各下位層の承認ゲートは、どの単一スケジュールの特徴でもない、共有された横断的ポリシーである。基準を `operant/stateful/*.md` の全ファイルで繰り返すと重複リスクが生じる。単一の権威ある節（`design-philosophy.md §2.1`）に基準を置き、下位層ディレクトリから参照する形とすることで、仕様の DRY が保たれる。
