# contingency-dsl Core-TrialBased Defaults

Explicit documentation of all implicit defaults in the Core-TrialBased layer.
When a parameter is omitted, the following values apply.

## Matching-to-Sample (MTS)

### Incorrect response consequence

| Written | Default | Rationale |
|---------|---------|-----------|
| `MTS(comparisons=3, consequence=CRF, ITI=5s)` | `incorrect=EXT` | Extinction is the standard consequence for incorrect selections in MTS procedures (Sidman & Tailby, 1982). Non-reinforcement of incorrect responses is the procedural baseline; explicit punishment or correction requires deliberate specification. |

### Matching type

| Written | Default | Rationale |
|---------|---------|-----------|
| `MTS(comparisons=3, consequence=CRF, ITI=5s)` | `type=arbitrary` | Arbitrary matching (class-based) is the more general case. Identity matching is a special case where sample and correct comparison are physically identical. Defaulting to arbitrary avoids false assumptions about stimulus relations. |

### Linter interactions with defaults

| Condition | Code | Rationale |
|-----------|------|-----------|
| `type` omitted (default `arbitrary`) and no `@stimulus_classes` annotation | `MTS_ARBITRARY_WITHOUT_CLASSES` | Arbitrary MTS requires class definitions for the runtime to determine correctness. The default type triggers this warning when classes are absent. |
| `incorrect` omitted (default `EXT`) | No warning | EXT is the standard procedural default. No warning emitted. |

### Parameters with no default (all required)

| Parameter | Why no default |
|-----------|---------------|
| `comparisons` | Number of comparison stimuli is a fundamental procedural parameter that varies across experiments (Cumming & Berryman, 1965). No single value is standard. |
| `consequence` | Reinforcement schedule for correct responses must be explicitly specified. CRF is common but not universal (e.g., intermittent reinforcement in probe trials). |
| `ITI` | Inter-trial interval varies widely across preparations (1 s to 30+ s). No principled default exists. |

---

## Go/No-Go Discrimination (GoNoGo)

### Incorrect consequence

| Written | Default | Rationale |
|---------|---------|-----------|
| `GoNoGo(responseWindow=5s, consequence=CRF, ITI=10s)` | `incorrect=EXT` | Extinction is the standard consequence for errors (miss and false alarm) in Go/No-Go procedures. Non-reinforcement of errors is the procedural baseline; explicit timeout or correction requires deliberate specification. |

### False alarm consequence

| Written | Default | Rationale |
|---------|---------|-----------|
| `GoNoGo(responseWindow=5s, consequence=CRF, ITI=10s)` | `falseAlarm=EXT` (= incorrect) | By default, false alarms receive the same consequence as misses. Nevin (1969) demonstrated SDT-style arrangements where false alarms produce timeout while misses produce extinction — the `falseAlarm` parameter enables this asymmetric arrangement without changing `incorrect`. |

### Correct rejection (implicit, not a parameter)

| Outcome | Value | Rationale |
|---------|-------|-----------|
| Correct rejection (NoGo + no response) | EXT (fixed) | No programmed consequence for correctly withholding a response. This is the standard Go/No-Go procedure (Dinsmoor, 1995a). Not configurable in v1; future extension reserved. |

### Linter interactions with defaults

| Condition | Code | Rationale |
|-----------|------|-----------|
| `falseAlarm` specified but `incorrect` omitted (default `EXT`) | `GONOGO_FALSE_ALARM_WITHOUT_INCORRECT` | User explicitly differentiated false alarm consequence but left miss consequence at default EXT. May be intentional (SDT-style) — warning, not error. |

### Parameters with no default (all required)

| Parameter | Why no default |
|-----------|---------------|
| `responseWindow` | Duration of response opportunity varies widely across preparations (500 ms to 30+ s). No single value is standard. This is the structural parameter that defines Go/No-Go as a discrete-trial procedure. |
| `consequence` | Reinforcement schedule for hits must be explicitly specified. CRF is common but not universal (e.g., intermittent reinforcement in maintenance phases). |
| `ITI` | Inter-trial interval varies widely across preparations (1 s to 30+ s). No principled default exists. |

---

## References

- Cumming, W. W., & Berryman, R. (1965). The complex discriminated operant:
  Studies of matching-to-sample and related problems. In D. I. Mostofsky
  (Ed.), *Stimulus generalization* (pp. 284-330). Stanford University Press.
- Dinsmoor, J. A. (1995a). Stimulus control: Part I. *The Behavior
  Analyst*, *18*(1), 51-68.
- Nevin, J. A. (1969). Signal detection theory and operant behavior.
  *Journal of the Experimental Analysis of Behavior*, *12*(3), 475-480.
  https://doi.org/10.1901/jeab.1969.12-475
- Sidman, M., & Tailby, W. (1982). Conditional discrimination vs.
  matching to sample: An expansion of the testing paradigm. *JEAB*,
  37(1), 5-22. https://doi.org/10.1901/jeab.1982.37-5
