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
```

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

## Progressive Ratio step function

| Written | Default | Notes |
|---------|---------|-------|
| `PR` | `hodos` | Hodos & Kalman (1963) step function |
| `PR(linear)` | `start=1, increment=5` | Linear default parameters |

## Limited Hold

| Written | Behavior |
|---------|----------|
| No `LH` specified | No availability window (infinite hold) |
| `LimitedHold = 10s` (program-level) | Applied individually to all leaf base_schedules |
| `FI30 LH10` (expression-level) | Overrides program-level default for that expression |

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
- Default behavior: symmetric, non-resetting.
- COD and FRCO may coexist: `Conc(VI30s, VI60s, COD=2s, FRCO=5)`.

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

## Timeout (TO) — design memo (v2.0 planned)

TO is deferred to v2.0. When implemented, the following constraints apply
(Issue #28):

- `reset_on_response` is **mandatory** (no default value).
  `TO(30s)` without reset specification → `SemanticError: MISSING_RESET_RULE`.
  This follows the same design philosophy as `MISSING_COD` for Conc.
- Resetting TO is functionally equivalent to DRO (same contingency structure,
  opposite consequence polarity).

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `duration` | time value | YES | TO duration |
| `reset_on_response` | boolean | YES (no default) | Whether responses during TO restart the timer |
| `contingent_response` | response class ref | YES (multi-operandum) | Which response class triggers TO |
