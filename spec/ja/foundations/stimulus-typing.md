# 刺激型付け — SD, SΔ, CS, US, Sr+, Sr−, 罰子

> contingency-dsl 基盤層（Ψ）の一部。オペラント・レスポンデント・合成の各層にまたがって用いられる標準的な刺激型格子を固定する。パラダイム層はこれらの型を再利用し、層ごとに再導入することはない。

---

## 1. 刺激型格子

DSL は刺激型を、物理的モダリティ（光、音、電撃、餌）ではなく、**随伴性における役割** により区別する。物理的モダリティは注釈レベルの属性である（`@reinforcer`, `@sd`, `@cs`, `@punisher`）。

| 型 | 記号 | 役割 | パラダイム | 標準参照 |
|---|---|---|---|---|
| 弁別刺激 | SD, `S^D` | 反応が強化されるタイミングを合図 | オペラント | Skinner (1938) |
| S-デルタ | SΔ, `S^Δ` | 同じ反応が強化されないタイミングを合図 | オペラント | Skinner (1938) |
| 条件刺激 | CS | レスポンデント手続きで US と対提示される信号 | レスポンデント | Pavlov (1927) |
| 無条件刺激 | US | UR を誘発する生物学的に有意な刺激 | レスポンデント | Pavlov (1927) |
| 正の強化子 | Sr+ | 呈示により R を増加させる結果 | オペラント | Skinner (1953) |
| 負の強化子 | Sr− | 除去により R を増加させる結果 | オペラント | Sidman (1953) |
| 罰子 | — | 呈示により R を減少させる結果 | オペラント | Azrin & Holz (1966) |

## 2. 直交する軸

刺激型は他の 2 つの軸と直交する。

- **valence（誘発価）** — 食欲的 vs 嫌悪的。`valence.md` を参照。
- **モダリティ** — 聴覚、視覚、触覚、味覚、嗅覚。注釈レベル（`@cs`, `@reinforcer` のパラメータ）。

同一の物理的刺激が、手続き間で異なる役割を果たしうる（例: レスポンデント対提示で CS だった音が、後に弁別オペラント手続きで SD として機能する）。DSL は役割を記録する。手続き間での再利用は、注釈レベルの刺激識別子に対する `let` 束縛によって実現される。

## 3. オペラント層における SD / SΔ

オペラント層において、SD と SΔ は **注釈レベル** のラベルであり、オペラント・スケジュール式に `@sd` および `@s_delta` を介して付与される。これらは CFG にプリミティブ・コンストラクタとして現れない。三項随伴性 `(SD, R, SR)` は、（スケジュール式, `@sd` 注釈）の対によって具現化される。

例:

```
Mult(VI 30-s @sd("tone"), EXT @s_delta("light"))
```

オペラント層の `procedure-annotator/stimulus` モジュール（`@sd`, `@s_delta`, `@reinforcer`）は、三項随伴性のための刺激型付け装置一式を提供する。

## 4. レスポンデント層における CS / US

レスポンデント層において、CS と US は **プリミティブレベル** のコンストラクタ引数である: `Pair.ForwardDelay(cs, us, isi, cs_duration)`, `Contingency(p_us_given_cs, p_us_given_no_cs)` 等。物理属性は `@cs` および `@us` 注釈（`annotations/extensions/respondent-annotator` が提供）により付与される。

例:

```
Pair.ForwardDelay(tone, shock, isi=5-s, cs_duration=10-s)
  @cs("tone", frequency=4000, modality="auditory")
  @us("shock", intensity="0.5mA", modality="electrical")
```

## 5. 強化子と罰子の四象限

valence（食欲的 / 嫌悪的）と操作（呈示 / 除去）の組み合わせは、オペラントの 4 象限を生む。

|  | 呈示 | 除去 |
|---|---|---|
| **食欲的** | 正の強化（Sr+） | 負の罰 |
| **嫌悪的** | 正の罰 | 負の強化（Sr−） |

これらの象限は注釈レベルで（valence／操作パラメータを伴う `@reinforcer` と `@punisher` を介して）解決される。文法的なものではない。DSL は解析時に象限の整合性を強制しない。リンターは明らかな不整合（例: valence の明示的宣言を伴わない `@reinforcer("shock")`）について警告を発することができる。

## 6. このファイルが **カバーしない** もの

- 物理モダリティのパラメータ（周波数、強度、持続時間）。これらは注釈レベルである。
- 無条件反応（UR）、条件反応（CR）、オペラント反応（R）のような **反応側** の型付け。反応側の分類は `operant/theory.md` および `respondent/theory.md` で扱う。
- 派生刺激クラス（等価クラス、関係フレーム）。これらは行動的帰結であり、刺激型ではない。

## 参考文献

- Azrin, N. H., & Holz, W. C. (1966). Punishment. In W. K. Honig (Ed.), *Operant behavior: Areas of research and application* (pp. 380–447). Appleton-Century-Crofts.
- Catania, A. C. (2013). *Learning* (5th ed.). Sloan.
- Pavlov, I. P. (1927). *Conditioned reflexes: An investigation of the physiological activity of the cerebral cortex* (G. V. Anrep, Trans.). Oxford University Press.
- Sidman, M. (1953). Two temporal parameters of the maintenance of avoidance behavior by the white rat. *Journal of Comparative and Physiological Psychology*, 46(4), 253–261. https://doi.org/10.1037/h0060730
- Skinner, B. F. (1938). *The behavior of organisms*. Appleton-Century.
- Skinner, B. F. (1953). *Science and human behavior*. Macmillan.
