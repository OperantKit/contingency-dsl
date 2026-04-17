# レスポンデント文法 — 二項随伴性（CS–US）

> contingency-dsl レスポンデント層の一部。二項随伴性（CS–US）のためのレスポンデント固有 EBNF 産出規則、Tier A パヴロフ型プリミティブ（R1〜R14）、およびサードパーティ・パッケージ（主として `contingency-respondent-dsl`）がレスポンデント文法を変更することなく Tier B 手続きを寄与する文法レベル拡張ポイントを定義する。パラダイム中立のメタ文法は `foundations/grammar.md` で定義される。オペラント固有の産出規則は `operant/grammar.md`、プリミティブごとの操作的仕様は `respondent/primitives.md` を参照。

**関連文書:**
- [レスポンデント理論](theory.md) — 形式オブジェクトとしての二項随伴性、Rescorla 随伴性空間、獲得／消去、I/T 比。
- [レスポンデント・プリミティブ](primitives.md) — R1〜R14 の操作的定義、パラメータ意味論、引用。
- [LL(2) 形式的証明](../foundations/ll2-proof.md) — 基盤層の曖昧性のなさの証明。レスポンデント文法は新たな LL(2) 決定点を導入しない。すべての決定点は LL(1) である。

---

## 1. レスポンデント層のスコープ

レスポンデント層は **二項随伴性**（CS–US）を記述する: 条件刺激（CS）と無条件刺激（US）の間の時間的・確率的関係である。スコープは意図的に最小限とされる — 下記の Tier A プリミティブは基盤的なパヴロフ型配置（Pavlov, 1927; Rescorla, 1967, 1968）とそれが必要とする統制手続きをカバーするが、より深いパヴロフ型現象（ブロッキング、影かけ、潜在抑制、更新、再発 等）は §4 の拡張ポイントを介して姉妹パッケージ `contingency-respondent-dsl` に委譲する。

二項随伴性は三項随伴性（SD–R–SR）とは構造的に異なる形式オブジェクトであり、その退化特殊事例ではない。形式的論証は `theory.md §1`、パラダイム中立な型付けは `foundations/contingency-types.md` を参照。

---

## 2. レスポンデント固有の産出規則

`foundations/grammar.md` のパラダイム中立骨格を踏まえ、レスポンデント層は `<expr>` を `<respondent_expr>` に特殊化する。

```bnf
<program>                 ::= <param_decl>* <binding>* <respondent_expr>
<respondent_expr>         ::= <core_respondent_primitive>
                            | <extension_respondent_primitive>

<core_respondent_primitive> ::= <pair_expr>
                              | <extinction_expr>
                              | <cs_only_expr>
                              | <us_only_expr>
                              | <contingency_expr>
                              | <truly_random_expr>
                              | <explicitly_unpaired_expr>
                              | <compound_expr>
                              | <serial_expr>
                              | <iti_expr>
                              | <differential_expr>

<extension_respondent_primitive> ::= <ident_upper> "(" <arg_list>? ")"
                                    -- program-scoped; §4 参照
<ident_upper>             ::= [A-Z][a-zA-Z0-9_]*
```

`<ident_upper>` 形式は Tier A プリミティブ名と非交差である: 拡張プリミティブは、その名前が Tier A プリミティブ名のいずれとも一致しない場合のみ、レスポンデント・レジストリを介してプログラム・スコープで解決される。

### 2.1 Pair プリミティブ（R1〜R4）

```bnf
<pair_expr>               ::= "Pair" "." <pair_mode> "(" <pair_args> ")"
<pair_mode>               ::= "ForwardDelay"
                            | "ForwardTrace"
                            | "Simultaneous"
                            | "Backward"
<pair_args>               ::= <pair_positional> ("," <pair_kw>)*
<pair_positional>         ::= <cs_ref> "," <us_ref>
                            | <us_ref> "," <cs_ref>     -- Backward のみ
<pair_kw>                 ::= "isi" "=" <value>
                            | "cs_duration" "=" <value>
                            | "trace_interval" "=" <value>
<cs_ref>                  ::= <ident> | <string_literal>
<us_ref>                  ::= <ident> | <string_literal>
```

4 つの `Pair.*` モードは `primitives.md` の R1〜R4 に対応する:
- `Pair.ForwardDelay(cs, us, isi, cs_duration)` — CS onset → CS 継続 → US onset。CS と US は時間的に重なる。
- `Pair.ForwardTrace(cs, us, trace_interval)` — CS offset → trace gap → US onset。
- `Pair.Simultaneous(cs, us)` — CS onset = US onset。
- `Pair.Backward(us, cs, isi)` — US onset → US offset → CS onset。US 参照が先に出現し、標準手続きの時間的順序に一致する。

モードごとのキーワード引数の合法性（例: `trace_interval` は `ForwardTrace` でのみ有効）は、文法レベルではなく Phase 2（`foundations/grammar.md §4`）で意味的に強制される。

### 2.2 初等単一刺激プリミティブ（R5〜R7）

```bnf
<extinction_expr>         ::= "Extinction" "(" <cs_ref> ")"
<cs_only_expr>            ::= "CSOnly" "(" <cs_ref> "," "trials" "=" <number> ")"
                            | "CSOnly" "(" <cs_ref> "," <number> ")"
<us_only_expr>            ::= "USOnly" "(" <us_ref> "," "trials" "=" <number> ")"
                            | "USOnly" "(" <us_ref> "," <number> ")"
```

`Extinction(cs)` は獲得履歴 **の後の** CS 単独呈示を表す（Pavlov, 1927; Bouton, 2004）。レスポンデント層は先行履歴を囲う `PhaseSequence` の属性として扱う。フェーズ文脈外の裸の `Extinction(cs)` は、プログラムがデフォルト履歴を割り当てることを選ばない限り、Phase 2 で意味的に不正である。`CSOnly` と `USOnly` はフェーズ非依存プリミティブである: これらは対提示刺激なしの呈示を表し、先行獲得を必要としない（Lubow & Moore, 1959; Randich & LoLordo, 1979）。

### 2.3 随伴性プリミティブ（R8〜R10）

```bnf
<contingency_expr>        ::= "Contingency" "(" <prob> "," <prob> ")"
<truly_random_expr>       ::= "TrulyRandom" "(" <cs_ref> "," <us_ref> ")"
                            | "TrulyRandom" "(" <cs_ref> "," <us_ref> "," "p" "=" <prob> ")"
<explicitly_unpaired_expr> ::= "ExplicitlyUnpaired" "(" <cs_ref> "," <us_ref>
                                ("," "min_separation" "=" <value>)? ")"
<prob>                    ::= <number>     -- 意味論的に 0 ≤ prob ≤ 1 に制約
```

`Contingency(p_us_given_cs, p_us_given_no_cs)` は Rescorla (1967) 随伴性空間上の点をパラメータ化する。第一引数は CS を所与とした US の確率、第二引数は ¬CS を所与とした US の確率である。引数順序（CS 条件付きを先に）は文法レベルで固定されており、順列変更できない。

`TrulyRandom(cs, us)` は随伴性空間の対角線 `Contingency(p, p)` 上の点の構文糖衣である（`theory.md §2`）。`ExplicitlyUnpaired(cs, us, min_separation)` は、US 配置に追加の時間的分離制約を伴う `Contingency(0, p)` に対応する（Ayres, Benedict, & Witcher, 1975）。両者とも、意味論的には `Contingency` の特殊化であるが、意図を構文木に保存するため別個のプリミティブとして保持される。

### 2.4 構造プリミティブ（R11〜R13）

```bnf
<compound_expr>           ::= "Compound" "(" <cs_list> ("," "mode" "=" <compound_mode>)? ")"
<cs_list>                 ::= "[" <cs_ref> ("," <cs_ref>)+ "]"
                            | <cs_ref> ("," <cs_ref>)+
<compound_mode>           ::= "Simultaneous"      -- デフォルト; 他モードは拡張

<serial_expr>             ::= "Serial" "(" <cs_list> "," "isi" "=" <value> ")"

<iti_expr>                ::= "ITI" "(" <iti_distribution> "," "mean" "=" <value> ")"
<iti_distribution>        ::= "fixed" | "uniform" | "exponential"
```

`Compound(cs_list, mode=Simultaneous)` は複数の CS を呈示する。`mode` 引数はデフォルトで `Simultaneous` である。追加モード（例: 非同期 onset 変種）は `contingency-respondent-dsl` の拡張プリミティブに繰り延べられる。

`Serial(cs_list, isi)` は CS を時間順で呈示し、`mode` 引数は受け付けない — 直列性はすでに時間的順序を含意する。

`ITI(distribution, mean)` は構造要素であり、メタデータではない。ジッターは別の関心事であり、`annotations/extensions/respondent-annotator.md` の `@iti` 注釈で扱う。ジッターが無関係な場合、プリミティブ単独で十分である。

### 2.5 分化条件づけ（R14）

```bnf
<differential_expr>       ::= "Differential" "(" <cs_ref> "," <cs_ref> "," <us_ref> ")"
                            | "Differential" "(" <cs_ref> "," <cs_ref> ")"
                               -- 短形式: US は暗黙、囲うフェーズから解決
```

`Differential(cs_positive, cs_negative, us)` は正 CS、負 CS、US を明示的に命名する。短形式 `Differential(cs_positive, cs_negative)` は、囲うフェーズレベルの `@us` 注釈（respondent-annotator）から US を推論する三引数形式への構文糖衣である。囲う `@us` が利用不能な場合、短形式は Phase 2 意味エラーである。

分化条件づけは Tier B から Tier A に昇格された。これは JEAB での頻度と、`Pair.ForwardDelay` + `CSOnly` の合成として符号化された場合にその操作的意図（`CS+` と `CS−` の対比訓練）が透明でないことによる（Pavlov, 1927; Mackintosh, 1974）。

---

## 3. 予約キーワード集合（レスポンデント層）

```bnf
<reserved>      ::= "Pair" | "ForwardDelay" | "ForwardTrace" | "Simultaneous" | "Backward"
                  | "Extinction" | "CSOnly" | "USOnly"
                  | "Contingency" | "TrulyRandom" | "ExplicitlyUnpaired"
                  | "Compound" | "Serial" | "ITI"
                  | "Differential"
                  | "trials" | "isi" | "cs_duration" | "trace_interval"
                  | "mode" | "mean" | "min_separation" | "p"
                  | "fixed" | "uniform" | "exponential"
```

レスポンデント層は `foundations/grammar.md` から `let`, `def`、およびパラダイム中立キーワードを継承する。レスポンデント予約集合はオペラント予約集合（`operant/grammar.md §1.1`）と非交差である: どの識別子も、Tier A レスポンデント・プリミティブとオペラント構成要素を同時に兼ねることはない。この非交差性は、両者を自由に混合する合成層（`composed/*`）の前提条件である。

---

## 4. レスポンデント拡張ポイント

サードパーティ・パッケージは、`<extension_respondent_primitive>` に産出規則を寄与することでレスポンデント層を拡張する。主要消費者は `contingency-respondent-dsl` であり、高次条件づけ、感覚前条件づけ、ブロッキング、影かけ、潜在抑制、条件性抑制、occasion setting、再発、更新、自発回復、対抗条件づけ、過期待、回顧的再評価、条件性味覚嫌悪 等の Tier B プリミティブを定義する。

この拡張ポイントは、オペラント層の Schedule 拡張ポイント（design-philosophy §5.1〜§5.3）と並列であり、同じ 5 つの性質を継承する（design-philosophy §5.4）。

1. **レスポンデント文法は不変のままである.** 拡張は産出規則を追加する。既存 Tier A 規則を書き換えない。
2. **プログラム・スコープの閉鎖性.** 各プログラム（ランタイム／インタプリタ）は自身のレスポンデント・レジストリを保持する。ある拡張をロードしないプログラムは、その構成員を未知トークンとして扱い、パースエラーを発する。
3. **静的検証境界.** Tier A プリミティブは完全に静的検証可能（パラメータ範囲、引数アリティ、CS/US 束縛）である。拡張は自身の検証規則を提供する。
4. **TC 境界の保護.** 拡張はランタイム状態を消費しうる（例: 先行消去相に条件付けされた再発）が、レスポンデント層自身はチューリング完全な構成要素を導入しない。下記 §5 を参照。
5. **等価性判定は拡張の責任.** 2 つの同一拡張構成員の等価性は、拡張モジュールが提供する規則によって判定される。コア等価性規則は Tier A にのみ適用される。

### 4.1 拡張登録規約

拡張プリミティブは以下を満たす場合にのみ認識される:
- 名前が `<ident_upper>` に一致する（先頭大文字）。
- プログラムのレスポンデント・レジストリがその名前を登録済み拡張に解決する。
- プリミティブの引数リストが拡張宣言スキーマに適合する。

文法は解析時に整形された `<ident_upper> "(" <arg_list>? ")"` を許容する。レジストリ解決は Phase 2（解析後）の責任である。これによりレスポンデント構文解析器がプログラム非依存であるという性質が保存される。

### 4.2 注釈層との関係

一部のレスポンデント現象は、拡張プリミティブ（文法への構造的追加）または注釈（Tier A プリミティブに付与されるメタデータ）として表現できる。境界は `annotations/boundary-decision.md §2`（Q1〜Q3）により規定される。
- 現象が **手続きの構造を変える** 場合（例: 高次条件づけのように CS の新しい時間順序を導入する）、レスポンデント拡張ポイントに属する。
- 既存の Tier A 手続きの **属性を注釈するだけ** の場合（例: CS モダリティ、US 強度）、注釈層に属する — 具体的には `annotations/extensions/respondent-annotator.md`。

---

## 5. 静的解析性質

レスポンデント文法は基盤 + オペラント層の計算的性質を保存する。

**命題（CFG）.** レスポンデント文法は文脈自由文法である。上記のすべての産出規則は左辺に最大 1 つの非終端記号を持ち、右辺に終端と非終端の有限列を持つ。どの産出も文脈依存性を導入しない。

**命題（非 TC）.** レスポンデント層はチューリング完全ではない。各 Tier A プリミティブは、パラメータが解析時に決定されるリテラル値である有限で宣言的な手続きを規定する。どのプリミティブも文法レベルでランタイム反復・再帰・状態依存分岐を許容しない。レスポンデント拡張ポイント（§4）は意味的評価でランタイム状態を消費しうるが、拡張機構自体はレスポンデント文法に TC 能力を加えない。

**命題（LL(2) 適合）.** レスポンデント文法は、`foundations/ll2-proof.md` で既に解析された以外の新たな LL(2) 決定点を導入しない。すべての `<respondent_expr>` 代替は先頭トークンで区別可能である（LL(1)）: `Pair`, `Extinction`, `CSOnly`, `USOnly`, `Contingency`, `TrulyRandom`, `ExplicitlyUnpaired`, `Compound`, `Serial`, `ITI`, `Differential`、または上記いずれにも一致しない `<ident_upper>`（拡張）。

これら 3 つの性質は合成層の前提条件である。合成層はレスポンデントとオペラントの式を組み合わせる。いずれかの構成要素が TC であれば、合成層も TC を継承することになり、design-philosophy §2（基盤 + オペラント + レスポンデント + 合成は非 TC であり続ける）に反する。

---

## 6. 例

```
-- Pair プリミティブ
Pair.ForwardDelay(tone, shock, isi=10-s, cs_duration=15-s)
Pair.ForwardTrace(tone, food, trace_interval=5-s)
Pair.Simultaneous(light, airpuff)
Pair.Backward(shock, tone, isi=2-s)

-- 初等プリミティブ
Extinction(tone)
CSOnly(tone, trials=40)
USOnly(shock, trials=20)

-- 随伴性プリミティブ
Contingency(0.9, 0.1)                             -- Rescorla (1967) 正の随伴性
Contingency(0.5, 0.5)                             -- 対角線: truly random
TrulyRandom(tone, shock)                          -- Contingency(p, p) の糖衣
ExplicitlyUnpaired(tone, shock, min_separation=30-s)

-- 構造プリミティブ
Compound([tone, light])                           -- デフォルトは mode=Simultaneous
Compound([tone, light], mode=Simultaneous)        -- 明示
Serial([light, tone], isi=3-s)
ITI(exponential, mean=60-s)

-- 分化条件づけ
Differential(tone_plus, tone_minus, shock)        -- 完全形
Differential(tone_plus, tone_minus)               -- 短形式（US は囲う @us から）
```

---

## 7. エラー回復

レスポンデント固有のエラーコードは `conformance/respondent/errors.json` に記載される。エラー回復方針自身（panic-mode、同期トークン、マルチエラー報告）はパラダイム中立であり、`foundations/grammar.md §7` で規定される。

---

## 参考文献

- Ayres, J. J. B., Benedict, J. O., & Witcher, E. S. (1975). Systematic manipulation of individual events in a truly random control in rats. *Journal of Comparative and Physiological Psychology*, 88(1), 97–103. https://doi.org/10.1037/h0076200
- Bouton, M. E. (2004). Context and behavioral processes in extinction. *Learning & Memory*, 11(5), 485–494. https://doi.org/10.1101/lm.78804
- Ellison, G. D. (1964). Differential salivary conditioning to traces. *Journal of Comparative and Physiological Psychology*, 57(3), 373–380. https://doi.org/10.1037/h0043484
- Lubow, R. E., & Moore, A. U. (1959). Latent inhibition: The effect of nonreinforced pre-exposure to the conditional stimulus. *Journal of Comparative and Physiological Psychology*, 52(4), 415–419. https://doi.org/10.1037/h0046700
- Mackintosh, N. J. (1974). *The psychology of animal learning*. Academic Press.
- Pavlov, I. P. (1927). *Conditioned reflexes: An investigation of the physiological activity of the cerebral cortex* (G. V. Anrep, Trans.). Oxford University Press.
- Randich, A., & LoLordo, V. M. (1979). Associative and nonassociative theories of the UCS preexposure phenomenon. *Psychological Bulletin*, 86(3), 523–548. https://doi.org/10.1037/0033-2909.86.3.523
- Rescorla, R. A. (1967). Pavlovian conditioning and its proper control procedures. *Psychological Review*, 74(1), 71–80. https://doi.org/10.1037/h0024109
- Rescorla, R. A. (1968). Probability of shock in the presence and absence of CS in fear conditioning. *Journal of Comparative and Physiological Psychology*, 66(1), 1–5. https://doi.org/10.1037/h0025984
- Rescorla, R. A. (1972). Informational variables in Pavlovian conditioning. In G. H. Bower (Ed.), *The psychology of learning and motivation* (Vol. 6, pp. 1–46). Academic Press. https://doi.org/10.1016/S0079-7421(08)60383-7
- Rescorla, R. A. (1980). Simultaneous and successive associations in sensory preconditioning. *Journal of Experimental Psychology: Animal Behavior Processes*, 6(3), 207–216. https://doi.org/10.1037/0097-7403.6.3.207
- Rescorla, R. A., & Wagner, A. R. (1972). A theory of Pavlovian conditioning: Variations in the effectiveness of reinforcement and nonreinforcement. In A. H. Black & W. F. Prokasy (Eds.), *Classical conditioning II: Current research and theory* (pp. 64–99). Appleton-Century-Crofts.
- Spetch, M. L., Wilkie, D. M., & Pinel, J. P. J. (1981). Backward conditioning: A reevaluation of the empirical evidence. *Psychological Bulletin*, 89(1), 163–175. https://doi.org/10.1037/0033-2909.89.1.163
