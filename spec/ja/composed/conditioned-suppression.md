# 条件性抑制（CER）

> contingency-dsl 合成層の一部。条件性情動反応（CER）手続きは、オペラントの食欲性ベースラインとパヴロフ型嫌悪的オーバーレイを組み合わせる。CS 呈示中のオペラント・ベースラインの条件性抑制が主要な従属測度である。

**関連文書:**
- [2 過程理論](two-process-theory.md) — 合成手続きを動機づける Rescorla–Solomon (1967) の枠組み。
- [オペラント文法](../operant/grammar.md) — オペラント・ベースライン産出規則。
- [レスポンデント文法](../respondent/grammar.md) — パヴロフ型オーバーレイの産出規則。
- [実験 / フェーズ列](../experiment/phase-sequence.md) — 多相合成。

---

## 1. 手続き

Estes and Skinner (1941) は CER 手続きを導入した。被験体はまずオペラント食欲性スケジュール（典型的には安定したベースライン反応率を維持する変動時隔スケジュール）で訓練される。ベースライン安定後、パヴロフ型前方遅延対提示が重畳される: CS（例: 音）が固定持続呈示され、嫌悪的 US（例: 非信号化された短時間電撃）で終わる。US は **被験体の反応から独立して** 呈示される — CS–US 関係はパヴロフ型であり、オペラントではない。

CS 中の反応率は、CS 前ベースライン区間の反応率と比較して抑制される。抑制の大きさが主要従属測度である。

## 2. 抑制比

Annau and Kamin (1961) は **抑制比** を標準的な定量測度として形式化した。

`SR = B / (A + B)`

ここで `A` は CS 前区間（CS と同持続）における反応数、`B` は CS 中の反応数である。値:

- `SR = 0.5` — 抑制なし（CS 中反応率 = CS 前反応率）。
- `SR = 0` — 完全抑制（CS 中反応なし）。
- 獲得中 `SR → 0` — パヴロフ型連合が強まるにつれて CS がオペラント・ベースラインを抑制する。

Annau and Kamin (1961) は、抑制比の獲得が US 強度の段階的関数であることを示した。

## 3. DSL 符号化

CER は実験層で合成される: オペラント・ベースライン・スケジュールがセッション全体を通じて作動し、パヴロフ型フェーズレベル・オーバーレイが CS–US 随伴性を導入する。DSL はこれを、オペラント構成要素が VI ベースラインで、レスポンデント構成要素が前方遅延 Pair プリミティブである単一フェーズで表現する。注釈（`annotations/extensions/respondent-annotator.md` の `@cs`, `@us`）は刺激メタデータを記録する。

```
Phase(
  name = "cer_training",
  operant = VI 60-s,
  respondent = Pair.ForwardDelay(tone, shock, isi=60-s, cs_duration=60-s),
  criterion = Stability(window=5, tolerance=0.10)
)
@cs(label="tone", duration=60-s, modality="auditory")
@us(label="shock", intensity="0.5mA", delivery="unsignaled")
```

オペラント・ベースラインとパヴロフ型オーバーレイが同一フェーズに共存するのは、US がオペラント反応クラスから独立にパヴロフ型スケジュールで呈示されるからである。この時間的独立性が、CER をオペラント・ベースラインへの罰手続きではなく合成手続きたらしめる。

## 4. 罰との区別

罰は嫌悪刺激を **反応に随伴して** 呈示する（三項嫌悪的随伴性）。CER は嫌悪刺激を **刺激に随伴して** 呈示する（二項パヴロフ型随伴性）。構造的区別は文法レベルで保存される: 罰はオペラント層の構成要素である（`operant/grammar.md §1.4` と `Overlay` コンビネータ参照）。CER の US 呈示はレスポンデント層の構成要素である。

## 5. 2 過程理論との関係

CER は、パヴロフ型 CS が動機づけ的特性を獲得してオペラント・パフォーマンスを調整することの標準的デモンストレーションである。Rescorla–Solomon (1967) の 2 過程枠組み（`two-process-theory.md` 参照）の下では、CS–shock 連合が条件性嫌悪状態を生成する。この状態は、2 つの状態が動機づけ的に非両立であるため、食欲性オペラント・パフォーマンスを抑制する。

## 6. 引用

- Annau, Z., & Kamin, L. J. (1961). The conditioned emotional response as a function of intensity of the US. *Journal of Comparative and Physiological Psychology*, 54(4), 428–432. https://doi.org/10.1037/h0042199
- Estes, W. K., & Skinner, B. F. (1941). Some quantitative properties of anxiety. *Journal of Experimental Psychology*, 29(5), 390–400. https://doi.org/10.1037/h0062283
- Rescorla, R. A., & Solomon, R. L. (1967). Two-process learning theory: Relationships between Pavlovian conditioning and instrumental learning. *Psychological Review*, 74(3), 151–182. https://doi.org/10.1037/h0024475
