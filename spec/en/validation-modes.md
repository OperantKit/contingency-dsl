# contingency-dsl Validation Modes — Design Document

## Status: Revised (2026-04-12)

This document presupposes [design-philosophy.md](design-philosophy.md) §4.
Where the two conflict, **design-philosophy.md takes precedence as the canonical source**.

The Tier × Mode model described herein is **one exemplar** of the validation
framework that the DSL project proposes, and simultaneously serves as the
specification of the validators provided by the Python reference implementation.
In accordance with the program-scoped closure principle of design-philosophy
§4.2, each program (runtime / interpreter) is free to adopt, extend, or replace
this model. The provisions of this document are **recommended, not mandatory**.

Related documents:
- [ja/design-philosophy.md](design-philosophy.md) §4 — Annotation layer structure and categories (canonical)
- [annotation-design.md](annotation-design.md) — Recommended annotators and their boundary principles
- [architecture.md](architecture.md) §4.7 — Annotation architecture
- [grammar.ebnf](../../grammar.ebnf) — Formal grammar

---

## 1. Problem Statement

### 1.1 Conflation of Three Kinds of "Necessity"

The claim that a given annotation is "required" conflates three qualitatively
distinct senses. A single mandatory/optional binary judgment cannot
distinguish among them:

| Kind | Meaning | Consequence of omission |
|---|---|---|
| **Execution necessity** | The program cannot run without it | Simulation or experiment cannot proceed |
| **Publication necessity** | Needed for journal submission and peer review | Execution succeeds but the manuscript will not be accepted |
| **Analysis necessity** | Needed for data interpretation and statistical analysis | Execution succeeds but analytic results remain ambiguous |

### 1.2 Concrete Problems Arising from Binary Judgment

**Problem A: Insufficiency of a single mandatory/optional flag**

Consider `@session_end`. On a physical apparatus this annotation is mandatory
— without it, the session never terminates — yet for theoretical discussion
or virtual simulation it is entirely unnecessary. A single "mandatory/optional"
flag cannot express this context dependence; the information about *which*
situations require the annotation is lost.

Similarly, `@species` is mandatory for publication but unnecessary at
execution time. Again, a single flag is inadequate.

By the **program-scoped closure** principle of design-philosophy §4.2,
what counts as mandatory differs from program to program. As one
concretization of this principle, this document proposes the four-tier,
four-mode validator adopted by the Python reference implementation.

**Problem B: Barrier to entry for students**

```
FR5                          -- sufficient for discussion alone
Conc(VI30, VI60, COD=2s)     -- learning about choice procedures
```

The ability to discuss with this minimal notation is a core attraction of the
DSL. If annotations such as `@response(force_min=0.15)` or
`@session_end(time=60min)` were made mandatory at the grammar level, a
student who already has apparatus in the laboratory would be unable to
advance an experimental proposal because "the tests won't pass."

**Core insight:**
> **The DSL must serve both as a minimal discussion tool and as a rigorous
> execution tool, but these roles should be realized in distinct "modes."**

---

## 2. Design Principle: Grammar Is Permissive, Validator Is Strict

The same architecture used by Rust's type system (parser is lenient, borrow
checker is strict), TypeScript's `--strict` mode, and ESLint's rule sets is
adopted here.

```
parse(src)                        → syntactically correct? (Tier 0 only)
lint(src, mode="dev")             → runnable in dev mode?  (Tier 0-1)
lint(src, mode="production")      → runnable on hardware?  (Tier 0-2)
lint(src, mode="publication")     → publishable?           (Tier 0-3)
```

**Four guarantees:**
1. **Grammar-level enforcement is minimal**: `FR5` alone always parses successfully
2. **Lower tiers are unaffected by higher tiers**: publication linter requirements do not surface in dev mode
3. **Modes are cumulative and monotone**: publication mode includes all dev-mode requirements
4. **Error messages indicate the tier**: the mode that triggered the diagnostic is shown to the user

---

## 3. Four Requirement Tiers

### Tier 0 — Core Grammar

**Elements required for parsing itself to succeed. These are grammatical requirements.**

| Example | Description |
|---|---|
| `FR5` | atomic schedule |
| `Conc(VI30, VI60, COD=2s)` | compound schedule + keyword args |
| `let x = VI60 \n Chain(x, FR10)` | let bindings + compound |
| `LH = 10s` | program-level parameter declaration |

**Behavior on omission**: parse error. This is enforced by the grammar.
**Governing document**: BNF production rules in [grammar.ebnf](../../grammar.ebnf)

### Tier 1 — Defaulted Execution Parameters

**Parameters whose values are needed at runtime but can be filled by sensible defaults.**

| Example | Default | Rationale |
|---|---|---|
| `@clock(unit="s")` | `"s"` | ratio schedules are dimensionless; interval/time schedules use seconds |
| `@algorithm("fleshler-hoffman")` | Fleshler-Hoffman (1962) | de facto laboratory standard |
| `@hw("virtual")` | `"virtual"` | default backend |
| `@random(seed=<current_time>)` | current time | execution is possible even without reproducibility |

**Behavior on omission**: the validator operates with the default value. No warning is emitted.
**Relevant annotators**: temporal, apparatus (partial)

### Tier 2 — Production Requirements

**Elements required when `@hw` specifies a value other than virtual (i.e., physical hardware).**
**Not required for simulation (`@hw("virtual")`).**

| Element | Rationale |
|---|---|
| `@session_end(rule, time, reinforcers)` | A physical experiment cannot terminate without a session-end rule |
| `@response(force_min, duration_min, irt_min, trigger)` | A physical operandum requires an explicit response definition to operate |
| `@logging(resolution, events)` | An experiment without data collection is meaningless |
| `@hw("teensy41")` or other specific HW | Switch from simulation to physical apparatus |
| `@operandum("left_lever", ...)` | Identity of the physical device |
| `@interface("serial", port=...)` | Physical connection information |

**Behavior on omission**:
- In `mode="dev"` (virtual HW assumed): ignored
- In `mode="production"` (physical HW assumed): **production error**

**Dependency condition**: activation depends on the value of `@hw` (tier is dynamic)

### Tier 3 — Publication Requirements

**Elements required solely for manuscript preparation, peer review, and replication. Not required for experiment execution.**

| Element | Manuscript section |
|---|---|
| `@species("rat")` | Subjects |
| `@strain("Long-Evans")` | Subjects |
| `@deprivation(hours=22, target="food")` | Subjects |
| `@history("naive")` | Subjects |
| `@pretraining(magazine=2, lever=3)` | Subjects / Procedure |
| `@n(6)` | Subjects |
| `@chamber("med-associates", model="ENV-007")` | Apparatus |
| `@reinforcer("sucrose", concentration="10%")` details | Procedure |
| `@context(houselight, masker)` | Apparatus / Procedure |
| `@ethics(irb, consent, assent)` | (Ethics statement) |
| `@ioa(method, percent)` | (Reliability) |

**Behavior on omission**:
- In `mode="dev"`, `mode="production"`: ignored
- In `mode="publication"`: **publication error**

**Relevant annotators**: subject, apparatus (detailed), ethics (future)

### Tier Independence

**Important**: Tiers denote *kinds of necessity*, not *degrees of importance*.

- Tier 3 (`@species`) is not "less important" than Tier 2 (`@session_end`)
- In the publication phase, a missing Tier 3 element prevents the manuscript from being written
- In the execution phase, a missing Tier 2 element prevents the experiment from running
- **The role of validation modes is to require only what is needed at each phase**

---

## 4. Four Validation Modes

### 4.1 mode="parse" — Syntax Verification Only

```python
parse("FR5")                 # OK
parse("Conc(VI30, VI60)")    # OK (COD omission is a semantic warning only)
parse("@species(\"rat\")")   # still parses OK (annotation accepted)
```

- **Scope**: Tier 0
- **Use cases**: syntax learning, theoretical discussion, teaching materials, unit tests
- **Errors**: parse error, semantic error only
- **Warnings**: none

### 4.2 mode="dev" — Development / Simulation

```python
lint("FR5", mode="dev")
# → OK (warning: no @hw specified, assuming @hw("virtual"))

lint("Conc(VI30, VI60, COD=2s) @hw(\"virtual\")", mode="dev")
# → OK
```

- **Scope**: Tier 0-1
- **Use cases**: student learning, theoretical verification, simulation runs, CI tests
- **Assumption**: `@hw("virtual")` or default (treated as virtual)
- **Errors**: parse/semantic error
- **Warnings**: info-level output if Tier 1 defaulted elements are unspecified (not treated as errors)
- **Example**: `FR5` alone can be run as a simulation

### 4.3 mode="production" — Physical Apparatus Execution

```python
lint("FR5 @hw(\"teensy41\")", mode="production")
# → ERROR: @session_end required for physical HW
# → ERROR: @response required for physical HW
# → ERROR: @logging required for physical HW
# → ERROR: @operandum required for physical HW
```

- **Scope**: Tier 0-2
- **Use cases**: gatekeeper for physical experiments, final pre-experiment verification
- **Activation condition**: automatically activated when `@hw` is set to anything other than virtual
- **Errors**: missing Tier 2 elements
- **Warnings**: missing Tier 3 elements (noting that their absence will cause problems at publication)

**The "mandatory" requirements set out in §8 are realized here.** The parser
does not reject the source, but the moment physical hardware is connected the
validator halts the process.

### 4.4 mode="publication" — Manuscript Compilation

```python
lint(src, mode="publication")
# → ERROR: @species required for Methods section
# → ERROR: @strain required for Methods section
# → ERROR: @deprivation required for Methods section
# → ERROR: @chamber required for Apparatus section
# → ERROR: @n required for Subjects section
```

- **Scope**: Tier 0-3
- **Use cases**: automatic generation of the Methods section, preregistration submission, supplement publication
- **Errors**: missing Tier 3 elements
- **Output**: DSL source + validation pass enables generation of an APA-formatted Methods section

---

## 5. Monotonicity of Modes and the Student Pathway

### 5.1 Cumulative Guarantee

```
parse ⊆ dev ⊆ production ⊆ publication
```

Any program accepted by a higher mode is necessarily accepted by all lower
modes. A program that passes a lower mode may fail at a higher mode.

### 5.2 Formalization of Progressive Enrichment

The "progressive enrichment" currently described informally in
[docs/en/annotations.md](../../docs/en/annotations.md) is here formalized
from the perspective of validation modes:

| Stage | DSL source | Passing modes |
|---|---|---|
| Theoretical discussion | `FR5` | parse |
| Student learning | `Conc(VI30, VI60, COD=2s)` | parse, dev |
| Simulation | above + `@clock(unit="s")` + `@algorithm(...)` | parse, dev |
| Physical experiment preparation | above + `@hw("teensy41")` + `@session_end(...)` + `@response(...)` + `@operandum(...)` + `@logging(...)` | parse, dev, production |
| Manuscript submission | above + `@species` + `@strain` + `@deprivation` + `@chamber` + `@n` | parse, dev, production, publication |

### 5.3 Typical Student Pathway

```
Step 1: Discussion
  User: "I want to understand the difference between FR 5 and FI 10"
  DSL: FR5 / FI10
  Mode: parse ✓

Step 2: Choice procedure
  User: "I want to see a concurrent VI-VI"
  DSL: Conc(VI30, VI60, COD=2s)
  Mode: parse ✓, dev ✓ (can run as virtual)

Step 3: Simulation
  User: "I want to run a simulation"
  DSL: above + @algorithm("fleshler-hoffman", seed=42)
  Mode: dev ✓

Step 4: Hardware connection
  User: "I want to connect to a Teensy"
  DSL: add @hw("teensy41")
  Mode: production ✗
  Errors:
    - @session_end: physical HW requires explicit termination rule
    - @response: physical HW requires force/IRT specification
    - @operandum: physical HW requires operandum identity
    - @logging: physical HW requires logging specification
  → The student is forced to learn what is needed to operate physical apparatus

Step 5: Experiment execution
  DSL: above + @session_end + @response + @operandum + @logging
  Mode: production ✓

Step 6: Manuscript preparation
  User: "I want to generate the Methods section"
  Mode: publication ✗
  Errors:
    - @species, @strain, @deprivation, @chamber, @n are unspecified
  → The student encounters publication-level requirements for the first time
```

**Design guarantees of this pathway:**
- In Steps 1-3, the student does not need to know that Tier 2 or Tier 3 elements exist
- Tiers appear naturally at the stage when they become relevant
- For discussion, learning, and simulation the DSL remains minimal

---

## 6. Alignment with annotation-design.md

### 6.1 Boundary Tests and Their Relationship to Tiers

The boundary tests (Q1-Q3) of annotation-design.md §2 determine the
**Core vs. Annotation** classification. The specific content of the three
questions follows the sole definition in §2 and is not restated in this
document. The tier classification in this section determines, **within a
specific program (this Python reference implementation)**, which mode requires
a given element — after §2 has judged it an "annotation candidate." The two
mechanisms have distinct scopes of responsibility.

Decision flow adopted by this Python reference implementation:

```
Precondition: the boundary tests (Q1-Q3) of annotation-design.md §2
have judged the element an "Annotation candidate" rather than
"consider Core promotion"
(YES → revise grammar.ebnf under the constraints of design-philosophy §8)
  ↓
Tier classification (this document)
  T-A: Is @X a defaulted parameter? (e.g., @clock unit)
    YES → Tier 1
    NO  → ↓
  T-B: Is @X required when physical HW is connected? (e.g., @session_end)
    YES → Tier 2 (mandatory in production)
    NO  → ↓
  T-C: Is @X required in the publication phase? (e.g., @species)
    YES → Tier 3 (mandatory in publication)
    NO  → Tier 1 (informational metadata)
```

**Note:** The tier classification above is the rule followed by this Python
reference implementation's validator. A different program may adopt a
different tier classification; this is permitted by design-philosophy §4.2.

### 6.2 Reclassification of Existing Proposals from annotation-design.md §8

The program-level extensions enumerated in annotation-design.md §8 are
reclassified by tier as follows:

| Current §8 proposal | Reclassified Tier |
|---|---|
| `@session_end` | **Tier 2** (production) — the requirement stated in §8 is realized here |
| `@response(force, IRT)` | **Tier 2** (production) |
| `@logging` | **Tier 2** (production) |
| `@clock(unit)` | **Tier 1** (defaulted, s) |
| `@clock(precision, sampling, sync)` | **Tier 2** (production) |
| `@random(seed)` | **Tier 1** (defaulted, current time) |
| `@timeout` | **Tier 2** (production, conditional) |
| `@session_onset` | **Tier 2** (production) |
| `@reinforcer(clock_resume)` | **Tier 2** (production) |
| `@species`, `@strain` | **Tier 3** (publication) |
| `@deprivation`, `@history`, `@n` | **Tier 3** (publication) |
| `@pretraining` | **Tier 3** (publication) |
| `@chamber(model)` | **Tier 3** (publication) |
| `@context(houselight)` | **Tier 2** (production, physical apparatus) |
| `@drug`, `@phase`, `@preparation` | **Tier 3** (publication) + `@phase` is Tier 2 |
| `@pr_breakpoint` | **Tier 2** (production) |
| `@ioa`, `@ethics`, `@function` | **Tier 3** (publication) |

### 6.3 Preservation of the §2 Principle

The core principle of §2 — "annotations are orthogonal metadata that do not
alter the evaluation semantics" — is **preserved** after the introduction of
validation modes. The only change is the extension that "the requirement
level branches into multiple stages."

- The parser continues to accept annotations as optional
- The presence or absence of annotations does not change the mathematical properties of schedule expressions
- The tier-aware validator activates requirements according to the mode

---

## 7. Layer Responsibility Matrix

The separation of responsibilities from §8.4 is reorganized from the
perspective of validation modes and tiers:

### 7.1 Four Layers

| Layer | Role | Persistence unit |
|---|---|---|
| **DSL (contingency-dsl)** | Static structure of the experimental design (Tier 0-3) | `*.dsl` files |
| **session-recorder** | Runtime logs and observed values | `*.jsonl` event logs |
| **experiment-io** | Hardware abstraction and event codes | HW drivers + mappings |
| **manifest** | External metadata for the experimental design | `study.yaml` / `manifest.yaml` |

### 7.2 Per-Item Responsibilities

| Item | Layer | Rationale |
|---|---|---|
| schedule expression | DSL (Tier 0) | Core of the grammar |
| `@hw`, `@clock`, `@random` | DSL (Tier 1) | Execution parameters |
| `@session_end`, `@response`, `@operandum`, `@logging` | DSL (Tier 2) | Declarations for physical execution |
| `@species`, `@strain`, `@chamber(model)` | DSL (Tier 3) | Publication metadata |
| `session_id`, `timestamp` | session-recorder | Runtime artifacts |
| observed IRT, observed inter-reinforcement interval | session-recorder | Runtime measurements |
| calibration observed values | session-recorder | Runtime measurements |
| calibration expected values | DSL (`@hw(expected=...)`) | Part of the plan |
| event code mapping | experiment-io | Responsibility of the HW abstraction layer |
| software versions | session-recorder (manifest-embedded) | Recorded at runtime because they become stale if placed in the DSL |
| `experiment_id`, `subject_id` | **manifest** (outside the DSL) | "Who" and "which trial" are not part of the plan structure |
| `institution`, `grant`, `preregistration` | manifest | Not part of the experimental design |
| `irb_number`, `iacuc_number` | manifest (opaque) | Audit trail |
| `schedule vs obtained` guarantee | DSL schema (declaration) + recorder (recording obligation) | Both must be present |

### 7.3 Reformulation of the Reproducibility-Unit Principle

> **"Can we run the same experiment next time?" is the DSL's responsibility;
> "What happened this time?" is the recorder's responsibility.**

Restated in terms of tiers:

- **Tier 0-2**: "Information required to run the same experiment on physical apparatus next time"
- **Tier 3**: "Information required to write the same manuscript next time"
- **session-recorder**: "A record of what happened this time"
- **manifest**: "External metadata specifying who, when, and which trial"

### 7.4 Why `experiment_id` / `subject_id` Do Not Belong in the DSL

The classification proposed in annotation-design.md §8.4 —
"`subject_id`, `experiment_id` belong in the DSL" — is **revised by this
document to relocate them to the manifest layer**:

- The DSL defines the **structure of the experimental design** ("what kind of experiment")
- "Who" and "which trial" concern the **application** of the design ("to whom is this design applied"), not the design itself
- To allow the same DSL file to be applied to multiple subjects and multiple days,
  `subject_id` / `experiment_id` / `date` must be separated into an external manifest

```yaml
# manifest.yaml
experiment: dose-response-cocaine
protocol: sessions/fr5_baseline.dsl
subjects:
  - id: R12
    date: 2026-04-11
  - id: R15
    date: 2026-04-12
```

The DSL file becomes **reusable** across multiple execution instances.
This is consistent with the "reproducibility unit" design principle (the DSL
defines "the same experiment"; the manifest defines "which trial").

---

## 8. Implementation Notes

### 8.1 Outline of the Validator API

```python
from contingency_dsl import parse, validate

# Tier 0 only
ast = parse("FR5")

# Tier 0-1
validate(ast, mode="dev")

# Tier 0-2: Tier 2 requirements activate depending on the value of @hw
validate(ast, mode="production")

# Tier 0-3
validate(ast, mode="publication")
```

The return value is a list of diagnostic messages. Each message carries
tier, severity, and message fields.

### 8.2 Dynamic Activation of Tier 2

When `@hw` is `"virtual"`, Tier 2 requirements are relaxed:

```python
# This passes even in production mode (virtual HW)
validate(parse('FR5 @hw("virtual")'), mode="production")
# → OK (Tier 2 elements are not required for virtual)

# This fails in production mode
validate(parse('FR5 @hw("teensy41")'), mode="production")
# → ERROR: @session_end required (Tier 2)
# → ERROR: @response required (Tier 2)
```

### 8.3 Mode Independence Test

**Invariant:**
```python
for mode in ["parse", "dev", "production", "publication"]:
    for src in ALL_VALID_MINIMAL_SRCS:
        assert validate(parse(src), mode=mode).ok
```

Minimal examples such as `FR5` are **guaranteed to pass in all modes**
(a program that requires only Tier 0 is always OK in every mode).

### 8.4 Tier Display in Error Messages

```
error[E-tier2]: @session_end is required for physical HW
  --> session.dsl:1:1
  |
1 | FR5 @hw("teensy41")
  |     ^^^^^^^^^^^^^^^ physical HW specified here
  |
  = note: this requirement is active in mode="production"
  = note: to skip this check, use @hw("virtual") or mode="dev"
  = help: add @session_end(rule="first", time=60min, reinforcers=60)
```

The tier, mode, and available workarounds are made explicit in the error
message (modeled on Rust's diagnostic format).

---

## 9. Open Design Questions

### 9.1 Dynamic Tiers

The mechanism by which Tier 2 activation depends on the value of `@hw` is
straightforward, but whether additional dynamic tiers are needed should be
investigated:

- When `@phase("extinction")` is specified, does `@reinforcer` become unnecessary?
- In a multiple schedule, does `@sd` become mandatory?

### 9.2 Tier Ownership

- Should the tier classification be declared by the annotation itself (self-describing)?
- Or should an external tier registry be created?

This decision will be made when the meta-DSL (annotation-design.md §7) is introduced.

### 9.3 Flexibility of the Mode Hierarchy

Whether modes beyond `"dev"`, `"production"`, and `"publication"` are needed:
- `"teaching"` — Tier 0 only, no warnings at all (for teaching materials)
- `"simulation_precise"` — intermediate between dev and production
- `"preregistration"` — stricter than publication, requiring a pre-analysis plan

Future extensions can be accommodated by adding to the set of modes (as long
as monotonicity is preserved).

### 9.4 Warning vs. Error Boundary

Whether the boundary between Tier 1 warnings and Tier 2 errors is fixed or
user-configurable. Whether ESLint-style rule-set enable/disable is permitted.

---

## 10. References

- Sidman, M. (1960). *Tactics of scientific research*. Basic Books.
- Baron, A., & Perone, M. (1998). Experimental design and analysis in the laboratory study of human operant behavior. In K. A. Lattal & M. Perone (Eds.), *Handbook of research methods in human operant behavior* (pp. 45-91). Plenum.
- Fleshler, M., & Hoffman, H. S. (1962). A progression for generating variable-interval schedules. *JEAB*, 5(4), 529-530. https://doi.org/10.1901/jeab.1962.5-529
- annotation-design.md §2 (boundary tests), §6 (two-tier scoping), §8 (program-level extensions)
- architecture.md §4.7 (annotation architecture)
- docs/en/annotations.md / docs/ja/annotations.md (informal description of Progressive Enrichment)
