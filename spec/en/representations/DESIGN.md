# contingency-dsl Representations — Design Document

## Status: Draft

---

## 1. Policy: Representations as Alternative Coordinate Systems

A representation is an alternative coordinate system that describes the **same
behavioral space** as the 3×3 lattice (Distribution × Domain) under a different
parameterization.

### Distinction from annotations/

| Property | annotation | representation |
|------|------------|----------------|
| **Core function** | Adds information | Changes the form of expression |
| **Core semantics** | Unchanged (orthogonal metadata) | Changed (coordinate transformation) |
| **Example** | `@reinforcer("pellet")` | `TTau(T=60, tau=30)` |
| **Boundary test §2** | "Not needed to discuss the FI scallop" | "Rewrite FI in T-tau" |
| **When omitted** | Information is reduced | Coordinate system reverts to default (lattice) |

An annotation **adds** information to `FI 10`. A representation **rewrites**
`FI 10` as `TTau(T=10, τ=10)`. The latter changes the evaluation semantics,
which violates the annotation boundary test (DESIGN.md §2 question #2).
Therefore representations belong to a design space independent from annotations/.

### Motivation

1. **Theoretical completeness** — Behavior analysis admits multiple description
   systems for the same phenomena, including Schoenfeld & Cole's (1972) T-tau
   and Catania's response-rate × reinforcement-rate space. Formally connecting
   these in the DSL strengthens its completeness as a theoretical tool.
2. **Cross-literature search** — Procedures expressed in T-tau can be converted
   to the lattice form, enabling procedural similarity comparison with past
   experiments classified under Ferster & Skinner.
3. **Language independence** — Conversion rules are defined at the DSL level
   and can be implemented equivalently in any backend (Python / Rust / Kotlin).

---

## 2. Boundary Principles for Coordinate System Extensions

### Principle: A representation is an alternative parameterization with bidirectional conversion to the lattice

Conditions a representation `R` must satisfy:

| # | Condition | Rationale |
|---|------|------|
| 1 | `R` describes a subset of the **same behavioral space** as the lattice | Unrelated systems are not representations |
| 2 | The lattice → R conversion rule is **formally defined** | Ambiguous correspondences preclude conversion tests |
| 3 | The R → lattice inverse conversion rule is defined (may be partial) | Without bidirectionality the system is a projection, not a coordinate system |
| 4 | Conversion **preserves information, or makes its loss explicit if not** | Implicit information loss is theoretically unsound |
| 5 | The conversion domain (the convertible Domain) is **type-level constrained** | Invalid conversions are excluded at compile time |

### Permitting Partial Mapping

A representation need not cover all 9 cells of the 3×3 lattice. T-tau is
time-based, so Ratio (response-count-based) lies outside its domain. This is
not a defect; it is the honest boundary of the system.

When the conversion function receives an input outside its domain, it rejects
it as a **type error**. Implicit approximate conversions are not performed
(approximations are provided explicitly in a separated layer).

---

## 3. Classification of Information Loss

Information that may be lost in lattice → representation conversion is
classified as follows.

| Loss Category | Example | Treatment |
|---|---|---|
| **Outside the domain** | Ratio → T-tau | Type error (reject the conversion) |
| **Dimensional collapse** | FI ↔ FT collapse to the same T-tau form | Make `domain` argument mandatory in the inverse conversion |
| **Distribution information collapse** | Variable and Random are indistinguishable in T-tau | Make `distribution` argument mandatory in the inverse conversion |
| **Reversible** | FI(30) → TTau(T=30, τ=30) → FI(30) | No information loss |

---

## 4. Approximate Conversion Layer

Rather than completely prohibiting outside-domain conversions (e.g.,
FR → T-tau), an **approximate conversion that explicitly declares its
assumptions** is provided as a separated layer.

```python
# Type error (core conversion)
to_ttau(FR(5))  # → RatioScheduleError

# Approximate conversion (separated layer — assumption is encoded in the type)
approximate_ttau(FR(5), irt=2.0)
# → TTauApprox(T=10, tau=10, assumption=IRTAssumption(irt=2.0))
```

The result of an approximate conversion is the `TTauApprox` type, which is
distinct from `TTauParams`. As a result:
- The fact that IRT (inter-response time) is a **dependent variable** and not
  part of the schedule definition is made type-explicit.
- Code that conflates approximate results with exact conversion results is
  detected at compile time.

---

## 5. Annotation Preservation Law (Functor Law)

### Principle: Representation conversion preserves annotations

A representation is a coordinate transformation; an annotation is orthogonal
metadata (§1). Therefore, for every representation conversion `T: Lattice → R`,
**annotations are preserved across the conversion** — this is taken as an axiom.

### Formal definition

For any representation conversion `forward` / `backward`, the following two
invariants (functor laws) must hold:

```
Law 1 (Annotation Preservation):
  forward(S).annotations == S.annotations
  backward(R).annotations == R.annotations

Law 2 (Roundtrip Identity — strengthening of §2 condition 4):
  backward(forward(S), disambig).annotations == S.annotations
```

Here `S` is an annotated schedule expression, `R` is an annotated
representation, and `disambig` is the disambiguation parameter required for
the inverse conversion.

### Rationale

1. **Annotations do not change core semantics** (annotations/design.md §2).
   Coordinate conversions also do not change core semantics (§1). The two are
   orthogonal information layers, and operations on one must not affect the
   other.
2. The information-preservation requirement (§2 condition 4) speaks of the
   conversion's core parameters; annotations are "added information" with no
   legitimate reason to be discarded by a coordinate conversion.
3. If a future representation such as a response-rate × reinforcement-rate
   space is added, then without this preservation law the behavior of
   annotations would be undefined per representation, and the consistency of
   the specification would collapse.

### Two-layer metadata model

Metadata involved in representation conversion is separated into two layers.

```
┌─────────────────────────────────────────────┐
│  Layer 0: Source Annotations                 │  Functor Law guarantees preservation
│  @reinforcer("pellet"), @clock(unit="s")     │  Common across all representations
└─────────────────────────────────────────────┘
┌─────────────────────────────────────────────┐
│  Layer 1: Representation Metadata            │  Each representation defines freely
│  TTauApprox.assumption = IRT(2.0)            │  Type-separated from the annotation set
│  (future) RateSpace.fitting_method = ...     │  Discarded on inverse conversion
└─────────────────────────────────────────────┘
```

**Layer 0 (Source Annotations)** is metadata originating in the DSL source
expression. By the Functor Law above, it is preserved across all representation
conversions. It is the invariant information layer shared by the conversion's
input and output.

**Layer 1 (Representation Metadata)** is metadata generated during the
conversion process and specific to a particular representation. It is not
mixed into the annotation set; it is expressed as a structural field of the
result type.

#### Requirements for Representation Metadata

Each representation may declare its own typed fields for metadata generated
during conversion, subject to the following:

| # | Requirement | Rationale |
|---|------|------|
| M1 | The metadata field is closed within the representation's result type | Guarantees separation from the annotation set |
| M2 | The metadata is discarded on inverse conversion (backward) | The recovered schedule expression must not retain representation-specific information |
| M3 | When adding a new representation, submit the metadata schema as `representations/<name>/metadata.schema.json` | Enables mechanical verification |
| M4 | The type of the metadata field must be expressible in JSON Schema | Maintains language independence (the primary goal of §1) |

#### Scope of program-level annotations

Program-level annotations (such as `@species("rat")`) are outside the domain
of schedule-unit representation conversion and are not included in the
conversion's input or output. Annotations attached to a layer of the program
AST above the schedule node do not participate in schedule-unit coordinate
conversion and remain in their original layer.

#### Concrete examples

Preservation of source annotations (Layer 0):

```
input:    FI 10 @reinforcer("pellet") @clock(unit="s")
                ↓ to_ttau
output:   TTau(T=10, tau=10) @reinforcer("pellet") @clock(unit="s")
                ↓ from_ttau(domain="I", distribution="F")
recovered: FI 10 @reinforcer("pellet") @clock(unit="s")
```

Two-layer separation in approximate conversion (Layer 0 + Layer 1):

```
input:    FR 5 @reinforcer("pellet")
                ↓ approximate_ttau(irt=2.0)
output:   TTauApprox(T=10, tau=10, assumption=IRTAssumption(irt=2.0))
            @reinforcer("pellet")
        ↑ Layer 0: annotation preserved
        ↑ Layer 1: assumption is a structural field of TTauApprox
                ↓ from_ttau(domain="R", distribution="F")
recovered: FR 5 @reinforcer("pellet")
        ↑ Layer 0: annotation preserved
        ↑ Layer 1: assumption discarded (requirement M2)
```

Example for a future representation addition:

```
representations/rate-space/
├── README.md
├── metadata.schema.json        ← requirement M3: declares fitting_method etc.
└── conformance/
    ├── to_rate_space.json
    ├── from_rate_space.json
    ├── roundtrip.json
    ├── errors.json
    └── annotation_preservation.json
```

### Verification method

The annotation preservation law is verified by conformance tests:

- `conformance/representations/t-tau/annotation_preservation.json`
  — forward / backward / roundtrip tests for annotated schedules.

When a new representation is added (§7 review mechanism), submission of an
annotation-preservation conformance test is included in the mechanical
verification requirements.

---

## 6. Directory Structure

```
representations/
├── DESIGN.md               # this file — design principles for coordinate system extensions
└── t-tau/
    ├── README.md            # Formal definition and conversion rules of T-tau
    ├── metadata.schema.json # JSON Schema for Representation Metadata (§5 requirement M3)
    └── conformance/         # Conversion tests (JSON)
        ├── to_ttau.json                # Lattice → T-tau
        ├── from_ttau.json              # T-tau → Lattice
        ├── roundtrip.json              # Roundtrip verification
        ├── errors.json                 # Tests for outside-domain inputs and type errors
        └── annotation_preservation.json # Annotation preservation law tests (§5)
```

To add another coordinate system in the future (e.g., a response-rate ×
reinforcement-rate space), add it under `representations/<name>/` with the
same structure. The `metadata.schema.json` must be submitted even when the
representation has no representation-specific metadata, supplied as an empty
schema (`{}`) to guarantee its existence.

---

## 7. Review Mechanism

> **Note:** When adding a new representation, include submission of the
> annotation-preservation conformance test in the mechanical verification
> requirements (see §5).

Adding a new representation requires the following review:

| Layer | Content |
|-------|------|
| 1. Mechanical verification | Formal definition of conversion rules, presence of conformance test JSON, annotation preservation tests (§5), metadata.schema.json (§5 requirement M3) |
| 2. Theoretical verification | Identity of the behavioral space, explicit information loss, validity of partial mapping |
| 3. Domain expert review | Foundational theory (basic learning theorist), quantitative validity (quantitative choice theorist) |
