# 省略手続き (Negative Automaintenance)

> contingency-dsl 合成層の一部。省略手続きでは、自動形成と同様に前方パヴロフ型対提示が計画され、CS 中のいかなる反応もその試行で予定されていた US を **キャンセル** する追加制約が課される。この手続きの下で維持される反応を理論の層がどう読むかは [レスポンデント理論 §6](../respondent/theory.md) と [オペラント理論の「解釈の注記」](../operant/theory.md) にある。

**関連文書:**
- [自動形成](autoshaping.md) — 反応→US キャンセル項を除いた同じ手続き。
- [2 過程理論](two-process-theory.md) — オペラントの層とレスポンデントの層にまたがる解釈の枠組み。
- [レスポンデント・プリミティブ](../respondent/primitives.md) — 根底にある配置としての `Pair.ForwardDelay`。
- [オペラント・スケジュール](../operant/schedules/differential.md) — 関連するオペラント省略スケジュール (DRO)。

---

## 1. 手続き

Williams and Williams (1969) は修正自動形成手続きでハトを訓練した: キー光 (CS) は固定持続呈示され、穀物 (US) が標準自動形成と同様に続く。**ただし**、CS 呈示中のキー突きはその試行の US を即座にキャンセルする。

ハトは多くのセッションにわたってキー光を実質的な率で突き続け、その試行の US は取りやめられた。Williams and Williams (1969) はこの効果を「negative automaintenance」と呼んだ — auto-maintained 反応が負の反応-結果の依存の下で持続した。

## 2. 解釈

この手続きの文書は、配置と §1 の観察だけを記す。持続性についてのレスポンデントの伝統の読みは [レスポンデント理論 §6](../respondent/theory.md) にある。オペラントの層は、その側の読みを書く場所を [オペラント理論の「解釈の注記」](../operant/theory.md) に空けている。

## 3. 自動形成との関係

省略は自動形成 (`autoshaping.md`) の構造的修正である: 同じ CS、同じ US、同じ前方パヴロフ型配置に、**反応→刺激の依存** が 1 つ加えられる (CS 中の反応がその試行の US を取りやめる)。

省略における反応-US 関係は **負の随伴性** である: 反応は US の確率を減らす。これは罰 (反応に随伴して嫌悪的 US を加える) とも、他行動分化強化 (DRO、標的反応が指定持続不在でない限り強化子を保留するオペラント配置) とも構造的に異なる。

## 4. DSL 符号化

省略随伴性は、根底にあるパヴロフ型対提示に付与される `@omission` アノテーションとして表現される。当該アノテーションには、反応の同定情報と、反応が US をキャンセルする時間窓を記録する。最小の符号化:

```
@cs(label="key_light", duration=6-s, modality="visual")
@us(label="grain", delivery="cancelled_on_cs_response")

phase omission_training:
  sessions = 20
  Pair.ForwardDelay(key_light, grain, isi=6-s, cs_duration=6-s) @omission(response="key_peck", during="cs")
```

`@omission` アノテーションのパラメータ:

- `response` — その試行で予定された US をキャンセルする、観察可能な反応クラス。
- `during` — キャンセル規則が適用される呈示窓。`"cs"` (CS 呈示中、標準的な事例) がデフォルト。

アナライザ／実行器のパスがアノテーションを解釈する。指定された窓内で該当反応が出現するたびに、その試行の US 呈示が抑制される。パヴロフ型配置自体は変更されない。したがって AST は Tier A レスポンデント・プリミティブおよびその他の合成層アノテーションと整合的に合成される。

## 5. 分類体系内の位置づけ

省略の随伴性構造は、反応→US キャンセル項を除いて自動形成と同一である。その 1 項が計画された配置を変えるので、省略は暗黙にするのではなく命名された手続きとして文書化される。

## 6. 引用

- Williams, D. R., & Williams, H. (1969). Auto-maintenance in the pigeon: Sustained pecking despite contingent non-reinforcement. *Journal of the Experimental Analysis of Behavior*, 12(4), 511–520. https://doi.org/10.1901/jeab.1969.12-511
