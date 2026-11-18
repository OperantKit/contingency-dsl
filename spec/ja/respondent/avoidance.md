# 回避 (レスポンデントの語彙)

> contingency-dsl レスポンデント層の一部。レスポンデントの語彙では、回避手続きは前方の CS–US 対提示に反応→刺激の依存を 1 つ足したものである: CS 中の反応が、その試行の US を取りやめるか先送りする。`@avoidance` は、中立の反応→刺激の依存の取りやめ・先送りの形への、レスポンデントの層の別名である ([レスポンデント理論 §0](theory.md))。

**関連文書:**
- [省略手続き](omission.md) — レスポンデントの層のもう 1 つの反応→刺激の依存 (`@omission`)。
- [composed-annotator](../annotations/extensions/composed-annotator.md) — `@avoidance` とそのパラメータの定義。
- [オペラント理論 §2.9](../operant/theory.md) — 同じ種類の手続きをオペラントの語彙 (`DiscriminatedAvoidance`) で書いたもの。
- [2 過程理論](../composed/two-process-theory.md) — オペラントの層とレスポンデントの層にまたがる解釈の枠組み。その適合テストの fixture は、オペラントの phase とこの符号化を組み合わせる。

---

## 1. 手続き

警告刺激 (CS) が呈示され、前方の対提示と同じく、その offset に嫌悪的な US が続く。CS 中に被験体が指定の反応を出すと、その試行の US は取りやめられる (`mode="cancel"`、既定) か、CS の offset / US の onset が先送りされる (`mode="postpone"`)。

## 2. DSL 符号化

```
@cs(label="tone", duration=5-s, modality="auditory")
@us(label="shock", intensity="0.8mA")

phase avoidance_training:
  sessions = 20
  Pair.ForwardDelay(tone, shock, isi=5-s, cs_duration=5-s) @avoidance(response="lever_press", mode="cancel")
```

対提示そのものは変わらない。アナライザ／実行器のパスが注釈を解釈する。1 つのレスポンデント・プリミティブに付けられる `@omission` / `@avoidance` は高々 1 つである (composed-annotator §4)。

## 3. 2 つの語彙

オペラントの層は、回避を自分のプリミティブ (`DiscriminatedAvoidance`・`Sidman`) で書く。この文書は、特定の `DiscriminatedAvoidance` のプログラムと上の符号化が、同じ反応の列に対して同じ刺激の列を出すとは述べない。それは実行のテストで確かめていない。

## 4. 引用

- Solomon, R. L., & Wynne, L. C. (1954). Traumatic avoidance learning: The principles of anxiety conservation and partial irreversibility. *Psychological Review*, 61(6), 353–385. https://doi.org/10.1037/h0054540
