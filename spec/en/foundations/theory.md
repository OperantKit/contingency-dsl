# Foundations Theory — Paradigm-Neutral Mathematical Substrate

> Part of the contingency-dsl foundations layer. Defines the paradigm-neutral mathematical foundations shared by operant (three-term) and respondent (two-term) contingency structures: the general definition of contingency, determinism of the grammar, and the non-Turing-complete (non-TC) claim. Operant-specific derivations (three-term contingency computations, schedule algebra, combinator semantics) live in `operant/theory.md`; respondent-specific derivations live in `respondent/theory.md`.

---

## 1. Contingency as a General Relation

In the experimental analysis of behavior, a **contingency** is a probabilistic / logical relation between events. The foundations layer defines the relation abstractly; the operant and respondent layers specialize it.

**Definition 1 (Event).** An event is an occurrence at a point in time, belonging to one of the following categories defined in `stimulus-typing.md` and `time-scales.md`:

- Stimulus onsets and offsets (CS, US, SD, SΔ)
- Responses (R)
- Consequences (Sr+, Sr−, punisher)
- Time ticks (clock advances)

**Definition 2 (Contingency).** A contingency is a triple `(A, B, P)` where `A` and `B` are event types and `P` is a conditional probability structure relating them. Two canonical specializations exist:

- **Two-term contingency** (respondent): `P(US | CS)` vs `P(US | ¬CS)` — the Pavlovian contingency space (Rescorla, 1967). Detailed in `contingency-types.md` and `respondent/theory.md`.
- **Three-term contingency** (operant): `P(Sr+ | R, SD)` — the Skinnerian three-term contingency (SD–R–SR). Detailed in `contingency-types.md` and `operant/theory.md`.

The distinction between contingent and non-contingent (response-independent) arrangements is foundational and is treated separately in `contingency-types.md`.

## 2. Determinism of the Grammar

**Proposition 1 (Syntactic determinism).** For any valid source string `s`, the DSL grammar admits exactly one parse tree. This is established by the LL(2) proof in `ll2-proof.md`: every decision point is LL(1) except one local LL(2) decision inside operant compound `arg_list`; no decision point admits multiple alternatives.

**Proposition 2 (Semantic determinism).** Given a parse tree and a canonical initial state `σ₀`, the semantic analysis phase produces a unique resolved AST. The three-phase pipeline (§4 of `foundations/grammar.md`) is total: each phase transition is either total success (producing the next-phase AST) or total failure (reporting an error list with no AST). No phase introduces nondeterminism.

**Corollary.** `parse ∘ resolve` is a partial function from source strings to resolved ASTs. On success, the output is unique; on failure, an error list is produced.

## 3. Non-Turing-Complete (non-TC) Claim

**Claim.** The DSL — encompassing the foundations, operant, respondent, composed, and experiment layers — is **not Turing-complete**.

**Grounds.** Each layer is characterized by the Schedule Expression Invariance (SEI) properties P1, P2, P3 defined in `architecture.md §4.1.1`:

- **P1 (Expression Tree Fixity).** The AST is fully determined at parse time and does not structurally change during a session.
- **P2 (Parameter Enumerability).** All parameters are literal values or outputs of closed-form, parse-time-fixed rules.
- **P3 (Single-Schedule Identity).** The schedule identity remains invariant within a phase; no transition to a structurally different expression occurs based on runtime state.

Turing-complete runtime features (arbitrary conditional branching on runtime observables, recursive schedule transitions, yoked cross-subject evaluation, external-state-conditioned parameter updates) are delegated to sibling packages (`contingency-core`, `experiment-core`). See `architecture.md §4.1` for the full layer boundary.

**What this buys us.** Non-TC grammars admit statically decidable properties that a TC language cannot express:

- Reachability ("Does this procedure ever produce reinforcement?")
- Dead-code detection ("Are all components reachable?")
- Structural validity ("Does `Conc` have ≥ 2 components?")
- Linter warnings anchored to tree structure (e.g., `MISSING_COD` in operant-layer concurrent schedules)

These properties are decidable by syntax-tree traversal because the grammar position in the Chomsky hierarchy is CFG + bounded macro expansion (`let`, `Repeat`).

## 4. The Three Equivalence Relations

All paradigm layers share the following relations on expressions. Paradigm-specific refinements (semantic equivalence `≡` operating over observation traces) live in the respective layer's `theory.md`.

**Definition 3 (Syntactic equality, `=_syn`).** Two expressions `E₁` and `E₂` are *syntactically equal* iff their AST representations are structurally identical — every node type, operator, parameter value, and child ordering matches. Syntactic equality is decidable by recursive structural comparison.

**Definition 4 (Semantic equivalence, `≡`).** Two expressions are *semantically equivalent* iff they produce identical outcomes for every possible observation trace (the trace universe is paradigm-specific; operant uses response streams with time ticks, respondent uses CS/US event streams with time ticks). The negation is written `≢`.

**Definition 5 (Sound rewrite rule, `→`).** A *sound rewrite rule* `E₁ → E₂` is a directed AST transformation such that `E₁ ≡ E₂`. Conforming implementations MAY apply sound rewrites as optimization passes but MUST NOT apply unsound ones.

The operant and respondent layers each populate these relations with a concrete trace universe and outcome sequence definition.

## 5. Type Safety (Paradigm-Neutral)

Well-formed DSL programs do not produce type errors during semantic analysis. The argument follows Pierce (2002, TAPL §8.3) adapted to the DSL's three-phase compilation pipeline. The paradigm-neutral claim is:

**Theorem (Progress + Preservation, foundations statement).** For every source string `s` that parses successfully under any paradigm layer:

- (*Progress*) Either the AST is in Phase 3 (a value), or it is reducible by exactly one of: binding expansion, `Repeat` desugaring (if applicable to the paradigm layer), or paradigm-specific default propagation.
- (*Preservation*) Each phase transition preserves well-typedness: it maps a well-typed Phase-k AST to a well-typed Phase-(k+1) AST, or fails with a typed error list.

**Corollary (no type errors).** No well-formed DSL program produces a type error during semantic analysis. All errors are either lexical, syntactic, or paradigm-specific semantic (constraint violations reported with error codes).

This theorem is proved for the operant layer in `operant/theory.md §2.12` and for the respondent layer in `respondent/theory.md`; the argument structure is identical and is abstracted here for reuse.

## 6. Scope Limitations

This foundations theory covers the DSL's static semantics (compilation pipeline). Runtime correctness — that a resolved AST, when interpreted by a schedule engine, produces the intended behavior — depends on engine implementation (e.g., `contingency-core`) and is outside the foundations scope.

## References

- Aho, A. V., Lam, M. S., Sethi, R., & Ullman, J. D. (2006). *Compilers: Principles, techniques, and tools* (2nd ed.). Addison-Wesley.
- Catania, A. C. (2013). *Learning* (5th ed.). Sloan Publishing.
- Lattal, K. A. (1995). Contingency and behavior analysis. *Mexican Journal of Behavior Analysis*, 21, 47–73.
- Pierce, B. C. (2002). *Types and programming languages*. MIT Press.
- Rescorla, R. A. (1967). Pavlovian conditioning and its proper control procedures. *Psychological Review*, 74(1), 71–80. https://doi.org/10.1037/h0024109
- Skinner, B. F. (1938). *The behavior of organisms*. Appleton-Century.
