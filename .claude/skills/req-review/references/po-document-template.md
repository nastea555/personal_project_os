# PO questions document — template

This is the document QA sends to the product owner. It is not the QA report: the PO needs decisions to make, not the reviewer's working. Keep it short, self-contained and answerable in place.

What goes in:
- every question that needs a PO decision (from `ambiguity`, `untestable`, `contradiction`, `missing-requirement`, `boundary`, `scope`, `data`, `nfr`, `dependency`, `decision-rationale` findings);
- a short list of fixes that need no decision (non-atomic AC, traceability, terminology, implementation details, missing sections) — the PO just applies them.

What stays out: script output, dismissed warnings, the per-AC matrix, the reviewer's reasoning beyond one "why it matters" line. Anyone reading only this document must understand each question without opening the QA report.

Language: English; quotes from the spec stay in the original Russian.

```markdown
# Questions for the PO — <SPEC-ID> v<version>

| | |
|---|---|
| Spec | `<path>` |
| From | QA — <YYYY-MM-DD> |
| QA verdict | **Not ready for development** / **Ready with comments** / **Ready** |
| Decisions needed | <n> blocking · <n> other |
| Full QA report | `<path to the QA report>` |

## How to answer

Write your answer under **Answer:** for each question — a letter (A/B/…) or a value is enough. Add a reason if you pick something other than the recommended option. When all blocking questions are answered, update the spec (new version + change log) and send it back for re-review.

## Blocking — must be answered before development

### Q-01 · <short title>
**Where:** AC-XX-002 (also BR-1)
**Spec says:** «exact quote»
**Why it matters:** One or two sentences: the two readings and an example where they differ, or the rule that gets broken.
**Options:**
- **A.** <concrete behaviour>
- **B.** <concrete behaviour>
**Recommended:** A — <one-line reason>.
**Answer:**

(repeat; most consequential first)

## Other questions — answer before the next spec version

(same format)

## Fixes that need no decision

| # | Where | Fix |
|---|---|---|
| 1 | AC-XX-003 | Split into separate criteria: … |
| 2 | Matrix | TC-XX-004 is linked to AC-XX-002 in the matrix but to AC-XX-004 in the spec — align |

## After you answer

QA re-reviews the new version, checks that every answer above is reflected in the spec, and closes the questions.
```

If there are no questions at all, still produce the document with the verdict, "No decisions needed", and the fixes table (or "None").
