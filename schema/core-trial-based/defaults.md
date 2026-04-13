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

References:
- Cumming, W. W., & Berryman, R. (1965). The complex discriminated operant:
  Studies of matching-to-sample and related problems. In D. I. Mostofsky
  (Ed.), *Stimulus generalization* (pp. 284-330). Stanford University Press.
- Sidman, M., & Tailby, W. (1982). Conditional discrimination vs.
  matching to sample: An expansion of the testing paradigm. *JEAB*,
  37(1), 5-22. https://doi.org/10.1901/jeab.1982.37-5
