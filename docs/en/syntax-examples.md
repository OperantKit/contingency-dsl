# Syntax Examples

> Examples of contingency-dsl expressions for each layer. For a step-by-step introduction, see the [Syntax Guide](syntax-guide.md); for the formal grammar, see [operant/grammar.md](../../spec/en/operant/grammar.md) and [respondent/grammar.md](../../spec/en/respondent/grammar.md).

[日本語版](../ja/syntax-examples.md)

## Operant

```
FR5                           -- Fixed Ratio 5
VI60s                         -- Variable Interval 60 seconds
Chain(FR5, FI30s)             -- Chained: FR5 then FI30
Conc(VI30s, VI60s)            -- Concurrent VI30 VI60
Mult(VI30s, VI60s)            -- Multiple schedule (alternating components)
Mix(VI30s, VI60s)             -- Mixed schedule (alternating, no signaling)
Conj(FI15s, FR10)             -- Conjunctive: both requirements must be met
Alt(FR5, VI60s)               -- Alternative: either requirement satisfies
FR5(FI30)                     -- Second-order: 5 FI30 completions
let baseline = VI60s          -- Named binding
DRL5s                         -- Differential Reinforcement of Low rate
FI30 LH10                     -- Limited Hold: 10s availability window
FI30 TO(duration=30s)         -- Timeout after reinforcement

-- Aversive control
Sidman(SSI=20s, RSI=5s) @punisher("shock", intensity="0.5mA")
                              -- Sidman free-operant avoidance (Sidman, 1953)
DiscrimAv(CSUSInterval=10s, ITI=3min, mode=fixed, ShockDuration=0.5s)
                              -- Discriminated avoidance (Solomon & Wynne, 1953)
DiscrimAv(CSUSInterval=10s, ITI=3min, mode=response_terminated)
                              -- Response-terminated mode: response terminates shock
@reinforcer("token") VI60s ResponseCost(amount=1)
                              -- Response cost on conditioned reinforcer

-- Punishment overlays
Overlay(VI60s, FR1) @punisher("shock")
                              -- Punishment overlay on VI60 baseline
Overlay(Conc(VI30s, VI60s, COD=2s), FR1, target=changeover)
                              -- Changeover-only punishment (Todorov, 1971)
Conc(VI30s, VI60s, COD=2s, PUNISH(1->2)=FR1, PUNISH(2->1)=FR1)
                              -- Directional response-class punishment
```

## Operant — stateful and trial-based

```
Pctl(IRT, 50)                 -- Percentile schedule (Platt, 1973)
Adj(delay, start=10s, step=1s)
                              -- Adjusting schedule
Interlock(R0=300, T=10min)    -- Interlocking schedule (Berryman & Nevin, 1962)
MTS(comparisons=3, consequence=CRF, ITI=5s)
                              -- Matching-to-Sample (trial-based)
GoNoGo(responseWindow=5s, consequence=CRF, ITI=10s)
                              -- Go/NoGo discrimination
```

## Respondent

```
Pair.ForwardDelay(cs=Tone, us=Shock, isi=10s, cs_duration=12s)
Pair.ForwardTrace(cs=Tone, us=Shock, trace_interval=5s)
Pair.Simultaneous(cs=Light, us=Food)
Pair.Backward(us=Shock, cs=Tone, isi=10s)
Contingency(p_us_given_cs=0.8, p_us_given_no_cs=0.2)
TrulyRandom(cs=Tone, us=Shock)           -- sugar for Contingency(p, p)
ExplicitlyUnpaired(cs=Tone, us=Shock, min_separation=30s)
Compound(cs_list=[Tone, Light], mode=Simultaneous)
Serial(cs_list=[Tone, Light], isi=5s)
Differential(cs_positive=Tone, cs_negative=Noise, us=Shock)  -- A+/B− discrimination
Extinction(cs=Tone)
ITI(distribution=exponential, mean=120s)
```

## Composed (operant × respondent)

```
-- CER (Estes & Skinner, 1941): operant baseline + Pavlovian pairing + reference reinstatement
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

-- Autoshaping (Brown & Jenkins, 1968)
@cs(label="KeyLight", duration=8s, modality="visual")
@us(label="Food", delivery="unsignaled")

phase autoshaping_training:
  sessions = 10
  Pair.ForwardDelay(KeyLight, Food, isi=8s, cs_duration=8s)

-- Omission / negative automaintenance (Williams & Williams, 1969)
@cs(label="KeyLight", duration=6s, modality="visual")
@us(label="Food", delivery="cancelled_on_cs_response")

phase omission_training:
  sessions = 20
  Pair.ForwardDelay(KeyLight, Food, isi=6s, cs_duration=6s) @omission(response="key_peck", during="cs")
```

## References

- Berryman, R., & Nevin, J. A. (1962). Interlocking schedules of reinforcement. *Journal of the Experimental Analysis of Behavior*, 5(2), 213–223. https://doi.org/10.1901/jeab.1962.5-213
- Brown, P. L., & Jenkins, H. M. (1968). Auto-shaping of the pigeon's key-peck. *Journal of the Experimental Analysis of Behavior*, 11(1), 1–8. https://doi.org/10.1901/jeab.1968.11-1
- Estes, W. K., & Skinner, B. F. (1941). Some quantitative properties of anxiety. *Journal of Experimental Psychology*, 29(5), 390–400. https://doi.org/10.1037/h0062283
- Platt, J. R. (1973). Percentile reinforcement. In G. H. Bower (Ed.), *The psychology of learning and motivation* (Vol. 7, pp. 271–296).
- Sidman, M. (1953). Two temporal parameters of the maintenance of avoidance behavior by the white rat. *Journal of Comparative and Physiological Psychology*, 46(4), 253–261. https://doi.org/10.1037/h0060730
- Solomon, R. L., & Wynne, L. C. (1953). Traumatic avoidance learning: Acquisition in normal dogs. *Psychological Monographs: General and Applied*, 67(4), 1–19. https://doi.org/10.1037/h0093649
- Todorov, J. C. (1971). Concurrent performances: Effect of punishment contingent on the switching response. *Journal of the Experimental Analysis of Behavior*, 16(1), 51–62. https://doi.org/10.1901/jeab.1971.16-51
- Williams, D. R., & Williams, H. (1969). Auto-maintenance in the pigeon: Sustained pecking despite contingent non-reinforcement. *Journal of the Experimental Analysis of Behavior*, 12(4), 511–520. https://doi.org/10.1901/jeab.1969.12-511
