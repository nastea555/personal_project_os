# Report template

The internal QA report: the reviewer's full working. The PO receives the separate questions document (`po-document-template.md`), which links back here. Use this structure exactly; reviewers and the compare mode rely on it. Quotes stay in Russian; everything else is English.

```markdown
# Requirements review — <SPEC-ID> v<version>

| | |
|---|---|
| Spec | `<path>` |
| Reviewed | <YYYY-MM-DD> |
| Reviewer | req-review skill (AI) — to be verified by QA |
| Verdict | **Not ready for development** / **Ready with comments** / **Ready** |
| Findings | <n> High · <n> Medium · <n> Low |
| PO questions | `<path to the PO questions document>` |

## 1. Summary
Two or three sentences: what the feature is, the main risks, what must be answered before development.

## 2. Findings by category
| Category | High | Medium | Low |
|---|---|---|---|
| contradiction | 1 | 0 | 0 |
(one row per category from problem-types.md that has findings)

## 3. Findings

### F-01 · <short title> · High
| | |
|---|---|
| Where | AC-XX-001 (line 87) |
| Category | contradiction (problem-types.md) |
| Property | consistent (checklist.md) |
| Quote | «…exact text…» |
| Problem | One sentence. |
| Reading A / B | A: … · B: … · Example: input X → A gives …, B gives … |
| Impact | What goes wrong if nobody asks. |
| PO question | Q-01 in the PO document, or "fix, no decision" |

(repeat per finding, ordered by severity)

## 4. Business rules → acceptance criteria
| BR | Covered by | Gap |
|---|---|---|
| BR-1 | AC-XX-002 | — |
| BR-3 | — | No AC for a second entry on the same date (F-07) |

## 5. Automated checks
Command and its full output. For each VAGUE_WORD / BARE_TERM warning: confirmed as F-nn, or dismissed with a reason.

## 6. Not checked / limits
What this review did not cover and why.
```
