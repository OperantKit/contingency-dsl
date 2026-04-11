# 強化スケジュールの代数的型体系

## 概要

本文書は、強化スケジュールの分類体系を代数的型体系として形式化し、contingency-dsl ドメイン固有言語の理論的基盤を提供する。全ての単純強化スケジュールが2つの独立次元 — 分布（Distribution）と領域（Domain）— の直積として表現できることを示し、3×3 の原子スケジュール格子を導出する。7つの結合子（Concurrent, Alternative, Conjunctive, Chained, Tandem, Multiple, Mixed）による合成代数を定義し、可換性・結合性・単位元・零化元を含む代数的性質を形式的に特徴づける。

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

行動的含意: 比率スケジュールは高く安定した反応率と特徴的な強化後休止（PRP）を生成する（Ferster & Skinner, 1957, Ch. 3-4）。間隔スケジュールはスキャロップまたは break-and-run パターンを生み、最低限の閾値を超える反応率には非感受的である（Ferster & Skinner, 1957, Ch. 5-6）。時間スケジュールは迷信的強化（Skinner, 1948）または適切なパラメータ化の下でオペラントスケジュールの近似（Schoenfeld & Cole, 1972）として行動を維持する。

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

**差異強化（DR）スケジュール** は反応数や経過時間ではなく、反応間時間（IRT: inter-response time）の時間的性質に基づいて強化を制約する*制約スケジュール*である。

```
DRConstraint ::= DRL(irt_min : ℝ⁺)       -- IRT ≥ 閾値
               | DRH(irt_max : ℝ⁺)       -- IRT ≤ 閾値
               | DRO(omission_time : ℝ⁺)  -- 一定時間反応なし
```

DR スケジュールは格子と直交する位置にあり、格子スケジュールと tandem または conjunctive 合成で組み合わせ可能な**フィルタ**または**修飾子**として理解すべきである。例: `Tand(VR20, DRL5s)` は変動比率の反応要件*かつ* IRT ≥ 5 秒を要求する。

**DRA/DRI に関する注記。** 代替行動の差異強化（DRA）および両立不能行動の差異強化（DRI）は、応用行動分析で広く使用される臨床手続きの名称である（Cooper, Heron, & Heward, 2020）。DRO/DRL/DRH が時間パラメータで定義される単一オペランダムのスケジュール修飾子であるのに対し、DRA/DRI は本質的に*2つの*反応クラスにまたがる随伴性（標的行動の消去 + 代替行動の強化）を記述する。スケジュール水準では、DRA は並行配置として表現可能である:

```
let dra = Conc(EXT, CRF)           -- または Conc(EXT, FR1), Conc(EXT, VI30) 等
```

DRI は代替行動が標的行動と物理的に両立不能な DRA の特殊ケースであり、スケジュール構造は同一である。両者の差異はトポグラフィー上のもの（どの行動を代替として選択するか）であり、手続き上の差異ではない。したがって DRA/DRI は DSL プリミティブではなく、既存結合子を用いたドキュメント化されたパターンとして扱う。臨床メタデータ（行動機能、代替行動の記述）は注釈拡張レイヤー（§5 参照）に委譲される。

**累進比率（PR）** は*メタスケジュール*である: 提示された強化の数によりインデックスされた決定論的ステップ関数に従ってパラメータが変化する比率スケジュール。

```
PR(step : ℕ → ℕ) = FR(step(n))  ここで n は各強化後にインクリメント
```

PR は*スケジュール関手*であり、ステップ関数を FR スケジュールの系列にマッピングする。DSL ではステップ関数を列挙集合（`hodos`, `linear`, `exponential`）に限定し、決定可能性を保持する。任意のステップ関数は Python API レベルでのみ利用可能。

### 1.5 行動理論との対応

2次元型体系は以下の正典的出典に直接マッピングされる:

| 出典 | カバレッジ |
|------|-----------|
| Ferster & Skinner (1957) | FR, VR, FI, VI（第3-6章）; CRF, EXT を境界条件として |
| Catania (2013) | Time（反応非依存）次元の拡張 |
| Farmer (1963) | Random スケジュール（RR, RI, RT）の形式化 — 単位あたり等確率仮定 |
| Fleshler & Hoffman (1962) | Variable スケジュールの値生成アルゴリズム |
| Schoenfeld & Cole (1972) | 同一行動空間の代替座標系としての T-tau 体系（[representations.md](representations.md) 参照） |

---

### 1.6 Limited Hold — 時間的利用可能性制約

**Limited Hold（LH）** は、強化機会の *時間的利用可能性* を制限する修飾子である。内部スケジュールが要件を充足した時点で強化窓が開き、`hold_duration` 秒以内に反応が生じれば強化が成立する。窓が期限切れになると強化機会は消失し、内部スケジュールはリセットされる。

**形式的定義。** スケジュール `S` および `hold_duration h > 0` が与えられたとき:

```
LH(h, S) において:
  - t_open  = S が充足された時刻
  - t_resp  = t_open 以降の最初の反応の時刻
  - 強化成立 iff t_resp - t_open ≤ h
  - t_resp - t_open > h ならば: 強化機会消失、S.next() 呼び出し（リセット）
```

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

- `LH(∞, S) = S`（制限なし = 元のスケジュール）
- `LH(0, S) = EXT`（即時期限切れ = 消去）
- `LH` は連言（Conj）に還元不可: `Conj` は無状態の同時充足チェックであり、充足イベントにゲートされた状態付き時間窓を表現できない
- `LH` は T-tau と非同一: T-tau は固定周期クロック駆動、LH は充足イベントトリガー。詳細は [representations.md](representations.md) 参照

**適用範囲:**

| 内部スケジュール | 用途 |
|---|---|
| FI, VI | 正典的用法（Ferster & Skinner, 1957, Ch.5） |
| FT, VT | 反応非依存 → 反応依存変換 |
| DRL | 文献に記録あり（Kramer & Rilling, 1970） |
| DRO | 臨床応用（問題行動ゼロ後の反応窓） |
| FR, VR | 意味論的に問題あり（充足反応 = 窓内反応）— v1.0 パーサで警告 |

**参考文献:** Ferster, C. B., & Skinner, B. F. (1957). *Schedules of reinforcement*. Appleton-Century-Crofts. (Ch. 5); Kramer, T. J., & Rilling, M. (1970). Differential reinforcement of low rates: A selective critique. *Psychological Bulletin, 74*(4), 225–254. https://doi.org/10.1037/h0029813


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

**定理 1（可換性）.**
- `Conc(A, B) = Conc(B, A)` — 操作体の割り当ては任意（ラベリングを除く）。
- `Alt(A, B) = Alt(B, A)` — 選言は可換。
- `Conj(A, B) = Conj(B, A)` — 連言は可換。
- `Chain(A, B) ≠ Chain(B, A)` — 逐次順序は重要。
- `Tand(A, B) ≠ Tand(B, A)` — 逐次順序は重要。
- `Mult(A, B) ≠ Mult(B, A)` — 交替順序は重要。
- `Mix(A, B) ≠ Mix(B, A)` — 交替順序は重要。

**定理 2（結合性）.** 全7結合子は N 項合成に平坦化可能な意味で結合的である:
- `Conc(A, Conc(B, C)) ≡ Conc(A, B, C)`
- `Alt(A, Alt(B, C)) ≡ Alt(A, B, C)`
- `Chain(A, Chain(B, C)) ≡ Chain(A, B, C)`
- 他の結合子も同様。

**定理 3（単位元）.**
- `Alt(S, EXT) = S` — EXT は Alt の単位元（充足されない要素との選言は S のみ）。
- `Conj(S, CRF) = S` — CRF（最初の反応で必ず充足）は Conj の単位元。
- `Chain(CRF, S) = S` — CRF を初期リンクとすると即座に充足される。

**定理 4（零化元）.**
- `Conj(S, EXT) = EXT` — EXT が充足されなければ連言全体が充足されない。
- `Alt(S, CRF) = CRF` — CRF は必ず最初に充足される。

**非分配性.** 一般に、複合スケジュール合成は分配しない:

```
Alt(A, Conj(B, C)) ≢ Conj(Alt(A, B), Alt(A, C))
```

これは意味的に重要であり、括弧が随伴性構造を決定するため、DSL では括弧を明示しなければならない。

### 2.3 再帰的合成

型体系は任意にネストされた合成を支持する:

```
Schedule = AtomicSchedule | CompoundSchedule | ModifierSchedule
CompoundSchedule = Combinator(Schedule, Schedule, ...)
```

これは標準的な再帰的代数的データ型（ADT）である。例:

```
Conc(Chain(FR5, VI60), Alt(FR10, FT30))
```

は、操作体 1 が連鎖 FR5-次に-VI60 を提示し、操作体 2 が選択 FR10-または-FT30 を提示する並行スケジュールである。

### 2.4 切替遅延（COD）と切替反応（COR）

切替遅延（COD: Changeover Delay）は、操作体の切替後に新しい操作体での強化を一定時間抑制するパラメータである（Catania, 1966）。COD は `Conc` の**定義的パラメータ**であり、省略可能なメタデータではない:

- COD なしの並行スケジュールは手続き的に特定されない（Herrnstein, 1961）。DSL はリンター警告（`MISSING_COD`）を発し、明示的な COD 指定を推奨する。ランタイムデフォルトは `COD=0s`。
- `COD=0s` は合法（明示的ゼロ遅延）で、Shull & Pliskoff (1967) の統制条件に対応するが、VI-VI 配置では lint 警告を出すべきである。

```
Conc(VI30s, VI60s, COD=2s)           -- 2秒の切替遅延
Conc(VI30s, VI60s, COD=0s)           -- 明示的ゼロ遅延（統制条件）
```

**デフォルト動作:** 対称（切替方向によらず同一の遅延）、非リセット（COD 中の再切替でタイマーが再起動しない）。

**切替反応（COR: Changeover Response）:** 時間ベースの COD に代わる反応ベースの要件。COR は切替後、新しい操作体で N 回反応するまで強化を抑制する（Findley, 1958）。COD と COR は共存可能:

```
Conc(VI30s, VI60s, COR=5)            -- 切替後 5 反応が必要
Conc(VI30s, VI60s, COD=2s, COR=5)   -- 時間と反応の両方の要件
```

| パラメータ | エイリアス | 次元 | 参考文献 |
|-----------|-----------|------|---------|
| COD | ChangeoverDelay | 時間 (s/ms/min) | Catania (1966) |
| COR | ChangeoverResponse | 反応数 (dimensionless) | Findley (1958) |

COD と COR はいずれも `param_decl` によるプログラムレベルのデフォルトをサポートする（`LH = 10s` と同様）:

```
COD = 2s                              -- このプログラム内の全 Conc に適用
Conc(VI30s, VI60s)                    -- COD=2s を継承
Conc(VI30s, VI60s, COD=5s)           -- 式レベルがプログラムレベルを上書き
```

**将来（v1.2）:** 非対称 COD（切替方向ごとに異なる値）とリセット型 COD をコンポーネントラベルで表現。

### 2.5 ブラックアウト（BO）

ブラックアウト（BO: Blackout）は、**多重スケジュール（Multiple）** および **混合スケジュール（Mixed）** の成分間に挿入される、応答非随伴的な暗室期間を指定する。COD（応答随伴的、Conc 固有）と異なり、BO はいかなる応答にも随伴せず、成分間の行動的独立性を確保するための方法論的統制として機能する。

**設計根拠。** BO は行動的コントラスト（behavioral contrast; Reynolds, 1961）に直接影響する。BO 期間が長いほど成分間相互作用が減少し、各成分の弁別制御がより純粋になる。連合学習的には、BO の持続時間が先行成分の刺激表象の減衰に十分かどうかが、成分間の般化を規定する（Bouton, 2004; Wagner, 1981）。これにより BO は Mult/Mix の**構造的パラメータ**であり、単なるセッションメタデータではない — COD の Conc における役割と構造的に対称である。

```
Mult(FR5, EXT, BO=5s)               -- 成分間に5秒のブラックアウト
Mix(VI30s, VI60s, BO=3s)            -- 3秒のブラックアウト（無弁別）
Mult(FR5, EXT)                       -- ブラックアウトなし（即時遷移）
```

**デフォルト動作:** BO は省略可能（COD と異なる）。省略時または `BO=0s` は、ブラックアウトなし（即時成分切り替え）を意味する。対称的（全遷移で同一の持続時間）。

**将来（v1.2）:** 非対称 BO（遷移方向ごとに異なる値。例: Rich→Lean vs. Lean→Rich）。非対称 COD（Issue #25）と同期して設計。

**タイムアウト（TO）との関係。** BO は応答非随伴的、TO は応答随伴的。TO は負の罰（応答に随伴する正の強化からの除去）として機能し、v2.0 で modifier として導入予定。操作的区別と COD/TO/DRO の構造的関係については Issue #28 を参照。

### 2.6 選択行動と手続き–帰結の境界

並行 VR-VR スケジュールは、並行 VI-VI スケジュールとは質的に異なる選択行動を産出する。並行 VI-VI では、被験体は相対的な強化率に比例して反応を配分する——**マッチング法則**（Herrnstein, 1961）。並行 VR-VR では、被験体はより豊かな選択肢にほぼ全ての反応を集中させる——**排他的選択**（exclusive choice; Herrnstein & Loveland, 1975; Baum, Aparicio, & Alonso-Alvarez, 2022）。

**設計判断:** DSL はこの区別を符号化**しない**。`Conc` は構成スケジュールの型（VI/VR/FI/FR 等）に依らず、単一の汎用結合子のままである。これは意図的な設計であり、以下のアーキテクチャ原則を反映している:

> **DSL は手続き（procedure）——実験者が設定するもの——を記述する。行動的帰結（effect）——被験体がどう振る舞うか——を予測するものではない。**

その根拠:

1. **手続きの完備性。** `Conc(VR20, VR40, COD=2s)` は操作的随伴性を完全に記述している: 2つの比率スケジュールが同時に利用可能で、2秒の切替遅延を伴う。整形式の手続き記述にこれ以上のパラメータは不要である。

2. **帰結の経験的条件依存性。** 排他的選択が実際に生じるかどうかは、DSL が既に捉えているパラメータ（比率値、COD、COR）だけでなく、DSL のスコープ外の要因（訓練履歴、セッション時間、種）にも依存する。`choice_mode = "exclusive"` を DSL に焼き込むことは、経験的な一般化を手続きの論理的帰結として主張することになる。そうではない。

3. **メカニズムからの導出可能性。** VI-VI と VR-VR の差異は分子的随伴性構造に由来する: VI スケジュールはより長い反応間時間（IRT）を差異強化するが、VR スケジュールでは強化が IRT に依存しない。これにより、VI では切替が有益（未収集の強化子が他方の選択肢に蓄積する）だが VR ではそうでない。構成スケジュールの型は既に DSL 式に符号化されているため、下流の分析レイヤーが冗長なアノテーションなしに予測される選択パターンを導出できる。

**選択分析の所在:** 選択配分（choice allocation）、排他的選択の検出、選択モードの分類は **session-analyzer** レイヤーの責務であり、観察された行動データに基づいて動作する:

| 概念 | レイヤー | 根拠 |
|------|---------|------|
| スケジュール構造（`Conc(VR20, VR40, COD=2s)`） | DSL | 手続き記述 |
| 強化ゲーティング（COD 抑制、比率カウント） | ランタイム（`contingency-py`） | 随伴性の執行 |
| 選択配分、マッチングパラメータ、排他的選択の検出 | session-analyzer | 行動的測定と分類 |

この三層分離により、DSL は随伴性の正確な表記法として保たれ、ランタイムはその随伴性を忠実に実行し、分析器は手続き記述を汚染することなく行動的帰結を特徴づける。

---

## 参考文献

- Catania, A. C. (2013). *Learning* (5th ed.). Sloan Publishing.
- Farmer, J. (1963). Properties of behavior under random interval reinforcement schedules. *Journal of the Experimental Analysis of Behavior*, 6(4), 607-616. https://doi.org/10.1901/jeab.1963.6-607
- Ferster, C. B., & Skinner, B. F. (1957). *Schedules of reinforcement*. Appleton-Century-Crofts.
- Findley, J. D. (1958). Preference and switching under concurrent scheduling. *Journal of the Experimental Analysis of Behavior*, 1(2), 123-144. https://doi.org/10.1901/jeab.1958.1-123
- Fleshler, M., & Hoffman, H. S. (1962). A progression for generating variable-interval schedules. *Journal of the Experimental Analysis of Behavior*, 5(4), 529-530. https://doi.org/10.1901/jeab.1962.5-529
- Herrnstein, R. J. (1961). Relative and absolute strength of response as a function of frequency of reinforcement. *Journal of the Experimental Analysis of Behavior*, 4(3), 267-272. https://doi.org/10.1901/jeab.1961.4-267
- Herrnstein, R. J., & Loveland, D. H. (1975). Maximizing and matching on concurrent ratio schedules. *Journal of the Experimental Analysis of Behavior*, 24(1), 107-116. https://doi.org/10.1901/jeab.1975.24-107
- Azrin, N. H., & Holz, W. C. (1966). Punishment. In W. K. Honig (Ed.), *Operant behavior: Areas of research and application* (pp. 380-447). Appleton-Century-Crofts.
- Baum, W. M., Aparicio, C. F., & Alonso-Alvarez, B. (2022). Rate matching, probability matching, and optimization in concurrent ratio schedules. *Journal of the Experimental Analysis of Behavior*, 118(1). https://doi.org/10.1002/jeab.771
- Bouton, M. E. (2004). Context and behavioral processes in extinction. *Learning & Memory*, 11, 485-494. https://doi.org/10.1101/lm.78804
- Kramer, T. J., & Rilling, M. (1970). Differential reinforcement of low rates: A selective critique. *Psychological Bulletin*, *74*(4), 225–254. https://doi.org/10.1037/h0029813
- Mizutani, Y. (2018). OperantKit: A Swift framework for reinforcement schedule simulation [Computer software]. GitHub. https://github.com/YutoMizutani/OperantKit
- Nevin, J. A. (1974). Response strength in multiple schedules. *Journal of the Experimental Analysis of Behavior*, *21*(3), 389–408. https://doi.org/10.1901/jeab.1974.21-389
- Schoenfeld, W. N., & Cole, B. K. (1972). *Stimulus schedules: The t-τ systems*. Harper & Row.
- Reynolds, G. S. (1961). Behavioral contrast. *Journal of the Experimental Analysis of Behavior*, 4(1), 57-71. https://doi.org/10.1901/jeab.1961.4-57
- Skinner, B. F. (1948). 'Superstition' in the pigeon. *Journal of Experimental Psychology*, 38(2), 168-172. https://doi.org/10.1037/h0055873
- Wagner, A. R. (1981). SOP: A model of automatic memory processing in animal behavior. In N. E. Spear & R. R. Miller (Eds.), *Information processing in animals: Memory mechanisms* (pp. 5-47). Erlbaum.
