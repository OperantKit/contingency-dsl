# Annotations Guide

> How to enrich schedule expressions with experimental metadata.
> For the annotation system design, see [annotation-design.md](../../spec/en/annotation-design.md).

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

COD = 2-s

Conc(VI 30-s, VI 60-s)
  @operandum("left_lever", component=1)   -- Schedule-level: per-component
  @operandum("right_lever", component=2)
```

If the same annotation keyword appears at both levels, the schedule-level value overrides the program-level default for that expression.

### Progressive Enrichment and Validation Modes

The same schedule expression grows richer as it moves from theory to publication. Each stage corresponds to a **validation mode** that checks only what's needed at that point:

| Context | Expression | Validation Mode | Tier |
|---------|-----------|----------------|------|
| Theoretical discussion | `FR 5` | `parse` | Tier 0 only |
| Simulation | + `@clock(unit="s")` `@algorithm(...)` | `dev` | Tier 0-1 |
| Physical experiment | + `@hardware("teensy41")` `@session_end(...)` `@response(...)` `@operandum(...)` | `production` | Tier 0-2 |
| Paper publication | + `@species(...)` `@strain(...)` `@chamber(...)` `@n(...)` `@dependent_measure(...)` `@training_volume(...)` | `publication` | Tier 0-3 |

**Key guarantee:** `FR 5` alone always passes *every* mode. Annotations are never required by the parser. Instead, `production` and `publication` validators enforce progressively stricter requirements depending on the stage of work.

A student writing `FR 5` for a class discussion never encounters `@species` or `@response`. Those requirements appear naturally when connecting physical hardware (Tier 2) or compiling a Methods section (Tier 3).

For the full specification of tiers and modes, see [validation-modes.md](../../spec/en/annotations/validation-modes.md).

---

## The Four Recommended Annotators (JEAB 4-category mapping)

The contingency-dsl project ships four **recommended annotators** whose
names correspond 1:1 to the JEAB Method section headings (Procedure /
Subjects / Apparatus / Measurement).

| JEAB Category | Annotator | Keywords |
|---|---|---|
| Procedure | `procedure-annotator` (stimulus + temporal + context sub) | `@reinforcer`, `@sd`, `@brief`, `@clock`, `@warmup`, `@algorithm`, `@iti`, `@post_blackout`, `@context` |
| Subjects | `subjects-annotator` | `@species`, `@strain`, `@deprivation`, `@history`, `@n` |
| Apparatus | `apparatus-annotator` | `@chamber`, `@operandum`, `@interface`, `@hardware` (alias: `@hw`), `@feeder` |
| Measurement | `measurement-annotator` | `@session_end`, `@baseline`, `@steady_state`, `@dependent_measure`, `@training_volume`, `@microstructure`, `@phase_end`, `@logging`, `@iri_window`, `@warmup_exclude` |

These form the project's recommended set; programs (runtime / interpreter)
are free to adopt, extend, or replace them (see
[design-philosophy.md §4.2](../../spec/ja/design-philosophy.md)).

### 1. procedure-annotator/stimulus — What Stimuli Are Involved?

Declares the **identity and function** of stimuli in the experiment.

**`@reinforcer` aliases:** `@reinforcer` is the **primary form** (the most
established term in EAB literature). `@punisher` and `@consequentStimulus`
are equivalent aliases — use them when you want to make the experimenter's
intent explicit in source (e.g., `FR 3 @punisher("shock")`). All three collapse
to the same AST node and do not affect equivalence judgment. See
[annotation-design.md §3.5](../../spec/en/annotation-design.md) for details.

| Keyword | Purpose | Example |
|---------|---------|---------|
| `@reinforcer` | Declares a reinforcer (primary form) | `@reinforcer("food", type="unconditioned", access_duration=3)` |
| `@sd` | Discriminative stimulus identity | `@sd("red_light", component=1)` |
| `@brief` | Brief stimulus in second-order schedules | `@brief("light", duration=2)` |

Note: `@operandum` (response device identity) was previously listed here but
moved to **apparatus-annotator** on 2026-04-12. See the Apparatus section below.

**Example: Concurrent schedule with identified components**

```
Conc(VI 30-s, VI 60-s, COD=2-s)
  @operandum("left_lever", component=1)
  @operandum("right_lever", component=2)
  @reinforcer("sucrose", concentration="10%", duration=3)
  @sd("red_light", component=1)
  @sd("green_light", component=2)
```

**What this enables:**
- Verify that each `Conc` component has an assigned operandum (referential integrity)
- Compile to: *"Two response levers were available. The left lever (red light) operated on VI 30-s and the right lever (green light) on VI 60-s. Reinforcement consisted of 3-s access to 10% sucrose solution."*

**`@reinforcer` `access_duration` parameter:** Reinforcer access duration (seconds the hopper remains raised, or access time to the pellet) is owned by `@reinforcer` as an attribute of the reinforcer itself. Ferster & Skinner (1957) used 4-s hopper access as standard but never included it in schedule notation. Making this implicit parameter explicit guarantees reproducibility.

**What does NOT belong here:**
- Physical specifications of stimuli (LED wavelength, sound dB) → apparatus-annotator
- Session-level temporal structure (ITI, warm-up, blackout) → procedure-annotator/temporal
- Physical constraints of reinforcer delivery (minimum IRI) → apparatus-annotator (`@feeder`)
- Learning history of conditioned stimuli → runtime state, not a declaration

**Reference:**
- Kelleher, R. T. (1966). Conditioned reinforcement in second-order schedules. *JEAB*, *9*, 475. https://doi.org/10.1901/jeab.1966.9-475 (brief stimulus functioning as conditioned reinforcer)

---

### 2. procedure-annotator/temporal — How Is Time Structured?

Declares **session-level temporal parameters** that affect reproducibility.

| Keyword | Purpose | Example |
|---------|---------|---------|
| `@clock` | Time unit declaration | `@clock(unit="s")` |
| `@warmup` | Pre-session warm-up period | `@warmup(duration=60)` |
| `@algorithm` | Schedule value generation method | `@algorithm("fleshler-hoffman", n=12)` |
| `@iti` | Inter-Trial Interval | `@iti(duration=10)` |
| `@post_blackout` | Post-reinforcement blackout (schedule-inactive period after reinforcer access) | `@post_blackout(duration=2)` |

Note: `@blackout` and `@cod` were initially proposed as temporal annotations but have been **promoted to core grammar** as keyword arguments (`BO=5-s`, `COD=2-s`) because they directly affect contingency structure.

**Example: VI schedule with full temporal specification**

```
VI 30-s
  @clock(unit="s")
  @algorithm("fleshler-hoffman", n=12, seed=42)
  @warmup(duration=60)
  @iti(duration=10)
  @post_blackout(duration=2)
```

**What this enables:**
- Exact reproducibility: another lab can generate the identical VI value sequence from the seed
- Compile to: *"A variable-interval 30-s schedule (Fleshler & Hoffman, 1962; list length = 12) was used. Sessions began after a 60-s warm-up period during which no reinforcement was available. A 2-s blackout followed each reinforcer delivery."*

**Why `@algorithm` matters:** `VI 30` with Fleshler-Hoffman distribution produces different inter-reinforcement intervals than `VI 30` with arithmetic progression or exponential distribution. The schedule notation alone (`VI 30-s`) is ambiguous — `@algorithm` resolves this for reproducibility.

**`@algorithm` `n` parameter:** The `n` parameter specifies the series length (number of intervals) in the Fleshler-Hoffman progression. Fleshler & Hoffman (1962) discussed N=12 and N=20; the choice of N affects the shape of the resulting interval distribution. When `n` is omitted, it defaults to `null`, meaning the runtime chooses an appropriate value. This is intentional for educational contexts where the focus is on understanding the schedule type rather than exact replication. For published research, explicitly specifying `n` is strongly recommended to ensure reproducibility.

**`@iti` and `@post_blackout` design rationale:** ITI and post-reinforcement blackout do not change the schedule's contingency structure (boundary test: can you discuss FI scallops without `@iti`? → YES). However, they are essential for method description and reproducibility as session-level temporal parameters, on the same level as `@warmup`.

**What does NOT belong here:**
- Reinforcer access duration → procedure-annotator/stimulus (`@reinforcer` `access_duration` param)
- Minimum inter-reinforcement interval (IRI) → apparatus-annotator (`@feeder` `min_cycle` param); a physical recovery time of the delivery device, not session temporal structure
- Session day number → session metadata, not a time structure
- Hardware response latency → apparatus-annotator

**References:**
- Fleshler, M., & Hoffman, H. S. (1962). A progression for generating variable-interval schedules. *JEAB*, *5*(4), 529-530. https://doi.org/10.1901/jeab.1962.5-529

---

### 3. procedure-annotator/context — What Is the Environmental Context?

Declares the **environmental context** in which a phase or schedule operates. Essential for renewal (ABA/ABC/AAB) designs and contextual control studies.

| Keyword | Purpose | Example |
|---------|---------|---------|
| `@context` | Environmental context identifier | `@context("A")`, `@context("B", cues="black-white-stripes+peppermint")` |

**Example: ABA renewal design (Broomer & Bouton, 2022)**

```
@species("rat") @strain("Wistar")
@reinforcer("food", type="pellet")

phase ResponseTraining:
  sessions = 6
  RI30s
  @context("A")

phase Punishment:
  sessions = 4
  Overlay(RI30s, VI90s)
  @context("B")

phase RenewalTest:
  sessions = 1
  EXT
  @context("A")
  @session_end(rule="time", time=10min)
```

**What this enables:**
- Explicitly encode the context manipulation that is central to renewal paradigms
- Compile to: *"Response training was conducted in Context A. Punishment was conducted in Context B. The renewal test was conducted in Context A."*

**Example: no_schedule phase with context exposure**

```
phase MagazineTraining:
  sessions = 1
  no_schedule
  @context("A")
  @context("B")
```

A `no_schedule` phase has no operant contingency (e.g., response-independent food delivery, Pavlovian revaluation, habituation). The `@context` annotations describe where the procedure takes place.

**What does NOT belong here:**
- Physical specifications of the context (chamber dimensions, floor material) → apparatus-annotator
- Stimulus features presented during the context → procedure-annotator/stimulus (`@sd`)

**Reference:**
- Bouton, M. E. (2002). Context, ambiguity, and unlearning: Sources of relapse after behavioral extinction. *Biological Psychiatry*, *52*(10), 976-986. https://doi.org/10.1016/S0006-3223(02)01546-9

---

### 4. subjects-annotator — Who Is the Subject?

Declares **biological conditions and motivating operations (MOs)** of the experimental subject.

| Keyword | Purpose | Example |
|---------|---------|---------|
| `@species` | Species declaration | `@species("rat")` |
| `@strain` | Strain/breed | `@strain("Long-Evans")` |
| `@deprivation` | Establishing operation | `@deprivation(hours=22, target="food")` |
| `@history` | Prior experimental experience | `@history("naive")` |
| `@n` | Number of subjects | `@n(6)` |

**Example: Standard rat operant experiment**

```
FR 5
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
In behavior analysis terminology, food deprivation is an establishing operation that increases the reinforcing efficacy of food and evokes food-seeking behavior (Michael, 1982). The annotation captures this motivating operation (MO; Laraway et al., 2003) as a procedural declaration, not an internal state attribution.

**What does NOT belong here:**
- Internal state attributions ("anxiety level", "motivation") → mentalist terms; use `@deprivation` or `@history` instead
- Response topography ("pressed with left paw") → behavioral data, not a declaration
- Group assignment / counterbalancing → experimental design metadata

---

### 5. apparatus-annotator — What Equipment Is Used?

Declares the **physical equipment** used to run the experiment.

| Keyword | Purpose | Example |
|---------|---------|---------|
| `@chamber` | Experimental chamber model | `@chamber("med-associates", model="ENV-007")` |
| `@interface` | Hardware interface | `@interface("serial", port="/dev/ttyUSB0")` |
| `@hardware` | Physical hardware backend | `@hardware("teensy41")` — omit for simulation |
| `@feeder` | Reinforcer delivery device specs | `@feeder("pellet_dispenser", min_cycle=0.5)` |

**Example: Physical experiment setup**

```
Conc(VI 30-s, VI 60-s, COD=2-s)
  @chamber("med-associates", model="ENV-007")
  @hardware("teensy41")
  @interface("serial", port="/dev/ttyACM0", baud=115200)
```

`@hw` is an abbreviation alias for `@hardware` — both produce the same AST node. See [annotation-design.md §3.5](../../spec/en/annotation-design.md).

**What this enables:**
- Target selection for experiment-io / contingency-bench
- Compile to: *"Sessions were conducted in Med Associates (ENV-007) operant chambers interfaced with a Teensy 4.1 microcontroller via serial connection."*
- Omitting `@hardware` means simulation mode (virtual by default)

**`@feeder` design rationale:** Minimum inter-reinforcement interval (IRI) originates from the physical recovery time of the reinforcer delivery mechanism (pellet dispenser motor cycle, liquid dipper raise/lower time). The same schedule (`VR 3`) has different min_cycle values depending on whether a pellet dispenser (0.5 s) or liquid dipper (3 s) is used. This is an apparatus constraint, not a contingency or session-temporal parameter.

**What does NOT belong here:**
- Logical names for response devices ("left_lever") → apparatus-annotator (`@operandum`)
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
@hardware("teensy41")
@feeder("pellet_dispenser", min_cycle=0.5)

-- Measurement (program-level)
@session_end(rule="first", time=60min, reinforcers=60)
@baseline(pre_training_sessions=3)
@steady_state(window_sessions=5, max_change_pct=10)
@dependent_measure(variables=["rate", "irt", "prf_pause", "running_rate", "changeover_rate"])
@microstructure(burst_threshold=2s, prf_pause_method="latency_to_first", report=["irt_distribution", "bout_statistics", "prf_pause"])
@phase_end(rule="all", min_sessions=20, stability="steady_state", cv_threshold=0.15)
@logging(events=["response", "reinforcer"], precision="ms")
@iri_window(bin_width=5s, report=["distribution", "cv"])
@warmup_exclude(duration=5min)

-- Session parameters (program-level)
@clock(unit="s")
@algorithm("fleshler-hoffman", n=12, seed=42)
@warmup(duration=300)
@iti(duration=10)
@post_blackout(duration=2)
@reinforcer("sucrose", concentration="10%", access_duration=3)

-- Schedule parameters
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
   - Copy `spec/en/annotation-template.md`
   - Answer the boundary test questions (see [annotation-design.md](../../spec/en/annotation-design.md) §2)
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
as an annotation (though core changes are restricted by design-philosophy §8).

---

## References

- Fleshler, M., & Hoffman, H. S. (1962). A progression for generating variable-interval schedules. *JEAB*, *5*(4), 529-530. https://doi.org/10.1901/jeab.1962.5-529
- Kelleher, R. T. (1966). Conditioned reinforcement in second-order schedules. *JEAB*, *9*, 475. https://doi.org/10.1901/jeab.1966.9-475
- Michael, J. (1982). Distinguishing between discriminative and motivational functions of stimuli. *JABA*, *15*(1), 149-155. https://doi.org/10.1901/jaba.1982.15-149
