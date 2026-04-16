# Compound Schedules — Conc, Chain, Tand, Mult, Mix, Alt, Conj

> Part of the contingency-dsl operant layer. Defines the seven compound-schedule combinators over the atomic operant grid: concurrent, chained, tandem, multiple, mixed, alternative, and conjunctive arrangements. The conjunctive schedule is included here as a compound-schedule variant (Herrnstein & Morse, 1958).

---

## 1. Classification

Compound schedules form a structured algebra over atomic schedules. We classify them along three independent semantic dimensions (see `operant/theory.md §2.1` for the full derivation):

- **Topology** — parallel, sequential, or alternating.
- **Discriminability** — whether discriminative stimuli (SD) signal transitions.
- **Satisfaction logic** — OR (disjunctive), AND (conjunctive), independent, sequential, or context-switched.

| Schedule | Abbrev. | Topology | Discriminability | Logic | Operanda |
|---|---|---|---|---|---|
| Concurrent | Conc | Parallel | N/A (separate) | Independent | Multiple |
| Alternative | Alt | Parallel | N/A | OR | Single |
| Conjunctive | Conj | Parallel | N/A | AND | Single |
| Chained | Chain | Sequential | Discriminated | Sequential | Single |
| Tandem | Tand | Sequential | Undiscriminated | Sequential | Single |
| Multiple | Mult | Alternating | Discriminated | Context-switched | Single |
| Mixed | Mix | Alternating | Undiscriminated | Context-switched | Single |

Chain/Tand and Mult/Mix are discriminated/undiscriminated pairs under the same topology.

## 2. Algebraic Properties (summary)

The full algebra with theorems, proofs, and sound rewrite rules is in `operant/theory.md §2.2`. Key properties:

- **Commutativity.** `Conc`, `Alt`, `Conj` are commutative. `Chain`, `Tand`, `Mult`, `Mix` are not (sequential/alternation order matters).
- **Associativity.** All seven flatten to N-ary compositions.
- **Identities.** `Alt(S, EXT) ≡ S`, `Conj(S, CRF) ≡ S`, `Chain(CRF, S) ≡ S`.
- **Annihilators.** `Conj(S, EXT) ≡ EXT`, `Alt(S, CRF) ≡ CRF`.
- **Non-distributivity.** Parenthesization is structurally significant; no distribution law applies.

## 3. Concurrent — Conc

Two or more schedules operate simultaneously on distinct operanda. The subject freely allocates responses; each operandum maintains its own contingency.

```
Conc(VI 30-s, VI 60-s, COD=2-s)
```

**Changeover Delay (COD; Catania, 1966) and Fixed-Ratio Changeover (FRCO; Hunter & Davison, 1985)** are structural parameters of `Conc`:

- `COD=Xs` — minimum time after an operandum switch before reinforcement becomes available on the new operandum.
- `FRCO=N` — minimum N responses on the new operandum after switch before reinforcement.

Directional COD enables asymmetric switch costs (Pliskoff, 1971; Williams & Bell, 1999):

```
Conc(VI 30-s, VI 60-s, COD(1->2)=2-s, COD(2->1)=5-s)
```

See `operant/theory.md §2.4` for the full COD/FRCO specification, directional semantics, and base+override rules.

**Canonical references:**
- Catania, A. C. (1966). Concurrent performances: Reinforcement interaction and response independence. *Journal of the Experimental Analysis of Behavior*, 9(5), 573–588. https://doi.org/10.1901/jeab.1966.9-573
- Herrnstein, R. J. (1961). Relative and absolute strength of response as a function of frequency of reinforcement. *Journal of the Experimental Analysis of Behavior*, 4(3), 267–272. https://doi.org/10.1901/jeab.1961.4-267
- Hunter, I., & Davison, M. (1985). Determination of a behavioral transfer function. *Journal of the Experimental Analysis of Behavior*, 43(1), 43–59. https://doi.org/10.1901/jeab.1985.43-43
- Shull, R. L., & Pliskoff, S. S. (1967). Changeover delay and concurrent schedules. *Journal of the Experimental Analysis of Behavior*, 10(6), 517–527. https://doi.org/10.1901/jeab.1967.10-517
- Findley, J. D. (1958). Preference and switching under concurrent scheduling. *Journal of the Experimental Analysis of Behavior*, 1(2), 123–144. https://doi.org/10.1901/jeab.1958.1-123

## 4. Chained — Chain and Tandem — Tand

Sequential combinators: completing one schedule (link) transitions control to the next. The final link's reinforcement ends the arrangement.

- **Chain**: each link is paired with a distinct discriminative stimulus (SD). The SD change signals the transition.
- **Tand**: no SD change signals the transition; the links share a single stimulus context.

```
Chain(FR 5, FI 30-s)       -- FR 5 in SD_A, then FI 30-s in SD_B
Tand(VR 20, DRL 5-s)        -- VR 20 then DRL 5-s without SD change
```

At the denotational level, `Chain` and `Tand` share the same transition structure; the discriminability difference is an environmental variable outside the schedule machine (see `operant/theory.md §2.13.4`).

**Canonical references:**
- Ferster, C. B., & Skinner, B. F. (1957). *Schedules of reinforcement*. Appleton-Century-Crofts. (Ch. 11–12)
- Kelleher, R. T., & Fry, W. (1962). Stimulus functions in chained fixed-interval schedules. *Journal of the Experimental Analysis of Behavior*, 5(2), 167–173. https://doi.org/10.1901/jeab.1962.5-167
- Autor, S. M. (1969). The strength of conditioned reinforcers as a function of frequency and probability of reinforcement. In D. P. Hendry (Ed.), *Conditioned reinforcement* (pp. 127–162). Dorsey Press.

## 5. Multiple — Mult and Mixed — Mix

Alternating combinators: components alternate with transitions controlled by the environment (not by the subject's satisfaction of the current component).

- **Mult**: each component is paired with a distinct SD. Used in behavioral-contrast research.
- **Mix**: components alternate without SD change.

```
Mult(VI 30-s, EXT, BO=5-s)       -- Mult with 5-s blackout between components
Mix(FR 5, FR 10, BO=3-s)         -- Mix with blackout, undiscriminated
```

**Blackout (BO)** is a response-independent dark period between components, structurally symmetric with COD's role in Conc. See `operant/theory.md §2.5` for the BO specification.

**Canonical references:**
- Ferster, C. B., & Skinner, B. F. (1957). *Schedules of reinforcement*. Appleton-Century-Crofts. (Ch. 13–14)
- Reynolds, G. S. (1961). Behavioral contrast. *Journal of the Experimental Analysis of Behavior*, 4(1), 57–71. https://doi.org/10.1901/jeab.1961.4-57

## 6. Alternative — Alt

Disjunctive parallel combinator: whichever component is satisfied first triggers reinforcement; all components then reset.

```
Alt(FR 10, FI 5-min)             -- reinforced when FR 10 or FI 5-min is satisfied
```

Algebraically: `Alt(S, EXT) ≡ S` (identity), `Alt(S, CRF) ≡ CRF` (annihilator).

## 7. Conjunctive — Conj (including Herrnstein-Morse Conjunctive FR FI)

Conjunctive parallel combinator: reinforcement requires **all** components to be satisfied simultaneously.

```
Conj(FR 5, FI 30-s)              -- reinforced when FR 5 AND FI 30-s are both satisfied
```

**Herrnstein-Morse (1958) conjunctive FR FI** is a specific case of `Conj` applied to one FR component and one FI component. It is not a separate primitive in contingency-dsl — the `Conj` combinator with FR and FI arguments expresses exactly this arrangement:

```
Conj(FR 5, FI 30-s)              -- conjunctive FR 5 FI 30 (Herrnstein & Morse, 1958)
```

Algebraically: `Conj(S, CRF) ≡ S` (identity), `Conj(S, EXT) ≡ EXT` (annihilator).

**Canonical references:**
- Herrnstein, R. J., & Morse, W. H. (1958). Some effects of response-independent positive reinforcement on maintained operant behavior. *Journal of Comparative and Physiological Psychology*, 50(5), 461–467.
- Catania, A. C. (2013). *Learning* (5th ed.). Sloan. (Glossary: conjunctive schedule)

## 8. Second-Order Schedules

A second-order schedule composes two atomic schedules into hierarchical roles — an inner unit schedule whose completions are counted by an outer overall schedule (Kelleher, 1966):

```
FR 5(FI 30-s)      -- treat each FI 30 completion as one unit; reinforce after 5 units
```

See `operant/theory.md §2.11` for the full specification, brief-stimulus requirement (`@brief` annotation), and FR-overall equivalence to `Repeat`.

## 9. Nested Compositions

All combinators compose recursively:

```
Conc(Chain(FR 5, VI 60-s), Alt(FR 10, FT 30-s))
```

The DSL grammar supports arbitrary nesting depth; the type system guarantees that every compound expression terminates in atomic leaves (see `foundations/theory.md §5`).

## 10. Errors and Warnings

| Code | Condition | Severity |
|---|---|---|
| `COMPOUND_TOO_FEW_ARGS` | Compound with < 2 positional args | SemanticError |
| `MISSING_COD` | `Conc(VI, VI)` without COD specification | WARNING |
| `INVALID_KEYWORD_ARG` | Unknown keyword on specific combinator | SemanticError |
| `DUPLICATE_KEYWORD_ARG` | Same keyword appearing twice | SemanticError |

See `conformance/operant/errors.json` for the full registry.

## References

See inline references in each section. Additional compound-schedule literature:

- Autor, S. M. (1969). See §4.
- Ferster, C. B., & Skinner, B. F. (1957). *Schedules of reinforcement*. Appleton-Century-Crofts.
- Herrnstein, R. J. (1961). See §3.
- Herrnstein, R. J., & Morse, W. H. (1958). See §7.
- Kelleher, R. T. (1966). Conditioned reinforcement in second-order schedules. *Journal of the Experimental Analysis of Behavior*, 9(5), 475–485. https://doi.org/10.1901/jeab.1966.9-475
- Kelleher, R. T., & Fry, W. (1962). See §4.
- Shull, R. L., & Pliskoff, S. S. (1967). See §3.
- Findley, J. D. (1958). See §3.
