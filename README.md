# contingency-dsl

:jp: [日本語版 README](README.ja.md)

Language-independent specification for declaring reinforcement contingencies and Pavlovian pairings. Organized by scientific category (operant / respondent / composed) under a paradigm-neutral formal foundation.

## Layer structure

| Layer | Scope | Directory |
|---|---|---|
| **Foundations** | CFG / LL(2) meta-grammar; paradigm-neutral types (contingency, time scales, stimulus typing, valence, context) | `spec/*/foundations/`, `schema/foundations/` |
| **Operant** | Three-term contingency (SD-R-SR); reinforcement schedules by Ferster-Skinner class (ratio / interval / time / differential / compound / progressive); aversive control (Sidman free-operant avoidance, discriminated avoidance, escape, response cost); stateful variants (Percentile, Adjusting, Interlocking, Admission Gate); trial-based variants (MTS, Go/NoGo); response modifiers (Limited Hold, Timeout, reinforcement delay, interpolated schedules) | `spec/*/operant/`, `schema/operant/` |
| **Respondent** | Two-term contingency (CS-US); minimum Tier A primitives (Pair, Extinction, CSOnly, USOnly, Contingency, TrulyRandom, ExplicitlyUnpaired, Compound, Serial, ITI, Differential). Deeper Pavlovian procedures live in the companion package `contingency-respondent-dsl`. | `spec/*/respondent/`, `schema/respondent/` |
| **Composed** | Procedures that combine operant and respondent building blocks: CER, PIT, autoshaping, omission, two-process theory. Encoded as `PhaseSequence` AST trees built from operant + respondent primitives plus the composed-layer annotations `@omission` / `@avoidance` (`schema/annotations/extensions/composed-annotator.schema.json`); no dedicated composed-procedure AST schema. | `spec/*/composed/` |
| **Experiment** | Declarative multi-phase designs; phase and context as first-class constructs; JEAB-style inheritance of Subjects / Apparatus annotations | `spec/*/experiment/`, `schema/experiment/` |
| **Annotation** | Program-scoped metadata following JEAB Method categories (Subjects / Apparatus / Procedure / Measurement); extensions under `annotations/extensions/` (e.g., respondent-annotator, learning-models-annotator) | `spec/*/annotations/`, `schema/annotations/` |

## What this package contains

- **`spec/{en,ja}/`** — Formal specification per layer (theory, grammar, primitives, design rationale)
- **`schema/`** — EBNF grammar per layer + JSON Schemas for the AST
- **`conformance/`** — Language-independent conformance test suite (input text → expected AST JSON)
- **`docs/{en,ja}/`** — User-facing documentation (syntax guide, use cases, annotations, paper examples, tooling)
- **`scripts/`** — EBNF → Langium and EBNF → Tree-sitter converters; regeneration scripts for `dist/`

## What this package does NOT contain

- No code. No parser implementation. No runtime dependencies.
- Parser implementations live in separate packages:
  - **contingency-dsl-py** — Python reference parser
  - **contingency-dsl-rs** — Rust parser (future)
- Tier B Pavlovian procedures (higher-order conditioning, blocking, overshadowing, latent inhibition, renewal, reinstatement, occasion setting, etc.) live in the companion package **contingency-respondent-dsl**, which plugs into the Respondent extension point defined in `spec/en/respondent/grammar.md`.

## Syntax examples

### Operant
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

### Operant — stateful and trial-based
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

### Respondent
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

### Composed (operant × respondent)
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

## Documentation

- **[Syntax Guide (EN)](docs/en/syntax-guide.md)** / **[構文ガイド (JA)](docs/ja/syntax-guide.md)** — Progressive guide covering operant, respondent, and composed primitives
- **[Use Cases (EN)](docs/en/use-cases.md)** / **[ユースケース (JA)](docs/ja/use-cases.md)** — What each construct enables, with citations
- **[Annotations (EN)](docs/en/annotations.md)** / **[アノテーション (JA)](docs/ja/annotations.md)** — Metadata layers including `@reinforcer`, `@punisher`, `@sd`, `@cs`, `@us`, `@iti`, `@cs_interval`, `@context`, `@species`, `@strain`, `@apparatus`, `@model`
- **[Paper Examples (EN)](docs/en/paper-examples.md)** / **[論文例 (JA)](docs/ja/paper-examples.md)** — DSL encodings of CER, autoshaping, PIT, omission, and classical schedule studies
- **[Architecture (EN)](spec/en/architecture.md)** / **[アーキテクチャ (JA)](spec/ja/architecture.md)** — Six-layer diagram, SEI P1/P2/P3, TC / non-TC boundary
- **[Design Philosophy (EN)](spec/en/design-philosophy.md)** / **[設計思想 (JA)](spec/ja/design-philosophy.md)** — Supreme objective, layer rationale, admission gate
- **[Operant Grammar (EN)](spec/en/operant/grammar.md)** / **[オペラント文法 (JA)](spec/ja/operant/grammar.md)** — Three-term contingency productions
- **[Respondent Grammar (EN)](spec/en/respondent/grammar.md)** / **[レスポンデント文法 (JA)](spec/ja/respondent/grammar.md)** — Tier A primitives + extension point
- **[Foundations Grammar (EN)](spec/en/foundations/grammar.md)** / **[基盤文法 (JA)](spec/ja/foundations/grammar.md)** — Paradigm-neutral lexical structure
- **[Tooling (EN)](docs/en/tooling.md)** / **[ツーリング (JA)](docs/ja/tooling.md)** — Tree-sitter, Langium LSP, EBNF loader order

## Conformance testing

Any parser implementation should pass all tests under `conformance/`:

```bash
# Python example
cd ../contingency-dsl-py && pytest tests/test_conformance.py -v

# Rust example (future)
cd ../contingency-dsl-rs && cargo test conformance
```

The test corpus is organized by layer:
- `conformance/foundations/` — paradigm-neutral lexical tests (intentionally empty under the strict scoping rule defined in `conformance/foundations/README.md`)
- `conformance/operant/` — atomic schedules, compound combinators (Conc / Alt / Conj / Chain / Tand / Mult / Mix / Overlay / Interpolate), modifiers (DR*, PR, Lag, Repeat, Limited Hold, Timeout, reinforcement delay), second-order, aversive (Sidman, DiscriminatedAvoidance), response cost, algebraic equivalences, boundary values, errors, warnings
- `conformance/operant/stateful/` — Percentile, Adjusting, Interlocking
- `conformance/operant/trial-based/` — MTS, Go/NoGo
- `conformance/respondent/` — Tier A primitive fixtures (Pair, contingency controls, compound stimuli, elementary)
- `conformance/composed/` — CER (conditioned suppression), PIT, autoshaping, omission, two-process avoidance
- `conformance/experiment/` — phase, progressive-training, shaping
- `conformance/annotations/` — subjects, apparatus, procedure (stimulus / temporal / trial-structure), measurement, program-level; `extensions/respondent-annotator.json`
- `conformance/representations/` — alternative coordinate systems (t-τ)

## Regenerating `dist/`

The `dist/` tree (Langium and Tree-sitter artifacts) is gitignored and reproducible from `schema/*/grammar.ebnf`:

```bash
./scripts/gen-langium.sh      # dist/langium/contingency-dsl.langium
./scripts/gen-treesitter.sh   # dist/tree-sitter/grammar.js
```

Loader order: Foundations → Operant → Operant.Stateful → Operant.TrialBased → Respondent, followed by any additional `grammar.ebnf` discovered via rglob in sorted order.

## References

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

