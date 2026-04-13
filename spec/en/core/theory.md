# An Algebraic Type System for Reinforcement Schedules

## Abstract

This document formalizes the taxonomy of reinforcement schedules as an algebraic type system, providing a theoretical foundation for the contingency-dsl domain-specific language. We show that every simple reinforcement schedule is a product of two independent dimensions — Distribution and Domain — yielding a 3×3 grid of atomic schedules. We define a composition algebra over seven combinators (Concurrent, Alternative, Conjunctive, Chained, Tandem, Multiple, Mixed) with formally characterized algebraic properties including commutativity, associativity, identity elements, and annihilators.

For the formal grammar, architectural boundaries, implementation bridge, and alternative representations, see companion documents:

- [grammar.md](grammar.md) — Context-free grammar (BNF), notational flexibility, dual API
- [architecture.md](architecture.md) — Three-layer architecture, computability, annotation system
- [implementation.md](implementation.md) — Python type mapping, legacy assessment
- [representations.md](representations.md) — Alternative coordinate systems (T-tau)

---

## Part I: Atomic Schedule Taxonomy — The Product Type Distribution × Domain

### 1.1 Two Independent Dimensions

Every simple reinforcement schedule can be expressed as the product of two independent dimensions. This insight, implicit in Ferster and Skinner's (1957) original taxonomy and made explicit in the OperantKit framework's bit-packed `ScheduleType` (Mizutani, 2018), admits the following formalization.

**Definition 1 (Distribution).** The value distribution dimension determines *how* the schedule parameter is selected across successive reinforcement cycles.

```
Distribution ::= Fixed | Variable | Random
```

- **Fixed**: The parameter value is constant across all reinforcement cycles. Deterministic.
- **Variable**: The parameter is drawn from a Fleshler-Hoffman (1962) generated sequence that guarantees mean-preserving, non-replacement sampling within each cycle. Quasi-random with controlled statistical properties.
- **Random**: The parameter is sampled independently on each trial from a uniform distribution. Truly stochastic, memoryless.

The critical distinction between Variable and Random — often confused in the literature — is that Variable uses a pre-computed Fleshler-Hoffman sequence cycled deterministically, while Random generates a fresh value per trial. This corresponds to sampling without replacement from a constrained distribution (Variable) versus sampling with replacement from a simple distribution (Random). The Variable distribution implements the constant-probability-of-reinforcement-per-response assumption more faithfully than naive randomization (Fleshler & Hoffman, 1962).

**Definition 2 (Domain).** The contingency domain dimension determines *what behavioral dimension* the schedule parameter applies to.

```
Domain ::= Ratio | Interval | Time
```

- **Ratio**: The parameter specifies a response count. Reinforcement is contingent upon emitting N responses. Response-dependent.
- **Interval**: The parameter specifies a time duration. Reinforcement is contingent upon the first response *after* the interval has elapsed. Both response-dependent and time-dependent (conjunctive).
- **Time**: The parameter specifies a time duration. Reinforcement is delivered when time elapses regardless of behavior. Response-independent (non-contingent).

The behavioral significance: Ratio schedules generate high, steady response rates with characteristic post-reinforcement pauses (Ferster & Skinner, 1957, Ch. 3-4). Interval schedules produce scalloped or break-and-run patterns insensitive to rate above a minimal threshold (Ferster & Skinner, 1957, Ch. 5-6). Time schedules maintain behavior through adventitious reinforcement (Skinner, 1948) or, under proper parameterization, approximate operant schedules (Schoenfeld & Cole, 1972).

**Definition 3 (Atomic Schedule).** An atomic schedule is the product type:

```
AtomicSchedule = Distribution × Domain × Value
```

where `Value ∈ ℝ⁺` (response count for Ratio; seconds for Interval/Time).

This yields the **3 × 3 grid**:

|              | Ratio    | Interval | Time     |
|--------------|----------|----------|----------|
| **Fixed**    | FR(*n*)  | FI(*t*)  | FT(*t*)  |
| **Variable** | VR(*n*)  | VI(*t*)  | VT(*t*)  |
| **Random**   | RR(*n*)  | RI(*t*)  | RT(*t*)  |

### 1.2 The Bit-Packed Encoding

The OperantKit framework (Mizutani, 2018) encodes this product type as a `UInt64` with `PrepositionSchedule` (Distribution) in the upper 16 bits and `PostpositionSchedule` (Domain) in the lower 16 bits. Query methods extract each dimension independently via bit-shifting:

```
hasFixedSchedule()    →  (rawValue << 32) >> 48 == Fixed
hasRatioSchedule()    →  (rawValue << 48) >> 48 == Ratio
```

This encoding is a *tagged product* that preserves the 2D queryability at the type level. The Python equivalent does not require bit-packing but must preserve this dimensional independence — an enum pair or frozen dataclass with `.distribution` and `.domain` properties serves the same purpose with better ergonomics.

### 1.3 Degenerate and Boundary Cases

**EXT (Extinction)** has `rawValue = 0` in the OperantKit encoding. It is the *zero element* of the schedule algebra: `EXT.is_satisfied()` always returns `false`. Formally:

```
EXT = AtomicSchedule(distribution = ⊥, domain = ⊥, value = 0)
```

The zero encoding is not accidental but reflects that extinction is the absence of reinforcement contingency — the additive identity of the schedule space.

**CRF (Continuous Reinforcement)** is `FR(1)` — the *identity element* for ratio schedules. The OperantKit source explicitly notes: "FR 1 と結果は同一" (results are identical to FR 1). Formally:

```
CRF ≡ FR(1) = AtomicSchedule(Fixed, Ratio, 1)
```

CRF is not a separate type but a named constant. Every response produces reinforcement; it is the lower bound of the ratio dimension.

### 1.4 Non-Grid Schedules

Certain schedules do not fit the 3 × 3 grid because they operate on different behavioral dimensions.

**Differential Reinforcement (DR) Schedules** are *constraint schedules* that gate reinforcement based on temporal properties of the response stream — specifically, inter-response time (IRT) — rather than response count or elapsed time.

```
DRConstraint ::= DRL(irt_min : ℝ⁺)       -- IRT ≥ threshold
               | DRH(irt_max : ℝ⁺)       -- IRT ≤ threshold
               | DRO(omission_time : ℝ⁺)  -- no response for duration
```

**Note on the name "DRO."** The abbreviation stands for "Differential Reinforcement of Other behavior," but this name is historically misleading. Component analyses demonstrate that DRO's effectiveness depends primarily on its *omission/extinction* contingency, not on reinforcing "other" behavior (Mazaleski et al., 1993; Rey et al., 2020; Hronek & Kestner, 2025). The current DSL represents fixed whole-interval DRO; Lindberg et al. (1999) 2×2 taxonomy is deferred to v1.x. See [design-rationale.md §1](../../../docs/en/design-rationale.md#1-dro-why-other-behavior-is-a-misnomer) for the full evidence review.

DR schedules sit orthogonally to the grid and are best understood as **filters** or **modifiers** that can be composed with grid schedules via tandem or conjunctive composition. For example, `Tand(VR 20, DRL 5-s)` requires a variable-ratio response count *and* an inter-response time ≥ 5 seconds.

**Standalone DR modifiers.** A DR modifier written without an enclosing combinator (e.g., `DRL 5-s` as a top-level schedule expression) is semantically equivalent to that modifier applied to an implicit CRF base schedule — i.e., `DRL 5-s` ≡ `Tand(CRF, DRL 5-s)`. This matches standard laboratory notation: "DRL 20-s" in the literature denotes a schedule in which every response satisfying the IRT criterion is reinforced (Ferster & Skinner, 1957, Ch. 8; Kramer & Rilling, 1970). The implicit CRF is a semantic default documented in [defaults.md](../../../schema/core/defaults.md); conforming parsers emit a `Modifier` AST node without desugaring.

**Note on DRA/DRI.** Differential Reinforcement of Alternative behavior (DRA) and Differential Reinforcement of Incompatible behavior (DRI) are clinical procedure labels commonly used in applied behavior analysis (Cooper, Heron, & Heward, 2020). Unlike DRO/DRL/DRH, which are single-operandum schedule modifiers defined by temporal parameters, DRA/DRI inherently specify contingencies across *two* response classes (extinction for the target behavior, reinforcement for the alternative). At the schedule level, DRA is expressible as a concurrent arrangement:

```
let dra = Conc(EXT, CRF)           -- or Conc(EXT, FR 1), Conc(EXT, VI 30-s), etc.
```

DRI is a special case of DRA where the alternative behavior is physically incompatible with the target; the schedule structure is identical. The distinction is topographical (which behavior is selected as the alternative), not procedural. Therefore, DRA/DRI are not DSL primitives but documented patterns using existing combinators. Clinical metadata (behavioral function, alternative behavior description) is delegated to the annotation layer (see [architecture.md §4.7](architecture.md)).

**Progressive Ratio (PR)** is a *meta-schedule*: a ratio schedule whose parameter itself changes according to a deterministic step function indexed by the number of reinforcements delivered.

```
PR(step : ℕ → ℕ) = FR(step(n)) where n increments after each reinforcement
```

PR is a *schedule functor* — it maps a step function to a sequence of FR schedules. The DSL offers two syntactic forms:

- **Shorthand:** `PR n` — arithmetic progression with step size *n* (Jarmolowicz & Lattal, 2010). `PR 5` expands to `PR(linear, start=5, increment=5)`, producing FR 5, FR 10, FR 15, ... This matches the notation proposed in *The Behavior Analyst* and is the natural form for educational and clinical contexts.
- **Explicit:** `PR(hodos)`, `PR(linear, start=1, increment=5)`, `PR(exponential)` — for full control over the step function. Bare `PR` without a number or parenthesized options is a parse error.

Arithmetic and geometric progressions produce qualitatively different response-rate functions, and no consensus default step function exists (Killeen et al., 2009; Stafford & Branch, 1998). See [design-rationale.md §2](../../../docs/en/design-rationale.md#2-progressive-ratio-why-the-step-function-is-required) for the evidence review, including why breakpoint ≠ Pmax (Lambert et al., 2026).

### 1.5 Mapping to Behavioral Theory

The 2D type system maps directly to canonical sources:

| Source | Coverage |
|--------|----------|
| Ferster & Skinner (1957) | FR, VR, FI, VI (Chapters 3-6); CRF, EXT as boundary conditions |
| Catania (2013) | Extends with Time (response-independent) dimension |
| Farmer (1963) | Formalizes Random schedules (RR, RI, RT) — constant-probability-per-unit assumption |
| Fleshler & Hoffman (1962) | Variable schedule value generation algorithm |
| Schoenfeld & Cole (1972) | T-tau system as an alternative coordinate system (see [representations.md](representations.md)) |

### 1.6 Limited Hold — Temporal Availability Constraint

**Definition.** A Limited Hold (LH) is a temporal constraint on reinforcement *availability* that is imposed on any inner schedule `S`. Once `S`'s criterion is first satisfied, a hold window of duration `d` seconds opens. If a response occurs within that window, reinforcement is delivered. If no response occurs before the window closes, the reinforcement opportunity is cancelled and `S` resets.

```
LH(d, S)
```

**State machine:**

```
WAITING
  │  S.is_satisfied(obs) → True  (records t_satisfied = obs.current_time)
  ▼
HOLD_OPEN
  │  response within d of t_satisfied  →  reinforce, S.next()  →  WAITING
  │  obs.current_time − t_satisfied > d, no response  →  cancel, S.next()  →  WAITING
```

**Algebraic properties:**
- `LH(∞, S) ≡ S` — infinite hold is the identity (no constraint). See §2.2.4.
- `LH(0, S) ≡ EXT` — zero hold makes reinforcement unavailable. See §2.2.4.
- LH is **not reducible to Conj**: `Conj(S, TimeWindow(d))` checks simultaneous satisfaction against the same observation (stateless). LH is state-dependent — it gates access based on a satisfaction event timestamp recorded across ticks.
- LH is **not a special case of T-tau**: T-tau duty cycles are fixed, clock-driven, and response-independent in their cycling. LH's window is triggered by `S`'s satisfaction event, not by a recurring timer. See [representations.md](representations.md) for the formal relationship.
- LH is a **congruent unary schedule transformer**: `LH : (ℝ⁺, Schedule) → Schedule`.

**Formal verification of LH's algebraic status.** LH(d, −) is a mapping from schedules to schedules. Its algebraic properties with respect to the semantic equivalence relation (§2.2.1) are:

*Property 1 (Congruence — HOLDS).* LH preserves semantic equivalence:

```
S₁ ≡ S₂  ⟹  LH(d, S₁) ≡ LH(d, S₂)
```

*Proof.* If S₁ ≡ S₂, they produce identical reinforcement outcomes for all observation traces (Definition 4, §2.2.1). For a schedule without an outer LH wrapper, the satisfaction event coincides with the reinforcement event. Therefore S₁ and S₂ satisfy at the same trace positions for any trace. Since LH's state machine transitions are determined entirely by the inner schedule's satisfaction events and the response stream, LH(d, S₁) and LH(d, S₂) undergo identical state transitions for any trace, producing identical outcomes. ∎

*Property 2 (Non-commutativity of nesting — composition law FAILS).* In general:

```
LH(d₂, LH(d₁, S)) ≢ LH(d₁, LH(d₂, S))
```

*Counterexample.* Consider `LH(10, LH(5, FI 30-s))` vs. `LH(5, LH(10, FI 30-s))`.

In `LH(10, LH(5, FI 30-s))`: FI 30 is satisfied at t₀. A first response must occur within 5 s of t₀ (inner LH). A second response must then occur within 10 s of the first response (outer LH). In `LH(5, LH(10, FI 30-s))`: FI 30 is satisfied at t₀. A first response must occur within 10 s of t₀ (inner LH). A second response must then occur within 5 s of the first response (outer LH). These impose different temporal constraints, so a trace exists that reinforces under one but not the other. ∎

*Consequence.* The original characterization of LH as an "endofunctor on the schedule algebra" is imprecise. LH(d, −) satisfies the congruence property (which corresponds to the identity-preservation functor law in the preorder category induced by ≡), but does NOT satisfy the composition-preservation functor law in any natural category structure on schedules. The correct characterization is: **LH(d, −) is a congruent unary schedule transformer** — it maps schedules to schedules and preserves semantic equivalence, but nested LH application is order-dependent.

**Semantics of nested LH.** `LH(d₂, LH(d₁, S))` is interpreted as follows:
1. The inner schedule `S` runs until its criterion is satisfied (at time `t₀`).
2. The inner LH opens a window of `d₁` seconds. A response must occur at some `t₁ ∈ [t₀, t₀ + d₁)` for the inner LH to be satisfied.
3. The outer LH then opens a window of `d₂` seconds from `t₁`. A second response must occur at some `t₂ ∈ [t₁, t₁ + d₂)` for reinforcement to be delivered.

This effectively requires **two sequential responses** within specified time windows — a tandem-like temporal constraint. The response that satisfies the inner LH is consumed as that layer's satisfaction event; it does not also satisfy the outer LH.

**Canonical scope:**
- Interval schedules (FI, VI): primary usage — Ferster & Skinner (1957, Ch. 5).
- Time schedules (FT, VT): converts response-independent delivery into a response-dependent window.
- DRL + LH: documented in Kramer & Rilling (1970) — response must occur after IRT ≥ t and before t + d.
- DRO + LH: used clinically — the hold window opens after the omission interval elapses.
- Ratio schedules (FR, VR, RR): semantically vacuous — the satisfying response *is* the response within the window; ratio schedules are satisfied on the response itself. The v1.0 parser emits a warning for `FR(n) LH(d)`.

**Position in the schedule taxonomy.** LH sits alongside DRL, DRH, and DRO as a **temporal eligibility modifier** — a constraint on *when* the response-reinforcer contingency holds. It is placed in the base grammar (not an annotation) because, like DRL, it directly determines the reinforcement function that quantitative models (matching law, behavioral momentum) depend on.

**References:**
- Ferster, C. B., & Skinner, B. F. (1957). *Schedules of reinforcement*. Appleton-Century-Crofts. (Ch. 5)
- Kramer, T. J., & Rilling, M. (1970). Differential reinforcement of low rates: A selective critique. *Psychological Bulletin*, *74*(4), 225–254. https://doi.org/10.1037/h0029813
- Nevin, J. A. (1974). Response strength in multiple schedules. *Journal of the Experimental Analysis of Behavior*, *21*(3), 389–408. https://doi.org/10.1901/jeab.1974.21-389

#### 1.6.1 LH Default Propagation — Attribute Grammar

The program-level `LH` parameter declaration (`LH = d`) specifies a default limited hold that propagates to eligible leaf schedule nodes. This subsection formalizes the propagation rules as an **attribute grammar** (Aho et al., 2006, §5.2), replacing the informal description "applies to all leaf base_schedules."

**Attributes.**

| Attribute | Kind | Type | Scope |
|---|---|---|---|
| `lh_default` | Synthesized | `Option<(ℝ⁺, Option<TimeUnit>)>` | `Program` node |
| `inherited_lh` | Inherited | `Option<(ℝ⁺, Option<TimeUnit>)>` | All `ScheduleExpr` nodes |
| `effective_lh` | Synthesized | `Option<(ℝ⁺, Option<TimeUnit>)>` | Leaf nodes |

- `lh_default`: extracted from `Program.param_decls`. Value is `⊥` if no `LH` declaration is present.
- `inherited_lh`: the LH default flowing top-down from the Program root through the AST.
- `effective_lh`: the LH that actually wraps a leaf node. If `≠ ⊥`, the semantic analyzer performs the transformation `leaf ↦ LH(effective_lh, leaf)`.

**Phase ordering.** LH propagation is a **semantic analysis** pass that operates on the **post-expansion** AST — after let-binding substitution and `Repeat` desugaring, but before warnings/linting. The pipeline:

```
Source → Lex → Parse → [Pre-expansion AST]
  → Binding expansion / Repeat desugaring → [Post-expansion AST]
  → LH default propagation (this AG) → [Resolved AST]
  → Warnings / Linting
```

This ordering resolves the pre/post-expansion phase ambiguity: LH propagation always operates on fully expanded ASTs, where no `IdentifierRef` or `Repeat` nodes remain.

**Propagation rules.** `⊥` denotes the absence of an LH value (no propagation).

```
R1  Program → param_decls bindings schedule
    schedule.inherited_lh = lookup("LH", param_decls)      -- ⊥ if absent

R2  Compound[C] → C(components[1..n])
    where C ∈ {Conc, Alt, Conj, Chain, Tand, Mult, Mix, Interpolate}
    ∀i ∈ [1..n]:
        components[i].inherited_lh = Compound.inherited_lh

R3  Overlay → Overlay(baseline, punisher)
    baseline.inherited_lh  = Overlay.inherited_lh
    punisher.inherited_lh  = ⊥

R4  LimitedHold → LH(d, inner)
    inner.inherited_lh = ⊥

R5  Leaf: node ∈ {Atomic, Special, Modifier, SecondOrder}
    node.effective_lh = node.inherited_lh
    action: if effective_lh ≠ ⊥ then node ↦ LH(effective_lh, node)

R6  AversiveSchedule → Sidman(...) | DiscrimAv(...)
    inherited_lh is discarded (no wrapping, no propagation)
```

**Summary by node type.**

| Node type | Behavior | Rule |
|---|---|---|
| `Compound` (Conc, Alt, Conj, Chain, Tand, Mult, Mix, Interpolate) | Pass `inherited_lh` to each component | R2 |
| `Overlay` | Pass to baseline; punisher gets `⊥` | R3 |
| `LimitedHold` | Block propagation (explicit overrides default) | R4 |
| `Atomic`, `Special`, `Modifier` (DRL, DRH, DRO, PR, Lag) | Wrap with LH if `inherited_lh ≠ ⊥` | R5 |
| `SecondOrder` | Wrap entire node as a unit; unit schedule is not individually propagated | R5 |
| `AversiveSchedule` (Sidman, DiscrimAv) | Discard `inherited_lh` | R6 |

**Rationale for key design decisions.**

*R3 — Overlay punisher isolation.* Program-level LH constrains reinforcement availability. The punishment contingency in an `Overlay` operates on a separate consequence class (aversive stimuli). Propagating a reinforcement-availability window to a punishment schedule would be procedurally incoherent.

*R4 — Explicit LH overrides default.* Expression-level LH overrides program-level LH, analogous to expression-level COD overriding program-level COD (§2.4). The explicit LH already provides the intended temporal constraint; propagating the default further would create unintended double-gating.

*R5 — SecondOrder as leaf.* In second-order schedules (e.g., `FR5(FI30)`), the unit schedule defines a derived response unit (Kelleher, 1966). The session-level LH constrains overall reinforcement delivery, not each unit's internal temporal dynamics. Propagating LH into the unit position would fundamentally alter the procedure — particularly in behavioral pharmacology, where the unit schedule's independent operation is often the experimental variable of interest (Goldberg & Kelleher, 1977). Wrapping the entire SecondOrder preserves the intended semantics: "once the second-order arrangement produces a reinforcement opportunity, you have *d* seconds to collect it."

*R6 — Aversive schedule isolation.* Sidman avoidance and discriminated avoidance have dedicated temporal parameters (SSI/RSI, CSUSInterval) that govern consequence timing. LH constrains *reinforcement availability*; these schedules deliver *aversive consequences* on procedurally distinct timelines (Sidman, 1953).

**Worked examples.**

*Example 1 — Basic propagation through Conc.*
```
Input:    LH = 10s
          Conc(VI 30s, VI 60s)
Resolved: Conc(VI 30s LH 10s, VI 60s LH 10s)
```
Trace: R1 → R2 (×2) → R5 (×2, wrap).

*Example 2 — Expression-level override.*
```
Input:    LH = 10s
          Conc(FR 5, VI 60s LH 20s)
Resolved: Conc(FR 5 LH 10s, VI 60s LH 20s)
```
Trace: R1 → R2 (×2). `FR 5`: R5 (wrap, + `VACUOUS_LH_RATIO` warning). `LH(20s, VI 60s)`: R4 (blocks propagation); explicit LH 20s retained.

*Example 3 — SecondOrder unit isolation.*
```
Input:    LH = 10s
          FR 5(FI 30s)
Resolved: FR 5(FI 30s) LH 10s
```
Trace: R1 → R5 (SecondOrder treated as leaf, wrap). The unit `FI 30s` is untouched; the LH window constrains when the subject can collect reinforcement after the 5th unit completion.

*Example 4 — Nested compound.*
```
Input:    LH = 10s
          Conc(Chain(FR 5, FI 30s), VI 60s)
Resolved: Conc(Chain(FR 5 LH 10s, FI 30s LH 10s), VI 60s LH 10s)
```
Trace: R1 → R2 → R2 (into Chain) → R5 (×3, wrap). Each leaf independently receives the default.

*Example 5 — Aversive schedule isolation.*
```
Input:    LH = 10s
          Sidman(SSI=20s, RSI=5s)
Resolved: Sidman(SSI=20s, RSI=5s)
```
Trace: R1 → R6 (`inherited_lh` discarded).

*Example 6 — No LH param_decl (identity).*
```
Input:    Conc(VI 30s, VI 60s)
Resolved: Conc(VI 30s, VI 60s)
```
Trace: R1 (`lh_default = ⊥`). No propagation occurs.

**Conformance test suite.** `conformance/core/lh_propagation.json` provides test vectors for all propagation rules. Each test specifies both the parser output (`expected`, pre-propagation) and the resolved AST (`resolved`, post-propagation).

**References.**
- Aho, A. V., Lam, M. S., Sethi, R., & Ullman, J. D. (2006). *Compilers: Principles, Techniques, and Tools* (2nd ed.). Addison-Wesley. (§5.2: Inherited Attributes)
- Goldberg, S. R., & Kelleher, R. T. (1977). Reinforcement of behavior by cocaine injections. In E. H. Ellinwood & M. M. Kilbey (Eds.), *Cocaine and other stimulants* (pp. 523–544). Plenum Press.
- Kelleher, R. T. (1966). Conditioned reinforcement in second-order schedules. *Journal of the Experimental Analysis of Behavior*, *9*(5), 475–485. https://doi.org/10.1901/jeab.1966.9-475
- Sidman, M. (1953). Two temporal parameters of the maintenance of avoidance behavior by the white rat. *Journal of Comparative and Physiological Psychology*, *46*(4), 253–261. https://doi.org/10.1037/h0060730

### 1.7 Reinforcement Delay — Response-Consequence Temporal Interval

**The problem.** The temporal interval between the response that satisfies a schedule requirement and the delivery of the consequence is a fundamental parameter of any contingency. Even brief delays — including feeder actuation time (≈0.5 s in standard operant chambers) — systematically modulate response patterns and can be confounded with schedule effects if not controlled (Lattal, 2010). This parameter must be expressible in the DSL.

**Per-schedule delay is a tandem arrangement.** In the delay-of-reinforcement literature, a delay imposed on a specific schedule is operationalized as a tandem FT requirement. Sizemore and Lattal (1978) described their procedure as: "responses on the VI 60-s schedule were followed by a tandem FT *t*-s requirement before reinforcer delivery." This is directly expressible in the DSL using existing combinators:

| Delay type | DSL expression | Semantics | Reference |
|---|---|---|---|
| Nonresetting, unsignaled | `Tand(VI 60-s, FT 5-s)` | After VI satisfaction, wait 5 s regardless of responses | Sizemore & Lattal (1978) |
| Resetting, unsignaled | `Tand(VI 60-s, DRO 5-s)` | After VI satisfaction, wait 5 s; responses restart the timer | Lattal (2010) |
| Signaled | `Chain(VI 60-s, FT 5-s)` | After VI, discriminative stimulus changes; food after 5 s | Richards (1981) |
| Differential (concurrent) | `Conc(Tand(VI 60-s, FT 1-s), Tand(VI 60-s, FT 8-s), COD=2-s)` | Each alternative has its own delay | Chung & Herrnstein (1967) |
| Adjusting (choice) | `Adj(delay, start=10-s, step=1-s)` | Delay adjusts per trial (Core-Stateful) | Mazur (1987) |

No new expression-level primitive is needed: `Tand(S, FT d)` is the established formalization of per-schedule reinforcement delay, and the DSL already supports it.

**Session-wide apparatus delay.** The remaining gap is the common case where *all* reinforcement events in a session share the same apparatus-imposed latency. This is expressed via a program-level `param_decl`:

```
RD = 500ms
VI 60-s
```

The `RD` param_decl instructs the runtime to impose a uniform delay between any schedule satisfaction event and consequence delivery. It has no expression-level syntax — when per-schedule specificity is needed, the user writes an explicit `Tand(S, FT d)`.

**Properties:**
- `RD = 0s` is legal (explicit immediate delivery).
- Time unit is mandatory (delay is intrinsically temporal).
- `RD > 30s` triggers a linter warning (most published research uses delays ≤ 30 s).
- `RD` does not specify signaling, resetting, or response-handling during the delay — those procedural details are properties of the `Tand`/`Chain`/`DRO` arrangement or runtime configuration.

**Position in the grammar.** `RD` is a `param_decl` keyword (alongside `LH`, `COD`, `FRCO`, `BO`), not a schedule expression modifier. This reflects the literature: Lattal (2010) reviews delay as a *procedural parameter* that applies to the session arrangement, while per-schedule delays are tandem schedule structures that belong in the schedule expression itself.

**References:**
- Lattal, K. A. (2010). Delayed reinforcement of operant behavior. *Journal of the Experimental Analysis of Behavior*, *93*(1), 129–139. https://doi.org/10.1901/jeab.2010.93-129
- Sizemore, O. J., & Lattal, K. A. (1978). Unsignalled delay of reinforcement in variable-interval schedules. *Journal of the Experimental Analysis of Behavior*, *30*(2), 169–175. https://doi.org/10.1901/jeab.1978.30-169
- Richards, R. W. (1981). A comparison of signaled and unsignaled delay of reinforcement. *Journal of the Experimental Analysis of Behavior*, *35*(2), 145–152. https://doi.org/10.1901/jeab.1981.35-145
- Chung, S.-H., & Herrnstein, R. J. (1967). Choice and delay of reinforcement. *Journal of the Experimental Analysis of Behavior*, *10*(1), 67–74. https://doi.org/10.1901/jeab.1967.10-67
- Renner, K. E. (1964). Delay of reinforcement: A historical review. *Psychological Bulletin*, *61*(5), 341–361. https://doi.org/10.1037/h0048335

---

## Part II: Composition Algebra — Compound Schedule Combinators

### 2.1 Classifying Combinators

The compound schedules form a structured algebra over atomic schedules. We classify them along three independent semantic dimensions:

**Dimension A: Topology** — How components relate in time.
- *Parallel*: Components operate simultaneously.
- *Sequential*: Components operate in fixed order; completing one transitions to the next.
- *Alternating*: Components alternate, with transitions controlled by the environment.

**Dimension B: Discriminability** — Whether discriminative stimuli (S^D) signal transitions.
- *Discriminated*: Each component is paired with a distinct S^D.
- *Undiscriminated*: No S^D change signals transitions.

**Dimension C: Satisfaction Logic** — How component satisfaction relates to reinforcement.
- *OR (Disjunctive)*: Any one component satisfied triggers reinforcement.
- *AND (Conjunctive)*: All components must be simultaneously satisfied.
- *Independent*: Each component maintains its own reinforcement contingency.
- *Sequential*: Completion of one component is prerequisite for the next.
- *Context-switched*: Only the currently-active component's contingency applies.

This yields the complete classification:

| Schedule | Abbreviation | Topology | Discriminability | Logic | Operanda |
|----------|-------------|----------|-----------------|-------|----------|
| Concurrent | Conc | Parallel | N/A (separate) | Independent | Multiple |
| Alternative | Alt | Parallel | N/A | OR | Single |
| Conjunctive | Conj | Parallel | N/A | AND | Single |
| Chained | Chain | Sequential | Discriminated | Sequential | Single |
| Tandem | Tand | Sequential | Undiscriminated | Sequential | Single |
| Multiple | Mult | Alternating | Discriminated | Context-switched | Single |
| Mixed | Mix | Alternating | Undiscriminated | Context-switched | Single |

A structural observation: **Chain and Tand** form a discriminated/undiscriminated pair under sequential topology. **Mult and Mix** form the same pair under alternating topology. This suggests higher-level abstractions:

```
Sequential(components, discriminated: bool)
  discriminated = true   → Chain
  discriminated = false  → Tand

Alternating(components, discriminated: bool)
  discriminated = true   → Mult
  discriminated = false  → Mix
```

### 2.2 Algebraic Properties

#### 2.2.1 Equivalence Relations — Definitions

This specification uses three distinct relations on schedule expressions. All algebraic claims in this section and throughout the specification are stated under these definitions.

**Definition 1 (Syntactic equality).** Two schedule expressions `S₁` and `S₂` are *syntactically equal*, written `S₁ =_syn S₂`, if and only if their AST representations are structurally identical — i.e., every node type, combinator, parameter value, and child ordering is the same. Syntactic equality is decidable by recursive structural comparison.

**Definition 2 (Observation trace).** An *observation trace* is a finite sequence of timestamped events `τ = ⟨(e₁, t₁), (e₂, t₂), …, (eₙ, tₙ)⟩` where each `eᵢ` is either a response event or a time-tick event and `t₁ ≤ t₂ ≤ … ≤ tₙ`. Let `T` denote the set of all finite observation traces.

**Definition 3 (Reinforcement outcome sequence).** Given a schedule expression `S` and an observation trace `τ ∈ T`, the *reinforcement outcome sequence* `outcome(S, τ)` is the sequence of reinforcement decisions (reinforced / not reinforced) that `S` produces when processing `τ` from a canonical initial state `σ₀`. The canonical initial state has all counters at zero, all timers at zero, and an empty reinforcement history.

**Definition 4 (Semantic equivalence, ≡).** Two schedule expressions `S₁` and `S₂` are *semantically equivalent*, written `S₁ ≡ S₂`, if and only if they produce identical reinforcement outcome sequences for every possible observation trace:

```
S₁ ≡ S₂  ⟺  ∀τ ∈ T. outcome(S₁, τ) = outcome(S₂, τ)
```

Informally: no observer can distinguish `S₁` from `S₂` by examining reinforcement outcomes alone, regardless of the subject's behavior. Semantic equivalence is an equivalence relation (reflexive, symmetric, transitive). The negation is written `≢`.

**Definition 5 (Sound rewrite rule, →).** A *sound rewrite rule* `S₁ → S₂` is a directed AST transformation such that `S₁ ≡ S₂`. Rewrite rules are applied left-to-right; a conforming implementation MAY apply any sound rewrite rule as an optimization pass but MUST NOT apply unsound rewrites. The notation `S₁ ≡ S₂` implies both `S₁ → S₂` and `S₂ → S₁` are sound.

**Notation convention.** Throughout this specification:
- `≡` and `≢` denote semantic equivalence and its negation (Definition 4).
- `=` is used only in mathematical prose (e.g., `n + 1 = m`) or in informal glosses where the context makes the intended relation unambiguous.
- `=_syn` denotes syntactic equality when the distinction matters (Definition 1).

#### 2.2.2 Fundamental Theorems

**Theorem 1 (Commutativity).**
- `Conc(A, B) ≡ Conc(B, A)` — operandum assignment is arbitrary (modulo labeling).
- `Alt(A, B) ≡ Alt(B, A)` — disjunction is commutative.
- `Conj(A, B) ≡ Conj(B, A)` — conjunction is commutative.
- `Chain(A, B) ≢ Chain(B, A)` — sequential order matters.
- `Tand(A, B) ≢ Tand(B, A)` — sequential order matters.
- `Mult(A, B) ≢ Mult(B, A)` — alternation order matters.
- `Mix(A, B) ≢ Mix(B, A)` — alternation order matters.

*Proof sketch (commutativity of Alt).* For any trace `τ`, `outcome(Alt(A, B), τ)` reinforces at step `i` iff `A` or `B` would reinforce at step `i`. Since disjunction is commutative, `outcome(Alt(A, B), τ) = outcome(Alt(B, A), τ)`. ∎

*Counterexample (non-commutativity of Chain).* Consider `Chain(FR 1, FI 10-s)` vs. `Chain(FI 10-s, FR 1)`. In the first, a single response completes the FR link and transitions to the FI link. In the second, 10 seconds must elapse first. The trace `τ = ⟨(response, t=0)⟩` reinforces under neither, but `τ' = ⟨(response, t=0), (response, t=11)⟩` reinforces under the first but not the second (which requires the FI to be satisfied first, then one more response). ∎

**Theorem 2 (Associativity).** All seven combinators are associative in the sense that they flatten to N-ary compositions:
- `Conc(A, Conc(B, C)) ≡ Conc(A, B, C)`
- `Alt(A, Alt(B, C)) ≡ Alt(A, B, C)`
- `Conj(A, Conj(B, C)) ≡ Conj(A, B, C)`
- `Chain(A, Chain(B, C)) ≡ Chain(A, B, C)`
- `Tand(A, Tand(B, C)) ≡ Tand(A, B, C)`
- `Mult(A, Mult(B, C)) ≡ Mult(A, B, C)`
- `Mix(A, Mix(B, C)) ≡ Mix(A, B, C)`

**Theorem 3 (Identity Elements).**
- `Alt(S, EXT) ≡ S` — EXT is the identity for Alt (never-satisfied OR'd with S is just S).
- `Conj(S, CRF) ≡ S` — CRF (always satisfied on first response) is the identity for Conj.
- `Chain(CRF, S) ≡ S` — CRF as initial link is immediately satisfied.

**Theorem 4 (Annihilator Elements).**
- `Conj(S, EXT) ≡ EXT` — if EXT is never satisfied, the conjunction can never be satisfied.
- `Alt(S, CRF) ≡ CRF` — CRF is always satisfied first.

**Theorem 5 (Non-distributivity).** In general, compound schedule composition does NOT distribute:

```
Alt(A, Conj(B, C)) ≢ Conj(Alt(A, B), Alt(A, C))
```

This is semantically significant: parenthesization determines contingency structure and must be explicit in the DSL.

#### 2.2.3 Repeat Algebraic Properties

`Repeat(n, S)` is defined as syntactic sugar for `Tand(S, S, …, S)` with `n` copies of `S` (§1.4). The following properties are derived from the Tand desugaring and the semantic equivalence definition above.

**Theorem 6 (Repeat identity).**
```
Repeat(1, S) ≡ S
```
*Proof.* `Repeat(1, S)` desugars to `Tand(S)`, a unary tandem, which is semantically equivalent to `S` itself (a single-component sequential composition is the component). ∎

**Theorem 7 (Repeat exponent rule).**
```
Repeat(m, Repeat(n, S)) ≡ Repeat(m × n, S)
```
*Proof.* The left-hand side desugars to `m` copies of `Tand(S, …, S)` [each with `n` copies], concatenated as a tandem. By associativity of Tand (Theorem 2), this flattens to `Tand(S, …, S)` with `m × n` copies, which is `Repeat(m × n, S)`. ∎

**Theorem 8 (Repeat additive decomposition).**
```
Repeat(m + n, S) ≡ Tand(Repeat(m, S), Repeat(n, S))
```
*Proof.* Both sides desugar to `Tand(S, …, S)` with `m + n` copies by associativity of Tand. ∎

**Completeness as syntactic sugar.** `Repeat(n, S)` always expands to a finite `Tand`, so `Repeat` introduces no new semantic primitives. The meaning of any `Repeat` expression is fully determined by the `Tand` semantics.

#### 2.2.4 LH Boundary Identities

From the LH definition (§1.6):

- `LH(∞, S) ≡ S` — infinite hold imposes no temporal constraint.
- `LH(0, S) ≡ EXT` — zero hold makes reinforcement unavailable (the hold window closes before any response can occur).

#### 2.2.5 Sound Rewrite Rules (Summary)

The following table collects all sound rewrite rules derived from Theorems 1–8 and §1.6. A conforming implementation MAY apply these as optimization passes. The `Direction` column indicates whether the rule is applied left-to-right only (→) or is bidirectional (↔, i.e., full semantic equivalence).

| # | Rule | Direction | Priority | Theorem |
|---|------|-----------|----------|---------|
| R1 | `Alt(S, EXT) → S` | → | 1 | Thm 3 |
| R2 | `Alt(EXT, S) → S` | → | 1 | Thm 1 + Thm 3 |
| R3 | `Conj(S, CRF) → S` | → | 1 | Thm 3 |
| R4 | `Conj(CRF, S) → S` | → | 1 | Thm 1 + Thm 3 |
| R5 | `Chain(CRF, S) → S` | → | 1 | Thm 3 |
| R6 | `Conj(S, EXT) → EXT` | → | 2 | Thm 4 |
| R7 | `Conj(EXT, S) → EXT` | → | 2 | Thm 1 + Thm 4 |
| R8 | `Alt(S, CRF) → CRF` | → | 2 | Thm 4 |
| R9 | `Alt(CRF, S) → CRF` | → | 2 | Thm 1 + Thm 4 |
| R10 | `Repeat(1, S) → S` | → | 3 | Thm 6 |
| R11 | `LH(∞, S) → S` | → | 3 | §1.6 |
| R12 | `LH(0, S) → EXT` | → | 3 | §1.6 |
| R13 | `Conc(A, Conc(B, C)) ↔ Conc(A, B, C)` | ↔ | 4 | Thm 2 |
| R14 | `Alt(A, Alt(B, C)) ↔ Alt(A, B, C)` | ↔ | 4 | Thm 2 |
| R15 | `Conj(A, Conj(B, C)) ↔ Conj(A, B, C)` | ↔ | 4 | Thm 2 |
| R16 | `Chain(A, Chain(B, C)) ↔ Chain(A, B, C)` | ↔ | 4 | Thm 2 |
| R17 | `Tand(A, Tand(B, C)) ↔ Tand(A, B, C)` | ↔ | 4 | Thm 2 |

**Priority** indicates the recommended application order when multiple rules match. Lower numbers are applied first. Rules R1–R12 are *simplifying* (the right-hand side has fewer AST nodes); R13–R17 are *structural* (flattening nested compositions).

### 2.3 Recursive Composition

The type system supports arbitrarily nested compositions:

```
Schedule = AtomicSchedule | CompoundSchedule | ModifierSchedule
CompoundSchedule = Combinator(Schedule, Schedule, ...)
```

This is a standard recursive algebraic data type (ADT). For example:

```
Conc(Chain(FR 5, VI 60-s), Alt(FR 10, FT 30-s))
```

is a concurrent schedule where operandum 1 presents a chained FR5-then-VI 60, and operandum 2 presents an alternative FR10-or-FT 30.

### 2.4 Changeover Delay (COD) and Fixed-Ratio Changeover (FRCO)

The Changeover Delay (COD) specifies a minimum time after an operandum switch before reinforcement becomes available on the new operandum (Catania, 1966). COD is a **definitional parameter** of `Conc`, not optional metadata:

- Without COD, a concurrent schedule is procedurally underspecified (Herrnstein, 1961). The DSL emits a linter WARNING (`MISSING_COD`) recommending explicit COD specification; the runtime default is `COD=0-s`.
- `COD=0-s` is legal (explicit no-delay), matching Shull & Pliskoff (1967), but parsers SHOULD emit a lint warning for VI-VI arrangements.

```
Conc(VI 30-s, VI 60-s, COD=2-s)           -- 2-s changeover delay
Conc(VI 30-s, VI 60-s, COD=0-s)           -- explicit no-delay (control condition)
```

**Default behavior:** Symmetric (same delay regardless of switch direction), non-resetting (switching again during active COD does not restart the timer).

**Fixed-Ratio Changeover (FRCO):** A response-based alternative to time-based COD. FRCO requires N responses on the new operandum before reinforcement becomes available (Hunter & Davison, 1985; Pliskoff & Fetterman, 1981). FRCO and COD may coexist:

```
Conc(VI 30-s, VI 60-s, FRCO=5)            -- 5 responses required after switch
Conc(VI 30-s, VI 60-s, COD=2-s, FRCO=5)   -- both time and response requirements
```

| Parameter | Alias | Dimension | Reference |
|-----------|-------|-----------|-----------|
| COD | ChangeoverDelay | Time (s/ms/min) | Herrnstein (1961); Catania (1966) |
| FRCO | FixedRatioChangeover | Responses (dimensionless) | Hunter & Davison (1985) |

**Terminology note.** Earlier drafts used the abbreviation `COR` (Changeover Response). The established literature abbreviation is **FRCO**, introduced by Hunter & Davison (1985). Pliskoff & Fetterman (1981) used the descriptive term "changeover requirement" without a fixed abbreviation.

Both COD and FRCO support program-level defaults via `param_decl` (analogous to `LH = 10-s`):

```
COD = 2-s                              -- applies to all Conc in this program
Conc(VI 30-s, VI 60-s)                    -- inherits COD=2-s
Conc(VI 30-s, VI 60-s, COD=5-s)           -- expression-level overrides program-level
```

**Directional COD.** When changeover costs differ by switch direction, COD accepts a directional form specifying the (from, to) component pair and the delay for that transition (Pliskoff, 1971; Williams & Bell, 1999). Direction references may use 1-indexed integers or `let`-bound identifiers:

```
-- Fully explicit directional (index-based)
Conc(VI 30-s, VI 60-s, COD(1->2)=2-s, COD(2->1)=5-s)

-- Base + override: "COD was 2s, except from VR 20 it was 5s"
Conc(VI 30-s, VR 20, COD=2-s, COD(2->1)=5-s)

-- With let-bound labels (self-documenting)
let interval = VI 30-s
let ratio    = VR 20
Conc(interval, ratio, COD(interval->ratio)=1-s, COD(ratio->interval)=3-s)
```

**Base + override semantics.** Scalar `COD=Xs` provides a base delay for all unspecified directions. Directional entries `COD(x->y)=Ys` override specific transitions. This maps to the common JEAB Method section phrasing: "The COD was 2 s, except for switches from the VR 20 schedule, where it was 5 s."

Semantic rules for directional COD:
- `dir_ref` as integer must be in range [1, N]. As identifier, must resolve to a `let`-bound component name.
- Self-referencing direction (`COD(1->1)`) → `DIRECTIONAL_SELF_REFERENCE`.
- Duplicate direction pair → `DUPLICATE_DIRECTIONAL_KW`.
- Directional form valid for COD on Conc only; other keyword args → `INVALID_DIRECTIONAL_KW`.
- Program-level `param_decl` accepts scalar COD only (symmetric base). Expression-level directional COD overrides specific directions.
- Per-value validation: same rules as scalar COD (time unit required, ≥ 0).

**Future (v1.2):** Resetting COD (timer restarts on re-switch during active COD).

### 2.5 Blackout (BO)

The Blackout (BO) specifies a response-independent dark period inserted between component transitions in **Multiple** and **Mixed** schedules. Unlike COD (which is response-contingent and Conc-specific), BO is not contingent on any response and serves as a methodological control for inter-component behavioral independence.

**Design rationale.** BO directly affects behavioral contrast (Reynolds, 1961): longer BO periods reduce inter-component interaction, producing cleaner discrimination between components. From an associative learning perspective, BO duration determines whether prior-component stimulus representations decay sufficiently to prevent generalization across components (Bouton, 2004; Wagner, 1981). This makes BO a **structural parameter of Mult/Mix**, not mere session metadata — structurally symmetric with COD's role in Conc.

```
Mult(FR 5, EXT, BO=5-s)               -- 5-s blackout between components
Mix(VI 30-s, VI 60-s, BO=3-s)            -- 3-s blackout (undiscriminated)
Mult(FR 5, EXT)                       -- no blackout (immediate transition)
```

**Default behavior:** BO is optional (unlike COD). Omission or `BO=0-s` means immediate component transition with no blackout period. Symmetric (same duration for all transitions).

**Future (v1.2):** Asymmetric BO (different values per transition direction, e.g., Rich→Lean vs. Lean→Rich). To be designed in conjunction with asymmetric COD (Issue #25).

**Relationship to Timeout (TO).** BO is response-independent; TO is response-contingent. TO functions as negative punishment (removal of positive reinforcement contingent on a response) and is deferred to v2.0 as a modifier. See Issue #28 for the full operational distinction and COD/TO/DRO structural relationship.

### 2.6 Choice Behavior and the Procedure–Effect Boundary

A concurrent VR-VR schedule produces qualitatively different choice behavior from a concurrent VI-VI schedule. Under concurrent VI-VI, organisms typically allocate responses in proportion to the relative reinforcement rate — the **matching law** (Herrnstein, 1961). Under concurrent VR-VR, organisms tend to allocate nearly all responses to the richer alternative — **exclusive choice** (Herrnstein & Loveland, 1975; Baum, Aparicio, & Alonso-Alvarez, 2022).

**Design decision.** The DSL does **not** encode this distinction. `Conc` remains a single, generic combinator regardless of the component schedule types. This is deliberate and reflects a fundamental architectural principle:

> **The DSL specifies the procedure — what the experimenter arranges. It does not predict the effect — what the organism does.**

The rationale:

1. **Procedural completeness.** `Conc(VR 20, VR 40, COD=2-s)` fully specifies the operative contingency: two ratio schedules, simultaneously available, with a 2-second changeover delay. No additional parameter is needed to make this a well-formed procedure.

2. **Empirical contingency of the effect.** Whether exclusive choice actually occurs depends on parameters that the DSL already captures (ratio values, COD, FRCO) as well as factors outside the DSL's scope (training history, session duration, species). Baking `choice_mode = "exclusive"` into the DSL would assert an empirical generalization as if it were a logical entailment of the procedure. It is not.

3. **Mechanistic derivability.** The VI-VI / VR-VR difference arises from the molecular contingency structure: VI schedules differentially reinforce longer inter-response times (IRTs), while VR schedules reinforce independently of IRT. This makes switching profitable under VI (uncollected reinforcers accumulate on the unattended alternative) but not under VR. Since the component schedule types are already encoded in the DSL expression, a downstream analysis layer can derive the expected choice pattern without redundant annotation.

**Where choice analysis belongs.** Choice allocation, exclusive-choice detection, and choice-mode classification are the responsibility of the **session-analyzer** layer, which operates on observed behavioral data:

| Concept | Layer | Rationale |
|---------|-------|-----------|
| Schedule structure (`Conc(VR 20, VR 40, COD=2-s)`) | DSL | Procedural specification |
| Reinforcement gating (COD suppression, ratio counting) | Runtime (`contingency-py`) | Contingency enforcement |
| Choice allocation, matching parameters, exclusive-choice detection | session-analyzer | Behavioral measurement and classification |

This three-layer separation ensures that the DSL remains a precise notation for contingencies, the runtime faithfully implements those contingencies, and the analyzer characterizes behavioral outcomes without contaminating the procedural specification.

### 2.7 Aversive Schedules — Sidman Free-Operant Avoidance

The reinforcement schedule matrix (dist × domain = F/V/R × R/I/T) captures
the vast majority of positive reinforcement procedures. However, a class of
aversive control procedures — most prominently **Sidman (1953) free-operant
avoidance** — has a contingency structure that does not fit this matrix:
two temporal parameters with distinct semantics, and a response-contingent
rescheduling rule that differs from ratio / interval / time schedules.

The DSL therefore introduces a dedicated primitive, `Sidman`, in the
`aversive_schedule` production (grammar.ebnf). This is an additive Core
extension under design-philosophy §8.1.

**Procedural definition.** Two temporal parameters:

- **SSI (Shock-Shock Interval)**: baseline time between shocks in the absence
  of any response.
- **RSI (Response-Shock Interval)**: postponement time triggered by each response.

The next shock time is computed as:

```
next_shock(t) = max(last_shock_time + SSI, last_response_time + RSI)
```

In the absence of responses, shocks occur every SSI seconds. Each response
resets the next shock to occur at `last_response + RSI`, i.e., at least RSI
seconds from the response. When RSI ≤ SSI, responses can successfully
postpone shocks.

**Syntax.**

```
Sidman(SSI=20-s, RSI=5-s)                             -- primary form
SidmanAvoidance(SSI=20-s, RSI=5-s)                    -- verbose alias
Sidman(ShockShockInterval=20-s, ResponseShockInterval=5-s)  -- verbose params
```

Both parameters are required; there is no default. Time units are mandatory.

**Composition with other schedules.** `Sidman` is a `base_schedule` and may
appear inside any compound combinator:

```
Chain(FR 10 @punisher("food"), Sidman(SSI=20-s, RSI=5-s) @punisher("shock"))
```

This is a chained schedule in which completing an FR 10 for food transitions
the subject into a free-operant avoidance component (de Waard, Galizio, &
Baron, 1979).

**Semantic constraints.**

- Both `SSI` and `RSI` must be specified. Missing either → `MISSING_SIDMAN_PARAM`.
- Both must carry a time unit. Dimensionless values → `SIDMAN_TIME_UNIT_REQUIRED`.
- Both must be strictly positive. Non-positive → `SIDMAN_NONPOSITIVE_PARAM`.
- `RSI > SSI` triggers a linter WARNING `RSI_EXCEEDS_SSI`: when RSI exceeds
  SSI, responses cannot actually postpone shocks below the SSI baseline
  (Sidman, 1953; Hineline, 1977).

**Stimulus annotation.** Sidman procedures are aversive by definition. The
recommended practice is to use `@punisher` to make the experimenter's intent
explicit in source, though `@reinforcer` is accepted as an equivalent alias
(see annotation-design.md §3.5):

```
Sidman(SSI=20-s, RSI=5-s) @punisher("shock", intensity="0.5mA")
Sidman(SSI=20-s, RSI=5-s) @reinforcer("shock", intensity="0.5mA")  -- equivalent
```

**Scope of v1.x aversive schedules.** The `aversive_schedule` production is
additive. v1.x includes `Sidman` (free-operant avoidance) and
`DiscriminatedAvoidance` (trial-based avoidance). Punishment overlay is
expressed via the `Overlay` combinator (§2.10). Simple escape (response
terminates ongoing aversive stimulus without a predictive CS) can be
approximated with existing constructs using stimulus annotations.

### 2.8 Lag Schedule — Operant Variability

The differential reinforcement modifiers DRL, DRH, and DRO all operate on a
**temporal** dimension (inter-response time). A different kind of
differential reinforcement operates on **response variability** itself:
**Page & Neuringer (1985)** introduced the **Lag schedule**, in which a
response (or response sequence) is reinforced only if it differs from each
of the previous *n* responses. This demonstrated that variability is itself
an operant dimension — a behavioral property that can be strengthened by
contingent reinforcement like any other dimension.

The DSL introduces `Lag` as a differential reinforcement modifier in the
`modifier` production (grammar.ebnf), alongside DRL/DRH/DRO/PR/Repeat. This
is an additive Core extension under design-philosophy §8.1.

**Procedural definition.**

- **n**: the number of previous responses/sequences to compare against.
  `Lag 1` reinforces if the current response differs from the immediately
  previous one. `Lag 5` reinforces if it differs from each of the previous 5.
- **length** (optional, default = 1): the size of the response unit.
  `length=1` treats each individual response as the unit (the applied
  research default). `length=8` treats each 8-response sequence as the unit
  (Page & Neuringer, 1985 used this for 2-key 8-peck sequences).

Formally, let S(t) be the response unit at time t. Reinforcement is
delivered if and only if:

```
S(t) ∉ { S(t-1), S(t-2), ..., S(t-n) }
```

**Syntax.**

```
Lag 5                       -- shorthand, matches literature "Lag 5" notation;
                               length defaults to 1 (individual response unit)
Lag(5)                      -- parenthesized equivalent of Lag 5
Lag(5, length=8)            -- Page & Neuringer (1985) style 8-peck sequence
Lag(50, length=8)           -- Page & Neuringer (1985) Experiment 3 high Lag
```

The parameter `n` is positional to match the literature notation ("Lag 5",
"Lag 10"). The optional keyword argument `length` is the response-unit size.

**Semantic constraints.**

- `n` must be a non-negative integer. `Lag 0` is legal and is semantically
  equivalent to CRF (no variability requirement).
- `n` must NOT carry a time unit. `Lag 5s` → `LAG_UNEXPECTED_TIME_UNIT`.
  Lag is categorical / sequence-based; no established variant uses a time
  dimension (see `ShockShockInterval` for time-based reinforcement via
  aversive-schedule primitives, or DRL/DRH for time-based differential
  reinforcement).
- `length`, if specified, must be a positive integer (>= 1). Omission
  implies `length = 1`.
- Large `n` (> 50) triggers a linter WARNING `LAG_LARGE_N`. Historical
  research uses n <= 50.

**Stimulus annotation.** Lag works with `@reinforcer` like any other
schedule:

```
Lag(5, length=8)
  @reinforcer("grain")
  @operandum("left_key") @operandum("right_key")
```

**Composition.** Lag is a modifier and may appear inside any compound
combinator. A common pattern is to use `Mult` to alternate variability
training with a CRF baseline:

```
Mult(Lag(5, length=8), CRF)
```

**Historical notes.**

- The primary research unit in Page & Neuringer (1985) is the
  **response sequence**; `length = 1` (individual response) is formally a
  degenerate sequence and corresponds to applied research use cases (mand
  and tact variability training; Miller & Neuringer, 2000; Lee, McComas, &
  Jawor, 2002; Rodriguez et al., 2011).
- There is no established Lag schedule variant that uses a time dimension.
  Time-based variability research uses different procedures: response
  duration differential reinforcement (Platt, 1973), IRT distributions via
  percentile schedules (Alleman & Platt, 1973), or DRD.
- `Lag 0` ≡ CRF is a boundary case preserved for consistency. It declares
  the user's intent ("this is a Lag schedule with no variability
  requirement") rather than being optimized away at parse time.

**Why `length` is explicit.** The literature shows no standard sequence length (Page & Neuringer, 1985: 8; Ribeiro et al., 2022: 5; applied research: 1). The DSL exposes `length` because no single default is universally appropriate. Whether variability constitutes a true operant dimension remains debated (Nergaard & Holth, 2020 vs. Reed, 2023); the DSL takes no position. See [design-rationale.md §3](../../../docs/en/design-rationale.md#3-lag-why-length-is-explicit-and-the-operant-dimension-debate) for the full discussion.

### 2.9 Discriminated Avoidance

Sidman free-operant avoidance (§2.7) has no warning signal — shocks occur
on a temporal cycle that the organism can only postpone. **Discriminated
avoidance** (Solomon & Wynne, 1953) introduces a conditioned stimulus (CS)
that predicts the unconditioned stimulus (US). A response during the CS
prevents the US (avoidance trial); failure to respond results in US delivery
(escape or failure trial).

The two paradigms represent distinct contingency structures:
- **Sidman (free-operant):** no CS, response postpones the next US by RSI.
- **Discriminated (trial-based):** CS predicts US at a fixed CSUSInterval;
  response during the CS cancels the US.

The DSL introduces `DiscriminatedAvoidance` (alias `DiscrimAv`) as a second
aversive-schedule primitive in the `aversive_schedule` production.

**Procedural definition.**

- **CSUSInterval** (required): time from CS onset to US onset. If the
  subject responds before this interval elapses, the US is cancelled
  (avoidance trial).
- **ITI** (required): inter-trial interval, measured CS-onset to
  next-CS-onset. Must be > CSUSInterval.
- **mode** (required): `fixed` or `escape`.
  - `fixed`: US is presented for a fixed `ShockDuration`.
  - `escape`: US continues until the subject responds. Optional `MaxShock`
    sets a safety cutoff.
- **ShockDuration** (required for mode=fixed): duration of the fixed US.
- **MaxShock** (optional for mode=escape): safety cutoff for escape-
  terminated US. Solomon & Wynne (1953) used a 2-minute cutoff.

**Syntax.**

```
DiscriminatedAvoidance(CSUSInterval=10-s, ITI=3-min, mode=escape)
DiscriminatedAvoidance(CSUSInterval=10-s, ITI=3-min, mode=escape, MaxShock=2-min)
DiscriminatedAvoidance(CSUSInterval=10-s, ITI=3-min, mode=fixed, ShockDuration=0.5-s)
DiscrimAv(CSUSInterval=10-s, ITI=3-min, mode=escape)  -- short alias
```

**Semantic constraints.**

- `CSUSInterval`, `ITI`, and `mode` must all be specified. Missing any →
  `MISSING_DA_PARAM`.
- All temporal params must carry a time unit. Dimensionless → `DA_TIME_UNIT_REQUIRED`.
- All temporal values must be strictly positive. Non-positive → `DA_NONPOSITIVE_PARAM`.
- `ITI` must be > `CSUSInterval` → `DA_ITI_TOO_SHORT`.
- `mode=fixed` requires `ShockDuration` → `MISSING_SHOCK_DURATION`.
- Cross-mode parameter exclusion → `INVALID_PARAM_FOR_MODE`.
- Unknown mode value → `DA_INVALID_MODE`.

**Stimulus annotation.** Like Sidman, discriminated avoidance is aversive by
definition. `@punisher` is recommended:

```
DiscrimAv(CSUSInterval=10-s, ITI=3-min, mode=escape, MaxShock=2-min)
  @punisher("shock", intensity="1.0mA")
  @sd("light", modality="visual")
```

**Composition.** `DiscriminatedAvoidance` is a `base_schedule` and may
appear inside any compound combinator:

```
Chain(FR 10, DiscrimAv(CSUSInterval=10-s, ITI=3-min, mode=escape))
```

### 2.10 Punishment Overlay

The `Overlay` combinator superimposes a punishment contingency on an
existing reinforcement baseline. This is the standard paradigm for studying
the effects of response-contingent aversive stimulation on maintained
operant behavior (Azrin & Holz, 1966).

**Procedural definition.** The baseline schedule continues to deliver
reinforcers. Simultaneously, the punisher schedule delivers aversive stimuli
contingent on the same responses. Both schedules share a single response
stream.

**Syntax.**

```
Overlay(VI 60-s, FR 1)                     -- every response punished
Overlay(Conc(VI 60-s, VI 180-s, COD=2-s), FR 1)  -- concurrent baseline
```

The first component is the reinforcement baseline; the second is the
punishment schedule.

**Semantic constraints.**

- Exactly 2 positional components. More than 2 → `OVERLAY_REQUIRES_TWO`.
- No keyword args in v1.x → `INVALID_KEYWORD_ARG`.

**Stimulus annotation.** Use `@punisher` for the aversive stimulus and
`@reinforcer` for the baseline:

```
Overlay(VI 60-s, FR 1)
  @reinforcer("food")
  @punisher("shock", intensity="0.5mA")
```

**v1.x scope.** Punishment targets all responses. Response-class-specific
punishment (e.g., changeover-only punishment; Todorov, 1971) is planned for
v1.y.

### 2.11 Second-Order Schedules

A **second-order schedule** composes two atomic schedules into two hierarchical roles (Kelleher, 1966; Kelleher & Fry, 1962):

- **Unit schedule** — the inner schedule that defines a *derived response unit*. Each completion of the unit schedule counts as one unit.
- **Overall schedule** — the outer schedule that arranges reinforcement contingent on unit completions.

```
SecondOrder = Overall(Unit)
Overall     = AtomicSchedule          -- parametric only (no EXT, CRF)
Unit        = AtomicSchedule          -- simple schedules only (v1.0)
```

**Syntax example.** `FR5(FI30)` means: treat each completion of FI 30-s as one unit; reinforce after 5 such unit completions.

**Critical semantic constraint.** In the overall position, the `value` field is always interpreted as a **unit completion count** — the number of times the unit schedule must be completed — *not* as an individual response count. A standalone `FR5` counts 5 individual responses; `FR5(FI30)` counts 5 completions of FI 30-s. The notation is intentionally shared, but the operand differs: the overall schedule operates on the derived response unit defined by the unit schedule (Kelleher & Fry, 1962, p. 544).

This distinction is procedurally essential. If the overall were interpreted as a response count, `FR5(FI30)` would reduce to a simple FR 5 that happens to ignore the unit schedule — a degenerate and experimentally meaningless arrangement.

**References.**

- Kelleher, R. T. (1966). Conditioned reinforcement in second-order schedules. *Journal of the Experimental Analysis of Behavior*, 9(5), 475-485. https://doi.org/10.1901/jeab.1966.9-475
- Kelleher, R. T., & Fry, W. (1962). Stimulus functions in chained fixed-interval schedules. *Journal of the Experimental Analysis of Behavior*, 5(2), 167-173. https://doi.org/10.1901/jeab.1962.5-167

---

## References

- Azrin, N. H., & Holz, W. C. (1966). Punishment. In W. K. Honig (Ed.), *Operant behavior: Areas of research and application* (pp. 380-447). Appleton-Century-Crofts.
- Bloomfield, T. M. (1966). Two types of behavioral contrast in discrimination learning. *JEAB*, 9(2), 155-161. https://doi.org/10.1901/jeab.1966.9-155
- Catania, A. C. (2013). *Learning* (5th ed.). Sloan Publishing.
- Farmer, J. (1963). Properties of behavior under random interval reinforcement schedules. *Journal of the Experimental Analysis of Behavior*, 6(4), 607-616. https://doi.org/10.1901/jeab.1963.6-607
- Ferster, C. B., & Skinner, B. F. (1957). *Schedules of reinforcement*. Appleton-Century-Crofts.
- Solomon, R. L., & Wynne, L. C. (1953). Traumatic avoidance learning: Acquisition in normal dogs. *Psychological Monographs: General and Applied*, 67(4), 1-19. https://doi.org/10.1037/h0093649
- Todorov, J. C. (1971). Concurrent performances: Effect of punishment contingent on the switching response. *JEAB*, 16(1), 51-62. https://doi.org/10.1901/jeab.1971.16-51
- Findley, J. D. (1958). Preference and switching under concurrent scheduling. *Journal of the Experimental Analysis of Behavior*, 1(2), 123-144. https://doi.org/10.1901/jeab.1958.1-123
- Fleshler, M., & Hoffman, H. S. (1962). A progression for generating variable-interval schedules. *Journal of the Experimental Analysis of Behavior*, 5(4), 529-530. https://doi.org/10.1901/jeab.1962.5-529
- Herrnstein, R. J. (1961). Relative and absolute strength of response as a function of frequency of reinforcement. *Journal of the Experimental Analysis of Behavior*, 4(3), 267-272. https://doi.org/10.1901/jeab.1961.4-267
- Herrnstein, R. J., & Loveland, D. H. (1975). Maximizing and matching on concurrent ratio schedules. *Journal of the Experimental Analysis of Behavior*, 24(1), 107-116. https://doi.org/10.1901/jeab.1975.24-107
- Herrnstein, R. J., & Vaughan, W. (1980). Melioration and behavioral allocation. In J. E. R. Staddon (Ed.), *Limits to action: The allocation of individual behavior* (pp. 143-176). Academic Press.
- Azrin, N. H., & Holz, W. C. (1966). Punishment. In W. K. Honig (Ed.), *Operant behavior: Areas of research and application* (pp. 380-447). Appleton-Century-Crofts.
- Baum, W. M., Aparicio, C. F., & Alonso-Alvarez, B. (2022). Rate matching, probability matching, and optimization in concurrent ratio schedules. *Journal of the Experimental Analysis of Behavior*, 118(1). https://doi.org/10.1002/jeab.771
- Bouton, M. E. (2004). Context and behavioral processes in extinction. *Learning & Memory*, 11, 485-494. https://doi.org/10.1101/lm.78804
- Kramer, T. J., & Rilling, M. (1970). Differential reinforcement of low rates: A selective critique. *Psychological Bulletin*, *74*(4), 225–254. https://doi.org/10.1037/h0029813
- Mizutani, Y. (2018). OperantKit: A Swift framework for reinforcement schedule simulation [Computer software]. GitHub. https://github.com/YutoMizutani/OperantKit
- Nevin, J. A. (1974). Response strength in multiple schedules. *Journal of the Experimental Analysis of Behavior*, *21*(3), 389–408. https://doi.org/10.1901/jeab.1974.21-389
- Schoenfeld, W. N., & Cole, B. K. (1972). *Stimulus schedules: The t-τ systems*. Harper & Row.
- Reynolds, G. S. (1961). Behavioral contrast. *Journal of the Experimental Analysis of Behavior*, 4(1), 57-71. https://doi.org/10.1901/jeab.1961.4-57
- Sidman, M. (1953). Two temporal parameters of the maintenance of avoidance behavior by the white rat. *Journal of Comparative and Physiological Psychology*, 46(4), 253-261. https://doi.org/10.1037/h0060730
- Hineline, P. N. (1977). Negative reinforcement and avoidance. In W. K. Honig & J. E. R. Staddon (Eds.), *Handbook of operant behavior* (pp. 364-414). Prentice-Hall.
- de Waard, R. J., Galizio, M., & Baron, A. (1979). Chained schedules of avoidance: Reinforcement within and by avoidance situations. *Journal of the Experimental Analysis of Behavior*, 32(3), 399-407. https://doi.org/10.1901/jeab.1979.32-399
- Page, S., & Neuringer, A. (1985). Variability is an operant. *Journal of Experimental Psychology: Animal Behavior Processes*, 11(3), 429-452. https://doi.org/10.1037/0097-7403.11.3.429
- Neuringer, A. (2002). Operant variability: Evidence, functions, and theory. *Psychonomic Bulletin & Review*, 9(4), 672-705. https://doi.org/10.3758/BF03196324
- Miller, N., & Neuringer, A. (2000). Reinforcing variability in adolescents with autism. *Journal of Applied Behavior Analysis*, 33(2), 151-165. https://doi.org/10.1901/jaba.2000.33-151
- Lee, R., McComas, J. J., & Jawor, J. (2002). The effects of differential and lag reinforcement schedules on varied verbal responding by individuals with autism. *Journal of Applied Behavior Analysis*, 35(4), 391-402. https://doi.org/10.1901/jaba.2002.35-391
- Skinner, B. F. (1948). 'Superstition' in the pigeon. *Journal of Experimental Psychology*, 38(2), 168-172. https://doi.org/10.1037/h0055873
- Wagner, A. R. (1981). SOP: A model of automatic memory processing in animal behavior. In N. E. Spear & R. R. Miller (Eds.), *Information processing in animals: Memory mechanisms* (pp. 5-47). Erlbaum.
