# Formal Grammar

> Part of the [contingency-dsl theory documentation](theory.md). Defines the context-free grammar (BNF) for the DSL.

**Companion document:** [LL(2) Formal Proof](ll2-proof.md) — FIRST₁/FIRST₂/FOLLOW₂ sets, LL(2) parse table, unambiguity proof, and Core-Stateful preservation proof. The grammar has exactly one LL(2) decision point (`PosTail` in compound `arg_list`); all other decision points are LL(1).

---

## 3.1 Design Principles

The DSL grammar satisfies four criteria:

1. **Notational fidelity**: Matches behavioral literature conventions (`FR 5`, `conc VI 30 VI 60`).
2. **Unambiguous parsing**: Every expression has exactly one parse tree.
3. **Composability**: Supports arbitrarily nested schedule expressions.
4. **Python embeddability**: Usable as both standalone text format and Python constructor calls.

## 3.2 BNF Grammar (Base CFG)

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
<value>         ::= <number> <time_unit>?
<time_unit>     ::= "s" | "ms" | "min"
<number>        ::= [0-9]+ ("." [0-9]+)?

<ident>         ::= [a-z_][a-zA-Z0-9_]*   -- must not match <reserved>
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
                  | "hodos" | "exponential" | "linear"
                  | "start" | "increment"
                  | "Sidman" | "SidmanAvoidance"
                  | "SSI" | "ShockShockInterval"
                  | "RSI" | "ResponseShockInterval"
                  | "Lag" | "length"
                  | "DiscriminatedAvoidance" | "DiscrimAv"
                  | "CSUSInterval" | "ITI" | "mode"
                  | "ShockDuration" | "MaxShock"
                  | "fixed" | "escape"
                  | "Overlay"
                  | "Interpolate" | "Interp"
                  | "count" | "onset"

<compound>      ::= <combinator> "(" <arg_list> ")"
                  | <interpolate>
<combinator>    ::= "Conc" | "Alt" | "Conj"
                  | "Chain" | "Tand"
                  | "Mult" | "Mix"
                  | "Overlay"
<arg_list>      ::= <positional_args> ("," <keyword_arg>)*
<positional_args> ::= <schedule> ("," <schedule>)+
<keyword_arg>   ::= <kw_name> "=" <value>
<kw_name>       ::= "COD" | "ChangeoverDelay"
                   | "FRCO" | "FixedRatioChangeover"
                   | "BO"  | "Blackout"

<modifier>      ::= <dr_mod> | <pr_mod> | <repeat> | <lag_mod>
<dr_mod>        ::= ("DRL" | "DRH" | "DRO") <ws>? <value>
<pr_mod>        ::= "PR" "(" <pr_opts> ")"
                  | "PR" <ws>? <number>
<pr_opts>       ::= <pr_step> ("," <pr_param>)*
<pr_step>       ::= "hodos" | "exponential" | "linear"
<pr_param>      ::= "start" "=" <number>
                  | "increment" "=" <number>
<repeat>        ::= "Repeat" "(" <number> "," <schedule> ")"
<lag_mod>       ::= "Lag" <ws>? <number>
                  | "Lag" "(" <number> ("," <lag_kw_arg>)* ")"
<lag_kw_arg>    ::= "length" "=" <number>

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

**Identifier naming constraint.** Identifiers must begin with a lowercase ASCII letter or underscore (`[a-z_]`), followed by any combination of ASCII letters, digits, or underscores. This ensures lexical disjointness from DSL keywords and schedule type prefixes, all of which begin with an uppercase letter. The `<reserved>` production additionally prevents lowercase keywords (`let`, `def`, `hodos`, etc.) from being used as identifiers. `def` is reserved for future use (see [architecture.md §4.4](architecture.md)).

## 3.3 Notational Flexibility

The grammar supports multiple notational forms matching behavioral literature conventions:

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

## 3.4 Syntactic Sugar

**`Repeat(n, S)`** is syntactic sugar for n-fold tandem composition:

```
Repeat(n, S) ≡ Tand(S, S, ..., S)
                    └── n copies ──┘
```

It does not increase the computational power of the DSL. The parser expands it at parse time into a let-free syntax tree.

**`let` bindings** are macro expansion (textual substitution). Binding names must satisfy `<ident>`: they must begin with a lowercase letter or underscore and must not match any `<reserved>` word.

```
let baseline = VI 60-s
let treatment = Conc(VI 30-s, EXT)
Conc(baseline, treatment)
```

expands to:

```
Conc(VI 60-s, Conc(VI 30-s, EXT))
```

`let` does not introduce mutable state, closures, or recursive definitions. After expansion, the result is a let-free syntax tree within the base CFG.

**Scoping rules.** `let` bindings are subject to three semantic constraints:

1. **No shadowing.** Each binding name must be unique within a program. Duplicate names are a static error (e.g., `"duplicate binding 'x' (first defined at line N)"`).
2. **No forward references.** In binding `let x_k = e`, every identifier in `e` must be among `{x_1, ..., x_{k-1}}` — i.e., defined in a preceding binding. Referencing an undefined or later-defined identifier is a static error. As a corollary, transitive mutual references (e.g., `let a = b; let b = a`) are rejected.
3. **Top-level only.** Bindings appear only at the `<program>` level (`<program> ::= <binding>* <schedule>`). `let` cannot appear inside compound expressions.

Implementations SHOULD additionally emit a warning for unused bindings (a binding whose name is never referenced in the schedule expression or subsequent bindings).

## 3.5 Dual API

The v1.0 DSL provides two equivalent interfaces:

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

## 3.6 Example Expressions

```
-- Atomic schedules
FR 5                                   -- Fixed Ratio 5
VI 30-s                                 -- Variable Interval 30 seconds
RR 20                                  -- Random Ratio 20
EXT                                   -- Extinction
CRF                                   -- Continuous Reinforcement (= FR 1)

-- Compound schedules
Conc(VI 30-s, VI 60-s, COD=2-s)           -- Concurrent VI 30-s VI 60-s with 2-s COD
Chain(FR 5, FI 30-s)                     -- Chained FR 5 then FI 30
Alt(FR 10, FI 5-min)                     -- Alternative FR 10 or FI 5-min
Conj(FR 5, FI 30-s)                      -- Conjunctive FR 5 AND FI 30
Tand(VR 20, DRL 5-s)                     -- Tandem VR 20 then DRL 5
Mult(FR 5, EXT)                        -- Multiple FR 5/EXT
Mix(FR 5, FR 10)                        -- Mixed FR 5/FR 10

-- Nested compositions
Conc(Chain(FR 5, VI 60-s), Alt(FR 10, FT 30-s))

-- Modifiers
DRL 5-s                                 -- Differential Reinforcement of Low rate
DRO 10-s                                -- Differential Reinforcement of Other behavior
PR(hodos)                             -- Progressive Ratio (Hodos step)
PR(linear, start=1, increment=5)      -- Progressive Ratio (linear step)

-- Limited Hold (temporal availability constraint)
FI 30-s LH 10-s                           -- FI 30-s with 10-s hold (Ferster & Skinner, 1957)
VI 60-s LH 5-s                            -- VI 60-s with 5-s hold
DRL 3-s LH 8-s                            -- DRL 3-s with 8-s hold (Kramer & Rilling, 1970)
Conc(VI 30-s LH 5-s, VI 60-s LH 10-s)        -- Concurrent with per-component hold
Chain(FR 5, FI 30-s) LH 10-s              -- Hold on the entire chain expression
(Conc(VI 30-s, VI 60-s)) LH 10-s           -- Parenthesised expression with hold

-- Program-level LH default (applies individually to all base_schedules)
-- LH = 10-s
-- Conc(VI 30-s, VI 60-s, COD=2-s)       -- equivalent to Conc(VI 30-s LH 10-s, VI 60-s LH 10-s, COD=2-s)

-- Changeover Delay and Fixed-Ratio Changeover (§2.4)
Conc(VI 30-s, VI 60-s, COD=2-s)           -- 2-s changeover delay (Herrnstein, 1961)
Conc(VI 30-s, VI 60-s, COD=0-s)           -- explicit no-delay (control condition)
Conc(VI 30-s, VI 60-s, FRCO=5)           -- 5 fixed-ratio changeover (Hunter & Davison, 1985)
Conc(VI 30-s, VI 60-s, COD=2-s, FRCO=5)   -- both COD and FRCO

-- Program-level COD default (applies to all Conc in this program)
-- COD = 2-s
-- Conc(VI 30-s, VI 60-s)               -- inherits COD=2-s from param_decl

-- Repeat (syntactic sugar)
Tand(Repeat(3, FR 10), VI 60-s)          -- FR 10 × 3 then VI 60

-- Sidman free-operant avoidance (§2.7)
Sidman(SSI=20-s, RSI=5-s)                              -- basic Sidman avoidance (Sidman, 1953)
SidmanAvoidance(SSI=20-s, RSI=5-s)                     -- verbose alias
Sidman(ShockShockInterval=20-s, ResponseShockInterval=5-s) -- verbose parameter names
Chain(FR 10, Sidman(SSI=20-s, RSI=5-s))                 -- chained schedule with avoidance link

-- Lag schedule, operant variability (§2.8)
Lag 5                                                 -- Lag 5 shorthand; length defaults to 1
Lag(5)                                                -- parenthesized equivalent
Lag(5, length=8)                                      -- Page & Neuringer (1985) 8-peck sequence
Lag 0                                                 -- no variability requirement (equivalent to CRF)
Mult(Lag(5, length=8), CRF)                           -- Lag vs CRF baseline in multiple schedule

-- Discriminated avoidance (§2.9)
DiscriminatedAvoidance(CSUSInterval=10-s, ITI=3-min, mode=escape)       -- Solomon & Wynne (1953) style
DiscriminatedAvoidance(CSUSInterval=10-s, ITI=3-min, mode=escape, MaxShock=2-min) -- with safety cutoff
DiscriminatedAvoidance(CSUSInterval=10-s, ITI=3-min, mode=fixed, ShockDuration=0.5-s)  -- fixed US
DiscrimAv(CSUSInterval=10-s, ITI=3-min, mode=escape)                    -- short alias

-- Blackout (§2.5)
Mult(FR 5, EXT, BO=5-s)                            -- 5-s blackout between components
Mix(VI 30-s, VI 60-s, BO=3-s)                         -- 3-s blackout (undiscriminated)

-- Reinforcement Delay (§1.7; program-level apparatus delay)
-- RD = 500-ms
-- VI 60-s                                          -- all reinforcers delayed by 500 ms

-- Interpolated schedule (Ferster & Skinner, 1957)
Interpolate(FI 15-min, FI 1-min, count=16)              -- 16 reinforcements on FI 1 inserted into FI 15
Interp(FI 15-min, FR 50, count=10, onset=3-min)         -- with onset delay; Interp is short alias

-- Punishment overlay (§2.10)
Overlay(VI 60-s, FR 1)                              -- every response punished on VI 60 baseline
Overlay(Conc(VI 60-s, VI 180-s, COD=2-s), FR 1)        -- punishment on concurrent baseline

-- let bindings (macro expansion)
let baseline = VI 60-s
let probe = Conc(VI 30-s, VI 60-s)
Conc(baseline, probe)
```

## 3.7 Error Recovery Policy

Conforming parsers MUST follow this error recovery policy:

**Error reporting requirements (MUST):**
- Report at least one error with its error code, position (line and column), and error category (`LexError`, `ParseError`, or `SemanticError`).
- The error code MUST match one of the codes defined in `conformance/core/errors.json`.

**Multiple error recovery (SHOULD):**
- Parsers SHOULD implement **panic-mode recovery** (Aho et al., 2006, §4.8.2): upon detecting an error, discard input tokens until a synchronization token is reached, then resume parsing.
- Synchronization tokens: `)`, `,`, newline (`\n`), `EOF`.
- Report all detected errors as a list, ordered by position.

**Partial AST (MUST NOT):**
- Parsers MUST NOT return a partial AST when errors are present. On error, the result is an error list with no AST.

**Error limits (MAY):**
- Parsers MAY stop after a configurable maximum number of errors (recommended default: 10) to prevent cascading error noise.

**Rationale.** Single-error-then-stop forces users to fix one error at a time, which is unacceptable for a DSL where a single misplaced character can mask downstream issues. Panic-mode recovery is the simplest strategy that enables multi-error reporting while avoiding the complexity of phrase-level or error-production recovery (Aho et al., 2006, §4.8).
