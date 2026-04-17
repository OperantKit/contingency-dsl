# contingency-dsl — Respondent Defaults

Explicit documentation of all implicit defaults and type-discriminator
conventions in the respondent (two-term, CS-US) layer. When a parameter
is omitted, the following values apply.

## Type discriminator convention

Every node in `ast.schema.json` carries a `type` field that serves as the
oneOf discriminator. The discriminator value is the Pascal-case form of
the primitive's source syntax, flattened where necessary to remove
infix punctuation. Specifically:

| Source syntax | AST `type` value | Note |
|---|---|---|
| `Pair.ForwardDelay(cs, us, ...)` | `"PairForwardDelay"` | Flattens the `.` prefix |
| `Pair.ForwardTrace(cs, us, ...)` | `"PairForwardTrace"` | Flattens the `.` prefix |
| `Pair.Simultaneous(cs, us)` | `"PairSimultaneous"` | Flattens the `.` prefix |
| `Pair.Backward(us, cs, ...)` | `"PairBackward"` | Flattens the `.` prefix |
| `Extinction(cs)` | `"Extinction"` | — |
| `CSOnly(cs, trials=n)` | `"CSOnly"` | — |
| `USOnly(us, trials=n)` | `"USOnly"` | — |
| `Contingency(p_cs, p_nocs)` | `"Contingency"` | — |
| `TrulyRandom(cs, us, ...)` | `"TrulyRandom"` | Preserved even though it sugars to `Contingency(p, p)` — intent is recorded in the parse tree |
| `ExplicitlyUnpaired(cs, us, ...)` | `"ExplicitlyUnpaired"` | Preserved even though it sugars to `Contingency(0, p)` |
| `Compound([cs1, cs2])` | `"Compound"` | — |
| `Serial([cs1, cs2], ...)` | `"Serial"` | — |
| `ITI(distribution, mean=...)` | `"ITI"` | — |
| `Differential(cs+, cs-, us)` | `"Differential"` | — |
| `<UpperIdentifier>(...)` | `"ExtensionPrimitive"` | Registry-resolved at Phase 2 |

Implementations MUST produce exactly these discriminator values.
Validation against `ast.schema.json` relies on `const` matches to pick
the correct `oneOf` branch.

## Default values by primitive

### `Compound`

| Parameter | Default | Rationale |
|---|---|---|
| `mode` | `"Simultaneous"` | The only Tier A mode. Additional modes (e.g., asynchronous onset) are deferred to extension primitives in `contingency-respondent-dsl`. |

### `TrulyRandom`

| Parameter | Default | Rationale |
|---|---|---|
| `p` | (unresolved; program-provided) | The primitive sugars to `Contingency(p, p)`, but at the AST level `p` MAY be omitted. Programs that require a numeric value before execution supply it via the respondent-annotator `@iti`/`@us`-layer metadata or via explicit `TrulyRandom(cs, us, p=0.5)` syntax. |

### `ExplicitlyUnpaired`

| Parameter | Default | Rationale |
|---|---|---|
| `min_separation` | (unresolved; optional) | When omitted, the primitive specifies only that US is not paired with CS (equivalent to `Contingency(0, p)` without a separation constraint). Programs that enforce apparatus-side separation supply it explicitly. |

### `PairForwardTrace`

| Parameter | Default | Rationale |
|---|---|---|
| `cs_duration` | (unresolved; optional in AST) | When omitted, the CS window is determined by the program's apparatus configuration. The grammar only requires `trace_interval`, which is the defining temporal parameter of the trace procedure (Ellison, 1964). |

## Extension-primitive registration

The `ExtensionPrimitive` discriminator is the grammar-level escape hatch
for Tier B procedures. Its structural shape is fixed by this schema
(`name`, `positional`, `params`), but the semantic contract — which
`name` values are valid and which parameter combinations are well-formed
— is owned by the registering extension (e.g.,
`contingency-respondent-dsl`). The respondent core performs only
syntactic validation; per-extension validation runs in Phase 2 of the
pipeline (see `schema/foundations/defaults.md`).

Extensions MUST register under a name matching
`^[A-Z][a-zA-Z0-9_]*$` (`UpperIdentifier` in
`schema/foundations/types.schema.json`) and MUST NOT shadow any Tier A
primitive name listed in the discriminator table above. Shadowing is a
registration-time error, not a Phase 2 error: registries with colliding
names fail to load.

## Short-form resolution (Differential)

The short form `Differential(cs_positive, cs_negative)` infers the US
reference from the enclosing phase-level `@us` annotation
(`schema/annotations/extensions/respondent-annotator.schema.json`).
When no enclosing `@us` is available, Phase 2 raises a semantic error
(`DIFFERENTIAL_US_UNRESOLVED`, emitted by the respondent validator;
the operant validator has no analogue). The AST representation uses
the three-argument form after Phase 2 resolution; the pre-resolution
(Phase 1) AST MAY carry a missing `us` field.

## References

- Ayres, J. J. B., Benedict, J. O., & Witcher, E. S. (1975). Systematic
  manipulation of individual events in a truly random control in rats.
  *Journal of Comparative and Physiological Psychology*, 88(1), 97-103.
  https://doi.org/10.1037/h0076200
- Bouton, M. E. (2004). Context and behavioral processes in extinction.
  *Learning & Memory*, 11(5), 485-494.
  https://doi.org/10.1101/lm.78804
- Ellison, G. D. (1964). Differential salivary conditioning to traces.
  *Journal of Comparative and Physiological Psychology*, 57(3), 373-380.
  https://doi.org/10.1037/h0043484
- Lubow, R. E., & Moore, A. U. (1959). Latent inhibition: The effect of
  nonreinforced pre-exposure to the conditional stimulus. *Journal of
  Comparative and Physiological Psychology*, 52(4), 415-419.
  https://doi.org/10.1037/h0046700
- Mackintosh, N. J. (1974). *The psychology of animal learning*. Academic Press.
- Pavlov, I. P. (1927). *Conditioned reflexes* (G. V. Anrep, Trans.).
  Oxford University Press.
- Randich, A., & LoLordo, V. M. (1979). Associative and nonassociative
  theories of the UCS preexposure phenomenon. *Psychological Bulletin*,
  86(3), 523-548. https://doi.org/10.1037/0033-2909.86.3.523
- Rescorla, R. A. (1967). Pavlovian conditioning and its proper control
  procedures. *Psychological Review*, 74(1), 71-80.
  https://doi.org/10.1037/h0024109
- Rescorla, R. A. (1968). Probability of shock in the presence and
  absence of CS in fear conditioning. *Journal of Comparative and
  Physiological Psychology*, 66(1), 1-5.
  https://doi.org/10.1037/h0025984
- Rescorla, R. A. (1980). Simultaneous and successive associations in
  sensory preconditioning. *Journal of Experimental Psychology: Animal
  Behavior Processes*, 6(3), 207-216.
  https://doi.org/10.1037/0097-7403.6.3.207
- Spetch, M. L., Wilkie, D. M., & Pinel, J. P. J. (1981). Backward
  conditioning: A reevaluation of the empirical evidence. *Psychological
  Bulletin*, 89(1), 163-175. https://doi.org/10.1037/0033-2909.89.1.163
