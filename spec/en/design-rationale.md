# contingency-dsl Design Rationale

> **Status:** Informative
>
> This document records the alternatives considered for the annotation
> architecture and explains why the current design was chosen. It is
> subordinate to [design-philosophy.md](design-philosophy.md) and uses
> the six axes defined in [evaluation-criteria.md](evaluation-criteria.md).

---

## 1. Purpose

[design-philosophy.md](design-philosophy.md) states *what* the design is
and *why* it matters. [evaluation-criteria.md](evaluation-criteria.md)
defines the axes for evaluation. This document fills the remaining gap:
**what alternatives were considered, and how did they compare?**

Recording rejected alternatives extends the useful life of design
decisions by making their trade-offs explicit, reducing the likelihood
that future contributors re-propose already-evaluated options.

---

## 2. Alternatives Considered

Five alternative architectures were evaluated against the current design
(annotation + tier + representation with program-scoped closure).

### 2.1 Typed Attributes

**Reference:** Rust `#[derive(...)]`, Lean 4 attributes.

Annotations are typed parameters embedded in the grammar. A type checker
validates annotation values at parse time.

- **Strength:** Formal soundness is maximized; invalid annotations are
  caught statically.
- **Weakness:** Every annotation type must be known to the grammar,
  breaking incremental extensibility. Educational minimality suffers
  because the type system becomes a prerequisite for reading annotated
  programs.

### 2.2 Manifest Separation

**Reference:** Kubernetes YAML + Custom Resource Definitions.

The DSL is reduced to pure schedule expressions. All metadata lives in
external manifest files (YAML, JSON) linked by identifier.

- **Strength:** Language independence is maximized; the DSL carries no
  host-language assumptions.
- **Weakness:** The DSL loses self-containedness. A reader must
  cross-reference two files to understand a single procedure, which
  undermines educational minimality and research rigor (implicit
  information is no longer made explicit inline).

### 2.3 Embedded Python DSL

**Reference:** Pydantic model declarations, SQLAlchemy declarative base.

Annotations are Python objects composed directly in Python source.
The DSL is a Python library, not a language-independent notation.

- **Strength:** Implementation cost is minimal; the full Python ecosystem
  is available.
- **Weakness:** Language independence is abandoned by definition. The
  notation cannot serve as a shared vocabulary across Python, Rust, and
  Kotlin implementations.

### 2.4 Macro Expansion

**Reference:** Racket `#lang`, Lean elaboration.

Schedule variants and annotations are expressed as macros that expand
into core constructs. The surface syntax is extensible without grammar
changes.

- **Strength:** Formal soundness and incremental extensibility can both
  be high if the macro system is well-designed.
- **Weakness:** Macro systems are inherently powerful and risk breaching
  the non-Turing-complete boundary of the Core. Educational minimality
  drops because understanding expansion rules becomes necessary.

### 2.5 Effect System

**Reference:** Koka, OCaml 5 effects.

Tiers are modeled as algebraic effects. An annotation's tier is its
effect signature; tier composition follows effect-handler semantics.

- **Strength:** Research rigor benefits from the precision of effect
  typing. Tier interactions are formally tractable.
- **Weakness:** Effect systems require substantial type-theoretic
  background to read, severely limiting educational minimality.
  Implementation cost is high in both Python and Rust.

---

## 3. Comparison

Axes are from [evaluation-criteria.md](evaluation-criteria.md). Ratings
are relative within this comparison (higher is better for the axis).

| Axis | Typed attr | Manifest | Embedded DSL | Macro | Effect sys | **Current** |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| 1. Formal soundness | ★★★★★ | ★★★ | ★★ | ★★★★★ | ★★★★ | ★★★★ |
| 2. Language independence | ★★ | ★★★★★ | ★ | ★★ | ★★ | ★★★ |
| 3. Incremental extensibility | ★★★ | ★★★★ | ★★★ | ★★★★ | ★★★ | ★★★★ |
| 4. Educational minimality | ★★★ | ★★ | ★★★★ | ★★ | ★★ | ★★★★★ |
| 5. Research rigor | ★★★★ | ★★★★ | ★★★ | ★★★★ | ★★★★★ | ★★★★ |
| 6. Boundary clarity | ★★★★ | ★★★★★ | ★★ | ★★★ | ★★★★ | ★★★★ |
| Implementation cost | High | Medium | Low | High | High | Medium |

---

## 4. Why the Current Design

The current design occupies a deliberate middle ground:

1. **Educational minimality (★5) is the strongest axis.** The DSL must
   function as a shared notation readable by students and researchers
   with no programming background (design-philosophy §3.1). This
   immediately disqualifies alternatives that require type-system,
   macro-expansion, or effect-system literacy.

2. **Incremental extensibility (★4) preserves long-term stability.**
   Program-scoped annotation and schedule-extension registries allow
   third parties to extend the DSL without Core grammar changes
   (design-philosophy §4.2, §5). Typed attributes and effect systems
   both couple extensions to the grammar or type system.

3. **Language independence (★3) is structurally guaranteed but not yet
   fully proven.** The meta-DSL (`schema-format.md`) and AST schema
   ensure that the spec is not Python-specific. Full proof requires a
   second-language reference implementation, which is a downstream
   deliverable, not a DSL-spec concern (see design-philosophy §6).

4. **Formal soundness (★4) is sufficient for the intended use.**
   The Core is non-Turing-complete and LL(1)/LL(2) decidable. Full ★5
   (typed attributes, macro systems) would require users to understand
   the verification machinery, conflicting with educational minimality.

5. **Research rigor (★4) is achieved through tier and mode.**
   The tier system (Tier 0-3) and validation modes (parse, dev,
   production, publication) ensure that implicit experimental details
   are surfaced when needed, without burdening casual use.

6. **Boundary clarity (★4) is maintained by principled criteria.**
   The annotation-vs-extension decision matrix (design-philosophy §5.4)
   provides a reproducible test. Manifest separation scores higher on
   this axis but at the cost of self-containedness.

In summary, the current design **maximizes educational minimality while
maintaining sufficient scores on all other axes**. No alternative
achieves this balance; each trades educational accessibility for
strength on a different axis.

---

## 5. Six-Layer Structure Rationale

The six-layer architecture (Foundations / Operant / Respondent /
Composed / Experiment / Annotation) is defined in
[design-philosophy.md §2](design-philosophy.md). This section records
why that structure was chosen over the two alternatives considered.

### 5.1 Alternatives Considered

**Case A (rejected)** — abstract axes at the top-level directory:
`core-paradigm/`, `core-execution/`, `core-composition/`,
`core-cross-paradigm/`. Each top-level directory was named by an
abstract engineering axis (paradigm, execution mode, composition,
cross-paradigm), independent of the scientific categories it covered.

- **Strength:** Formally orthogonal; each axis is a clean dimension of
  variation.
- **Weakness:** The naming is too abstract for the target audience (EAB
  researchers and students). `core-paradigm/` does not communicate that
  this is where operant vs. respondent procedures live; `core-execution/`
  does not communicate that this is where Percentile / Adjusting /
  Interlocking / MTS live. The naming gives operant and respondent
  symmetric weight, which misrepresents the actual coverage target: the
  DSL is aimed primarily at operant procedures reported in JEAB, with
  respondent procedures represented only at the minimum necessary level
  in the main package and depth delegated to a companion package.

**Case B (rejected)** — respondent primitives as annotations only: the
respondent layer is collapsed into an annotation package (`@cs`, `@us`,
`@pair`, `@contingency`, etc.) attached to schedule expressions or to
`no_schedule` phases. No first-class respondent grammar exists.

- **Strength:** Minimal grammar impact; existing Core + annotations
  suffice.
- **Weakness:** The CS-US contingency structure (Pavlov, 1927; Rescorla,
  1967, 1968) is **grammar-level**, not metadata-level. An
  `ExplicitlyUnpaired` or `Contingency(p_us_given_cs, p_us_given_no_cs)`
  procedure defines a structural relationship between stimulus events;
  changing that structure changes what the procedure is, not just how
  it is described. This is the same boundary test that separates
  schedule variants from annotations (design-philosophy §5.5). Case B
  fails the test: it would place grammatically load-bearing constructs
  in a layer whose contract guarantees they do not affect evaluation.

**Case C (chosen)** — scientific-category naming with an extension point
for respondent depth: the top-level directories are named by the
scientific categories they cover (foundations / operant / respondent /
composed / experiment / annotations). The Operant layer carries the
largest volume; the Respondent layer is deliberately minimal (Tier A
only) and exposes an extension point (`ExtensionRespondentPrimitive`)
through which the companion package `contingency-respondent-dsl`
supplies Tier B primitives.

- **Strength:** Directory names are immediately readable to the target
  audience; the operant-vs-respondent split matches how the discipline
  organizes itself (Skinner, 1938; Pavlov, 1927). The Composed layer
  formalizes Rescorla & Solomon's (1967) two-process composition as a
  first-class sibling, not a sub-case.
- **Weakness (accepted):** The directory tree is asymmetric in volume
  (operant is heavy, respondent is thin). This asymmetry is intentional
  and explicitly documented in design-philosophy §2 as an EAB-centric
  weighting.

### 5.2 EAB-Centric Weighting

The six-layer volume distribution reflects the primary coverage target:

- **Operant layer — largest volume.** Six schedule files
  (`operant/schedules/{ratio,interval,time,differential,compound,progressive}.md`)
  plus `operant/stateful/{percentile,adjusting,interlocking}.md` plus
  `operant/trial-based/{mts,go-nogo}.md`. This mirrors the distribution
  of procedures reported in JEAB since Ferster & Skinner (1957).
- **Respondent layer — minimal.** Tier A primitives only; deeper
  Pavlovian procedures (blocking, overshadowing, latent inhibition,
  renewal, reinstatement, etc.) are delegated to
  `contingency-respondent-dsl` through the Respondent extension point.
- **Composed layer — limited initial set, open-ended.** Five initial
  procedures (conditioned suppression, PIT, autoshaping, omission,
  two-process theory); further composed procedures admitted on a
  case-by-case basis per the `composed/` admission criteria.

### 5.3 Scientific Grounding

The layer names and distinctions derive from primary sources:

- Skinner, B. F. (1938). *The behavior of organisms*. Appleton-Century. — operant three-term contingency
- Pavlov, I. P. (1927). *Conditioned reflexes: An investigation of the physiological activity of the cerebral cortex* (G. V. Anrep, Trans.). Oxford University Press. — respondent two-term contingency
- Rescorla, R. A. (1967). Pavlovian conditioning and its proper control procedures. *Psychological Review*, 74(1), 71–80. https://doi.org/10.1037/h0024109 — contingency space
- Rescorla, R. A. (1968). Probability of shock in the presence and absence of CS in fear conditioning. *Journal of Comparative and Physiological Psychology*, 66(1), 1–5. https://doi.org/10.1037/h0025984 — contingency parameterization
- Rescorla, R. A., & Solomon, R. L. (1967). Two-process learning theory: Relationships between Pavlovian conditioning and instrumental learning. *Psychological Review*, 74(3), 151–182. https://doi.org/10.1037/h0024475 — composed-layer justification
- Catania, A. C. (2013). *Learning* (5th ed.). Sloan. — unified treatment of contingency relations across operant and respondent

---

## Relationship to Other Documents

- [design-philosophy.md](design-philosophy.md) — Canonical design intent (superordinate)
- [evaluation-criteria.md](evaluation-criteria.md) — Axis definitions used in §3
- [architecture.md](architecture.md) — Structural overview of the current design
