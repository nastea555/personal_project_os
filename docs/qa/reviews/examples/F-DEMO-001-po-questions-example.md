# Questions for the PO — F-DEMO-001 v0.1

> **Example output** of `/req-review` for the training spec F-DEMO-001 (weight entry). It shows the format of the document QA sends to the PO. Written by hand while following the skill, not from a real eval run.

| | |
|---|---|
| Spec | `.claude/skills/req-review/evals/review-planted-defects-weight-entry/files/F-DEMO-001-weight-entry.md` |
| From | QA — 2026-11-02 |
| QA verdict | **Not ready for development** |
| Decisions needed | 2 blocking · 4 other |
| Full QA report | not produced for this example |

## How to answer

Write your answer under **Answer:** for each question — a letter (A/B/…) or a value is enough. Add a reason if you pick something other than the recommended option. When all blocking questions are answered, update the spec (new version + change log) and send it back for re-review.

## Blocking — must be answered before development

### Q-01 · Allowed weight range
**Where:** AC-DEMO-002, BR-1
**Spec says:** BR-1: «Вес — число от 20 до 300 кг включительно» · AC-DEMO-002: «Значения веса меньше 30 или больше 250 кг отклоняются»
**Why it matters:** The two contradict each other. A user who enters 25 kg is accepted by the business rule and rejected by the AC. TC-DEMO-002 tests 30/250, so the tests would pass while the business rule is broken.
**Options:**
- **A.** 20–300 kg inclusive (BR-1 is right; fix the AC and TC-DEMO-002).
- **B.** 30–250 kg inclusive (the AC is right; fix BR-1).
**Recommended:** A — the business rule is the source of truth for limits; the AC should only make it observable.
**Answer:**

### Q-02 · Second entry for the same date
**Where:** BR-3 — no acceptance criterion covers it
**Spec says:** «BR-3. На одну дату — не больше одной записи.»
**Why it matters:** The rule exists, but nothing says what the user sees when they save a second entry for a date that already has one. The developer will guess, and QA cannot write the expected result.
**Options:**
- **A.** Reject with an error under the «Дата» field; the existing entry stays unchanged.
- **B.** Replace the existing entry with the new value, without asking.
- **C.** Ask for confirmation: «На эту дату уже есть запись (X кг). Заменить?»
**Recommended:** C — the user does not lose the earlier value by accident, and does not have to find and edit it by hand.
**Answer:**

## Other questions — answer before the next spec version

### Q-03 · Edit window
**Where:** AC-DEMO-005
**Spec says:** «Запись можно редактировать в течение 7 дней.»
**Why it matters:** An entry for 1 November created on 5 November: is it editable on 9 November? Yes if counted from creation, no if counted from the entry date. Day 8 behaviour is also not defined.
**Options:**
- **A.** 7 days from the entry's date, inclusive: an entry for 1 Nov can be edited until 8 Nov 23:59 (device time zone).
- **B.** 7 days from the moment the entry was created.
**Recommended:** A — users think of "the day I weighed in"; B makes a back-dated entry uneditable almost at once.
**Also needed:** after the window, is the edit action hidden, or shown disabled with an explanation?
**Answer:**

### Q-04 · Which entries the list shows
**Where:** AC-DEMO-003 (second one)
**Spec says:** «Список показывает последние записи, новые сверху.»
**Why it matters:** "Последние" has no number, and "новые" can mean the newest entry date or the newest creation time — a back-dated entry lands in a different place depending on the reading.
**Options:**
- **A.** All entries, sorted by entry date, newest date first.
- **B.** The last 30 entries by entry date, newest first, with «Показать ещё».
**Recommended:** A for v1 — one user, a few hundred entries a year; revisit pagination when the list exceeds about 1000.
**Answer:**

### Q-05 · Error message for an invalid weight
**Where:** AC-DEMO-003 (first one)
**Spec says:** «под полем показывается понятное сообщение об ошибке»
**Why it matters:** "Понятное" cannot be tested. Two testers will disagree on whether «Ошибка ввода» passes.
**Options:**
- **A.** Exact text: «Введите число от 20 до 300» (range per Q-01).
- **B.** Any text that names the allowed range.
**Recommended:** A — testable by exact match, and it tells the user how to fix the value.
**Answer:**

### Q-06 · When a saved entry appears in the list
**Where:** AC-DEMO-001, AC-DEMO-004
**Spec says:** AC-DEMO-001: «запись быстро появляется в списке» · AC-DEMO-004: «отображается в списке после перезагрузки страницы»
**Why it matters:** "Быстро" has no threshold, and AC-DEMO-004 can be read as "the entry appears only after a reload". Neither AC says the list updates without a reload.
**Options:**
- **A.** After «Сохранить», the entry appears in the list without a page reload, within 1 s of the server's response; after a reload it is still there.
- **B.** The entry appears only after the page is reloaded.
**Recommended:** A — the user should see the result of their action.
**Answer:**

## Fixes that need no decision

| # | Where | Fix |
|---|---|---|
| 1 | AC-DEMO-003 (second row) | The ID AC-DEMO-003 is used twice. Give the list criterion a new ID (AC-DEMO-006) and update TC-DEMO-005. |
| 2 | AC-DEMO-003 (first row) | Five behaviours in one criterion — split into: no entry is created; error text (Q-05); entered value stays in the field; focus moves to the field; repeated-error highlighting. |
| 3 | AC-DEMO-004 | Remove the table and class names (`weight_entries`, `WeightRepository.save()`); keep only what the user observes. |
| 4 | AC-DEMO-005 | No test case. Add TCs for the edit window boundaries once Q-03 is answered. |
| 5 | Traceability matrix | TC-DEMO-004 is linked to AC-DEMO-004 in the spec but listed under AC-DEMO-002 in the matrix — align. The summary «5/5 AC» is wrong (AC-DEMO-005 has no TC). |
| 6 | Spec structure | Add the missing sections: edge cases, UI states, API / data model, security and performance, limitations and open questions (or mark a section N/A with a reason). |

## After you answer

QA re-reviews the new version, checks that every answer above is reflected in the spec, and closes the questions.
