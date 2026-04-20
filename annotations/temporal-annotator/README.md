# temporal-annotator — Temporal & Algorithmic Setup

## Purpose

Declares the **temporal frame** and **algorithmic parameter generation**
for a session: time-unit conventions, warm-up exclusions, and the
algorithm used to materialise stochastic schedule values (VI/VR/RI/RR/VT).

Corresponds to the portion of a JEAB Procedure section that describes
session timing and the method used to derive interval/ratio series. The
declarations are *intent only* — the runtime resolves the declared clock
against hardware, and the declared algorithm against a generator
implementation.

Boundary: this annotator does **not** describe session-runtime IO (that
is the responsibility of `experiment-io`), and it does **not** describe
dependent measures or session-end rules (that is the responsibility of
`measurement-annotator`).

This annotator is part of the **core recommended vocabulary** maintained
by the DSL project. Per
[design-philosophy.md §4.2](../../spec/en/design-philosophy.md), third-party
programs retain the freedom to reinterpret or replace these categories, but
the DSL project supplies and maintains the reference implementation in
[`contingency-dsl-py`](../../../contingency-dsl-py/) and
[`contingency-dsl-rs`](../../../contingency-dsl-rs/).

---

## Status

`Design`

---

## Category

- [x] **Setup** — procedure-foundations: clock, warm-up, parameter generator

---

## Keywords

| Keyword | Purpose | Example |
|---|---|---|
| `@clock(unit)` | Declares the session time unit. Required at program level when not implicit in literals. | `@clock(unit="s")` |
| `@warmup(duration)` | Initial period excluded from response/reinforcement records. | `@warmup(duration=300)` |
| `@algorithm(name, n?, seed?)` | Selects the parameter-generation algorithm for stochastic schedules. | `@algorithm("fleshler-hoffman", n=12, seed=42)` |

## Scope and attachment

All three keywords are **program-level** annotations placed in the
preamble. They modify the surrounding program rather than any single
schedule node, and surface in the AST under `program_annotations`.

## Validation rules

- `@clock` `unit` must be one of the enum values `s`, `ms`, `min`.
- `@warmup` `duration` must be a non-negative number expressed in the
  declared clock unit.
- `@algorithm` positional `name` must be a known generator
  (`fleshler-hoffman`, `arithmetic`); optional `n` is a positive integer
  series length; optional `seed` is an integer for reproducibility.
- `@algorithm` is meaningful only for stochastic schedules
  (`V`/`R`-distribution); attaching it to a program that contains only
  fixed schedules is a warning, not an error.

## Cross-references

- The **clock** declaration is consumed by `experiment-io`, which binds
  the declared unit to a concrete hardware clock at session start.
- The **algorithm** declaration is consumed by `contingency-py`, which
  selects a parameter generator (e.g. Fleshler–Hoffman series) when
  materialising a stochastic schedule.
- The **warmup** declaration is consumed jointly by `experiment-io`
  (to gate session start) and `measurement-annotator` (to align with
  `@warmup_exclude`-style measurement filters).

This annotator declares the *intent*; the runtime layers resolve it.

## References

- Fleshler, M., & Hoffman, H. S. (1962). A progression for generating variable-interval schedules. *Journal of the Experimental Analysis of Behavior*, 5(4), 529–530. https://doi.org/10.1901/jeab.1962.5-529
- Hantula, D. A. (1991). A progression for generating variable-interval schedules. *Journal of the Experimental Analysis of Behavior*, 56(2), 391–392. https://doi.org/10.1901/jeab.1991.56-391

## Reference implementation

[`contingency_dsl.annotations.temporal`](../../../contingency-dsl-py/src/contingency_dsl/annotations/temporal/).
