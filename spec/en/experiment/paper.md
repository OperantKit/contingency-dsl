# Paper and Experiment — Multi-Experiment Publications

> Part of the contingency-dsl experiment layer. Defines the `Experiment` wrapper (label + body) and the `Paper` wrapper (one or more Experiments as they appear in a single publication). This file is the human-facing specification; the corresponding JSON Schema is `schema/experiment/experiment.schema.json`.

**Companion documents:**
- [Experiment / Phase Sequence](phase-sequence.md) — multi-phase body for a single experiment.
- [Experiment / Context](context.md) — first-class Context within an experiment body.
- [Experiment / Criteria](criteria.md) — phase-change criteria used inside PhaseSequence bodies.
- [Operant Grammar](../operant/grammar.md) — operant productions that appear in an Experiment body.

---

## 1. Rationale

A typical JEAB publication is not a single procedure. Catania & Reynolds (1968) reports six experiments; Mazur (2005) reports four; Blough (1972) reports four. Each experiment has its own Subjects section, its own Apparatus section, and its own Procedure. Annotations that describe one experiment do not generalize to the next. The experiment layer therefore elevates the publication's internal boundary — "Experiment 1", "Experiment 2", and so on — to a first-class construct, so that a program can represent the full content of a paper rather than an arbitrary slice of it.

A `Paper` is an ordered sequence of `Experiment` nodes. Each `Experiment` wraps a single design (a `Program` for single-schedule experiments, a `PhaseSequence` for multi-phase experiments) under a human-readable label. Annotations do not cross Experiment boundaries; a paper-wide subject description is not part of the grammar and must be expressed by repeating the relevant annotations inside each Experiment.

## 2. The `Experiment` Construct

```
Experiment(
  label = <string>,
  body  = <Program> | <PhaseSequence>
)
```

`label` is the human-readable experiment identifier as it appears in the source publication: "Experiment 1", "Experiment 2a", "Study 3", and so on. The label is metadata for the reader; it does not participate in the grammar's static verification.

`body` is either a `Program` (a single-schedule design; see `foundations/grammar.md §2`) or a `PhaseSequence` (a multi-phase design; see `phase-sequence.md`). The choice depends on whether the experiment's Procedure section describes one schedule or multiple phases with transition criteria. The body inherits none of its annotations from the enclosing Paper — every annotation the experiment relies on (Subjects, Apparatus, Procedure, Measurement) must appear inside the body itself.

## 3. The `Paper` Construct

```
Paper(
  experiments = [Experiment1, Experiment2, ..., ExperimentN]
)
```

A `Paper` has at least one Experiment. A publication with a single experiment may be represented either as a bare `Program` / `PhaseSequence` or as a `Paper` with one Experiment — the two forms are equivalent in content but differ in framing. Tools that report experiment labels or iterate over experiments prefer the `Paper` form; tools that execute a single procedure prefer the bare form.

`experiments` is ordered. The order reflects the publication's internal order ("Experiment 1" precedes "Experiment 2"), not any execution ordering. The grammar does not require experiments to be conducted in label order, nor does it require labels to be numerically contiguous — a paper that skips from "Experiment 1" to "Experiment 3" is well-formed at this layer (semantic linters may flag such gaps as warnings).

## 4. Shared Annotations and Per-Experiment Overrides

A Paper may carry `shared_annotations` that are inherited by every experiment, and each Experiment body may carry its own annotations that override the shared ones by keyword. The inheritance rule is symmetric with `PhaseSequence.shared_annotations` vs per-Phase annotations:

- A paper-level `@subjects(species="pigeon")` is inherited by every experiment that does not itself declare `@subjects(...)`.
- An experiment that declares its own `@subjects(...)` uses its own value; the paper-level default is unused for that experiment only.
- An experiment that adds an annotation keyword not present at paper level simply adds it for itself.

This mirrors the JEAB convention: when every experiment in a paper uses the same subjects and the same apparatus, the Method section often hoists those descriptions to a "General Method" preamble. When one experiment deviates (different pigeons, different chamber), its Method section redeclares only the differing field. The DSL expresses the same pattern: shared annotations at the Paper level express what is common; per-Experiment annotations express what differs.

When nothing is common across experiments, `Paper.shared_annotations` is empty and each Experiment body declares its own annotations independently. The `PhaseSequence` construct continues to handle shared annotations *within* a single experiment; the `Paper` construct extends that pattern *across* experiments.

## 5. Relationship to Other Layers

`Paper` and `Experiment` are purely experiment-layer wrappers. They do not introduce new operant, respondent, or composed procedures. An `Experiment.body` is resolved by the operant, respondent, and composed layers; only the multi-phase coordination (via `PhaseSequence`) and the multi-experiment coordination (via `Paper`) live at the experiment layer.

Downstream tools that accept `Paper` inputs typically iterate over `experiments`, unwrap each `Experiment.body`, and dispatch to the appropriate layer-specific compiler. Tools that accept only a single procedure unwrap the first Experiment or require an explicit Experiment selector.

## 6. Relationship to the Existing Schema

The authoritative machine-readable form of this specification lives in `schema/experiment/experiment.schema.json`. That schema defines the exact JSON shapes for `Experiment` and `Paper`, including constraint details (`Paper.experiments` minimum item count, `Experiment.body` one-of dispatch between Program and PhaseSequence). The present file is the human-facing prose counterpart and is authoritative for the conceptual design; the schema is authoritative for the exact serialized form.

## 7. DSL Surface Syntax

The grammar (`schema/operant/grammar.ebnf`) defines three top-level file forms:

```
file            ::= paper | experiment_body | program
paper           ::= program_annotation* experiment_decl+
experiment_decl ::= "experiment" experiment_label ":" experiment_body
experiment_body ::= program_annotation* (phase_decl | progressive_decl | shaping_decl)+
```

An `experiment_label` is either an upper-ident (`Experiment1`) or a digit-ident (`1`, `2a`, `3_pilot`), matching the JEAB convention of numbering experiments as "Experiment 1", "Experiment 2a", and so on. Phase labels accept the same two ident forms.

### 7.1 Single Experiment, Single Schedule (`program` form)

```
@subjects(species="pigeon", n=4)
@apparatus(chamber="operant_chamber_A")

VI 30-s
```

### 7.2 Single Experiment, Multiple Phases (`experiment_body` form)

```
@subjects(species="rat", n=8)
@apparatus(chamber="operant_chamber_1")

phase Baseline:
  sessions >= 20
  stable(cv, threshold=10%, window=5)
  VI 60-s

phase Reversal_1:
  stable(cv, threshold=10%, window=5)
  VI 120-s

phase Reversal_2:
  VI 60-s
```

### 7.3 Multiple Experiments in One Paper (`paper` form)

Paper-level annotations apply to every experiment; per-experiment annotations override paper-level values for that experiment only.

```
@subjects(species="pigeon", n=4)
@apparatus(chamber="chamber_A")

experiment 1:
  VI 30-s

experiment 2:
  phase Baseline:
    stable(cv, threshold=10%, window=5)
    VI 60-s

  phase Extinction:
    sessions = 5
    EXT

  phase Recovery:
    VI 60-s
```

Both experiments inherit `@subjects(species="pigeon", n=4)` and `@apparatus(chamber="chamber_A")` from the paper level. Experiment 1 uses a single-schedule body; Experiment 2 uses a three-phase body. The paper-level annotations are written once, not repeated in each experiment.

### 7.4 Per-Experiment Override

When experiments differ in subjects or apparatus, the differing experiment redeclares the annotation. Other experiments continue to use the paper-level default.

```
@subjects(species="pigeon", n=4)

experiment 1:
  @apparatus(chamber="chamber_A")
  VI 30-s

experiment 2a:
  @subjects(species="pigeon", n=6)    -- overrides paper-level n=4
  @apparatus(chamber="chamber_B")
  VI 60-s

experiment 2b:
  @apparatus(chamber="chamber_B")     -- inherits paper-level @subjects
  VI 120-s
```

Experiment 2a redeclares `@subjects` because its subject count differs; Experiment 2b inherits the paper-level `@subjects` unchanged. Experiment labels here are `"1"`, `"2a"`, `"2b"` — digit-starting labels permitted by `digit_ident`.

### 7.5 Single-Experiment Paper (wrapper omission)

A paper with exactly one experiment is semantically equivalent to the bare `experiment_body` form. The wrapper may be omitted. These two files parse to equivalent ASTs (the first as a bare Program, the second as a Paper with one Experiment whose body is that Program):

```
-- bare form (program)
@subjects(species="rat", n=8)

VI 60-s
```

```
-- wrapped form (paper with one experiment)
@subjects(species="rat", n=8)

experiment 1:
  VI 60-s
```

Tools that report experiment labels prefer the wrapped form; tools that execute a single procedure accept either.

## References

- Catania, A. C., & Reynolds, G. S. (1968). A quantitative analysis of the responding maintained by interval schedules of reinforcement. *Journal of the Experimental Analysis of Behavior*, 11(3, Pt.2), 327–383. https://doi.org/10.1901/jeab.1968.11-s327
