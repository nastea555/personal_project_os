# Review checklist

Based on the quality characteristics of requirements in ISO/IEC/IEEE 29148, made practical. Each property has the question to ask, the red flags that usually mean it fails, and an example.

## Contents
1. Business rules (BR)
2. Acceptance criteria (AC) — 8 properties
3. The whole set
4. Red-flag phrases (Russian specs)

---

## 1. Business rules (BR)

A business rule states a constraint or calculation that is true regardless of the UI. AC make it observable.

| Property | Question | Red flags | Example |
|---|---|---|---|
| **Precise** | Are values, units, precision and inclusivity stated? | "от 20 до 300" (inclusive?), no units, "округляется" (how?) | "Вес 20–300" → kg? 300 allowed? 300.05? |
| **Verifiable** | Can a test show the rule is broken? | Subjective words; "должно быть удобно" | "Ввод должен быть быстрым" is a wish, not a rule |
| **Consistent** | Does it agree with other BR, the brief, ADRs? | Same quantity with different limits in two places | BR-1 20–300 kg vs AC 30–250 kg |
| **Complete** | What happens when the rule is violated? | Rule states a limit but no reaction | "Одна запись на дату" — and the second one? |
| **Rule, not screen** | Is it independent of UI layout? | Buttons, colours, positions inside a BR | "Кнопка неактивна" belongs in an AC |
| **Covered** | Which AC make it testable? | No AC mentions the behaviour | BR with no AC = nobody builds or tests it |

## 2. Acceptance criteria — 8 properties

| # | Property | Question | Red flags |
|---|---|---|---|
| 1 | **Verifiable** | Can I write the expected result? Would two testers reach the same pass/fail? | Vague words (section 4), "корректно", "нормально" |
| 2 | **Unambiguous** | Does each word have one meaning? Is the AC self-contained? | "в порядке из …" (lookup elsewhere), undefined terms, pronouns with unclear referent, "последние" without a number |
| 3 | **Singular** | Does it check one behaviour? | Many commas / verbs / "и … и …"; > 2 conditions |
| 4 | **Complete** | Precondition, action and expected result all stated? Error/empty/loading/boundary covered? | Only the happy path; "при ошибке" without what the user sees |
| 5 | **Consistent** | Does it contradict a BR, another AC, the glossary, scope? | Numbers that differ from the BR; something out of scope required |
| 6 | **Feasible** | Can it be built and verified with our stack? | "Код не попадает в бандл" with no way to check |
| 7 | **Necessary** | Is it traceable to a user story / BR / NFR? | An AC nobody would miss |
| 8 | **Implementation-free** | Does it describe what a user sees, not how code works? | Table names, class names, library behaviour |

**Two-readings test** (use it for every suspected ambiguity): write Reading A and Reading B, then an input where they give different results. If you cannot find a differing input, it is probably not a real ambiguity — drop it.

## 3. The whole set

- **Coverage**: every user story and every BR has at least one AC; every AC has at least one TC.
- **Gaps**: every UI state, error and boundary in the spec appears in some AC.
- **No duplicates**: two AC do not say the same thing in different words.
- **Terms**: glossary terms are used the same way everywhere.
- **TC agree with AC and BR**: a TC that tests the AC's wrong boundary will pass while the BR is broken.

## 4. Red-flag phrases (Russian specs)

The scripts catch the common words; these patterns need judgment:

| Pattern | Examples | Why it fails |
|---|---|---|
| Subjective quality | удобно, понятно, красиво, аккуратно, ненавязчиво, логично | No threshold |
| Relative time | быстро, сразу, мгновенно, вовремя, потом | No number, no reference point |
| Comparison without baseline | быстрее, лучше, меньше | Than what? |
| Open lists | и т.д., и т.п., например (in an AC) | Which items are required? |
| Unbounded quantity | последние, несколько, все (for large data) | How many? Paginated? |
| Optional language | может, по возможности, при необходимости | Is it required or not? |
| Missing actor | «сохраняется», «проверяется» | Who/what does it, and when? |
| Interval without inclusivity | от … до …, в течение N дней | Is the edge included? From when? |
| Lookup elsewhere | как в разделе …, по аналогии | The AC is not self-contained |
