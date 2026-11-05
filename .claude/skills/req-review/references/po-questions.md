# Writing questions for the product owner

The goal of a question is a decision that removes the ambiguity in one answer. A PO who has to think about *what you are asking* will answer late or vaguely — and a vague answer brings the ambiguity back.

## Rules

1. **One decision per question.** Two decisions in one question get one answer.
2. **Closed form when possible.** Offer options A / B / (C), each a concrete behaviour. The PO can reply "B".
3. **Include a recommended option** with one line of reasoning (usability, consistency with another rule, simplicity to test). Mark it "Recommended". The PO may reject it — that is fine, it still speeds up the answer.
4. **Make it concrete with an example input.** "The user enters 25 kg — accept or reject?" beats "Clarify the weight range."
5. **Ask about behaviour, not implementation.** "What does the user see?" not "Which table stores it?"
6. **Don't ask what the docs already answer.** Cite the document instead and raise a consistency finding if the spec disagrees.
7. **Link it** to the finding ID and the spec location, so the answer goes back to the right place.
8. **Order by blocking power.** Questions behind High findings first.

## Format

```
Q-03 (F-05, AC-DEMO-005) — blocking
The spec says "запись можно редактировать в течение 7 дней".
A. 7 days from the entry's date (an entry for 1 Nov is editable until 8 Nov 23:59).
B. 7 days from the moment the entry was created.
Recommended: A — users think in terms of the day they weighed in; B makes a back-dated entry uneditable at once.
Also needed: on day 8, is the Edit button hidden, or shown with an explanation?
```

## Bad → good

| Bad | Why | Good |
|---|---|---|
| "Please clarify AC-DEMO-002." | Clarify what? | "BR-1 allows 20–300 kg, AC-DEMO-002 rejects < 30 and > 250. Which range is correct? A. 20–300 (BR-1). B. 30–250 (AC). Recommended: A." |
| "Is the message clear enough?" | Same subjectivity as the AC | "What must the error message contain? A. Exact text: «Введите число от 20 до 300». B. Any text that names the allowed range. Recommended: A — testable by exact match." |
| "Should the list be fast and sorted?" | Two decisions, one vague word | Split: "How many entries does the list show? …" and "Sort by entry date or by creation time? …" |
| "Should we use optimistic updates?" | Implementation | "After Save, must the entry appear in the list without a page reload?" |
