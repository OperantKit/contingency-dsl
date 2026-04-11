# Annotations Guide

> How to enrich schedule expressions with experimental metadata.
> For the annotation system design, see [annotation-design.md](../../spec/annotation-design.md).

---

## What Are Annotations?

Annotations are **optional metadata** attached to schedule expressions. They declare information needed to *run* an experiment (what reinforcer, which lever, what species) without changing the schedule's *theoretical properties*.

```
FI 10                          -- Theoretically complete. Discuss scallops here.
FI 10 @reinforcer("pellet")    -- Now we know WHAT is delivered.
      @operandum("left_lever") -- Now we know WHERE to respond.
      @subject(species="rat")  -- Now we know WHO is the subject.
```

**Core principle:** `FI 10` is always valid on its own. Annotations are additive, never required.

### Two-Level Scoping

Annotations can appear at two levels in a program:

1. **Program-level** — before parameter declarations (`COD`, `LH`, etc.). These are session-wide defaults: subject conditions, apparatus, temporal parameters.
2. **Schedule-level** — attached to a specific schedule expression. These describe per-contingency details (which operandum, which discriminative stimulus) or override program-level defaults.

This mirrors how scientific papers are structured: **Subjects** and **Apparatus** are described once, before the **Procedure** details.

```
-- Program-level: session-wide defaults
@species("rat")
@strain("Long-Evans")
@chamber("med-associates", model="ENV-007")
@clock(unit="s")

COD = 2s

Conc(VI30s, VI60s)
  @operandum("left_lever", component=1)   -- Schedule-level: per-component
  @operandum("right_lever", component=2)
```

If the same annotation keyword appears at both levels, the schedule-level value overrides the program-level default for that expression.

### Progressive Enrichment

The same schedule expression grows richer as it moves from theory to publication:

| Context | Expression | Annotations Needed |
|---------|-----------|-------------------|
| Theoretical discussion | `FI 10` | None |
| Simulation | `@clock(unit="s")` + `FI 10 @algorithm("fleshler-hoffman")` | temporal |
| Physical experiment | `@species(...)` `@chamber(...)` + `FI 10 @operandum(...) @reinforcer(...)` | All four |
| Paper publication | All of the above | Full — compiles to Methods section |

---

## The Four Recommended Annotators

The contingency-dsl project ships four **recommended annotators** covering
the universal dimensions of experimental procedures. These form the project's
recommended set; programs (runtime / interpreter) are free to adopt, extend,
or replace them (see [design-philosophy.md §4.2](../../spec/ja/design-philosophy.md)).

### 1. stimulus-annotator — What Stimuli Are Involved?

Declares the **identity and function** of stimuli in the experiment.

| Keyword | Purpose | Example |
|---------|---------|---------|
| `@reinforcer` | What is delivered as consequence | `@reinforcer("food", type="unconditioned")` |
| `@sd` | Discriminative stimulus identity | `@sd("red_light", component=1)` |
| `@operandum` | Response device identity | `@operandum("left_lever")` |
| `@brief` | Brief stimulus in second-order schedules | `@brief("light", duration=2)` |

**Example: Concurrent schedule with identified components**

```
Conc(VI30s, VI60s, COD=2s)
  @operandum("left_lever", component=1)
  @operandum("right_lever", component=2)
  @reinforcer("sucrose", concentration="10%", duration=3)
  @sd("red_light", component=1)
  @sd("green_light", component=2)
```

**What this enables:**
- Verify that each `Conc` component has an assigned operandum (referential integrity)
- Compile to: *"Two response levers were available. The left lever (red light) operated on VI 30-s and the right lever (green light) on VI 60-s. Reinforcement consisted of 3-s access to 10% sucrose solution."*

**What does NOT belong here:**
- Physical specifications of stimuli (LED wavelength, sound dB) → apparatus-annotator
- Presentation timing (stimulus duration, ISI) → temporal-annotator
- Learning history of conditioned stimuli → runtime state, not a declaration

**Reference:**
- Kelleher, R. T. (1966). Conditioned reinforcement in second-order schedules. *JEAB*, *9*, 475. https://doi.org/10.1901/jeab.1966.9-475 (brief stimulus as conditioned reinforcer)

---

### 2. temporal-annotator — How Is Time Structured?

Declares **session-level temporal parameters** that affect reproducibility.

| Keyword | Purpose | Example |
|---------|---------|---------|
| `@clock` | Time unit declaration | `@clock(unit="s")` |
| `@warmup` | Pre-session warm-up period | `@warmup(duration=60)` |
| `@algorithm` | Schedule value generation method | `@algorithm("fleshler-hoffman", n=12)` |

Note: `@blackout` and `@cod` were initially proposed for temporal-annotator but have been **promoted to core grammar** as keyword arguments (`BO=5s`, `COD=2s`) because they directly affect contingency structure.

**Example: VI schedule with full temporal specification**

```
VI30s
  @clock(unit="s")
  @algorithm("fleshler-hoffman", n=12, seed=42)
  @warmup(duration=60)
```

**What this enables:**
- Exact reproducibility: another lab can generate the identical VI value sequence from the seed
- Compile to: *"A variable-interval 30-s schedule (Fleshler & Hoffman, 1962; list length = 12) was used. Sessions began after a 60-s warm-up period during which no reinforcement was available."*

**Why `@algorithm` matters:** `VI 30` with Fleshler-Hoffman distribution produces different inter-reinforcement intervals than `VI 30` with arithmetic progression or exponential distribution. The schedule notation alone (`VI30s`) is ambiguous — `@algorithm` resolves this for reproducibility.

**What does NOT belong here:**
- Reinforcer duration → stimulus-annotator (`@reinforcer` duration param)
- Session day number → session metadata, not a time structure
- Hardware response latency → apparatus-annotator

**References:**
- Fleshler, M., & Hoffman, H. S. (1962). A progression for generating variable-interval schedules. *JEAB*, *5*(4), 529-530. https://doi.org/10.1901/jeab.1962.5-529

---

### 3. subject-annotator — Who Is the Subject?

Declares **biological and motivational conditions** of the experimental subject.

| Keyword | Purpose | Example |
|---------|---------|---------|
| `@species` | Species declaration | `@species("rat")` |
| `@strain` | Strain/breed | `@strain("Long-Evans")` |
| `@deprivation` | Establishing operation | `@deprivation(hours=22, target="food")` |
| `@history` | Prior experimental experience | `@history("naive")` |
| `@n` | Number of subjects | `@n(6)` |

**Example: Standard rat operant experiment**

```
FR5
  @species("rat")
  @strain("Long-Evans")
  @deprivation(hours=22, target="food")
  @history("naive")
  @n(8)
```

**What this enables:**
- Compile to: *"Subjects were 8 experimentally naive male Long-Evans rats maintained at 85% free-feeding body weight by 22-hr food deprivation."*
- Cross-experiment comparison: filter by species, deprivation level

**`@deprivation` is an establishing operation (EO):**
In behavior analysis terminology, food deprivation is an establishing operation that increases the reinforcing efficacy of food and evokes food-seeking behavior (Michael, 1982). The annotation captures this motivational variable as a procedural declaration, not an internal state attribution.

**What does NOT belong here:**
- Internal state attributions ("anxiety level", "motivation") → mentalist terms; use `@deprivation` or `@history` instead
- Response topography ("pressed with left paw") → behavioral data, not a declaration
- Group assignment / counterbalancing → experimental design metadata

---

### 4. apparatus-annotator — What Equipment Is Used?

Declares the **physical equipment** used to run the experiment.

| Keyword | Purpose | Example |
|---------|---------|---------|
| `@chamber` | Experimental chamber model | `@chamber("med-associates", model="ENV-007")` |
| `@interface` | Hardware interface | `@interface("serial", port="/dev/ttyUSB0")` |
| `@hw` | Hardware backend | `@hw("teensy41")` or `@hw("virtual")` |

**Example: Physical experiment setup**

```
Conc(VI30s, VI60s, COD=2s)
  @chamber("med-associates", model="ENV-007")
  @hw("teensy41")
  @interface("serial", port="/dev/ttyACM0", baud=115200)
```

**What this enables:**
- Target selection for experiment-io / contingency-bench
- Compile to: *"Sessions were conducted in Med Associates (ENV-007) operant chambers interfaced with a Teensy 4.1 microcontroller via serial connection."*
- `@hw("virtual")` selects the software simulation backend instead of physical hardware

**What does NOT belong here:**
- Logical names for response devices ("left_lever") → stimulus-annotator (`@operandum`)
- Measured response latency / jitter → contingency-bench output, not a declaration
- Software configuration (log paths, output directories) → outside DSL scope

---

## Composing Annotations: A Complete Example

A fully annotated program for a concurrent VI-VI experiment, organized by scoping level:

```
-- Subjects (program-level)
@species("rat")
@strain("Sprague-Dawley")
@deprivation(hours=23, target="food")
@history("naive")
@n(6)

-- Apparatus (program-level)
@chamber("med-associates", model="ENV-007")
@hw("teensy41")

-- Session parameters (program-level)
@clock(unit="s")
@algorithm("fleshler-hoffman", n=12, seed=42)
@warmup(duration=300)
@reinforcer("sucrose", concentration="10%", duration=3)

-- Schedule parameters
COD = 2s
LH = 10s

let left = VI30s
let right = VI60s
Conc(left, right)
  @operandum("left_lever", component=1)   -- schedule-level
  @operandum("right_lever", component=2)  -- schedule-level
  @sd("red_light", component=1)           -- schedule-level
  @sd("green_light", component=2)         -- schedule-level
```

Program-level annotations (Subjects, Apparatus, Session) match the structure of a paper's Method section. Schedule-level annotations describe per-contingency details.

This single DSL source can compile to:
- **Python runtime** (contingency-py + annotator)
- **Rust runtime** (contingency-rs)
- **MedPC syntax** (existing MedPC equipment)
- **Paper Methods section** (natural language)

---

## Creating Custom Annotations

Domain-specific annotations (ABA clinical, OBM social, behavioral pharmacology,
etc.) are not part of the DSL project's recommended set. They can be added
via two routes:

1. **Propose addition to the DSL project's recommended set**
   - Copy `spec/annotation-template.md`
   - Answer the boundary test questions (see [annotation-design.md](../../spec/annotation-design.md) §2)
   - Go through project review to land in the recommended registry

2. **Build your program's own registry**
   - Each program (runtime / interpreter) is free to define its own registry
   - No DSL-project review is required
   - Core DSL grammar stays unchanged

Which route you choose depends on whether the annotation deserves inclusion
in the project-wide recommended set (see
[design-philosophy.md §4.2](../../spec/ja/design-philosophy.md)).

**Boundary test (quick version):** If removing `@X` makes the schedule
theoretically incomplete, it may belong in the core grammar rather than
as an annotation (though core changes are restricted by design-philosophy §7).

---

## References

- Fleshler, M., & Hoffman, H. S. (1962). A progression for generating variable-interval schedules. *JEAB*, *5*(4), 529-530. https://doi.org/10.1901/jeab.1962.5-529
- Kelleher, R. T. (1966). Conditioned reinforcement in second-order schedules. *JEAB*, *9*, 475. https://doi.org/10.1901/jeab.1966.9-475
- Michael, J. (1982). Distinguishing between discriminative and motivational functions of stimuli. *JABA*, *15*(1), 149-155. https://doi.org/10.1901/jaba.1982.15-149
