# Formal Semantics of Trial-Based Schedules

## Abstract

This document formalizes the semantics of Core-TrialBased schedules,
establishing the theoretical foundation for discrete-trial procedures
in the contingency-dsl. We define the trial as a finite-state machine,
formalize correctness criteria for Matching-to-Sample (MTS), and prove
the incompatibility of free-operant modifiers with trial-based schedules.
We show that trial-based and free-operant schedules share a common type
(`ScheduleExpr`) but differ in their response opportunity structure,
establishing the precise boundary between the two paradigms.

For the formal grammar, see [grammar.md](grammar.md).
For the architectural context, see [architecture.md](../architecture.md).
For the Core algebra of free-operant schedules, see [core/theory.md](../core/theory.md).

---

## §1. Free-Operant vs. Discrete-Trial: The Response Opportunity Axis

### 1.1 The Distinction

Core and Core-Stateful schedules assume a **free-operant** response
opportunity: the subject may emit the target response at any time, and
the schedule evaluates a continuous stream of responses against its
criterion. The dependent variable is response rate (Skinner, 1938).

Core-TrialBased schedules assume a **discrete-trial** response
opportunity: the experimenter presents a structured stimulus
configuration, the subject emits exactly one selection response per
trial, and the schedule evaluates that response against a correctness
criterion. The dependent variable is accuracy (percent correct).

**Definition 1 (Response Opportunity).** A response opportunity is
characterized by the tuple `(structure, cardinality, stream)`:

```
Free-operant:   (unstructured, unbounded, continuous)
Discrete-trial: (structured,   1-per-trial, segmented)
```

This distinction is **procedural**, not behavioral — it describes what
the experimenter arranges, not what the subject does. A subject in a
free-operant procedure may pause; a subject in a discrete-trial
procedure may attempt multiple responses. The distinction pertains to
the reinforcement contingency: in free-operant schedules, any response
in the stream may satisfy the criterion; in discrete-trial schedules,
only the first response within a trial window is evaluated.

### 1.2 Shared Type, Different Structure

Both paradigms produce values of type `ScheduleExpr` in the AST.
Core-TrialBased schedules appear wherever `base_schedule` is expected:

```
base_schedule ::= ... | trial_based_schedule
```

This means trial-based schedules compose with Core combinators
(`Conc`, `Mult`, `Chain`, etc.) at the syntactic level. Semantic
appropriateness of specific combinations is enforced by linter
WARNINGs, not parse errors — following the DSL's principle that
syntactic permissiveness enables future paradigms while semantic
analysis catches current misuse.

---

## §2. The Trial State Machine

### 2.1 Trial States

An MTS trial is a finite-state machine with 5 states:

```
         ┌──────────────────────────────────────────────┐
         │                                              │
         ▼                                              │
    ┌─────────┐     ┌────────────┐     ┌──────────┐    │
    │ SAMPLE  │────▶│ COMPARISON │────▶│ EVALUATE │    │
    └─────────┘     └────────────┘     └──────────┘    │
                                         │      │      │
                                    correct  incorrect  │
                                         │      │      │
                                         ▼      ▼      │
                                  ┌─────────────────┐   │
                                  │   CONSEQUENCE   │   │
                                  └────────┬────────┘   │
                                           │            │
                                           ▼            │
                                       ┌───────┐       │
                                       │  ITI  │───────┘
                                       └───────┘
```

**Definition 2 (Trial State Machine).** An MTS trial is a quintuple
`T = (Q, q₀, δ, F, C)` where:

- `Q = {SAMPLE, COMPARISON, EVALUATE, CONSEQUENCE, ITI}` — finite set of states
- `q₀ = SAMPLE` — initial state
- `δ: Q × Event → Q` — transition function (deterministic)
- `F = {ITI}` — final state (trial complete, triggers next trial)
- `C: {correct, incorrect} → ScheduleExpr` — consequence mapping

The transition function:

```
δ(SAMPLE, sample_presented)     = COMPARISON
δ(COMPARISON, response(i))      = EVALUATE
δ(EVALUATE, match_result(r))    = CONSEQUENCE
δ(CONSEQUENCE, schedule_complete) = ITI
δ(ITI, iti_elapsed)             = SAMPLE   (next trial)
```

### 2.2 Trial Parameters

An MTS trial is parameterized by:

```
MTS_params = {
  n:           ℤ⁺, n ≥ 2         -- number of comparisons
  consequence: ScheduleExpr       -- correct response schedule
  incorrect:   ScheduleExpr       -- incorrect response schedule (default: EXT)
  iti:         ℝ⁺ × TimeUnit     -- inter-trial interval
  match_type:  {identity, arbitrary}  -- correctness criterion
}
```

### 2.3 Time Within a Trial

The trial state machine introduces **two time scales**:

1. **Within-trial time**: Time spent in SAMPLE, COMPARISON, EVALUATE,
   CONSEQUENCE states. Not specified by the DSL — determined by
   stimulus presentation software and subject behavior.
2. **Between-trial time**: The ITI, explicitly parameterized.

This contrasts with free-operant schedules where there is a single
continuous time scale. The dual time scale is why free-operant
modifiers (DRL, DRH, DRO) are semantically incompatible — they
operate on inter-response times within a continuous stream, which
does not exist in trial-based procedures (see §4).

---

## §3. Correctness Criteria

### 3.1 Identity Matching

**Definition 3 (Identity Criterion).** Given sample stimulus `s` and
comparison stimuli `{c₁, c₂, ..., cₙ}`, response `cᵢ` is correct iff:

```
correct(cᵢ, s) ⟺ cᵢ ≡ s
```

where `≡` denotes physical identity (same stimulus). The identity
relation is:

- **Reflexive**: `s ≡ s` (trivially)
- **Symmetric**: `s ≡ c ⟹ c ≡ s`
- **Transitive**: `s ≡ c ∧ c ≡ t ⟹ s ≡ t`

Identity matching requires no external information beyond stimulus
properties. The runtime can determine correctness by comparing
stimulus identifiers.

### 3.2 Arbitrary Matching

**Definition 4 (Arbitrary Criterion).** Given sample stimulus `s`,
comparison stimuli `{c₁, c₂, ..., cₙ}`, and a class function
`κ: Stimulus → Class`, response `cᵢ` is correct iff:

```
correct(cᵢ, s) ⟺ κ(cᵢ) = κ(s)
```

where `κ` is defined by the `@stimulus_classes` annotation.

The class function `κ` induces an equivalence relation `~` on the
stimulus set:

```
a ~ b ⟺ κ(a) = κ(b)
```

This relation is reflexive, symmetric, and transitive by construction
(it is the kernel of `κ`). Note that this is **not** the same as
Sidman's (1994) stimulus equivalence — the DSL defines class membership
declaratively via `@stimulus_classes`, while stimulus equivalence is an
**emergent behavioral outcome** that the MTS procedure is designed to
test. The DSL specifies the procedure; the behavior is observed.

### 3.3 The Procedure-Effect Boundary

This distinction is critical and warrants emphasis:

| | DSL specification | Behavioral outcome |
|---|---|---|
| **Identity MTS** | `correct ⟺ cᵢ ≡ s` (physical identity) | Generalized identity matching (Oden et al., 1988) |
| **Arbitrary MTS** | `correct ⟺ κ(cᵢ) = κ(s)` (class membership) | Stimulus equivalence (Sidman & Tailby, 1982) |

The DSL defines the **contingency** (what the experimenter arranges).
Whether the subject's behavior comes under the control of the
contingency — and whether untrained relations emerge — is an empirical
question. The DSL must not presuppose the answer.

---

## §4. Modifier Incompatibility Proof

### 4.1 Statement

**Theorem 1.** Free-operant modifiers (DRL, DRH, DRO, Pctl, Lag)
are semantically incompatible with trial-based schedules.

### 4.2 Proof

Each modifier assumes a property of the free-operant response stream
that does not exist in trial-based procedures:

**DRL (Differential Reinforcement of Low rate).** DRL requires
inter-response time (IRT) ≥ threshold. IRT is defined as the time
between two successive responses in a continuous stream. In a
trial-based procedure, responses are separated by the trial state
machine (CONSEQUENCE + ITI + SAMPLE + COMPARISON), not by
inter-response pauses. The time between the response on trial *t*
and the response on trial *t+1* is not an IRT — it is a structured
interval containing experimenter-controlled events. DRL applied to
this interval would reinforce slow trial completion, which is a
property of the apparatus, not the subject's behavior. ∎

**DRH (Differential Reinforcement of High rate).** DRH requires
response rate ≥ threshold within a time window. Trial-based procedures
produce at most 1 response per trial. Response rate is
`trials_completed / session_time`, which is controlled by trial
parameters (SAMPLE duration, COMPARISON duration, ITI), not by the
subject's behavior alone. DRH applied to trial rate confounds
procedure parameters with behavioral output. ∎

**DRO (Differential Reinforcement of Other behavior).** DRO requires
the absence of the target response for a specified duration. In a
trial-based procedure, the target response (comparison selection) is
*impossible* during SAMPLE, ITI, and CONSEQUENCE states — the absence
of responding is enforced by the procedure, not by the subject's
behavior. DRO during ITI would always be satisfied (trivially), and
DRO during COMPARISON would be satisfied by withholding response
(which the procedure does not reinforce). Neither interpretation is
meaningful. ∎

**Pctl (Percentile schedule).** Pctl reinforces responses whose IRT
(or other dimension) falls below/above a percentile threshold of recent
responses. Same IRT objection as DRL: the relevant time dimension in
trial-based procedures is not inter-response time but
inter-trial time, which is experimenter-controlled. ∎

**Lag.** Lag reinforces responses that differ from the previous *n*
responses (or response sequences). In standard MTS, the "response" is
a comparison selection. Lag applied to comparison selections would
require the subject to select *different* comparisons across trials —
but the correct comparison is determined by the sample, not by
variability requirements. Lag would create a conflict between the
MTS correctness criterion and the variability criterion. ∎

### 4.3 Combinators Are Permitted

Combinators (`Conc`, `Mult`, `Chain`, etc.) operate at a different
level — they arrange schedules relative to each other, not within
a schedule's response stream. A `Mult(MTS(...), EXT)` alternates
between an MTS component and an extinction component, which is
procedurally coherent (e.g., alternating training and probe phases).
A `Chain(FR5, MTS(...))` requires FR5 completion before an MTS trial
begins, which models a response requirement preceding stimulus
presentation.

Therefore, combinators are syntactically and semantically permitted
with trial-based schedules, while modifiers are not.

---

## §5. Consequence Embedding

### 5.1 Core Schedules as Consequence Parameters

MTS `consequence` and `incorrect` parameters accept Core
`ScheduleExpr` values. This creates an embedding:

```
TrialBased.consequence : ScheduleExpr    (Core)
TrialBased.incorrect   : ScheduleExpr    (Core)
```

The consequence schedule executes within the CONSEQUENCE state of the
trial state machine. Its completion triggers the transition to ITI.

### 5.2 Semantic Restrictions

Not all Core expressions are appropriate as consequences:

| Restriction | Code | Rationale |
|---|---|---|
| No compound schedules | `MTS_INVALID_CONSEQUENCE` | A trial consequence is a single atomic event |
| No trial-based schedules | `MTS_RECURSIVE_CONSEQUENCE` | Prevents infinite nesting of trial state machines |

Permitted consequence expressions are restricted to:

```
consequence ∈ { Atomic, Special(CRF), Special(EXT), SecondOrder }
```

This restriction is semantic, not syntactic. The grammar permits any
`schedule` expression; the validator rejects inappropriate ones.

### 5.3 Default Consequence for Incorrect Responses

When `incorrect` is omitted, it defaults to `EXT` (extinction). This
is the standard procedure in MTS research: incorrect responses produce
no programmed consequence. The default is documented in
[defaults.md](../../../schema/core-trial-based/defaults.md).

---

## §6. Relationship to Stimulus Equivalence

### 6.1 MTS as Procedural Foundation

MTS is the procedural foundation for stimulus equivalence research
(Sidman, 1971; Sidman & Tailby, 1982). The DSL's treatment reflects
this relationship:

- **MTS primitive** defines the trial structure (§2)
- **`@stimulus_classes`** defines class membership (§3.2)
- **`@training` / `@testing`** (planned) define phase configuration

The DSL separates these concerns because they have different
ontological status:

| Concern | DSL representation | Status |
|---|---|---|
| Trial structure | `MTS(...)` primitive | Procedural — what the experimenter arranges |
| Class membership | `@stimulus_classes` annotation | Definitional — experimenter's classification of stimuli |
| Training/testing | `@training` / `@testing` annotations | Procedural — phase configuration |
| Equivalence relations | Not represented | Behavioral — emergent outcome, not a procedure |

### 6.2 What the DSL Does Not Represent

The DSL does not represent:

1. **Emergent relations** (reflexivity, symmetry, transitivity) — these
   are behavioral outcomes observed *after* MTS training, not
   procedural specifications.
2. **Derived stimulus relations** (Hayes et al., 2001) — theoretical
   constructs about the *process* underlying equivalence.
3. **Transfer of function** — a behavioral phenomenon observed across
   stimulus classes.

These are intentional omissions. The DSL specifies procedures; the
behavior is discovered. Following the procedure-effect boundary
established in [core/theory.md §2.6](../core/theory.md):

> "The DSL specifies procedures — what the experimenter arranges.
> It does not predict effects — what the organism does."

---

## References

- Cumming, W. W., & Berryman, R. (1965). The complex discriminated
  operant: Studies of matching-to-sample and related problems. In
  D. I. Mostofsky (Ed.), *Stimulus generalization* (pp. 284–330).
  Stanford University Press.
- Ferster, C. B., & Skinner, B. F. (1957). *Schedules of reinforcement*.
  Appleton-Century-Crofts.
- Hayes, S. C., Barnes-Holmes, D., & Roche, B. (2001). *Relational
  frame theory: A post-Skinnerian account of human language and
  cognition*. Kluwer Academic/Plenum.
- Oden, D. L., Thompson, R. K. R., & Premack, D. (1988). Spontaneous
  transfer of matching by infant chimpanzees (*Pan troglodytes*).
  *Journal of Experimental Psychology: Animal Behavior Processes*,
  *14*(2), 140–145. https://doi.org/10.1037/0097-7403.14.2.140
- Sidman, M. (1971). Reading and auditory-visual equivalences. *Journal
  of Speech and Hearing Research*, *14*(1), 5–13.
  https://doi.org/10.1044/jshr.1401.05
- Sidman, M. (1994). *Equivalence relations and behavior: A research
  story*. Authors Cooperative.
- Sidman, M., & Tailby, W. (1982). Conditional discrimination vs.
  matching to sample: An expansion of the testing paradigm. *JEAB*,
  *37*(1), 5–22. https://doi.org/10.1901/jeab.1982.37-5
- Skinner, B. F. (1938). *The behavior of organisms: An experimental
  analysis*. Appleton-Century-Crofts.
- Zentall, T. R., Hogan, D. E., & Edwards, C. A. (1981). Oddity
  learning in the pigeon: Effect of negative instances, correction, and
  number of incorrect alternatives. *Animal Learning & Behavior*,
  *9*(4), 493–497. https://doi.org/10.3758/BF03209781
