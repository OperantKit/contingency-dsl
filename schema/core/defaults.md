# contingency-dsl Defaults

Explicit documentation of all implicit defaults in the DSL.
When a parameter is omitted, the following values apply.

## Variable schedule distribution family

| Written | Default distribution | Rationale |
|---------|---------------------|-----------|
| `VI60s` | Fleshler-Hoffman (1962) | De facto standard in modern EAB laboratories |
| `VR20` | Fleshler-Hoffman (1962) | Same rationale |
| `VT60s` | Fleshler-Hoffman (1962) | Same rationale |

Explicit override (future syntax, not in v1.0 BNF):
```
VI60s:arith       -- arithmetic progression
VI60s:exp         -- exponential (constant-probability)
VI60s:fh(N=20)   -- Fleshler-Hoffman with explicit N
```

### Fleshler-Hoffman default parameters

| Parameter | Default | Notes |
|-----------|---------|-------|
| `N` (series length) | **12** | Number of intervals in the FH progression. Fleshler & Hoffman (1962) discussed N=12 and N=20 |
| `seed` | **auto** (runtime-generated) | RNG seed for non-replacement sampling. `auto` = runtime generates a unique seed per schedule instance |

When no distribution family is specified (e.g., bare `VI60s`), the DSL assumes
Fleshler-Hoffman with `N=12` and `seed=auto`.

**`seed` is not a DSL-level concern.** No published JEAB/JABA paper has ever
reported the RNG seed used for FH value generation. The purpose of Variable
schedules is to guarantee unpredictable, unbiased reinforcement timing; the
FH algorithm achieves this mathematically regardless of seed. In typical
experimental practice (e.g., renewal procedures with ~20 sessions per phase),
fixing a seed across all sessions would produce a repeating fixed pattern,
undermining the very purpose of the Variable schedule. Requiring seed-level
replication as a condition for procedural reproducibility has no basis in
EAB methodology — steady-state behavior under a given schedule is the
replication target, not the specific interval sequence (Sidman, 1960).

The `seed` parameter exists in the runtime layer for computational
determinism in unit tests and simulations, not as a procedural parameter.
The DSL does not emit any linter warning for omitted `seed`.

**Overriding N.** The choice of N affects the shape of the interval
distribution. N=12 closely approximates the theoretical constant-probability
(exponential) distribution while remaining practical for laboratory use.
Larger N values (e.g., N=20) provide finer granularity but require longer
series before recycling.

| Written | `N` | Notes |
|---------|-----|-------|
| `VI60s` | 12 | Default; sufficient for all standard use |
| `@algorithm("fleshler-hoffman", n=20)` | 20 | Explicit N override |

**Future inline syntax (reserved, not in v1.0 BNF):**

```
VI60s:fh          -- explicit FH, default parameters (N=12, seed=auto)
VI60s:fh(N=20)    -- FH with N=20
```

The `:fh(...)` suffix is reserved for future versions. v1.0 parsers that
encounter this syntax MUST reject it with a clear error message indicating
the syntax is reserved. The `@algorithm(...)` annotation remains the v1.0
mechanism for specifying FH parameters.

Reference: Fleshler, M., & Hoffman, H. S. (1962). A progression for generating
variable-interval schedules. *JEAB*, 5(4), 529-530.

## Time unit

| Written | Default | Notes |
|---------|---------|-------|
| `FR5` | dimensionless | Ratio schedules count responses, not time |
| `FI30` | seconds (`s`) | Time-based schedules default to seconds |
| `VI60` | seconds (`s`) | Same |

The `time_unit` field in the AST is `null` when not explicitly declared.
Conversion to canonical seconds occurs at the runtime bridge, not in the DSL.

**v1.0:** Interval and Time domain schedules (FI, VI, RI, FT, VT, RT) without
an explicit time unit emit a linter WARNING (code `MISSING_TIME_UNIT`). The
expression remains valid and parseable, but the omission is flagged for
procedural clarity. Ratio domain schedules (FR, VR, RR) are dimensionless and
never trigger this warning.

Rationale: In JEAB Method sections, writing "FI 30" without a unit would prompt
a reviewer to ask whether 30 seconds, 30 milliseconds, or 30 minutes is
intended. This follows the same design philosophy as `MISSING_COD` for Conc
(Herrnstein, 1961) — procedurally essential information that is permitted to
omit for conceptual or pedagogical use, but flagged to encourage explicitness.

## Progressive Ratio step function

| Written | Expansion | Notes |
|---------|-----------|-------|
| ~~`PR`~~ | — | **Removed in v1.0.** Bare `PR` (no number, no parens) is a ParseError. |
| `PR n` | `PR(linear, start=n, increment=n)` | Jarmolowicz & Lattal (2010) notation. `PR 5` → FR 5, FR 10, FR 15, ... |
| `PR(linear)` | `start=1, increment=5` | Linear default parameters |
| `PR(geometric)` | `start=1, ratio=2` | Geometric default parameters (doubling: 1, 2, 4, 8, ...) |

## Limited Hold

| Written | Behavior |
|---------|----------|
| No `LH` specified | No availability window (infinite hold); `limitedHold` property absent |
| `LimitedHold = 10s` (program-level) | `limitedHold` property set on all leaf schedules (Atomic, Special, DRModifier, SecondOrder, TrialBased) |
| `FI30 LH10` (expression-level) | `limitedHold=10` set on that schedule node; overrides program-level default |
| `Conc(VI30, VI60) LH10` | SemanticError (`LH_ON_COMPOUND`); use per-component LH or program-level default |

## Reinforcement Delay (RD)

**v1.x:** RD is a **program-level param_decl only** (no expression-level
suffix). It specifies the session-wide temporal interval between any
schedule satisfaction event and the delivery of the consequence — typically
representing apparatus-imposed delay (e.g., feeder actuation time).

| Parameter | Alias | Syntax (param_decl) | Dimension |
|-----------|-------|---------------------|-----------|
| RD | ReinforcementDelay | `RD = 500ms` | Time (s/ms/min) |

| Written | Behavior |
|---------|----------|
| No `RD` specified | No explicit delay (immediate delivery) |
| `RD = 500ms` (program-level) | Session-wide: runtime delays all consequence delivery by 500 ms |
| `RD = 0s` | Explicit immediate delivery (no linter warning) |

- `RD=0s` is legal and does NOT trigger a linter warning.
- `RD > 30s` triggers Linter WARNING `RD_LARGE_DELAY`.
- Time unit is mandatory. `RD = 5` (dimensionless) → `RD_TIME_UNIT_REQUIRED`.

**RD has no expression-level syntax.** Per-schedule delays are already
expressible via existing combinators:

| Delay type | DSL expression | Reference |
|---|---|---|
| Nonresetting (unsignaled) | `Tand(VI 60-s, FT 5-s)` | Sizemore & Lattal (1978) |
| Resetting (unsignaled) | `Tand(VI 60-s, DRO 5-s)` | Lattal (2010) |
| Signaled | `Chain(VI 60-s, FT 5-s)` | Richards (1981) |
| Differential (concurrent) | `Conc(Tand(VI 60-s, FT 1-s), Tand(VI 60-s, FT 8-s), COD=2-s)` | Chung & Herrnstein (1967) |
| Adjusting (choice) | `Adj(delay, start=10-s, step=1-s)` | Mazur (1987) |

The program-level `RD` param_decl captures the remaining case: session-wide
apparatus delay that applies uniformly to all reinforcement events.

**Design rationale.** Even brief delays — including feeder actuation time
(≈0.5 s) — systematically modulate response patterns (Lattal, 2010). In
the delay-of-reinforcement literature, per-schedule delay is operationalized
as a tandem FT requirement (Sizemore & Lattal, 1978: "responses on the
VI 60-s schedule were followed by a tandem FT t-s requirement before
reinforcer delivery"). The DSL reuses this established formulation rather
than introducing a redundant expression-level modifier.

References:
- Lattal, K. A. (2010). Delayed reinforcement of operant behavior. *JEAB*,
  93(1), 129-139. https://doi.org/10.1901/jeab.2010.93-129
- Sizemore, O. J., & Lattal, K. A. (1978). Unsignalled delay of
  reinforcement in variable-interval schedules. *JEAB*, 30(2), 169-175.
  https://doi.org/10.1901/jeab.1978.30-169
- Richards, R. W. (1981). A comparison of signaled and unsignaled delay of
  reinforcement. *JEAB*, 35(2), 145-152.
  https://doi.org/10.1901/jeab.1981.35-145
- Chung, S.-H., & Herrnstein, R. J. (1967). Choice and delay of
  reinforcement. *JEAB*, 10(1), 67-74.
  https://doi.org/10.1901/jeab.1967.10-67

## Concurrent changeover delay (COD) and fixed-ratio changeover (FRCO)

**v1.0:** COD is optional for `Conc`. Omitting COD emits a linter WARNING
(code `MISSING_COD`), recommending explicit specification per Herrnstein (1961).
The runtime default is `COD=0s` (no changeover delay), applied at the runtime
bridge layer — the AST does not contain an implicit COD.

**v1.1 (planned):**

| Parameter | Alias | Syntax (expression) | Syntax (param_decl) | Dimension |
|-----------|-------|---------------------|---------------------|-----------|
| COD | ChangeoverDelay | `Conc(VI30s, VI60s, COD=2s)` | `COD = 2s` | Time (s/ms/min) |
| FRCO | FixedRatioChangeover | `Conc(VI30s, VI60s, FRCO=5)` | `FRCO = 5` | Responses (dimensionless) |

- Expression-level keyword argument overrides program-level `param_decl`
  (same priority rule as LH).
- `COD=0s` is legal (explicit no-delay), but parsers SHOULD emit a lint
  WARNING for VI-VI concurrent schedules (Shull & Pliskoff, 1967).
- Default behavior: symmetric, resetting (each changeover starts a fresh
  COD timer; this follows from the standard definition — "since the last
  changeover," Catania, 1966).
- COD and FRCO may coexist: `Conc(VI30s, VI60s, COD=2s, FRCO=5)`.
- **Directional COD** (Pliskoff, 1971; Williams & Bell, 1999):
  `COD(x->y)=value` specifies the COD for a specific (from, to) pair.
  `Conc(VI30s, VI60s, COD(1->2)=2s, COD(2->1)=5s)` means 2s when
  switching 1→2, 5s when switching 2→1.
  - **Base + override**: `COD=2s, COD(2->1)=5s` — base 2s for all
    directions, overridden to 5s for the 2→1 transition.
  - dir_ref: 1-indexed integer or let-bound identifier.
  - Program-level `param_decl` accepts scalar (symmetric) only.
  - Directional COD + FRCO: both may coexist.
    `Conc(VI30s, VI60s, COD(1->2)=2s, COD(2->1)=5s, FRCO=5)` —
    directional time-based delay with symmetric response requirement.

**Terminology note.** Earlier drafts used the abbreviation `COR` (Changeover
Response), but this abbreviation is not established in the EAB literature.
The standard abbreviation is **FRCO** (Fixed-Ratio Changeover), introduced
by Hunter & Davison (1985). Pliskoff & Fetterman (1981) used the descriptive
term "changeover requirement" without a fixed abbreviation.

References:
- Herrnstein, R. J. (1961). Relative and absolute strength of response as a
  function of frequency of reinforcement. *JEAB*, 4(3), 267-272.
  https://doi.org/10.1901/jeab.1961.4-267
- Catania, A. C. (1966). Concurrent operants. In W. K. Honig (Ed.),
  *Operant behavior: Areas of research and application* (pp. 213-270).
- Shull, R. L., & Pliskoff, S. S. (1967). Changeover delay and concurrent
  performances. *JEAB*, 10(6), 517-527.
  https://doi.org/10.1901/jeab.1967.10-517
- Pliskoff, S. S., & Fetterman, J. G. (1981). Undermatching and overmatching:
  The fixed-ratio changeover requirement. *JEAB*, 36(1), 21-27.
  https://doi.org/10.1901/jeab.1981.36-21
- Hunter, I., & Davison, M. (1985). Determination of a behavioral transfer
  function: White-noise analysis of session-to-session response-ratio
  dynamics on concurrent VI VI schedules. *Animal Learning & Behavior*,
  13(3), 293-299. https://doi.org/10.3758/BF03197983

### Behavioral effects (for procedure selection)

COD and FRCO are not interchangeable. Published concurrent VI VI data
(reviewed by Davison & McCarthy, 1988) show:

- COD typically produces **undermatching** (GML sensitivity a < 1);
  matching improves as COD increases from 0 to ~5 s, then plateaus
  (Shull & Pliskoff, 1967).
- FRCO typically produces **overmatching** (a > 1); larger FR values
  produce more extreme overmatching (Pliskoff & Fetterman, 1981).
- In within-subject comparisons, the two procedures shift response
  allocation in **opposite directions** while leaving time allocation
  comparable (Hunter & Davison, 1985).
- On concurrent **ratio** schedules (not VI), the COD→undermatching
  relation reverses (Bellow & Lattal, 2023).

This DSL treats both parameters as procedural primitives and does not
predict behavioral outcomes; parameter selection is the user's
responsibility. The above is provided as a literature pointer only.

- Davison, M., & McCarthy, D. (1988). *The matching law: A research
  review*. Lawrence Erlbaum Associates.
- Bellow, D. T., & Lattal, K. A. (2023). Choice dynamics in concurrent
  ratio schedules of reinforcement. *JEAB*, 119(2), 337-355.
  https://doi.org/10.1002/jeab.828

## Blackout (BO) — Multiple/Mixed schedules

**v1.1:** BO is **optional** for `Mult` and `Mix`. Omitting BO means no blackout
(immediate component transition). This contrasts with COD, which is mandatory
for `Conc`.

| Parameter | Alias | Syntax (expression) | Syntax (param_decl) | Dimension |
|-----------|-------|---------------------|---------------------|-----------|
| BO | Blackout | `Mult(FR5, EXT, BO=5s)` | `BO = 5s` | Time (s/ms/min) |

- Expression-level keyword argument overrides program-level `param_decl`
  (same priority rule as LH and COD).
- `BO=0s` is legal (explicit no-blackout, equivalent to omission).
- Default behavior: symmetric (same BO for all component transitions).
- **Future (v1.2):** Asymmetric BO per transition direction.

**Design rationale:** BO directly affects behavioral contrast between components
(Reynolds, 1961) and inter-component associative independence (Bouton, 2004).
Structurally symmetric with COD's role in Conc.

References:
- Reynolds, G. S. (1961). Behavioral contrast. *JEAB*, 4(1), 57-71.
- Bouton, M. E. (2004). Context and behavioral processes in extinction.
  *Learning & Memory*, 11, 485-494.

## Second-order schedules

### Brief stimulus

| Written | Default | Notes |
|---------|---------|-------|
| `FR5(FI30s)` | No brief stimulus (Tand-equivalent) | Linter WARNING `MISSING_BRIEF` |
| `FR5(FI30s) @brief("light")` | Brief = light | No warning |
| `FR5(FI30s) @brief("light", duration=0.5)` | Brief = light, 0.5 s | No warning |
| `FR5(FI30s) @brief(none)` | No brief stimulus (explicit opt-out) | No warning |

**Omission triggers `MISSING_BRIEF` WARNING.** Brief stimulus (conditioned
reinforcer) is a defining independent variable of second-order schedules
(Kelleher, 1966). Without brief stimulus, a ratio-overall second-order
schedule is procedurally equivalent to a tandem arrangement (§2.11.1 in
theory.md). The DSL does not block this — the arrangement may be
intentional — but requires the user to acknowledge the omission explicitly
via `@brief(none)`.

**`@brief(none)` is the explicit opt-out.** Writing `@brief(none)` signals
that the user has considered and deliberately excluded the brief stimulus.
This suppresses the `MISSING_BRIEF` warning. The semantics are identical
to bare omission (no conditioned reinforcer between unit completions),
but the intent is documented in the source.

This follows the same design philosophy as `MISSING_COD` for `Conc`
(constraint §7): procedurally essential information that is permitted to
omit for conceptual or pedagogical use, but flagged to encourage
explicitness.

References:
- Kelleher, R. T. (1966). Conditioned reinforcement in second-order
  schedules. *JEAB*, 9(5), 475-485.
  https://doi.org/10.1901/jeab.1966.9-475
- Goldberg, S. R., Kelleher, R. T., & Morse, W. H. (1975). Second-order
  schedules of drug injection. *Federation Proceedings*, 34(9), 1771-1776.

### Unit completion count

In a second-order schedule `OVERALL(UNIT)`, the overall schedule's `value`
is always a **unit completion count**, not an individual response count.

| Written | Overall value means | Unit value means |
|---------|---------------------|------------------|
| `FR5(FI30)` | 5 completions of FI 30-s | 30-s interval (standard) |
| `FI120s(FR10)` | first unit completion after 120 s | 10 responses (standard) |
| `VI60s(FR10)` | first unit completion after ≈60 s | 10 responses (standard) |

A standalone `FR5` counts 5 individual responses. `FR5(FI30)` counts 5
completions of FI 30-s. The notation is shared, but the operand differs:
the overall schedule operates on the derived response unit defined by the
unit schedule (Kelleher & Fry, 1962).

Reference: Kelleher, R. T., & Fry, W. (1962). Stimulus functions in
chained fixed-interval schedules. *JEAB*, 5(2), 167-173.
https://doi.org/10.1901/jeab.1962.5-167

## Standalone DR modifier (DRL/DRH/DRO)

A DR modifier written without an enclosing combinator is a valid schedule
expression. It denotes the DR constraint applied to an **implicit CRF
(FR 1)** base schedule.

| Written | Equivalent expansion | Semantics |
|---------|---------------------|-----------|
| `DRL5s` | `Tand(CRF, DRL5s)` | Reinforce every response whose IRT ≥ 5 s |
| `DRH2s` | `Tand(CRF, DRH2s)` | Reinforce every response whose IRT ≤ 2 s |
| `DRO10s` | `Tand(CRF, DRO10s)` | Deliver reinforcer if no target response occurs for 10 s |

This matches standard laboratory usage: "DRL 20-s" in the literature
denotes a schedule in which every response satisfying the IRT criterion
is reinforced — i.e., CRF gated by a temporal filter (Ferster & Skinner,
1957, Ch. 8; Kramer & Rilling, 1970).

When a DR modifier appears inside an explicit combinator (e.g.,
`Tand(VR20, DRL5s)`), the combinator's base schedule replaces the
implicit CRF.

**AST note.** The implicit CRF is a *semantic* default, not an AST
transformation. Conforming parsers emit a `Modifier` node; desugaring
to `Tand(CRF, Modifier)` is optional and implementation-defined.

**DRO specificity.** Standalone `DRO10s` means "deliver reinforcement
contingent on the absence of the target response for 10 s." The implicit
CRF applies to the *reinforcement delivery*, not to the target response
class (which is under extinction by definition of the omission
contingency). See [design-rationale.md §1](../../../docs/en/design-rationale.md#1-dro-why-other-behavior-is-a-misnomer).

References:
- Ferster, C. B., & Skinner, B. F. (1957). *Schedules of reinforcement*.
  Appleton-Century-Crofts.
- Kramer, T. J., & Rilling, M. (1970). Differential reinforcement of low
  rates: A selective critique. *Psychological Bulletin*, 74(4), 225-254.
  https://doi.org/10.1037/h0029813

## Lag schedule (v1.x)

**v1.x:** `Lag` is a differential reinforcement modifier for operant
variability (see grammar.ebnf `lag_mod` production and
[spec/en/theory.md §2.8](spec/en/theory.md)). The parameter `n` is positional
to match literature notation ("Lag 5", Page & Neuringer, 1985). The keyword
argument `length` specifies the response unit size.

| Parameter | Position | Default | Dimension |
|-----------|----------|---------|-----------|
| n | positional (first) | no default (required) | non-negative integer, dimensionless |
| length | keyword (`length=N`) | **1** (individual response unit) | positive integer, dimensionless |

- `n` must be a non-negative integer. Non-integer or negative → `LAG_INVALID_N_VALUE`.
- `n` must NOT carry a time unit. `Lag 5s` → `LAG_UNEXPECTED_TIME_UNIT`.
- `length` defaults to 1 if omitted. When specified, it must be >= 1.
  `length=0` or negative → `LAG_INVALID_LENGTH`.
- Large `n` (> 50) → linter WARNING `LAG_LARGE_N`.
- `Lag 0` is legal and semantically equivalent to CRF (no variability
  requirement, all responses reinforced).
- `Lag(5, length=8)` replicates Page & Neuringer (1985) Experiment 1 style
  (2-key 8-peck sequences, Lag 1-50 across experiments).

**Semantics.** Let S(t) be the response unit (individual response if
`length=1`, or N-response sequence if `length=N`). Reinforcement is
delivered iff:

```
S(t) ∉ { S(t-1), S(t-2), ..., S(t-n) }
```

In words: reinforce only if the current unit differs from each of the
previous n units.

References:
- Page, S., & Neuringer, A. (1985). Variability is an operant. *Journal of
  Experimental Psychology: Animal Behavior Processes*, 11(3), 429-452.
  https://doi.org/10.1037/0097-7403.11.3.429
- Neuringer, A. (2002). Operant variability: Evidence, functions, and
  theory. *Psychonomic Bulletin & Review*, 9(4), 672-705.
  https://doi.org/10.3758/BF03196324

## Sidman free-operant avoidance (v1.x)

**v1.x:** Sidman is a dedicated aversive-schedule primitive
(see grammar.ebnf `aversive_schedule` production and
[spec/en/theory.md §2.7](spec/en/theory.md)). Both parameters are
mandatory; **there is no default value**.

| Parameter | Alias | Syntax | Dimension |
|-----------|-------|--------|-----------|
| SSI | ShockShockInterval | `Sidman(SSI=20s, ...)` | Time (s/ms/min), strictly positive, unit required |
| RSI | ResponseShockInterval | `Sidman(..., RSI=5s)` | Time (s/ms/min), strictly positive, unit required |

- Both SSI and RSI must be specified. Missing either → `MISSING_SIDMAN_PARAM`.
- Time unit is mandatory for each parameter. Dimensionless → `SIDMAN_TIME_UNIT_REQUIRED`.
- Values must be strictly positive. Non-positive → `SIDMAN_NONPOSITIVE_PARAM`.
- `RSI > SSI` is legal but triggers a linter WARNING `RSI_EXCEEDS_SSI`:
  when RSI exceeds SSI, responses cannot actually postpone shocks below
  the SSI baseline (Sidman, 1953; Hineline, 1977).
- Duplicate SSI or RSI → `DUPLICATE_SIDMAN_PARAM` (aliases count as duplicate,
  e.g., `SSI` and `ShockShockInterval` in the same expression).

**Semantics.** In the absence of responses, shocks occur every SSI seconds.
Each response resets the next shock to occur at `last_response + RSI`:

```
next_shock(t) = max(last_shock_time + SSI, last_response_time + RSI)
```

References:
- Sidman, M. (1953). Two temporal parameters of the maintenance of avoidance
  behavior by the white rat. *Journal of Comparative and Physiological
  Psychology*, 46(4), 253-261. https://doi.org/10.1037/h0060730
- Hineline, P. N. (1977). Negative reinforcement and avoidance. In W. K. Honig
  & J. E. R. Staddon (Eds.), *Handbook of operant behavior* (pp. 364-414).
  Prentice-Hall.

## Discriminated avoidance (v1.x)

**v1.x:** `DiscriminatedAvoidance` (alias `DiscrimAv`) is a dedicated
aversive-schedule primitive (see grammar.ebnf `discriminated_avoidance`
production and [spec/en/theory.md §2.9](spec/en/theory.md)). Three
parameters are mandatory; **there is no default value** for any of them.

| Parameter | Alias | Syntax | Dimension | Required |
|-----------|-------|--------|-----------|----------|
| CSUSInterval | — | `DiscrimAv(CSUSInterval=10s, ...)` | Time (s/ms/min), strictly positive, unit required | YES |
| ITI | — | `DiscrimAv(..., ITI=3min, ...)` | Time (s/ms/min), strictly positive, unit required, must be > CSUSInterval | YES |
| mode | — | `DiscrimAv(..., mode=escape, ...)` | `fixed` \| `escape` | YES |
| ShockDuration | — | `DiscrimAv(..., ShockDuration=0.5s)` | Time (s/ms/min), strictly positive, unit required | YES (mode=fixed only) |
| MaxShock | — | `DiscrimAv(..., MaxShock=2min)` | Time (s/ms/min), strictly positive, unit required | NO (mode=escape only, default=no cutoff) |

- `CSUSInterval`, `ITI`, and `mode` must all be specified. Missing any → `MISSING_DA_PARAM`.
- Temporal parameters must carry a time unit. Dimensionless → `DA_TIME_UNIT_REQUIRED`.
- Temporal values must be strictly positive. Non-positive → `DA_NONPOSITIVE_PARAM`.
- `ITI` must be > `CSUSInterval`. Otherwise → `DA_ITI_TOO_SHORT`.
- `mode=fixed` requires `ShockDuration`. Missing → `MISSING_SHOCK_DURATION`.
- `mode=fixed` with `MaxShock` → `INVALID_PARAM_FOR_MODE`.
- `mode=escape` with `ShockDuration` → `INVALID_PARAM_FOR_MODE`.
- Unknown mode value → `DA_INVALID_MODE`.
- Duplicate parameters → `DUPLICATE_DA_PARAM`.

**Semantics.** A CS (warning signal) is presented. If the subject responds
within CSUSInterval (avoidance trial), the US is cancelled and the next
trial begins at ITI from the current CS onset. If the subject fails to
respond within CSUSInterval (escape/failure trial), the US is delivered:

- `mode=fixed`: US is presented for exactly `ShockDuration`.
- `mode=escape`: US continues until the subject responds (terminates the US).
  Optional `MaxShock` sets a safety cutoff (Solomon & Wynne, 1953 used 2min).

```
next_cs(t) = current_cs_onset + ITI
us_onset = current_cs_onset + CSUSInterval  (if no avoidance response)
```

References:
- Solomon, R. L., & Wynne, L. C. (1953). Traumatic avoidance learning:
  Acquisition in normal dogs. *Psychological Monographs: General and Applied*,
  67(4), 1-19. https://doi.org/10.1037/h0093649

## Punishment overlay (v1.x) — Overlay combinator

**v1.x:** `Overlay` is a compound combinator that superimposes a punishment
contingency on an existing reinforcement baseline. It takes exactly 2
positional components: the baseline schedule and the punisher schedule.

```
Overlay(VI 60s, FR 1)          -- every response produces punisher on VI 60s baseline
Overlay(Conc(VI 60s, VI 180s, COD=2s), FR 1)  -- punishment on a concurrent baseline
Overlay(Conc(VI 30s, VI 60s, COD=2s), FR 1, target=changeover)
                               -- punishment contingent on changeover responses only
```

- Exactly 2 positional components required. More → `OVERLAY_REQUIRES_TWO`.
- Only `target` keyword arg is permitted. Other keyword args → `INVALID_KEYWORD_ARG`.
- The first component is the reinforcement baseline; the second is the
  punishment schedule. Both schedules operate on the same response stream.

**Semantics.** Responses satisfy both schedules simultaneously. The baseline
schedule delivers reinforcers; the punisher schedule delivers aversive stimuli.
This models the standard punishment paradigm in which a response-contingent
aversive event is added to an ongoing reinforcement schedule.

**Response-class targeting (`target` kw_arg).** Narrows the response class
that the punisher schedule applies to:

- `target=all` (default): the punisher schedule is contingent on every response
  in the baseline. Omitting `target` is identical to `target=all`.
- `target=changeover`: the punisher schedule is contingent only on changeover
  responses (transitions between concurrent components). Requires the baseline
  to be a `Conc` combinator; non-Conc baseline → `TARGET_REQUIRES_CONC`.
  Models Todorov (1971): punishment added to the switching response.

`target` is valid on `Overlay` only; use on other combinators →
`INVALID_OVERLAY_TARGET`. Duplicate `target` → `DUPLICATE_KEYWORD_ARG`.
AST: when `target=changeover`, `params.target` is emitted; when `target=all`
(implicit or explicit), `params.target` is absent (backward-compatible).

References:
- Azrin, N. H., & Holz, W. C. (1966). Punishment. In W. K. Honig (Ed.),
  *Operant behavior: Areas of research and application* (pp. 380-447).
  Appleton-Century-Crofts.
- Todorov, J. C. (1971). Concurrent performances: Effect of punishment
  contingent on the switching response. *JEAB*, 16(1), 51-62.
  https://doi.org/10.1901/jeab.1971.16-51
- Bloomfield, T. M. (1966). Two types of behavioral contrast in
  discrimination learning. *JEAB*, 9(2), 155-161.
  https://doi.org/10.1901/jeab.1966.9-155

## Response-class-specific punishment — PUNISH directive (Conc kw_arg)

`PUNISH` is a Conc keyword argument that attaches a punishment schedule to
a specific response class. Unlike `Overlay + target=changeover`, which layers
a single punisher on a single response class, `PUNISH` supports heterogeneous
punishers across multiple response classes within one `Conc` expression.

### Syntax

```
-- Directional punishment (Todorov, 1971, Exp. 1-2)
Conc(VI 30s, VI 60s, COD=2s, PUNISH(1->2)=FR1, PUNISH(2->1)=FR1)

-- Changeover shorthand (all changeover directions)
Conc(VI 30s, VI 60s, COD=2s, PUNISH(changeover)=FR1)

-- Component-targeted punishment (de Villiers, 1980)
Conc(VI 30s, VI 60s, COD=2s, PUNISH(1)=VI30s)

-- Let-bound identifiers (parallel to directional COD)
let rich = VI30s
let lean = VI60s
Conc(rich, lean, COD=2s, PUNISH(rich->lean)=FR1)
```

The value of `PUNISH` is a `schedule` expression (atomic, compound, modifier,
or special), not a `value` expression. This is the key structural difference
from `scalar_kw_arg` (COD, FRCO, BO) and `directional_kw_arg` (COD).

### Target modes

1. `PUNISH(changeover)`: punisher schedule applied to all changeover responses.
   Mutually exclusive with directional entries.
2. `PUNISH(x->y)`: punisher schedule applied to transitions from component x
   to component y. Multiple directional entries may coexist (enumerate all
   asymmetric directions explicitly rather than combining with `changeover`).
3. `PUNISH(n)`: punisher schedule applied to all responses on component n
   (regardless of source). Independent of directional entries; may coexist.

### Semantic constraints (summary)

- Conc-only; use on other combinators → `INVALID_PUNISH_COMBINATOR`.
- `dir_ref` resolution: 1-indexed integer or let-bound identifier (shares
  resolution rules with directional COD).
- Self-reference `PUNISH(1->1)` → `PUNISH_SELF_REFERENCE`.
- Duplicate target → `DUPLICATE_PUNISH_DIRECTIVE`.
- `PUNISH(changeover)` + `PUNISH(x->y)` → `PUNISH_TARGET_CONFLICT`.
- Out-of-range index → `DIRECTIONAL_INDEX_OUT_OF_RANGE` (shared with COD).
- Nested PUNISH inside a PUNISH schedule → `NESTED_PUNISH_DIRECTIVE`.

### When to use PUNISH vs Overlay + target

| Scenario | Use |
|---|---|
| Single punisher on all responses | `Overlay(baseline, punisher)` |
| Single punisher on all changeovers | `Overlay(Conc(...), punisher, target=changeover)` |
| Asymmetric punishers per direction | `PUNISH(1->2)=..., PUNISH(2->1)=...` |
| Component-specific punishment | `PUNISH(n)=...` |
| Mixed direction + component | `PUNISH(1->2)=..., PUNISH(2)=...` |

References:
- Todorov, J. C. (1971). Concurrent performances: Effect of punishment
  contingent on the switching response. *JEAB*, 16(1), 51-62.
  https://doi.org/10.1901/jeab.1971.16-51
- de Villiers, P. A. (1980). Toward a quantitative theory of punishment.
  *JEAB*, 33(1), 15-25. https://doi.org/10.1901/jeab.1980.33-15
- Farley, J. (1980). Reinforcement and punishment effects in concurrent
  schedules: A test of two models. *JEAB*, 33(3), 311-326.
  https://doi.org/10.1901/jeab.1980.33-311
- Critchfield, T. S., Paletz, E. M., MacAleese, K. R., & Newland, M. C.
  (2003). Punishment in human choice: Direct or competitive suppression?
  *JEAB*, 80(1), 1-27. https://doi.org/10.1901/jeab.2003.80-1

## Timeout (TO) — v2.0

Timeout is a response-contingent removal of reinforcement availability
(negative punishment; Leitenberg, 1965). TO is a postfix qualifier on
schedule expressions, structurally parallel to LH (Limited Hold).

### Syntax

```
VI 60-s TO(duration=30-s, reset_on_response=true)
```

TO follows the base schedule (and optional LH) as a parenthesized keyword
argument list. No `+` operator — same postfix pattern as LH.

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `duration` | time value | YES | — | TO period duration. Must be > 0 with time unit. |
| `reset_on_response` | boolean | YES | — (no default) | Whether responses during TO restart the timer. |
| `contingent_response` | label ref | conditional | — | Which response class triggers TO. Required in multi-operandum contexts. |

### No-default design (reset_on_response)

`reset_on_response` has **no default value**. Omission →
`SemanticError: MISSING_TO_RESET_RULE`. This follows the same design
philosophy as `MISSING_COD` for Conc (grammar.ebnf constraint §7):
procedurally essential information that the DSL refuses to guess.

Rationale: Resetting and non-resetting TO produce qualitatively different
behavioral effects:

- **Resetting TO** (`reset_on_response=true`): Each response during TO
  restarts the timer. Functionally equivalent to DRO (same contingency
  structure, opposite consequence polarity — TO removes reinforcement
  availability, DRO delivers it).
- **Non-resetting TO** (`reset_on_response=false`): Responses during TO
  have no effect on the timer. The timeout period elapses regardless.

### AST representation

TO is absorbed into the inner schedule node as an optional `timeout`
property (a `TimeoutParams` object), not emitted as a separate wrapper.
This is structurally parallel to `limitedHold`/`limitedHoldUnit` for LH.

```json
{
  "type": "Atomic",
  "dist": "V", "domain": "I", "value": 60.0, "time_unit": "s",
  "timeout": {
    "duration": 30.0,
    "durationUnit": "s",
    "resetOnResponse": true
  }
}
```

### Permitted targets

| Target | Allowed | Error/Warning |
|--------|---------|---------------|
| Atomic | YES | — |
| Special (CRF) | YES | — |
| Special (EXT) | YES | WARNING: TO_ON_EXT |
| DRModifier | YES | — |
| SecondOrder | YES | — |
| Compound | NO | SemanticError: TO_ON_COMPOUND |
| AversiveSchedule | NO | SemanticError: TO_ON_AVERSIVE |

### Semantic constraints

See grammar.ebnf constraints §75–§83.

### References

- Leitenberg, H. (1965). Is time-out from positive reinforcement an
  aversive event? *Psychological Bulletin*, 64(6), 428-441.
  https://doi.org/10.1037/h0022657
- Solnick, J. V., Rincover, A., & Peterson, C. R. (1977). Some
  determinants of the reinforcing and punishing effects of timeout.
  *JABA*, 10(3), 415-424.
  https://doi.org/10.1901/jaba.1977.10-415
