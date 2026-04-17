# オペラント層 — 理論-実装ブリッジとレガシー評価

> contingency-dsl オペラント層（Ψ）の一部。オペラント・スケジュール式のための Python 型マッピング、ランタイムブリッジ、OperantKit レガシー評価を扱う。オペラント理論は [theory.md](theory.md)、オペラント EBNF は [grammar.md](grammar.md) を参照。

---

## 5.1 Python 型マッピング

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
    # ... 次元的問い合わせ
```

`frozen=True` な dataclass により、プロジェクト規約に沿った不変値セマンティクスが得られる。

## 5.2 代数的データ型

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
    # params 例:
    #   対称 COD:    {"COD": {"value": 2.0, "time_unit": "s"}}
    #   方向性 COD:  {"COD": {"base": {...}, "directional": [{"from": 2, "to": 1, "value": 5.0, ...}]}}
    #   FRCO:        {"FRCO": {"value": 5}}

@dataclass(frozen=True)
class ModifierSchedule:
    modifier: str  # "DRL" | "DRH" | "DRO" | "PR" | "Repeat" | "Lag"
    value: float | None = None
    inner: ScheduleExpr | None = None  # Repeat 用
    length: int | None = None  # Lag 用（系列長、デフォルト 1）
    # PR 固有フィールド...

@dataclass(frozen=True)
class LimitedHoldSchedule:
    hold_duration: float      # 秒; > 0 でなければならない（制約 62）
    inner: ScheduleExpr       # ラップされるスケジュール

@dataclass(frozen=True)
class AversiveSchedule:
    kind: str  # "Sidman"（現行）、将来: "DiscrimAv", "Escape", ...
    params: dict[str, Any]  # Sidman: {"SSI": {"value": 20.0, "time_unit": "s"}, "RSI": {"value": 5.0, "time_unit": "s"}}

ScheduleExpr = Union[AtomicSchedule, CompoundSchedule, ModifierSchedule, LimitedHoldSchedule, AversiveSchedule]
```

## 5.3 `to_schedule()` ブリッジ

現行のモノリシックな if-elif 連鎖は、構造的パターンマッチング（Python 3.10+）に置き換えるべきである。

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
            # 方向性 COD: "directional" キー = (from,to) ごとの上書き
            # 対称 COD: "value" キー = 一様な遅延
            if cod and "directional" in cod:
                base = cod.get("base", {}).get("value", 0.0)
                n = len(components)
                # n×n 行列構築; 対角成分は未使用
                cod_matrix = [[base] * n for _ in range(n)]
                for entry in cod["directional"]:
                    cod_matrix[entry["from"] - 1][entry["to"] - 1] = entry["value"]
            elif cod:
                cod_matrix = None  # 対称 — 単一値
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

## 5.4 欠落ランタイム型

contingency-py は現状、以下を欠いている。

- `RandomRatio`, `RandomInterval`, `RandomTime`（OperantKit Swift 版に存在: `RR.swift`, `RI.swift`, `RT.swift`）
- `Distribution` / `Domain` 列挙型
- `CRF` の利便エイリアス（`FixedRatio(target=1)`）

Random スケジュールは Swift パターンに従う。`RR(n)` は `next()` 呼び出しごとに `random.randint(1, n)` を生成する一方、`VR(n)` は事前計算された Fleshler-Hoffman 系列からドローする。

---

## 6. レガシー評価

### 6.1 レガシーが正しく行っていた点

1. **2 次元型システム.** `PrepositionSchedule × PostpositionSchedule` は、Distribution と Domain の基本的な独立性を捉えた、理論的に根拠のある分解である。

2. **ビルダー API.** `ScheduleBuilder.swift` は、文献に合致する API（`FR(5)`, `Conc(FR(5), VI(30))`）を提供し、Python DSL の表層として的確である。

3. **プロトコル指向設計.** `ScheduleUseCase` はすべてのスケジュール（アトミックおよび合成）に対して一様なインターフェースを定義し、多相的な合成を可能にする。

4. **合成のための Template Method.** `CompoundScheduleUseCaseBase` は共有された `updateValue()` ロジックを提供し、個別の合成が `decision()` をオーバーライドする。

5. **ゼロとしての EXT.** `rawValue = 0` の選択は代数的に正しく、分類問い合わせを助ける。

### 6.2 改善可能な点

1. **ビットパッキング → 列挙ペア.** UInt64 符号化は Swift では慣用的（`OptionSet`）だが、Python では不要である。次元的問い合わせ可能性を保つ列挙ペアに置き換える。

2. **フラットな ScheduleConfig → 代数的 ADT.** 現行の `ScheduleConfig`（12 個のオプショナルフィールドを持つ単一 Pydantic モデル）はスケールしない。ADT アプローチは無関係なフィールドを排除する。

3. **Concurrent のみ → 7 コンビネータ全体.** contingency-py は 7 つすべてを既に実装しているが、DSL v0.1 は Concurrent のみを露出している。

4. **DR の形式化.** DR スケジュールは、3×3 格子への追加エントリとしてではなく、格子と直交する修飾子／フィルタとして明示的にモデル化すべきである。

5. **欠落 Random スケジュール.** RR, RI, RT は Swift で実装されているが、contingency-py には存在しない。

---

## 参考文献

- Mizutani, Y. (2018). OperantKit: A Swift framework for reinforcement schedule simulation [Computer software]. GitHub. https://github.com/YutoMizutani/OperantKit
