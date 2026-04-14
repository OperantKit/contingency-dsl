# contingency-dsl Design Rationale

> **Status:** Informative (2026-04-14)
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

## Relationship to Other Documents

- [design-philosophy.md](design-philosophy.md) — Canonical design intent (superordinate)
- [evaluation-criteria.md](evaluation-criteria.md) — Axis definitions used in §3
- [architecture.md](architecture.md) — Structural overview of the current design
