# contingency-dsl Annotations — Design Document

## Status: Revised (2026-04-12)

This document presupposes [design-philosophy.md](design-philosophy.md) §4.
Where the two documents conflict, **design-philosophy.md takes precedence as the canonical reference**.

Related documents:
- [en/design-philosophy.md](design-philosophy.md) §4 — Annotation layer structure and categories (canonical)
- [schema-format.md](schema-format.md) — Annotation Schema Format (language-independent meta-DSL)
- [validation-modes.md](validation-modes.md) — Design examples of tier × mode validation for each program
- [grammar.ebnf](../../grammar.ebnf) §4.7 — Annotation syntax and program-scope closure

---

## 1. Guiding Principle: A Language-Agnostic Annotation Schema

The semantic definition of annotations is not confined to the type system of any particular implementation language (Python / Rust / Kotlin, etc.) but is instead defined as a **language-agnostic schema description**.
This is a concretization of design-philosophy §6 (language-agnosticism as a substantive requirement).

### Motivation

1. **Language agnosticism** — Multiple language implementations can reference the same annotation schema and interpret it equivalently.
2. **Canonical representation of experiments** — The DSL source (Core + annotations) serves as the single source of truth for experimental procedures.
3. **Paper compilation** — The DSL source can be compiled into natural-language Method / Procedure sections. An unambiguous, reproducible procedure description with zero ambiguity.

### Positioning of the "Meta-DSL" — Not a Monolithic Definition

The previous version of this document was written under the assumption that "the DSL project monolithically defines a meta-DSL, and all implementations conform to it."
Since design-philosophy §4.2, this assumption has been **retracted**:

- The annotation schema **belongs to the registry provided by each program (runtime / interpreter)**. The DSL spec itself only presents "recommendations."
- Categories (Procedure / Subjects / Apparatus / Measurement, etc.) are **recommended classifications** and are not enforced. Third parties are free to define new categories and to ignore or redefine existing ones.
- Therefore, what the term "meta-DSL" denotes is **"a language-agnostic schema format for describing each program's registry."** Nothing more.

### Relationship to the Current State

The language-agnostic schema format is now formally specified in
[schema-format.md](schema-format.md) (Annotation Schema Format).
It is based on JSON Schema 2020-12 with DSL-specific extensions
(`keywords`, `scope`, `positional`, `required_if`/`forbidden_if`,
`aliases`, `errors`). All 5 recommended annotator schemas conform
to this format as of 2026-04-13.

This spec positions the existing `contingency-dsl-py` `AnnotationModule` Protocol as the **"Python reference implementation provided by the DSL project."**
Other language implementations may be freely constructed as long as they follow the schema format; conformance with the Python implementation is guaranteed through the schema description.

```
Annotation Schema Format (schema-format.md)
    ↓ schema/annotations/*.schema.json
    ↓ Each program implements
AnnotationModule (Python)  ← reference implementation
AnnotationModule (Rust)    ← reference implementation (future)
3rd-party registry          ← may be constructed independently, ignoring the above
```

---

## 2. Boundary Principle Between Core DSL and Annotations

### Principle: Annotations Must Not Alter Core Semantics

The presence or absence of annotations must not change the evaluation semantics of Core schedule expressions.
`FI 10` is semantically equivalent to `FI 10 @clock(unit="s")`; the latter merely adds information to the former.

```
FI 10                           -- Theoretically complete. Scalloping can be discussed
FI 10 @clock(unit="s")          -- Time unit made explicit. Properties of FI unchanged
FI 10 @clock(unit="s")          -- Needed to run the experiment, but
      @operandum("left_lever")     not needed to discuss properties of FI 10
      @reinforcer("pellet")
      @subject(species="rat")
```

### Boundary Test (Determining Core vs. Annotation)

> **Canonical definition:** [boundary-decision.md](boundary-decision.md) §2 (Phase A) and §3 (Phase B).
>
> The boundary test (Q1–Q3) and subsequent tier classification (T-A–T-C)
> are defined in a single document. All proposals should reference that
> file for the authoritative decision tree and application examples.

---

## 3. Annotator Ownership Policy

This DSL project provides a **recommended** set of annotations. Each program has the freedom to adopt, extend, or replace them.

### What the DSL Project Provides

| Category | Recommended annotator | Example keywords |
|---|---|---|
| **Procedure** | procedure-annotator (stimulus + temporal sub-annotators) | `@reinforcer`, `@sd`, `@brief`, `@clock`, `@warmup`, `@algorithm` |
| **Subjects** | subjects-annotator | `@species`, `@strain`, `@deprivation`, `@history`, `@n` |
| **Apparatus** | apparatus-annotator | `@chamber`, `@operandum`, `@interface`, `@hardware` (alias: `@hw`) |
| **Measurement** | measurement-annotator (v1.x formal set) | `@session_end`, `@baseline`, `@steady_state` (for detailed parameter schemas, see [annotations/measurement-annotator/README.md](../../annotations/measurement-annotator/README.md) §Parameter Schemas) |

**Extensions** (recommended annotators that do not fit the four categories, located under `annotations/extensions/`):

| Extension | Example keywords | Domain |
|---|---|---|
| extensions/social-annotator | `@subject`, `@ibc` | Multi-subject contingencies, cooperative tasks. `@ibc` = Interlocking Behavioral Contingencies (Glenn, 2004); renamed from `@interlocking` to avoid collision with `Interlock(...)` schedule (Ferster & Skinner, 1957) |
| extensions/clinical-annotator | `@function`, `@target`, `@replacement` | ABA clinical metadata |

Category classification conforms to [design-philosophy.md](design-philosophy.md#41-推奨カテゴリ体系jeab-method-節に準拠) §4.1.
For the 1:1 correspondence principle between annotator names and JEAB categories, see §3.7.

### What Third Parties Are Free to Do

- **Adopt** the DSL project's recommended annotators as-is
- **Ignore** some of them (e.g., a program that manages environmental conditions externally may not use Apparatus)
- **Define new categories** of their own (e.g., Clinical, Derivational, Pharmacology)
- **Reinterpret or replace** existing annotators (implementation of competing theories)

In all cases, no changes to the Core DSL are required.

### Principle of Incremental Addition

```
Theoretical discussion:  FI 10
Simulation:              FI 10 @clock(unit="s") @algorithm("fleshler-hoffman", n=12)
Physical experiment:     FI 10 @clock(unit="s") @algorithm(...) @operandum("left_lever")
                               @reinforcer("pellet") @subject(species="rat")
                               @chamber("med-associates", model="ENV-007")
Paper publication:       All of the above (publish DSL source as supplement)
```

Each layer is **optional and additive**. `FI 10` is valid in any program's registry (as long as that registry can interpret Core).

### How to Define a New Annotation

1. Copy [annotation-template.md](annotation-template.md) as a template
2. Answer the boundary test in §2 to demonstrate that it is appropriate as an annotation rather than Core
3. Select the corresponding category (Procedure / Subjects / Apparatus / Measurement / Extension)
4. Add it to the appropriate package or independent registry through the review mechanism in §4

---

## 3.5 Annotation Aliases — Reconciling Theoretical Neutrality with Practical Notation

### Problem

**Reinforcer** (強化子) and **punisher** (罰子), core concepts in behavior analysis, have **functional (post hoc, effect-based) definitions** from the standpoint of radical behaviorism.
That is, whether a stimulus is a reinforcer or a punisher is determined only post hoc by whether it increases or decreases behavior. Labeling something as "a reinforcer" at the stage of procedure description is subject to criticism of mentalism conflation and a priori labeling.

On the other hand, this DSL is a **procedure description language** that records the experimenter's intent. The declaration "this stimulus is presented with the intent of using it as a punisher" is procedurally meaningful and aids the writing of the Methods section and the reader's understanding.

### Solution: Provide Multiple Semantically Equivalent Keywords as Type Aliases

For a single **primary form** keyword, multiple semantically equivalent aliases are permitted. Aliases are **collapsed to the same node at the AST level**, so they do not affect equivalence judgments or program generation. Differences in surface notation are retained only as **pragmatic hints**.

### Adopted Example: `@reinforcer` Family in procedure-annotator/stimulus

| Keyword | Role | Notes |
|---|---|---|
| `@reinforcer` | **Primary form** | Declaration of a reinforcer (強化子). The most established notation in EAB |
| `@punisher` | Alias | Explicit statement of punisher (罰子) intent |
| `@consequentStimulus` | Alias | Theoretically neutral notation |

All three are converted to the same `Reinforcer(stimulus=..., label=...)` node in the AST.
The `label` retains the surface notation but is ignored during equivalence judgments.

```
FR 3 @reinforcer("shock") @operandum("lever")
FR 3 @punisher("shock") @operandum("lever")
FR 3 @consequentStimulus("shock") @operandum("lever")
```

The above three are all treated as **the same procedure**.

For details, see [annotations/procedure-annotator/stimulus/README.md](../../annotations/procedure-annotator/stimulus/README.md) §Keyword Aliases.

### General Principles

Annotation aliases may be adopted when the following conditions are met:

1. **A primary form exists** — There is already one established keyword
2. **Aliases are strictly equivalent** — They collapse to the same node at the AST level
3. **Intent declaration** — Aliases serve to record the experimenter's intent or theoretical stance in the source
4. **No new semantics** — Aliases do not introduce meaning different from the primary form

"Similar-function keywords" that do not satisfy the above conditions should be defined as separate annotators, not aliases.

### Note on Terminology Choice

This document uses the expression "primary form (primary / base form)." The term `canonical form`, widely used in programming / type theory, is not a universal term in the JEAB literature (although `canonical taxonomy` and `canonical data` appear as adjectival uses in some JEAB papers in EAB, it is not established as a technical term denoting the standard form of a specific keyword). `Primary` or `base` is adopted as the terminology choice most familiar to behavior analysts.

### Implications for Third Parties

Alias relationships are recommended by the DSL project but are not mandatory. A third-party registry may:

- Adopt all aliases
- Adopt only the primary form (recognize only `@reinforcer`; `@punisher` yields a parse error)
- Add custom aliases (e.g., `@stimulus`)
- Redefine alias relationships (not recommended)

All of these follow the principle of design-philosophy §4.2 (program-scoped closure).

## 3.6 Annotation Category Audit — Alignment with JEAB Method Sections

This section documents the current state based on the annotation category audit conducted on 2026-04-12 (performed via PROCEDURE_INVENTORY), and explicitly identifies items requiring future adjustment.

### 3.6.1 Resolved: Migration of `@operandum` to Apparatus

**Change:** `@operandum` was migrated from `stimulus-annotator` to `apparatus-annotator` on 2026-04-12.

**Rationale:**
- In JEAB Method sections, operanda (levers, keys, etc.) are traditionally described in the **Apparatus** section (e.g., "Two retractable levers (ENV-112CM, Med Associates) were mounted on the front wall")
- Even when the current DSL uses `@operandum("left_lever", component=1)` in a procedural manner to assign to schedule components, this is fundamentally an identification of physical equipment and naturally belongs to the Apparatus category

**Scope of impact:** stimulus-annotator/README, apparatus-annotator/README, architecture.md §4.7.2 / §4.7.3 / §4.7.7 / §4.7.10, docs/annotations.md, grammar.ebnf §4.7 comments, this document §3 (recommended annotator list).

### 3.6.2 Design Decisions

**`@algorithm`** — Maintained in Procedure. Specifies the generation method for schedule
values (e.g., Fleshler-Hoffman), not the measurement method for effects. JEAB convention
places algorithm notes in the Procedure section.

**`@hardware`** — Physical hardware only (Apparatus category). Omission means
virtual/simulation mode (see validation-modes §4.2).

**`@session_end` / `@baseline` / `@steady_state`** — Measurement category (v1.0).
**`@dependent_measure` / `@training_volume` / `@microstructure`** — Measurement category
(v1.1, added 2026-04-13). `@dependent_measure` declares primary dependent variables
(including timing indices, behavioral economics measures, and CER suppression ratios);
`@training_volume` tracks cumulative training exposure for overtraining/habit formation
paradigms; `@microstructure` configures IRT distribution, bout analysis, log-survivor
analysis, and post-reinforcement pause measurement parameters.
**`@phase_end` / `@logging` / `@iri_window` / `@warmup_exclude`** — Measurement category
(v1.2, added 2026-04-13). `@phase_end` declares compound phase termination criteria
(conjunction/disjunction of session count, stability, and CV thresholds);
`@logging` specifies event-level data recording (event types, format, precision);
`@iri_window` configures inter-reinforcement interval analysis (binning, normalization,
sequential dependency tracking); `@warmup_exclude` declares session-onset exclusion
periods for analysis. `future_keywords` is now empty — all planned measurement keywords
have been promoted to full schema definitions.

## 3.7 Annotator Naming Convention — 1:1 Correspondence with JEAB Categories

### Principle

With the annotator reorganization of 2026-04-12, the naming convention was adopted that **recommended annotator names correspond 1:1 with JEAB Method section headings**:

| Annotator name | JEAB category (Method section heading) |
|---|---|
| `procedure-annotator` | Procedure |
| `subjects-annotator` | Subjects |
| `apparatus-annotator` | Apparatus |
| `measurement-annotator` | Measurement |

### Advantages of This Principle

1. **Classification is self-evident**: The JEAB category is immediately apparent from the annotator name
2. **Easy to freeze**: "4 categories = 4 annotators" serves as the invariant base rule
3. **Clear boundary determination**: Items that do not fit the four categories are explicitly directed to either `extensions/` or the [Schedule Extension layer](design-philosophy.md#5-schedule-extension-%E5%B1%A4--%E5%8B%95%E7%9A%84tc-%E8%BF%91%E5%82%8D%E3%81%AE-schedule-%E6%A7%8B%E6%88%90%E7%B4%A0)
4. **Measurement gap becomes visible**: It is immediately apparent when `measurement-annotator` does not exist (the state prior to 2026-04-12)

### Internal Structure of the Procedure Category

`procedure-annotator` is composed of two sub-annotators:

```
procedure-annotator/
├── stimulus/    — Stimulus identity (@reinforcer, @sd, @brief)
└── temporal/    — Session-level temporal structure (@clock, @warmup, @algorithm)
```

Both sub-annotators belong to the Procedure category. The sub-annotator split is for dimensional readability and does not affect category determination.

### Extensions

Annotators that do not fit the four JEAB categories are placed under `annotations/extensions/`:

```
annotations/extensions/
├── social-annotator   — Multi-subject contingencies (future)
└── clinical-annotator — ABA clinical metadata (future)
```

The intent of placing them under Extensions is to "make it explicit, in both documentation and physical structure, that these lie outside the four JEAB categories." If in the future these evolve into a form that can be absorbed into the four JEAB categories, there is the option of extracting them from `extensions/` and integrating them as sub-annotators of the appropriate annotator.

### Third-Party Freedom

Per the program-scoped closure principle (§4.2 in design-philosophy), third parties may:

- Follow this naming convention (recommended)
- Adopt a different naming convention
- Ignore Extensions
- Add their own annotators

All of these are permitted. The 1:1 correspondence in this section is a **recommendation** from the DSL project, not a mandate.

### Change History

- 2026-04-12: Initial version. The following reorganization was performed:
  - `stimulus-annotator` + `temporal-annotator` → `procedure-annotator/` (stimulus + temporal sub-annotators)
  - `subject-annotator` → `subjects-annotator` (singular → plural)
  - `measurement-annotator` established (v1.x minimal set)
  - `social-annotator` / `clinical-annotator` → moved under `extensions/`

---

## 4. Review Mechanism: Process for Adding DSL Project Recommended Annotators

This section defines the review procedure for **adding recommended annotators to the DSL project**.
This procedure is not imposed on third-party independent registries (each project determines its own review procedure).

### Problem: What to Verify When Adding a Recommended Annotator

When a recommendation candidate appears, the following must be determined:

- Whether promotion to Core grammar is necessary (boundary test Q1-Q3 in §2) or whether annotation is sufficient
- Which recommended category (Procedure / Subjects / Apparatus / Measurement) it belongs to
- Whether keyword conflicts exist with existing annotators in the recommended registry

### Review Structure

```
Layer 1: Mechanical verification (programmatic)
    ├── Keyword collision detection (disjointness within the recommended registry)
    ├── Inter-annotator dependency verification
    └── Schema syntax verification

Layer 2: Boundary test (structured markdown)
    ├── Answer the 3 boundary test questions from §2
    ├── Inclusion/exclusion criteria described in each annotator's README.md
    └── → Answerable by human or LLM
```

### Layer 2: Boundary Test Matrix

When a proposal is made to add a new annotation keyword `@X` to annotator `A`, the following markdown template is completed:

```markdown
## Boundary Review: @X → A

### 1. Core independence (§2 boundary test)
The following correspond to Q1-Q3 in annotation-design.md §2.
§2 is the authoritative description; if this checklist diverges, follow §2.
- [ ] Q1: Can the theoretical properties of the schedule (e.g., FI scallop) be discussed without `@X`? → YES means annotation OK
- [ ] Q2: Does `@X` alter the evaluation semantics of the schedule expression? → NO means annotation OK
- [ ] Q3: Can `@X` be claimed as mandatory at the Core grammar level (universally required across the entire DSL spec, independent of any registry)? → NO means annotation OK

### 2. Category fit
- [ ] Is `@X` consistent with the category (Procedure / Subjects / Apparatus / Measurement) to which A belongs?
- [ ] Is `@X` semantically coherent with the existing keywords of A?
- [ ] Does `@X` conflict with keywords of other annotators in the recommended registry?

### 3. Necessity for recommendation
- [ ] Is the information covered by `@X` not sufficiently handled outside the DSL (comments / external files)?
- [ ] Does declaring `@X` within the DSL benefit compilation targets (paper / code generation / validation)?
- [ ] Is there value in including `@X` in the DSL project's recommended set, not just in a third-party set?

### 4. Domain expert sign-off
- [ ] EAB: Valid from the perspective of basic research
- [ ] PLT: Consistent from the perspective of language design
```

---

## 5. Compilation Targets (Future Vision)  <!-- was §5 before §6 scoping insert -->

```
DSL source (with annotations)
    │
    ├──→ Python runtime    (contingency-py + annotator)
    ├──→ Rust runtime      (contingency-rs)
    ├──→ MedPC syntax      (existing MedPC equipment)
    ├──→ Arduino/Teensy    (experiment-io)
    ├──→ JSON interchange  (data exchange)
    └──→ Natural language  (paper Methods section)
```

### Paper Compilation Example

Input:
```
VI 30 @clock(unit="s")
  @algorithm("fleshler-hoffman", n=12)
  @cod(duration=2)
  @reinforcer("sucrose", concentration="10%", duration=3)
```

Output (APA Methods section):
> Responses were reinforced according to a variable-interval 30-s schedule
> (Fleshler & Hoffman, 1962; list length = 12) with a 2-s changeover delay.
> Each reinforcer delivery consisted of 3-s access to 10% sucrose solution.

---

## 6. Two-Level Scoping: Program Level vs. Schedule Level

### Motivation

The Method section of a scientific paper has a clear hierarchical structure:
**Subjects** → **Apparatus** → **Procedure** (Sidman, 1960; Ferster & Skinner, 1957).
Subject conditions and apparatus are boundary conditions that apply to the entire experimental session and are conceptually superordinate to the reinforcement schedule (independent variable).

The DSL reflects this structure: `@species("rat")` is not a modifier of `FR 5` but should be declared as a precondition for the entire program.
This follows the same pattern as `LH = 10-s` being declared at the program level.

### Grammar

```ebnf
program ::= program_annotation* param_decl* binding* annotated_schedule
program_annotation ::= annotation
annotated_schedule ::= schedule annotation*
```

LL(1) determination: If the next token is `@` → consume `program_annotation`; otherwise → transition to `param_decl*`.
No ambiguity. The `@` syntax is shared between program level and schedule level.

### Scoping Semantics

```
resolve(key, S) = S.annotations[key]  if key ∈ S.annotations
                  program.annotations[key]  otherwise
```

- **Program level** = session-wide defaults
- **Schedule level** = overrides for a specific expression
- **The same keyword is permitted at both levels** — e.g., `@reinforcer` can be set as a default at the program level and overridden only for a specific component in a choice procedure

### Recommended Scope Classification

| Scope | Annotations | Rationale |
|---|---|---|
| **Program level (Subjects)** | `@species`, `@strain`, `@n`, `@history`, `@deprivation` | Invariant within a session. Subjects are boundary conditions |
| **Program level (Apparatus)** | `@chamber`, `@hardware`, `@interface` | Apparatus is fixed throughout the session |
| **Program level (Session)** | `@clock`, `@warmup`, `@algorithm` | Session temporal parameters |
| **Program level (Measurement)** | `@session_end`, `@baseline`, `@steady_state` | Measurement criteria apply session-wide. Steady-state and baseline conditions are boundary conditions |
| **Schedule level** | `@operandum`, `@sd`, `@brief` | Differ across components (concurrent, multiple) |
| **Both (default + override)** | `@reinforcer` | Usually uniform; may differ in choice procedures |

Note: This is a recommended classification, not a grammar-level constraint. Any annotation keyword can syntactically appear at both levels. Semantic constraints are verified in a semantic pass.

### Semantic Constraints

- Placing `@operandum(component=N)` at the program level → `SemanticError: PROGRAM_ANNOTATION_COMPONENT`
  (Component indices are meaningful only in a schedule context)
- Program-level annotation with component-specific parameters → linter WARNING

### Complete Example

```
-- Subjects (program-level)
@species("rat")
@strain("Sprague-Dawley")
@deprivation(hours=23, target="food")
@history("naive")
@n(6)

-- Apparatus (program-level)
@chamber("med-associates", model="ENV-007")
@hardware("teensy41")

-- Session parameters (program-level)
@clock(unit="s")
@algorithm("fleshler-hoffman", n=12, seed=42)
@warmup(duration=300)
@reinforcer("sucrose", concentration="10%", duration=3)

-- Measurement (program-level)
@session_end(rule="first", time=60min, reinforcers=60)
@baseline(pre_training_sessions=3)
@steady_state(window_sessions=5, max_change_pct=10, measure="rate")

-- Schedule parameters (core grammar)
COD = 2-s
LH = 10-s

let left = VI 30-s
let right = VI 60-s
Conc(left, right)
  @operandum("left_lever", component=1)   -- schedule-level
  @operandum("right_lever", component=2)  -- schedule-level
  @sd("red_light", component=1)           -- schedule-level
  @sd("green_light", component=2)         -- schedule-level
```

### Design Rationale

**PL-theoretic rationale:**
- A `session { }` block syntax has no precedent in the existing grammar and is excessive — positional distinction suffices
- Integrating into `param_decl` violates the boundary principle (`param_decl` = affects Core semantics; annotation = orthogonal metadata)
- The design is close to Rust's inner/outer attributes (`#![...]` vs `#[...]`), but positional scoping is more natural for a non-TC DSL

**Behavior-analytic rationale:**
- Subjects = boundary conditions (the baseline in Sidman's (1960) steady-state design)
- Schedule = independent variable
- The causal structure is directly mapped onto the DSL's syntactic hierarchy

---

## 7. Unresolved Design Issues

### Meta-DSL Grammar (Format)

The **format** for describing annotation schemas in a language-agnostic way is undetermined. Candidates:

1. **EBNF + constraint language** — Extend grammar.ebnf to declare types and constraints
2. **JSON Schema-based** — Define annotation schemas as an extension of ast-schema.json
3. **Custom DSL** — `annotation "reinforcer" { ... }` format

Regardless of which is adopted, following the principle of design-philosophy §4.2, this DSL project provides only **recommended** schemas, and each program can independently construct its own registry.

### Validation Responsibility for annotation_name

As defined in grammar.ebnf §4.7, validation of annotation_name is the **program's** responsibility. The DSL grammar defines only syntactic form (`@name(args)`). Programs that adopt the recommended schema validate recommended keywords; programs with their own registry validate their own keywords.

### Upper Bound on Inter-Annotator Dependencies

Annotators can require other annotators (e.g., extensions/social-annotator → procedure-annotator/stimulus). Whether an upper bound should be placed on the depth of the dependency chain will be decided once the number of concrete recommended annotators grows.

---

## 8. Extension Proposal List for Recommended Annotators (Draft)

### Status: Draft - awaiting review

This section lists candidate annotations for addition to the DSL project's **recommended** annotators. Candidates independently raised from multiple domain perspectives (basic EAB, behavioral pharmacology, ABA practice, reproducibility design) are consolidated here.

> **Important reinterpretation (after design-philosophy finalization on 2026-04-12):**
>
> The terms "mandatory" and "should be made mandatory" in this section denote **the degree of recommendation for inclusion in the DSL project's recommended set**. Nothing becomes "mandatory" at the DSL grammar level.
> Each program's registry determines what is mandatory vs. optional according to its own rules. For concrete examples, see the tier × mode model in [validation-modes.md](validation-modes.md).
>
> The same annotation may be mandatory (tier 2) in one program, optional in another, and unused in yet another. This is a necessary consequence of [design-philosophy.md §4.2](design-philosophy.md#42-カテゴリは-推奨分類であって強制ではない).

### 8.1 Unanimously Agreed Addition Proposals (Core EAB Extensions)

Extensions considered essential for basic EAB research:

#### 8.1.1 `@session_end` — Session Termination Criteria **[Implemented]** `Tier 2 (production)`

> **Implemented:** measurement-annotator v1.x (2026-04-12).
> See [annotations/measurement-annotator/README.md](../../annotations/measurement-annotator/README.md)
> §Parameter Schemas for the formal parameter schema.

```
@session_end(rule="first", time=60min, reinforcers=60)
```

- `rule`: `"first"` (whichever first) | `"time_only"` | `"reinforcers_only"`
- Sidman (1960) steady-state estimation and Baron & Perone (1998) procedural description standards
- **Strong recommendation**: Should be made mandatory at the program level

#### 8.1.2 `@response` — Response Topography `Tier 2 (production)`

```
@response(
  force_min=0.15,         -- newtons
  duration_min=0.05,      -- seconds
  irt_min=0.01,           -- debounce / response individuation
  trigger="onset"         -- "onset" | "offset"
)
```

- Prevents "two labs running the same `FR 10` from conducting different experiments"
- Force threshold is part of the response definition itself
- Program level (invariant within a session)

#### 8.1.3 `@pretraining` — Procedural History (Separated from `@history`) `Tier 3 (publication)`

```
@pretraining(
  magazine=2,             -- days
  lever=3,
  criterion="50 presses/session"
)
```

- Subject history (`@history`) and procedural history are different dimensions
- Shaping / autoshaping records

#### 8.1.4 `@context` — Stimulus Context `Tier 2 (production)`

```
@context(
  houselight="on",
  iti_light="off",
  masker="white-noise-70dB"
)
```

- Context definition is decisive in renewal research (Bouton, 2004)
- Program level (constant throughout the session)

#### 8.1.5 `@logging` — Data Recording Specifications `Tier 2 (production)`

```
@logging(
  resolution="10ms",      -- time resolution
  events=["lever", "reinforcer", "sd"]
)
```

- A prerequisite for molecular analysis
- Declaration of temporal resolution is part of reproducibility

#### 8.1.6 `@clock` Extension — Temporal Precision and Synchronization `Tier 1 (unit) / Tier 2 (precision, sampling, sync)`

```
@clock(
  unit="s",
  precision="μs",         -- runtime measurement precision
  sampling=1000,          -- Hz (for continuous data)
  sync="PTP"              -- "PTP" | "NTP" | "trigger"
)
```

#### 8.1.7 `@random` — Global Random Seed `Tier 1 (defaulted)`

```
@random(seed=42, scope="global")
```

- `@algorithm(seed=...)` is for schedule value generation
- `@random(seed=..., scope="global")` is for counterbalancing / stimulus order / everything else
- Both can be declared separately

### 8.2 Additional Proposals (JEAB Review Perspective)

#### 8.2.1 `@session_onset` — Schedule Onset Timing `Tier 2 (production)`

```
@session_onset(
  clock_start="session_start",    -- "session_start" | "first_response"
  houselight="on",
  warmup_complete=true
)
```

- Declaration of inter-component intervals in multiple/chained schedules

#### 8.2.2 `@reinforcer` Extension — Refinement of Temporal Contingency `Tier 2 (production)`

```
@reinforcer(
  "sucrose",
  consumption_window=3s,
  clock_resume="post_consumption"  -- "delivery" | "availability" | "post_consumption"
)
```

- Specifies whether FI interval measurement begins at the moment of reinforcer delivery or after consumption
- JEAB review perspective: Papers that fail to specify the time base of the interval are invariably flagged during review

#### 8.2.3 Distinction Between `@scheduled` and Runtime `obtained`

The DSL declares `@scheduled(VI=60)`, while the runtime records `obtained_rate`.
By **guaranteeing the existence of both** at the schema level, confusion between "VI 60-s the program" and "VI 60-s the subject's experience" is prevented.

- DSL: Declaration of intent only
- session-recorder: Schema-enforced obligation to record the obtained values

#### 8.2.4 `@timeout` — Error Responses / Error Correction `Tier 2 (production)`

```
@timeout(duration=5s, stimuli_off=true, lever_retracted=false)
```

### 8.3 Domain-Specific Extensions (Individual Annotators)

#### 8.3.1 Behavioral Pharmacology — `pharmacology-annotator` (New) `Tier 3 (publication) / @phase: Tier 2`

```
@drug(
  name="cocaine",
  dose=0.5, unit="mg/kg",
  route="iv",              -- "ip" | "iv" | "sc" | "po"
  vehicle="saline",
  injection_volume=0.1,
  pre_session_interval=15min
)

@phase("reinstatement", trigger="cue")
                         -- "acquisition" | "maintenance"
                         -- | "extinction" | "reinstatement"

@preparation(
  implant="iv_catheter",
  location="jugular",
  patency_check="thiopental"
)

@pr_breakpoint(idle="10min")
```

- `@preparation` is separated from `@history` (catheter patency is a session-level variable)
- `@phase` is a **program-level-only** informational label (Tier 3). It does not alter evaluation semantics — extinction is expressed by changing the schedule to `EXT`, not by annotating an active schedule with `@phase("extinction")`. See [boundary-decision.md](boundary-decision.md) §5 for the full rationale

#### 8.3.2 ABA Clinical — `subject-human` (Separated from `subject-animal`) `Tier 3 (publication)`

Separation of annotators is recommended because the ethical frameworks (IACUC vs. IRB) are entirely different.

```
@client(
  age=5,
  vb_mapp(version="2.0", level=2, milestones_passed=42),
  communication_modality="PECS"    -- "vocal" | "PECS" | "SGD" | "sign"
)

@setting("clinic")                 -- "clinic" | "home" | "school" | "community"

@function(
  type="escape",
  evidence="functional_analysis"   -- "FA" | "indirect" | "descriptive"
)

@ioa(
  method="exact",                  -- "exact" | "partial" | "total"
  percent=85,
  sessions_pct=33                  -- % of sessions with IOA measured
)

@ethics(irb="IRB-2026-0042", consent=true, assent=true)
                                   -- opaque field, does not affect DSL semantics
```

**Design principles:**
- `@species`, `@strain`, `@deprivation` are exclusive to subject-animal
- `@client`, `@setting`, `@function`, `@ioa` are exclusive to subject-human
- Only shared neutral fields (e.g., age) belong to subject-base
- **Intervention synthesis (DRA + extinction) is expressed via schedule composition** (placing it at the program level prevents procedural fidelity evaluation)

### 8.4 Session Identification — Separation of Responsibilities from the Implementation/Recording Layer

> **Details**: See [validation-modes.md](validation-modes.md) §7 for the full
> Layer Responsibility Matrix. This section is a summary only. In particular,
> §7.4 proposes moving `experiment_id` / `subject_id` out of the DSL to the
> manifest layer.

Reproducibility unit principle: **"Can the same experiment be run next time?" is the DSL's concern; "What happened this time?" is the recorder's concern**

| Item | Owner | Rationale |
|---|---|---|
| schedule expression | DSL (Tier 0) | Core grammar |
| `@hardware`, `@clock`, `@random` | DSL (Tier 1) | Execution parameters (defaulted) |
| `@session_end`, `@response`, `@logging` | DSL (Tier 2) | Physical experiment declarations |
| `@species`, `@strain`, `@chamber(model)` | DSL (Tier 3) | Publication metadata |
| `experiment_id`, `subject_id` | **manifest** (outside DSL) | Application of the plan, not the plan itself |
| `session_id`, `timestamp` | session-recorder | Runtime artifacts |
| software versions | session-recorder (manifest) | Becomes stale if written in the DSL |
| event code mapping | experiment-io | Responsibility of the HW abstraction |
| calibration measured values | session-recorder | Runtime measurements |
| calibration expected values | DSL (`@hardware(expected=...)`) | Part of the design |

### 8.5 Multi-Session Structure (Point of Contention — Undecided)

**Multi-session structure proposal:**
```
program ABA_reversal {
  session A { baseline }
  session B { treatment }
  session A' { return_to_baseline }
}
```

**Opposing view (maintain 1 DSL = 1 procedure):** Multiple sessions are bundled at the manifest layer.

**Compromise:** Maintain the `1 DSL file = 1 session` principle and bundle multiple DSL files via an external `manifest.yaml`.
"The unit of reproducibility" is guaranteed at the manifest level.

```yaml
# manifest.yaml
experiment: dose-response-cocaine
sessions:
  - file: session_01_vehicle.dsl
    subject: R12
    date: 2026-04-11
  - file: session_02_0.5mg.dsl
  - file: session_03_1.0mg.dsl
```

### 8.6 Items Agreed to Be Outside DSL Scope

- **Automatic steady-state judgment**: Responsibility of the data analysis layer. Judging within the DSL would "confuse procedure with effect." However, **declaring** the steady-state criterion (when to consider responding stable) is implemented as `@steady_state` in measurement-annotator (2026-04-12). What is "outside DSL scope" here is the **automatic execution** of judgment based on the criterion.
- **Institution, grant number, preregistration ID**: Not part of the experimental design. Separated into an external `study.yaml`.
- **Microdialysis / photometry raw data** (behavioral pharmacology perspective): Only a hook such as `@coregister(stream="photometry")`.
- **IRB/IACUC approval number**: Retained as an opaque field (does not affect DSL semantics).

### 8.7 Implementation Priority (Reviewer Recommendations)

**Phase 1 (Highest priority — essential for basic EAB research):**
1. ~~`@session_end`~~ — **Implemented** (measurement-annotator v1.x, 2026-04-12)
2. `@response` — Should be made mandatory
3. `@pretraining` — Separation from `@history`
4. `@context` — Prerequisite for renewal research
5. `@logging` + `@clock` extension

**Phase 2 (Reproducibility enhancement):**
6. `@random` global seed
7. `@session_onset` / `@reinforcer` clock_resume
8. `@scheduled` vs. `obtained` schema separation

**Phase 3 (Domain-specific — owned by each application):**
9. `pharmacology-annotator` (`@drug`, `@phase`, `@preparation`, `@pr_breakpoint`)
10. `subject-human` annotator (`@client`, `@setting`, `@function`, `@ioa`, `@ethics`)

**Phase 4 (Undecided):**
11. Multi-session structure vs. bundling at the manifest layer

### 8.8 Next Steps

1. Prepare boundary test responses (see §2) following `spec/en/annotation-template.md` for each Phase 1 annotation
2. Refactoring to separate `subject-animal` and `subject-human` annotators
3. Create new spec for `pharmacology-annotator`
4. Conduct cross-review from each domain perspective (JEAB, behavioral pharmacology, ABA, reproducibility design) once more before implementation

### 8.9 References

- Baron, A., & Perone, M. (1998). Experimental design and analysis in the laboratory study of human operant behavior. In K. A. Lattal & M. Perone (Eds.), *Handbook of research methods in human operant behavior* (pp. 45-91). Plenum.
- Bouton, M. E. (2004). Context and behavioral processes in extinction. *Learning & Memory*, 11(5), 485-494. https://doi.org/10.1101/lm.78804
- Lattal, K. A. (2010). Delayed reinforcement of operant behavior. *JEAB*, 93, 129-139. https://doi.org/10.1901/jeab.2010.93-129
- Sidman, M. (1960). *Tactics of scientific research*. Basic Books.
- Stokes, T. F., & Baer, D. M. (1977). An implicit technology of generalization. *JABA*, 10(2), 349-367. https://doi.org/10.1901/jaba.1977.10-349
