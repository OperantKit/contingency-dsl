# contingency-dsl 設計根拠

> **ステータス:** 参考情報 (2026-04-14)
>
> 本ドキュメントは、注釈アーキテクチャについて検討した代替案を記録し、
> 現行設計が選ばれた理由を説明するものである。
> [design-philosophy.md](design-philosophy.md) の下位に位置し、
> [evaluation-criteria.md](evaluation-criteria.md) で定義された 6 軸を用いる。
>
> 本ドキュメントは 2026-04-14 に最初に作成され、2026-04-17 に
> §5 (Ψ 再編の根拠) の追補とあわせて再編された。

---

## 1. 目的

[design-philosophy.md](design-philosophy.md) は、この設計が*何であり*
*なぜ重要であるか*を述べる。[evaluation-criteria.md](evaluation-criteria.md)
は、評価のための軸を定義する。本ドキュメントは残された隙間を埋める:
**どの代替案が検討され、それらはどのように比較されたのか?**

却下された代替案を記録することで、設計判断のトレードオフを明示化し、
その設計判断の有効寿命を延ばす。これにより、評価済みの選択肢が
将来の貢献者によって再提案される確率を下げることができる。

---

## 2. 検討した代替案

現行設計 (注釈 + Tier + 表現、プログラムスコープの閉包) と比較して、
5 つの代替アーキテクチャが評価された。

### 2.1 型付き属性 (Typed Attributes)

**参考:** Rust `#[derive(...)]`, Lean 4 attributes.

注釈は、文法に埋め込まれた型付きパラメータとなる。型チェッカが
パース時に注釈値を検証する。

- **長所:** 形式的健全性が最大化される。不正な注釈は静的に検出される。
- **短所:** すべての注釈型を文法が知っている必要があり、漸進的拡張性が
  損なわれる。注釈付きプログラムを読むために型システムの前提知識が
  必要になるため、教育的最小性も低下する。

### 2.2 マニフェスト分離 (Manifest Separation)

**参考:** Kubernetes YAML + Custom Resource Definitions.

DSL を純粋なスケジュール式にのみ還元し、すべてのメタデータは識別子で
リンクされた外部マニフェストファイル (YAML, JSON) に置く。

- **長所:** 言語非依存性が最大化される。DSL はホスト言語の前提を一切
  持ち込まない。
- **短所:** DSL が自己完結性を失う。単一の手続きを理解するのに
  読者が 2 つのファイルを相互参照する必要があり、教育的最小性と
  研究的厳密性 (暗黙情報がもはやインラインでは明示されない) が
  損なわれる。

### 2.3 組込み Python DSL (Embedded Python DSL)

**参考:** Pydantic model declarations, SQLAlchemy declarative base.

注釈を Python のソース中で直接組み立てられる Python オブジェクトとする。
DSL は言語非依存の表記ではなく、Python ライブラリとなる。

- **長所:** 実装コストが最小になる。Python エコシステム全体が利用可能。
- **短所:** 定義上、言語非依存性を放棄する。この表記は Python / Rust /
  Kotlin 実装間で共有される語彙として機能できなくなる。

### 2.4 マクロ展開 (Macro Expansion)

**参考:** Racket `#lang`, Lean elaboration.

スケジュール変種と注釈を、コア構築物へ展開されるマクロとして表現する。
表層構文は文法の変更なしに拡張可能となる。

- **長所:** マクロシステムがよく設計されていれば、形式的健全性と
  漸進的拡張性の双方を高く維持できる。
- **短所:** マクロシステムは本質的に強力であり、Core の non-Turing-complete
  境界を侵犯するリスクがある。展開規則の理解が必要になるため、教育的
  最小性が低下する。

### 2.5 効果システム (Effect System)

**参考:** Koka, OCaml 5 effects.

Tier を代数的効果としてモデル化する。注釈の Tier はその効果シグネチャに
対応し、Tier の合成は効果ハンドラのセマンティクスに従う。

- **長所:** 効果型付けの精密性により研究的厳密性が高まる。Tier 相互作用が
  形式的に扱いやすい。
- **短所:** 効果システムを読むには、実質的な型理論の背景知識が必要となり、
  教育的最小性が著しく制限される。実装コストは Python / Rust いずれに
  おいても高い。

---

## 3. 比較

軸は [evaluation-criteria.md](evaluation-criteria.md) に準拠する。
評価はこの比較の内部で相対的なものであり (軸ごとに値が大きいほど良い)。

| 軸 | Typed attr | Manifest | Embedded DSL | Macro | Effect sys | **現行** |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| 1. 形式的健全性 | ★★★★★ | ★★★ | ★★ | ★★★★★ | ★★★★ | ★★★★ |
| 2. 言語非依存性 | ★★ | ★★★★★ | ★ | ★★ | ★★ | ★★★ |
| 3. 漸進的拡張性 | ★★★ | ★★★★ | ★★★ | ★★★★ | ★★★ | ★★★★ |
| 4. 教育的最小性 | ★★★ | ★★ | ★★★★ | ★★ | ★★ | ★★★★★ |
| 5. 研究的厳密性 | ★★★★ | ★★★★ | ★★★ | ★★★★ | ★★★★★ | ★★★★ |
| 6. 境界明確性 | ★★★★ | ★★★★★ | ★★ | ★★★ | ★★★★ | ★★★★ |
| 実装コスト | High | Medium | Low | High | High | Medium |

---

## 4. 現行設計を選ぶ理由

現行設計は、意図的に中間的な立ち位置をとっている:

1. **教育的最小性 (★5) が最も強い軸である。** DSL はプログラミングの
   バックグラウンドを持たない学生・研究者にも読める共有表記として機能
   しなければならない (design-philosophy §3.1)。これにより、型システム・
   マクロ展開・効果システムの素養を必要とする代替案は即座に失格となる。

2. **漸進的拡張性 (★4) が長期安定性を担保する。** プログラムスコープの
   注釈およびスケジュール拡張レジストリによって、第三者は Core 文法を
   変更することなく DSL を拡張できる (design-philosophy §4.2, §5)。
   型付き属性と効果システムはいずれも、拡張を文法または型システムに
   結合してしまう。

3. **言語非依存性 (★3) は構造的に保証されているが、まだ完全には
   証明されていない。** メタ DSL (`schema-format.md`) と AST スキーマにより、
   仕様が Python 固有でないことは担保されている。完全な証明には
   第二言語の参照実装が必要だが、それは下流の成果物であり DSL 仕様の
   関心事ではない (design-philosophy §6 を参照)。

4. **形式的健全性 (★4) は意図する用途に対して十分である。**
   Core は non-Turing-complete かつ LL(1)/LL(2) で決定可能である。
   完全な ★5 (型付き属性・マクロシステム) を達成するには、利用者が
   検証機構を理解する必要が生じ、教育的最小性と衝突する。

5. **研究的厳密性 (★4) は Tier とモードを通じて達成される。**
   Tier システム (Tier 0-3) と検証モード (parse, dev, production,
   publication) により、必要なときに暗黙の実験的詳細を表面化しつつ、
   カジュアルな利用に負担をかけない仕組みが保証される。

6. **境界明確性 (★4) は原則的な基準によって維持される。**
   注釈 vs 拡張の判断マトリクス (design-philosophy §5.4) が再現可能な
   テストを提供する。マニフェスト分離はこの軸でより高いスコアを取るが、
   自己完結性を失うという代償を伴う。

まとめると、現行設計は **他のすべての軸で十分なスコアを維持しながら、
教育的最小性を最大化する**。どの代替案もこのバランスを達成せず、
それぞれが教育的アクセシビリティを別の軸の強度と引き換えにしている。

---

## 5. Ψ 再編の根拠 (2026-04-17)

本ドキュメントの旧版 (上記 §§1-4) は、DSL が 5 層構造
(Core / Core-Stateful / Core-TrialBased / Schedule Extension /
Annotation) で組織されていた時点での、注釈アーキテクチャ代替案を
評価していた。2026-04-17 にディレクトリ構造は Ψ 6 層アーキテクチャ
(Foundations / Operant / Respondent / Composed / Experiment /
Annotation) へ再編された。設計チェックポイントの記録については
[versioning.md §0](versioning.md) を、正典的な層定義については
[design-philosophy.md §2](design-philosophy.md) を参照。

本節は、当該判断時点で検討された他の 2 つのアーキテクチャを差し置いて
Ψ 構造が選ばれた理由を記録する。

### 5.1 検討した代替案

**Case ρ (却下)** — トップレベルディレクトリに抽象軸を採用:
`core-paradigm/`, `core-execution/`, `core-composition/`,
`core-cross-paradigm/`。各トップレベルディレクトリは、それが扱う
科学的カテゴリとは独立に、抽象的な工学的軸 (パラダイム・実行モード・
合成・パラダイム横断) によって命名されていた。

- **長所:** 形式的に直交している。各軸が変動次元としてきれいに切れる。
- **短所:** 命名が対象読者 (EAB 研究者・学生) にとって抽象的すぎる。
  `core-paradigm/` は、そこにオペラント vs レスポンデントの手続きが
  置かれることを伝えない。`core-execution/` は、そこに
  Percentile / Adjusting / Interlocking / MTS が置かれることを伝えない。
  この命名は、オペラントとレスポンデントに対称な重みを与えてしまうが、
  これは実際のカバレッジ対象を誤って表す。DSL はまず JEAB で報告される
  オペラント手続きを主たる対象とし、レスポンデント手続きは本パッケージ
  では必要最小限の水準のみを扱い、深さは伴侶パッケージに委譲する。

**Case Ω (却下)** — レスポンデントのプリミティブを注釈のみで表現:
レスポンデント層を注釈パッケージ (`@cs`, `@us`, `@pair`, `@contingency`
等) に畳み、スケジュール式または `no_schedule` フェーズに付与する。
第一級のレスポンデント文法は存在しない。

- **長所:** 文法への影響が最小。既存の Core + 注釈で事足りる。
- **短所:** CS-US 随伴性の構造 (Pavlov, 1927; Rescorla, 1967, 1968) は
  **文法レベル**の事象であり、メタデータレベルの事象ではない。
  `ExplicitlyUnpaired` や `Contingency(p_us_given_cs, p_us_given_no_cs)`
  という手続きは、刺激イベント間の構造的関係を定義するものであり、
  その構造を変えることは手続きの記述方法を変えるのではなく、手続きが
  何であるかそのものを変える。これは、スケジュール変種を注釈から
  切り分ける境界テスト (design-philosophy §5.5) と同一のテストである。
  Case Ω はこのテストに失敗する。評価に影響しないことを契約で保証する
  層に、文法的に load-bearing な構築物を置こうとするためである。

**Case Ψ (採用)** — レスポンデントの深さに対する拡張ポイントを備えた
科学的カテゴリ命名: トップレベルディレクトリを、それが扱う科学的
カテゴリ (foundations / operant / respondent / composed / experiment /
annotations) によって命名する。Operant 層が最大の分量を担う。
Respondent 層は意図的に最小限 (Tier A のみ) とし、伴侶パッケージ
`contingency-respondent-dsl` が Tier B のプリミティブを供給する
拡張ポイント (`ExtensionRespondentPrimitive`) を露出する。

- **長所:** ディレクトリ名が対象読者にとって即座に読みやすい。
  オペラント vs レスポンデントの分割は、本分野が自らを組織する方法
  (Skinner, 1938; Pavlov, 1927) に一致する。Composed 層は
  Rescorla & Solomon (1967) の二過程合成を、下位ケースではなく第一級の
  兄弟として形式化する。
- **短所 (受容):** ディレクトリツリーは分量の上で非対称となる
  (operant は重く、respondent は薄い)。この非対称性は意図的であり、
  EAB 中心の重み付けとして design-philosophy §2 に明示的に記録されている。

### 5.2 EAB 中心の重み付け

Ψ の分量配分は、主要なカバレッジ対象を反映する:

- **Operant 層 — 最大の分量。** 6 つのスケジュールファイル
  (`operant/schedules/{ratio,interval,time,differential,compound,progressive}.md`)
  に加えて `operant/stateful/{percentile,adjusting,interlocking}.md`、
  さらに `operant/trial-based/{mts,go-nogo}.md`。これは Ferster & Skinner
  (1957) 以降の JEAB で報告されてきた手続きの分布を反映する。
- **Respondent 層 — 最小限。** Tier A のプリミティブのみ。より深い
  パヴロフ型手続き (blocking, overshadowing, latent inhibition, renewal,
  reinstatement 等) は、Respondent の拡張ポイントを通じて
  `contingency-respondent-dsl` に委譲される。
- **Composed 層 — 限定された初期セット、将来拡張あり。** 5 つの
  初期手続き (conditioned suppression, PIT, autoshaping, omission,
  two-process theory)。追加の合成手続きは `composed/` の受け入れ基準に
  従ってケースバイケースで受け入れる。

### 5.3 科学的根拠

Ψ の層名および区分は一次文献に由来する:

- Skinner, B. F. (1938). *The behavior of organisms*. Appleton-Century. — operant three-term contingency
- Pavlov, I. P. (1927). *Conditioned reflexes: An investigation of the physiological activity of the cerebral cortex* (G. V. Anrep, Trans.). Oxford University Press. — respondent two-term contingency
- Rescorla, R. A. (1967). Pavlovian conditioning and its proper control procedures. *Psychological Review*, 74(1), 71–80. https://doi.org/10.1037/h0024109 — contingency space
- Rescorla, R. A. (1968). Probability of shock in the presence and absence of CS in fear conditioning. *Journal of Comparative and Physiological Psychology*, 66(1), 1–5. https://doi.org/10.1037/h0025984 — contingency parameterization
- Rescorla, R. A., & Solomon, R. L. (1967). Two-process learning theory: Relationships between Pavlovian conditioning and instrumental learning. *Psychological Review*, 74(3), 151–182. https://doi.org/10.1037/h0024475 — composed-layer justification
- Catania, A. C. (2013). *Learning* (5th ed.). Sloan. — unified treatment of contingency relations across operant and respondent

---

## 他ドキュメントとの関係

- [design-philosophy.md](design-philosophy.md) — 正典的な設計意図 (上位)
- [evaluation-criteria.md](evaluation-criteria.md) — §3 で使用した軸の定義
- [architecture.md](architecture.md) — 現行設計の構造的概観
- [versioning.md §0](versioning.md) — 2026-04-17 の Ψ チェックポイントを含む設計変更ログ
