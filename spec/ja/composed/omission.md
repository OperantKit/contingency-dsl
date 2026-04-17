# 省略手続き（Negative Automaintenance）

> contingency-dsl 合成層（Ψ）の一部。省略手続きは診断的手続きである: 自動形成と同様に前方パヴロフ型対提示が計画されるが、CS 中のいかなる反応もその試行で予定されていた US を **キャンセル** する追加制約が課される。省略は自動形成反応のパヴロフ型統制とオペラント統制を分離する: 反応が本質的にオペラントであれば、省略随伴性は素早くそれを消去する。反応がパヴロフ型であれば、省略にもかかわらずしばしば持続する。

**関連文書:**
- [自動形成](autoshaping.md) — 省略が診断的に分岐する元の手続き。
- [2 過程理論](two-process-theory.md) — 診断的区別を動機づける理論枠組み。
- [レスポンデント・プリミティブ](../respondent/primitives.md) — 根底にある配置としての `Pair.ForwardDelay`。
- [オペラント・スケジュール](../operant/schedules/differential.md) — 関連するオペラント省略スケジュール（DRO）。

---

## 1. 手続き

Williams and Williams (1969) は修正自動形成手続きでハトを訓練した: キー光（CS）は固定持続呈示され、穀物（US）が標準自動形成と同様に続く。**ただし**、CS 呈示中のキー突きはその試行の US を即座にキャンセルする。純粋にオペラントな説明の下では、突き行動はもはや餌を生成しないため消去するはずである。実際、突きは今や餌を *防ぐ* オペラントである。

この予測に反して、ハトは多くのセッションにわたってキー光を実質的な率で突き続け、試行を重ねるごとに強化を失った。Williams and Williams (1969) はこの効果を「negative automaintenance」と呼んだ — auto-maintained 反応が負の反応-結果随伴性の下で持続した。この持続性は自動形成突き行動の単純なオペラント説明と両立しない。

## 2. 診断的機能

省略手続きは、自動形成反応の統制の所在に対して **診断的** である。

- 自動形成が起源においてオペラントであれば、省略随伴性の下で突きは消去するはずである（突きは今や強化を減らすから）。
- 自動形成が起源においてパヴロフ型であれば、突きは持続するはずである。US が断続的に失われても、パヴロフ型 CS–US 随伴性が依然として反応を誘発するからである。

Williams and Williams (1969) が観察した持続性は、自動形成のパヴロフ型統制説明を支持する標準的な経験的論拠である。

## 3. 自動形成との関係

省略は自動形成（`autoshaping.md`）の構造的修正である: 同じ CS、同じ US、同じ前方パヴロフ型配置に、**追加のオペラント制約** が加えられる（CS 中の反応 → その試行で US キャンセル）。この修正は、本来ならば純粋なパヴロフ型手続きであったものにオペラント構成要素を導入する。これが、省略がレスポンデント層ではなく合成層に属する理由である。

省略における反応-US 関係は **負の随伴性** である: 反応は US の確率を減らす。これは罰（反応に随伴して嫌悪的 US を加える）とも、他行動分化強化（DRO、標的反応が指定持続不在でない限り強化子を保留するオペラント配置）とも構造的に異なる。

## 4. DSL 符号化

省略随伴性は `PUNISH(...)` 指示子を加える、あるいは反応時に予定 US をキャンセルするオペラント制約を用いることで表現される。最小の符号化:

```
Phase(
  name = "omission_training",
  respondent = Pair.ForwardDelay(key_light, food, isi=8-s, cs_duration=8-s),
  operant_constraint = Overlay(EXT, cancel_us_on_response=true),
  criterion = FixedSessions(n=10)
)
@cs(label="key_light", duration=8-s, modality="visual")
@us(label="food", intensity="3s_access", delivery="cancelled_on_cs_response")
```

`operant_constraint` フィールド（実験層フェーズ仕様の一部）は、CS 中の反応が予定 US をキャンセルする随伴性を表現する。プログラムは特定のオペラント・コンビネータや専用の省略指示子を介してこれを符号化してよい。DSL 文法は、意味論的結果（CS-反応 → その試行の US 省略）が明確であれば、いずれの符号化も許容する。

## 5. 分類体系内の位置づけ

省略は、理論的に新規ではなく **診断的** な手続きが合成層に位置を得る唯一最も明確な事例である。その随伴性構造は反応→US キャンセル項を除いて自動形成と同一である。その小さな構造的追加は、維持される反応の解釈にとって決定的である。そのため、省略は暗黙にするのではなく命名された手続きとして文書化される。

## 6. 引用

- Williams, D. R., & Williams, H. (1969). Auto-maintenance in the pigeon: Sustained pecking despite contingent non-reinforcement. *Journal of the Experimental Analysis of Behavior*, 12(4), 511–520. https://doi.org/10.1901/jeab.1969.12-511
