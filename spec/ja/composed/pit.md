# Pavlovian-to-Instrumental Transfer（PIT）

> contingency-dsl 合成層の一部。PIT は、独立に訓練されたパヴロフ型 CS による道具的訓練された反応の調整を指す。2 つの訓練履歴は独立に確立され、テスト相ではオペラント反応が消去（または維持ベースライン）下で利用可能な状態でパヴロフ型 CS が呈示される。

**関連文書:**
- [2 過程理論](two-process-theory.md) — 転移効果を動機づける Rescorla–Solomon (1967) の枠組み。
- [オペラント文法](../operant/grammar.md) — オペラント反応の産出規則。
- [レスポンデント文法](../respondent/grammar.md) — パヴロフ型訓練の産出規則。
- [実験 / フェーズ列](../experiment/phase-sequence.md) — 多相計画。

---

## 1. 手続き

PIT 手続きは 3 相から成り、最初の 2 つは重要なテスト前に **独立に** 確立される。

1. **パヴロフ型訓練.** オペラント反応要件の不在下で CS が US と対提示される（例: `Pair.ForwardDelay(cs, food, ...)`）。CS はオペラント反応履歴なしで予告特性を獲得する。
2. **道具的訓練.** パヴロフ型 CS なしで、同じ US を生成するスケジュール上でオペラント反応（例: レバー押し）が訓練される（例: 餌呈示によって維持される VI 60 秒）。オペラント履歴は CS 曝露なしで確立される。
3. **転移テスト.** 道具的反応が利用可能な状態で、パヴロフ型 CS が呈示される。典型的には、CS の動機づけ的影響を継続強化から分離するため、消去下（テスト中に US 呈示なし）で行う。

従属測度は、テストにおける CS 呈示中とマッチした無 CS 区間の間のオペラント反応率の変化である。

Estes (1948) は最初に転移効果を示した。Rescorla and Solomon (1967) は理論的解釈を明確化し、Lovibond (1983) はパラダイムを食欲性計画に拡張した。食欲性計画では、パヴロフ型 CS が道具的パフォーマンスを（抑制ではなく）促進する。

## 2. 一般 PIT vs 特異 PIT

パヴロフ型と道具的訓練が共有する内容により、主要な 2 つの変種が区別される。

- **一般 PIT.** パヴロフ型訓練と道具的訓練は **同じ動機づけクラス** の結果を用いるが、必ずしも同一の結果ではない（例: パヴロフ型 CS をスクロースと対提示; 道具的反応を餌ペレットで強化）。CS は共有された動機づけ状態を介して道具的反応を促進する。
- **結果特異 PIT.** パヴロフ型 CS と道具的反応は **同一の結果** を共有する（例: 両者ともスクロースで訓練）。複数の結果特異反応を同時にテストする場合、CS はその特定結果に対する道具的反応を選択的に促進する。この変種は、パヴロフ型段階における結果特異な S–O 連合の証拠とされる。

DSL は両変種を同じ合成構造で表現する。区別はパヴロフ型および オペラント・フェーズ上の `@us` / 強化子ラベルが担う。

## 3. DSL 符号化

```
PhaseSequence(
  Phase(
    name = "pavlovian_training",
    respondent = Pair.ForwardDelay(tone, food, isi=10-s, cs_duration=10-s),
    criterion = FixedSessions(n=8)
  ),
  Phase(
    name = "instrumental_training",
    operant = VI 60-s,
    criterion = Stability(window=5, tolerance=0.10)
  ),
  Phase(
    name = "transfer_test",
    operant = EXT,
    respondent = CSOnly(tone, trials=8),
    criterion = FixedSessions(n=1)
  )
)
@cs(label="tone", duration=10-s, modality="auditory")
@us(label="food", intensity="45mg_pellet", delivery="signaled")
```

パヴロフ型と道具的フェーズは別セッション（またはセッション内で明確に分離されたブロック）で作動する。これは `PhaseSequence` 構成要素が保証する。転移テストはオペラント・スケジュールを消去（`EXT`）下に置き、ゼロ・ベースライン強化に対して CS の効果を読み取るようにする。`CSOnly` は US なしでパヴロフ型 CS を呈示する。

## 4. CER との関係

PIT と CER（`conditioned-suppression.md` 参照）はいずれも、オペラント・パフォーマンスを調整するパヴロフ型 CS を含む。両者は訓練履歴で異なる。

- **CER**: パヴロフ型オーバーレイがすでに訓練されたオペラント・ベースラインに、典型的には同一セッション内で重畳される。CS はオペラントが同時に維持されている間にその特性を獲得する。
- **PIT**: パヴロフ型と道具的訓練は明示的に **独立** である。重要なテストは、道具的反応と対提示されたことのない CS を呈示する。

この独立性が、PIT を同一セッション内の調整ではなく、パヴロフ型学習から道具的パフォーマンスへの転移の診断手続きたらしめる。

## 5. 引用

- Estes, W. K. (1948). Discriminative conditioning. II. Effects of a Pavlovian conditioned stimulus upon a subsequently established operant response. *Journal of Experimental Psychology*, 38(2), 173–177. https://doi.org/10.1037/h0057525
- Lovibond, P. F. (1983). Facilitation of instrumental behavior by a Pavlovian appetitive conditioned stimulus. *Journal of Experimental Psychology: Animal Behavior Processes*, 9(3), 225–247. https://doi.org/10.1037/0097-7403.9.3.225
- Rescorla, R. A., & Solomon, R. L. (1967). Two-process learning theory: Relationships between Pavlovian conditioning and instrumental learning. *Psychological Review*, 74(3), 151–182. https://doi.org/10.1037/h0024475
