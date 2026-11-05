---
name: req-review
description: Full QA review of a feature spec — business rules, acceptance criteria, NFR, user stories, scope, glossary, edge cases, UI states, API/data, test cases and PO decisions. Finds every type of requirements problem (ambiguity, untestable wording, contradictions, missing requirements, unclear boundaries, non-atomic AC, implementation details, broken traceability, missing sections) and produces two documents — an internal QA report and a questions document ready to send to the product owner, so the whole team reads the spec the same way. Use it whenever someone asks to review, check, validate or "QA" a spec, requirements, AC, business rules or user stories, asks whether a spec is ready for development, wants questions or a document for the PO, or wants to check the PO's answers — even if they only give a path like specs/features/F-*.md. Also use it for coach mode (hints only, for practice) and compare mode (a human's review vs the skill's).
---

# Requirements review

A spec is a shared contract. Every sentence two people can read differently becomes two different products: the developer builds reading A, QA tests reading B, and the bug is found late and argued about. This review finds those sentences — and the requirements that are missing altogether — *before* development, and turns each one into a decision the product owner (PO) can make in a minute.

Roles on this project: the PO and the developer are AI agents; QA is a human. The review never changes the spec — it reports and asks. The PO decides; QA judges whether the result is clear and testable. Keeping the reviewer out of the editor keeps the review independent.

## Inputs

- **Spec**: `specs/features/<ID>-*.md` (Russian). Quote it in Russian; write everything else in English.
- **Traceability matrix**: `docs/qa/traceability-matrix.md` (found automatically).
- **Context for consistency**: `docs/product/product-brief.md`, `docs/architecture/architecture-decisions.md`, and any spec the reviewed spec references.

Do not open `datasets/` or `evals/` inside this skill folder. They hold answer keys for testing the skill; reading them during a review would turn the review into copying.

## Outputs

Two files in `docs/qa/reviews/` (create the folder if needed; keep everything inside the project; if a name exists, add `-2`, `-3`):

| File | Reader | Template |
|---|---|---|
| `<SPEC-ID>-review-<YYYY-MM-DD>.md` | QA — the full working: every finding, categories, BR coverage, script output | `references/report-template.md` |
| `<SPEC-ID>-po-questions-<YYYY-MM-DD>.md` | The PO — only decisions to make and fixes to apply, answerable in place | `references/po-document-template.md` |

They are separate because they serve different readers: QA needs the evidence to check the review; the PO needs to decide quickly without wading through it. In chat, give the verdict, the counts, both paths and the blocking questions only.

## Modes

| Mode | When | Output |
|---|---|---|
| `review` (default) | Normal work | QA report + PO questions document |
| `answers <po-document>` | The PO has answered and/or a new spec version exists | Follow-up check (see below) |
| `coach` | The human is practising | Hints only, no answers |
| `compare <human-review>` | After the human's own review | Side-by-side comparison |

## Workflow (review mode)

### 1. Run the deterministic checks

```bash
python3 <this skill's folder>/scripts/run_all.py <spec> [--matrix <matrix.md>]
```

In this project the skill folder is `.claude/skills/req-review/`. On Windows the command is `python` instead of `python3`. The matrix is found at `docs/qa/traceability-matrix.md` above the spec; pass `--matrix` if it lives elsewhere. If Python is not available, say so in the report and do these checks by reading.

It checks required sections, IDs, spec↔matrix traceability, vague words and glossary terms, and prints an inventory (BR / AC / TC counts). Errors are facts — copy them into the report as they are. `VAGUE_WORD`, `BARE_TERM` and `MISSING_SECTION` warnings are *candidates*: confirm each as a finding or dismiss it with a one-line reason (a subjective word in a manual visual check can be acceptable; a section can be legitimately N/A if the spec says so). The scripts cannot judge meaning; that is the next steps' job.

### 2. Read for understanding

Read the whole spec, then the product brief and ADRs it depends on. Before judging anything, be able to say in two sentences what the feature does and where its borders are. Many apparent defects disappear once scope is clear, and real contradictions only show up against the brief and ADRs.

### 3. Business rules

For each BR apply `references/checklist.md` §1, then build the **BR → AC coverage table**. A BR with no AC is a gap — nobody will build or test it on purpose.

### 4. Acceptance criteria and NFR

For each AC apply the 8 properties in `references/checklist.md` §2; for each NFR also ask how and where it is measured. The fastest test of an AC: write its expected result yourself. If you cannot, or can write two different ones, it fails.

### 5. The rest of the spec

Go section by section with `references/problem-types.md` §2: scope, glossary, user scenarios, edge cases, UI states, API/data, security/performance, test cases, decisions and open questions. PO decisions deserve real scrutiny: does the stated reason actually support the decision, and does the decision contradict any BR or the brief?

### 6. Gap pass — what is *not* written

Ask "which requirement covers this?" for: every BR; every number (below / at / above — inclusive? unit? precision? counted from what?); every UI state and error; time (later, at midnight, after N days, second attempt, after reload); every user story's main failure.

### 7. Consistency pass

AC vs BR, AC vs AC, spec vs brief/ADRs, glossary vs usage, test cases vs AC/BR (a TC that tests the wrong boundary hides a contradiction instead of catching it).

### 8. Write findings

One finding = one problem, filed under one category from `references/problem-types.md`. For each:
- quote the exact text — no quote, no finding (for a missing requirement, quote the BR or scope line it should implement);
- show **Reading A / Reading B** with an example input where they differ — this is what makes the PO see why it matters; if you cannot find a differing input, it is probably not a real ambiguity, so drop it;
- decide whether it needs a **PO decision** (goes to the questions list) or is a **fix with no decision** (goes to the fixes table).

Do not invent product behaviour. When you see a likely answer, offer it as an option marked "Recommended" with a one-line reason — never as a fact or a spec edit.

Severity — ask "if development starts today and nobody asks, what happens?":
- **High** — wrong behaviour gets built or a rule is broken: contradiction with a BR, a stated rule with no behaviour, duplicate IDs, an AC nobody can test.
- **Medium** — two people would build or test it differently.
- **Low** — everyone would build the same thing; it is unclear or untidy.

### 9. Write the PO questions

Follow `references/po-questions.md`: one decision per question, closed options A/B(/C), a recommended option with a reason, a concrete example, blocking questions first. Each question must be understandable without the QA report — quote the spec, say why it matters in one or two sentences.

### 10. Verdict and documents

- **Not ready for development** — at least one High finding is open.
- **Ready with comments** — only Medium/Low findings.
- **Ready** — nothing found. Still list what was *not* checked.

Write both documents from the templates. Before finishing, check that every PO question maps to a finding in the report and every finding that needs a decision has a question — the two documents must agree.

## Answers mode (follow-up)

Input: the PO questions document with answers filled in, and the spec (new version if there is one).

For each question report one of: **resolved** (answered clearly *and* the spec now says it), **answered, not in spec** (decision made but the spec still says the old thing — the next reader will not see the answer), **answer unclear** (the answer itself is vague or picks no option — ask again, sharper), **unanswered**. Then run a normal review on the changed parts of the spec only: new text brings new defects. Write `<SPEC-ID>-answers-check-<YYYY-MM-DD>.md`, and a new PO questions document only if questions remain.

## Coach mode

The human is learning to review; giving answers would take the learning away.
1. Run step 1 and do steps 2–7 privately. Write no files.
2. Reply with hints only, per item: which property or category is at risk ("AC-UI-003: check *singular*"; "§6: think *boundary*"), plus how many findings remain per category. No quotes, no explanations, no proposals.
3. If asked for a stronger hint, name the sentence, not the problem. If asked for the answer, say so plainly and switch to review mode.

## Compare mode

Input: the human's review (any format). Produce a table:

| Finding | Human | Skill | Verdict |
|---|---|---|---|

- *Found by both* — compare severity, category and wording; note if the human's question to the PO would be ambiguous.
- *Only the human* — judge it honestly. If valid, say so and add it to the report; if not, explain why. Do not agree to be polite — a wrong "yes" teaches the wrong thing.
- *Only the skill* — name the category or technique that would have found it (e.g., "boundary: below / at / above"), so the human knows what to practise.

End with the two or three patterns behind the misses, not a list of every miss.

## Limits — state them in every report

The review is a model reading text. It can miss defects and can be confidently wrong, and it does not know what the PO intended. It does not review visual design, code or test implementation. List anything you could not check (e.g., a referenced spec that does not exist yet).
