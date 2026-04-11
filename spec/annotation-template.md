# example-annotator — Annotation Template

## Purpose

This is a template for proposing a new annotator for the **DSL project's
recommended registry**. Copy this directory and fill in each section.

Per [design-philosophy.md §4.2](ja/design-philosophy.md), third-party
programs are free to build their own registries without following this
template. This template is for annotators that aim to be adopted into
the DSL project's recommended set.

---

## Status

`[ Proposed | Schema Design | Stable ]`

---

## Category

Which of the JEAB-aligned recommended categories does this annotator
belong to? Choose one:

- [ ] **Procedure** — schedule description, equivalence, conversion fill-in
- [ ] **Subjects** — subject history, establishing operations, state
- [ ] **Apparatus** — chamber, operandum, HW binding, timing contract
- [ ] **Measurement** — steady-state, baseline, phase logic, DV specs
- [ ] **Extension** — clinical, derivational, provenance, domain-specific
      (requires justification for a new category)

---

## Keywords

| Keyword | Purpose | Example |
|---|---|---|
| @example_key | What this annotation declares | `@example_key("value", param=42)` |

---

## Boundary Justification

**この annotation がないと理論的議論ができないか: YES / NO**

- (explain why the schedule's theoretical properties don't require this annotation)

**この annotation が DSL 内にあるべき理由:**

- (explain what becomes verifiable / compilable / reproducible by having it in DSL)

---

## Inclusion Criteria

- What *belongs* in this annotator (one dimension, clearly stated)

## Exclusion Criteria

- What does *not* belong here, and where it should go instead

---

## Boundary Review Checklist

Fill this in when proposing a new keyword `@X`:

```markdown
### 1. Core independence (Core vs Annotation)
- [ ] `@X` なしでスケジュールの理論的性質を議論できるか → YES なら annotation OK
- [ ] `@X` は schedule 式の評価結果を変えるか → NO なら annotation OK
- [ ] `@X` を Core 文法に昇格すべきか → NO なら annotation OK
      (昇格する場合は design-philosophy §7 の制約下でのみ可)

### 2. Category fit
- [ ] `@X` は選択したカテゴリ（Procedure / Subjects / Apparatus / Measurement / 拡張）と整合するか
- [ ] `@X` はこの annotator の次元に属するか
- [ ] `@X` は既存 keywords と意味的に一貫するか
- [ ] 他の推奨 annotator の keywords と衝突しないか

### 3. Necessity for recommendation
- [ ] DSL 外（コメント・外部ファイル）では不十分か
- [ ] コンパイル対象（論文・コード生成・検証）に利益があるか
- [ ] 3rd-party 限定ではなく、DSL プロジェクトの推奨集合に含める価値があるか

### 4. Domain expert sign-off
- [ ] EAB: 基礎研究の観点から妥当
- [ ] (domain): 関連ドメインの観点から妥当
- [ ] PLT: 言語設計の観点から一貫
```

---

## Dependencies

Other annotators this one requires (if any). Prefer none.

---

## Implementation Reference

Where the implementation lives (e.g., `apps/experiment/contingency-annotator/src/contingency_annotator/<name>_annotator/`).

Note: third-party programs may implement their own annotator conforming
to this schema without using the reference implementation.
