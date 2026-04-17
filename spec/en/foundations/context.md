# Context — Temporal, Spatial, and Stimulus Contexts as First-Class Objects

> Part of the contingency-dsl foundations layer. Defines context as a foundational construct to support renewal, reinstatement, and context-driven respondent procedures that are anticipated in a later phase and in the `contingency-respondent-dsl` extension package.

---

## 1. What Is a Context?

**Definition 1 (Context).** A context is a set of environmental conditions that remain in effect during a trial, session, or phase but are not themselves the target stimuli of the contingency. The contingency (two-term or three-term) operates *within* the context; the context does not directly produce a CR or Sr+.

Bouton (2004, §2) articulates the modern view: contexts modulate retrieval of learned associations rather than participating as elements in the associations themselves. When a CS–US pairing is extinguished in context B and tested in the original context A, responding renews (ABA renewal). The context's role is disambiguating, not associative.

## 2. Three Context Categories

The DSL recognizes three context categories:

| Category | Examples | Parameterized by |
|---|---|---|
| **Temporal context** | Time of day, session number, elapsed session time | `@context(time=...)`, phase ordering |
| **Spatial context** | Chamber, room, apparatus identifier | `@context(location=...)`, `@apparatus` |
| **Stimulus context** | Ambient tone, house light, olfactory cue | `@context(cue=...)`, background stimuli |

A context is specified by a set of coordinates across one or more categories. Two contexts differ if any coordinate differs.

## 3. Context as First-Class

Context is first-class in two senses:

1. **Foundations-level type.** A context is a named entity in the DSL's type lattice. Expressions can reference context identifiers and annotations can scope to specific contexts.
2. **Experiment-layer construct.** Phases can declare their context; phase-change criteria can reference context changes. See `experiment/context.md` for the concrete phase-level syntax.

This dual positioning — foundational type + experiment-layer construct — is necessary to support procedures that require context to drive behavior, such as Bouton's (2004) renewal designs (ABA / ABC / AAB), reinstatement procedures (Rescorla & Heth, 1975), and occasion-setting preparations (Holland, 1983).

## 4. Context vs Discriminative Stimulus

A context and a discriminative stimulus (SD) are formally distinguishable:

- An **SD** is a stimulus whose presence signals when a specific response will be reinforced. The SD is part of the three-term contingency `(SD, R, SR)`; its control is differential.
- A **context** sets the conditions under which the contingency applies at all. Context control modulates retrieval of the whole contingency rather than differentially selecting a response.

This distinction is operationally subtle — a discriminative stimulus, sustained continuously, can function as a context. The DSL's convention: label a stimulus SD (`@sd`) when it differentially controls response rate within a contingency; label it context (`@context`) when it modulates which contingency is retrieved. Linters may emit advisory warnings when the distinction is unclear, but no hard grammatical constraint enforces it.

## 5. Scope in Current Phase

At the current design checkpoint, the foundations layer fixes only the **type** of context. Concrete grammar for context-dependent respondent procedures (renewal, reinstatement, occasion setting) lives in `contingency-respondent-dsl` (Tier B extension package) and relies on this foundational definition.

The `experiment/context.md` file specifies the phase-level syntax for declaring contexts in multi-phase designs; this is the mechanism by which current DSL programs express ABA, ABC, and AAB structures.

## 6. What This Layer Does **Not** Define

- **Context similarity metrics** (how similar is context B to context A?). Such metrics are behavioral/theoretical, not DSL-level.
- **Automatic context extraction** from apparatus annotations. Contexts must be explicitly declared.
- **Cross-subject context sharing** (one subject's context determining another's). This is a `contingency-core` concern.

## References

- Bouton, M. E. (2004). Context and behavioral processes in extinction. *Learning & Memory*, 11(5), 485–494. https://doi.org/10.1101/lm.78804
- Bouton, M. E., & Bolles, R. C. (1979). Contextual control of the extinction of conditioned fear. *Learning and Motivation*, 10(4), 445–466. https://doi.org/10.1016/0023-9690(79)90057-2
- Holland, P. C. (1983). Occasion-setting in Pavlovian feature positive discriminations. In M. L. Commons, R. J. Herrnstein, & A. R. Wagner (Eds.), *Quantitative analyses of behavior: Discrimination processes* (Vol. 4, pp. 183–206). Ballinger.
- Rescorla, R. A., & Heth, C. D. (1975). Reinstatement of fear to an extinguished conditioned stimulus. *Journal of Experimental Psychology: Animal Behavior Processes*, 1(1), 88–96. https://doi.org/10.1037/0097-7403.1.1.88
