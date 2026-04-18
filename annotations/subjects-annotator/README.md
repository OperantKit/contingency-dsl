# subjects-annotator — Subjects & History Declaration

## Purpose

Declares the **biological, motivational, and experiential conditions** of
the organisms run under a contingency program: species, strain, the
establishing operation that maintains the reinforcer's efficacy
(deprivation), prior experimental history, and group size.

Corresponds to the JEAB Method/Subjects subsection: the metadata that
must accompany any operant procedure for a reader to understand *who* was
exposed to the contingency and *under what motivational state*. The
declarations are program-level and purely descriptive; they do not
generate runtime behavior. Apparatus parameters belong to
`apparatus-annotator`; dependent measures belong to `measurement-annotator`.

Per [design-philosophy.md §4.2](../../spec/en/design-philosophy.md),
third-party programs are free to reinterpret, extend, or replace this
annotator. This README documents the DSL project's recommended set.

---

## Status

`Design` — schema specified; reference implementation
(`contingency_annotator.subjects_ext`) not yet built.

---

## Category

- [x] **Subjects** — JEAB Method/Subjects (setup-time declarations)

---

## Keywords

| Keyword | Purpose | Example |
|---|---|---|
| `@species` | Species declaration | `@species("rat")` |
| `@strain` | Strain declaration | `@strain("Long-Evans")` |
| `@deprivation` | Establishing operation: hours and target of deprivation | `@deprivation(hours=23, target="food")` |
| `@history` | Prior experimental history of the subjects | `@history("naive")` |
| `@n` | Number of subjects in the group | `@n(8)` |

## Scope and attachment

All five keywords are **program-level**: they appear in the program
preamble (before any schedule expression) and surface in the AST as
entries of `program_annotations`. They do not attach postfix to any
schedule and are not nested inside `AnnotatedSchedule` nodes.

## Validation rules

The validator enforces the following constraints, all sourced from
[`subjects.schema.json`](../../schema/annotations/subjects.schema.json):

1. **`@species` requires a positional string.** Rejected if missing or
   non-string.
2. **`@strain` requires a positional string.** Rejected if missing or
   non-string.
3. **`@deprivation` requires both `hours` and `target` named
   parameters.** `hours` must be a non-negative number (`minimum: 0`);
   `target` must be a string (e.g., `"food"`, `"water"`). Positional
   arguments are not accepted.
4. **`@history` requires a positional string.** Free-form descriptor
   (e.g., `"naive"`, `"experienced: 6 months lever-press training"`).
5. **`@n` requires a positional integer ≥ 1** (`minimum: 1`). Non-integer
   or non-positive values are rejected.

## References

- American Psychological Association. (2020). *Publication manual of the American Psychological Association* (7th ed.). https://doi.org/10.1037/0000165-000

## Reference implementation

`contingency_annotator.subjects_ext` (planned).
