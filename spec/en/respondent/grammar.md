# Respondent Grammar — Two-Term Contingency (CS–US)

> Part of the contingency-dsl respondent layer (Ψ). Defines the respondent-specific EBNF productions for the two-term contingency (CS–US), the Tier A Pavlovian primitives (R1–R14), and the grammar-level extension point through which third-party packages (primarily `contingency-respondent-dsl`) contribute Tier B procedures without modifying the respondent grammar. Paradigm-neutral meta-grammar is defined in `foundations/grammar.md`; operant-specific productions in `operant/grammar.md`; per-primitive operational specifications in `respondent/primitives.md`.

**Companion documents:**
- [Respondent Theory](theory.md) — two-term contingency as a formal object, Rescorla contingency space, acquisition / extinction, I/T ratio.
- [Respondent Primitives](primitives.md) — operational definitions, parameter semantics, and citations for R1–R14.
- [LL(2) Formal Proof](../foundations/ll2-proof.md) — Foundations-level unambiguity proof. The respondent grammar introduces no new LL(2) decision points; all decision points are LL(1).

---

## 1. Scope of the Respondent Layer

The respondent layer describes the **two-term contingency** (CS–US): a temporal and probabilistic relation between a conditional stimulus (CS) and an unconditional stimulus (US). The scope is intentionally minimal — the Tier A primitives below cover the foundational Pavlovian arrangements (Pavlov, 1927; Rescorla, 1967, 1968) and the control procedures they require, but delegate deeper Pavlovian phenomena (blocking, overshadowing, latent inhibition, renewal, reinstatement, etc.) to the companion package `contingency-respondent-dsl` via the extension point in §4.

The two-term contingency is a structurally distinct formal object from the three-term contingency (SD-R-SR), not a degenerate special case of it. See `theory.md §1` for the formal argument and `foundations/contingency-types.md` for the paradigm-neutral typing.

---

## 2. Respondent-Specific Productions

Building on the paradigm-neutral skeleton in `foundations/grammar.md`, the respondent layer specializes `<expr>` to `<respondent_expr>`:

```bnf
<program>                 ::= <param_decl>* <binding>* <respondent_expr>
<respondent_expr>         ::= <core_respondent_primitive>
                            | <extension_respondent_primitive>

<core_respondent_primitive> ::= <pair_expr>
                              | <extinction_expr>
                              | <cs_only_expr>
                              | <us_only_expr>
                              | <contingency_expr>
                              | <truly_random_expr>
                              | <explicitly_unpaired_expr>
                              | <compound_expr>
                              | <serial_expr>
                              | <iti_expr>
                              | <differential_expr>

<extension_respondent_primitive> ::= <ident_upper> "(" <arg_list>? ")"
                                    -- program-scoped; see §4
<ident_upper>             ::= [A-Z][a-zA-Z0-9_]*
```

The `<ident_upper>` form is disjoint from Tier A primitive names: an extension primitive is resolved at program scope via the respondent registry only if its name does not match any Tier A primitive name.

### 2.1 Pair Primitives (R1–R4)

```bnf
<pair_expr>               ::= "Pair" "." <pair_mode> "(" <pair_args> ")"
<pair_mode>               ::= "ForwardDelay"
                            | "ForwardTrace"
                            | "Simultaneous"
                            | "Backward"
<pair_args>               ::= <pair_positional> ("," <pair_kw>)*
<pair_positional>         ::= <cs_ref> "," <us_ref>
                            | <us_ref> "," <cs_ref>     -- Backward only
<pair_kw>                 ::= "isi" "=" <value>
                            | "cs_duration" "=" <value>
                            | "trace_interval" "=" <value>
<cs_ref>                  ::= <ident> | <string_literal>
<us_ref>                  ::= <ident> | <string_literal>
```

The four `Pair.*` modes correspond to R1–R4 in `primitives.md`:
- `Pair.ForwardDelay(cs, us, isi, cs_duration)` — CS onset → CS continues → US onset; CS and US temporally overlap.
- `Pair.ForwardTrace(cs, us, trace_interval)` — CS offset → trace gap → US onset.
- `Pair.Simultaneous(cs, us)` — CS onset = US onset.
- `Pair.Backward(us, cs, isi)` — US onset → US offset → CS onset. The US reference appears first, matching the temporal order in the canonical procedure.

Per-mode keyword-argument legality (e.g., `trace_interval` is valid only for `ForwardTrace`) is enforced semantically in Phase 2 (`foundations/grammar.md §4`), not syntactically at the grammar level.

### 2.2 Elementary Single-Stimulus Primitives (R5–R7)

```bnf
<extinction_expr>         ::= "Extinction" "(" <cs_ref> ")"
<cs_only_expr>            ::= "CSOnly" "(" <cs_ref> "," "trials" "=" <number> ")"
                            | "CSOnly" "(" <cs_ref> "," <number> ")"
<us_only_expr>            ::= "USOnly" "(" <us_ref> "," "trials" "=" <number> ")"
                            | "USOnly" "(" <us_ref> "," <number> ")"
```

`Extinction(cs)` denotes CS-alone presentation **after** an acquisition history (Pavlov, 1927; Bouton, 2004). The respondent layer treats the prior history as a property of the enclosing `PhaseSequence`; a bare `Extinction(cs)` outside a phase context is semantically ill-formed at Phase 2 unless the program chooses to assign it a default history. `CSOnly` and `USOnly` are phase-independent primitives: they denote presentation without the paired stimulus and do not require prior acquisition (Lubow & Moore, 1959; Randich & LoLordo, 1979).

### 2.3 Contingency Primitives (R8–R10)

```bnf
<contingency_expr>        ::= "Contingency" "(" <prob> "," <prob> ")"
<truly_random_expr>       ::= "TrulyRandom" "(" <cs_ref> "," <us_ref> ")"
                            | "TrulyRandom" "(" <cs_ref> "," <us_ref> "," "p" "=" <prob> ")"
<explicitly_unpaired_expr> ::= "ExplicitlyUnpaired" "(" <cs_ref> "," <us_ref>
                                ("," "min_separation" "=" <value>)? ")"
<prob>                    ::= <number>     -- constrained 0 ≤ prob ≤ 1 semantically
```

`Contingency(p_us_given_cs, p_us_given_no_cs)` parameterizes a point in the Rescorla (1967) contingency space. The first argument is the probability of US given CS; the second is the probability of US given ¬CS. The argument order (CS-conditional first) is fixed at the grammar level and is not permutable.

`TrulyRandom(cs, us)` is syntactic sugar for a point on the diagonal `Contingency(p, p)` of the contingency space (`theory.md §2`). `ExplicitlyUnpaired(cs, us, min_separation)` corresponds to `Contingency(0, p)` with an additional temporal-separation constraint on US placement (Ayres, Benedict, & Witcher, 1975). Both are kept as distinct primitives so that intent is preserved in the parse tree, even though they are semantic specializations of `Contingency`.

### 2.4 Structural Primitives (R11–R13)

```bnf
<compound_expr>           ::= "Compound" "(" <cs_list> ("," "mode" "=" <compound_mode>)? ")"
<cs_list>                 ::= "[" <cs_ref> ("," <cs_ref>)+ "]"
                            | <cs_ref> ("," <cs_ref>)+
<compound_mode>           ::= "Simultaneous"      -- default; other modes are extensions

<serial_expr>             ::= "Serial" "(" <cs_list> "," "isi" "=" <value> ")"

<iti_expr>                ::= "ITI" "(" <iti_distribution> "," "mean" "=" <value> ")"
<iti_distribution>        ::= "fixed" | "uniform" | "exponential"
```

`Compound(cs_list, mode=Simultaneous)` presents multiple CSs. The `mode` argument defaults to `Simultaneous`; additional modes (e.g., asynchronous-onset variants) are deferred to extension primitives in `contingency-respondent-dsl`.

`Serial(cs_list, isi)` presents CSs in temporal order and does **not** accept a `mode` argument — seriality already implies temporal ordering.

`ITI(distribution, mean)` is a structural element, not metadata. Jitter is a separate concern handled by the `@iti` annotation in `annotations/extensions/respondent-annotator.md`; when jitter is irrelevant, the primitive alone suffices.

### 2.5 Differential Conditioning (R14)

```bnf
<differential_expr>       ::= "Differential" "(" <cs_ref> "," <cs_ref> "," <us_ref> ")"
                            | "Differential" "(" <cs_ref> "," <cs_ref> ")"
                               -- short form: US implicit, resolved from enclosing phase
```

`Differential(cs_positive, cs_negative, us)` explicitly names the positive CS, the negative CS, and the US. The short form `Differential(cs_positive, cs_negative)` is syntactic sugar for the three-argument form with the US inferred from the enclosing phase-level `@us` annotation (respondent-annotator); when no enclosing `@us` is available, the short form is a Phase 2 semantic error.

Differential conditioning was promoted from Tier B to Tier A because of its JEAB frequency and because its operational intent (contrastive training of `CS+` versus `CS−`) is not transparent when encoded as a composition of `Pair.ForwardDelay` plus `CSOnly` (Pavlov, 1927; Mackintosh, 1974).

---

## 3. Reserved Keyword Set (Respondent Layer)

```bnf
<reserved>      ::= "Pair" | "ForwardDelay" | "ForwardTrace" | "Simultaneous" | "Backward"
                  | "Extinction" | "CSOnly" | "USOnly"
                  | "Contingency" | "TrulyRandom" | "ExplicitlyUnpaired"
                  | "Compound" | "Serial" | "ITI"
                  | "Differential"
                  | "trials" | "isi" | "cs_duration" | "trace_interval"
                  | "mode" | "mean" | "min_separation" | "p"
                  | "fixed" | "uniform" | "exponential"
```

The respondent layer inherits `let`, `def`, and paradigm-neutral keywords from `foundations/grammar.md`. The respondent reserved set is disjoint from the operant reserved set (`operant/grammar.md §1.1`): no identifier is simultaneously a Tier A respondent primitive and an operant construct. This disjointness is a precondition for the Composed layer (`composed/*`), which freely mixes both.

---

## 4. Respondent Extension Point

Third-party packages extend the respondent layer by contributing production rules to `<extension_respondent_primitive>`. The primary consumer is `contingency-respondent-dsl`, which defines Tier B primitives such as higher-order conditioning, sensory preconditioning, blocking, overshadowing, latent inhibition, conditioned inhibition, occasion setting, reinstatement, renewal, spontaneous recovery, counterconditioning, overexpectation, retrospective revaluation, conditioned taste aversion, and others.

This extension point parallels the Schedule Extension point in the Operant layer (design-philosophy §5.1–§5.3) and inherits the same five properties (design-philosophy §5.4):

1. **Respondent grammar remains immutable.** Extensions add production rules; they do not rewrite existing Tier A rules.
2. **Program-scoped closure.** Each program (runtime / interpreter) maintains its own respondent registry. A program that does not load a given extension treats its constituents as unknown tokens and emits a parse error.
3. **Static verification boundary.** Tier A primitives are fully statically verifiable (parameter ranges, argument arity, CS/US binding). Extensions supply their own verification rules.
4. **Protection of the TC boundary.** Extensions may consume runtime state (e.g., reinstatement conditional on a prior extinction phase), but the Respondent layer itself introduces no Turing-complete construct. See §5 below.
5. **Equivalence judgment is the extension's responsibility.** Equivalence of two identical extension constituents is judged by rules provided by the extension module; the core equivalence rules apply only to Tier A.

### 4.1 Extension Registration Conventions

An extension primitive is recognized only when:
- Its name matches `<ident_upper>` (initial uppercase letter).
- The program's respondent registry resolves the name to a registered extension.
- The primitive's argument list conforms to the extension-declared schema.

The grammar admits any well-formed `<ident_upper> "(" <arg_list>? ")"` at parse time; registry resolution is a Phase 2 (post-parsing) responsibility. This preserves the property that the respondent parser is program-independent.

### 4.2 Relationship to the Annotation Layer

Some respondent phenomena can be expressed as extension primitives (structural additions to the grammar) or as annotations (metadata attached to Tier A primitives). The boundary is governed by `annotations/boundary-decision.md §2` (Q1–Q3):
- If a phenomenon **changes the structure of the procedure** (e.g., introduces a new temporal order of CSs, as in higher-order conditioning), it belongs in the Respondent extension point.
- If it merely **annotates properties** of an existing Tier A procedure (e.g., CS modality, US intensity), it belongs in the Annotation layer — specifically `annotations/extensions/respondent-annotator.md`.

---

## 5. Static Analysis Properties

The respondent grammar preserves the computational properties of the Foundations + Operant layers:

**Proposition (CFG).** The respondent grammar is a context-free grammar. Every production rule above has at most one nonterminal on the left-hand side and a finite sequence of terminals and nonterminals on the right-hand side. No production introduces context dependence.

**Proposition (Non-TC).** The respondent layer is not Turing-complete. Each Tier A primitive specifies a finite, declarative procedure whose parameters are literal values determined at parse time; no primitive admits runtime iteration, recursion, or state-dependent branching at the grammar level. The Respondent extension point (§4) may consume runtime state in its semantic evaluation, but the extension mechanism itself does not add TC power to the respondent grammar.

**Proposition (LL(2)-compatible).** The respondent grammar introduces no new LL(2) decision points beyond those already analyzed in `foundations/ll2-proof.md`. Every `<respondent_expr>` alternative is distinguishable by its first token (LL(1)): `Pair`, `Extinction`, `CSOnly`, `USOnly`, `Contingency`, `TrulyRandom`, `ExplicitlyUnpaired`, `Compound`, `Serial`, `ITI`, `Differential`, or an `<ident_upper>` not matching any of the above (extension).

These three properties are preconditions for the Composed layer, which combines respondent and operant expressions: if either constituent were TC, the composed layer would inherit TC, violating design-philosophy §2 (Foundations + Operant + Respondent + Composed remain non-TC).

---

## 6. Example Expressions

```
-- Pair primitives
Pair.ForwardDelay(tone, shock, isi=10-s, cs_duration=15-s)
Pair.ForwardTrace(tone, food, trace_interval=5-s)
Pair.Simultaneous(light, airpuff)
Pair.Backward(shock, tone, isi=2-s)

-- Elementary primitives
Extinction(tone)
CSOnly(tone, trials=40)
USOnly(shock, trials=20)

-- Contingency primitives
Contingency(0.9, 0.1)                             -- Rescorla (1967) positive contingency
Contingency(0.5, 0.5)                             -- diagonal: truly random
TrulyRandom(tone, shock)                          -- sugar for Contingency(p, p)
ExplicitlyUnpaired(tone, shock, min_separation=30-s)

-- Structural primitives
Compound([tone, light])                           -- defaults to mode=Simultaneous
Compound([tone, light], mode=Simultaneous)        -- explicit
Serial([light, tone], isi=3-s)
ITI(exponential, mean=60-s)

-- Differential conditioning
Differential(tone_plus, tone_minus, shock)        -- full form
Differential(tone_plus, tone_minus)               -- short form (US from enclosing @us)
```

---

## 7. Error Recovery

Respondent-specific error codes appear in `conformance/respondent/errors.json`. The error recovery policy itself (panic-mode, synchronization tokens, multi-error reporting) is paradigm-neutral and specified in `foundations/grammar.md §7`.

---

## References

- Ayres, J. J. B., Benedict, J. O., & Witcher, E. S. (1975). Systematic manipulation of individual events in a truly random control in rats. *Journal of Comparative and Physiological Psychology*, 88(1), 97–103. https://doi.org/10.1037/h0076200
- Bouton, M. E. (2004). Context and behavioral processes in extinction. *Learning & Memory*, 11(5), 485–494. https://doi.org/10.1101/lm.78804
- Ellison, G. D. (1964). Differential salivary conditioning to traces. *Journal of Comparative and Physiological Psychology*, 57(3), 373–380. https://doi.org/10.1037/h0043484
- Lubow, R. E., & Moore, A. U. (1959). Latent inhibition: The effect of nonreinforced pre-exposure to the conditional stimulus. *Journal of Comparative and Physiological Psychology*, 52(4), 415–419. https://doi.org/10.1037/h0046700
- Mackintosh, N. J. (1974). *The psychology of animal learning*. Academic Press.
- Pavlov, I. P. (1927). *Conditioned reflexes: An investigation of the physiological activity of the cerebral cortex* (G. V. Anrep, Trans.). Oxford University Press.
- Randich, A., & LoLordo, V. M. (1979). Associative and nonassociative theories of the UCS preexposure phenomenon. *Psychological Bulletin*, 86(3), 523–548. https://doi.org/10.1037/0033-2909.86.3.523
- Rescorla, R. A. (1967). Pavlovian conditioning and its proper control procedures. *Psychological Review*, 74(1), 71–80. https://doi.org/10.1037/h0024109
- Rescorla, R. A. (1968). Probability of shock in the presence and absence of CS in fear conditioning. *Journal of Comparative and Physiological Psychology*, 66(1), 1–5. https://doi.org/10.1037/h0025984
- Rescorla, R. A. (1972). Informational variables in Pavlovian conditioning. In G. H. Bower (Ed.), *The psychology of learning and motivation* (Vol. 6, pp. 1–46). Academic Press. https://doi.org/10.1016/S0079-7421(08)60383-7
- Rescorla, R. A. (1980). Simultaneous and successive associations in sensory preconditioning. *Journal of Experimental Psychology: Animal Behavior Processes*, 6(3), 207–216. https://doi.org/10.1037/0097-7403.6.3.207
- Rescorla, R. A., & Wagner, A. R. (1972). A theory of Pavlovian conditioning: Variations in the effectiveness of reinforcement and nonreinforcement. In A. H. Black & W. F. Prokasy (Eds.), *Classical conditioning II: Current research and theory* (pp. 64–99). Appleton-Century-Crofts.
- Spetch, M. L., Wilkie, D. M., & Pinel, J. P. J. (1981). Backward conditioning: A reevaluation of the empirical evidence. *Psychological Bulletin*, 89(1), 163–175. https://doi.org/10.1037/0033-2909.89.1.163
