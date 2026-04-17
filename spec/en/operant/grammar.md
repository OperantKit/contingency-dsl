# Operant Grammar — Three-Term Contingency (SD–R–SR)

> Part of the contingency-dsl operant layer. Defines the operant-specific EBNF productions: `ScheduleExpr`, the combinator family (Conc, Alt, Conj, Chain, Tand, Mult, Mix, Overlay), modifiers (DRL, DRH, DRO, PR, Lag, Repeat), qualifiers (LH, TO, ResponseCost), and aversive schedules (Sidman, DiscriminatedAvoidance). Paradigm-neutral meta-grammar is defined in `foundations/grammar.md`. Per-schedule-class specifications live in `operant/schedules/{ratio,interval,time,differential,compound,progressive}.md`. Stateful and trial-based sublayers live under `operant/stateful/` and `operant/trial-based/`.

**Companion document:** [LL(2) Formal Proof](../foundations/ll2-proof.md) — FIRST₁/FIRST₂/FOLLOW₂ sets, LL(2) parse table, unambiguity proof. The operant grammar has exactly one LL(2) decision point (`PosTail` in compound `arg_list`); all other decision points are LL(1).

---

## 1. Operant-Specific Productions

Building on the paradigm-neutral skeleton in `foundations/grammar.md`, the operant layer specializes `<expr>` to `<schedule>`:

```bnf
<program>       ::= <param_decl>* <binding>* <schedule>
<param_decl>    ::= <param_name> "=" <value>
<param_name>    ::= "LH" | "LimitedHold"
                  | "COD" | "ChangeoverDelay"
                  | "FRCO" | "FixedRatioChangeover"
                  | "BO"  | "Blackout"
                  | "RD"  | "ReinforcementDelay"
<binding>       ::= "let" <ident> "=" <schedule>

<schedule>      ::= <base_schedule> ("LH" <ws>? <value>)?
                                   (("TO" | "Timeout") "(" <timeout_args> ")")?
<base_schedule> ::= <atomic>
                  | <compound>
                  | <modifier>
                  | <aversive_schedule>
                  | <ident>
                  | "(" <schedule> ")"

<atomic>        ::= <dist><domain> <ws>? <value>
                  | "EXT"
                  | "CRF"
<dist>          ::= "F" | "V" | "R"
<domain>        ::= "R" | "I" | "T"
<ws>            ::= " "+
```

The `<dist><domain>` prefix produces the 3×3 atomic schedule grid (FR, VR, RR, FI, VI, RI, FT, VT, RT) specialized in `operant/schedules/{ratio, interval, time}.md`. `EXT` and `CRF` are boundary cases (extinction and continuous reinforcement; see `operant/theory.md §1.3`).

### 1.1 Reserved Keyword Set (Operant Layer)

```bnf
<reserved>      ::= "let" | "def"
                  | <dist><domain>
                  | "EXT" | "CRF"
                  | <combinator>
                  | "DRL" | "DRH" | "DRO" | "LH" | "LimitedHold"
                  | "COD" | "ChangeoverDelay"
                  | "FRCO" | "FixedRatioChangeover"
                  | "RD"  | "ReinforcementDelay"
                  | "BO"  | "Blackout"
                  | "PR" | "Repeat"
                  | "hodos" | "exponential" | "linear" | "geometric"
                  | "start" | "increment"
                  | "Sidman" | "SidmanAvoidance"
                  | "SSI" | "ShockShockInterval"
                  | "RSI" | "ResponseShockInterval"
                  | "Lag" | "length"
                  | "DiscriminatedAvoidance" | "DiscrimAv"
                  | "CSUSInterval" | "ITI" | "mode"
                  | "ShockDuration" | "MaxShock"
                  | "fixed" | "escape"
                  | "TO" | "Timeout"
                  | "duration" | "reset_on_response" | "contingent_response"
                  | "true" | "false"
                  | "Overlay"
                  | "target" | "changeover" | "all"
                  | "PUNISH"
                  | "Interpolate" | "Interp"
                  | "count" | "onset"
```

`def` is reserved by the foundations layer; the operant layer inherits this reservation.

### 1.2 Compound Productions

```bnf
<compound>      ::= <combinator> "(" <arg_list> ")"
                  | <interpolate>
<combinator>    ::= "Conc" | "Alt" | "Conj"
                  | "Chain" | "Tand"
                  | "Mult" | "Mix"
                  | "Overlay"
<arg_list>      ::= <positional_args> ("," <keyword_arg>)*
<positional_args> ::= <schedule> ("," <schedule>)+
<keyword_arg>   ::= <scalar_kw_arg> | <directional_kw_arg>
                  | <overlay_kw_arg> | <punish_directive>
<scalar_kw_arg> ::= <kw_name> "=" <value>
<directional_kw_arg> ::= <kw_name> "(" <dir_ref> "->" <dir_ref> ")" "=" <value>
<dir_ref>       ::= <number> | <ident>
<kw_name>       ::= "COD" | "ChangeoverDelay"
                   | "FRCO" | "FixedRatioChangeover"
                   | "BO"  | "Blackout"

<overlay_kw_arg> ::= "target" "=" <target_value>
<target_value>  ::= "changeover" | "all"

<punish_directive> ::= "PUNISH" "(" <punish_target> ")" "=" <schedule>
<punish_target>    ::= "changeover"
                     | <dir_ref> "->" <dir_ref>
                     | <dir_ref>
```

Per-combinator semantics are specified in `operant/schedules/compound.md`. Per-modifier semantics are specified in the schedule-class files (`ratio.md`, `interval.md`, `time.md`, `differential.md`, `progressive.md`).

### 1.3 Modifier Productions

```bnf
<modifier>      ::= <dr_mod> | <pr_mod> | <repeat> | <lag_mod>
<dr_mod>        ::= ("DRL" | "DRH" | "DRO") <ws>? <value>
<pr_mod>        ::= "PR" "(" <pr_opts> ")"
                  | "PR" <ws>? <number>
<pr_opts>       ::= <pr_step> ("," <pr_param>)*
<pr_step>       ::= "hodos" | "exponential" | "linear" | "geometric"
<pr_param>      ::= "start" "=" <number>
                  | "increment" "=" <number>
                  | "ratio" "=" <number>
<repeat>        ::= "Repeat" "(" <number> "," <schedule> ")"
<lag_mod>       ::= "Lag" <ws>? <number>
                  | "Lag" "(" <number> ("," <lag_kw_arg>)* ")"
<lag_kw_arg>    ::= "length" "=" <number>
```

DR modifiers are detailed in `operant/schedules/differential.md`. PR is detailed in `operant/schedules/progressive.md`. `Repeat` is syntactic sugar (see §3). `Lag` is an operant-variability modifier (Page & Neuringer, 1985).

### 1.4 Qualifier and Aversive Productions

```bnf
<timeout_args>  ::= <timeout_kwarg> ("," <timeout_kwarg>)*
<timeout_kwarg> ::= "duration" "=" <value>
                  | "reset_on_response" "=" <boolean>
                  | "contingent_response" "=" <label_ref>
<boolean>       ::= "true" | "false"
<label_ref>     ::= <ident> | <number>

<interpolate>   ::= ("Interpolate" | "Interp") "(" <schedule> "," <schedule>
                    ("," <interp_kw_arg>)+ ")"
<interp_kw_arg> ::= "count" "=" <number>
                  | "onset" "=" <value>

<aversive_schedule> ::= <sidman_avoidance>
                      | <discriminated_avoidance>
<sidman_avoidance>  ::= ("Sidman" | "SidmanAvoidance") "(" <sidman_arg> ("," <sidman_arg>)* ")"
<sidman_arg>        ::= <sidman_kw> "=" <value>
<sidman_kw>         ::= "SSI" | "ShockShockInterval"
                      | "RSI" | "ResponseShockInterval"
<discriminated_avoidance> ::= ("DiscriminatedAvoidance" | "DiscrimAv")
                              "(" <da_arg> ("," <da_arg>)* ")"
<da_arg>            ::= <da_temporal_kw> "=" <value>
                      | "mode" "=" <da_mode>
<da_temporal_kw>    ::= "CSUSInterval" | "ITI" | "ShockDuration" | "MaxShock"
<da_mode>           ::= "fixed" | "escape"
```

Sidman free-operant avoidance and DiscriminatedAvoidance are first-class aversive-control primitives (see `operant/theory.md §2.7–§2.9`).

## 2. Notational Flexibility

The operant grammar supports multiple notational forms matching behavioral literature conventions:

```
VI 60-s      -- JEAB modern standard (recommended)
VI 60-sec    -- JEAB older papers (1960s-1970s)
VI 60 s      -- space-separated unit (JEAB 1986, 2012)
VI 60 sec    -- space-separated unit (Ferster & Skinner, 1957)
VI 60-min    -- minutes (e.g., VI 1-min)
VI 60 min    -- minutes, space-separated
VI 60s       -- attached unit (no separator)
VI60s        -- compact with unit
VI60         -- compact (unit implied)
VI 60        -- whitespace-separated, no unit (Ferster & Skinner, 1957)
VI(60)       -- Python constructor form
```

All resolve to the same `VariableInterval(target_time=60.0)`. The parser reads the two-character `<dist><domain>` prefix, skips optional whitespace, and reads `<value>`.

## 3. Syntactic Sugar

**`Repeat(n, S)`** is syntactic sugar for n-fold tandem composition:

```
Repeat(n, S) ≡ Tand(S, S, ..., S)
                    └── n copies ──┘
```

It does not increase the computational power of the DSL. The parser expands it at parse time into a let-free syntax tree. Algebraic properties are proved in `operant/theory.md §2.2.3`.

## 4. Dual API

The DSL provides two equivalent interfaces:

**A. Text DSL (configuration files, documentation):**
```python
from contingency_dsl import parse
schedule = parse("Conc(VI 30-s, VI 60-s)")
```

**B. Python constructors (programmatic composition):**
```python
from contingency_dsl import FR, VI, Conc, Chain, Tand, Repeat
schedule = Conc(VI(30), VI(60))
nested = Conc(Chain(FR(5), VI(60)), FR(10))
repeated = Tand(Repeat(3, FR(10)), VI(60))
```

The Python constructor API replicates the OperantKit `ScheduleBuilder.swift` pattern: `FR(5)`, `Conc(...)`, `Alt(...)`, `Chain(...)`.

## 5. Example Expressions

```
-- Atomic schedules (see operant/schedules/{ratio,interval,time}.md)
FR 5                                   -- Fixed Ratio 5
VI 30-s                                 -- Variable Interval 30 seconds
RR 20                                  -- Random Ratio 20
EXT                                   -- Extinction
CRF                                   -- Continuous Reinforcement (= FR 1)

-- Compound schedules (see operant/schedules/compound.md)
Conc(VI 30-s, VI 60-s, COD=2-s)           -- Concurrent VI 30-s VI 60-s with 2-s COD
Chain(FR 5, FI 30-s)                     -- Chained FR 5 then FI 30
Alt(FR 10, FI 5-min)                     -- Alternative FR 10 or FI 5-min
Conj(FR 5, FI 30-s)                      -- Conjunctive FR 5 AND FI 30
Tand(VR 20, DRL 5-s)                     -- Tandem VR 20 then DRL 5
Mult(FR 5, EXT)                        -- Multiple FR 5/EXT
Mix(FR 5, FR 10)                        -- Mixed FR 5/FR 10

-- Modifiers (see operant/schedules/{differential,progressive}.md)
DRL 5-s                                 -- Differential Reinforcement of Low rate
DRO 10-s                                -- Differential Reinforcement of Other behavior
PR(hodos)                             -- Progressive Ratio (Hodos step)
PR(linear, start=1, increment=5)      -- Progressive Ratio (linear step)

-- Limited Hold (temporal availability constraint)
FI 30-s LH 10-s                           -- FI 30-s with 10-s hold (Ferster & Skinner, 1957)
VI 60-s LH 5-s                            -- VI 60-s with 5-s hold

-- Changeover Delay and Fixed-Ratio Changeover
Conc(VI 30-s, VI 60-s, COD=2-s)           -- 2-s changeover delay (Herrnstein, 1961)
Conc(VI 30-s, VI 60-s, FRCO=5)           -- 5 fixed-ratio changeover (Hunter & Davison, 1985)

-- Sidman free-operant avoidance
Sidman(SSI=20-s, RSI=5-s)                              -- Sidman (1953)

-- Discriminated avoidance
DiscriminatedAvoidance(CSUSInterval=10-s, ITI=3-min, mode=escape)       -- Solomon & Wynne (1953)

-- Punishment overlay
Overlay(VI 60-s, FR 1)                              -- every response punished on VI 60 baseline
Overlay(Conc(VI 30-s, VI 60-s, COD=2-s), FR 1,
        target=changeover)                          -- punishment on changeover only (Todorov, 1971)
```

## 6. Error Recovery

Operant-specific error codes appear in `conformance/operant/errors.json`. The error recovery policy itself (panic-mode, synchronization tokens, multi-error reporting) is paradigm-neutral and specified in `foundations/grammar.md §7`.

## 7. Experiment Layer Extensions

Multi-phase experimental designs (phase sequences, progressive training, shaping) extend the operant grammar additively. See `experiment/phase-sequence.md` for the grammar and `experiment/criteria.md` for phase-change criteria.

## References

- Ferster, C. B., & Skinner, B. F. (1957). *Schedules of reinforcement*. Appleton-Century-Crofts.
- Herrnstein, R. J. (1961). Relative and absolute strength of response as a function of frequency of reinforcement. *Journal of the Experimental Analysis of Behavior*, 4(3), 267–272. https://doi.org/10.1901/jeab.1961.4-267
- Hunter, I., & Davison, M. (1985). Determination of a behavioral transfer function. *Journal of the Experimental Analysis of Behavior*, 43(1), 43–59. https://doi.org/10.1901/jeab.1985.43-43
- Page, S., & Neuringer, A. (1985). Variability is an operant. *Journal of Experimental Psychology: Animal Behavior Processes*, 11(3), 429–452. https://doi.org/10.1037/0097-7403.11.3.429
- Sidman, M. (1953). Two temporal parameters of the maintenance of avoidance behavior by the white rat. *Journal of Comparative and Physiological Psychology*, 46(4), 253–261. https://doi.org/10.1037/h0060730
- Skinner, B. F. (1938). *The behavior of organisms*. Appleton-Century.
- Solomon, R. L., & Wynne, L. C. (1953). Traumatic avoidance learning: Acquisition in normal dogs. *Psychological Monographs: General and Applied*, 67(4), 1–19. https://doi.org/10.1037/h0093649
- Todorov, J. C. (1971). Concurrent performances: Effect of punishment contingent on the switching response. *Journal of the Experimental Analysis of Behavior*, 16(1), 51–62. https://doi.org/10.1901/jeab.1971.16-51
