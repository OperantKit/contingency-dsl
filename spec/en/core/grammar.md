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
                  | "target" | "changeover" | "all"     -- Overlay target kw_arg
                  | "PUNISH"                            -- Conc response-class-specific punishment
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
<keyword_arg>   ::= <scalar_kw_arg> | <directional_kw_arg>
                  | <overlay_kw_arg> | <punish_directive>
<scalar_kw_arg> ::= <kw_name> "=" <value>
<directional_kw_arg> ::= <kw_name> "(" <dir_ref> "->" <dir_ref> ")" "=" <value>
<dir_ref>       ::= <number> | <ident>
<kw_name>       ::= "COD" | "ChangeoverDelay"
                   | "FRCO" | "FixedRatioChangeover"
                   | "BO"  | "Blackout"

<!-- Overlay response-class targeting (§2.10) -->
<overlay_kw_arg> ::= "target" "=" <target_value>
<target_value>  ::= "changeover" | "all"

<!-- Response-class-specific punishment for Conc (§2.10.1) -->
<punish_directive> ::= "PUNISH" "(" <punish_target> ")" "=" <schedule>
<punish_target>    ::= "changeover"
                     | <dir_ref> "->" <dir_ref>
                     | <dir_ref>

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
Overlay(Conc(VI 30-s, VI 60-s, COD=2-s), FR 1,
        target=changeover)                          -- punishment on changeover only (Todorov, 1971)

-- Response-class-specific punishment directive (Conc kw_arg; §2.10.1)
Conc(VI 30-s, VI 60-s, COD=2-s, PUNISH(1->2)=FR 1, PUNISH(2->1)=FR 1)
                                                    -- asymmetric directional punishment
Conc(VI 30-s, VI 60-s, COD=2-s, PUNISH(changeover)=FR 1)
                                                    -- shorthand for all changeover directions
Conc(VI 30-s, VI 60-s, COD=2-s, PUNISH(1)=VI 30-s)     -- component-targeted punishment (de Villiers, 1980)

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

## 3.8 Experiment Layer — Multi-Phase Grammar (v2.0)

The Experiment Layer extends the DSL to describe multi-phase experimental designs — the across-session structure that JEAB Method sections encode as sequences of named conditions with phase-change criteria. This layer is **additive**: a file without `phase`, `progressive`, or `shaping` declarations is parsed as a single-phase `program` (fully backward compatible).

**Design rationale.** No existing formal notation unifies within-session contingency description (Mechner, 1959; State Notation, Snapper et al., 1982) with across-session experimental design structure (A-B-A-B notation, Cooper et al., 2020). JEAB papers describe these two levels in separate prose subsections of the Method. The Experiment Layer bridges this gap by embedding the existing schedule grammar within a phase-sequencing structure.

### 3.8.1 Top-Level Disambiguation

```bnf
<file>          ::= <experiment> | <program>
```

**LL(1) decision:** If the first non-annotation token is `phase`, `progressive`, or `shaping`, the file is an `experiment`. Otherwise it is a `program`. Since all three are lowercase reserved words not in `FIRST₁(Schedule)`, no ambiguity arises.

### 3.8.2 Experiment and Phase

```bnf
<experiment>    ::= <program_annotation>* (<phase_decl> | <progressive_decl> | <shaping_decl>)+

<phase_decl>    ::= "phase" <phase_name> ":" <phase_body>
<phase_name>    ::= <upper_ident>
<phase_body>    ::= <phase_meta>* (<phase_content> | <phase_ref> | "no_schedule") <annotation>*

<phase_meta>    ::= <session_spec> | <stability_spec>
<session_spec>  ::= "sessions" ("=" | ">=") <number>
<stability_spec> ::= "stable" "(" <stability_method> ("," <stability_param>)* ")"
<stability_method> ::= "visual" | "cv" | "relative-range" | "dual-criterion"
                     | "performance" | <ident>
<stability_param>  ::= <ident> "=" (<number> | <number> "%" | <string_literal> | <value>)

<phase_content> ::= <param_decl>* <binding>* <annotated_schedule>
<phase_ref>     ::= "use" <phase_name>
<upper_ident>   ::= [A-Z] [a-zA-Z0-9_]*
```

**Semantics:**
- `program_annotation`s before the first `phase`/`progressive`/`shaping` declaration establish experiment-level defaults. Phase-level annotations override (same resolution as program-level vs. schedule-level in Core).
- `sessions = N` specifies a fixed session count. `sessions >= N` specifies a minimum before stability criteria apply.
- `use <PhaseName>` copies the referenced phase's schedule expression. Forward references are not permitted.
- `no_schedule` declares a phase with no operant contingency. Used for Pavlovian revaluation, context exposure, habituation, or other procedures where no response-consequence relation is programmed. Resolves to `Phase.schedule = null` in the AST. Annotations (e.g., `@punisher`, `@context`) may still be attached to describe stimulus presentations.

### 3.8.3 Progressive Training (Syntactic Sugar)

**Sidman (1960) / Zeiler (1977) sense of "shaping"** — across-session parametric progression where the response class is already established and the schedule parameter is varied across sessions. Surface keyword: `progressive`. Distinct from `shaping` (§3.8.4), which denotes Skinner's within-session successive approximation of response topography.

```bnf
<progressive_decl>    ::= "progressive" <phase_name> ":" <progressive_body>
<progressive_body>    ::= <progressive_steps>+ <interleave_decl>* <phase_meta>* <param_decl>* <binding>* <annotated_schedule>
<progressive_steps>   ::= "steps" <ident> "=" "[" <number_list> "]"
<number_list>     ::= <number> ("," <number>)*
<interleave_decl> ::= "interleave" <phase_name> [ "no_trailing" ]
```

`progressive` desugars to a sequence of `phase` declarations, analogous to `Repeat(n, S)` → `Tand(S, ..., S)`. The schedule expression and annotation values may contain `{ident}` placeholders that reference `steps` variables.

**Expansion rule (E-PROGRESSIVE):**

```
progressive Name:
  steps x = [v₁, v₂, ..., vₙ]
  <meta>
  <schedule_template({x})>

  ≡  (desugars to)

phase Name_1: <meta>  <schedule_template(v₁)>
phase Name_2: <meta>  <schedule_template(v₂)>
...
phase Name_n: <meta>  <schedule_template(vₙ)>
```

**Multi-variable expansion (E-PROGRESSIVE-MULTI):** If multiple `steps` declarations are present, all lists must have identical length. Variables are zipped pairwise: `(x₁, y₁), (x₂, y₂), ...`.

**Interleave expansion (E-PROGRESSIVE-INTERLEAVE).** Optional `interleave` clauses insert clones of pre-declared phases between every pair of generated phases (and, by default, after the last one — *intercalate* semantics). The referenced phase becomes a **template**: it does not appear standalone in the resolved PhaseSequence at its declaration position. Each clone receives an auto-generated label `<ref>_after_<Name>_<i>` (1-based), e.g., `Recovery_after_DoseResponse_3`.

```
progressive Name:
  steps x = [v₁, ..., vₙ]
  interleave R          -- default: trailing clone included (intercalate)
  <meta>
  <schedule_template({x})>

  ≡  [ Phase(Name_1, ..., T(v₁)),
       clone(R, after=Name_1),
       Phase(Name_2, ..., T(v₂)),
       clone(R, after=Name_2),
       ...,
       Phase(Name_n, ..., T(vₙ)),
       clone(R, after=Name_n) ]
```

`interleave R no_trailing` suppresses the final clone (intersperse). Multiple `interleave` lines compose a gap block in declaration order; `no_trailing` on the last entry applies to the entire block. See [theory.md Definition 16](theory.md) for the formal denotational semantics including the `intercalate` and `intersperse` operators.

**Annotation locality.** Cloned phases inherit only the template's annotations and parameters. The enclosing progressive's annotations and `{ident}` placeholders affect only the generated `Name_i` phases — they do not leak into clones. This guarantees that a `Recovery` template referenced by multiple progressives runs identically (e.g., at a fixed reference dose) at every site.

### 3.8.4 Shaping (Skinner Response Shaping)

**Skinner (1953) / Catania (2013) sense of "shaping"** — within-session differential reinforcement of successive approximations to a terminal response class. Surface keyword: `shaping`. Distinct from `progressive` (§3.8.3), which denotes Sidman-sense across-session parameter progression.

Shaping is **syntactic sugar** that desugars to a single `Phase` (for `method=artful` or `method=percentile`) or to a `progressive_decl` (for `method=staged`). The primitive exists primarily for IDE auto-completion, required-field enforcement (Galbicka's Rule 2: "clearly define the terminal response"), and paper-to-DSL faithful transcription of under-specified Methods sections.

```bnf
<shaping_decl>    ::= "shaping" <phase_name> ":" <shaping_body>
<shaping_body>    ::= <shaping_meta>+ <phase_meta>* <annotation>*

<shaping_meta>    ::= <target_decl>           -- required
                    | <method_decl>           -- optional (default: artful)
                    | <approximations_decl>   -- optional
                    | <dimension_decl>        -- required when method=percentile
                    | <pctl_rank_decl>        -- required when method=percentile
                    | <pctl_window_decl>      -- optional (default: 20)
                    | <pctl_dir_decl>         -- optional (default: below)
                    | <stages_decl>           -- required when method=staged

<target_decl>         ::= "target" "=" <string_literal>
<method_decl>         ::= "method" "=" ("artful" | "percentile" | "staged")
<approximations_decl> ::= "approximations" "=" "[" <string_literal_list> "]"
<dimension_decl>      ::= "dimension" "=" <pctl_target>
<pctl_rank_decl>      ::= "percentile_rank" "=" <number>
<pctl_window_decl>    ::= "percentile_window" "=" <number>
<pctl_dir_decl>       ::= "percentile_dir" "=" <pctl_dir>
<stages_decl>         ::= "stages" "=" "[" <schedule_expr_list> "]"
```

**Desugar rules (D-SHAPING):**

```
shaping Name:
  target = "X"
  method = artful                      [default]
  approximations = ["a1", "a2", ...]   [optional]
  stable(...)                          [optional; default = ExperimenterJudgment]

  ≡  phase Name:
       @procedure("shape", target="X", method="artful",
                  approximations=["a1", "a2", ...])
       CRF
       [stability_spec | ExperimenterJudgment]
```

```
shaping Name:
  target = "X"
  method = percentile
  dimension = force
  percentile_rank = 50
  percentile_window = 20   [default]
  percentile_dir = below   [default]
  stable(...)              [required]

  ≡  phase Name:
       @procedure("shape", target="X", method="percentile", dimension="force")
       Pctl(force, 50, window=20, dir=below)
       [stability_spec]
```

```
shaping Name:
  target = "X"
  method = staged
  stages = [S₁, S₂, ..., Sₙ]
  stable(...)              [required]

  ≡  progressive Name:
       steps i = [1, 2, ..., n]         -- synthetic index
       [stability_spec]
       <stages[i-1]>                     -- each stage becomes a phase
```

**Reference:**
- Skinner, B. F. (1953). *Science and human behavior*. Macmillan.
- Catania, A. C. (2013). *Learning* (5th ed.). Sloan Publishing.
- Galbicka, G. (1994). Shaping in the 21st century: Moving percentile schedules into applied settings. *Journal of Applied Behavior Analysis*, 27(4), 739-760. https://doi.org/10.1901/jaba.1994.27-739
- Platt, J. R. (1973). Percentile reinforcement: Paradigms for experimental analysis of response shaping. In G. H. Bower (Ed.), *The psychology of learning and motivation* (Vol. 7, pp. 271-296). Academic Press.

**Design rationale:** [AST completeness vs execution orthogonality](../../../.local/context/ast-completeness-vs-execution-orthogonality.md) (method=artful is a declaration, not an executable specification; the DSL transcribes JEAB Methods that report "shaping by successive approximation" without losing that fact).

### 3.8.5 Usage Examples

**ABA Reversal (Brown et al., 2020, JEAB):**

```
@species("rat") @strain("Long-Evans") @n(5)
@reinforcer("food", type="pellet", magnitude="45mg", duration=3s)

phase Baseline:
  sessions = 25
  Conc(VI60s @operandum("target-lever"), EXT @operandum("inactive-lever"))

phase DRA:
  sessions = 14
  Conc(VI60s @operandum("target-lever"), VI15s @operandum("nose-poke"), COD=3s)

phase ExtinctionTest:
  sessions = 5
  Conc(EXT @operandum("target-lever"), EXT @operandum("nose-poke"))
```

**Progressive FI Training (Eckard & Kyonka, 2018, Behav Processes):**

```
@species("mouse") @strain("C57BL/6J") @n(27)
@reinforcer("sucrose", concentration="15%")

progressive FI_Training:
  steps v = [2, 4, 8, 12, 18]
  sessions >= 3
  stable(visual)
  FI {v}s LH3s

phase Peak_Baseline:
  sessions = 25
  FI18s LH3s

phase DRL_Intervention:
  sessions = 38
  DRL18s

phase Peak_Retest:
  sessions = 25
  use Peak_Baseline
```

**Parametric Dose-Response with Interleaved Recovery (John & Nader, 2016, JEAB style):**

In drug-self-administration dose-response designs, each test dose is followed by a recovery (return-to-baseline) period before the next dose. The `interleave` clause expresses this 1:1 with the Method statement *"each dose was followed by a return to baseline (≥ 3 sessions, visual stability)"*.

```
@species("rhesus monkey") @n(4)
@apparatus(chamber="primate-test", operandum="lever")

phase Recovery:
  sessions >= 3
  stable(visual)
  FI600s(FR30)
  @reinforcer("cocaine", dose="0.1mg/kg")

progressive DoseResponse:
  steps dose = [0.003, 0.01, 0.03, 0.1, 0.3, 0.56]
  interleave Recovery
  sessions >= 5
  stable(visual)
  FI600s(FR30)
  @reinforcer("cocaine", dose="{dose}mg/kg")
```

`phase Recovery` is declared **before** the progressive that references it (no forward references — constraint 74). Because it is referenced by `interleave`, the `Recovery` declaration becomes a *template* (constraint 76) and does not appear standalone in the resolved PhaseSequence; it materializes only as clones interspersed between dose conditions. The expansion produces 12 phases — 6 doses + 6 recoveries, matching the paper's Method exactly:

```
DoseResponse_1, Recovery_after_DoseResponse_1,
DoseResponse_2, Recovery_after_DoseResponse_2,
DoseResponse_3, Recovery_after_DoseResponse_3,
DoseResponse_4, Recovery_after_DoseResponse_4,
DoseResponse_5, Recovery_after_DoseResponse_5,
DoseResponse_6, Recovery_after_DoseResponse_6
```

**Parametric Dose-Response (Rickard et al., 2009, JEAB):**

```
@species("rat") @strain("Wistar") @n(15)
@session_end(rule="time", time=50min)

progressive DoseResponse:
  steps vol = [6, 12, 25, 50, 100, 200, 300]
  sessions = 30
  PR(exponential)
  @reinforcer("sucrose", concentration="0.6M", volume="{vol}ul")
```

### 3.8.6 Experiment-Level Semantic Constraints

| # | Constraint | Error Code | Level |
|---|---|---|---|
| 63 | Duplicate phase names | `DUPLICATE_PHASE_NAME` | SemanticError |
| 64 | Undefined `use` reference | `UNDEFINED_PHASE_REF` | SemanticError |
| 65 | Progressive steps length mismatch | `PROGRESSIVE_STEPS_LENGTH_MISMATCH` | SemanticError |
| 66 | Empty progressive steps list | `PROGRESSIVE_EMPTY_STEPS` | SemanticError |
| 67 | Undefined progressive placeholder | `PROGRESSIVE_UNDEFINED_VARIABLE` | SemanticError |
| 68 | Experiment-level annotation scoping | (inherits Core scoping) | — |
| 69 | Duplicate session_spec per phase | `DUPLICATE_SESSION_SPEC` | SemanticError |
| 70 | Duplicate stability_spec per phase | `DUPLICATE_STABILITY_SPEC` | SemanticError |
| 71 | `sessions >= 0` (nonpositive) | `SESSION_NONPOSITIVE` | SemanticError |
| 72 | `sessions = 0` (nonpositive) | `SESSION_NONPOSITIVE` | SemanticError |
| 73 | `no_schedule` body (Pavlovian / exposure phase) | (advisory; no error) | — |
| 74 | `interleave` references undeclared/forward phase | `UNDEFINED_PHASE_REF` | SemanticError |
| 75 | `interleave` self-reference (target = enclosing or later progressive_decl) | `PROGRESSIVE_SELF_INTERLEAVE` | SemanticError |
| 76 | Template consumption — referenced phase removed from standalone PhaseSequence | (semantics; no error) | — |
| 63b | `interleave` clone label collides with user-declared phase | `DUPLICATE_PHASE_NAME` | SemanticError |
| 83 | `shaping` missing required `target` | `MISSING_SHAPING_TARGET` | SemanticError |
| 84 | `shaping` unknown `method` value | `UNKNOWN_SHAPING_METHOD` | SemanticError |
| 85 | `shaping` method=percentile missing `dimension` / `percentile_rank` / criterion | `INCOMPLETE_PERCENTILE_SHAPING` | SemanticError |
| 86 | `shaping` method=staged missing `stages` / criterion | `INCOMPLETE_STAGED_SHAPING` | SemanticError |
| 87 | `shaping` method=artful: both stability_spec and session_spec absent ⇒ default ExperimenterJudgment | (advisory; no error) | — |
| 88 | `percentile_rank` out of range | `PCTL_INVALID_RANK` | SemanticError |
| 89 | `percentile_window` non-positive | `PCTL_INVALID_WINDOW` | SemanticError |
| 90 | Duplicate shaping_meta declaration | `DUPLICATE_SHAPING_META` | SemanticError |
| 91 | shaping_meta forbidden for chosen method | `SHAPING_META_METHOD_MISMATCH` | SemanticError |
| 92 | Empty string in `approximations` | `EMPTY_APPROXIMATION_LABEL` | SemanticError |
| 93 | `stages` list contains fewer than 2 elements | `SHAPING_INSUFFICIENT_STAGES` | SemanticError |

### 3.8.7 LL(1) Verification

All Experiment Layer decision points are LL(1):

| Decision Point | Lookahead | Token Sets |
|---|---|---|
| `file → experiment \| program` | 1 | `{phase, progressive, shaping}` vs. all others |
| `(phase_decl \| progressive_decl \| shaping_decl)+` | 1 | `phase` vs. `progressive` vs. `shaping` |
| `phase_meta → session_spec \| stability_spec` | 1 | `sessions` vs. `stable` |
| `session_spec → "=" \| ">="` | 1 | `=` vs. `>=` |
| `phase_content \| phase_ref` | 1 | `use` vs. all others |
| `progressive_body: interleave_decl* vs. phase_meta*` | 1 | `interleave` vs. `{sessions, stable, ...}` |
| `shaping_body: shaping_meta+` | 1 | `{target, method, approximations, dimension, stages, percentile_*}` vs. FOLLOW |
| `interleave_decl: optional "no_trailing"` | 1 | `no_trailing` vs. FOLLOW (`interleave`, `sessions`, `stable`, `let`, `@`, schedule starters) |

No new LL(2) decision points are introduced. See [LL(2) Formal Proof §11](ll2-proof.md) for the verification.
