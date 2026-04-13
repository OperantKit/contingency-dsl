# Theory-Implementation Bridge and Legacy Assessment

> Part of the [contingency-dsl theory documentation](theory.md). Covers Python type mapping, runtime bridge, and OperantKit legacy evaluation.

---

## 5.1 Python Type Mapping

```python
from enum import Enum
from dataclasses import dataclass, field
from typing import Union

class Distribution(Enum):
    FIXED = "fixed"
    VARIABLE = "variable"
    RANDOM = "random"

class Domain(Enum):
    RATIO = "ratio"
    INTERVAL = "interval"
    TIME = "time"

@dataclass(frozen=True)
class ScheduleType:
    distribution: Distribution
    domain: Domain

    def has_fixed(self) -> bool:
        return self.distribution == Distribution.FIXED
    def has_ratio(self) -> bool:
        return self.domain == Domain.RATIO
    # ... dimensional queries
```

The `frozen=True` dataclass provides immutable value semantics consistent with the project convention.

## 5.2 Algebraic Data Type

```python
@dataclass(frozen=True)
class AtomicSchedule:
    schedule_type: ScheduleType
    value: float

@dataclass(frozen=True)
class CompoundSchedule:
    combinator: str  # "Conc" | "Alt" | "Conj" | "Chain" | "Tand" | "Mult" | "Mix"
    components: tuple[ScheduleExpr, ...]
    params: dict[str, Any] | None = None
    # v1.1 params examples:
    #   Symmetric COD:    {"COD": {"value": 2.0, "time_unit": "s"}}
    #   Directional COD:  {"COD": {"base": {...}, "directional": [{"from": 2, "to": 1, "value": 5.0, ...}]}}
    #   FRCO:             {"FRCO": {"value": 5}}

@dataclass(frozen=True)
class ModifierSchedule:
    modifier: str  # "DRL" | "DRH" | "DRO" | "PR" | "Repeat" | "Lag"
    value: float | None = None
    inner: ScheduleExpr | None = None  # for Repeat
    length: int | None = None  # for Lag (sequence length, default 1)
    # PR-specific fields...

@dataclass(frozen=True)
class LimitedHoldSchedule:
    hold_duration: float      # seconds; must be >= 0
    inner: ScheduleExpr       # the wrapped schedule

@dataclass(frozen=True)
class AversiveSchedule:
    kind: str  # "Sidman" (v1.x); future: "DiscrimAv", "Escape", ...
    params: dict[str, Any]  # v1.x Sidman: {"SSI": {"value": 20.0, "time_unit": "s"}, "RSI": {"value": 5.0, "time_unit": "s"}}

ScheduleExpr = Union[AtomicSchedule, CompoundSchedule, ModifierSchedule, LimitedHoldSchedule, AversiveSchedule]
```

## 5.3 The `to_schedule()` Bridge

The current monolithic if-elif chain should be replaced by structural pattern matching (Python 3.10+):

```python
def to_runtime(expr: ScheduleExpr) -> Schedule:
    match expr:
        case AtomicSchedule(ScheduleType(Distribution.FIXED, Domain.RATIO), n):
            return FixedRatio(target=int(n))
        case AtomicSchedule(ScheduleType(Distribution.VARIABLE, Domain.INTERVAL), t):
            return VariableInterval(targets=generate_intervals(t, ...))
        case CompoundSchedule("Conc", components, params):
            cod = params.get("COD") if params else None
            frco = params.get("FRCO") if params else None
            # Directional COD: "directional" key = per-(from,to) overrides
            # Symmetric COD: "value" key = uniform delay
            if cod and "directional" in cod:
                base = cod.get("base", {}).get("value", 0.0)
                n = len(components)
                # Build n×n matrix; diagonal unused
                cod_matrix = [[base] * n for _ in range(n)]
                for entry in cod["directional"]:
                    cod_matrix[entry["from"] - 1][entry["to"] - 1] = entry["value"]
            elif cod:
                cod_matrix = None  # symmetric — single value
                base = cod["value"]
            else:
                cod_matrix = None
                base = None
            return ConcurrentSchedule(
                [to_runtime(c) for c in components],
                changeover_delay=base,
                changeover_delay_matrix=cod_matrix,
                changeover_ratio=frco["value"] if frco else None,
            )
        case CompoundSchedule("Chain", components, _):
            return ChainedSchedule([to_runtime(c) for c in components])
        # ...
```

## 5.4 Missing Runtime Types

contingency-py currently lacks:
- `RandomRatio`, `RandomInterval`, `RandomTime` (present in OperantKit Swift: `RR.swift`, `RI.swift`, `RT.swift`)
- `Distribution` / `Domain` enums
- `CRF` convenience alias (`FixedRatio(target=1)`)

The Random schedules follow the Swift pattern: `RR(n)` generates `random.randint(1, n)` on each `next()` call, while `VR(n)` draws from a pre-computed Fleshler-Hoffman sequence.

---

## 6. Legacy Assessment

### 6.1 What the Legacy Got Right

1. **The 2D type system.** `PrepositionSchedule × PostpositionSchedule` is a theoretically grounded decomposition that captures the fundamental independence of Distribution and Domain.

2. **The builder API.** `ScheduleBuilder.swift` provides a literature-matching API (`FR(5)`, `Conc(FR(5), VI(30))`) — exactly the right surface for the Python DSL.

3. **Protocol-oriented design.** `ScheduleUseCase` defines a uniform interface for all schedules (atomic and compound), enabling polymorphic composition.

4. **Template Method for compounds.** `CompoundScheduleUseCaseBase` provides shared `updateValue()` logic while individual compounds override `decision()`.

5. **EXT as zero.** The `rawValue = 0` choice is algebraically correct and aids classification queries.

### 6.2 What Can Be Improved

1. **Bit-packing → enum pairs.** The UInt64 encoding was idiomatic Swift (`OptionSet`) but unnecessary in Python. Replace with enum pairs preserving dimensional queryability.

2. **Flat ScheduleConfig → algebraic ADT.** The current `ScheduleConfig` (a single Pydantic model with 12 optional fields) does not scale. The ADT approach eliminates irrelevant fields.

3. **Concurrent-only → all 7 combinators.** contingency-py already implements all 7, but the DSL v0.1 only exposes Concurrent.

4. **DR formalization.** DR schedules should be explicitly modeled as modifiers/filters orthogonal to the 3×3 grid, not as additional grid entries.

5. **Missing Random schedules.** RR, RI, RT are implemented in Swift but absent from contingency-py.

---

## References

- Mizutani, Y. (2018). OperantKit: A Swift framework for reinforcement schedule simulation [Computer software]. GitHub. https://github.com/YutoMizutani/OperantKit
