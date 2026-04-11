# Formal Grammar

> Part of the [contingency-dsl theory documentation](theory.md). Defines the context-free grammar (BNF) for the DSL.

---

## 3.1 Design Principles

The DSL grammar satisfies four criteria:

1. **Notational fidelity**: Matches behavioral literature conventions (`FR5`, `conc VI30 VI60`).
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
                  | "PR" | "Repeat"
                  | "hodos" | "exponential" | "linear"
                  | "start" | "increment"
                  | "Sidman" | "SidmanAvoidance"
                  | "SSI" | "ShockShockInterval"
                  | "RSI" | "ResponseShockInterval"
                  | "Lag" | "length"

<compound>      ::= <combinator> "(" <arg_list> ")"
<combinator>    ::= "Conc" | "Alt" | "Conj"
                  | "Chain" | "Tand"
                  | "Mult" | "Mix"
<arg_list>      ::= <positional_args> ("," <keyword_arg>)*
<positional_args> ::= <schedule> ("," <schedule>)+
<keyword_arg>   ::= <kw_name> "=" <value>
<kw_name>       ::= "COD" | "ChangeoverDelay"
                   | "FRCO" | "FixedRatioChangeover"

<modifier>      ::= <dr_mod> | <pr_mod> | <repeat> | <lag_mod>
<dr_mod>        ::= ("DRL" | "DRH" | "DRO") <ws>? <value>
<pr_mod>        ::= "PR" ("(" <pr_opts> ")")?
<pr_opts>       ::= <pr_step> ("," <pr_param>)*
<pr_step>       ::= "hodos" | "exponential" | "linear"
<pr_param>      ::= "start" "=" <number>
                  | "increment" "=" <number>
<repeat>        ::= "Repeat" "(" <number> "," <schedule> ")"
<lag_mod>       ::= "Lag" <ws>? <number>
                  | "Lag" "(" <number> ("," <lag_kw_arg>)* ")"
<lag_kw_arg>    ::= "length" "=" <number>

<aversive_schedule> ::= <sidman_avoidance>
<sidman_avoidance>  ::= ("Sidman" | "SidmanAvoidance") "(" <sidman_arg> ("," <sidman_arg>)* ")"
<sidman_arg>        ::= <sidman_kw> "=" <value>
<sidman_kw>         ::= "SSI" | "ShockShockInterval"
                      | "RSI" | "ResponseShockInterval"
```

**Identifier naming constraint.** Identifiers must begin with a lowercase ASCII letter or underscore (`[a-z_]`), followed by any combination of ASCII letters, digits, or underscores. This ensures lexical disjointness from DSL keywords and schedule type prefixes, all of which begin with an uppercase letter. The `<reserved>` production additionally prevents lowercase keywords (`let`, `def`, `hodos`, etc.) from being used as identifiers. `def` is reserved for future use (see [architecture.md §4.4](architecture.md)).

## 3.3 Notational Flexibility

The grammar supports multiple notational forms matching behavioral literature conventions:

```
VI(60)       -- Python constructor form
VI60         -- Compact form (most common in papers)
VI 60        -- Whitespace-separated (Ferster & Skinner, 1957)
VI60s        -- Unit-annotated (disambiguation)
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
let baseline = VI60
let treatment = Conc(VI30, EXT)
Conc(baseline, treatment)
```

expands to:

```
Conc(VI60, Conc(VI30, EXT))
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
schedule = parse("Conc(VI 30s, VI 60s)")
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
FR5                                   -- Fixed Ratio 5
VI30s                                 -- Variable Interval 30 seconds
RR20                                  -- Random Ratio 20
EXT                                   -- Extinction
CRF                                   -- Continuous Reinforcement (= FR1)

-- Compound schedules
Conc(VI30s, VI60s, COD=2s)           -- Concurrent VI30 VI60 with 2s COD
Chain(FR5, FI30s)                     -- Chained FR5 then FI30
Alt(FR10, FI5min)                     -- Alternative FR10 or FI5min
Conj(FR5, FI30s)                      -- Conjunctive FR5 AND FI30
Tand(VR20, DRL5s)                     -- Tandem VR20 then DRL5
Mult(FR5, EXT)                        -- Multiple FR5/EXT
Mix(FR5, FR10)                        -- Mixed FR5/FR10

-- Nested compositions
Conc(Chain(FR5, VI60s), Alt(FR10, FT30s))

-- Modifiers
DRL5s                                 -- Differential Reinforcement of Low rate
DRO10s                                -- Differential Reinforcement of Other behavior
PR(hodos)                             -- Progressive Ratio (Hodos step)
PR(linear, start=1, increment=5)      -- Progressive Ratio (linear step)

-- Limited Hold (temporal availability constraint)
FI30 LH10                            -- FI 30s with 10s hold (Ferster & Skinner, 1957)
VI60 LH5                             -- VI 60s with 5s hold
DRL3 LH8                             -- DRL 3s with 8s hold (Kramer & Rilling, 1970)
Conc(VI30 LH5, VI60 LH10)           -- Concurrent with per-component hold
Chain(FR5, FI30) LH10                -- Hold on the entire chain expression
(Conc(VI30, VI60)) LH10              -- Parenthesised expression with hold

-- Program-level LH default (applies individually to all base_schedules)
-- LH = 10s
-- Conc(VI30, VI60, COD=2s)         -- equivalent to Conc(VI30 LH10, VI60 LH10, COD=2s)

-- Changeover Delay and Fixed-Ratio Changeover (§2.4)
Conc(VI30s, VI60s, COD=2s)           -- 2-s changeover delay (Herrnstein, 1961)
Conc(VI30s, VI60s, COD=0s)           -- explicit no-delay (control condition)
Conc(VI30s, VI60s, FRCO=5)           -- 5 fixed-ratio changeover (Hunter & Davison, 1985)
Conc(VI30s, VI60s, COD=2s, FRCO=5)   -- both COD and FRCO

-- Program-level COD default (applies to all Conc in this program)
-- COD = 2s
-- Conc(VI30s, VI60s)               -- inherits COD=2s from param_decl

-- Repeat (syntactic sugar)
Tand(Repeat(3, FR10), VI60s)          -- FR10 × 3 then VI60

-- Sidman free-operant avoidance (§2.7)
Sidman(SSI=20s, RSI=5s)                              -- basic Sidman avoidance (Sidman, 1953)
SidmanAvoidance(SSI=20s, RSI=5s)                     -- verbose alias
Sidman(ShockShockInterval=20s, ResponseShockInterval=5s) -- verbose parameter names
Chain(FR10, Sidman(SSI=20s, RSI=5s))                 -- chained schedule with avoidance link

-- Lag schedule, operant variability (§2.8)
Lag 5                                                 -- Lag 5 shorthand; length defaults to 1
Lag(5)                                                -- parenthesized equivalent
Lag(5, length=8)                                      -- Page & Neuringer (1985) 8-peck sequence
Lag 0                                                 -- no variability requirement (equivalent to CRF)
Mult(Lag(5, length=8), CRF)                           -- Lag vs CRF baseline in multiple schedule

-- let bindings (macro expansion)
let baseline = VI60s
let probe = Conc(VI30s, VI60s)
Conc(baseline, probe)
```
