# contingency-dsl

:gb: [English README](README.md)

強化随伴性と Pavlov 型対提示を宣言するための言語非依存な仕様。パラダイム中立な形式的基盤の上で、科学的カテゴリ（operant / respondent / composed）別に構成されている。

## レイヤ構造

| レイヤ | 範囲 | ディレクトリ |
|---|---|---|
| **Foundations** | CFG / LL(2) メタ文法；パラダイム中立な型（随伴性・時間スケール・刺激型付け・価（valence）・文脈） | `spec/*/foundations/`, `schema/foundations/` |
| **Operant** | 三項随伴性（SD-R-SR）；Ferster-Skinner 分類に基づく強化スケジュール（比率 / 間隔 / 時間 / 分化強化 / 複合 / 累進）；嫌悪制御（Sidman 自由オペラント回避・弁別回避・逃避・応答コスト）；状態保持バリアント（Percentile, Adjusting, Interlocking, Admission Gate）；試行ベースバリアント（MTS, Go/NoGo）；反応修飾子（Limited Hold, Timeout, 強化遅延, 内挿スケジュール） | `spec/*/operant/`, `schema/operant/` |
| **Respondent** | 二項随伴性（CS-US）；最小限の Tier A プリミティブ（Pair, Extinction, CSOnly, USOnly, Contingency, TrulyRandom, ExplicitlyUnpaired, Compound, Serial, ITI, Differential）。より深い Pavlov 型手続きは姉妹パッケージ `contingency-respondent-dsl` に収録。 | `spec/*/respondent/`, `schema/respondent/` |
| **Composed** | オペラントとレスポンデントの構成要素を組み合わせる手続き：CER, PIT, オートシェイピング, 省略（omission）, 二過程理論。`PhaseSequence` AST ツリーとしてエンコードされ、operant + respondent プリミティブに composed レイヤのアノテーション `@omission` / `@avoidance`（`schema/annotations/extensions/composed-annotator.schema.json`）を加えて構成される；composed 手続き専用の AST スキーマは存在しない。 | `spec/*/composed/` |
| **Experiment** | 宣言的な多フェーズデザイン；Phase と Context を第一級構成要素として扱う；JEAB スタイルの Subjects / Apparatus アノテーション継承 | `spec/*/experiment/`, `schema/experiment/` |
| **Annotation** | JEAB Method カテゴリ（Subjects / Apparatus / Procedure / Measurement）に沿ったプログラムスコープのメタデータ；拡張は `annotations/extensions/` 配下（例: respondent-annotator, learning-models-annotator） | `spec/*/annotations/`, `schema/annotations/` |

## このパッケージが含むもの

- **`spec/{en,ja}/`** — レイヤ別の形式仕様（理論、文法、プリミティブ、設計根拠）
- **`schema/`** — レイヤ別 EBNF 文法 + AST 用 JSON Schema
- **`conformance/`** — 言語非依存の適合性テストスイート（入力テキスト → 期待される AST JSON）
- **`docs/{en,ja}/`** — ユーザ向けドキュメント（構文ガイド、ユースケース、アノテーション、論文例、ツーリング）
- **`scripts/`** — EBNF → Langium および EBNF → Tree-sitter 変換スクリプト、`dist/` 再生成スクリプト

## このパッケージが含まないもの

- コードは含まない。パーサ実装もランタイム依存も含まない。
- パーサ実装は別パッケージに存在する：
  - **contingency-dsl-py** — Python リファレンスパーサ（唯一のリファレンス実装）
- Tier B の Pavlov 型手続き（高次条件づけ、阻止、隠蔽、潜在制止、更新（renewal）、再生（reinstatement）、条件性弁別（occasion setting）等）は姉妹パッケージ **contingency-respondent-dsl** に存在し、`spec/en/respondent/grammar.md` で定義された Respondent 拡張点に差し込まれる。

## 構文例

### Operant
```
FR5                           -- Fixed Ratio 5
VI60s                         -- Variable Interval 60秒
Chain(FR5, FI30s)             -- Chained: FR5 の後 FI30
Conc(VI30s, VI60s)            -- Concurrent VI30 VI60
Mult(VI30s, VI60s)            -- Multiple schedule（成分を交互に呈示、弁別刺激あり）
Mix(VI30s, VI60s)             -- Mixed schedule（交互だが弁別信号なし）
Conj(FI15s, FR10)             -- Conjunctive: 両方の要件を満たす必要がある
Alt(FR5, VI60s)               -- Alternative: いずれかの要件で充足
FR5(FI30)                     -- 二次スケジュール: FI30 を 5 回完了
let baseline = VI60s          -- 名前付き束縛
DRL5s                         -- 低反応率分化強化
FI30 LH10                     -- Limited Hold: 10秒の利用可能ウィンドウ
FI30 TO(duration=30s)         -- 強化後の Timeout

-- 嫌悪制御
Sidman(SSI=20s, RSI=5s) @punisher("shock", intensity="0.5mA")
                              -- Sidman 自由オペラント回避 (Sidman, 1953)
DiscrimAv(CSUSInterval=10s, ITI=3min, mode=fixed, ShockDuration=0.5s)
                              -- 弁別回避 (Solomon & Wynne, 1953)
DiscrimAv(CSUSInterval=10s, ITI=3min, mode=response_terminated)
                              -- 応答終結モード: 反応がショックを終結させる
@reinforcer("token") VI60s ResponseCost(amount=1)
                              -- 条件性強化子への応答コスト

-- 罰オーバレイ
Overlay(VI60s, FR1) @punisher("shock")
                              -- VI60 ベースラインへの罰オーバレイ
Overlay(Conc(VI30s, VI60s, COD=2s), FR1, target=changeover)
                              -- 変化行動のみへの罰 (Todorov, 1971)
Conc(VI30s, VI60s, COD=2s, PUNISH(1->2)=FR1, PUNISH(2->1)=FR1)
                              -- 方向性のある応答クラス罰
```

### Operant — 状態保持・試行ベース
```
Pctl(IRT, 50)                 -- Percentile スケジュール (Platt, 1973)
Adj(delay, start=10s, step=1s)
                              -- Adjusting スケジュール
Interlock(R0=300, T=10min)    -- Interlocking スケジュール (Berryman & Nevin, 1962)
MTS(comparisons=3, consequence=CRF, ITI=5s)
                              -- 見本合わせ（試行ベース）
GoNoGo(responseWindow=5s, consequence=CRF, ITI=10s)
                              -- Go/NoGo 弁別
```

### Respondent
```
Pair.ForwardDelay(cs=Tone, us=Shock, isi=10s, cs_duration=12s)
Pair.ForwardTrace(cs=Tone, us=Shock, trace_interval=5s)
Pair.Simultaneous(cs=Light, us=Food)
Pair.Backward(us=Shock, cs=Tone, isi=10s)
Contingency(p_us_given_cs=0.8, p_us_given_no_cs=0.2)
TrulyRandom(cs=Tone, us=Shock)           -- Contingency(p, p) の糖衣構文
ExplicitlyUnpaired(cs=Tone, us=Shock, min_separation=30s)
Compound(cs_list=[Tone, Light], mode=Simultaneous)
Serial(cs_list=[Tone, Light], isi=5s)
Differential(cs_positive=Tone, cs_negative=Noise, us=Shock)  -- A+/B− 弁別
Extinction(cs=Tone)
ITI(distribution=exponential, mean=120s)
```

### Composed（operant × respondent）
```
-- CER (Estes & Skinner, 1941): オペラントベースライン + Pavlov 型対提示 + baseline の再利用
@cs(label="Tone", duration=60s, modality="auditory")
@us(label="Shock", intensity="0.5mA", delivery="unsignaled")

phase baseline:
  sessions = 10
  VI60s

phase pairing:
  sessions = 5
  Pair.ForwardDelay(Tone, Shock, isi=60s, cs_duration=60s)

phase test:
  sessions = 3
  use baseline

-- オートシェイピング (Brown & Jenkins, 1968)
@cs(label="KeyLight", duration=8s, modality="visual")
@us(label="Food", delivery="unsignaled")

phase autoshaping_training:
  sessions = 10
  Pair.ForwardDelay(KeyLight, Food, isi=8s, cs_duration=8s)

-- Omission / 負の自動維持 (Williams & Williams, 1969)
@cs(label="KeyLight", duration=6s, modality="visual")
@us(label="Food", delivery="cancelled_on_cs_response")

phase omission_training:
  sessions = 20
  Pair.ForwardDelay(KeyLight, Food, isi=6s, cs_duration=6s) @omission(response="key_peck", during="cs")
```

## ドキュメント

- **[Syntax Guide (EN)](docs/en/syntax-guide.md)** / **[構文ガイド (JA)](docs/ja/syntax-guide.md)** — operant, respondent, composed プリミティブを段階的に解説
- **[Use Cases (EN)](docs/en/use-cases.md)** / **[ユースケース (JA)](docs/ja/use-cases.md)** — 各構成要素で何が可能になるかを引用付きで解説
- **[Annotations (EN)](docs/en/annotations.md)** / **[アノテーション (JA)](docs/ja/annotations.md)** — `@reinforcer`, `@punisher`, `@sd`, `@cs`, `@us`, `@iti`, `@cs_interval`, `@context`, `@species`, `@strain`, `@apparatus`, `@model` を含むメタデータレイヤ
- **[Paper Examples (EN)](docs/en/paper-examples.md)** / **[論文例 (JA)](docs/ja/paper-examples.md)** — CER, オートシェイピング, PIT, omission, 古典的スケジュール研究の DSL エンコーディング
- **[Architecture (EN)](spec/en/architecture.md)** / **[アーキテクチャ (JA)](spec/ja/architecture.md)** — 6 層図、SEI P1/P2/P3、TC / non-TC 境界
- **[Design Philosophy (EN)](spec/en/design-philosophy.md)** / **[設計思想 (JA)](spec/ja/design-philosophy.md)** — 至高目的、各レイヤの根拠、Admission Gate
- **[Operant Grammar (EN)](spec/en/operant/grammar.md)** / **[オペラント文法 (JA)](spec/ja/operant/grammar.md)** — 三項随伴性の生成規則
- **[Respondent Grammar (EN)](spec/en/respondent/grammar.md)** / **[レスポンデント文法 (JA)](spec/ja/respondent/grammar.md)** — Tier A プリミティブ + 拡張点
- **[Foundations Grammar (EN)](spec/en/foundations/grammar.md)** / **[基盤文法 (JA)](spec/ja/foundations/grammar.md)** — パラダイム中立な字句構造
- **[Tooling (EN)](docs/en/tooling.md)** / **[ツーリング (JA)](docs/ja/tooling.md)** — Tree-sitter, Langium LSP, EBNF ローダ順

## 適合性テスト

任意のパーサ実装は `conformance/` 配下の全テストをパスすること：

```bash
# Python リファレンスパーサ
cd ../contingency-dsl-py && pytest tests/test_conformance.py -v
```

テストコーパスはレイヤ別に構成されている：
- `conformance/foundations/` — パラダイム中立な字句テスト（`conformance/foundations/README.md` で定義された厳格なスコーピングルールにより意図的に空）
- `conformance/operant/` — 原子スケジュール、複合コンビネータ（Conc / Alt / Conj / Chain / Tand / Mult / Mix / Overlay / Interpolate）、修飾子（DR*, PR, Lag, Repeat, Limited Hold, Timeout, 強化遅延）、二次スケジュール、嫌悪制御（Sidman, DiscriminatedAvoidance）、応答コスト、代数的等価性、境界値、エラー、警告
- `conformance/operant/stateful/` — Percentile, Adjusting, Interlocking
- `conformance/operant/trial-based/` — MTS, Go/NoGo
- `conformance/respondent/` — Tier A プリミティブのフィクスチャ（Pair, 随伴性統制, 複合刺激, 基本構成）
- `conformance/composed/` — CER（条件性抑制）、PIT、オートシェイピング、omission、二過程回避
- `conformance/experiment/` — phase, progressive-training, shaping
- `conformance/annotations/` — subjects, apparatus, procedure（刺激 / 時間 / 試行構造）、measurement, プログラムレベル；`extensions/respondent-annotator.json`
- `conformance/representations/` — 代替座標系（t-τ）

## `dist/` の再生成

`dist/` ツリー（Langium および Tree-sitter のアーティファクト）は gitignored であり、`schema/*/grammar.ebnf` から再現可能：

```bash
./scripts/gen-langium.sh      # dist/langium/contingency-dsl.langium
./scripts/gen-treesitter.sh   # dist/tree-sitter/grammar.js
```

ローダ順: Foundations → Operant → Operant.Stateful → Operant.TrialBased → Respondent、続いて rglob でソート順に発見された追加の `grammar.ebnf`。

## 参考文献

- Brown, P. L., & Jenkins, H. M. (1968). Auto-shaping of the pigeon's key-peck. *Journal of the Experimental Analysis of Behavior*, 11(1), 1–8. https://doi.org/10.1901/jeab.1968.11-1
- Catania, A. C. (2013). *Learning* (5th ed.). Sloan Publishing.
- Estes, W. K., & Skinner, B. F. (1941). Some quantitative properties of anxiety. *Journal of Experimental Psychology*, 29(5), 390–400. https://doi.org/10.1037/h0062283
- Ferster, C. B., & Skinner, B. F. (1957). *Schedules of reinforcement*. Appleton-Century-Crofts.
- Fleshler, M., & Hoffman, H. S. (1962). A progression for generating variable-interval schedules. *Journal of the Experimental Analysis of Behavior*, 5(4), 529–530. https://doi.org/10.1901/jeab.1962.5-529
- Pavlov, I. P. (1927). *Conditioned reflexes: An investigation of the physiological activity of the cerebral cortex* (G. V. Anrep, Trans.). Oxford University Press.
- Rescorla, R. A. (1967). Pavlovian conditioning and its proper control procedures. *Psychological Review*, 74(1), 71–80. https://doi.org/10.1037/h0024109
- Rescorla, R. A., & Solomon, R. L. (1967). Two-process learning theory. *Psychological Review*, 74(3), 151–182. https://doi.org/10.1037/h0024475
- Skinner, B. F. (1938). *The behavior of organisms*. Appleton-Century.
- Williams, D. R., & Williams, H. (1969). Auto-maintenance in the pigeon: Sustained pecking despite contingent non-reinforcement. *Journal of the Experimental Analysis of Behavior*, 12(4), 511–520. https://doi.org/10.1901/jeab.1969.12-511

