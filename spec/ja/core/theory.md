# 強化スケジュールの代数的型体系

## 概要

本文書は、強化スケジュールの分類体系を代数的型体系として形式化し、contingency-dsl ドメイン固有言語の理論的基盤を提供する。全ての単純強化スケジュールが2つの独立次元 — 分布（Distribution）と領域（Domain）— の直積として表現できることを示し、3×3 の原子スケジュール格子を導出する。7つの結合子（Concurrent, Alternative, Conjunctive, Chained, Tandem, Multiple, Mixed）による合成代数を定義し、可換性・結合性・単位元・零化元を含む代数的性質を形式的に特徴づける。表示的意味論（§2.13）は各スケジュール式を Mealy 機械型のスケジュールマシンに写像し、意味論的等価性についての合成的推論を可能にするとともに、表示的定義と操作的定義を結ぶ形式的妥当性定理を提供する。

形式文法、アーキテクチャ境界、実装橋渡し、代替表現については関連文書を参照:

- [grammar.md](grammar.md) — 文脈自由文法（BNF）、表記の柔軟性、二重 API
- [architecture.md](architecture.md) — 3層アーキテクチャ、計算可能性、拡張システム
- [implementation.md](implementation.md) — Python 型マッピング、Legacy 評価
- [representations.md](representations.md) — 代替座標系（T-tau）

---

## Part I: 原子スケジュールの分類体系 — 積型 Distribution × Domain

### 1.1 2つの独立次元

全ての単純強化スケジュールは、2つの独立次元の直積として表現できる。この知見は Ferster & Skinner（1957）の原典分類に暗黙的に含まれ、OperantKit フレームワークのビットパック `ScheduleType`（Mizutani, 2018）で型レベルに明示化された。

**定義 1（分布: Distribution）.** 値分布次元は、連続する強化サイクルにわたってスケジュールパラメータが*どのように*選択されるかを決定する。

```
Distribution ::= Fixed | Variable | Random
```

- **Fixed（固定）**: パラメータ値は全強化サイクルで一定。決定論的。
- **Variable（変動）**: Fleshler-Hoffman（1962）生成系列からのサンプリング。平均保存・非復元抽出。準ランダムだが統計的性質が制御されている。
- **Random（ランダム）**: 各試行ごとに一様分布から独立にサンプリング。真に確率的・無記憶。

Variable と Random の決定的な違い — 文献でしばしば混同される — は、Variable が事前計算された Fleshler-Hoffman 系列を決定論的にサイクルするのに対し、Random は試行ごとに新しい値を生成する点にある。前者は制約付き分布からの非復元抽出、後者は単純分布からの復元抽出に対応する。

**定義 2（領域: Domain）.** 随伴性領域次元は、スケジュールパラメータが*どの行動次元*に適用されるかを決定する。

```
Domain ::= Ratio | Interval | Time
```

- **Ratio（比率）**: パラメータは反応数を指定。N 回の反応の放出に随伴して強化が提示される。反応依存的。
- **Interval（間隔）**: パラメータは時間の長さを指定。間隔経過*後の*最初の反応に随伴して強化が提示される。反応依存的かつ時間依存的（連言的）。
- **Time（時間）**: パラメータは時間の長さを指定。行動に関わらず時間の経過により強化が提示される。反応非依存的（非随伴的）。

行動的含意: 比率スケジュールは高く安定した反応率と特徴的な強化後休止（PRP）を生成する（Ferster & Skinner, 1957, Ch. 3-4）。間隔スケジュールはスキャロップまたは break-and-run パターンを生み、最低限の閾値を超える反応率には非感受的である（Ferster & Skinner, 1957, Ch. 5-6）。時間スケジュールは迷信的強化（Skinner, 1948）または適切なパラメータ化の下でオペラントスケジュールの近似（Schoenfeld & Cole, 1972）として行動を維持する。FT は反応非依存にもかかわらず正加速的反応パターン（スキャロップ）を産出し（Zeiler, 1968; Herrnstein & Morse, 1957）、VT は FT とは異なる安定的ないし不規則な反応率を産出する（Zeiler, 1968）。反応-強化子非依存化（FT/VT）は従来型消去よりも緩徐な反応減少をもたらす（Lattal, 1972）。

**定義 3（原子スケジュール）.** 原子スケジュールは以下の積型である:

```
AtomicSchedule = Distribution × Domain × Value
```

ここで `Value ∈ ℝ⁺`（Ratio の場合は反応数、Interval/Time の場合は秒）。

これにより **3 × 3 格子** が得られる:

|            | Ratio    | Interval | Time     |
|------------|----------|----------|----------|
| **Fixed**  | FR(*n*)  | FI(*t*)  | FT(*t*)  |
| **Variable** | VR(*n*)  | VI(*t*)  | VT(*t*)  |
| **Random** | RR(*n*)  | RI(*t*)  | RT(*t*)  |

### 1.2 ビットパックエンコーディング

OperantKit フレームワーク（Mizutani, 2018）はこの積型を `UInt64` としてエンコードする。上位 16 ビットに `PrepositionSchedule`（Distribution）、下位 16 ビットに `PostpositionSchedule`（Domain）を配置し、ビットシフトにより各次元を独立に抽出するクエリメソッドを提供する:

```
hasFixedSchedule()    →  (rawValue << 32) >> 48 == Fixed
hasRatioSchedule()    →  (rawValue << 48) >> 48 == Ratio
```

このエンコーディングは型レベルで2次元のクエリ可能性を保持する*タグ付き積*である。Python 実装ではビットパックは不要だが、この次元的独立性は保持しなければならない — enum ペアまたは `.distribution` と `.domain` プロパティを持つ frozen dataclass が同等の機能を提供する。

### 1.3 退化的ケースと境界条件

**EXT（消去）** は OperantKit エンコーディングで `rawValue = 0` を持つ。スケジュール代数の*零元*であり、`EXT.is_satisfied()` は常に `false` を返す。形式的には:

```
EXT = AtomicSchedule(distribution = ⊥, domain = ⊥, value = 0)
```

零エンコーディングは偶然ではなく、消去が強化随伴性の不在 — スケジュール空間の加法単位元 — であることを反映している。

**CRF（連続強化）** は `FR(1)` — 比率スケジュールの*単位元*である。OperantKit のソースは明示的に「FR 1 と結果は同一」と注記している。形式的には:

```
CRF ≡ FR(1) = AtomicSchedule(Fixed, Ratio, 1)
```

CRF は独立した型ではなく名前付き定数である。全ての反応が強化を産出する。比率次元の下限。

### 1.4 非格子スケジュール

特定のスケジュールは異なる行動次元に作用するため、3×3 格子に収まらない。

**分化強化（DR）スケジュール** は反応数や経過時間ではなく、反応間時間（IRT: inter-response time）の時間的性質に基づいて強化を制約する*制約スケジュール*である。

```
DRConstraint ::= DRL(irt_min : ℝ⁺)       -- IRT ≥ 閾値
               | DRH(irt_max : ℝ⁺)       -- IRT ≤ 閾値
               | DRO(omission_time : ℝ⁺)  -- 一定時間反応なし
```

**DRO の名称に関する注記。** DRO は "Differential Reinforcement of Other behavior"（他行動の分化強化）の略称であるが、この名称は歴史的に誤解を招く。成分分析は、DRO の有効性が主に*省略/消去随伴性*に依存し、「他行動」の強化には依存しないことを示している（Mazaleski et al., 1993; Rey et al., 2020; Hronek & Kestner, 2025）。現在の DSL は固定全インターバル DRO を表現する; Lindberg et al. (1999) の 2×2 分類法は v1.x に延期。証拠の詳細は [design-rationale.md §1](../../../docs/ja/design-rationale.md#1-dro-他行動の強化はなぜ誤称か) を参照。

DR スケジュールは格子と直交する位置にあり、格子スケジュールと tandem または conjunctive 合成で組み合わせ可能な**フィルタ**または**修飾子**として理解すべきである。例: `Tand(VR 20, DRL 5-s)` は変動比率の反応要件*かつ* IRT ≥ 5 秒を要求する。

**DRA/DRI に関する注記。** 代替行動の分化強化（DRA）および両立不能行動の分化強化（DRI）は、応用行動分析で広く使用される臨床手続きの名称である（Cooper, Heron, & Heward, 2020）。DRO/DRL/DRH が時間パラメータで定義される単一オペランダムのスケジュール修飾子であるのに対し、DRA/DRI は本質的に*2つの*反応クラスにまたがる随伴性（標的行動の消去 + 代替行動の強化）を記述する。スケジュール水準では、DRA は並立配置として表現可能である:

```
let dra = Conc(EXT, CRF)           -- または Conc(EXT, FR 1), Conc(EXT, VI 30-s) 等
```

DRI は代替行動が標的行動と物理的に両立不能な DRA の特殊ケースであり、スケジュール構造は同一である。両者の差異はトポグラフィー上のもの（どの行動を代替として選択するか）であり、手続き上の差異ではない。したがって DRA/DRI は DSL プリミティブではなく、既存結合子を用いたドキュメント化されたパターンとして扱う。臨床メタデータ（行動機能、代替行動の記述）は注釈拡張レイヤー（§5 参照）に委譲される。

**累進比率（PR）** は*メタスケジュール*である: 提示された強化の数によりインデックスされた決定論的ステップ関数に従ってパラメータが変化する比率スケジュール。

```
PR(step : ℕ → ℕ) = FR(step(n))  ここで n は各強化後にインクリメント
```

PR は*スケジュール関手*であり、ステップ関数を FR スケジュールの系列にマッピングする。DSL は2つの構文形式を提供する:

- **略記形式:** `PR n` — ステップサイズ *n* の算術プログレッション（Jarmolowicz & Lattal, 2010）。`PR 5` は `PR(linear, start=5, increment=5)` に展開され、FR 5, FR 10, FR 15, ... を生成する。*The Behavior Analyst* で提案された表記に一致し、教育・臨床文脈での自然な形式である。
- **明示形式:** `PR(hodos)`, `PR(linear, start=1, increment=5)`, `PR(exponential)`, `PR(geometric, start=1, ratio=2)` — ステップ関数の完全な制御用。数値も括弧もない bare `PR` は ParseError。

算術と幾何プログレッションは質的に異なる反応率関数を産出し、文献にコンセンサスのあるデフォルトは存在しない（Killeen et al., 2009; Stafford & Branch, 1998）。証拠の詳細（breakpoint ≠ Pmax を含む）は [design-rationale.md §2](../../../docs/ja/design-rationale.md#2-累進比率pr-ステップ関数が必須である理由) を参照。

### 1.5 行動理論との対応

2次元型体系は以下の正典的出典に直接マッピングされる:

| 出典 | カバレッジ |
|------|-----------|
| Ferster & Skinner (1957) | FR, VR, FI, VI（第3-6章）; CRF, EXT を境界条件として |
| Catania (2013) | Time を正式な第3ドメインとする 3×3 分類体系の成文化; FT, VT, RT 略称の標準化 |
| Zeiler (1968) | "FT" および "VT" 略称の初出; ハトでの FT スキャロップおよび VT の安定的/不規則パターンの実証 |
| Herrnstein & Morse (1957) | FT 類似手続き（固定間隔での反応非依存的食物提示）の最初期の実験的実証; 正加速 |
| Lattal (1972) | 反応-強化子非依存化（FT/VT）と従来型消去の比較; FT/VT はより緩徐な反応減少を産出 |
| Farmer (1963) | Random スケジュール（RR, RI, RT）の形式化 — 単位あたり等確率仮定 |
| Lachter, Cole, & Schoenfeld (1971) | 不規則間隔での非随伴強化（VT/RT 類似）; RT の最も近い実験的実証 |
| Fleshler & Hoffman (1962) | Variable スケジュールの値生成アルゴリズム |
| Schoenfeld & Cole (1972) | 同一行動空間の代替座標系としての T-tau 体系（[representations.md](representations.md) 参照） |

---

### 1.6 Limited Hold — 時間的利用可能性制約

**Limited Hold（LH）** は、強化機会の *時間的利用可能性* を制限するスケジュールの **修飾語（qualifier）** である。スケジュールが要件を充足した時点で強化窓が開き、`hold_duration` 秒以内に反応が生じれば強化が成立する。窓が期限切れになると強化機会は消失し、スケジュールはリセットされる。

**形式的定義。** スケジュール `S` および `hold_duration h > 0` が与えられたとき:

```
S LH h
```

```
  - t_open  = S が充足された時刻
  - t_resp  = t_open 以降の最初の反応の時刻
  - 強化成立 iff t_resp - t_open ≤ h
  - t_resp - t_open > h ならば: 強化機会消失、S.next() 呼び出し（リセット）
```

**設計ノート: modifier ではなく qualifier。** LH はスケジュールを外側から包む修飾子（modifier）ではなく、スケジュール自体に付与される時間的制約パラメータ（qualifier）として分類する。行動分析の文献では LH は常にスケジュールの属性として記述される（"FI 30-sec LH 10-sec"、"VI 1-min with limited hold"）。スケジュールが文法的・概念的な主語であり、LH はその一側面を制約する。

| 観点 | Qualifier（採用） |
|---|---|
| 記法 | `FI 30 LH 10` — スケジュールが主語 |
| Python API | `FI(30, limitedHold=10)` or `FI(30, LH=10)` |
| 文法 | `<schedule> ::= <base_schedule> ("LH" <value>)?` — 後置節 |
| 概念 | LH はスケジュールパラメータであり、スケジュール変換子ではない |

代数的推論を含め、本仕様では一貫して qualifier 形式 `S LH d` を使用する。

文法はこれを反映している: `<schedule> ::= <base_schedule> ("LH" <value>)?` は LH を後置節として配置し、`<modifier>`（DRL, DRH, DRO が属する）には含めない。DRL/DRH/DRO は内部スケジュールを包んで差異強化基準を課す modifier であるのに対し、LH はスケジュール固有の要件充足後の強化*利用可能性*の失効を修飾する qualifier である。

**状態機械:**

```
WAITING
  → [S.is_satisfied(obs) = True]  → HOLD_OPEN(t_open = obs.current_time)
HOLD_OPEN(t_open)
  → [obs.current_time - t_open ≤ h] → True（強化成立可能）
  → [obs.current_time - t_open > h]  → S.next(); WAITING（消失）
```

`next()` が呼ばれる（強化が実際に成立した）とき: `S.next(); _satisfaction_time = None → WAITING`

**代数的性質:**

- `S LH ∞ ≡ S` — 無限の保持は制約を課さない。§2.2.4 参照。
- `S LH 0 ≡ EXT` — ゼロの保持は強化を利用不可能にする。§2.2.4 参照。
- `LH` は連言（Conj）に還元不可: `Conj` は無状態の同時充足チェックであり、充足イベントにゲートされた状態付き時間窓を表現できない。
- `LH` は T-tau と非同一: T-tau は固定周期クロック駆動、LH は充足イベントトリガー。詳細は [representations.md](representations.md) 参照。
- 代数的には、LH は**合同なスケジュール修飾語**である: `(− LH d) : Schedule → Schedule`（各 `d ∈ ℝ⁺` について）。

**LH の代数的地位の形式的検証.** LH qualifier は `S ↦ S LH d` というスケジュールからスケジュールへの写像を定義する。意味論的等価関係（§2.2.1）に関する代数的性質:

*性質 1（合同性 — 成立）.* LH は意味論的等価を保存する:

```
S₁ ≡ S₂  ⟹  S₁ LH d ≡ S₂ LH d
```

*証明.* S₁ ≡ S₂ ならば、全観察トレースに対して同一の強化帰結列を生成する（定義 4, §2.2.1）。LH qualifier を持たないスケジュールにおいて、充足イベントは強化イベントと一致する。よって S₁ と S₂ は任意のトレースで同一の位置で充足される。LH の状態機械遷移はスケジュールの充足イベントと反応ストリームのみで決定されるため、`S₁ LH d` と `S₂ LH d` は同一の状態遷移を経て同一の帰結を生成する。 ∎

*性質 2（ネストの非可換性 — 合成保存則は不成立）.* 一般に:

```
(S LH d₁) LH d₂ ≢ (S LH d₂) LH d₁
```

*反例.* `(FI 30-s LH 5) LH 10` と `(FI 30-s LH 10) LH 5` を比較する。

`(FI 30-s LH 5) LH 10` では: FI 30 が t₀ で充足 → 最初の反応が t₀ から 5 秒以内に必要（内側 LH）→ 2番目の反応が最初の反応から 10 秒以内に必要（外側 LH）。`(FI 30-s LH 10) LH 5` では: FI 30 が t₀ で充足 → 最初の反応が t₀ から 10 秒以内に必要（内側 LH）→ 2番目の反応が最初の反応から 5 秒以内に必要（外側 LH）。異なる時間的制約を課すため、一方で強化が生じ他方で生じないトレースが存在する。 ∎

*帰結.* LH を「スケジュール代数上の内函子（endofunctor）」とする元の特徴づけは不正確である。LH qualifier は合同性（≡ による前順序圏での恒等射保存関手則に対応）を満たすが、スケジュール上の自然な圏構造での合成保存関手則は満たさない。正確な特徴づけ: **LH は合同なスケジュール修飾語**である — スケジュールをスケジュールに写し、意味論的等価を保存するが、ネストされた LH の適用は順序依存的である。

**ネストされた LH の意味論.** `(S LH d₁) LH d₂` は以下のように解釈される:
1. スケジュール `S` が要件を充足する（時刻 `t₀`）。
2. 内側 LH が `d₁` 秒の窓を開く。反応が `t₁ ∈ [t₀, t₀ + d₁)` で生じなければならない。
3. 外側 LH が `t₁` から `d₂` 秒の窓を開く。2番目の反応が `t₂ ∈ [t₁, t₁ + d₂)` で生じなければ強化は成立しない。

これは実質的に**2回の逐次的反応**を指定の時間窓内で要求する — 逐次（tandem）的な時間的制約である。内側 LH を充足した反応はその層の充足イベントとして消費され、外側 LH の充足には寄与しない。

**適用範囲:**

| 内部スケジュール | 用途 |
|---|---|
| FI, VI | 正典的用法（Ferster & Skinner, 1957, Ch.5） |
| FT, VT | 反応非依存 → 反応依存変換 |
| DRL | 文献に記録あり（Kramer & Rilling, 1970） |
| DRO | 臨床応用（問題行動ゼロ後の反応窓） |
| FR, VR | 意味論的に問題あり（充足反応 = 窓内反応）— v1.0 パーサで警告 |

**参考文献:**
- Ferster, C. B., & Skinner, B. F. (1957). *Schedules of reinforcement*. Appleton-Century-Crofts. (Ch. 5, pp. 153–176: FI + limited hold の手続き的導入と累積記録による実証)
- Catania, A. C. (2013). *Learning* (5th ed.). Sloan Publishing. (用語集 "limited hold" — 操作的定義: スケジュール要件充足後に強化子が利用可能な時間の制限; "availability" の枠組みを確認)
- Lattal, K. A. (1991). Scheduling positive reinforcers. In I. H. Iversen & K. A. Lattal (Eds.), *Experimental analysis of behavior, Part 1* (Techniques in the Behavioral and Neural Sciences, Vol. 6, pp. 87–134). Elsevier. (最も手続き的に明示的な扱い: LH タイマーは要件充足時に開始; 窓の期限切れで強化機会が消失しスケジュールは次のサイクルへ進行)
- Zeiler, M. D. (1977). Schedules of reinforcement: The controlling variables. In W. K. Honig & J. E. R. Staddon (Eds.), *Handbook of operant behavior* (pp. 201–232). Prentice-Hall. (LH が機能的に意味を持つのは要件充足と次の反応の間に時間的ギャップが生じうる場合のみ)
- Kramer, T. J., & Rilling, M. (1970). Differential reinforcement of low rates: A selective critique. *Psychological Bulletin, 74*(4), 225–254. https://doi.org/10.1037/h0029813 (DRL + LH の用例)

#### 1.6.1 LH デフォルト伝播 — 属性文法

プログラムレベルの `LH` パラメータ宣言（`LH = d`）は、適格な葉スケジュールノードに伝播するデフォルト Limited Hold を指定する。本節では、自然言語の記述「全ての leaf base_schedules に適用」を**属性文法**（Aho et al., 2006, §5.2）として形式化し、実装者間の解釈の揺らぎを排除する。

**属性の定義.**

| 属性 | 種別 | 型 | スコープ |
|---|---|---|---|
| `lh_default` | 合成属性 | `Option<(ℝ⁺, Option<TimeUnit>)>` | `Program` ノード |
| `inherited_lh` | 継承属性 | `Option<(ℝ⁺, Option<TimeUnit>)>` | 全 `ScheduleExpr` ノード |
| `effective_lh` | 合成属性 | `Option<(ℝ⁺, Option<TimeUnit>)>` | 葉ノード |

- `lh_default`: `Program.param_decls` から抽出。`LH` 宣言がなければ `⊥`。
- `inherited_lh`: Program ルートから AST を下降するトップダウン属性。
- `effective_lh`: 葉ノードに実際に適用される LH。`≠ ⊥` の場合、意味解析器が `leaf ↦ leaf LH effective_lh` の変換を行う。

**フェーズ順序.** LH 伝播は**意味解析**パスであり、**展開後** AST（let 束縛置換および `Repeat` 脱糖後、警告/リンティング前）に対して動作する。

```
Source → 字句解析 → 構文解析 → [展開前 AST]
  → 束縛展開 / Repeat 脱糖 → [展開後 AST]
  → LH デフォルト伝播（本属性文法）→ [解決済み AST]
  → 警告 / リンティング
```

この順序により、展開前/後のフェーズ曖昧性が解消される: LH 伝播は常に完全に展開された AST に対して動作し、`IdentifierRef` や `Repeat` ノードは残存しない。

**伝播規則.** `⊥` は LH 値の不在（伝播なし）を表す。

```
R1  Program → param_decls bindings schedule
    schedule.inherited_lh = lookup("LH", param_decls)      -- 不在なら ⊥

R2  Compound[C] → C(components[1..n])
    ただし C ∈ {Conc, Alt, Conj, Chain, Tand, Mult, Mix, Interpolate}
    ∀i ∈ [1..n]:
        components[i].inherited_lh = Compound.inherited_lh

R3  Overlay → Overlay(baseline, punisher)
    baseline.inherited_lh  = Overlay.inherited_lh
    punisher.inherited_lh  = ⊥

R4  LimitedHold → inner LH d
    inner.inherited_lh = ⊥

R5  葉ノード: node ∈ {Atomic, Special, Modifier, SecondOrder}
    node.effective_lh = node.inherited_lh
    action: effective_lh ≠ ⊥ ならば node ↦ node LH effective_lh

R6  AversiveSchedule → Sidman(...) | DiscrimAv(...)
    inherited_lh は破棄（ラッピングも伝播もなし）
```

**ノード種別ごとの振る舞い.**

| ノード種別 | 振る舞い | 規則 |
|---|---|---|
| `Compound` (Conc, Alt, Conj, Chain, Tand, Mult, Mix, Interpolate) | `inherited_lh` を各成分に渡す | R2 |
| `Overlay` | ベースラインにのみ渡す; 罰子は `⊥` | R3 |
| `LimitedHold` | 伝播を遮断（明示的 LH がデフォルトに優先） | R4 |
| `Atomic`, `Special`, `Modifier` (DRL, DRH, DRO, PR, Lag) | `inherited_lh ≠ ⊥` なら LH でラップ | R5 |
| `SecondOrder` | ノード全体をラップ; unit は個別に伝播しない | R5 |
| `AversiveSchedule` (Sidman, DiscrimAv) | `inherited_lh` を破棄 | R6 |

**主要な設計判断の根拠.**

*R3 — Overlay 罰子の隔離.* プログラムレベル LH は強化の利用可能性を制約する。`Overlay` の罰子は別の帰結クラス（嫌悪刺激）で動作するため、強化の利用可能性窓を罰スケジュールに伝播させることは手続き的に非整合である。

*R4 — 明示的 LH がデフォルトに優先.* 式レベル COD がプログラムレベル COD に優先するのと同様のオーバーライド意味論（§2.4）。明示的 LH は意図した時間的制約を既に提供しており、デフォルトをさらに伝播すると意図しない二重ゲーティングが生じる。

*R5 — SecondOrder を葉として扱う.* 二次スケジュール（例: `FR5(FI30)`）の unit スケジュールは派生的反応単位を定義する（Kelleher, 1966）。セッションレベル LH は全体の強化配達を制約するものであり、各 unit の内部的時間的力学を制約するものではない。LH を unit 位置に伝播すると手続きが根本的に変わる — 特に行動薬理学では、unit スケジュールの独立した動作が実験変数であることが多い（Goldberg & Kelleher, 1977）。SecondOrder 全体をラップすることで、意図された意味論が保存される: 「二次スケジュールの配置が強化機会を生成した後、*d* 秒以内に収集する必要がある」。

*R6 — 嫌悪スケジュールの隔離.* Sidman 回避と弁別回避には専用の時間的パラメータ（SSI/RSI, CSUSInterval）がある。LH は*強化の利用可能性*を制約する; これらのスケジュールは手続き的に異なるタイムラインで*嫌悪帰結*を配達する（Sidman, 1953）。

**具体例.**

*例 1 — Conc を通じた基本伝播.*
```
入力:     LH = 10s
          Conc(VI 30s, VI 60s)
解決後:   Conc(VI 30s LH 10s, VI 60s LH 10s)
```
トレース: R1 → R2 (×2) → R5 (×2, ラップ).

*例 2 — 式レベルのオーバーライド.*
```
入力:     LH = 10s
          Conc(FR 5, VI 60s LH 20s)
解決後:   Conc(FR 5 LH 10s, VI 60s LH 20s)
```
トレース: R1 → R2 (×2). `FR 5`: R5 (修飾, + `VACUOUS_LH_RATIO` 警告). `VI 60s LH 20s`: R4 (伝播遮断); 明示的 LH 20s が保持。

*例 3 — SecondOrder unit の隔離.*
```
入力:     LH = 10s
          FR 5(FI 30s)
解決後:   FR 5(FI 30s) LH 10s
```
トレース: R1 → R5 (SecondOrder を葉として扱い、ラップ). unit `FI 30s` は不変; LH 窓は 5 回目の unit 完了後に被験体が強化を収集できる時間を制約する。

*例 4 — 入れ子の複合スケジュール.*
```
入力:     LH = 10s
          Conc(Chain(FR 5, FI 30s), VI 60s)
解決後:   Conc(Chain(FR 5 LH 10s, FI 30s LH 10s), VI 60s LH 10s)
```
トレース: R1 → R2 → R2 (Chain 内部) → R5 (×3, ラップ). 各葉が独立にデフォルトを受け取る。

*例 5 — 嫌悪スケジュールの隔離.*
```
入力:     LH = 10s
          Sidman(SSI=20s, RSI=5s)
解決後:   Sidman(SSI=20s, RSI=5s)
```
トレース: R1 → R6 (`inherited_lh` 破棄).

*例 6 — LH param_decl なし（恒等）.*
```
入力:     Conc(VI 30s, VI 60s)
解決後:   Conc(VI 30s, VI 60s)
```
トレース: R1 (`lh_default = ⊥`). 伝播は生じない。

**適合テストスイート.** `conformance/core/lh_propagation.json` が全伝播規則のテストベクトルを提供する。各テストはパーサ出力（`expected`, 伝播前）と解決済み AST（`resolved`, 伝播後）の両方を指定する。

**参考文献.**
- Aho, A. V., Lam, M. S., Sethi, R., & Ullman, J. D. (2006). *Compilers: Principles, Techniques, and Tools* (2nd ed.). Addison-Wesley. (§5.2: Inherited Attributes)
- Goldberg, S. R., & Kelleher, R. T. (1977). Reinforcement of behavior by cocaine injections. In E. H. Ellinwood & M. M. Kilbey (Eds.), *Cocaine and other stimulants* (pp. 523–544). Plenum Press.
- Kelleher, R. T. (1966). Conditioned reinforcement in second-order schedules. *Journal of the Experimental Analysis of Behavior*, *9*(5), 475–485. https://doi.org/10.1901/jeab.1966.9-475
- Sidman, M. (1953). Two temporal parameters of the maintenance of avoidance behavior by the white rat. *Journal of Comparative and Physiological Psychology*, *46*(4), 253–261. https://doi.org/10.1037/h0060730


---

## Part II: 合成代数 — 複合スケジュールの結合子

### 2.1 結合子の分類

複合スケジュールは原子スケジュール上の構造化代数を形成する。3つの独立した意味的次元に沿って分類する:

**次元 A: トポロジー** — 成分が時間的にどう関係するか。
- *並列*: 成分が同時に作動する。
- *逐次*: 成分が固定順序で作動し、一方の完了が次への遷移を駆動する。
- *交替*: 成分が交替し、遷移は環境により制御される。

**次元 B: 弁別性** — 弁別刺激（S^D）が遷移をシグナルするか。
- *弁別あり*: 各成分に個別の S^D が対応する。
- *弁別なし*: S^D の変化なしに遷移する。

**次元 C: 充足論理** — 成分の充足が強化にどう関係するか。
- *OR（選言的）*: いずれか1つの成分の充足が強化を誘起する。
- *AND（連言的）*: 全成分が同時に充足されなければならない。
- *独立*: 各成分が独自の強化随伴性を維持する。
- *逐次*: 一方の成分の完了が次の前提条件となる。
- *文脈切替*: 現在活性化されている成分の随伴性のみが適用される。

完全な分類:

| スケジュール | 略称 | トポロジー | 弁別性 | 充足論理 | 操作体 |
|------------|------|---------|--------|---------|--------|
| Concurrent | Conc | 並列 | N/A（別操作体） | 独立 | 複数 |
| Alternative | Alt | 並列 | N/A | OR | 単一 |
| Conjunctive | Conj | 並列 | N/A | AND | 単一 |
| Chained | Chain | 逐次 | 弁別あり | 逐次 | 単一 |
| Tandem | Tand | 逐次 | 弁別なし | 逐次 | 単一 |
| Multiple | Mult | 交替 | 弁別あり | 文脈切替 | 単一 |
| Mixed | Mix | 交替 | 弁別なし | 文脈切替 | 単一 |

構造的観察: **Chain と Tand** は逐次トポロジーにおける弁別あり/なしの対を形成する。**Mult と Mix** は交替トポロジーにおける同様の対を形成する。これはより高次の抽象を示唆する:

```
Sequential(components, discriminated: bool)
  discriminated = true   → Chain
  discriminated = false  → Tand

Alternating(components, discriminated: bool)
  discriminated = true   → Mult
  discriminated = false  → Mix
```

### 2.2 代数的性質

#### 2.2.1 等価関係 — 定義

本仕様では、スケジュール式に対して3つの異なる関係を使用する。本節および仕様全体における全ての代数的主張は、以下の定義のもとで述べられる。

**定義 1（構文的等価）.** 2つのスケジュール式 `S₁` と `S₂` が*構文的に等価*（`S₁ =_syn S₂` と書く）であるとは、それらの AST 表現が構造的に同一であること — すなわち、全てのノード型、結合子、パラメータ値、子要素の順序が同一であることをいう。構文的等価は再帰的構造比較により決定可能である。

**定義 2（観察トレース）.** *観察トレース*とは、タイムスタンプ付きイベントの有限列 `τ = ⟨(e₁, t₁), (e₂, t₂), …, (eₙ, tₙ)⟩` であり、各 `eᵢ` は反応イベントまたは時間ティックイベントで、`t₁ ≤ t₂ ≤ … ≤ tₙ` を満たす。全ての有限観察トレースの集合を `T` と表記する。

**定義 3（強化帰結列）.** スケジュール式 `S` と観察トレース `τ ∈ T` が与えられたとき、*強化帰結列* `outcome(S, τ)` とは、正準初期状態 `σ₀` から `τ` を処理した際に `S` が生成する強化判定（強化された / 強化されなかった）の列をいう。正準初期状態は全カウンタがゼロ、全タイマーがゼロ、強化履歴が空の状態である。

**定義 4（意味論的等価, ≡）.** 2つのスケジュール式 `S₁` と `S₂` が*意味論的に等価*（`S₁ ≡ S₂` と書く）であるとは、全ての可能な観察トレースに対して同一の強化帰結列を生成することをいう:

```
S₁ ≡ S₂  ⟺  ∀τ ∈ T. outcome(S₁, τ) = outcome(S₂, τ)
```

非形式的には：被験体の行動に関わらず、強化帰結のみを調べることで `S₁` と `S₂` を区別できる観察者は存在しない。意味論的等価は同値関係（反射的、対称的、推移的）である。否定は `≢` と書く。

**定義 5（健全な書き換え規則, →）.** *健全な書き換え規則* `S₁ → S₂` とは、`S₁ ≡ S₂` を満たす AST の有向変換をいう。書き換え規則は左から右へ適用される。適合実装は任意の健全な書き換え規則を最適化パスとして適用してよい（MAY）が、不健全な書き換えを適用してはならない（MUST NOT）。`S₁ ≡ S₂` は `S₁ → S₂` と `S₂ → S₁` の両方が健全であることを含意する。

**表記規約.** 本仕様全体を通じて:
- `≡` と `≢` は意味論的等価とその否定（定義 4）を表す。
- `=` は数学的記述（例: `n + 1 = m`）、または文脈から意図する関係が明白な非形式的説明にのみ使用する。
- `=_syn` は区別が重要な場合に構文的等価（定義 1）を表す。

#### 2.2.2 基本定理

**定理 1（可換性）.**
- `Conc(A, B) ≡ Conc(B, A)` — 操作体の割り当ては任意（ラベリングを除く）。
- `Alt(A, B) ≡ Alt(B, A)` — 選言は可換。
- `Conj(A, B) ≡ Conj(B, A)` — 連言は可換。
- `Chain(A, B) ≢ Chain(B, A)` — 逐次順序は重要。
- `Tand(A, B) ≢ Tand(B, A)` — 逐次順序は重要。
- `Mult(A, B) ≢ Mult(B, A)` — 交替順序は重要。
- `Mix(A, B) ≢ Mix(B, A)` — 交替順序は重要。

*証明スケッチ（Alt の可換性）.* 任意のトレース `τ` に対して、`outcome(Alt(A, B), τ)` はステップ `i` で強化が生じるのは `A` または `B` がステップ `i` で強化を生じる場合に限る。選言は可換であるから `outcome(Alt(A, B), τ) = outcome(Alt(B, A), τ)`。 ∎

*反例（Chain の非可換性）.* `Chain(FR 1, FI 10-s)` と `Chain(FI 10-s, FR 1)` を比較する。前者では1回の反応が FR リンクを完了し FI リンクに遷移する。後者では先に10秒の経過が必要である。トレース `τ' = ⟨(response, t=0), (response, t=11)⟩` は前者で強化を生じるが、後者では生じない。 ∎

**定理 2（結合性）.** 全7結合子は N 項合成に平坦化可能な意味で結合的である:
- `Conc(A, Conc(B, C)) ≡ Conc(A, B, C)`
- `Alt(A, Alt(B, C)) ≡ Alt(A, B, C)`
- `Conj(A, Conj(B, C)) ≡ Conj(A, B, C)`
- `Chain(A, Chain(B, C)) ≡ Chain(A, B, C)`
- `Tand(A, Tand(B, C)) ≡ Tand(A, B, C)`
- `Mult(A, Mult(B, C)) ≡ Mult(A, B, C)`
- `Mix(A, Mix(B, C)) ≡ Mix(A, B, C)`

**定理 3（単位元）.**
- `Alt(S, EXT) ≡ S` — EXT は Alt の単位元（充足されない要素との選言は S のみ）。
- `Conj(S, CRF) ≡ S` — CRF（最初の反応で必ず充足）は Conj の単位元。
- `Chain(CRF, S) ≡ S` — CRF を初期リンクとすると即座に充足される。

**定理 4（零化元）.**
- `Conj(S, EXT) ≡ EXT` — EXT が充足されなければ連言全体が充足されない。
- `Alt(S, CRF) ≡ CRF` — CRF は必ず最初に充足される。

**定理 5（非分配性）.** 一般に、複合スケジュール合成は分配しない:

```
Alt(A, Conj(B, C)) ≢ Conj(Alt(A, B), Alt(A, C))
```

これは意味的に重要であり、括弧が随伴性構造を決定するため、DSL では括弧を明示しなければならない。

#### 2.2.3 Repeat の代数的性質

`Repeat(n, S)` は `Tand(S, S, …, S)`（`S` の `n` 個のコピー）への構文糖衣として定義される（§1.4）。以下の性質は Tand への脱糖と上記の意味論的等価の定義から導出される。

**定理 6（Repeat の単位元）.**
```
Repeat(1, S) ≡ S
```
*証明.* `Repeat(1, S)` は `Tand(S)` に脱糖される。単項の逐次合成はその要素自体と意味論的に等価である。 ∎

**定理 7（Repeat の指数法則）.**
```
Repeat(m, Repeat(n, S)) ≡ Repeat(m × n, S)
```
*証明.* 左辺は `m` 個の `Tand(S, …, S)`（各 `n` 個のコピー）を逐次合成したものに脱糖される。Tand の結合性（定理 2）により、`m × n` 個の `S` の逐次合成に平坦化される。これは `Repeat(m × n, S)` である。 ∎

**定理 8（Repeat の加法的分解）.**
```
Repeat(m + n, S) ≡ Tand(Repeat(m, S), Repeat(n, S))
```
*証明.* 両辺は Tand の結合性により `m + n` 個の `S` の逐次合成に脱糖される。 ∎

**構文糖衣としての完全性.** `Repeat(n, S)` は常に有限の `Tand` に展開されるため、新たな意味論的プリミティブを導入しない。`Repeat` 式の意味は `Tand` の意味論により完全に決定される。

#### 2.2.4 LH の境界恒等式

LH の定義（§1.6）より:

- `S LH ∞ ≡ S` — 無限の保持は時間的制約を課さない。
- `S LH 0 ≡ EXT` — ゼロの保持は強化を利用不可能にする（保持窓は反応が生じる前に閉じる）。

#### 2.2.5 健全な書き換え規則（一覧）

以下の表は、定理 1–8 および §1.6 から導出された全ての健全な書き換え規則をまとめたものである。適合実装はこれらを最適化パスとして適用してよい（MAY）。`方向`列は規則が左から右のみの適用（→）か双方向（↔、すなわち完全な意味論的等価）かを示す。

| # | 規則 | 方向 | 優先度 | 定理 |
|---|------|------|--------|------|
| R1 | `Alt(S, EXT) → S` | → | 1 | 定理 3 |
| R2 | `Alt(EXT, S) → S` | → | 1 | 定理 1 + 定理 3 |
| R3 | `Conj(S, CRF) → S` | → | 1 | 定理 3 |
| R4 | `Conj(CRF, S) → S` | → | 1 | 定理 1 + 定理 3 |
| R5 | `Chain(CRF, S) → S` | → | 1 | 定理 3 |
| R6 | `Conj(S, EXT) → EXT` | → | 2 | 定理 4 |
| R7 | `Conj(EXT, S) → EXT` | → | 2 | 定理 1 + 定理 4 |
| R8 | `Alt(S, CRF) → CRF` | → | 2 | 定理 4 |
| R9 | `Alt(CRF, S) → CRF` | → | 2 | 定理 1 + 定理 4 |
| R10 | `Repeat(1, S) → S` | → | 3 | 定理 6 |
| R11 | `S LH ∞ → S` | → | 3 | §1.6 |
| R12 | `S LH 0 → EXT` | → | 3 | §1.6 |
| R13 | `Conc(A, Conc(B, C)) ↔ Conc(A, B, C)` | ↔ | 4 | 定理 2 |
| R14 | `Alt(A, Alt(B, C)) ↔ Alt(A, B, C)` | ↔ | 4 | 定理 2 |
| R15 | `Conj(A, Conj(B, C)) ↔ Conj(A, B, C)` | ↔ | 4 | 定理 2 |
| R16 | `Chain(A, Chain(B, C)) ↔ Chain(A, B, C)` | ↔ | 4 | 定理 2 |
| R17 | `Tand(A, Tand(B, C)) ↔ Tand(A, B, C)` | ↔ | 4 | 定理 2 |

**優先度**は複数の規則が適合する場合の推奨適用順序を示す。数値が小さいほど先に適用する。R1–R12 は*簡約規則*（右辺の AST ノード数が少ない）、R13–R17 は*構造規則*（ネストされた合成の平坦化）である。

### 2.3 再帰的合成

型体系は任意にネストされた合成を支持する:

```
Schedule = AtomicSchedule | CompoundSchedule | ModifierSchedule
CompoundSchedule = Combinator(Schedule, Schedule, ...)
```

これは標準的な再帰的代数的データ型（ADT）である。例:

```
Conc(Chain(FR 5, VI 60-s), Alt(FR 10, FT 30-s))
```

は、操作体 1 が連鎖 FR5-次に-VI 60 を提示し、操作体 2 が選択 FR10-または-FT 30 を提示する並立スケジュールである。

### 2.4 切替遅延（COD）と固定比切替（FRCO）

切替遅延（COD: Changeover Delay）は、操作体の切替後に新しい操作体での強化を一定時間抑制するパラメータである（Catania, 1966）。COD は `Conc` の**定義的パラメータ**であり、省略可能なメタデータではない:

- COD なしの並立スケジュールは手続き的に特定されない（Herrnstein, 1961）。DSL はリンター警告（`MISSING_COD`）を発し、明示的な COD 指定を推奨する。ランタイムデフォルトは `COD=0-s`。
- `COD=0-s` は合法（明示的ゼロ遅延）で、Shull & Pliskoff (1967) の統制条件に対応するが、VI-VI 配置では lint 警告を出すべきである。

```
Conc(VI 30-s, VI 60-s, COD=2-s)           -- 2秒の切替遅延
Conc(VI 30-s, VI 60-s, COD=0-s)           -- 明示的ゼロ遅延（統制条件）
```

**デフォルト動作:** 対称（切替方向によらず同一の遅延）、非リセット（COD 中の再切替でタイマーが再起動しない）。

**固定比切替（FRCO: Fixed-Ratio Changeover）:** 時間ベースの COD に代わる反応ベースの要件。FRCO は切替後、新しい操作体で N 回反応するまで強化を抑制する（Hunter & Davison, 1985; Pliskoff & Fetterman, 1981）。COD と FRCO は共存可能:

```
Conc(VI 30-s, VI 60-s, FRCO=5)            -- 切替後 5 反応が必要
Conc(VI 30-s, VI 60-s, COD=2-s, FRCO=5)   -- 時間と反応の両方の要件
```

| パラメータ | エイリアス | 次元 | 参考文献 |
|-----------|-----------|------|---------|
| COD | ChangeoverDelay | 時間 (s/ms/min) | Herrnstein (1961); Catania (1966) |
| FRCO | FixedRatioChangeover | 反応数 (dimensionless) | Hunter & Davison (1985) |

**用語に関する注記:** 以前のドラフトでは略語 `COR`（Changeover Response）を使用していたが、これは EAB 文献で確立された略語ではない。標準略語は **FRCO** であり、Hunter & Davison (1985) で導入された。Pliskoff & Fetterman (1981) は "changeover requirement" という記述的表現を用い、定型略語は用いなかった。

COD と FRCO はいずれも `param_decl` によるプログラムレベルのデフォルトをサポートする（`LH = 10-s` と同様）:

```
COD = 2-s                              -- このプログラム内の全 Conc に適用
Conc(VI 30-s, VI 60-s)                    -- COD=2-s を継承
Conc(VI 30-s, VI 60-s, COD=5-s)           -- 式レベルがプログラムレベルを上書き
```

**方向付き COD（directional COD）。** 切替方向によって切替コストが異なる場合、COD は方向指定形式で（出発, 到着）のコンポーネント対と当該遷移の遅延を受け付ける（Pliskoff, 1971; Williams & Bell, 1999）。方向参照には 1 始まりの整数インデックスまたは `let` 束縛名を使用可能:

```
-- 完全な方向指定（インデックスベース）
Conc(VI 30-s, VI 60-s, COD(1->2)=2-s, COD(2->1)=5-s)

-- ベース + 上書き:「COD は 2s だが、VR 20 からの切替のみ 5s」
Conc(VI 30-s, VR 20, COD=2-s, COD(2->1)=5-s)

-- let 束縛ラベルによる自己文書化
let interval = VI 30-s
let ratio    = VR 20
Conc(interval, ratio, COD(interval->ratio)=1-s, COD(ratio->interval)=3-s)
```

**ベース + 上書き意味論。** スカラー `COD=Xs` は全方向へのベース遅延を提供する。方向指定エントリ `COD(x->y)=Ys` は特定の遷移を上書きする。これは JEAB Method section の典型的な記述「COD は 2 s であったが、VR 20 スケジュールからの切替のみ 5 s であった」に直接対応する。

方向付き COD の意味論的規則:
- `dir_ref` が整数の場合 [1, N] の範囲内でなければならない。識別子の場合、`let` 束縛されたコンポーネント名に解決されなければならない。
- 自己参照方向（`COD(1->1)`）→ `DIRECTIONAL_SELF_REFERENCE`。
- 同一方向ペアの重複 → `DUPLICATE_DIRECTIONAL_KW`。
- 方向指定形式は Conc の COD にのみ有効。他のキーワード引数 → `INVALID_DIRECTIONAL_KW`。
- プログラムレベル `param_decl` はスカラー COD のみ（対称ベース）。式レベルの方向付き COD が特定方向を上書きする。
- 各値の検証: スカラー COD と同じ規則（時間単位必須、≥ 0）。

**将来（v1.2）:** リセット型 COD（COD 作動中の再切替でタイマーがリスタートする）。

### 2.5 ブラックアウト（BO）

ブラックアウト（BO: Blackout）は、**多重スケジュール（Multiple）** および **混合スケジュール（Mixed）** の成分間に挿入される、応答非随伴的な暗室期間を指定する。COD（応答随伴的、Conc 固有）と異なり、BO はいかなる応答にも随伴せず、成分間の行動的独立性を確保するための方法論的統制として機能する。

**設計根拠。** BO は行動的コントラスト（behavioral contrast; Reynolds, 1961）に直接影響する。BO 期間が長いほど成分間相互作用が減少し、各成分の弁別制御がより純粋になる。連合学習的には、BO の持続時間が先行成分の刺激表象の減衰に十分かどうかが、成分間の般化を規定する（Bouton, 2004; Wagner, 1981）。これにより BO は Mult/Mix の**構造的パラメータ**であり、単なるセッションメタデータではない — COD の Conc における役割と構造的に対称である。

```
Mult(FR 5, EXT, BO=5-s)               -- 成分間に5秒のブラックアウト
Mix(VI 30-s, VI 60-s, BO=3-s)            -- 3秒のブラックアウト（無弁別）
Mult(FR 5, EXT)                       -- ブラックアウトなし（即時遷移）
```

**デフォルト動作:** BO は省略可能（COD と異なる）。省略時または `BO=0-s` は、ブラックアウトなし（即時成分切り替え）を意味する。対称的（全遷移で同一の持続時間）。

**将来（v1.2）:** 非対称 BO（遷移方向ごとに異なる値。例: Rich→Lean vs. Lean→Rich）。非対称 COD（Issue #25）と同期して設計。

**タイムアウト（TO）との関係。** BO は応答非随伴的、TO は応答随伴的。TO は負の罰（応答に随伴する正の強化からの除去）として機能し、v2.0 で modifier として導入予定。操作的区別と COD/TO/DRO の構造的関係については Issue #28 を参照。

### 2.6 選択行動と手続き–帰結の境界

並立 VR-VR スケジュールは、並立 VI-VI スケジュールとは質的に異なる選択行動を産出する。並立 VI-VI では、被験体は相対的な強化率に比例して反応を配分する——**マッチング法則**（Herrnstein, 1961）。並立 VR-VR では、被験体はより豊かな選択肢にほぼ全ての反応を集中させる——**排他的選択**（exclusive choice; Herrnstein & Loveland, 1975; Baum, Aparicio, & Alonso-Alvarez, 2022）。

**設計判断:** DSL はこの区別を符号化**しない**。`Conc` は構成スケジュールの型（VI/VR/FI/FR 等）に依らず、単一の汎用結合子のままである。これは意図的な設計であり、以下のアーキテクチャ原則を反映している:

> **DSL は手続き（procedure）——実験者が設定するもの——を記述する。行動的帰結（effect）——被験体がどう振る舞うか——を予測するものではない。**

その根拠:

1. **手続きの完備性。** `Conc(VR 20, VR 40, COD=2-s)` は操作的随伴性を完全に記述している: 2つの比率スケジュールが同時に利用可能で、2秒の切替遅延を伴う。整形式の手続き記述にこれ以上のパラメータは不要である。

2. **帰結の経験的条件依存性。** 排他的選択が実際に生じるかどうかは、DSL が既に捉えているパラメータ（比率値、COD、FRCO）だけでなく、DSL のスコープ外の要因（訓練履歴、セッション時間、種）にも依存する。`choice_mode = "exclusive"` を DSL に焼き込むことは、経験的な一般化を手続きの論理的帰結として主張することになる。そうではない。

3. **メカニズムからの導出可能性。** VI-VI と VR-VR の差異は分子的随伴性構造に由来する: VI スケジュールはより長い反応間時間（IRT）を分化強化するが、VR スケジュールでは強化が IRT に依存しない。これにより、VI では切替が有益（未収集の強化子が他方の選択肢に蓄積する）だが VR ではそうでない。構成スケジュールの型は既に DSL 式に符号化されているため、下流の分析レイヤーが冗長なアノテーションなしに予測される選択パターンを導出できる。

**選択分析の所在:** 選択配分（choice allocation）、排他的選択の検出、選択モードの分類は **session-analyzer** レイヤーの責務であり、観察された行動データに基づいて動作する:

| 概念 | レイヤー | 根拠 |
|------|---------|------|
| スケジュール構造（`Conc(VR 20, VR 40, COD=2-s)`） | DSL | 手続き記述 |
| 強化ゲーティング（COD 抑制、比率カウント） | ランタイム（`contingency-py`） | 随伴性の執行 |
| 選択配分、マッチングパラメータ、排他的選択の検出 | session-analyzer | 行動的測定と分類 |

この三層分離により、DSL は随伴性の正確な表記法として保たれ、ランタイムはその随伴性を忠実に実行し、分析器は手続き記述を汚染することなく行動的帰結を特徴づける。

### 2.7 嫌悪スケジュール — Sidman 自由オペラント回避

強化スケジュールのマトリクス（dist × domain = F/V/R × R/I/T）は正の強化
手続きの大多数をカバーするが、嫌悪制御の一部の手続き — とりわけ
**Sidman (1953) の自由オペラント回避** — はこのマトリクスに収まらない
随伴性構造を持つ。2 つの独立した時間パラメータと、反応随伴的な
再スケジュール規則が比率 / 間隔 / 時間のいずれとも異なる。

そのため DSL は `aversive_schedule` 生成規則のもとに専用 primitive
`Sidman` を導入する（grammar.ebnf 参照）。これは design-philosophy §8.1 の
additive な Core 拡張である。

**手続きの定義:** 2 つの時間パラメータを持つ。

- **SSI (Shock-Shock Interval):** 反応がない場合に shock が発生する基底間隔
- **RSI (Response-Shock Interval):** 反応ごとに次の shock を postpone する時間

次の shock 時刻は次の式で決まる:

```
next_shock(t) = max(last_shock_time + SSI, last_response_time + RSI)
```

反応がなければ SSI 秒ごとに shock が発生する。各反応は次の shock を
`last_response + RSI` に再スケジュールし、反応から少なくとも RSI 秒の
無 shock 期間を確保する。RSI ≤ SSI のとき、反応は実際に shock を postpone する
効果を持つ。

**構文:**

```
Sidman(SSI=20-s, RSI=5-s)                              -- 基本形
SidmanAvoidance(SSI=20-s, RSI=5-s)                     -- verbose alias
Sidman(ShockShockInterval=20-s, ResponseShockInterval=5-s)  -- verbose parameter
```

両パラメータとも必須。デフォルト値なし。時間単位は必須。

**他スケジュールとの合成:** `Sidman` は `base_schedule` であり、任意の複合
コンビネータ内部に出現できる:

```
Chain(FR 10 @punisher("food"), Sidman(SSI=20-s, RSI=5-s) @punisher("shock"))
```

これは第 1 link で food の FR 10 を完了し、第 2 link で自由オペラント回避に
遷移する連鎖スケジュールである（de Waard, Galizio, & Baron, 1979）。

**意味的制約:**

- `SSI` と `RSI` の両方が必須。いずれかが欠けると `MISSING_SIDMAN_PARAM`。
- 両方とも時間単位を持つ必要がある。無次元値は `SIDMAN_TIME_UNIT_REQUIRED`。
- 両方とも厳密に正の値。非正の値は `SIDMAN_NONPOSITIVE_PARAM`。
- `RSI > SSI` は linter WARNING `RSI_EXCEEDS_SSI` を発する。RSI が SSI を
  超えると、反応は SSI の基底発動を下回って shock を postpone できない
  （Sidman, 1953; Hineline, 1977）。

**刺激 annotation:** Sidman 手続きは定義上嫌悪的である。source 上で実験者の
意図を明示するため `@punisher` の使用を推奨する。ただし `@reinforcer` も
等価な alias として受理される（annotation-design.md §3.5 参照）:

```
Sidman(SSI=20-s, RSI=5-s) @punisher("shock", intensity="0.5mA")
Sidman(SSI=20-s, RSI=5-s) @reinforcer("shock", intensity="0.5mA")  -- equivalent
```

**v1.x の嫌悪スケジュールのスコープ:** `aversive_schedule` 生成規則は
additive である。v1.x では `Sidman`（自由オペラント回避）と
`DiscriminatedAvoidance`（試行ベース回避）を含む。罰の重畳は `Overlay`
コンビネータ（§2.10）で表現する。単純な escape（予告 CS なしで進行中の
嫌悪刺激を反応で終了）は、既存の構成素と刺激 annotation で近似可能である。

### 2.8 Lag スケジュール — オペラント変動性

分化強化修飾子 DRL、DRH、DRO はいずれも **時間次元**（反応間間隔）に対して
動作する。これらとは異なる種類の分化強化として、**反応の変動性（variability）
そのもの** に対して動作する手続きがある。**Page & Neuringer (1985)** が導入した
**Lag スケジュール** は、現在の反応（または反応系列）が直前 *n* 回の反応の
いずれとも異なる場合にのみ強化する。これは、**変動性それ自体が随伴強化によって
制御可能なオペラント次元** であることを示した画期的な発見であった。

本 DSL は `Lag` を分化強化修飾子として `modifier` 生成規則（grammar.ebnf）に
追加する。DRL/DRH/DRO/PR/Repeat と同列である。これは design-philosophy §8.1 の
additive な Core 拡張である。

**手続きの定義:**

- **n**: 照合する直前反応/系列の数。`Lag 1` は直前反応と異なれば強化。
  `Lag 5` は直前 5 回のいずれとも異なれば強化。
- **length**（optional, default = 1）: 反応単位のサイズ。`length=1` は個別反応
  を単位とする（応用研究のデフォルト）。`length=8` は 8 反応系列を単位とする
  （Page & Neuringer 1985 の 2 キー 8-peck 系列で使用）。

形式的には、時刻 t における反応単位を S(t) とすると、強化は以下の条件で提示される:

```
S(t) ∉ { S(t-1), S(t-2), ..., S(t-n) }
```

**構文:**

```
Lag 5                       -- 略記形式。文献の "Lag 5" 表記と一致。
                               length は default=1（個別反応単位）
Lag(5)                      -- Lag 5 の括弧形式（等価）
Lag(5, length=8)            -- Page & Neuringer (1985) 風 8-peck sequence
Lag(50, length=8)           -- Page & Neuringer (1985) Experiment 3 の高 Lag
```

パラメータ `n` は文献表記（"Lag 5", "Lag 10"）と一致させるため **positional**
とする。optional な keyword argument `length` は反応単位のサイズ。

**意味的制約:**

- `n` は非負整数。`Lag 0` は合法で、意味論的に CRF と等価（variability 要求なし）。
- `n` に時間単位を付けることは不可。`Lag 5s` → `LAG_UNEXPECTED_TIME_UNIT`。
  Lag は categorical / sequence ベースであり、time dimension を持つ variant は
  文献上存在しない（時間ベースの分化強化は DRL/DRH、嫌悪系の時間パラメータは
  `ShockShockInterval` を参照）。
- `length` を指定する場合、正整数（>= 1）でなければならない。省略時は
  `length = 1`。
- 大きな `n`（> 50）は linter WARNING `LAG_LARGE_N` を発する。歴史的研究は
  n <= 50 を使用する。

**刺激アノテーション:** Lag は他のスケジュールと同様に `@reinforcer` と組み合わせ
られる:

```
Lag(5, length=8)
  @reinforcer("grain")
  @operandum("left_key") @operandum("right_key")
```

**合成:** Lag は modifier であり、任意の複合コンビネータの内部に出現できる。
よく使われるパターンは `Mult` による variability 訓練と CRF ベースラインの
交替:

```
Mult(Lag(5, length=8), CRF)
```

**歴史的注記:**

- Page & Neuringer (1985) の主要な研究単位は **反応系列** であり、`length = 1`
  （個別反応）は系列の退化形で、応用研究のユースケースに対応する
  （マンド・タクトの variability 訓練: Miller & Neuringer, 2000; Lee, McComas,
  & Jawor, 2002; Rodriguez et al., 2011）。
- Lag スケジュールに時間次元の variant は確立していない。時間ベースの
  variability 研究は別手続き（Platt, 1973 の反応持続時間分化強化、
  Alleman & Platt, 1973 の percentile schedule、DRD 等）で行われる。
- `Lag 0` ≡ CRF は一貫性のために保持される境界ケース。「variability 要求なしの
  Lag schedule」というユーザーの意図を保存し、parse 時に最適化消去されない。

**`length` が明示的である理由。** 文献は標準的な系列長を示さない（Page & Neuringer, 1985: 8; Ribeiro et al., 2022: 5; 応用研究: 1）。DSL が `length` を公開するのは、普遍的に適切な単一のデフォルトが存在しないためである。変動性が真のオペラント次元を構成するか否かは論争中（Nergaard & Holth, 2020 vs. Reed, 2023）; DSL は立場を取らない。詳細は [design-rationale.md §3](../../../docs/ja/design-rationale.md#3-lag-length-が明示的である理由とオペラント次元論争) を参照。

### 2.9 弁別回避（Discriminated Avoidance）

Sidman 自由オペラント回避（§2.7）には警告信号がない — shock は反応によって
postpone されるだけの時間的サイクルで発生する。**弁別回避**（Solomon & Wynne,
1953）は条件刺激（CS）が無条件刺激（US）を予告する手続きである。CS 中に
反応すれば US が阻止され（回避試行）、反応しなければ US が呈示される
（逃避/失敗試行）。

2 つのパラダイムの随伴性構造は異なる:
- **Sidman（自由オペラント）:** CS なし。反応は RSI 分だけ次の US を postpone。
- **弁別（試行ベース）:** CS が固定の CSUSInterval で US を予告。CS 中の反応で
  US を阻止。

本 DSL は `DiscriminatedAvoidance`（alias `DiscrimAv`）を `aversive_schedule`
生成規則の第 2 の primitive として追加する。

**手続きの定義:**

- **CSUSInterval**（必須）: CS 提示から US 提示までの時間。この間隔内に反応
  すると US は阻止（回避試行）。
- **ITI**（必須）: 試行間間隔。CS-onset → 次の CS-onset で測定。CSUSInterval
  より大きくなければならない。
- **mode**（必須）: `fixed` または `escape`。
  - `fixed`: US は固定の `ShockDuration` で呈示。
  - `escape`: US は被験体の反応で終了。optional な `MaxShock` で安全カットオフを
    設定可能。
- **ShockDuration**（mode=fixed のみ必須）: 固定 US 呈示時間。
- **MaxShock**（mode=escape のみ optional）: escape 終端の安全カットオフ。
  Solomon & Wynne (1953) は 2 分を使用。

**構文:**

```
DiscriminatedAvoidance(CSUSInterval=10-s, ITI=3-min, mode=escape)
DiscriminatedAvoidance(CSUSInterval=10-s, ITI=3-min, mode=escape, MaxShock=2-min)
DiscriminatedAvoidance(CSUSInterval=10-s, ITI=3-min, mode=fixed, ShockDuration=0.5-s)
DiscrimAv(CSUSInterval=10-s, ITI=3-min, mode=escape)  -- 短縮 alias
```

**意味的制約:**

- `CSUSInterval`、`ITI`、`mode` は全て必須。欠損 → `MISSING_DA_PARAM`。
- 全ての時間パラメータに時間単位必須。無次元 → `DA_TIME_UNIT_REQUIRED`。
- 全ての時間値は厳密に正。非正 → `DA_NONPOSITIVE_PARAM`。
- `ITI` は `CSUSInterval` より大きい必要あり → `DA_ITI_TOO_SHORT`。
- `mode=fixed` は `ShockDuration` 必須 → `MISSING_SHOCK_DURATION`。
- モード非対応パラメータ → `INVALID_PARAM_FOR_MODE`。
- 未知の mode 値 → `DA_INVALID_MODE`。

**刺激 annotation:** Sidman と同様、弁別回避は定義上嫌悪的。`@punisher` を推奨:

```
DiscrimAv(CSUSInterval=10-s, ITI=3-min, mode=escape, MaxShock=2-min)
  @punisher("shock", intensity="1.0mA")
  @sd("light", modality="visual")
```

**合成:** `DiscriminatedAvoidance` は `base_schedule` であり、任意の複合
コンビネータ内部に出現できる:

```
Chain(FR 10, DiscrimAv(CSUSInterval=10-s, ITI=3-min, mode=escape))
```

### 2.10 罰の重畳（Punishment Overlay）

`Overlay` コンビネータは、既存の強化ベースラインに罰随伴性を重畳する。これは、
維持されたオペラント行動に対する反応随伴性嫌悪刺激の効果を研究する標準パラダイム
である（Azrin & Holz, 1966）。

**手続きの定義:** ベースラインスケジュールは通常通り強化子を配分する。同時に、
罰スケジュールが同じ反応に対して嫌悪刺激を呈示する。両スケジュールは単一の
反応ストリームを共有する。

**構文:**

```
Overlay(VI 60-s, FR 1)                     -- 全反応に罰
Overlay(Conc(VI 60-s, VI 180-s, COD=2-s), FR 1)  -- 並立ベースライン
```

第 1 成分がベースライン（強化）、第 2 成分が罰スケジュール。

**意味的制約:**

- 正確に 2 成分。3 以上 → `OVERLAY_REQUIRES_TWO`。
- v1.x ではキーワード引数なし → `INVALID_KEYWORD_ARG`。

**刺激 annotation:** `@punisher` で嫌悪刺激、`@reinforcer` でベースラインを記述:

```
Overlay(VI 60-s, FR 1)
  @reinforcer("food")
  @punisher("shock", intensity="0.5mA")
```

**v1.x のスコープ:** 罰は全反応を対象とする。反応クラス特異的な罰
（例: 切替反応のみに罰; Todorov, 1971）は v1.y で対応予定。

### 2.11 二次スケジュール（Second-Order Schedules）

**二次スケジュール**は 2 つの原子スケジュールを階層的な 2 つの役割に合成する（Kelleher, 1966; Kelleher & Fry, 1962）:

- **Unit スケジュール** — *派生的反応単位*を定義する内部スケジュール。unit の各完了が 1 単位として計数される。
- **Overall スケジュール** — unit 完了に随伴して強化を配分する外部スケジュール。

```
SecondOrder = Overall(Unit)
Overall     = AtomicSchedule          -- パラメトリックのみ（EXT, CRF 不可）
Unit        = AtomicSchedule          -- 単純スケジュールのみ（v1.0, 凍結）
```

**Unit 制約（v1.0 凍結）.** unit 位置は単純（原子）スケジュールのみを受け付ける。`Chain(FR3, FI10)` や `Conc(FR5, FI30)` 等の複合スケジュールは `INVALID_SECOND_ORDER_UNIT` で拒否される。この制約は歴史的文献の調査に基づき v1.x で凍結される: Kelleher (1966)、Malagodi, DeWeese & Johnston (1973)、Jwaideh (1973) はいずれも simple-inside-simple の配置のみを使用しており、compound inner を用いた二次スケジュール実験の公刊例は存在しない。将来的に新たな実験手続きにより必要性が生じた場合、design-philosophy §7.1 の additive only 原則に従い minor version で拡張可能である。

**構文例.** `FR5(FI30)` = FI 30-s の各完了を 1 単位とし、5 回の単位完了で強化。

**重要な意味的制約.** overall 位置の `value` は常に**単位完了計数**として解釈される — 個別反応計数ではない。単独の `FR5` は 5 個別反応を計数するが、`FR5(FI30)` は FI 30-s の 5 回完了を計数する（Kelleher & Fry, 1962, p. 544）。

#### 2.11.1 操作的意味論

**FR-overall の脱糖.** overall が比率スケジュール（FR, VR, RR）の場合、brief 刺激なしでは tandem 合成に還元可能:

```
FR_n(S) ≡ Repeat(n, S) ≡ Tand(S, S, …, S)    [n コピー]
```

**Interval/Time-overall: 非還元的プリミティブ.** overall が時間間隔スケジュール（FI, VI 等）の場合、Tand への還元は**不可能**。overall が unit 完了間の強化の時間的分布を制御するため、状態付きプリミティブが必要。

**状態機械.**

```
State: (unit_state, overall_state, unit_completion_count)

初期化:
  unit_state     = Unit.initial()
  overall_state  = Overall.initial()
  unit_completion_count = 0

反応イベント発生時 (obs):
  unit_result = Unit.evaluate(unit_state, obs)
  if unit_result.satisfied:
    unit_completion_count += 1
    unit_state = Unit.initial()                -- unit リセット
    overall_result = Overall.evaluate(overall_state, unit_completion_event)
    if overall_result.satisfied:
      一次強化子配達()
      overall_state = Overall.initial()        -- overall リセット
      unit_completion_count = 0
    else:
      brief 刺激呈示()                         -- 条件性強化子（設定時）
  else:
    unit_state = unit_result.next_state
```

**overall クロックリセット規則.** overall の内部タイマーは各一次強化配達後にリセットされる。`FI120(FR10)` では: 一次強化後、FI 120-s クロックはゼロから再開する（Goldberg, Kelleher, & Morse, 1975）。

**ドメイン別動作.**

| Overall ドメイン | `overall_result.satisfied` の条件 | 還元可能? |
|---|---|---|
| 比率 (FR, VR, RR) | `unit_completion_count == Overall.value` | Yes → `Repeat(n, Unit)` |
| 時間間隔 (FI, VI, RI) | `最終強化からの経過時間 ≥ Overall.value` かつ unit 完了が生じた | No |
| 時間 (FT, VT, RT) | `最終強化からの経過時間 ≥ Overall.value`（反応非依存） | No |

**参考文献:**
- Goldberg, S. R., Kelleher, R. T., & Morse, W. H. (1975). Second-order schedules of drug injection. *Federation Proceedings*, *34*(9), 1771–1776.
- Kelleher, R. T. (1966). Conditioned reinforcement in second-order schedules. *JEAB*, 9(5), 475–485. https://doi.org/10.1901/jeab.1966.9-475
- Kelleher, R. T., & Fry, W. (1962). Stimulus functions in chained fixed-interval schedules. *JEAB*, 5(2), 167–173. https://doi.org/10.1901/jeab.1962.5-167
- Kelleher, R. T., & Gollub, L. R. (1962). A review of positive conditioned reinforcement. *JEAB*, *5*(S4), 543–597. https://doi.org/10.1901/jeab.1962.5-s543

---

### 2.13 表示的意味論（Denotational Semantics）

本節では、合成的意味関数 `⟦_⟧` を定義し、すべての `ScheduleExpr` を数学的対象——*スケジュールマシン*——に写像する。さらに、この表示が §2.2.1 で定義した操作的等価性に対して妥当（adequate）であることを証明する。§2.2.1 が `≡` を観察トレースに対する全称量化で定義するのに対し、表示的意味論は*合成的*推論を可能にする：複合式の意味はその構成要素の意味のみから決定される。

#### 2.13.1 スケジュールマシン

**定義 9（事象）。** *事象*（event）とは、反応事象またはセッション時刻を伴う時間刻み事象のいずれかである：

```
E  ::=  Response(t)        -- セッション時刻 t での反応
      | Tick(t)            -- セッション時刻 t への時計進行
```

**定義 10（帰結）。** *帰結*（outcome）とは、所与の事象に対するスケジュールの決定である：

```
O  ::=  Reinforced         -- 一次強化子の配達
      | Brief              -- 短時間刺激 / 条件性強化子（SecondOrder のみ）
      | None               -- 帰結なし
```

**定義 11（スケジュールマシン）。** *スケジュールマシン*は三つ組 `M = (Σ, σ₀, δ)` であり：

- `Σ` は（無限の可能性もある）内部状態の集合、
- `σ₀ ∈ Σ` は初期状態、
- `δ : Σ × E → Σ × O` は遷移関数

である。事象列 `τ = ⟨e₁, e₂, …, eₙ⟩` に対する `M` の*走行*（run）を帰納的に定義する：

```
run(M, ⟨⟩)        = ⟨⟩
run(M, ⟨e₁⟩ ++ τ) = let (σ', o) = δ(σ₀, e₁)
                      in ⟨o⟩ ++ run((Σ, σ', δ), τ)
```

*帰結列*は `outcomes(M, τ) = run(M, τ)` である。

**定義 12（外延的等価性）。** 2 つのスケジュールマシン `M₁ = (Σ₁, σ₁, δ₁)` と `M₂ = (Σ₂, σ₂, δ₂)` が*外延的に等価*であるとは、あらゆる有限事象列に対して同一の帰結列を生成することをいう。`M₁ ≈ M₂` と書く：

```
M₁ ≈ M₂  ⟺  ∀τ ∈ E*. outcomes(M₁, τ) = outcomes(M₂, τ)
```

注: `≈` はマシンレベルの関係であり、式レベルの `≡`（定義 4, §2.2.1）に対応する。妥当性定理（§2.13.6）が両者の一致を確立する。

#### 2.13.2 意味関数

意味関数 `⟦_⟧ : ScheduleExpr → ScheduleMachine` は AST 構造上の帰納的定義である。以下のすべての表示は Phase 3（Resolved）の AST（§2.12.1）——束縛展開、Repeat 脱糖、LH 伝播後——に対して作用する。

#### 2.13.3 原子スケジュールの表示

**比率スケジュール。** `dist ∈ {Fixed, Variable, Random}`、`n ∈ ℤ⁺` に対し：

```
⟦Atomic(dist, Ratio, n)⟧ = (Σ, σ₀, δ)  where
    Σ   = ℤ≥0 × ValueSeq           -- (反応カウント, 値生成器)
    σ₀  = (0, init(dist, n))
    δ((k, g), Response(t)) =
        let target = current(g) in
        if k + 1 ≥ target
            then ((0, advance(g)), Reinforced)
            else ((k + 1, g), None)
    δ((k, g), Tick(t)) = ((k, g), None)
```

`ValueSeq` は値生成器である。Fixed では `current = n` が定数。Variable では Fleshler-Hoffman (1962) 系列に従う。Random では平均 `n` の幾何分布から標本する。

**時間間隔スケジュール。** `dist ∈ {Fixed, Variable, Random}`、`t ∈ ℝ⁺` に対し：

```
⟦Atomic(dist, Interval, t)⟧ = (Σ, σ₀, δ)  where
    Σ   = ℝ≥0 × Bool × ValueSeq   -- (経過時間, 間隔経過フラグ, 値生成器)
    σ₀  = (0, false, init(dist, t))
    δ((e, _, g), Tick(t')) =
        let target = current(g) in
        ((t' − t_last_reinforcement, t' − t_last_reinforcement ≥ target, g), None)
    δ((e, true, g), Response(t')) =
        ((0, false, advance(g)), Reinforced)
    δ((e, false, g), Response(t')) =
        ((e, false, g), None)
```

**時間スケジュール。** `dist ∈ {Fixed, Variable, Random}`、`t ∈ ℝ⁺` に対し：

```
⟦Atomic(dist, Time, t)⟧ = (Σ, σ₀, δ)  where
    Σ   = ℝ≥0 × ValueSeq           -- (経過時間, 値生成器)
    σ₀  = (0, init(dist, t))
    δ((e, g), Tick(t')) =
        let target = current(g) in
        if t' − t_last_reinforcement ≥ target
            then ((0, advance(g)), Reinforced)
            else ((t' − t_last_reinforcement, g), None)
    δ((e, g), Response(t')) = ((e, g), None)
```

注: 時間スケジュールは反応非依存であり、反応事象は状態遷移にも帰結にも影響しない。

**特殊スケジュール。**

```
⟦EXT⟧ = ({∗}, ∗, λ(∗, e). (∗, None))

⟦CRF⟧ = ⟦Atomic(Fixed, Ratio, 1)⟧
```

EXT は決して強化しない自明な 1 状態マシンである。CRF は FR(1) に定義的に等しい（§1.3）。

#### 2.13.4 結合子の表示

各成分 `i` について `⟦Sᵢ⟧ = (Σᵢ, σᵢ, δᵢ)` とする。

**積結合子**（並行トポロジー）。状態空間を直積として合成する。

```
⟦Conc(S₁, …, Sₙ)⟧ = (Σ₁ × … × Σₙ, (σ₁, …, σₙ), δ)  where
    δ((s₁, …, sₙ), e) =
        let (s'ᵢ, oᵢ) = δᵢ(sᵢ, e)  for each i
        in ((s'₁, …, s'ₙ), aggregate_conc(o₁, …, oₙ))
    aggregate_conc: 各成分が独立に自身のオペランダムを強化する
```

```
⟦Alt(S₁, …, Sₙ)⟧ = (Σ₁ × … × Σₙ, (σ₁, …, σₙ), δ)  where
    δ((s₁, …, sₙ), e) =
        let (s'ᵢ, oᵢ) = δᵢ(sᵢ, e)  for each i
        in if ∃i. oᵢ = Reinforced
            then ((σ₁, …, σₙ), Reinforced)    -- 全成分リセット
            else ((s'₁, …, s'ₙ), None)
```

```
⟦Conj(S₁, …, Sₙ)⟧ = (Σ₁ × … × Σₙ × 𝒫({1..n}), (σ₁, …, σₙ, ∅), δ)  where
    δ((s₁, …, sₙ, sat), e) =
        let (s'ᵢ, oᵢ) = δᵢ(sᵢ, e)  for each i
        let sat' = sat ∪ {i | oᵢ = Reinforced}
        in if sat' = {1..n}
            then ((σ₁, …, σₙ, ∅), Reinforced)   -- 全充足 → 強化 + リセット
            else ((s'₁, …, s'ₙ, sat'), None)
```

**逐次結合子**（余積/連鎖トポロジー）。

```
⟦Chain(S₁, …, Sₙ)⟧ = (Σ₁ + … + Σₙ, inj₁(σ₁), δ)  where
    δ(injₖ(sₖ), e) =
        let (s'ₖ, oₖ) = δₖ(sₖ, e) in
        if oₖ = Reinforced ∧ k < n
            then (injₖ₊₁(σₖ₊₁), None)          -- 次のリンクへ（強化なし）
        else if oₖ = Reinforced ∧ k = n
            then (inj₁(σ₁), Reinforced)          -- 最終リンク → 強化 + 再開
        else (injₖ(s'ₖ), None)
```

`⟦Tand(S₁, …, Sₙ)⟧` は `Chain` と同一の遷移構造を持つ。両者の区別は弁別性（S^D の有無）であり、スケジュールマシンの遷移関数の外部にある環境変数である。表示レベルでは：

```
⟦Tand(S₁, …, Sₙ)⟧ ≈ ⟦Chain(S₁, …, Sₙ)⟧
```

これは、Tand と Chain がスケジュールエンジンの観点からは手続き的に同一であるという形式的事実を捉えている。行動的差異は強化随伴性からではなく S^D 制御から生じる（Ferster & Skinner, 1957, Ch. 11–12）。

**交替結合子**（切り替えトポロジー）。

```
⟦Mult(S₁, …, Sₙ)⟧ = (Σ₁ × … × Σₙ × ℕ, (σ₁, …, σₙ, 1), δ)  where
    δ((s₁, …, sₙ, k), e) =
        let (s'ₖ, oₖ) = δₖ(sₖ, e)                    -- 活性成分のみが事象を処理
        let s'ⱼ = sⱼ for j ≠ k                         -- 非活性成分は凍結
        in if oₖ = Reinforced
            then ((s'₁, …, s'ₙ, switch(k, n)), Reinforced)
            else ((s'₁, …, s'ₙ, k), None)
    switch: 成分遷移関数（環境制御、スケジュール非決定）
```

`⟦Mix(S₁, …, Sₙ)⟧` も同一構造であり、Mult/Mix の区別は Chain/Tand と同様に弁別性による：

```
⟦Mix(S₁, …, Sₙ)⟧ ≈ ⟦Mult(S₁, …, Sₙ)⟧
```

#### 2.13.5 修飾子とラッパーの表示

**LimitedHold。** `⟦S⟧ = (Σ_S, σ_S, δ_S)` とする。

```
⟦S LH d⟧ = (Σ_S × LHPhase, (σ_S, Waiting), δ)  where
    LHPhase  ::=  Waiting | HoldOpen(t_sat)

    δ((s, Waiting), e) =
        let (s', o) = δ_S(s, e) in
        if o = Reinforced
            then ((s', HoldOpen(time(e))), None)     -- S 充足 → 保持窓を開く
            else ((s', Waiting), None)

    δ((s, HoldOpen(t₀)), Response(t)) =
        if t − t₀ ≤ d
            then ((reset(s), Waiting), Reinforced)    -- 窓内の反応 → 配達
            else ((reset(s), Waiting), None)           -- 窓失効

    δ((s, HoldOpen(t₀)), Tick(t)) =
        if t − t₀ > d
            then ((reset(s), Waiting), None)           -- 窓失効、取消
            else ((s, HoldOpen(t₀)), None)
```

これは §1.6 の状態機械を合成的表示として直接形式化したものである。内部スケジュールの表示 `⟦S⟧` はそのまま埋め込まれ、LH が位相ラッパーを付加する。

**差異強化修飾子。** `⟦S⟧ = (Σ_S, σ_S, δ_S)` とする。

```
⟦DRL(t, S)⟧ = (Σ_S × ℝ≥0, (σ_S, ∞), δ)  where
    δ((s, t_last), Response(t')) =
        let IRT = t' − t_last in
        let (s', o) = δ_S(s, Response(t')) in
        if IRT ≥ t ∧ o = Reinforced
            then ((s', t'), Reinforced)
            else ((reset(s), t'), None)                -- IRT 不足 → リセット
    δ((s, t_last), Tick(t')) = let (s', _) = δ_S(s, Tick(t')) in ((s', t_last), None)
```

`DRH(t, S)` は IRT 条件を `IRT ≤ t` に置き換える。`DRO(t)` は内部スケジュールに依存しないタイマーベースのマシンであり、標的反応が時間 `t` 以上不在の場合に強化する。

**SecondOrder。** `⟦Unit⟧ = (Σ_U, σ_U, δ_U)` および `⟦Overall⟧ = (Σ_O, σ_O, δ_O)` とする。

```
⟦SecondOrder(Overall, Unit)⟧ = (Σ_U × Σ_O × ℕ, (σ_U, σ_O, 0), δ)  where
    δ((u, o, c), e) =
        let (u', o_u) = δ_U(u, e) in
        if o_u = Reinforced                                -- unit 完了
            then let c' = c + 1 in
                 let (o', o_o) = δ_O(o, UnitCompletion) in
                 if o_o = Reinforced
                     then ((σ_U, σ_O, 0), Reinforced)     -- 一次強化
                     else ((σ_U, o', c'), Brief)           -- 短時間刺激
            else ((u', o, c), None)
```

これは §2.11.1 の状態機械に正確に対応し、unit と overall のスケジュールの表示の合成として表現されている。

#### 2.13.6 妥当性定理

**定理 9（妥当性, Adequacy）。** 表示的意味論は操作的意味論に対して妥当である：すべてのスケジュール式 `S₁`, `S₂` に対し：

```
S₁ ≡ S₂  ⟺  ⟦S₁⟧ ≈ ⟦S₂⟧
```

*証明の概略。* 両方の関係は事象列に対する全称量化で定義される。操作的 `≡`（定義 4）は観察トレース `τ ∈ T` に対して量化し `outcome(S, τ)` を比較する。表示的 `≈`（定義 12）は事象列 `τ ∈ E*` に対して量化し `outcomes(⟦S⟧, τ)` を比較する。

（*右から左*） `⟦S₁⟧ ≈ ⟦S₂⟧` を仮定する。観察トレース（定義 2）はタイムスタンプ付き事象の有限列であり、`E*` の要素そのものである。定義 3 の `outcome` 関数は走行から強化決定を抽出するが、これは `outcomes(⟦S⟧, τ)` の `{Reinforced, None}` 成分への射影である。よって `outcomes(⟦S₁⟧, τ) = outcomes(⟦S₂⟧, τ)` はすべての `τ` に対して `outcome(S₁, τ) = outcome(S₂, τ)` を含意する。

（*左から右*） `S₁ ≡ S₂` を仮定する。表示マシンが同一の帰結を生成することを示す。構成により、`⟦S⟧` は `S` の操作的振る舞いを忠実に実装する：各意味節（§2.13.3–§2.13.5）は対応する操作的仕様（§1.6, §2.11.1 の状態機械、§2.1 の結合子定義）を反映している。定義 3 の正準的初期状態 `σ₀` は各マシンの `σ₀` に対応する。よって `outcome(S, τ) = outcomes(⟦S⟧, τ)|_{Reinforced/None}` がすべての `τ` について成立し、`S₁ ≡ S₂` は `⟦S₁⟧ ≈ ⟦S₂⟧` を含意する。∎

**系（合成性）。** `S₁ ≡ S₂` ならば、任意の文脈 `C[_]`（穴を持つスケジュール式）に対して `C[S₁] ≡ C[S₂]`。これは `⟦_⟧` の合成的構造から従う：各結合子の意味節は成分マシンから合成マシンを構築するため、成分を外延的等価なマシンで置換すれば外延的等価な合成が得られる。

#### 2.13.7 例：表示的証明

表示的枠組みは、マシンに対する代数的計算に帰着させることで、いくつかの証明を簡略化する。

**定理 3（再導出）：`Alt(S, EXT) ≡ S`。**

```
⟦Alt(S, EXT)⟧ = (Σ_S × {∗}, (σ_S, ∗), δ)  where
    δ((s, ∗), e) =
        let (s', o) = δ_S(s, e) in
        let (∗, None) = δ_EXT(∗, e) in      -- EXT は決して強化しない
        if o = Reinforced
            then ((σ_S, ∗), Reinforced)
            else ((s', ∗), None)
```

`{∗}` 成分は不活性であり、情報を寄与せず強化を発火しない。マシンの振る舞いは完全に `⟦S⟧` によって決定される。形式的に `{∗}` 成分を射影して除去すれば `⟦S⟧` と同型なマシンが得られる。よって `⟦Alt(S, EXT)⟧ ≈ ⟦S⟧` であり、妥当性により `Alt(S, EXT) ≡ S`。∎

**定理 4（再導出）：`Conj(S, EXT) ≡ EXT`。**

```
⟦Conj(S, EXT)⟧ = (Σ_S × {∗} × 𝒫({1,2}), (σ_S, ∗, ∅), δ)
```

連言が強化するには両成分が充足される必要がある。`δ_EXT` は `Reinforced` を生成しないため、すべてのトレースで `2 ∉ sat'` となる。よって `sat' ≠ {1, 2}` が常に成立し、マシンは決して強化しない。これは `⟦EXT⟧` に外延的等価である。∎

**定理 7（再導出）：`Repeat(m, Repeat(n, S)) ≡ Repeat(m × n, S)`。**

脱糖後、`Repeat(m, Repeat(n, S))` は `Tand(Tand(S,…,S), …, Tand(S,…,S))`（n 項 Tand の m 個の複製）となる。Chain/Tand の表示は状態空間の余積上の逐次的前進を使用する。余積の逐次合成の結合性により：

```
⟦Tand(Tand(S₁,…,Sₙ), Tand(Sₙ₊₁,…,S₂ₙ))⟧
    ≈ ⟦Tand(S₁,…,Sₙ, Sₙ₊₁,…,S₂ₙ)⟧
```

これは `m × n` 個の複製に一般化され、`⟦Repeat(m × n, S)⟧` を与える。∎

**参考文献:**

- Scott, D., & Strachey, C. (1971). Toward a mathematical semantics for computer languages. *Proceedings of the Symposium on Computers and Automata*, Polytechnic Institute of Brooklyn, 19–46.
- Stoy, J. E. (1977). *Denotational Semantics: The Scott-Strachey Approach to Programming Language Theory*. MIT Press.
- Wadler, P. (1992). The essence of functional programming. In *Proceedings of POPL '92* (pp. 1–14). ACM. https://doi.org/10.1145/143165.143169

---

## 参考文献

- Azrin, N. H., & Holz, W. C. (1966). Punishment. In W. K. Honig (Ed.), *Operant behavior: Areas of research and application* (pp. 380-447). Appleton-Century-Crofts.
- Bloomfield, T. M. (1966). Two types of behavioral contrast in discrimination learning. *JEAB*, 9(2), 155-161. https://doi.org/10.1901/jeab.1966.9-155
- Catania, A. C. (2013). *Learning* (5th ed.). Sloan Publishing.
- Farmer, J. (1963). Properties of behavior under random interval reinforcement schedules. *Journal of the Experimental Analysis of Behavior*, 6(4), 607-616. https://doi.org/10.1901/jeab.1963.6-607
- Ferster, C. B., & Skinner, B. F. (1957). *Schedules of reinforcement*. Appleton-Century-Crofts.
- Solomon, R. L., & Wynne, L. C. (1953). Traumatic avoidance learning: Acquisition in normal dogs. *Psychological Monographs: General and Applied*, 67(4), 1-19. https://doi.org/10.1037/h0093649
- Todorov, J. C. (1971). Concurrent performances: Effect of punishment contingent on the switching response. *JEAB*, 16(1), 51-62. https://doi.org/10.1901/jeab.1971.16-51
- Findley, J. D. (1958). Preference and switching under concurrent scheduling. *Journal of the Experimental Analysis of Behavior*, 1(2), 123-144. https://doi.org/10.1901/jeab.1958.1-123
- Fleshler, M., & Hoffman, H. S. (1962). A progression for generating variable-interval schedules. *Journal of the Experimental Analysis of Behavior*, 5(4), 529-530. https://doi.org/10.1901/jeab.1962.5-529
- Herrnstein, R. J. (1961). Relative and absolute strength of response as a function of frequency of reinforcement. *Journal of the Experimental Analysis of Behavior*, 4(3), 267-272. https://doi.org/10.1901/jeab.1961.4-267
- Herrnstein, R. J., & Morse, W. H. (1957). Some effects of response-independent positive reinforcement on maintained operant behavior. *Journal of Comparative and Physiological Psychology*, *50*(5), 461–467. https://doi.org/10.1037/h0048673
- Herrnstein, R. J., & Loveland, D. H. (1975). Maximizing and matching on concurrent ratio schedules. *Journal of the Experimental Analysis of Behavior*, 24(1), 107-116. https://doi.org/10.1901/jeab.1975.24-107
- Baum, W. M., Aparicio, C. F., & Alonso-Alvarez, B. (2022). Rate matching, probability matching, and optimization in concurrent ratio schedules. *Journal of the Experimental Analysis of Behavior*, 118(1). https://doi.org/10.1002/jeab.771
- Bouton, M. E. (2004). Context and behavioral processes in extinction. *Learning & Memory*, 11, 485-494. https://doi.org/10.1101/lm.78804
- Kramer, T. J., & Rilling, M. (1970). Differential reinforcement of low rates: A selective critique. *Psychological Bulletin*, *74*(4), 225–254. https://doi.org/10.1037/h0029813
- Mizutani, Y. (2018). OperantKit: A Swift framework for reinforcement schedule simulation [Computer software]. GitHub. https://github.com/YutoMizutani/OperantKit
- Nevin, J. A. (1974). Response strength in multiple schedules. *Journal of the Experimental Analysis of Behavior*, *21*(3), 389–408. https://doi.org/10.1901/jeab.1974.21-389
- Lachter, G. D., Cole, B. K., & Schoenfeld, W. N. (1971). Some temporal parameters of non-contingent reinforcement. *Journal of the Experimental Analysis of Behavior*, *16*(2), 207–217. https://doi.org/10.1901/jeab.1971.16-207
- Lattal, K. A. (1972). Response-reinforcer independence and conventional extinction after fixed-interval and variable-interval schedules. *Journal of the Experimental Analysis of Behavior*, *18*(1), 123–131. https://doi.org/10.1901/jeab.1972.18-123
- Schoenfeld, W. N., & Cole, B. K. (1972). *Stimulus schedules: The t-τ systems*. Harper & Row.
- Zeiler, M. D. (1968). Fixed and variable schedules of response-independent reinforcement. *Journal of the Experimental Analysis of Behavior*, *11*(4), 405–414. https://doi.org/10.1901/jeab.1968.11-405
- Reynolds, G. S. (1961). Behavioral contrast. *Journal of the Experimental Analysis of Behavior*, 4(1), 57-71. https://doi.org/10.1901/jeab.1961.4-57
- Sidman, M. (1953). Two temporal parameters of the maintenance of avoidance behavior by the white rat. *Journal of Comparative and Physiological Psychology*, 46(4), 253-261. https://doi.org/10.1037/h0060730
- Hineline, P. N. (1977). Negative reinforcement and avoidance. In W. K. Honig & J. E. R. Staddon (Eds.), *Handbook of operant behavior* (pp. 364-414). Prentice-Hall.
- de Waard, R. J., Galizio, M., & Baron, A. (1979). Chained schedules of avoidance: Reinforcement within and by avoidance situations. *Journal of the Experimental Analysis of Behavior*, 32(3), 399-407. https://doi.org/10.1901/jeab.1979.32-399
- Page, S., & Neuringer, A. (1985). Variability is an operant. *Journal of Experimental Psychology: Animal Behavior Processes*, 11(3), 429-452. https://doi.org/10.1037/0097-7403.11.3.429
- Neuringer, A. (2002). Operant variability: Evidence, functions, and theory. *Psychonomic Bulletin & Review*, 9(4), 672-705. https://doi.org/10.3758/BF03196324
- Miller, N., & Neuringer, A. (2000). Reinforcing variability in adolescents with autism. *Journal of Applied Behavior Analysis*, 33(2), 151-165. https://doi.org/10.1901/jaba.2000.33-151
- Lee, R., McComas, J. J., & Jawor, J. (2002). The effects of differential and lag reinforcement schedules on varied verbal responding by individuals with autism. *Journal of Applied Behavior Analysis*, 35(4), 391-402. https://doi.org/10.1901/jaba.2002.35-391
- Skinner, B. F. (1948). 'Superstition' in the pigeon. *Journal of Experimental Psychology*, 38(2), 168-172. https://doi.org/10.1037/h0055873
- Denney, J., & Neuringer, A. (1998). Behavioral variability is controlled by discriminative stimuli. *Animal Learning & Behavior*, *26*(2), 154-162. https://doi.org/10.3758/BF03199208
- Neuringer, A., & Jensen, G. (2010). Operant variability and voluntary action. *Psychological Review*, *117*(3), 972-993. https://doi.org/10.1037/a0020364
- Stokes, P. D. (1995). Learned variability. *Animal Learning & Behavior*, *23*(2), 164-176. https://doi.org/10.3758/BF03199931
- Wagner, A. R. (1981). SOP: A model of automatic memory processing in animal behavior. In N. E. Spear & R. R. Miller (Eds.), *Information processing in animals: Memory mechanisms* (pp. 5-47). Erlbaum.

---

## Part III: 実験層 — 多フェーズ合成

### 3.1 動機

Part I と Part II はセッション内の随伴性構造を形式化した: 原子スケジュール、結合子、修飾子、及びそれらの代数的・表示的性質。しかし JEAB の実験手続きは、相変化基準を伴う順序付けされたフェーズ（条件）の列から成る — Method セクションが「ベースライン → 処遇 → 反転」や「条件は以下の順序で提示された...」と記述するセッション間構造である。

これら2つのレベルを統一する既存の形式的表記法は存在しない。Mechner (1959) と State Notation (Snapper, Kadden, & Inglis, 1982) はセッション内の試行構造を形式化する。Cooper, Heron, & Heward (2020) はデザイン構造に A-B-A-B 記法を用いる。実験層はこのギャップを橋渡しする。

### 3.2 フェーズ列は非可換モノイド

**定義 13（フェーズ）。** フェーズは三つ組:

```
Phase = (label : String, meta : PhaseMeta, schedule : ScheduleExpr)
```

ここで `PhaseMeta` はセッション仕様と安定性基準を含む。

**定義 14（フェーズ列）。** フェーズ列はフェーズの順序付き非空リスト:

```
PhaseSequence = Phase⁺
```

**フェーズ列の代数的性質:**

*性質 1（結合則）。* フェーズ列の連結は結合的: `(P₁ ++ P₂) ++ P₃ = P₁ ++ (P₂ ++ P₃)`

*性質 2（非可換性）。* フェーズの順序は重要 — 行動の履歴は不可逆: `[Baseline, Treatment] ≠ [Treatment, Baseline]`。これは実験行動分析の基本的制約: Treatment を Baseline の前に経験した有機体は、Baseline を先に経験した有機体とは異なる行動状態にある (Sidman, 1960, Ch. 4)。

*性質 3（恒等元）。* 空列 `[]` が連結の恒等元。ただし実験は少なくとも1フェーズを必要とする。

**結論:** フェーズ列はフェーズの集合上の*自由モノイド*を形成し、連結が演算である。

### 3.3 Shaping は構文糖衣

**定義 15（Shaping 展開）。** steps 変数 `x = [v₁, ..., vₙ]`、フェーズメタデータ `M`、スケジュールテンプレート `T(x)` を持つ `shaping` 宣言は以下に展開される:

```
⟦shaping(Name, x=[v₁,...,vₙ], M, T(x))⟧ = [Phase(Name_1, M, T(v₁)), ..., Phase(Name_n, M, T(vₙ))]
```

これは `Repeat(n, S)` → `Tand(S, ..., S)` (§2.2.3) のスケジュール層における類似物であり、実験層で動作する。

**非チューリング完全性:** `steps` リストは有限リテラル — ループ・再帰・算術なし。展開はリスト長で有界な純粋マクロ置換。

### 3.4 実験の表示的意味論

**定義 16（実験マシン）。** 実験マシンはフェーズ列をスケジュールマシンの列に写像する:

```
⟦experiment⟧ : PhaseSequence → ScheduleMachine*
⟦[P₁, P₂, ..., Pₙ]⟧ = (⟦P₁.schedule⟧, ⟦P₂.schedule⟧, ..., ⟦Pₙ.schedule⟧)
```

各 `⟦Pᵢ.schedule⟧` は §2.13 で定義された Mealy マシンスケジュールマシン。**合成性:** 実験レベルの意味論は各フェーズのスケジュール意味論が独立であるため自明に合成的。

### 3.5 アノテーション継承

実験レベルのアノテーションは全フェーズに伝播する（§1.6.1 のプログラムレベル LH 伝播と同構造）:

```
R0  Experiment → shared_annotations, phases[1..n]
    ∀i: phases[i].effective_annotations = merge(shared_annotations, phases[i].phase_annotations)
```

### 参考文献（Part III）

- Cooper, J. O., Heron, T. E., & Heward, W. L. (2020). *Applied behavior analysis* (3rd ed.). Pearson.
- Mechner, F. (1959). A notation system for the description of behavioral procedures. *JEAB*, 2(2), 133-150. https://doi.org/10.1901/jeab.1959.2-133
- Sidman, M. (1960). *Tactics of scientific research*. Basic Books.
- Snapper, A. G., Kadden, R. M., & Inglis, G. B. (1982). State notation of behavioral procedures. *Behavior Research Methods*, 14(4), 329-342. https://doi.org/10.3758/BF03203225
