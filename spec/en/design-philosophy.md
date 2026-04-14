# contingency-dsl Design Philosophy

> **Status:** Authoritative design intent (2026-04-12)
>
> This document captures the design intent as directly stated by the project
> owner, preserving the original utterances as faithfully as possible. All
> subsequent spec revisions, annotation additions, and meta-DSL design
> decisions must be validated for consistency against this document.

---

## 1. Supreme Objective

**Enable accurate DSL representation of all experimental procedures to date, particularly those in behavior analysis (experimental analysis of behavior).**

This is the supreme goal; every other design decision serves this objective.
To achieve this goal, **the stability of the Core grammar is treated as the
highest priority, and the design pursues an architecture that does not
require breaking changes** (see §2 and §8 for details).

## 2. An Empirically Stable Foundation — The Core / Schedule Extension / Annotation Three-Layer Architecture

Throughout the history of the experimental analysis of behavior, despite
minor differences in theoretical interpretation or stimulus construal,
**the foundations of the three-term contingency and reinforcement schedules
have never collapsed and have constituted a stable basis for the discipline**.
The DSL design reflects this empirically observed stability.

However, this stability is **the current state based on empirical
observation**, not an absolute guarantee. In principle, the discipline
itself could collapse in the future; in that event, even the Core would
require exceptional modification. This DSL fixes the "currently most stable
layer" as Core; it does not claim "eternally immutable truth."

Accordingly, the DSL adopts the following **five-layer architecture**:

| Layer | Content | Tolerance for change |
|---|---|---|
| **Core (empirically stable)** | Three-term contingency, reinforcement schedules, compound schedules, modifiers. Criteria are literal values determined at parse time. CFG + non-TC. | Breaking changes are avoided in principle (see §8 for exceptions) |
| **Core-Stateful (established, stateful criteria)** | Schedules whose criteria are computed from runtime state (response history, trial outcomes, elapsed time as continuous function). Established in the discipline (§2.1 admission criteria). Parameters are declarative. | §8.1 additive procedure + §2.1 admission gate |
| **Experiment (declarative phase structure)** | Multi-phase experimental designs. Arranges Core ScheduleExpr nodes into ordered phases with declarative phase-change criteria (Stability, FixedSessions, PerformanceCriterion, etc.). Follows JEAB conventions: shared annotations inherited across phases, per-phase overrides. See `schema/experiment/`. | Additive (new Criterion types may be added). Core schema is not modified. |
| **Schedule Extension (extended schedule grammar)** | Non-standardized or user-defined schedule constituents. New schedule primitives added at program scope | Each program extends by loading extension modules into its own registry |
| **Annotation (metadata)** | Extended theories, detailed procedures, interpretation-dependent supplementary information | Freely added or removed in step with theoretical development and decline. Program-scoped |

Both Core and Core-Stateful are **common to all programs** (shared
vocabulary). The structural distinction: Core schedules have criteria that
are literal values (`FR 5`: criterion = 5 responses), while Core-Stateful
schedules have criteria computed from runtime state (`Pctl(IRT, 50)`:
criterion = median of recent IRT distribution). See §2.1 for details.

Schedule Extension and Annotation are **program-scoped**: each program
can define, adopt, or reject its own registry. See §4 (Annotation) and §5
(Schedule Extension) for details.

### 2.1 Core-Stateful Layer

Core-Stateful accommodates schedules that are **established in the
discipline** but whose reinforcement criteria require runtime state for
evaluation. These schedules share the Core's role as shared vocabulary
(common to all programs) while acknowledging that their evaluation
properties differ from Core's full static decidability.

**Structural distinction:**

| Property | Core | Core-Stateful |
|---|---|---|
| Syntax | CFG | CFG |
| Parameters | Literal values (parse-time) | Literal values (parse-time) |
| Reinforcement criterion | Comparison against literal | Comparison against runtime-computed value |
| Structural equivalence | Decidable | Undecidable (distribution-dependent) |
| Scope | Common to all programs | Common to all programs |

**Admission gate:** A schedule qualifies for Core-Stateful when it
satisfies (1) the disciplinary-establishment criteria below and (2) all
parameters are declarative (literal values determined at parse time).

The disciplinary-establishment criteria require:
- **N1 (Named procedure):** Multiple independent research groups use the
  same name for the procedure.
- **N2 (Primary literature):** At least one peer-reviewed publication
  provides an operational definition reproducible in sufficient detail.
- **N3 (Temporal persistence):** 20+ years since first publication, with
  publications in at least 2 non-overlapping decades.
- **Evidence score ≥ 3/5** across: (E1) JEAB/JABA publication,
  (E2) cross-laboratory replication in EAB/ABA, (E3) textbook inclusion,
  (E4) parametric study or theoretical integration, (E5) applied/
  translational use with human participants.

**Promotion process:** To promote a schedule to Core-Stateful, follow these steps:

1. **Proposal:** Submit an RFC to spec/ containing (a) the operational
   definition of the target schedule, (b) evidence of N1–N3 + E1–E5
   satisfaction (with citations), (c) confirmation that all parameters are
   declarative, and (d) a proposed syntax (grammar addition).
2. **Review:** The project owner approves the RFC. In borderline cases,
   the eab-researcher agent verifies disciplinary-establishment criteria
   and the pl-theorist agent verifies grammatical consistency.
3. **Implementation:** After approval, add production rules to
   `schema/core-stateful/grammar.ebnf`, AST nodes to ast-schema.json, and
   update both Python and Rust parsers, following the §8.1 additive procedure.
4. **Recording:** Add the promoted schedule to the constituents table below
   and remove it from §5.6.

**Current Core-Stateful constituents:**

| Schedule | Origin | Criterion = f(?) |
|---|---|---|
| Percentile (`Pctl`) | Platt (1973); Galbicka (1994) | f(response history) |
| Adjusting (`Adj`) | Blough (1958); Mazur (1987) | f(trial outcome) |
| Interlocking | Ferster & Skinner (1957) | f(elapsed time, continuous) |

## 3. User Structure

Users differ by layer. This distinction must not be conflated.

### 3.1 Users of the Core DSL

**All researchers, students, and anyone who uses it as a common language.**

Notations such as `FR 5`, `Chain(FR 5, FI 30-s)`, and `Conc(VI 30-s, VI 60-s)` must
function as a shared notation that any person trained in behavior analysis
can read and write.

### 3.2 Users of the Annotated DSL

**It is not a goal of this DSL for users to be able to write annotated DSL
directly from scratch** (the primary writers are conversion tools, or
humans working under tool assistance).

On the other hand, annotated DSL has **high educational value as something
to be read**. In particular, by explicitly verbalizing experimental
procedures, it serves an extremely important role as **material that makes
the dependent variable of an experiment explicit for students**. In the
experimental procedures of behavior analysis, where implicit assumptions
are prevalent, annotated DSL functions as an apparatus for visualizing the
structure of experimental designs that are difficult to discern from the
text of a paper alone.

The intended users are organized into two categories:

1. **Writers (agents of mechanical conversion)**
   Persons and conversion tools that transform programs described in papers
   or in DSL for purposes of replication or demonstration.
2. **Readers (humans)**
   - Students — learners who read the dependent variables, independent
     variables, and control conditions of experimental procedures
   - Researchers — readers who verify experimental designs for replication,
     peer review, or reproducibility confirmation

In other words, annotated DSL is **not an instructional target for
composition, but it is an instructional target for comprehension, and
simultaneously a target of mechanical conversion and verification**.

## 4. Structure and Categories of the Annotation Layer

Annotation serves as a supplementary mechanism for the Core DSL, carrying
supplementary information about experimental procedures. This section
defines the category system for annotations and the principle that
categories are "recommended classifications" rather than mandates.

### 4.1 Recommended Category System (Aligned with the JEAB Method Section)

Annotations are recommended to be classified into the following categories.
Category names conform to the traditional divisions of the JEAB Method
section (Subjects / Apparatus / Procedure), preserving a structure familiar
to readers in behavior analysis. Measurement is separated as a distinct
category to ensure the independence of measurement criteria.

| Category | Recommended annotator | Target | Primary purpose |
|---|---|---|---|
| **Procedure** | `procedure-annotator` (stimulus + temporal sub-annotators) | Description of procedures | (1) Making implicit procedures explicit, (2) supporting equivalence judgments between two procedures, (3) supplementing conditions necessary for mutual conversion between DSL and experimental programs |
| **Subjects** | `subjects-annotator` | Subjects (organisms) | Recording subject history, establishing operations, food-deprivation levels, species, and state. Documents factors that cause behavioral differences even when current contingencies are identical. |
| **Apparatus** | `apparatus-annotator` | Apparatus and physical implementation | Chamber, operandum, hardware specifications, timing tolerances, physical-quantity constraints, and other information that grounds the Core DSL's abstractions in the physical world. |
| **Measurement** | `measurement-annotator` | Measurement criteria | Steady-state criteria, baseline rates, phase-termination conditions, dependent measures, and other information that specifies *when and how* to read the effects of contingencies expressed in the Core. |

Annotator names and JEAB categories have a **1:1 correspondence**
(see [annotation-design.md §3.7](annotation-design.md)). The category to
which an annotator belongs is immediately apparent from the annotator name.
Annotators that do not fit the four JEAB categories are placed under
`annotations/extensions/`.

The three purposes of the Procedure category (making implicit procedures
explicit, equivalence judgment, mutual-conversion supplementation) represent
the core roles that this DSL has demanded of annotations from the outset;
the other categories occupy a complementary position.

### 4.2 Categories Are *Recommended Classifications*, Not Mandates

The category system in §4.1 is a **recommended classification** published
by the DSL project. The Core DSL grammar is unaware of categories; the
actual category assignment of annotations is performed by the annotation
registry and each program (runtime / interpreter).

Consequently, **adding, deleting, ignoring, or redefining categories does
not entail any change to the Core DSL**. This property ensures that:

- If a third-party program decides "we manage environmental conditions
  externally, so we do not handle them in the DSL," it can silently ignore
  Apparatus-category annotations. No change to the Core DSL is required.
- A different research group can define its own categories (e.g., derived
  relational responding, clinical classification) and load them into its
  own program. There is no need to wait for revisions to the canonical DSL.
- Programs dealing with competing theories can reinterpret or replace
  existing categories.

Through this architecture, **program extension and the establishment of
competing theories are possible without destroying or regenerating the
Core DSL**. This is the implementation-layer concretization of the §2
requirement to "maintain scholarly robustness while tracking the
development and decline of theories."

### 4.3 Principle of Category-Neutral Program Equivalence

**Principle:** Category classification exists for *organizational* purposes
and is not part of program semantics. The ground truth is the generated
experimental program itself.

From this principle, the following corollaries obtain:

1. **When the same annotation can belong to multiple categories, any
   classification is valid as long as the generated program is identical.**
   For example, whether `@body_weight(80%)` is interpreted as Subjects
   (food-deprivation level as an establishing operation) or as Procedure
   (pre-session manipulation) is immaterial so long as the generated
   experimental program is the same. Differences in classificatory
   perspective across schools are tolerated.

2. **Detection of overlap or incompatibility is the responsibility of the
   program.**
   The DSL itself does not adjudicate logical conflicts among annotations.
   Each program detects conflicts according to its own rules and rejects
   them as compile errors or parse errors. This keeps the DSL neutral with
   respect to theoretical disputes.

3. **There are no DSL-side constraints on category extension.**
   Third parties are free to define new categories and to ignore or
   redefine existing ones. No mechanism is provided that requires revisions
   to the canonical DSL in order to extend. Responsibility for annotation
   overlap and compatibility rests with the receiving program.

### 4.4 Domains Not Included in the Recommended Classification (Illustrating Extensibility)

The following are domains that do not directly correspond to the JEAB Method
section structure but may be extended by third parties in the future. These
are **illustrative examples of extensibility, not formal reservations**.
By the principle of §4.2, all of them can be defined without any change to
the Core DSL.

- **Clinical** — FBA results, clinical classification labels for
  interventions (DRA / DRI / NCR, etc.), social validity. May be needed in
  applied behavior analysis practice.
- **Derived relational responding** — Prior predictions of derived
  relational responding, functional roles of contextual cues
  (Crel / Cfunc), Baseline / Probe / Test distinctions. May be needed in
  procedures dealing with stimulus equivalence or relational frame theory.
- **Provenance metadata** — Author, version, date, revision history, and
  other document-management information external to the procedure.
- **Domain-specific extensions** — Information required by specific research
  domains such as behavioral pharmacology, neuroscience, or social behavior.

## 5. Schedule Extension Layer — Non-Standardized and User-Defined Schedule Constituents

### 5.1 An Extension Mechanism Distinct from Annotation and Core-Stateful

The Annotation layer handles **metadata** (information appended to
procedures). Core-Stateful (§2.1) handles **established schedules with
stateful criteria**. However, some experimental procedures require
extension of the schedule structure itself and are either not yet
established in the discipline or have parameters that are not declarative.
Representative examples include:

- **Conjugate reinforcement** — The reinforcer is delivered continuously in
  proportion to response magnitude. The response–reinforcer relationship is
  not a discrete schedule event. (Admission criterion E2 not yet satisfied.)
- **Laboratory-specific schedules** — Custom schedule constructs defined by
  individual research programs that have not achieved cross-laboratory
  standardization.
- **Schedules with computed parameters** — Schedules whose parameters are
  themselves expressions rather than literal values.

To accommodate these constituents that are "neither Core, Core-Stateful,
nor annotation," this DSL defines the **Schedule Extension layer**.

### 5.2 Positioning of Schedule Extension

| Layer | Role | Closure | Example |
|---|---|---|---|
| Core | Immutable schedule foundation (literal criteria) | Common to all programs | `FR 5`, `Conc(VI 30-s, VI 60-s)`, `Chain(FR 5, FI 30-s)` |
| Core-Stateful | Established schedules with runtime-computed criteria | Common to all programs | `Pctl(IRT, 50)`, `Adj(start=FR 1, step=2)` |
| **Schedule Extension** | Non-standardized / user-defined schedule constituents | Program-scoped | Laboratory-specific schedules, conjugate reinforcement |
| Annotation | Metadata | Program-scoped | `@reinforcer`, `@species`, `@chamber` |

Schedule Extension is the **second program-scoped extension dimension**
alongside Annotation, but differs in role:

- **Annotation** attaches supplementary information to schedule expressions
  (metadata)
- **Schedule Extension** **adds new constructs** to schedule expressions
  themselves (grammar-level)

### 5.3 Properties of Schedule Extension

1. **Core grammar remains immutable**
   Schedule Extension is realized by adding production rules to the Core
   grammar, but it does not rewrite existing Core rules. In programs that do
   not load a given extension, its constituents become unknown tokens and
   produce a parse error.

2. **Program-scoped closure**
   Each program (runtime / interpreter) maintains its own extension
   registry. Program A may be able to interpret `Percentile` while
   Program B cannot. Both programs can process the Core portion with the
   same parser.

3. **Static verification boundary**
   Schedule structures within the Core are fully statically verifiable
   (reachability, dead code, etc.). Each Schedule Extension module provides
   its own verification rules. The combination of Core plus a specific
   program's extension registry determines the decidable scope of static
   verification.

4. **Protection of the TC boundary**
   It is permissible for a Schedule Extension module to introduce
   TC-proximate functionality (dynamic computation, state, history).
   What matters is that **the Core does not introduce TC**; delegating TC
   functionality to the extension layer is consistent with this policy.

5. **Equivalence judgment is the extension's responsibility**
   Equivalence of identical Schedule Extension constituents (e.g., whether
   two `Percentile` expressions are equivalent) is judged by rules provided
   by the extension module. The Core's equivalence rules do not apply to
   extension constituents.

### 5.4 Boundary with Annotation

Criteria for determining "Is it an annotation or a Schedule Extension?":

| Question | Annotation | Schedule Extension |
|---|---|---|
| Does it alter the structure of the procedure? | No (metadata only) | Yes (new schedule constituent) |
| Does it satisfy the §2.1 disciplinary-establishment criteria? | (N/A — metadata is not a promotion candidate) | No (if satisfied, it is a Core-Stateful promotion candidate) |
| Does it change the evaluation result of an existing Core schedule expression? | No | Yes (introduces new evaluation) |
| Syntactic position in source | Post-fixed to expression (`FR 5 @name(...)`) | The expression form itself (`Name(...)`) |

A percentile schedule "dynamically computes the threshold for DRL" and
**changes the evaluation result of the schedule expression**; therefore it
cannot be handled as an annotation. It belongs in the Schedule Extension
layer as its own constituent.

In contrast, `@reinforcer("food")` is an attachment of metadata that does
not affect schedule evaluation and belongs in the Annotation layer.

### 5.5 Third-Party Extension

Programs can freely create, load, or omit Schedule Extension modules:

- One laboratory defines a custom `TitrationSchedule(...)` and incorporates
  it into their program
- Another laboratory defines an entirely different `AdaptiveFR(...)`
- A program for basic experiments only loads no extensions at all

None of these require changes to the Core DSL. This can be understood as
the program-scoped closure principle of design-philosophy §4.2 extended to
the schedule-grammar level.

### 5.6 Schedule Extension Candidates for This DSL Project

This DSL project does **not provide** Schedule Extensions for the time
being. Percentile and Adjusting schedules, formerly listed here as
extension candidates, have been promoted to Core-Stateful (§2.1) on the
basis of the §2.1 disciplinary-establishment criteria. The remaining
candidate:

- `conjugate-extension` — Continuous reinforcement procedures in the Rovee-Collier tradition (admission criterion E2 not yet satisfied)
- `yoked-extension` — Yoked control procedures (Church, 1964). Requires cross-subject reinforcement parameter referencing, which exceeds the single-program scope of Core. To be addressed via a multi-subject extension layer such as social-annotator.

These candidates may be added after the v1.0 Core freeze and will follow
the additive extension procedure described in §8.1.

## 6. Implementation Language Strategy

**Python and Rust are implemented in parallel from the outset.**

- **Python:** Affinity with researchers, education, and analysis pipelines
- **Rust:** HIL, timing guarantees, embedded systems, performance

This dual-language parallel implementation serves as a structural safeguard
against the DSL degenerating into "a dialect of a particular runtime." A
single spec (grammar / AST schema / annotation definitions) must be capable
of driving both implementations.

**Implication:** Language independence is a de facto requirement of this DSL.
Designs that make annotation value representations dependent on a specific
language's type system are not permitted.

## 7. Near-Term Goals and Deferrable Items

### 7.1 Near-Term Goals

- Reach a state where **existing experimental procedures can in principle
  be described in the DSL**.
- Secure the robustness of the Core grammar so that subsequent breaking
  changes become unnecessary.
- Establish a regime in which both the Python and Rust implementations are
  driven from the same specification.

### 7.2 Deferrable Items

The following can be undertaken at any time provided the DSL foundation is
robust. Foundation establishment takes priority; these are deprioritized:

- Runtime integration such as "write `FR 5` and a simulator emits data"
- Pipelines for reproducing figures from papers
- Student-oriented teaching materials and tutorials

## 8. Avoidance of Breaking Changes and Exception Conditions

Breaking changes to the Core grammar are **avoided in principle**. However,
as stated in §2, the stability of the Core is grounded in empirical
observation and is not an absolute guarantee. Exception conditions are
therefore explicitly acknowledged.

### 8.1 Standard Procedure

1. When the need arises to express a new experimental procedure, consider
   the following in order:
   a. **Can it be absorbed in the Annotation layer** (metadata layer, §4)?
   b. **Can it be absorbed in the Schedule Extension layer** (new schedule
      constituent, §5)?
   c. Consider addition to the Core grammar (last resort).
2. When addition to the Core is necessary, it must be **additive only**
   (no modification of existing syntax or semantics).

### 8.2 Conditions Under Which Breaking Changes Are Exceptionally Permitted

Breaking changes may be considered when any of the following conditions
are met:

- **Collapse of the disciplinary foundation**: The concepts of the
  three-term contingency or reinforcement schedules themselves are found
  untenable in light of future theoretical developments.
- **Critical error in the Core grammar**: The current Core grammar is found
  to be unable to correctly represent the behavior-analytic concepts it
  purports to capture.
- **Structurally unabsorbable by additive means**: A structural problem is
  discovered that cannot be expressed by Annotation, Schedule Extension, or
  additive-only changes.

### 8.3 Obligations When Making Breaking Changes

When a breaking change is judged unavoidable:

1. Increment the major version.
2. Simultaneously provide a conversion tool that enables mechanical
   migration of DSL written in the old version to the new version.
3. Record the motivation for the change against this document (specifying
   which condition in §8.2 applies).

---

## Relationship of This Document to Other Specs

This document is the superordinate document that states the "why" of
design and sits above the following spec documents:

- [evaluation-criteria.md](evaluation-criteria.md) — Six axes for evaluating design decisions (derived from this document)
- [design-rationale.md](design-rationale.md) — Alternatives considered and why the current design was chosen
- [grammar.ebnf](../../grammar.ebnf) — Core grammar
- [ast-schema.json](../../ast-schema.json) — Abstract syntax tree schema
- [annotation-design.md](annotation-design.md) — Annotation boundary principles and the AnnotationModule Protocol
- [validation-modes.md](validation-modes.md) — Verification system organized by Tier × Mode
- [representations/DESIGN.md](../../representations/DESIGN.md) — Design of alternative coordinate systems

If any spec contradicts this document, **this document takes precedence as
the canon**. When a contradiction is discovered, the relevant spec should be
revised or its relationship to this document annotated.

---

## Provenance

This document was produced by directly transcribing the design intent stated
by the project owner on 2026-04-12. The wording has been edited with the
policy of preserving the original utterances as faithfully as possible;
interpretive additions have been kept to a minimum.
