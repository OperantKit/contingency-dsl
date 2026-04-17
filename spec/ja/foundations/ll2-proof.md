# LL(2) 形式的証明 — contingency-dsl コア文法

> contingency-dsl 基盤層（Ψ）の一部。コア文法の LL(2) 性・非 LL(1) 性・曖昧性のなさを形式的に証明する。

---

## 日本語読者への注記

本ファイルの形式的内容（FIRST₁ / FIRST₂ / FOLLOW₂ 集合、LL(2) 構文解析表、パラダイム保存の証明、Operant Stateful 拡張の LL 分析）は、数学記号・表・形式文法による記述が中心であり、散文的翻訳を行うと記号の同一性が損なわれる恐れがある。したがって、英語版を正規参照とし、本ファイルでは定理の言明と主要節の見取り図のみを日本語化して提供する。完全な証明は [`../en/foundations/ll2-proof.md`](../../en/foundations/ll2-proof.md) を参照せよ。

---

## 1. 定理の言明

**定理.** contingency-dsl コア文法（`schema/operant/grammar.ebnf` で定義）は次の性質を持つ。

1. **LL(2)** — 2 トークン先読みを持つトップダウン予測構文解析器によって決定的に解析可能である。
2. **LL(1) ではない** — 2 トークン先読みを要する決定点が少なくとも 1 箇所存在する。
3. **曖昧性がない** — 任意の有効な入力に対し、構文木はちょうど 1 つ存在する。

**補足（§9）.** 注釈システムは、プログラムレベル注釈について、LL(2)／LL(3) の狭い境界事例を 1 つ導入する。コアのスケジュール文法（注釈を除く）は厳密に LL(2) である。注釈込みでも、標準的な貪欲曖昧性解消の下で LL(2) が成立する。厳密な LL(3) は特定の 1 つのトークン三つ組に適用される。分析は §9 を参照。

**拡張（§10）.** Operant Stateful 層（`schema/operant/stateful/grammar.ebnf` 定義の `Pctl`, `Adj`, `Interlock`）は LL(2) 分類を保存する。新規の決定点はすべて LL(1) であり、既存の決定点を無効化しない。完全な FIRST/FOLLOW 分析は §10 を参照。

## 2〜10. 形式的内容（英語版参照）

以下の各節の完全な内容は、英語版 `../en/foundations/ll2-proof.md` にある。

- §2: トークン語彙（terminal token classes および字句解析器の前提）
- §3: 文法（`schema/operant/grammar.ebnf` に準拠する EBNF）
- §4: FIRST₁ と FIRST₂ の計算
- §5: FOLLOW₂ の計算
- §6: LL(2) 構文解析表の構築
- §7: 曖昧性のなさの証明
- §8: パラダイム保存の証明
- §9: 注釈システムの LL(2)／LL(3) 境界事例分析
- §10: Operant Stateful 拡張（`Pctl`, `Adj`, `Interlock`）の LL 分析

## 参考文献

- Aho, A. V., Lam, M. S., Sethi, R., & Ullman, J. D. (2006). *Compilers: Principles, techniques, and tools* (2nd ed.). Addison-Wesley.
- Parr, T. (2013). *The definitive ANTLR 4 reference* (2nd ed.). Pragmatic Bookshelf.
