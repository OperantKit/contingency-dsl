# Progressive Ratio (PR) and Progressive-Interval Schedules

> Part of the contingency-dsl operant layer. Meta-schedules whose parameter itself changes according to a deterministic step function indexed by the number of reinforcements delivered.

---

## 1. Scope

A **progressive schedule** is a schedule whose parameter increases (or, in principle, decreases) across successive reinforcements according to a fixed step function. The canonical member is **Progressive Ratio (PR)**, introduced by Hodos (1961). Progressive-interval variants follow the same design logic (Hodos & Kalman, 1963).

```
PR(step : ℕ → ℕ) = FR(step(n)) where n increments after each reinforcement
```

PR is a **schedule functor** — it maps a step function to a sequence of FR schedules.

## 2. Syntax

The DSL offers two syntactic forms:

```
-- Shorthand: arithmetic progression with step size n
PR 5                                   -- Jarmolowicz & Lattal (2010)
                                       -- expands to PR(linear, start=5, increment=5)
                                       -- produces FR 5, FR 10, FR 15, ...

-- Explicit: full control over the step function
PR(hodos)                              -- Hodos (1961) step progression
PR(linear, start=1, increment=5)       -- arithmetic progression
PR(exponential)                        -- exponential progression
PR(geometric, start=1, ratio=2)        -- geometric (doubling)
```

Bare `PR` without a number or parenthesized options is a parse error.

## 3. Step Functions

| Step form | Example | Progression |
|---|---|---|
| `hodos` | `PR(hodos)` | Hodos (1961) original irregular step sequence |
| `linear`, `start=a`, `increment=d` | `PR(linear, start=5, increment=5)` | `a, a+d, a+2d, ...` |
| `exponential` | `PR(exponential)` | exponential per-reinforcement growth |
| `geometric`, `start=a`, `ratio=r` | `PR(geometric, start=1, ratio=2)` | `a, a·r, a·r², ...` |

Arithmetic and geometric progressions produce qualitatively different response-rate functions; no consensus default step function exists in the literature (Killeen et al., 2009; Stafford & Branch, 1998). The DSL requires explicit specification — bare `PR` is not permitted.

## 4. Breakpoint

The **breakpoint** is the ratio value beyond which the subject ceases responding — an emergent behavioral measure, not a DSL parameter. Historically the breakpoint was treated as synonymous with the "maximum effective ratio" (Pmax), but this conflation is increasingly recognized as problematic (Lambert et al., 2026). The DSL records only the procedural structure; breakpoint estimation belongs to the analysis layer.

## 5. Progressive-Interval

Progressive-interval schedules follow the analogous logic: the interval parameter increases across successive reinforcements per a step function. These are less common in the literature than PR and are accommodated by the same step-function syntax applied to FI:

```
-- Progressive FI (Hodos & Kalman, 1963)-style arrangements are currently expressed
-- through the Experiment Layer's `progressive` declaration rather than as a
-- schedule-level primitive. See experiment/phase-sequence.md for across-session
-- parametric progression.
```

This is a deliberate design decision: the Progressive Ratio primitive is anchored at the schedule level because PR operates *within* a session (the ratio increments on every reinforcement); progressive-interval training designs typically operate across sessions and are therefore expressed at the experiment layer.

## 6. Second-Order Progressive Ratio

`PR` can be composed with unit schedules, creating a second-order arrangement where each PR step counts unit completions:

```
PR(linear, start=5, increment=5)         -- first-order PR on individual responses
                                        -- (sessions 1..N: 5, 10, 15, ...)
```

A second-order PR (`PR_n(Unit)`) is expressible through the `SecondOrder` construction (`operant/theory.md §2.11`) combined with PR semantics.

## 7. Errors and Warnings

| Code | Condition | Severity |
|---|---|---|
| `PR_MISSING_STEP` | Bare `PR` without number or parenthesized options | SemanticError |
| `PR_NONPOSITIVE_START` | `start ≤ 0` | SemanticError |
| `PR_NONPOSITIVE_INCREMENT` | `increment ≤ 0` | SemanticError |
| `PR_NONPOSITIVE_RATIO` | `ratio ≤ 0` for geometric | SemanticError |
| `PR_UNKNOWN_STEP` | Step keyword not in `{hodos, linear, exponential, geometric}` | SemanticError |

See `conformance/operant/errors.json` for the full registry.

## 8. PR vs Adjusting (Adj)

| | PR(linear, start=1, increment=5) | Adj(ratio, start=5, step=2) |
|---|---|---|
| Direction | Monotonic increase only | Bidirectional (behavior-dependent) |
| Change rule | Deterministic (fixed increment each reinforcement) | Behavior-dependent (recent performance) |
| Convergence | None (increases until breakpoint) | Yes (indifference point) |
| Layer | Operant.Literal (schedules/) | Operant.Stateful (stateful/) |

See `operant/stateful/adjusting.md` for the Adjusting counterpart. The distinguishing criterion: PR's step function is deterministic and indexed only by reinforcement count; Adj's step is conditioned on recent trial outcomes.

## 9. Design Decisions

PR was brought into the DSL as a first-class modifier rather than a degenerate `Tand(FR 5, FR 10, FR 15, ...)` because:

1. The step-function abstraction is procedurally irreducible — the researcher specifies "how the ratio grows," not the individual ratio values.
2. Literature-standard notations (`PR 5`, `PR(hodos)`) must parse directly.
3. Breakpoint is a dependent measure tied to the PR primitive; preserving the primitive preserves the analytical bridge.

See `docs/en/design-rationale.md §2` for the historical discussion of why the step function must be explicit.

## References

- Hodos, W. (1961). Progressive ratio as a measure of reward strength. *Science*, 134(3483), 943–944. https://doi.org/10.1126/science.134.3483.943
- Hodos, W., & Kalman, G. (1963). Effects of increment size and reinforcer volume on progressive ratio performance. *Journal of the Experimental Analysis of Behavior*, 6(3), 387–392. https://doi.org/10.1901/jeab.1963.6-387
- Jarmolowicz, D. P., & Lattal, K. A. (2010). On distinguishing progressive increasing response requirements for reinforcement. *The Behavior Analyst*, 33(1), 119–125. https://doi.org/10.1007/BF03392206
- Killeen, P. R., Posadas-Sanchez, D., Johansen, E. B., & Thrailkill, E. A. (2009). Progressive ratio schedules of reinforcement. *Journal of Experimental Psychology: Animal Behavior Processes*, 35(1), 35–50. https://doi.org/10.1037/a0012497
- Stafford, D., & Branch, M. N. (1998). Effects of step size and break-point criterion on progressive-ratio performance. *Journal of the Experimental Analysis of Behavior*, 70(2), 123–138. https://doi.org/10.1901/jeab.1998.70-123
