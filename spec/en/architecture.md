# Computability, Expressiveness, and Architectural Boundaries

> Part of the [contingency-dsl theory documentation](theory.md). Describes the Ψ six-layer architecture, computability properties, and annotation system.

---

## 4.1 Ψ Six-Layer Architecture

Reinforcement schedules describe inherently **infinite processes**. A VI 60 schedule can run indefinitely; an FR 10 continues producing reinforcement as long as responses continue. This is not a defect but an essential property of behavioral contingencies. Pavlovian (respondent) procedures introduce an orthogonal structural axis: two-term CS–US relations that do not require an operant response.

The DSL is organized by **scientific category**. Layers inside `contingency-dsl` follow the Pavlov / Skinner distinction (two-term vs three-term contingency) at the directory level; composed procedures (e.g., conditioned suppression, Pavlovian-to-instrumental transfer) are a first-class sibling category, not a sub-case of either. Turing-complete runtime is delegated to sibling packages (`contingency-core`, `experiment-core`):

```
┌───────────────────────────────────────────┐
│ contingency-dsl                            │
│ ┌─────────────────────────────────────────┐│
│ │ Annotation (program-scoped, extensions/) ││
│ ├─────────────────────────────────────────┤│
│ │ Experiment (phase-sequence, context,     ││
│ │             criteria)                     ││
│ ├─────────────────────────────────────────┤│
│ │ Composed (CER, PIT, autoshape, omission, ││
│ │           two-process)                    ││
│ ├────────────────────┬────────────────────┤│
│ │ Operant (3-term)   │ Respondent (2-term)││
│ │  - schedules/      │  - Tier A primitives││
│ │  - stateful/       │  - extension point  ││
│ │  - trial-based/    │                     ││
│ ├────────────────────┴────────────────────┤│
│ │ Foundations (CFG/LL(2), contingency type,││
│ │              time, stimulus, valence,    ││
│ │              context)                     ││
│ └─────────────────────────────────────────┘│
├───────────────────────────────────────────┤
│ contingency-core (TC, dynamic)             │
├───────────────────────────────────────────┤
│ experiment-core (TC + constraints,         │
│                  finalization)              │
└───────────────────────────────────────────┘
```

**Why Operant and Respondent are sibling categories (not nested under a common "Paradigm" node).** The three-term contingency (SD-R-SR) and the two-term contingency (CS-US) are structurally distinct relations, not two parameterizations of a common super-relation. The operant analysis (Skinner, 1938) asks under what discriminative stimulus a response produces a consequence; the respondent analysis (Pavlov, 1927) asks what CS-US temporal / probabilistic relationship predicts the US. Attempting to nest them under a shared "Paradigm" node either (a) forces an artificial parameterization that obscures their distinct grammars, or (b) collapses the three-term and two-term structures into one, which misrepresents the discipline. They share only the neutral foundations (time scales, stimulus typing, valence, context) and a first-class composition point (`composed/`) for operant × respondent procedures.

**TC vs non-TC boundary (unchanged).** Foundations + Operant + Respondent remain CFG and non-TC. `contingency-core` and `experiment-core` remain Turing-complete. The Composed layer inherits the non-TC property from its Operant × Respondent constituents; it composes existing non-TC grammars and does not introduce new computational power.

The **Experiment layer** sits above the Foundations / Operant / Respondent / Composed layers within contingency-dsl. It arranges non-TC expressions into ordered phases with declarative phase-change criteria (Stability, FixedSessions, PerformanceCriterion), covering the common experimental designs found in JEAB papers. The lower layers describe *what each contingency is*; the Experiment layer describes *how those contingencies are sequenced across phases* in a declarative, non-procedural manner. For arbitrary runtime-conditioned transitions (e.g., rate-based schedule switching), `contingency-core` remains the appropriate layer.

A phase may declare `no_schedule` to indicate that no operant contingency is active during that phase. This covers Pavlovian revaluation procedures, context exposure, habituation, and other experimental intervals where no response-consequence relation is programmed. Such phases resolve to `Phase.schedule = null` in the AST; annotations (e.g., `@punisher`, `@context`) and respondent-layer expressions may still describe stimulus presentations or environmental conditions.

The Experiment layer follows the JEAB convention: Subjects and Apparatus annotations are shared across phases (inherited unless overridden), while each Phase specifies its own schedule and phase-change criterion. See `schema/experiment/phase-sequence.schema.json` for the full schema. Context is first-class (`foundations/context.md`, `experiment/context.md`) so that renewal, reinstatement, and context-driven respondent designs can be expressed via the respondent extension point (see design-philosophy §5.4).

The Operant layer is subdivided along two independent axes inherited from the previous five-layer architecture:

```
                      Response Opportunity
                 Free-operant       Discrete trial
                 ┌────────────────┬────────────────┐
  Criterion      │                │                │
  Literal        │ Operant.Literal│ Operant.       │
                 │ (schedules/)   │   TrialBased   │
                 │ FR,VI,DRL      │ (trial-based/) │
                 ├────────────────┤   MTS,         │
  Runtime        │ Operant.       │   Go/NoGo      │
  state          │   Stateful     │                │
                 │ (stateful/)    │                │
                 │ Pctl,Adj       │                │
                 └────────────────┴────────────────┘
```

The Respondent layer is uniform at this resolution: it hosts the Tier-A primitives enumerated in design-philosophy §2 plus the Respondent extension point (§5.4). Depth beyond Tier A (blocking, overshadowing, latent inhibition, renewal, reinstatement, etc.) is delegated to the companion package `contingency-respondent-dsl`.

| Layer | Directory | Computational Power | Describes | Examples |
|-------|-----------|---------------------|-----------|----------|
| **Annotation** | `annotations/` | Metadata (program-scoped) | Subjects, Apparatus, Procedure, Measurement; extensions (respondent-annotator, learning-models-annotator) | `@species("rat")`, `@cs("tone", duration=10s)`, `@model(RW)` |
| **Experiment** | `experiment/` | Declarative (enumerated criteria) | Multi-phase experimental designs, phase-change criteria, first-class Context | `PhaseSequence(Acquisition→Extinction→Test)`, `Stability(5, 10%)`, `FixedSessions(10)` |
| **Composed** | `composed/` | Non-TC (inherits from components) | Operant × Respondent composites | `CER`, `PIT`, `Autoshaping`, `Omission`, `TwoProcess` |
| **Operant** | `operant/` | CFG (non-TC) | Three-term contingency (SD-R-SR) | `FR 5`, `Conc(VI 30-s, VI 60-s)`, `Pctl(IRT, 50)`, `MTS(comparisons=3, consequence=CRF, ITI=5s)` |
| **Respondent** | `respondent/` | CFG (non-TC) | Two-term contingency (CS-US) — Tier A primitives + extension point | `Pair.ForwardDelay(cs, us)`, `Contingency(0.9, 0.1)`, `Differential(cs+, cs−)` |
| **Foundations** | `foundations/` | CFG / type theory (non-TC) | Paradigm-neutral formal base: CFG/LL(2), contingency type (2-term vs 3-term, contingent vs non-contingent), time scales, stimulus typing (SD, SΔ, CS, US, Sr+, Sr−), valence, context | Meta-grammar, type definitions |
| **contingency-core** | sibling package | Turing-complete | Dynamic contingency transitions | Rate-based schedule switching, arbitrary GTS transitions |
| **experiment-core** | sibling package | TC + constraints | Experimental finalization and verification | Exit conditions, ABA designs, safety constraints |

**contingency-core** (Turing-complete) enables:
- "Switch from VR to VI when response rate exceeds threshold"
- "Adaptive DRO with externally-conditioned adjustment rules (e.g., if rate < threshold then increase DRO interval, else decrease by 2×step)"
- "Titration with conditional branching logic (e.g., adjust step size based on multi-trial outcome pattern)"
- "Yoking procedures (one subject's schedule parameters determined by another subject's behavior)"

**experiment-core** (TC + constraints) guarantees:
- Termination (session exit conditions enforced)
- Static verification ("Does this schedule ever produce reinforcement?")
- Safety (reinforcement rate bounds, session time limits)
- Structural validity of experimental designs (A1-A2 identity in ABA)

Therefore:
- `until` clauses belong in experiment-core, not contingency-dsl
- contingency-dsl concerns itself with static contingency structure and declarative phase sequences
- Arbitrary dynamic transitions (runtime-conditioned) are contingency-core's responsibility
- Finalization and verification are experiment-core's responsibility

## 4.1.1 Operational Boundary: contingency-dsl vs. contingency-core

The Ψ layer diagram above uses the terms "static" and "dynamic" informally. This section provides an **operational definition** — a litmus test that determines, for any given procedure, which layer it belongs to. The test is semantically unchanged from the previous architecture; only the layer labels on the DSL side are renamed (`Core` → `Operant.Literal`, `Core-Stateful` → `Operant.Stateful`, `Core-TrialBased` → `Operant.TrialBased`, and the Respondent layer is an additional CFG non-TC sibling to which the same SEI reasoning applies).

### One-Sentence Summary

> contingency-dsl describes *what the contingency is*; contingency-core describes *how the contingency changes into a different contingency*.

### Schedule Expression Invariance (SEI) — The Three-Property Test

A procedure belongs to contingency-dsl (any of Operant.Literal, Operant.Stateful, Operant.TrialBased, or Respondent) if and only if **all three** of the following properties hold. Violation of any single property places it in contingency-core.

**P1 — Expression Tree Fixity.** The schedule expression tree (AST) is fully determined at parse time and does not structurally change during the session. The set of schedule nodes, their types, and their combinatorial structure remain identical from the first reinforcement cycle to the last.

**P2 — Parameter Enumerability.** All schedule parameters are either (a) literal values determined at parse time, or (b) computed by a closed-form function whose definition is itself a literal, parse-time-fixed specification. The *rule* for computing a parameter is fixed; only its *output* may vary.

**P3 — Single-Schedule Identity.** The schedule can be identified by a single, stable expression throughout the session. There is no point during the session at which the active contingency transitions to a structurally different schedule expression not already present as a subtree of the original expression.

### Decision Flowchart

```
Is the AST fully determined at parse time? (P1)
  NO  → contingency-core
  YES → Are all parameters literal or computed by a parse-time-fixed rule? (P2)
    NO  → contingency-core
    YES → Does the schedule identity remain invariant — no transitions
          to a schedule not already a subtree of the original expression? (P3)
      NO  → contingency-core
      YES → Is the procedure two-term (CS-US, no operant response)?
        YES → Respondent (Tier A or respondent extension point)
        NO  → Are response opportunities discrete trials?
          YES → Operant.TrialBased
          NO  → Are criteria compared against literal values?
            YES → Operant.Literal
            NO (compared against runtime-computed values) → Operant.Stateful
```

### Comparison Table

| Property | Operant.Literal | Operant.Stateful | Operant.TrialBased | Respondent | contingency-core |
|---|---|---|---|---|---|
| AST structure | Fixed at parse time | Fixed at parse time | Fixed at parse time | Fixed at parse time | Changes during session |
| Parameters | Literal values | Literal values | Literal values | Literal values | May be computed or switched |
| Criterion value | Literal | f(runtime_state), rule fixed at parse time | Stimulus–response matching | N/A (CS-US temporal / probabilistic structure) | May depend on arbitrary state |
| Response opportunity | Free-operant (continuous) | Free-operant (continuous) | Discrete trial | N/A (no operant response) | Any |
| Consequence | Implicit | Implicit | Explicit (operant schedule ref) | US presentation per CS-US structure | Any |
| Active schedule identity | Invariant | Invariant | Invariant | Invariant | Transitions to different schedule |
| Contingency type | Three-term (SD-R-SR) | Three-term (SD-R-SR) | Three-term (SD-R-SR) | Two-term (CS-US) | Any |
| Computational model | CFG (non-TC) | CFG syntax, TC-proximate eval | CFG syntax | CFG (non-TC) | Turing-complete |

The critical distinction between Operant.Stateful and contingency-core: in Operant.Stateful, the schedule expression is **self-contained** — the criterion computation rule is declared within the expression itself (e.g., `Pctl(IRT, 50)` declares a fixed percentile rule). In contingency-core, the system must evaluate **external conditions** (response rate, multi-trial outcome patterns, another subject's behavior) to determine which schedule expression should be **currently active**, and that expression may be structurally different from the previous one.

The Respondent layer applies the same SEI reasoning at the two-term contingency level: a `Pair.ForwardDelay(cs, us, isi=...)` or `Contingency(p_us_given_cs, p_us_given_no_cs)` expression is fully parse-time-determined; it does not transition to a structurally different CS-US expression based on runtime state. Procedures that require such transitions (e.g., a renewal design where the CS-US contingency shifts based on external context changes) are handled by the Respondent extension point plus the Experiment layer's phase-sequence structure, not by primitive-level mutation.

### Boundary Case Classifications

**Case 1: Adaptive DRO.**

- *Fixed step-function adaptation* (e.g., threshold increases by 1 s on each criterion achievement): expressible as `Adj(delay, start=5s, step=1s)`. All three properties hold. → **Operant.Stateful.**
- *Externally-conditioned adaptation* (e.g., if response rate drops below X, increase threshold; otherwise decrease by 2× step): the parameter computation rule itself is a conditional expression, not a fixed closed-form function. P2 is violated. → **contingency-core.**

**Case 2: Titration.**

- *Fixed staircase method* (e.g., +0.1 on correct, −0.1 on incorrect): expressible as `Adj(amount, start=0.4, step=0.1)`. Structurally identical to Progressive Ratio — the rule is fixed at parse time; only the current value varies. → **Operant.Stateful.**
- *Conditional-branching titration* (e.g., increase if correct on 3 of last 5 trials, otherwise decrease by 2× step): requires control flow that the DSL cannot express. P2 is violated. → **contingency-core.**

**Case 3: Phase-internal schedule changes.**

- *Fixed sequential order* (e.g., "complete FR 5 ten times, then VI 30"): expressible as `Tand(Repeat(10, FR 5), VI 30-s)`. The transition target is a subtree already present in the original AST. All three properties hold. → **Operant.Literal.**
- *Behavior-criterion-triggered transition* (e.g., "switch from FR 5 to VI 30 when response rate exceeds threshold"): the AST must change from one schedule to a structurally different one based on an external evaluation. P1 and P3 are violated. → **contingency-core.**

**Case 4: Discriminated avoidance.**

Discriminated avoidance (Solomon & Wynne, 1953) has a clear trial structure: CS onset → response window (CSUSInterval) → US or no US → ITI → next CS onset. This superficially resembles discrete trial procedures such as MTS.

However, the response opportunity *within* each trial is free-operant: the subject can respond at any moment during the CS-US interval, may emit multiple responses, and response latency is a primary dependent variable. The trial structure constrains *when the avoidance contingency is active* (signaled vs. unsignaled periods), not *how the subject responds*. This is analogous to a `Mult(avoidance, EXT)` arrangement where the CS signals the active component.

Operant.TrialBased requires that the response opportunity itself be discrete — a selection among presented alternatives (e.g., comparison stimuli in MTS). In discriminated avoidance, no such selection exists; the response is the same operant (e.g., lever press, shuttle crossing) available continuously within the signaled period.

Additionally, discriminated avoidance shares its aversive contingency structure with Sidman avoidance (free-operant, Core). The CS in discriminated avoidance adds a discriminative stimulus to the same underlying avoidance contingency; it does not transform the response opportunity from free-operant to discrete trial.

- All three SEI properties hold. Response opportunities are free-operant within trial boundaries. → **Operant.Literal.**

### Recommended Computational Model for contingency-core: Guarded Transition System (GTS)

Based on the SEI definition, contingency-core's defining characteristic is *schedule expression transitions conditioned on runtime behavioral state*. This maps naturally to a **guarded transition system**:

```
State      = ScheduleExpr            -- each state is a contingency-dsl expression
Guard      = BoolExpr(RuntimeState)  -- condition on behavioral observables
Transition = (State, Guard, State)   -- if guard is satisfied, transition S1 → S2
```

**Properties:**

| Property | Specification |
|---|---|
| States | Each state is a valid contingency-dsl expression (any of Operant.Literal, Operant.Stateful, Operant.TrialBased, Respondent, or Composed) |
| Guards | Boolean expressions over defined runtime observables (response rate, reinforcement count, time elapsed, cumulative responses, etc.) |
| Transitions | Deterministic: at most one guard may be true at any point, or a priority ordering resolves ties |
| Initial state | The first state in the definition |
| Terminal states | States with no outgoing transitions (session continues under this schedule until experiment-core terminates) |
| Composability | A contingency-core program is itself a valid "schedule" for experiment-core to wrap with exit conditions |

This model preserves composability: contingency-dsl expressions form the *vocabulary* (what a contingency is), and contingency-core transitions form the *grammar* (how contingencies change). Experiment-core then provides *finalization* (making the whole thing a finite experiment).

---

## 4.2 Branching Is Inherent in the Combinator Algebra

The claim that the DSL lacks "runtime conditional branching" is misleading. The compound schedule combinators themselves provide declarative branching mechanisms:

| Type of branching | Combinator | Control agent |
|-------------------|-----------|--------------|
| Behavioral choice | Conc | Subject selects operandum |
| Link completion | Chain, Tand | Contingency satisfaction drives transition |
| Stimulus-controlled context switch | Mult, Mix | Environment presents S^D |
| Satisfaction-based selection | Alt (OR), Conj (AND) | Which component is satisfied first |

What imperative programming expresses via `if/else/for`, behavior analysis expresses as typed combinators. This is not "no branching because non-Turing-complete" but rather "branching algebraically structured within the type system."

## 4.3 The Repeat Combinator

"Complete FR 10 three times, then switch to VI 60" is expressible with existing combinators:

```
Chain(FR 10, FR 10, FR 10, VI 60-s)  -- explicit unfolding
Tand(FR 10, FR 10, FR 10, VI 60-s)   -- without S^D change
```

The `Repeat(n, S)` combinator reduces verbosity:

```
Tand(Repeat(3, FR 10), VI 60-s)
```

**Formal definition:**
```
Repeat(n, S) ≡ Tand(S, S, ..., S)   for finite n ∈ ℕ
                    └── n copies ──┘
```

Repeat is syntactic sugar that does not increase computational power. It unfolds to a finite Tand at semantic analysis time.

**Algebraic properties of Repeat** (derived from desugaring `Repeat(n, S) ≡ Tand(S, ..., S)`):

**Identity:**
```
Repeat(1, S) ≡ S
```

**Exponent rule:**
```
Repeat(m, Repeat(n, S)) ≡ Repeat(m×n, S)
```

**Additive decomposition:**
```
Repeat(m+n, S) ≡ Tand(Repeat(m, S), Repeat(n, S))
```

**Completeness as syntactic sugar:** Repeat(n, S) always expands to finite Tand, therefore stoppage of expressions containing Repeat is guaranteed by stoppage of Tand. Repeat semantics completely reduce to Tand semantics (transparent syntactic sugar).

**Nested Repeat expansion strategy:** Desugaring proceeds inside-out: inner Repeat nodes are expanded first, then outer Repeat wraps the result. After expansion, Theorem 2 (Associativity) applies: `Tand(A, Tand(B, C)) ≡ Tand(A, B, C)`. Conformant implementations MUST flatten same-combinator nesting after Repeat expansion, producing the canonical N-ary form.

*Example:*
```
Repeat(2, Repeat(3, FR 5))
→ (inner expansion)  Repeat(2, Tand(FR 5, FR 5, FR 5))
→ (outer expansion)  Tand(Tand(FR 5, FR 5, FR 5), Tand(FR 5, FR 5, FR 5))
→ (Theorem 2 flatten) Tand(FR 5, FR 5, FR 5, FR 5, FR 5, FR 5)
```

Conformant implementations MUST also reduce `Repeat(1, S)` to `S` (not `Tand(S)`).

**Distinction from Mix:** `Mix(FR 10, VI 60-s)` is undiscriminated alternation (environment-controlled, typically random selection). `Tand(Repeat(3, FR 10), VI 60-s)` is sequential completion (FR 10 completed three times before transitioning to VI 60). These are distinct contingencies.

## 4.4 Variable Bindings as Macro Expansion

Variable bindings can be introduced without adding Turing completeness:

```
let baseline = VI 60-s
let treatment = Conc(VI 30-s, EXT)
let reversal = baseline
```

This is macro expansion (textual substitution) — no mutable state, no closures, no recursion. `let` is eliminated at parse time, yielding a let-free syntax tree. The resulting program is within the base CFG.

Potential extensions, all reducible to macro expansion:
- Parameterized templates: `def matching(a, b) = Conc(VI(a), VI(b))` → `matching(30, 90)`
- Annotations: `FR 10 @label("component A")` — metadata for analysis/visualization

None of these raise the position in the Chomsky hierarchy, provided the following well-formedness condition is enforced:

> **Well-formedness condition for `def`.** Let G = (V, E) be the directed graph where V is the set of `def` names and (f, g) ∈ E iff the body of f contains a call to g. G must be a directed acyclic graph (DAG). The parser SHALL reject any definition set where G contains a cycle (including self-loops and mutual recursion). This ensures that `def` expansion always terminates and the output remains within the base CFG.

`def` is deferred to a future version (not included in the v1.0 BNF). The keyword is reserved ([grammar.md §3.2](grammar.md)) to prevent identifier collisions.

## 4.5 Position in the Chomsky Hierarchy and Static Verification

The contingency-dsl is a **context-free grammar (CFG)**:
- Recursively nested parenthetical structure
- No context-sensitive dependencies or recursive function definitions
- Parseable by recursive descent in O(n)
- `let` / `Repeat` expand to pure CFG at parse time; `def` (when introduced) will also expand to pure CFG, subject to the DAG well-formedness condition (§4.4)

**Statically verifiable properties** (enabled by non-Turing-completeness):
- "Does this schedule ever produce reinforcement?" (reachability)
- "Are all components reachable?" (dead code detection)
- "Does Concurrent have ≥ 2 components?" (structural validity)
- "Does every Conc specify a COD?" (linter warning if omitted; Herrnstein, 1961)

These properties are decidable by syntax tree traversal. In a Turing-complete language, they reduce to the halting problem and are generally undecidable.

## 4.6 Controlled Extension Points

- **PR step functions**: Enumerated within the DSL (`hodos`, `linear`, `exponential`, `geometric`). Arbitrary functions available only via the Python API.
- **Fleshler-Hoffman generation**: `seed` parameter for deterministic generation. Runtime randomness is the engine's responsibility.
- **DR thresholds**: Scalar values only in Operant.Literal. Fixed step-function adaptation (e.g., `Adj(delay, start=5s, step=1s)`) belongs in Operant.Stateful. Only adaptive DRO with externally-conditioned adjustment rules (conditional branching on behavioral criteria) is delegated to contingency-core. See §4.1.1 for the operational boundary definition.

## 4.7 Annotation Architecture — Orthogonal Annotation Dimensions

The base DSL defines a schedule expression as a point in *schedule-space*: the structure of reinforcement contingencies. Annotators add **orthogonal coordinate axes** (dimensions) to that space through annotations. Each annotator contributes an independent axis; composing annotators forms the Cartesian product of their axes. An unannotated schedule lives in the base subspace — fully backward-compatible.

This design principle — *annotations that add dimensions to a simple core* — enables creative composition: a single schedule expression can simultaneously carry stimulus identity, subject assignment, temporal parameters, and clinical metadata without any modification to the base grammar.

**Two-level scoping.** Annotations may appear at two positions in the grammar:

1. **Program-level** (`program_annotation`): before `param_decl*`. Acts as session-wide default. Matches the paper structure where Subjects and Apparatus precede Procedure.
2. **Schedule-level** (in `annotated_schedule`): attached to a specific schedule expression. Overrides program-level for that expression.

```
resolve(key, S) = S.annotations[key]  if key ∈ S.annotations
                  program.annotations[key]  otherwise
```

See [annotation-design.md](annotation-design.md) §6 for full specification.

### 4.7.1 Motivation

**Multi-Subject Contingencies.** Behavioral pharmacology cooperation tasks — "Subject A's lever press produces reinforcement for Subject B" — require contingency mappings across subjects. The base DSL assumes a single implicit subject. Multi-subject contingencies introduce a new dimension: **subject** as a dimension of stimulus.

**Shared Reinforcers.** "Schedules A and C use the same food pellet reinforcer" — reinforcer identity is not expressible in the base CFG, which models only R-SR rules (schedule structure), not reinforcer properties. DSL-level reinforcer identity enables specification-level comparison with associative learning theories (Rescorla & Wagner, 1972), type-guaranteed reinforcer identity, and formal description of conditional reinforcement dynamics.

**Temporal Context.** Session-level temporal parameters (clock source, warm-up intervals) are orthogonal to schedule structure but must be declarable alongside it. Note: blackout (BO) has been promoted to core grammar as a Mult/Mix keyword argument, since BO duration directly affects inter-component behavioral independence (Reynolds, 1961; Bouton, 2004).

**Clinical Metadata.** ABA practitioners need to annotate schedules with functional behavior assessment results (function of behavior, target/replacement behavior labels) without polluting the schedule grammar.

### 4.7.2 Annotator Taxonomy

Each annotator is named with the `-annotator` suffix, meaning: *an annotation module that adds an orthogonal dimension to the base DSL*.

Recommended annotator names match JEAB Method section headings 1:1 (see
[annotation-design.md §3.7](annotation-design.md)). The 2026-04-12
annotator reorganization established this correspondence.

| Annotator | JEAB Category | Annotation Keywords | Purpose |
|-----------|---------------|---------------------|---------|
| `procedure-annotator` | **Procedure** | (see sub-annotators below) | Procedure-level information, split into stimulus and temporal sub-annotators |
| &nbsp;&nbsp;└ `procedure-annotator/stimulus` | Procedure | `@reinforcer`, `@sd`, `@brief` | Stimulus identity: reinforcers, discriminative stimuli, second-order brief stimuli |
| &nbsp;&nbsp;└ `procedure-annotator/temporal` | Procedure | `@clock`, `@warmup`, `@algorithm` | Session-level temporal parameters |
| `subjects-annotator` | **Subjects** | `@species`, `@strain`, `@deprivation`, `@history`, `@n` | Subject conditions (renamed from `subject-annotator` on 2026-04-12 to match JEAB plural heading) |
| `apparatus-annotator` | **Apparatus** | `@chamber`, `@operandum`, `@interface`, `@hardware` (alias: `@hw`) | Physical chambers, response devices, hardware interfaces. `@operandum` moved from `stimulus-annotator` on 2026-04-12 to align with JEAB Method section conventions. |
| `measurement-annotator` | **Measurement** | `@session_end`, `@baseline`, `@steady_state`, `@dependent_measure`, `@training_volume`, `@microstructure`, `@phase_end`, `@logging`, `@iri_window`, `@warmup_exclude` | Session termination rules, baseline conditions, steady-state criteria, dependent variables, training volume, response microstructure, phase termination, event logging, IRI analysis, warmup exclusion. Introduced 2026-04-12; completed 2026-04-14. |

**Extensions** (outside the four JEAB categories, under `annotations/extensions/`):

| Extension | Keywords (candidate) | Domain |
|---|---|---|
| `extensions/social-annotator` | `@subject`, `@ibc` | Multi-subject contingencies, cooperation tasks. `@ibc` = Interlocking Behavioral Contingencies (Glenn, 2004) |
| `extensions/clinical-annotator` | `@function`, `@target`, `@replacement` | ABA intervention metadata, FBA results |

**Orthogonality constraint:** Annotation keywords across all annotators are mutually disjoint. Multiple annotators can annotate the same schedule expression simultaneously:

```
FR 5 @reinforcer("food") @subject("A") @clock("real", unit="s") @function("escape")
```

### 4.7.3 Package Architecture

All annotators live as submodules within **contingency-annotator**. The base DSL (`contingency-dsl`) defines only the `AnnotationModule` protocol; concrete annotators are never part of the base package. Annotator names correspond 1:1 to JEAB Method section headings (see [annotation-design.md §3.7](annotation-design.md)).

```
contingency-dsl (base CFG)
  │  = Schedule structure (3×3 atomic + 7 combinators + DR + PR + Repeat + let + aversive)
  │  = Depends only on contingency-py
  │  = Defines: AnnotationModule Protocol, AnnotatedSchedule, AnnotationRegistry
  │
  └── contingency-annotator (annotation package)
        │  Shared types: Reinforcer hierarchy, AssociativeState, LearningRule,
        │  StimulusManager, OfflineRunner
        │
        ├── procedure_annotator/ (JEAB category: Procedure)
        │     │
        │     ├── stimulus/ (sub-annotator)
        │     │     + @reinforcer, @sd, @brief annotations
        │     │     + Reinforcer identity, S-S / S-R formal descriptions
        │     │     + Note: @operandum moved to apparatus_annotator on 2026-04-12
        │     │
        │     └── temporal/ (sub-annotator)
        │           + @clock, @warmup, @algorithm annotations
        │           + Session-level temporal parameter declaration
        │           + Note: BO and COD promoted to core grammar
        │
        ├── subjects_annotator/ (JEAB category: Subjects; renamed from subject_annotator on 2026-04-12)
        │     + @species, @strain, @deprivation, @history, @n annotations
        │
        ├── apparatus_annotator/ (JEAB category: Apparatus)
        │     + @chamber, @operandum, @interface, @hardware annotations
        │     + Physical chamber, response device, HW interface identity
        │
        ├── measurement_annotator/ (JEAB category: Measurement; introduced 2026-04-12, completed 2026-04-14)
        │     + @session_end, @baseline, @steady_state
        │     + @dependent_measure, @training_volume, @microstructure
        │     + @phase_end, @logging, @iri_window, @warmup_exclude
        │     + Session termination, baseline, steady-state, DV declaration,
        │     + training exposure tracking, response microstructure analysis,
        │     + phase termination, event logging, IRI analysis, warmup exclusion
        │
        └── extensions/ (outside the four JEAB categories)
              │
              ├── social_annotator/ (multi-subject / cooperation)
              │     + @subject, @ibc annotations
              │
              └── clinical_annotator/ (ABA clinical metadata)
                    + @function, @target, @replacement annotations

social-contingency-sim → uses contingency-annotator types (consumer, not provider)
experiment-core → uses contingency-dsl + contingency-annotator
```

**Dependency graph:**
- contingency-py: no dependencies on others
- contingency-dsl: depends on contingency-py; defines AnnotationModule Protocol
- contingency-annotator: depends on contingency-dsl + contingency-py; implements annotators
- Consumers (social-contingency-sim, experiment-core, etc.): depend on contingency-annotator

### 4.7.4 AnnotationModule Protocol

The annotation contract follows the same Protocol-based pattern used by `LearningRule` and `AssociativeState` in stimulus-annotator:

```python
@runtime_checkable
class AnnotationModule(Protocol):
    """Contract for a DSL annotation module that adds an orthogonal dimension."""

    name: ClassVar[str]       # e.g. "procedure-annotator" or "subjects-annotator"
    version: ClassVar[str]    # semver — see versioning.md §3 for capability semantics

    @property
    def annotation_keywords(self) -> FrozenSet[str]:
        """Reserved annotation keywords (e.g. frozenset({"@reinforcer", "@sd"})).
        Added to the parser's reserved-word set to prevent identifier collisions."""
        ...

    @property
    def grammar_productions(self) -> str:
        """BNF production rules this annotator adds. Appended to (never replace)
        the base grammar. Must reference only <schedule> and <value> from the
        base grammar, plus annotator-specific non-terminals."""
        ...

    @property
    def annotation_types(self) -> Mapping[str, type]:
        """Map annotation keyword -> frozen dataclass type for static validation."""
        ...

    def validate(self, annotated_expr: Any) -> Sequence[str]:
        """Annotator-specific semantic validation. Returns diagnostic messages."""
        ...

    @property
    def requires(self) -> FrozenSet[str]:
        """Names of other AnnotationModules this one depends on.
        E.g. extensions/social-annotator may require procedure-annotator/stimulus for reinforcer references."""
        ...
```

### 4.7.5 AnnotatedSchedule Type

```python
@dataclass(frozen=True)
class AnnotatedSchedule(Generic[T]):
    """A schedule expression with zero or more annotation dimensions.

    T is ScheduleExpr (v1.0 ADT) or ScheduleConfig (v0.1 Pydantic).
    The annotations mapping is the Cartesian product: expr × dim_1 × ... × dim_n
    where each dimension is optional (absent = not annotated on that axis).
    """
    expr: T
    annotations: Mapping[str, Any] = field(default_factory=dict)
    # key = annotator name ("procedure-annotator", "subjects-annotator", etc.), value = frozen annotation dataclass
```

### 4.7.6 AnnotationRegistry — Composition Rules

```python
@dataclass(frozen=True)
class AnnotationRegistry:
    """Collects enabled annotators, validates composition, merges grammars."""

    @staticmethod
    def build(*annotators: AnnotationModule) -> "AnnotationRegistry":
        """Create a registry. Raises ValueError if:
        - Two annotators claim the same annotation keyword (disjointness violation)
        - An annotator's requires set is not satisfied (dependency violation)"""
        ...
```

Two annotators compose if and only if their `annotation_keywords` are disjoint. The `requires` field handles dependency ordering (e.g. social-annotator depends on stimulus-annotator for `@reinforcer` references in inter-subject mappings). The parser accepts `annotators=registry` as a parameter; unregistered annotation names raise a parse error **within that program's registry**. The registry is program-scoped: across different programs, the same annotation name may be accepted by one and rejected by another. The DSL grammar itself does not enforce a global closure — see [ja/design-philosophy.md §4.2](../ja/design-philosophy.md) and grammar.ebnf §4.7.

### 4.7.7 Annotation BNF

Annotations appear at two scoping levels: **program-level** (session-wide defaults) and **schedule-level** (per-expression overrides).

```bnf
-- Top-level grammar (updated for two-level scoping)
<program>              ::= <program_annotation>* <param_decl>* <binding>* <annotated_schedule>
<program_annotation>   ::= <annotation>

-- Shared annotation syntax (both levels use the same production)
<annotated_schedule>   ::= <schedule> <annotation>*
<annotation>           ::= "@" <annotation_name> ("(" <annotation_args> ")")?

-- Argument list supports three forms:
--   1. Positional-only:           @species("rat")
--   2. Positional + keyword args: @chamber("med-associates", model="ENV-007")
--   3. Keyword-only:              @session_end(rule="first", time=60min)
<annotation_args>      ::= <positional_form> | <keyword_only_form>
<positional_form>      ::= <annotation_val> ("," <annotation_kv>)*
<keyword_only_form>    ::= <annotation_kv> ("," <annotation_kv>)*
<annotation_kv>        ::= <ident> "=" <annotation_val>
<annotation_val>       ::= <string_literal> | <number>
                         | <annotation_array>   -- v0.1: structured values (RFC 2026-04-17)
                         | <annotation_object>  -- v0.1: structured values (RFC 2026-04-17)
<annotation_array>     ::= "[" (<annotation_val> ("," <annotation_val>)*)? "]"
<annotation_object>    ::= "{" (<annotation_kv> ("," <annotation_kv>)*)? "}"

-- procedure-annotator/stimulus adds:
<annotation_name>      ::= "reinforcer" | "sd" | "brief"

-- procedure-annotator/temporal adds:
<annotation_name>      ::= "clock" | "warmup" | "algorithm"

-- subjects-annotator adds:
<annotation_name>      ::= "species" | "strain" | "deprivation" | "history" | "n"

-- apparatus-annotator adds:
<annotation_name>      ::= "chamber" | "operandum" | "interface" | "hardware" (alias: "hw")

-- measurement-annotator adds:
<annotation_name>      ::= "session_end" | "baseline" | "steady_state"
                          | "dependent_measure" | "training_volume" | "microstructure"
                          | "phase_end" | "logging" | "iri_window" | "warmup_exclude"

-- extensions/social-annotator adds:
<annotation_name>      ::= "subject" | "interlocking"

-- extensions/clinical-annotator adds:
<annotation_name>      ::= "function" | "target" | "replacement"
```

Each annotator extends the `<annotation_name>` production with its own keywords. The base grammar does not define `<annotation_name>` — it exists only when at least one annotator is enabled. LL(1) disambiguation: at program top-level, if the next token is `@`, consume a `program_annotation`; otherwise fall through to `param_decl*`.

**Syntax examples:**

```
-- procedure-annotator/stimulus
FR 5 @reinforcer("food-pellet")
Chain(FR 5, FI 30-s) @sd("red-light", component=1)
FR 5(FI 30-s) @brief("light", duration=2)

-- extensions/social-annotator
Conc(VI 30-s, VI 60-s) @subject("A")

-- composed (multiple annotators)
Conc(
  VI 30-s @subject("A") @reinforcer("food"),
  VI 60-s @subject("B") @reinforcer("water")
)

-- multiple annotator categories
FR 5 @reinforcer("food") @subject("A") @clock("real", unit="s") @function("escape")
```

### 4.7.8 Naming Convention

| Convention | Format | Example |
|------------|--------|---------|
| User-facing name | kebab-case with `-annotator` suffix, matching JEAB category | `procedure-annotator`, `subjects-annotator` |
| Sub-annotator (within procedure-annotator) | kebab-case, no suffix | `procedure-annotator/stimulus`, `procedure-annotator/temporal` |
| Python module | `contingency_annotator.<snake>` | `contingency_annotator.procedure_annotator.stimulus` |
| Protocol implementation | PascalCase + `Annotator` | `ProcedureAnnotator` |
| Annotation dataclass | PascalCase + `Annotation` | `ReinforcerAnnotation` |
| DSL syntax | `@` prefix + lowercase keyword | `@reinforcer("food")` |
| Extension annotator | `extensions/` prefix | `extensions/social-annotator` |

### 4.7.9 Design Principles

- **contingency-py remains minimal.** Only base CFG runtime types.
- **All annotation modules live in contingency-annotator.** DSL annotations are types and metadata, not simulation logic. `social-contingency-sim` is a consumer of these types, not a provider.
- **Base CFG is the common language.** Annotators add new production rules but never modify existing ones (open-closed principle).
- **Annotators compose via Cartesian product.** Each annotator adds an orthogonal dimension; they can be enabled independently or in any combination.
- **Protocol-based decoupling.** Third-party annotators can conform to `AnnotationModule` without inheriting from the framework (structural subtyping).

### 4.7.10 Three-Term Contingency Modeling Scope

| Element | Base CFG | procedure/stimulus | procedure/temporal | subjects | apparatus | measurement | ext/social | ext/clinical |
|---------|----------|-----|-----|-----|-----|-----|-----|-----|
| S^D (discriminative stimulus) | Implicit in Chain/Mult | `@sd("light")` | — | — | — | — | — | — |
| R (response) | Implicit as operandum | — | — | — | `@operandum("lever")` | — | — | `@target("hand-flap")` |
| S^R (reinforcer) | Not modeled | `@reinforcer` + Reinforcer type | — | — | — | — | — | — |
| Subject | Single, implicit | — | — | — | — | — | `@subject("A")` | — |
| S-S / S-R associations | Not modeled | Formal description | — | — | — | — | — | — |
| Inter-subject contingencies | Not modeled | — | — | — | — | — | Interlocking contingency | — |
| Time source / unit | Not modeled | — | `@clock("real")` | — | — | — | — | — |
| Blackout (inter-component) | `BO=5-s` (Mult/Mix kw_arg) | — | — | — | — | — | — | — |
| Session temporal structure | Not modeled | — | `@warmup` | — | — | — | — | — |
| Subject species / history | Not modeled | — | — | `@species`, `@history` | — | — | — | — |
| Physical chamber | Not modeled | — | — | — | `@chamber("ENV-007")` | — | — | — |
| Hardware backend | Not modeled | — | — | — | `@hardware("teensy41")` | — | — | — |
| Session termination | Not modeled | — | — | — | — | `@session_end` | — | — |
| Baseline measurement | Not modeled | — | — | — | — | `@baseline` | — | — |
| Steady-state criterion | Not modeled | — | — | — | — | `@steady_state` | — | — |
| Dependent variables | Not modeled | — | — | — | — | `@dependent_measure` | — | — |
| Training volume | Not modeled | — | — | — | — | `@training_volume` | — | — |
| Response microstructure | Not modeled | — | — | — | — | `@microstructure` | — | — |
| Phase termination | Not modeled | — | — | — | — | `@phase_end` | — | — |
| Event logging | Not modeled | — | — | — | — | `@logging` | — | — |
| IRI analysis | Not modeled | — | — | — | — | `@iri_window` | — | — |
| Warmup exclusion | Not modeled | — | — | — | — | `@warmup_exclude` | — | — |
| Behavior function | Not modeled | — | — | — | — | — | — | `@function("escape")` |
| Replacement behavior | Not modeled | — | — | — | — | — | — | `@replacement("mand")` |

## 4.8 Expressiveness Boundaries

| Layer | Computational Power | Responsibility | Expressible Range |
|-------|-------------------|----------------|-------------------|
| **contingency-dsl** (Foundations + Operant + Respondent + Composed + Experiment + Annotation) | CFG (non-TC) | Static contingency structure (SEI: P1-P3 hold, §4.1.1), covering both three-term operant and two-term respondent relations and their composites | Operant: 3×3 atomic + 7 combinators + DR modifiers + PR + Repeat + let bindings + stateful (Pctl, Adj, Interlocking) + trial-based (MTS, Go/NoGo). Respondent: Tier A primitives + respondent extension point. Composed: CER, PIT, autoshaping, omission, two-process. Experiment: phase sequences + context + criteria. |
| **contingency-core** | TC | Dynamic contingency transitions (SEI: any of P1-P3 violated, §4.1.1) | Guarded transitions between DSL expressions, conditional-branching titration/DRO, yoking |
| **experiment-core** | TC + constraints | Experimental finalization/verification | Exit conditions, ABA designs, safety constraints, static verification |
| **contingency-py** | Runtime | Evaluation engine | `is_satisfied()` judgment, state management, FH sequence cycling |

---

## Schema Path Conventions

The `schema/` tree mirrors the Ψ directory structure:

- `schema/foundations/` — meta-grammar, contingency-type definitions, time scales, stimulus typing, valence, context types
- `schema/operant/grammar.ebnf`, `schema/operant/ast.schema.json` — Operant layer grammar and AST
- `schema/operant/schedules/{ratio,interval,time,differential,compound,progressive}.ebnf` — per-class schedule EBNF fragments
- `schema/operant/stateful/grammar.ebnf` — Operant.Stateful (Percentile, Adjusting, Interlocking)
- `schema/operant/trial-based/grammar.ebnf` — Operant.TrialBased (MTS, Go/NoGo)
- `schema/respondent/grammar.ebnf`, `schema/respondent/ast.schema.json` — Respondent Tier A primitives + extension point
- `schema/composed/*.schema.json` — per-procedure composed schemas (conditioned-suppression, pit, autoshaping, omission, two-process-theory)
- `schema/experiment/phase-sequence.schema.json` — Experiment layer
- `schema/annotations/extensions/` — annotator extension schemas (learning-models, respondent-annotator, etc.)
- `schema/representations/` — alternative coordinate systems

---

## References

- Herrnstein, R. J. (1961). Relative and absolute strength of response as a function of frequency of reinforcement. *Journal of the Experimental Analysis of Behavior*, 4(3), 267-272. https://doi.org/10.1901/jeab.1961.4-267
- Pavlov, I. P. (1927). *Conditioned reflexes: An investigation of the physiological activity of the cerebral cortex* (G. V. Anrep, Trans.). Oxford University Press.
- Rescorla, R. A., & Wagner, A. R. (1972). A theory of Pavlovian conditioning: Variations in the effectiveness of reinforcement and nonreinforcement. In A. H. Black & W. F. Prokasy (Eds.), *Classical conditioning II: Current research and theory* (pp. 64-99). Appleton-Century-Crofts.
- Skinner, B. F. (1938). *The behavior of organisms*. Appleton-Century.
