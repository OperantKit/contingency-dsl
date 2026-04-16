# Operant.Stateful Admission Gate

> Pointer file. The admission criteria for the `operant/stateful/` sublayer (disciplinary-establishment N1/N2/N3, evidence E1–E5) are defined in `spec/en/design-philosophy.md §2.1`. This file exists to provide a navigable entry point from the `operant/stateful/` directory without duplicating the criteria.

---

## Where the Admission Criteria Live

The canonical source for the admission gate is **`spec/en/design-philosophy.md §2.1`**, titled *Operant.Stateful Admission Gate*.

That section specifies:

- The structural distinction within the Operant layer (Operant.Literal vs Operant.Stateful).
- The admission gate requiring (1) disciplinary-establishment criteria N1/N2/N3 and (2) declarative parameters.
- The disciplinary-establishment criteria: N1 (named procedure), N2 (primary literature), N3 (temporal persistence, 20+ years, ≥ 2 decades).
- The evidence-score criteria (≥ 3/5 across E1 JEAB/JABA publication, E2 cross-laboratory replication, E3 textbook inclusion, E4 parametric study or theoretical integration, E5 applied/translational use).
- The four-step promotion process (proposal → review → implementation → recording).
- The current Operant.Stateful constituents (Percentile, Adjusting, Interlocking).

## How to Use This Sublayer

If you are proposing a new schedule for promotion to `operant/stateful/`:

1. Read `spec/en/design-philosophy.md §2.1` in full.
2. Prepare an RFC per the four-step process.
3. Once approved, add the schedule's specification file under `spec/en/operant/stateful/<name>.md`, following the template set by the existing three files (`percentile.md`, `adjusting.md`, `interlocking.md`).
4. Update the constituents table in `design-philosophy.md §2.1`.

## Why This File Is Separate

Each sublayer's admission gate is a shared, cross-cutting policy — not a feature of any one schedule. Repeating the criteria in every `operant/stateful/*.md` file would create duplication hazards; placing the criteria in a single authoritative section (`design-philosophy.md §2.1`) and pointing to it from the sublayer directory keeps the specification DRY.
