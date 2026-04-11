# Computability, Expressiveness, and Architectural Boundaries

> Part of the [contingency-dsl theory documentation](theory.md). Describes the three-layer architecture, computability properties, and annotation system.

---

## 4.1 Three-Layer Architecture

Reinforcement schedules describe inherently **infinite processes**. A VI 60 schedule can run indefinitely; an FR 10 continues producing reinforcement as long as responses continue. This is not a defect but an essential property of behavioral contingencies.

We propose a three-layer architecture that separates concerns along the dimension of computational power:

```
┌─────────────────────┐
│   contingency-dsl   │  Non-Turing-complete (CFG)
│   "What produces     │  Static, declarative
│    reinforcement"    │  FR10, Conc(VI30, VI60)
├─────────────────────┤
│   contingency-core   │  Turing-complete
│   "How contingencies │  Dynamic, procedural
│    change over time" │  if rate > 5.0: switch(VI → VR)
├─────────────────────┤
│   experiment-core    │  Turing-complete + constraints
│   "Making it a       │  Verification, finalization
│    finite experiment" │  Session(sched, exit=Reinf(50))
└─────────────────────┘
```

| Layer | Computational Power | Describes | Examples |
|-------|-------------------|-----------|----------|
| **contingency-dsl** | CFG (non-TC) | Static contingency structure | `Conc(VI30, VI60)`, `Chain(FR5, FI30)` |
| **contingency-core** | Turing-complete | Dynamic contingency transitions | Rate-based schedule switching, titration |
| **experiment-core** | TC + constraints | Experimental finalization and verification | Exit conditions, ABA designs, safety constraints |

**contingency-core** (Turing-complete) enables:
- "Switch from VR to VI when response rate exceeds threshold"
- "Increment PR until breakpoint"
- "Adaptive DRO (dynamically adjust threshold on criterion achievement)"
- "Titration procedures (adjust stimulus intensity based on responding)"

**experiment-core** (TC + constraints) guarantees:
- Termination (session exit conditions enforced)
- Static verification ("Does this schedule ever produce reinforcement?")
- Safety (reinforcement rate bounds, session time limits)
- Structural validity of experimental designs (A1-A2 identity in ABA)

Therefore:
- `until` clauses belong in experiment-core, not contingency-dsl
- contingency-dsl concerns itself solely with static contingency structure
- Dynamic transitions are contingency-core's responsibility
- Finalization and verification are experiment-core's responsibility

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

"Complete FR10 three times, then switch to VI60" is expressible with existing combinators:

```
Chain(FR10, FR10, FR10, VI60)   -- explicit unfolding
Tand(FR10, FR10, FR10, VI60)    -- without S^D change
```

The `Repeat(n, S)` combinator reduces verbosity:

```
Tand(Repeat(3, FR10), VI60)
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
Repeat(2, Repeat(3, FR5))
→ (inner expansion)  Repeat(2, Tand(FR5, FR5, FR5))
→ (outer expansion)  Tand(Tand(FR5, FR5, FR5), Tand(FR5, FR5, FR5))
→ (Theorem 2 flatten) Tand(FR5, FR5, FR5, FR5, FR5, FR5)
```

Conformant implementations MUST also reduce `Repeat(1, S)` to `S` (not `Tand(S)`).

**Distinction from Mix:** `Mix(FR10, VI60)` is undiscriminated alternation (environment-controlled, typically random selection). `Tand(Repeat(3, FR10), VI60)` is sequential completion (FR10 completed three times before transitioning to VI60). These are distinct contingencies.

## 4.4 Variable Bindings as Macro Expansion

Variable bindings can be introduced without adding Turing completeness:

```
let baseline = VI60
let treatment = Conc(VI30, EXT)
let reversal = baseline
```

This is macro expansion (textual substitution) — no mutable state, no closures, no recursion. `let` is eliminated at parse time, yielding a let-free syntax tree. The resulting program is within the base CFG.

Potential extensions, all reducible to macro expansion:
- Parameterized templates: `def matching(a, b) = Conc(VI(a), VI(b))` → `matching(30, 90)`
- Annotations: `FR10 @label("component A")` — metadata for analysis/visualization

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

- **PR step functions**: Enumerated within the DSL (`hodos`, `linear`, `exponential`). Arbitrary functions available only via the Python API.
- **Fleshler-Hoffman generation**: `seed` parameter for deterministic generation. Runtime randomness is the engine's responsibility.
- **DR thresholds**: Scalar values only. Dynamic thresholds (adaptive DRO) are delegated to contingency-core.

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

See [annotation-design.md](../annotation-design.md) §6 for full specification.

### 4.7.1 Motivation

**Multi-Subject Contingencies.** Behavioral pharmacology cooperation tasks — "Subject A's lever press produces reinforcement for Subject B" — require contingency mappings across subjects. The base DSL assumes a single implicit subject. Multi-subject contingencies introduce a new dimension: **subject** as a dimension of stimulus.

**Shared Reinforcers.** "Schedules A and C use the same food pellet reinforcer" — reinforcer identity is not expressible in the base CFG, which models only R-SR rules (schedule structure), not reinforcer properties. DSL-level reinforcer identity enables specification-level comparison with associative learning theories (Rescorla & Wagner, 1972), type-guaranteed reinforcer identity, and formal description of conditional reinforcement dynamics.

**Temporal Context.** Session-level temporal parameters (clock source, warm-up intervals) are orthogonal to schedule structure but must be declarable alongside it. Note: blackout (BO) has been promoted to core grammar as a Mult/Mix keyword argument (v1.1), since BO duration directly affects inter-component behavioral independence (Reynolds, 1961; Bouton, 2004).

**Clinical Metadata.** ABA practitioners need to annotate schedules with functional behavior assessment results (function of behavior, target/replacement behavior labels) without polluting the schedule grammar.

### 4.7.2 Annotator Taxonomy

Each annotator is named with the `-annotator` suffix, meaning: *an annotation module that adds an orthogonal dimension to the base DSL*.

Recommended annotator names match JEAB Method section headings 1:1 (see
[annotation-design.md §3.7](../annotation-design.md)). The 2026-04-12
annotator reorganization established this correspondence.

| Annotator | JEAB Category | Annotation Keywords | Purpose |
|-----------|---------------|---------------------|---------|
| `procedure-annotator` | **Procedure** | (see sub-annotators below) | Procedure-level information, split into stimulus and temporal sub-annotators |
| &nbsp;&nbsp;└ `procedure-annotator/stimulus` | Procedure | `@reinforcer`, `@sd`, `@brief` | Stimulus identity: reinforcers, discriminative stimuli, second-order brief stimuli |
| &nbsp;&nbsp;└ `procedure-annotator/temporal` | Procedure | `@clock`, `@warmup`, `@algorithm` | Session-level temporal parameters |
| `subjects-annotator` | **Subjects** | `@species`, `@strain`, `@deprivation`, `@history`, `@n` | Subject conditions (renamed from `subject-annotator` on 2026-04-12 to match JEAB plural heading) |
| `apparatus-annotator` | **Apparatus** | `@chamber`, `@operandum`, `@interface`, `@hw` | Physical chambers, response devices, hardware interfaces. `@operandum` moved from `stimulus-annotator` on 2026-04-12 to align with JEAB Method section conventions. |
| `measurement-annotator` | **Measurement** | `@session_end`, `@baseline`, `@steady_state` | Session termination rules, baseline conditions, steady-state criteria (v1.x minimal set; introduced 2026-04-12 to close DIVERGENCE C). |

**Extensions** (outside the four JEAB categories, under `annotations/extensions/`):

| Extension | Keywords (candidate) | Domain |
|---|---|---|
| `extensions/social-annotator` | `@subject`, `@interlocking` | Multi-subject contingencies, cooperation tasks |
| `extensions/clinical-annotator` | `@function`, `@target`, `@replacement` | ABA intervention metadata, FBA results |

**Orthogonality constraint:** Annotation keywords across all annotators are mutually disjoint. Multiple annotators can annotate the same schedule expression simultaneously:

```
FR5 @reinforcer("food") @subject("A") @clock("real", unit="s") @function("escape")
```

### 4.7.3 Package Architecture

All annotators live as submodules within **contingency-annotator**. The base DSL (`contingency-dsl`) defines only the `AnnotationModule` protocol; concrete annotators are never part of the base package. Annotator names correspond 1:1 to JEAB Method section headings (see [annotation-design.md §3.7](../annotation-design.md)).

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
        │           + Note: BO and COD promoted to core grammar in v1.1
        │
        ├── subjects_annotator/ (JEAB category: Subjects; renamed from subject_annotator on 2026-04-12)
        │     + @species, @strain, @deprivation, @history, @n annotations
        │
        ├── apparatus_annotator/ (JEAB category: Apparatus)
        │     + @chamber, @operandum, @interface, @hw annotations
        │     + Physical chamber, response device, HW interface identity
        │
        ├── measurement_annotator/ (JEAB category: Measurement; introduced 2026-04-12)
        │     + @session_end, @baseline, @steady_state annotations (v1.x minimal set)
        │     + Session termination, baseline, steady-state criteria
        │
        └── extensions/ (outside the four JEAB categories)
              │
              ├── social_annotator/ (multi-subject / cooperation)
              │     + @subject, @interlocking annotations
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
    version: ClassVar[str]    # semver

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
<annotation>           ::= "@" <annotation_name> "(" <annotation_args> ")"
<annotation_args>      ::= <string_literal> ("," <annotation_kv>)*
<annotation_kv>        ::= <ident> "=" (<string_literal> | <value>)

-- procedure-annotator/stimulus adds:
<annotation_name>      ::= "reinforcer" | "sd" | "brief"

-- procedure-annotator/temporal adds:
<annotation_name>      ::= "clock" | "warmup" | "algorithm"

-- subjects-annotator adds:
<annotation_name>      ::= "species" | "strain" | "deprivation" | "history" | "n"

-- apparatus-annotator adds:
<annotation_name>      ::= "chamber" | "operandum" | "interface" | "hw"

-- measurement-annotator adds:
<annotation_name>      ::= "session_end" | "baseline" | "steady_state"

-- extensions/social-annotator adds:
<annotation_name>      ::= "subject" | "interlocking"

-- extensions/clinical-annotator adds:
<annotation_name>      ::= "function" | "target" | "replacement"
```

Each annotator extends the `<annotation_name>` production with its own keywords. The base grammar does not define `<annotation_name>` — it exists only when at least one annotator is enabled. LL(1) disambiguation: at program top-level, if the next token is `@`, consume a `program_annotation`; otherwise fall through to `param_decl*`.

**Syntax examples:**

```
-- procedure-annotator/stimulus
FR5 @reinforcer("food-pellet")
Chain(FR5, FI30) @sd("red-light", component=1)
FR5(FI30) @brief("light", duration=2)

-- extensions/social-annotator
Conc(VI30, VI60) @subject("A")

-- composed (multiple annotators)
Conc(
  VI30 @subject("A") @reinforcer("food"),
  VI60 @subject("B") @reinforcer("water")
)

-- multiple annotator categories
FR5 @reinforcer("food") @subject("A") @clock("real", unit="s") @function("escape")
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
| Blackout (inter-component) | `BO=5s` (Mult/Mix kw_arg) | — | — | — | — | — | — | — |
| Session temporal structure | Not modeled | — | `@warmup` | — | — | — | — | — |
| Subject species / history | Not modeled | — | — | `@species`, `@history` | — | — | — | — |
| Physical chamber | Not modeled | — | — | — | `@chamber("ENV-007")` | — | — | — |
| Hardware backend | Not modeled | — | — | — | `@hw("teensy41")` | — | — | — |
| Session termination | Not modeled | — | — | — | — | `@session_end` | — | — |
| Steady-state criterion | Not modeled | — | — | — | — | `@steady_state` | — | — |
| Behavior function | Not modeled | — | — | — | — | — | — | `@function("escape")` |
| Replacement behavior | Not modeled | — | — | — | — | — | — | `@replacement("mand")` |

## 4.8 Expressiveness Boundaries

| Layer | Computational Power | Responsibility | Expressible Range |
|-------|-------------------|----------------|-------------------|
| **contingency-dsl** | CFG (non-TC) | Static contingency structure | 3×3 atomic + 7 combinators + DR modifiers + PR + Repeat + let bindings |
| **contingency-core** | TC | Dynamic contingency transitions | Conditional transitions, titration, adaptive DRO, state machines |
| **experiment-core** | TC + constraints | Experimental finalization/verification | Exit conditions, ABA designs, safety constraints, static verification |
| **contingency-py** | Runtime | Evaluation engine | `is_satisfied()` judgment, state management, FH sequence cycling |

---

## References

- Herrnstein, R. J. (1961). Relative and absolute strength of response as a function of frequency of reinforcement. *Journal of the Experimental Analysis of Behavior*, 4(3), 267-272. https://doi.org/10.1901/jeab.1961.4-267
- Rescorla, R. A., & Wagner, A. R. (1972). A theory of Pavlovian conditioning: Variations in the effectiveness of reinforcement and nonreinforcement. In A. H. Black & W. F. Prokasy (Eds.), *Classical conditioning II: Current research and theory* (pp. 64-99). Appleton-Century-Crofts.
