# contingency-dsl Evaluation Criteria

> **Status:** Normative (2026-04-14)
>
> This document defines the axes by which design decisions in contingency-dsl
> are evaluated. It is subordinate to [design-philosophy.md](design-philosophy.md)
> and derives its axes from the design intent stated there.

---

## 1. Purpose

Design reviews, spec audits, and extension proposals require a shared
definition of "good." Without explicit criteria, reviewers fall back on
implicit preferences and evaluations become non-reproducible.

This document fixes the evaluation axes so that:

- Any reviewer (human or automated) can assess a proposal against the
  same dimensions.
- Trade-offs between axes are made visible and deliberate.
- The axes themselves can be revised through the same process as other
  specs (versioned, with rationale).

## 2. Evaluation Axes

Six axes are adopted. Each axis is grounded in a specific section of
[design-philosophy.md](design-philosophy.md).

| # | Axis | Definition | design-philosophy grounding | Current claim |
|---|---|---|---|---|
| 1 | **Formal soundness** | Determinism of the grammar; well-definedness of types and semantics | §2 (non-TC Core, CFG, decidability) | non-TC; LL(1)/LL(2) decidable |
| 2 | **Language independence** | A single spec can drive multiple implementations without language-specific assumptions | §6 (Python/Rust parallel implementation) | Dual-language strategy; meta-DSL planned |
| 3 | **Incremental extensibility** | Adding a new dimension does not break existing constructs or programs | §2 (five-layer architecture), §4 (program-scoped Annotation), §5 (Schedule Extension) | Annotator plugin + Tier + Schedule Extension |
| 4 | **Educational minimality** | The simplest valid program is a single token; complexity is opt-in | §3.1 (Core as shared notation for all users) | `FR 5` is a complete program in parse/dev mode |
| 5 | **Research rigor** | Real-apparatus and publication requirements are not lost or silently omitted | §1 (supreme objective), §7.1 (near-term goals) | production / publication validation modes |
| 6 | **Conceptual boundary clarity** | Annotation, schedule variant, and coordinate change are distinguished by principled criteria, not ad hoc convention | §4.3 (category-neutral equivalence), §5.4 (Annotation vs. Extension boundary) | Boundary tests + §5.4 decision matrix |

## 3. How to Use These Axes

### 3.1 Design Reviews

When reviewing a spec change or extension proposal, evaluate its impact
on each axis. A proposal that improves one axis at the cost of another
must make the trade-off explicit.

### 3.2 Boundary Decisions

When deciding whether a new concept belongs in Core, Core-Stateful,
Schedule Extension, or Annotation, check which placement scores highest
across the six axes. In particular:

- Axes 1 and 6 constrain **where** a concept belongs (layer assignment).
- Axes 3 and 4 constrain **how** it is exposed (API surface).
- Axes 2 and 5 constrain **what** it must support (implementation scope).

### 3.3 Automated Audits

Spec auditors (e.g., adversarial-spec-auditor) should reference these
axes when scoring proposals. Each axis maps to specific, testable
properties:

| Axis | Testable properties |
|---|---|
| Formal soundness | Grammar determinism proof; type-system consistency; absence of ambiguous productions |
| Language independence | No host-language type leakage in spec; AST schema is self-contained JSON |
| Incremental extensibility | Adding/removing an annotation module does not require Core grammar changes |
| Educational minimality | Shortest valid program length; number of concepts required to parse the simplest example |
| Research rigor | Coverage of JEAB Method section categories; validation mode completeness |
| Conceptual boundary clarity | Each construct passes the §5.4 decision matrix unambiguously |

## 4. Non-Goals

- These axes do not define a **scoring formula** or weighted index.
  They are dimensions of analysis, not a grading rubric.
- These axes do not prescribe **implementation priorities**. Priority
  is governed by [design-philosophy.md §7](design-philosophy.md).
- These axes are **not exhaustive**. A proposal may introduce concerns
  (e.g., performance, ergonomics) outside these axes; such concerns
  should be evaluated on their own terms and, if recurring, proposed
  as additions to this document.

---

## Relationship to Other Documents

This document is subordinate to [design-philosophy.md](design-philosophy.md).
If an axis defined here contradicts design-philosophy, design-philosophy
takes precedence and this document should be revised.

This document is referenced by:

- Spec reviewers and auditors as the shared evaluation framework.
- Extension proposals as the dimensions against which trade-offs are argued.
