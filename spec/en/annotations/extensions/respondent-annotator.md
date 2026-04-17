# respondent-annotator — Annotation Extension for Respondent Procedures

> Part of the contingency-dsl annotation layer. Documents the four respondent-related annotations — `@cs`, `@us`, `@iti`, `@cs_interval` — that attach metadata to respondent primitives and to phases that host composed operant × respondent procedures. The extension is bundled with the contingency-dsl project but lives under `annotations/extensions/` because it falls outside the four JEAB-aligned categories (Subjects / Apparatus / Procedure / Measurement).

**Companion documents:**
- [Annotation Design](../design.md) — annotation layer architecture and registry semantics.
- [Boundary Decision](../boundary-decision.md) — Q1–Q3 test for Core vs Annotation classification.
- [Schema Format](../schema-format.md) — annotation schema meta-format (for the corresponding JSON Schema file).
- [Template](../template.md) — annotator proposal template.
- [Respondent Grammar](../../respondent/grammar.md) — Tier A respondent primitives referenced below.
- [Respondent Primitives](../../respondent/primitives.md) — operational definitions of the primitives being annotated.

---

## 1. Status

**Status:** Schema Design (introduced as part of the layer restructuring). The companion JSON Schema file at `schema/annotations/extensions/respondent-annotator.schema.json` is scheduled for creation in a later schema restructure. Until then, this markdown specification is the authoritative design description.

## 2. Category

This annotator belongs to the **Extension** category (`annotations/extensions/`), not to any of the four JEAB-aligned categories. Respondent-specific stimulus and timing metadata cross-cut the Procedure / Apparatus / Measurement categories: `@cs` and `@us` carry stimulus information (between Apparatus and Procedure); `@iti` and `@cs_interval` carry timing information (between Procedure and Measurement). Placing these four under a single Extension annotator keeps the respondent metadata coherent and preserves the 1:1 annotator-to-category correspondence rule (design-philosophy §4.1) for the four primary categories.

## 3. Keywords

| Keyword | Purpose | Example |
|---|---|---|
| `@cs` | CS (conditional stimulus) metadata | `@cs(label="tone", duration=10-s, modality="auditory")` |
| `@us` | US (unconditional stimulus) metadata | `@us(label="shock", intensity="0.5mA", delivery="unsignaled")` |
| `@iti` | Intertrial-interval metadata with jitter | `@iti(distribution="exponential", mean=60-s, jitter=10-s)` |
| `@cs_interval` | CS presentation time window | `@cs_interval(cs_onset=0-s, cs_offset=10-s)` |

## 4. Per-Annotation Specification

### 4.1 `@cs(label, duration, modality)`

**Placement.** Attachable to any `Phase` or respondent expression (`ScheduleExpr` / `RespondentExpr`). Inherited from `PhaseSequence.shared_annotations` through the standard keyword-override rule.

**Parameters.**
- `label` — string; the CS identifier used in the respondent primitive (e.g., `"tone"`, `"light"`). Must match the `cs` reference used in the corresponding `Pair.*`, `Extinction`, `CSOnly`, `Compound`, `Serial`, or `Differential` primitive.
- `duration` — value; the nominal CS duration. Reproduces (redundantly, for readability) the `cs_duration` argument of `Pair.ForwardDelay` when present; required for respondent primitives that do not themselves carry a `cs_duration` argument.
- `modality` — string; the sensory modality of the CS (e.g., `"auditory"`, `"visual"`, `"olfactory"`, `"tactile"`).

**Boundary-decision rationale (Q1–Q3 from `annotations/boundary-decision.md §2`).**
- Q1 (required to discuss theoretical properties of the respondent primitive): **No.** The respondent primitive's operational definition (e.g., `Pair.ForwardDelay`) does not require knowledge of CS modality; the temporal structure is independent of modality.
- Q2 (alters evaluation semantics): **No.** Changing `modality` from `"auditory"` to `"visual"` does not change the parse tree or the evaluation result.
- Q3 (mandatory at grammar level): **No.** Different programs may omit `modality` (e.g., a general-purpose parser) or require it (e.g., an apparatus-verification pipeline). The grammar is independent of this choice.

All three answers are **No**, confirming `@cs` as an annotation candidate per the boundary test.

**Relationship to Tier A primitives.** `@cs` adds metadata to the `cs` parameter of `Pair.*`, `Extinction`, `CSOnly`, `Compound`, `Serial`, and `Differential`. When the primitive already carries a CS-duration parameter (e.g., `Pair.ForwardDelay`'s `cs_duration`), the `duration` attribute on `@cs` is a redundant readability aid; the primitive remains authoritative.

**Example.**
```
Phase(
  label = "Acquisition",
  schedule = Pair.ForwardDelay(tone, shock, isi=10-s, cs_duration=10-s)
)
@cs(label="tone", duration=10-s, modality="auditory")
@us(label="shock", intensity="0.5mA", delivery="unsignaled")
```

### 4.2 `@us(label, intensity, delivery)`

**Placement.** Attachable to any `Phase` or respondent expression. Inherited through the standard override rule.

**Parameters.**
- `label` — string; US identifier matching the `us` reference in the corresponding primitive.
- `intensity` — string or value; US intensity specification (e.g., `"0.5mA"`, `"45mg_pellet"`, `"3s_access"`).
- `delivery` — string; US delivery mode. Enumerated recommendations: `"unsignaled"`, `"signaled"`, `"response_contingent"`, `"cancelled_on_cs_response"`. The enumeration is not enforced by the grammar; programs may extend it.

**Boundary-decision rationale.**
- Q1: No. The respondent primitive operates independently of US intensity specification at the grammar level.
- Q2: No. Changing the intensity value does not alter the parse-tree structure.
- Q3: No. Programs may decide whether `intensity` is mandatory.

**Relationship to Tier A primitives.** `@us` adds metadata to the `us` parameter of any respondent primitive that carries a US reference (`Pair.*`, `USOnly`, `Differential`). It is also useful on composed-layer procedures (CER, PIT) where the US is specified in the operant context but drives Pavlovian learning.

**Example.**
```
@us(label="shock", intensity="0.5mA", delivery="unsignaled")
```

### 4.3 `@iti(distribution, mean, jitter)`

**Placement.** Attachable to `Phase` or `PhaseSequence` (shared inheritance); also to trial-based respondent blocks.

**Parameters.**
- `distribution` — string; one of `"fixed"`, `"uniform"`, `"exponential"` (matching the `ITI` primitive's distribution family).
- `mean` — value; mean ITI duration.
- `jitter` — value; the range or standard-deviation of ITI variability around the mean. `jitter=0` denotes no jitter.

**Distinction from the `ITI` primitive.** The `ITI(distribution, mean)` primitive (respondent R13) is a **structural** element: it declares that the respondent procedure includes intertrial intervals and specifies their distribution. The `@iti(distribution, mean, jitter)` annotation is **metadata** that adds jitter information and (redundantly, for readability) the distribution and mean. The boundary follows `boundary-decision.md §2`:

- If a phase has ITI at all, the structural declaration belongs in the primitive (`ITI(...)`).
- If jitter needs to be recorded, the annotation carries that additional detail.
- If jitter is irrelevant, the primitive alone suffices.

**Boundary-decision rationale.**
- Q1: No. Jitter does not participate in the primitive's operational definition.
- Q2: No. Changing jitter magnitude does not change the parse tree.
- Q3: No. Many programs do not need jitter metadata.

**Example.**
```
@iti(distribution="exponential", mean=60-s, jitter=10-s)
```

### 4.4 `@cs_interval(cs_onset, cs_offset)`

**Placement.** Attachable to `Pair` primitives (`Pair.ForwardDelay`, `Pair.ForwardTrace`, `Pair.Simultaneous`, `Pair.Backward`) and to phases hosting these primitives.

**Parameters.**
- `cs_onset` — value; time of CS onset relative to trial start (typically `0-s`).
- `cs_offset` — value; time of CS offset relative to trial start.

**Purpose.** Makes the CS presentation window explicit for apparatus-verification and for compilation into natural-language Method / Procedure sections. When `Pair.ForwardDelay(cs, us, isi, cs_duration)` is expanded, the CS window is `[0, cs_duration]`; `@cs_interval` records the same window in a reader-friendly form. For `Pair.ForwardTrace`, `@cs_interval` clarifies that the CS window ends at `cs_offset = cs_duration` and the US window begins at `cs_offset + trace_interval`.

**Boundary-decision rationale.**
- Q1: No. The temporal window is already encoded in the primitive's parameters.
- Q2: No. Adding or removing `@cs_interval` does not change the parse-tree structure.
- Q3: No. Not all programs need the reader-friendly CS window.

**Example.**
```
Pair.ForwardDelay(tone, shock, isi=10-s, cs_duration=15-s)
@cs_interval(cs_onset=0-s, cs_offset=15-s)
```

## 5. Tier Classification

Per the Phase B tier classification (`boundary-decision.md §3`):

| Annotation | Tier 1 (default / informational) | Tier 2 (production-required) | Tier 3 (publication-required) |
|---|---|---|---|
| `@cs` | `duration`, `modality` often defaulted | `label` required when apparatus verification is enabled | `label`, `modality` expected in manuscripts |
| `@us` | `intensity`, `delivery` often defaulted | `intensity` required for HW configuration | `intensity`, `delivery` expected in manuscripts |
| `@iti` | `jitter` often defaulted / informational | (no production requirement) | `distribution`, `mean`, `jitter` expected in manuscripts |
| `@cs_interval` | Informational | (no production requirement) | (optional; redundant with primitive) |

Programs select a tier policy appropriate to their mode (development / production / publication); the DSL grammar does not enforce tier assignment.

## 6. Relationship to the Respondent Extension Point

The respondent-annotator is **distinct** from the respondent extension point (`respondent/grammar.md §4`):

- **Respondent extension point** — adds new respondent **primitives** (structural grammar extensions). Used by `contingency-respondent-dsl` for Tier B procedures (blocking, overshadowing, renewal, etc.).
- **Respondent annotator** (this file) — adds **metadata** to existing Tier A primitives without changing the grammar.

A phenomenon that introduces structural relationships (e.g., serial compound CSs in a novel arrangement) belongs at the extension point, not in this annotator; the boundary-decision test (Q1–Q3) formalizes the distinction.

## 7. Companion JSON Schema

The authoritative schema for these four annotations will live at:

```
schema/annotations/extensions/respondent-annotator.schema.json
```

That file follows the annotation-schema meta-format defined in `annotations/schema-format.md`. Its creation is scheduled for a later schema restructure; the present markdown is authoritative for the conceptual design until the schema file exists.

## 8. Worked Example — Full CER Encoding

```
PhaseSequence(
  shared_annotations = [
    @subjects(species="rat", n=8),
    @apparatus(chamber="operant_chamber_1"),
    @iti(distribution="exponential", mean=120-s, jitter=30-s)
  ],
  phases = [
    Phase(
      label = "Baseline",
      schedule = VI 60-s,
      criterion = Stability(window_sessions=5, max_change_pct=10, measure="rate")
    ),
    Phase(
      label = "CER_Training",
      schedule = VI 60-s,
      phase_annotations = [
        @cs(label="tone", duration=60-s, modality="auditory"),
        @us(label="shock", intensity="0.5mA", delivery="unsignaled"),
        @cs_interval(cs_onset=0-s, cs_offset=60-s)
      ],
      criterion = FixedSessions(count=10)
    )
  ]
)
```

The shared `@iti` is inherited by both phases; the Baseline phase has no CS / US metadata (none is needed); the CER_Training phase adds `@cs`, `@us`, and `@cs_interval`. The composed procedure is documented in `composed/conditioned-suppression.md`; this example shows how the respondent-annotator augments it.
