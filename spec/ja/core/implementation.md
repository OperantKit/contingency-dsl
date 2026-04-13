# 理論と実装の橋渡し・Legacy 評価

> [contingency-dsl 理論文書](theory.md)の一部。Python 型マッピング、ランタイムブリッジ、OperantKit Legacy の評価をカバーする。

---

## Part V: 理論と実装の橋渡し

### 5.1 Python 型マッピング

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
    # ... 次元クエリ
```

`frozen=True` dataclass はプロジェクト慣習に沿った不変な値セマンティクスを提供する。

### 5.2 代数的データ型

```python
@dataclass(frozen=True)
class AtomicSchedule:
    schedule_type: ScheduleType
    value: float

@dataclass(frozen=True)
class CompoundSchedule:
    combinator: str  # "Conc" | "Alt" | "Conj" | "Chain" | "Tand" | "Mult" | "Mix"
    components: tuple[ScheduleExpr, ...]
    params: dict[str, Any] | None = None  # v1.1: {"COD": {"value": 2.0, "time_unit": "s"}, "FRCO": {"value": 5}}

@dataclass(frozen=True)
class ModifierSchedule:
    modifier: str  # "DRL" | "DRH" | "DRO" | "PR" | "Repeat" | "Lag"
    value: float | None = None
    inner: ScheduleExpr | None = None  # Repeat 用
    length: int | None = None  # Lag 用（sequence length, default 1）
    # PR 固有フィールド...

@dataclass(frozen=True)
class LimitedHoldSchedule:
    inner: ScheduleExpr
    hold_duration: float  # 秒; > 0 必須（制約 62）; 非正値は LH_NONPOSITIVE_VALUE

@dataclass(frozen=True)
class AversiveSchedule:
    kind: str  # "Sidman" (v1.x); 将来: "DiscrimAv", "Escape", ...
    params: dict[str, Any]  # v1.x Sidman: {"SSI": {"value": 20.0, "time_unit": "s"}, "RSI": {"value": 5.0, "time_unit": "s"}}

ScheduleExpr = Union[AtomicSchedule, CompoundSchedule, ModifierSchedule, LimitedHoldSchedule, AversiveSchedule]
```

### 5.3 `to_schedule()` ブリッジ

現在のモノリシックな if-elif チェーンは構造的パターンマッチ（Python 3.10+）で置き換えるべきである:

```python
def to_runtime(expr: ScheduleExpr) -> Schedule:
    match expr:
        case AtomicSchedule(ScheduleType(Distribution.FIXED, Domain.RATIO), n):
            return FixedRatio(target=int(n))
        case AtomicSchedule(ScheduleType(Distribution.VARIABLE, Domain.INTERVAL), t):
            return VariableInterval(targets=generate_intervals(t, ...))
        case CompoundSchedule("Conc", components):
            return ConcurrentSchedule([to_runtime(c) for c in components])
        case CompoundSchedule("Chain", components):
            return ChainedSchedule([to_runtime(c) for c in components])
        # ...
```

### 5.4 不足しているランタイム型

contingency-py に現在欠けているもの:
- `RandomRatio`, `RandomInterval`, `RandomTime`（OperantKit Swift に実装あり: `RR.swift`, `RI.swift`, `RT.swift`）
- `Distribution` / `Domain` enum
- `CRF` 便利エイリアス（`FixedRatio(target=1)`）

Random スケジュールは Swift のパターンに従う: `RR(n)` は各 `next()` 呼び出しで `random.randint(1, n)` を生成し、`VR(n)` は事前計算された Fleshler-Hoffman 系列からドローする。

---

## Part VI: Legacy 評価

### 6.1 Legacy が正しく行ったこと

1. **2次元型体系。** `PrepositionSchedule × PostpositionSchedule` は Distribution と Domain の根本的な独立性を捉えた理論的に健全な分解である。

2. **ビルダー API。** `ScheduleBuilder.swift` は文献に合致した API（`FR(5)`, `Conc(FR(5), VI(30))`）を提供する — Python DSL にとって正確に正しい API 面である。

3. **プロトコル指向設計。** `ScheduleUseCase` は全スケジュール（原子・複合）に対する統一インターフェースを定義し、多態的合成を可能にする。

4. **複合スケジュールの Template Method。** `CompoundScheduleUseCaseBase` は共有の `updateValue()` ロジックを提供し、個々の複合型は `decision()` のみをオーバーライドする。

5. **EXT = 零元。** `rawValue = 0` の選択は代数的に正しく、分類クエリを支援する。

### 6.2 改善すべき点

1. **ビットパック → enum ペア。** UInt64 エンコーディングは Swift 的（`OptionSet`）だが Python では不要。次元的クエリ可能性を保持しつつ enum ペアに置き換える。

2. **フラット ScheduleConfig → 代数的 ADT。** 現在の `ScheduleConfig`（12個のオプショナルフィールドを持つ単一 Pydantic モデル）はスケーラブルでない。ADT アプローチにより無関係なフィールドが排除される。

3. **Concurrent のみ → 全7結合子。** contingency-py は既に全7を実装しているが、DSL v0.1 は Concurrent しか公開していない。

4. **DR の形式化。** DR スケジュールは追加的な格子エントリとしてではなく、3×3 格子と直交する修飾子/フィルタとして明示的にモデル化すべきである。

5. **Random スケジュールの欠如。** RR, RI, RT は Swift で実装済みだが contingency-py には存在しない。

---

## 参考文献

- Catania, A. C. (2013). *Learning* (5th ed.). Sloan Publishing.
- Farmer, J. (1963). Properties of behavior under random interval reinforcement schedules. *Journal of the Experimental Analysis of Behavior*, 6(4), 607-616. https://doi.org/10.1901/jeab.1963.6-607
- Ferster, C. B., & Skinner, B. F. (1957). *Schedules of reinforcement*. Appleton-Century-Crofts.
- Findley, J. D. (1958). Preference and switching under concurrent scheduling. *Journal of the Experimental Analysis of Behavior*, 1(2), 123-144. https://doi.org/10.1901/jeab.1958.1-123
- Fleshler, M., & Hoffman, H. S. (1962). A progression for generating variable-interval schedules. *Journal of the Experimental Analysis of Behavior*, 5(4), 529-530. https://doi.org/10.1901/jeab.1962.5-529
- Herrnstein, R. J. (1961). Relative and absolute strength of response as a function of frequency of reinforcement. *Journal of the Experimental Analysis of Behavior*, 4(3), 267-272. https://doi.org/10.1901/jeab.1961.4-267
- Herrnstein, R. J., & Loveland, D. H. (1975). Maximizing and matching on concurrent ratio schedules. *Journal of the Experimental Analysis of Behavior*, 24(1), 107-116. https://doi.org/10.1901/jeab.1975.24-107
- Herrnstein, R. J., & Vaughan, W. (1980). Melioration and behavioral allocation. In J. E. R. Staddon (Ed.), *Limits to action: The allocation of individual behavior* (pp. 143-176). Academic Press.
- Baum, W. M., Aparicio, C. F., & Alonso-Alvarez, B. (2022). Rate matching, probability matching, and optimization in concurrent ratio schedules. *Journal of the Experimental Analysis of Behavior*, 118(1). https://doi.org/10.1002/jeab.771
- Mizutani, Y. (2018). OperantKit: A Swift framework for reinforcement schedule simulation [Computer software]. GitHub. https://github.com/YutoMizutani/OperantKit
- Rescorla, R. A., & Wagner, A. R. (1972). A theory of Pavlovian conditioning: Variations in the effectiveness of reinforcement and nonreinforcement. In A. H. Black & W. F. Prokasy (Eds.), *Classical conditioning II: Current research and theory* (pp. 64-99). Appleton-Century-Crofts.
- Schoenfeld, W. N., & Cole, B. K. (1972). *Stimulus schedules: The t-τ systems*. Harper & Row.
- Sidman, M. (1960). *Tactics of scientific research*. Basic Books.
- Skinner, B. F. (1948). 'Superstition' in the pigeon. *Journal of Experimental Psychology*, 38(2), 168-172. https://doi.org/10.1037/h0055873
