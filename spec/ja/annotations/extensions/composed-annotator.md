# composed-annotator

> 合成層のための注釈拡張。`@omission` と `@avoidance` —— CER, PIT,
> autoshaping, omission, two-process-theory の各手続きを純粋な
> Pavlovian 配置と区別する、応答随伴的な US 変調規則の 2 つ —— を定義する。

**カテゴリ.** Procedure（応答随伴的な US 規則）。

**関連ドキュメント.**
- [respondent-annotator](respondent-annotator.md) —— 合成手続きが
  基盤とする `@cs` / `@us` / `@iti` / `@cs_interval` メタデータ。
- [composed/omission.md](../../composed/omission.md) —— `@omission`
  の正準用例である負の自動維持（negative automaintenance）。
- [composed/two-process-theory.md](../../composed/two-process-theory.md)
  —— `@avoidance` の理論的枠組み。

---

## 1. 設計

contingency-dsl の合成手続きは、Pavlovian プリミティブ（通常
`Pair.ForwardDelay`）を実験層のフェーズブロック内に置くことで表現される。
構造的配置（CS, US, ISI, 試行数, フェーズ基準, 共有 `@cs` / `@us`
メタデータ）は Tier A / 実験層 AST ですでに完結している。

残るのは —— そして `composed-annotator` が供給するのは —— **執行時の
変調規則** である。指定の応答クラスが呈示窓内で発生した場合に、当該試行の
US スケジュールを変更する。omission 手続きは US をキャンセルし、
avoidance 手続きはキャンセルまたは延期する。両規則とも declarative で、
応答と窓を名指しし、解析器 / 実行器 pass が規則を解釈する。

---

## 2. `@omission(response, during?)`

### 操作的定義

`response` が `during` 窓内で発生した場合、当該試行の US スケジュールは
キャンセルされる。Pavlovian 対提示はそれ以外通常通り進行する: CS は
点灯し、予定された offset で消灯し、（窓内で応答が発生しなければ）
US が呈示される。

### パラメータ

- `response` *（文字列、必須）* —— US をキャンセルする応答クラス。
  通常は `@operandum` で宣言したキーつつき / レバー押し identifier
  と一致する。
- `during` *（文字列、任意、既定 `"cs"`、`{"cs", "iti", "trial"}` のいずれか）*
  —— キャンセル規則が適用される時間窓。

### 例

```
@cs(label="key_light", duration=6s, modality="visual")
@us(label="grain", delivery="cancelled_on_cs_response")

phase omission_training:
  sessions = 20
  Pair.ForwardDelay(key_light, grain, isi=6s, cs_duration=6s) @omission(response="key_peck", during="cs")
```

### 引用

Williams, D. R., & Williams, H. (1969). Auto-maintenance in the pigeon:
Sustained pecking despite contingent non-reinforcement. *Journal of the
Experimental Analysis of Behavior*, 12(4), 511–520.
https://doi.org/10.1901/jeab.1969.12-511

---

## 3. `@avoidance(response, mode?)`

### 操作的定義

`response` が CS 中に発生した場合、当該試行の US をキャンセル（既定の
`mode="cancel"`）するか、CS offset / US onset を延期（`mode="postpone"`）する。

### パラメータ

- `response` *（文字列、必須）* —— US を阻止する応答クラス。
- `mode` *（文字列、任意、既定 `"cancel"`、`{"cancel", "postpone"}` のいずれか）*
  —— 回避様式。

### 例

```
@cs(label="tone", duration=5s, modality="auditory")
@us(label="shock", intensity="0.8mA")

phase avoidance_training:
  sessions = 20
  Pair.ForwardDelay(tone, shock, isi=5s, cs_duration=5s) @avoidance(response="lever_press", mode="cancel")
```

### 引用

Solomon, R. L., & Wynne, L. C. (1954). Traumatic avoidance learning:
The principles of anxiety conservation and partial irreversibility.
*Psychological Review*, 61(6), 353–385.
https://doi.org/10.1037/h0054540

---

## 4. 合成規則

いずれのキーワードもスケジュール水準で attach され（respondent プリミティブに
postfix）、プリミティブを包む `AnnotatedSchedule` ノードに格納される。
単一の respondent プリミティブには `@omission` / `@avoidance` のいずれか
1 つのみを付与できる: 執行意味論が衝突するためである（キャンセル vs.
キャンセルまたは延期）。両方を同時に必要とするプログラムは、別フェーズに
分解すること。

---

## 5. 参照実装

Python 参照実装は `contingency_dsl.annotations.composed` パッケージ内の
`ComposedExtension` クラスに存在する。`contingency_dsl.extensions` の
`ExtensionModule` プロトコルに準拠し、各注釈の必須 / 列挙パラメータに
対する意味論的検証を提供し、`PhaseSequence` または `Program` AST を
走査して型付き `OmissionAnnotation` / `AvoidanceAnnotation` インスタンスを
返す `extract()` 関数を備える。
