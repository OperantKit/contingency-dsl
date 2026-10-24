# 構文例

> contingency-dsl の式の例を、レイヤごとに示します。段階的な入門は [構文ガイド](syntax-guide.md) を、形式文法は [operant/grammar.md](../../spec/ja/operant/grammar.md) と [respondent/grammar.md](../../spec/ja/respondent/grammar.md) を参照してください。

[English](../en/syntax-examples.md)

## Operant

```
FR5                           -- 固定比率 5
VI60s                         -- 変動時隔 60 秒
Chain(FR5, FI30s)             -- 連鎖: FR5 の後に FI30
Conc(VI30s, VI60s)            -- 並立 VI30 VI60
Mult(VI30s, VI60s)            -- 多元スケジュール（成分が交替する）
Mix(VI30s, VI60s)             -- 混合スケジュール（交替するが弁別刺激による信号はない）
Conj(FI15s, FR10)             -- 連言: 両方の要件を満たす必要がある
Alt(FR5, VI60s)               -- 二択: どちらかの要件を満たせばよい
FR5(FI30)                     -- 二次スケジュール: FI30 を 5 回完了
let baseline = VI60s          -- 名前付きの束縛（次の行で使う）
Mult(baseline, EXT)
DRL5s                         -- 低反応率分化強化
FI30 LH10                     -- 制限時間（Limited Hold）: 強化子を得られる時間は 10 秒
FI30 TO(duration=30s, reset_on_response=false)
                              -- 強化後のタイムアウト

-- 嫌悪性制御
Sidman(SSI=20s, RSI=5s) @punisher("shock", intensity="0.5mA")
                              -- Sidman 型の自由オペラント回避 (Sidman, 1953)
DiscrimAv(CSUSInterval=10s, ITI=3min, mode=fixed, ShockDuration=0.5s)
                              -- 弁別回避 (Solomon & Wynne, 1953)
DiscrimAv(CSUSInterval=10s, ITI=3min, mode=response_terminated)
                              -- 反応終了モード: 反応がショックを終了させる
@reinforcer("token") VI60s ResponseCost(amount=1)
                              -- 条件性強化子に対する反応コスト

-- 罰の重畳
Overlay(VI60s, FR1) @punisher("shock")
                              -- VI60 のベースラインに罰を重畳する
Overlay(Conc(VI30s, VI60s, COD=2s), FR1, target=changeover)
                              -- 切替反応だけへの罰 (Todorov, 1971)
Conc(VI30s, VI60s, COD=2s, PUNISH(1->2)=FR1, PUNISH(2->1)=FR1)
                              -- 切替の向きごとの反応クラスへの罰
```

> **参照パーサについて:** 上の `@punisher` を使う 2 例は、[contingency-dsl-py](https://github.com/OperantKit/contingency-dsl-py) に同梱されたアノテーション拡張では解析できません。仕様では `@punisher` は `@reinforcer` の別名です（`schema/annotations/procedure-stimulus.schema.json`）が、パーサは別名を解決する前に書かれたままのキーワードを照合するため、`unknown annotation '@punisher'` を報告します。`scripts/check_docs_examples.py` はこのキーワードだけを別に登録し、例の残りの部分を検査します。

## Operant — 状態を持つスケジュールと試行型の手続き

```
Pctl(IRT, 50)                 -- パーセンタイルスケジュール (Platt, 1973)
Adj(delay, start=10s, step=1s)
                              -- 調整スケジュール
Interlock(R0=300, T=10min)    -- 連動スケジュール (Berryman & Nevin, 1962)
MTS(comparisons=3, consequence=CRF, ITI=5s)
                              -- 見本合わせ（試行型）
GoNoGo(responseWindow=5s, consequence=CRF, ITI=10s)
                              -- Go/NoGo 弁別
```

## Respondent

```
Pair.ForwardDelay(cs=Tone, us=Shock, isi=10s, cs_duration=12s)
Pair.ForwardTrace(cs=Tone, us=Shock, trace_interval=5s)
Pair.Simultaneous(cs=Light, us=Food)
Pair.Backward(us=Shock, cs=Tone, isi=10s)
Contingency(p_us_given_cs=0.8, p_us_given_no_cs=0.2)
TrulyRandom(cs=Tone, us=Shock)           -- Contingency(p, p) の略記
ExplicitlyUnpaired(cs=Tone, us=Shock, min_separation=30s)
Compound(cs_list=[Tone, Light], mode=Simultaneous)
Serial(cs_list=[Tone, Light], isi=5s)
Differential(cs_positive=Tone, cs_negative=Noise, us=Shock)  -- A+/B− 弁別
Extinction(cs=Tone)
ITI(distribution=exponential, mean=120s)
```

## Composed（operant × respondent）

```
-- CER (Estes & Skinner, 1941): オペラントのベースライン + Pavlov 型の対提示 + ベースラインの再利用
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

-- 省略（omission）/ 負の自動維持 (Williams & Williams, 1969)
@cs(label="KeyLight", duration=6s, modality="visual")
@us(label="Food", delivery="cancelled_on_cs_response")

phase omission_training:
  sessions = 20
  Pair.ForwardDelay(KeyLight, Food, isi=6s, cs_duration=6s) @omission(response="key_peck", during="cs")
```

> **参照パーサについて:** これらの例は、[contingency-dsl-py](https://github.com/OperantKit/contingency-dsl-py) に同梱されたアノテーション拡張では解析できません。`@cs` と `@us` は `schema/annotations/extensions/respondent-annotator.schema.json` で定義されていますが、パーサにはこれらを扱う拡張がないため、`unknown annotation '@cs'` を報告します。`scripts/check_docs_examples.py` はこの 2 つのキーワードだけを別に登録し、例の残りの部分を検査します。

## 参考文献

- Berryman, R., & Nevin, J. A. (1962). Interlocking schedules of reinforcement. *Journal of the Experimental Analysis of Behavior*, 5(2), 213–223. https://doi.org/10.1901/jeab.1962.5-213
- Brown, P. L., & Jenkins, H. M. (1968). Auto-shaping of the pigeon's key-peck. *Journal of the Experimental Analysis of Behavior*, 11(1), 1–8. https://doi.org/10.1901/jeab.1968.11-1
- Estes, W. K., & Skinner, B. F. (1941). Some quantitative properties of anxiety. *Journal of Experimental Psychology*, 29(5), 390–400. https://doi.org/10.1037/h0062283
- Platt, J. R. (1973). Percentile reinforcement. In G. H. Bower (Ed.), *The psychology of learning and motivation* (Vol. 7, pp. 271–296).
- Sidman, M. (1953). Two temporal parameters of the maintenance of avoidance behavior by the white rat. *Journal of Comparative and Physiological Psychology*, 46(4), 253–261. https://doi.org/10.1037/h0060730
- Solomon, R. L., & Wynne, L. C. (1953). Traumatic avoidance learning: Acquisition in normal dogs. *Psychological Monographs: General and Applied*, 67(4), 1–19. https://doi.org/10.1037/h0093649
- Todorov, J. C. (1971). Concurrent performances: Effect of punishment contingent on the switching response. *Journal of the Experimental Analysis of Behavior*, 16(1), 51–62. https://doi.org/10.1901/jeab.1971.16-51
- Williams, D. R., & Williams, H. (1969). Auto-maintenance in the pigeon: Sustained pecking despite contingent non-reinforcement. *Journal of the Experimental Analysis of Behavior*, 12(4), 511–520. https://doi.org/10.1901/jeab.1969.12-511
