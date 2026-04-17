# Context in the Experiment Layer

> Part of the contingency-dsl experiment layer. Elaborates context as a phase-level construct: temporal, spatial, and stimulus contexts are named and attached to phases so that renewal, reinstatement, and context-driven respondent procedures can be expressed in the companion package `contingency-respondent-dsl`. The foundations-level definition of context lives in `foundations/context.md`; this file specifies the experiment-layer syntax.

**Companion documents:**
- [Foundations / Context](../foundations/context.md) — paradigm-neutral context typing (temporal, spatial, stimulus).
- [Experiment / Phase Sequence](phase-sequence.md) — the phase-level construct that attaches context.
- [Experiment / Paper](paper.md) — Experiment and Paper wrappers that host context-bearing bodies.
- [Respondent Theory](../respondent/theory.md) — why context matters for extinction and renewal.

---

## 1. Why Context Is First-Class

Bouton (2004) reviews the evidence that contexts modulate the retrieval of learned associations rather than participating as elements in the associations themselves. When a CS–US pairing is extinguished in one context and tested in a different context, the CR renews (renewal effect). A CS–US contingency learned under one set of ambient conditions behaves differently when those conditions change.

For the DSL to express renewal, reinstatement, spontaneous-recovery, and context-driven preparations, it must be able to:

1. **Name** a context (e.g., `A`, `B`, or descriptive names like `room_a`, `dark_chamber`).
2. **Attach** a context to a phase so that the phase is performed "in" that context.
3. **Compare** contexts across phases so that criteria and annotations can reference context changes.

The companion package `contingency-respondent-dsl` uses this substrate to express the Tier B renewal procedures (ABA, ABC, AAB) and reinstatement. The contingency-dsl experiment layer does not itself enumerate those procedures; it provides the phase-level syntax.

## 2. Context as a Phase Property

A phase may specify its context via a `@context` annotation or via a dedicated `context` field, depending on the program's chosen encoding. Both forms are admitted:

**Annotation form** (canonical):
```
Phase(
  label = "Acquisition",
  schedule = Pair.ForwardDelay(tone, shock, isi=10-s, cs_duration=15-s),
  phase_annotations = [@context(name="A", location="room_a")],
  criterion = FixedSessions(count=5)
)
```

**Field form** (structural):
```
Phase(
  label = "Acquisition",
  schedule = Pair.ForwardDelay(tone, shock, isi=10-s, cs_duration=15-s),
  context = ContextA,
  criterion = FixedSessions(count=5)
)
```

The annotation form is recommended because it participates in the JEAB annotation inheritance rules of `phase-sequence.md §2.1`: a `@context` declared at `shared_annotations` level is inherited by every phase unless overridden. The field form is provided for programs that prefer a structural representation in the AST; the two forms are semantically equivalent.

## 3. Context-Category Coordinates

Per `foundations/context.md §2`, a context has three coordinates:

| Category | Attached annotation coordinate | Example |
|---|---|---|
| Temporal | `time=` (time of day, session interval) | `@context(time="morning")` |
| Spatial | `location=` (chamber, room identifier) | `@context(location="room_a")` |
| Stimulus | `cue=` (ambient tone, house light, scent) | `@context(cue="house_light_off")` |

Two contexts are different if any coordinate differs. A program decides whether to interpret a mismatch as a renewal-eligible context change or as a noise-level difference; the DSL declares only the coordinates, not the interpretation.

## 4. The `@context` Annotation and `@iti` / `@cs` / `@us`

`@context` coexists with the respondent-annotator annotations (`@cs`, `@us`, `@iti`, `@cs_interval`) defined in `annotations/extensions/respondent-annotator.md`. The role separation:

- `@context` — the ambient conditions under which the phase is performed.
- `@cs`, `@us` — the CS and US metadata themselves (not the context).
- `@iti` — the intertrial-interval metadata including jitter.

All attach at the phase level (or higher) and are inherited through the shared / per-phase mechanism.

## 5. Design Scope: What This File Does Not Define

This file defines the **substrate** for context-driven procedures; it does not enumerate the procedures themselves. Specifically:

- **ABA / ABC / AAB renewal** — Tier B, defined in `contingency-respondent-dsl` using this substrate.
- **Reinstatement** — Tier B, defined in `contingency-respondent-dsl`.
- **Spontaneous recovery** — Tier B (although related to retention intervals more than context changes), defined in `contingency-respondent-dsl`.
- **Contextual fear conditioning** — Tier B, defined in `contingency-respondent-dsl`.

The substrate provided here is the minimum necessary for those extensions to describe their procedures in the DSL without modifying the grammar.

## 6. Example — A Two-Context Acquisition / Extinction Design

```
PhaseSequence(
  shared_annotations = [
    @subjects(species="rat", n=8),
    @apparatus(chamber="chamber_1")
  ],
  phases = [
    Phase(
      label = "Acquisition",
      schedule = Pair.ForwardDelay(tone, shock, isi=10-s, cs_duration=15-s),
      phase_annotations = [@context(name="A", location="room_a")],
      criterion = FixedSessions(count=5)
    ),
    Phase(
      label = "Extinction",
      schedule = Extinction(tone),
      phase_annotations = [@context(name="B", location="room_b")],
      criterion = FixedSessions(count=5)
    ),
    Phase(
      label = "Test",
      schedule = CSOnly(tone, trials=8),
      phase_annotations = [@context(name="A", location="room_a")]      -- back to A
    )
  ]
)
```

This encodes an acquisition / extinction / test arrangement across two contexts — the contingency-dsl-level substrate that `contingency-respondent-dsl` elaborates into the ABA-renewal procedure with its full diagnostic semantics.

## References

- Bouton, M. E. (2004). Context and behavioral processes in extinction. *Learning & Memory*, 11(5), 485–494. https://doi.org/10.1101/lm.78804
- Bouton, M. E., & Bolles, R. C. (1979). Contextual control of the extinction of conditioned fear. *Learning and Motivation*, 10(4), 445–466. https://doi.org/10.1016/0023-9690(79)90057-2
