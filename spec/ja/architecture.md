# 計算可能性・表現力・アーキテクチャ境界

> [contingency-dsl 理論文書](theory.md)の一部。4層アーキテクチャ、計算可能性の性質、アノテーションシステムを記述する。

---

## Part IV: 計算可能性・表現力・アーキテクチャ境界

### 4.1 4層アーキテクチャ

強化スケジュールは本質的に**無限過程**を記述する。VI 60 は理論上永遠に走り続けられるし、FR 10 も反応が続く限り強化を提示し続ける。これは欠陥ではなく、行動随伴性の本質的性質である。

4層の責務分離を提案する:

```
┌─────────────────────────┐
│   contingency-dsl       │
│   ┌───────────────────┐ │
│   │ Core              │ │  非チューリング完全（CFG）
│   │ criterion =       │ │  静的、宣言的
│   │   literal_value   │ │  FR 10, Conc(VI 30-s, VI 60-s)
│   ├───────────────────┤ │
│   │ Core-Stateful     │ │  CFG 構文、TC 近傍評価
│   │ criterion =       │ │  パラメータ宣言的、基準はランタイム算出
│   │   f(runtime_state)│ │  Pctl(IRT, 50), Adj(start=FR1, step=2)
│   └───────────────────┘ │
├─────────────────────────┤
│   contingency-core       │  チューリング完全
│   「随伴性がどう          │  動的、手続き的
│    変化するか」           │  if rate > 5.0: switch(VI → VR)
├─────────────────────────┤
│   experiment-core        │  チューリング完全 + 制約
│   「実験として             │  検証、有限化
│    成立させる」           │  Session(sched, exit=Reinf(50))
└─────────────────────────┘
```

| 層 | 計算能力 | 記述対象 | 例 |
|---|---|---|---|
| **contingency-dsl (Core)** | CFG（非TC） | 単一随伴性の静的構造。リテラル基準 | `Conc(VI 30-s, VI 60-s)`, `Chain(FR 5, FI 30-s)` |
| **contingency-dsl (Core-Stateful)** | CFG 構文、TC 近傍評価 | 確立された状態依存基準のスケジュール | `Pctl(IRT, 50)`, `Adj(start=FR 1, step=2)`, `Interlocking(R0=100, T=60s)` |
| **contingency-core** | TC | 随伴性の動的遷移・適応 | 反応率に基づくスケジュール切替、フェーズ遷移 |
| **experiment-core** | TC + 制約 | 実験パラダイムの有限化・検証 | 終了条件、ABA デザイン、安全性制約 |

**contingency-core**（チューリング完全）が可能にするもの:
- 「反応率が閾値を超えたら VR → VI に遷移」
- 「外部条件に基づく適応的 DRO（例: 反応率 < 閾値なら DRO 間隔を増加、そうでなければ 2×step で減少）」
- 「条件分岐を伴う滴定手続き（例: 直近5試行の正答パターンに基づきステップサイズを調整）」
- 「Yoking 手続き（他の被験体の行動に基づき一方のスケジュールパラメータを決定）」

**experiment-core**（TC + 制約）が保証するもの:
- 停止性（セッション終了条件の強制）
- 静的検証（「このスケジュールは ever に強化子を提示するか？」）
- 安全性（強化率の上下限、セッション時間制限）
- 実験デザインの構造的妥当性（ABA デザインの A1-A2 同一性等）

したがって:
- `until` 節は contingency-dsl のスコープ外。ExitConditionConfig は experiment-core に移動すべき
- contingency-dsl の関心事は「随伴性の静的構造」のみ
- 動的遷移・適応は contingency-core の責務
- 有限化・検証は experiment-core の責務

### 4.1.1 操作的境界定義: contingency-dsl vs. contingency-core

上記の4層図では「静的」「動的」を非形式的に用いている。本節では、任意の手続きがどの層に属するかを判定する**操作的定義**（リトマス試験）を与える。

#### 一文要約

> contingency-dsl は「随伴性が**何であるか**」を記述する。contingency-core は「随伴性が**どう別の随伴性に変わるか**」を記述する。

#### スケジュール式不変性（Schedule Expression Invariance, SEI）— 三性質テスト

手続きが contingency-dsl（Core または Core-Stateful）に属するための必要十分条件: 以下の **3性質すべて** を満たすこと。いずれか1つでも違反すれば contingency-core に属する。

**P1 — 式木固定性（Expression Tree Fixity）。** スケジュール式の AST がパース時に完全に決定され、セッション中に構造変化しない。スケジュールノードの集合、型、結合構造が最初の強化サイクルから最後まで同一である。

**P2 — パラメータ列挙可能性（Parameter Enumerability）。** 全てのスケジュールパラメータが (a) パース時に決定されるリテラル値、または (b) 定義自体がリテラルかつパース時に固定された閉形式関数による算出値のいずれかである。パラメータを計算する*ルール*は固定されており、変化するのは*出力値*のみ。

**P3 — 単一スケジュール同一性（Single-Schedule Identity）。** セッション全体を通じて、スケジュールが単一の安定した式で同定可能である。セッション中のいかなる時点においても、元の式木の部分木として存在しない、構造的に異なるスケジュール式への遷移が生じない。

#### 判定フローチャート

```
AST がパース時に完全に決定されるか？（P1）
  NO  → contingency-core
  YES → 全パラメータがリテラル値、またはパース時固定ルールによる算出値か？（P2）
    NO  → contingency-core
    YES → スケジュール同一性が不変か？ — 元の式木の部分木にない
          スケジュールへの遷移がないか？（P3）
      NO  → contingency-core
      YES → 基準値がリテラル値との比較か？
        YES → Core
        NO（実行時計算値との比較） → Core-Stateful
```

#### 比較表

| 性質 | Core | Core-Stateful | contingency-core |
|---|---|---|---|
| AST 構造 | パース時固定 | パース時固定 | セッション中に変化 |
| パラメータ | リテラル値 | リテラル値 | 計算値・切替可能 |
| 基準値 | リテラルとの比較 | f(runtime_state)、ルールはパース時固定 | 任意の状態に依存可能 |
| スケジュール同一性 | 不変 | 不変 | 別スケジュールへ遷移 |
| 計算モデル | CFG（非TC） | CFG 構文, TC 近傍評価 | チューリング完全 |

Core-Stateful と contingency-core の決定的な区別: Core-Stateful ではスケジュール式が**自己完結的**である — 基準の計算ルールが式自体の中で宣言される（例: `Pctl(IRT, 50)` は固定のパーセンタイルルールを宣言）。contingency-core では、システムが**外部条件**（反応率、多試行アウトカムパターン、他の被験体の行動）を評価して、**現在アクティブな**スケジュール式を決定する必要があり、その式は以前のものと構造的に異なりうる。

#### 境界ケースの分類

**ケース 1: 適応的 DRO。**

- *固定ステップ関数による適応*（例: 基準達成ごとに閾値 +1 秒）: `Adj(delay, start=5s, step=1s)` として表現可能。3性質すべてを充足。→ **Core-Stateful。**
- *外部条件に基づく適応*（例: 反応率が X 以下なら閾値を増加、そうでなければ 2×step で減少）: パラメータ計算ルール自体が条件式であり、固定の閉形式関数ではない。P2 違反。→ **contingency-core。**

**ケース 2: 滴定（Titration）。**

- *固定階段法*（例: 正答で +0.1、誤答で −0.1）: `Adj(amount, start=0.4, step=0.1)` として表現可能。Progressive Ratio と構造的に同型 — ルールはパース時に固定、変化するのは現在値のみ。→ **Core-Stateful。**
- *条件分岐型滴定*（例: 直近5試行中3正答なら増加、それ以外は 2×step で減少）: DSL が表現できない制御フローを必要とする。P2 違反。→ **contingency-core。**

**ケース 3: Phase 内スケジュール変更。**

- *固定順序*（例: FR 5 を10回完了後 VI 30）: `Tand(Repeat(10, FR 5), VI 30-s)` として表現可能。遷移先は元の AST 内の部分木として既に存在する。3性質すべてを充足。→ **Core。**
- *行動基準トリガーによる遷移*（例: 反応率が閾値超過で FR 5 → VI 30 に遷移）: AST が外部評価に基づいて構造的に異なるスケジュールに変化する。P1 および P3 違反。→ **contingency-core。**

#### contingency-core の推奨計算モデル: ガード付き遷移システム（Guarded Transition System, GTS）

SEI 定義に基づくと、contingency-core の本質的特徴は「実行時行動状態を条件としたスケジュール式間の遷移」である。これは**ガード付き遷移システム**に自然にマップされる:

```
State      = ScheduleExpr            -- 各状態は contingency-dsl 式
Guard      = BoolExpr(RuntimeState)  -- 行動観測量に対する条件
Transition = (State, Guard, State)   -- ガード充足時に S1 → S2
```

**性質:**

| 性質 | 仕様 |
|---|---|
| 状態 | 各状態は有効な contingency-dsl 式（Core または Core-Stateful） |
| ガード | 定義された実行時観測量（反応率、強化回数、経過時間、累積反応数等）上のブール式 |
| 遷移 | 決定的: 任意の時点で最大1つのガードが真、または優先順位で解決 |
| 初期状態 | 定義の最初の状態 |
| 終端状態 | 出力遷移のない状態（experiment-core が終了するまでこのスケジュールで継続） |
| 合成可能性 | contingency-core プログラムは experiment-core が終了条件で包むための有効な「スケジュール」である |

このモデルは合成可能性を保全する: contingency-dsl 式が*語彙*（随伴性が何であるか）、contingency-core 遷移が*文法*（随伴性がどう変わるか）、experiment-core が*有限化*（全体を有限の実験にする）を提供する。

---

### 4.2 分岐は合成代数に内在する

DSL に「ランタイム条件分岐が欠如している」という主張は正確でない。複合スケジュールの結合子自体が宣言的な分岐機構を提供する:

| 分岐の種類 | 結合子 | 制御主体 |
|-----------|--------|---------|
| 行動選択による分岐 | Conc | 被験体が操作体を選択 |
| リンク完了による遷移 | Chain, Tand | 随伴性の充足が遷移を駆動 |
| 弁別刺激による文脈切替 | Mult, Mix | 環境（実験者/装置）が S^D を提示 |
| 充足条件による選択 | Alt (OR), Conj (AND) | どの成分が先に充足されるか |

命令的プログラミングの `if/else/for` に対応するものが、行動分析学では型付けされた結合子として表現される。これは「非チューリング完全だから分岐できない」のではなく、「分岐が型体系の中に代数的に構造化されている」のである。

### 4.3 Repeat 結合子

「FR 10 を3回完了したら VI 60 に切り替え」は既存の結合子で表現可能:

```
Chain(FR 10, FR 10, FR 10, VI 60-s)  -- 明示的展開
Tand(FR 10, FR 10, FR 10, VI 60-s)   -- S^D 変化なし版
```

`Repeat(n, S)` 結合子は冗長性を削減する:

```
Tand(Repeat(3, FR 10), VI 60-s)
```

**形式的定義:**
```
Repeat(n, S) ≡ Tand(S, S, ..., S)   有限の n ∈ ℕ に対して
                    └── n 個 ──┘
```

Repeat は構文糖衣であり計算能力を増加させない。解析時に有限の Tand に展開される。

**Mix との区別:** `Mix(FR 10, VI 60-s)` は無弁別交替（環境制御、通常ランダム選択）。`Tand(Repeat(3, FR 10), VI 60-s)` は逐次的完了（FR 10 を3回完了してから VI 60 に遷移）。これらは異なる随伴性である。

### 4.4 変数束縛 — マクロ展開としての let

変数束縛はチューリング完全性を追加せずに導入できる:

```
let baseline = VI 60-s
let treatment = Conc(VI 30-s, EXT)
let reversal = baseline
```

これはマクロ展開（テキスト置換）に過ぎない。変更可能な状態、クロージャ、再帰を導入しない。`let` は解析時に除去され、let-free な構文木が残る。

拡張候補（全てマクロ展開に帰着し、以下の整形式条件の下で Chomsky 階層を上げない）:
- パラメータ化テンプレート: `def matching(a, b) = Conc(VI(a), VI(b))` → `matching(30, 90)`
- 注釈: `FR 10 @label("component A")` — 分析・可視化用メタデータ

> **`def` の整形式条件。** G = (V, E) を有向グラフとする。V は `def` 名の集合、(f, g) ∈ E は f の本体が g の呼び出しを含む場合に成立する。G は有向非巡回グラフ（DAG）でなければならない。パーサは G に閉路（自己ループおよび相互再帰を含む）が存在する定義集合を拒否しなければならない（SHALL）。これにより `def` の展開は常に停止し、出力は基底 CFG の範囲内に留まる。

`def` は将来バージョンに延期される（v1.0 BNF には含まれない）。キーワードは識別子の衝突を防ぐために予約されている（§3.2）。

### 4.5 Chomsky 階層上の位置と静的検証

contingency-dsl は**文脈自由文法（CFG）**である:
- 再帰的にネストされた括弧構造を持つが、文脈依存や再帰的関数定義を含まない
- 再帰下降法で O(n) の構文解析が可能
- `let` / `Repeat` は展開後に純粋な CFG となる。`def`（導入時）も DAG 整形式条件（§4.4）の下で同様に純粋な CFG に展開される

**静的に検証可能な性質**（非チューリング完全の利点）:
- 「このスケジュールは ever に強化子を提示するか？」（到達可能性）
- 「全コンポーネントに到達可能か？」（死コード検出）
- 「Concurrent の成分数は2以上か？」（構造的妥当性）
- 「全ての Conc が COD を指定しているか？」（必須パラメータ; Herrnstein, 1961）

これらは構文木の走査で判定可能。チューリング完全な言語では停止問題に還元され、一般に決定不能となる。

### 4.6 制御された拡張ポイント

- **PR のステップ関数:** DSL 内では `hodos` / `linear` / `exponential` の列挙に限定。任意関数は Python API レベルでのみ利用可能。
- **Fleshler-Hoffman 生成:** `seed` パラメータによる決定的生成。実行時のランダム性はランタイムエンジンの責務。
- **DR の閾値:** Core ではスカラー値のみ。固定ステップ関数による適応（例: `Adj(delay, start=5s, step=1s)`）は Core-Stateful に属する。外部条件に基づく調整ルール（行動基準に対する条件分岐）を伴う適応的 DRO のみ contingency-core に委任。操作的境界定義は §4.1.1 を参照。

### 4.7 アノテーションアーキテクチャ — 直交アノテーション次元

基底 DSL はスケジュール式を*スケジュール空間*上の点として定義する: 強化随伴性の構造である。各 annotator はこの空間に**直交する座標軸**（次元）をアノテーションとして追加する。各 annotator は独立した軸を提供し、annotator の合成はそれらの軸のデカルト積を形成する。アノテーションのないスケジュールは基底部分空間に留まる — 完全な後方互換性を持つ。

この設計原則 — *シンプルなコアに次元を加えるアノテーション* — は創造的な合成を可能にする: 単一のスケジュール式が刺激同一性、被験体割り当て、時間パラメータ、臨床メタデータを同時に運搬でき、基底文法への変更は一切不要である。

#### 4.7.1 動機

**多被験体随伴性。** 行動薬理学の協力課題 —「被験体 A のレバー押し → 被験体 B が報酬を得る」— は被験体間の随伴性マッピングを必要とする。基底 DSL は単一の暗黙的被験体を前提とする。

**共有強化子。**「スケジュール A と C は同一の食物ペレットを強化子として使用する」— 強化子の同一性は基底 CFG では表現不可能である。DSL レベルでの強化子同一性は、連合学習理論との仕様レベルでの比較（Rescorla & Wagner, 1972）、型による同一性保証、条件性強化の動学の形式的記述を可能にする。

**時間的文脈。** セッションレベルの時間パラメータ（クロックソース、準備期間）はスケジュール構造と直交するが、スケジュールと並行して宣言可能でなければならない。注: ブラックアウト（BO）は v1.1 でコア文法に昇格し、Mult/Mix の keyword argument となった。BO の持続時間は成分間の行動的独立性に直接影響するため（Reynolds, 1961; Bouton, 2004）。

**臨床メタデータ。** ABA 実践者は機能的行動アセスメントの結果（行動の機能、標的/代替行動ラベル）をスケジュールに注釈する必要があるが、スケジュール文法を汚すべきではない。

#### 4.7.2 Annotator タクソノミー

各 annotator は `-annotator` サフィックスで命名される。意味: *基底 DSL に直交する次元（座標軸）を追加するアノテーションモジュール*。

推奨 annotator 名は JEAB Method 節の見出しと 1:1 で一致する
（[annotation-design.md §3.7](annotation-design.md) 参照）。
2026-04-12 の annotator 再編でこの対応関係が確立された。

| Annotator | JEAB カテゴリ | アノテーションキーワード | 用途 |
|-----------|-------------|----------------------|------|
| `procedure-annotator` | **Procedure** | (sub-annotator 参照) | Procedure 層の情報。stimulus と temporal の 2 sub-annotator に分割 |
| &nbsp;&nbsp;└ `procedure-annotator/stimulus` | Procedure | `@reinforcer`, `@sd`, `@brief` | 刺激同一性: 強化子・弁別刺激・二次スケジュールの brief stimulus |
| &nbsp;&nbsp;└ `procedure-annotator/temporal` | Procedure | `@clock`, `@warmup`, `@algorithm` | セッションレベル時間パラメータ |
| `subjects-annotator` | **Subjects** | `@species`, `@strain`, `@deprivation`, `@history`, `@n` | 被験体条件（2026-04-12 に `subject-annotator` から改名、JEAB 複数形見出しに整合） |
| `apparatus-annotator` | **Apparatus** | `@chamber`, `@operandum`, `@interface`, `@hardware` (alias: `@hw`) | 物理的チャンバー、反応装置、HW インターフェース。`@operandum` は 2026-04-12 に `stimulus-annotator` から移管 |
| `measurement-annotator` | **Measurement** | `@session_end`, `@baseline`, `@steady_state` | セッション終了規則、ベースライン条件、安定性基準 (v1.x minimal set; 2026-04-12 に DIVERGENCE C 解決のため新設) |

**Extensions**（JEAB 4 カテゴリ外、`annotations/extensions/` 配下）:

| Extension | キーワード（候補） | 領域 |
|---|---|---|
| `extensions/social-annotator` | `@subject`, `@ibc` | 多被験体随伴性、協調課題。`@ibc` = Interlocking Behavioral Contingencies (Glenn, 2004) |
| `extensions/clinical-annotator` | `@function`, `@target`, `@replacement` | ABA 臨床メタデータ、FBA 結果 |

**直交性の制約:** 全 annotator のアノテーションキーワードは相互に重複しない。同一スケジュール式に複数 annotator のアノテーションを同時付与可能（デカルト積）:

```
FR 5 @reinforcer("food") @subject("A") @clock("real", unit="s") @function("escape")
```

#### 4.7.3 パッケージアーキテクチャ

全ての annotator は **contingency-annotator** のサブモジュールとして収容される。基底 DSL（`contingency-dsl`）は `AnnotationModule` Protocol のみを定義し、具体的な annotator 実装は持たない。Annotator 名は JEAB Method 節の見出しと 1:1 で対応する（[annotation-design.md §3.7](annotation-design.md) 参照）。

```
contingency-dsl（基底 CFG）
  │  = スケジュール構造（3×3 原子 + 7 結合子 + DR + PR + Repeat + let + aversive）
  │  = contingency-py にのみ依存
  │  = 定義: AnnotationModule Protocol, AnnotatedSchedule, AnnotationRegistry
  │
  └── contingency-annotator（アノテーションパッケージ）
        │  共有型: Reinforcer 階層、AssociativeState、LearningRule、
        │  StimulusManager、OfflineRunner
        │
        ├── procedure_annotator/ （JEAB カテゴリ: Procedure）
        │     │
        │     ├── stimulus/（sub-annotator）
        │     │     + @reinforcer, @sd, @brief 注釈
        │     │     + 強化子同一性、S-S / S-R 連合の形式的記述
        │     │     + 注: @operandum は 2026-04-12 に apparatus_annotator に移管
        │     │
        │     └── temporal/（sub-annotator）
        │           + @clock, @warmup, @algorithm 注釈
        │           + セッションレベルの時間パラメータ宣言
        │           + 注: BO, COD は v1.1 でコア文法に昇格
        │
        ├── subjects_annotator/ （JEAB カテゴリ: Subjects; 2026-04-12 に subject_annotator から改名）
        │     + @species, @strain, @deprivation, @history, @n 注釈
        │
        ├── apparatus_annotator/ （JEAB カテゴリ: Apparatus）
        │     + @chamber, @operandum, @interface, @hardware 注釈
        │     + 物理チャンバー・反応装置・HW インターフェースの同定
        │
        ├── measurement_annotator/ （JEAB カテゴリ: Measurement; 2026-04-12 新設）
        │     + @session_end, @baseline, @steady_state 注釈 (v1.x minimal set)
        │     + セッション終了、ベースライン、安定性基準
        │
        └── extensions/ （JEAB 4 カテゴリ外）
              │
              ├── social_annotator/ （多被験体・協調）
              │     + @subject, @ibc 注釈
              │
              └── clinical_annotator/ （ABA 臨床メタデータ）
                    + @function, @target, @replacement 注釈

social-contingency-sim → contingency-annotator の型を使う側（消費者であり提供者ではない）
experiment-core → contingency-dsl + contingency-annotator を使用
```

**依存グラフ:**
- contingency-py: 他への依存なし
- contingency-dsl: contingency-py に依存; AnnotationModule Protocol を定義
- contingency-annotator: contingency-dsl + contingency-py に依存; annotator を実装
- 消費者（social-contingency-sim, experiment-core 等）: contingency-annotator に依存

#### 4.7.4 AnnotationModule Protocol

annotator の契約は、stimulus-annotator の `LearningRule` / `AssociativeState` と同じ Protocol ベースのパターンに従う:

```python
@runtime_checkable
class AnnotationModule(Protocol):
    """DSL アノテーションモジュールの契約。直交する次元を追加する。"""

    name: ClassVar[str]       # 例: "procedure-annotator", "subjects-annotator"
    version: ClassVar[str]    # semver

    @property
    def annotation_keywords(self) -> FrozenSet[str]:
        """この annotator が導入する予約アノテーションキーワード。
        パーサの予約語集合に追加され、識別子の衝突を防ぐ。"""
        ...

    @property
    def grammar_productions(self) -> str:
        """この annotator が追加する BNF 生成規則。基底文法に追記（置換しない）。
        基底文法の <schedule> と <value> のみ参照可能。"""
        ...

    @property
    def annotation_types(self) -> Mapping[str, type]:
        """アノテーションキーワード → frozen dataclass 型のマッピング。"""
        ...

    def validate(self, annotated_expr: Any) -> Sequence[str]:
        """annotator 固有の意味的検証。診断メッセージのリストを返す。"""
        ...

    @property
    def requires(self) -> FrozenSet[str]:
        """この annotator が依存する他の AnnotationModule の名前。
        例: extensions/social-annotator は procedure-annotator/stimulus の @reinforcer を参照する場合あり。"""
        ...
```

#### 4.7.5 AnnotatedSchedule 型

```python
@dataclass(frozen=True)
class AnnotatedSchedule(Generic[T]):
    """ゼロ個以上のアノテーション次元を持つスケジュール式。

    T は ScheduleExpr（v1.0 ADT）または ScheduleConfig（v0.1 Pydantic）。
    annotations マッピングはデカルト積: expr × dim_1 × ... × dim_n
    各次元は省略可能（不在 = その軸でアノテーションなし）。
    """
    expr: T
    annotations: Mapping[str, Any] = field(default_factory=dict)
    # key = annotator 名 ("procedure-annotator", "subjects-annotator" 等), value = frozen annotation dataclass
```

#### 4.7.6 AnnotationRegistry — 合成規則

```python
@dataclass(frozen=True)
class AnnotationRegistry:
    """有効な annotator を収集し、合成を検証し、文法をマージする。"""

    @staticmethod
    def build(*annotators: AnnotationModule) -> "AnnotationRegistry":
        """レジストリを作成。以下の場合 ValueError:
        - 2つの annotator が同一のアノテーションキーワードを主張（非交差性違反）
        - annotator の requires が未充足（依存性違反）"""
        ...
```

2つの annotator が合成可能 ⟺ `annotation_keywords` が互いに素。`requires` フィールドが依存順序を解決する（例: social-annotator → stimulus-annotator）。パーサは `annotators=registry` をパラメータとして受け取り、未登録のアノテーション名は **そのプログラムの registry において** パースエラーとなる。registry は **program-scoped** であり、異なるプログラムでは同一のアノテーション名が受理される場合と拒否される場合がある。DSL 文法自身はグローバルな closure を強制しない — 詳細は [design-philosophy.md §4.2](design-philosophy.md) および grammar.ebnf §4.7 を参照。

#### 4.7.7 アノテーション BNF

各 annotator はスケジュール式への後置修飾子としてアノテーション生成規則を追加する:

```bnf
-- 共通アノテーション構文（任意の annotator が追加）
<annotated_schedule> ::= <schedule> <annotation>*
<annotation>         ::= "@" <annotation_name> ("(" <annotation_args> ")")?

-- 引数リストは 3 形式をサポート:
--   1. Positional のみ:          @species("rat")
--   2. Positional + keyword:     @chamber("med-associates", model="ENV-007")
--   3. Keyword-only:             @session_end(rule="first", time=60min)
<annotation_args>    ::= <positional_form> | <keyword_only_form>
<positional_form>    ::= <annotation_val> ("," <annotation_kv>)*
<keyword_only_form>  ::= <annotation_kv> ("," <annotation_kv>)*
<annotation_kv>      ::= <ident> "=" <annotation_val>
<annotation_val>     ::= <string_literal> | <number>

-- procedure-annotator/stimulus が追加:
<annotation_name>    ::= "reinforcer" | "sd" | "brief"

-- procedure-annotator/temporal が追加:
<annotation_name>    ::= "clock" | "warmup" | "algorithm"

-- subjects-annotator が追加:
<annotation_name>    ::= "species" | "strain" | "deprivation" | "history" | "n"

-- apparatus-annotator が追加:
<annotation_name>    ::= "chamber" | "operandum" | "interface" | "hw"

-- measurement-annotator が追加:
<annotation_name>    ::= "session_end" | "baseline" | "steady_state"

-- extensions/social-annotator が追加:
<annotation_name>    ::= "subject" | "interlocking"

-- extensions/clinical-annotator が追加:
<annotation_name>    ::= "function" | "target" | "replacement"
```

各 annotator は `<annotation_name>` 生成規則を自身のキーワードで拡張する。基底文法は `<annotation_name>` を定義しない — 少なくとも1つの annotator が有効な場合にのみ存在する。

**構文例:**

```
-- procedure-annotator/stimulus
FR 5 @reinforcer("food-pellet")
Chain(FR 5, FI 30-s) @sd("red-light", component=1)
FR 5(FI 30-s) @brief("light", duration=2)

-- extensions/social-annotator
Conc(VI 30-s, VI 60-s) @subject("A")

-- 合成（複数 annotator）
Conc(
  VI 30-s @subject("A") @reinforcer("food"),
  VI 60-s @subject("B") @reinforcer("water")
)

-- 複数カテゴリの annotator
FR 5 @reinforcer("food") @subject("A") @clock("real", unit="s") @function("escape")
```

#### 4.7.8 命名規則

| 規則 | 形式 | 例 |
|------|------|-----|
| ユーザー向け名 | kebab-case + `-annotator` サフィックス、JEAB カテゴリと一致 | `procedure-annotator`, `subjects-annotator` |
| Sub-annotator（procedure-annotator 内部） | kebab-case、suffix なし | `procedure-annotator/stimulus`, `procedure-annotator/temporal` |
| Python モジュール | `contingency_annotator.<snake>` | `contingency_annotator.procedure_annotator.stimulus` |
| Protocol 実装クラス | PascalCase + `Annotator` | `ProcedureAnnotator` |
| アノテーション dataclass | PascalCase + `Annotation` | `ReinforcerAnnotation` |
| DSL 構文 | `@` プレフィックス + 小文字キーワード | `@reinforcer("food")` |
| Extension annotator | `extensions/` プレフィックス | `extensions/social-annotator` |

#### 4.7.9 設計原則

- **contingency-py は増やさない。** 基底 CFG に対応するランタイム型のみ保持。
- **全てのアノテーションモジュールは contingency-annotator に集約。** DSL アノテーションは型とメタデータであり、シミュレーションロジックではない。`social-contingency-sim` はこれらの型の消費者であり、提供者ではない。
- **基底 CFG は全 annotator の共通言語。** Annotator は基底 CFG に新しい生成規則を**追加**するが、既存の規則を**変更しない**（開放閉鎖原則）。
- **Annotator はデカルト積で合成。** 各 annotator は直交する次元を追加し、独立に、または任意の組み合わせで有効化可能。
- **Protocol ベースの疎結合。** サードパーティの annotator もフレームワークを継承することなく `AnnotationModule` に適合可能（構造的部分型付け）。

#### 4.7.10 三項随伴性のモデル化スコープ

| 要素 | 基底 CFG | procedure/stimulus | procedure/temporal | subjects | apparatus | measurement | ext/social | ext/clinical |
|------|---------|-----|-----|-----|-----|-----|-----|-----|
| S^D（弁別刺激） | Chain/Mult に暗黙的 | `@sd("light")` | — | — | — | — | — | — |
| R（反応） | 操作体として暗黙的 | — | — | — | `@operandum("lever")` | — | — | `@target("hand-flap")` |
| S^R（強化子） | モデル化なし | `@reinforcer` + Reinforcer 型 | — | — | — | — | — | — |
| 被験体 | 単一・暗黙的 | — | — | — | — | — | `@subject("A")` | — |
| S-S / S-R 連合 | モデル化なし | 形式的記述 | — | — | — | — | — | — |
| 被験体間随伴性 | モデル化なし | — | — | — | — | — | interlocking | — |
| 時間ソース / 単位 | モデル化なし | — | `@clock("real")` | — | — | — | — | — |
| ブラックアウト（成分間） | `BO=5-s`（Mult/Mix kw_arg） | — | — | — | — | — | — | — |
| セッション時間構造 | モデル化なし | — | `@warmup` | — | — | — | — | — |
| 被験体種・履歴 | モデル化なし | — | — | `@species`, `@history` | — | — | — | — |
| 物理チャンバー | モデル化なし | — | — | — | `@chamber("ENV-007")` | — | — | — |
| HW バックエンド | モデル化なし | — | — | — | `@hardware("teensy41")` | — | — | — |
| セッション終了 | モデル化なし | — | — | — | — | `@session_end` | — | — |
| 安定性基準 | モデル化なし | — | — | — | — | `@steady_state` | — | — |
| 行動の機能 | モデル化なし | — | — | — | — | — | — | `@function("escape")` |
| 代替行動 | モデル化なし | — | — | — | — | — | — | `@replacement("mand")` |

### 4.8 表現力の境界

| 層 | 計算能力 | 責務 | 表現可能な範囲 |
|---|---|---|---|
| **contingency-dsl** | CFG（非TC） | 随伴性の静的構造（SEI: P1-P3 充足、§4.1.1） | 3×3 原子 + 7 結合子 + DR 修飾子 + PR + Repeat + let 束縛 |
| **contingency-core** | TC | 随伴性の動的遷移（SEI: P1-P3 のいずれか違反、§4.1.1） | DSL 式間のガード付き遷移、条件分岐型 titration/DRO、yoking |
| **experiment-core** | TC + 制約 | 実験の有限化・検証 | 終了条件、ABA デザイン、安全性制約、静的検証 |
| **contingency-py** | ランタイム | 評価エンジン | `is_satisfied()` 判定、状態管理、FH 系列サイクル |

---

