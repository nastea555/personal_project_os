# Problem types

The categories every finding is filed under. Use the `category` slug in the report. The per-item properties for BR and AC are in `checklist.md`; this file covers the whole spec.

## Contents
1. Taxonomy (16 categories)
2. Section-by-section checks
3. Choosing severity

---

## 1. Taxonomy

| Category | What it is | How to spot it | Typical PO question | Default severity |
|---|---|---|---|---|
| `ambiguity` | Text with two or more plausible readings | Two-readings test finds an input with different results | "Which reading: A or B?" | Medium |
| `untestable` | No pass/fail threshold or observable result | You cannot write the expected result | "What exact value / text / behaviour counts as pass?" | Medium |
| `contradiction` | Two statements cannot both be true | Same quantity, different values; AC breaks a BR; spec vs brief/ADR | "Which one is correct?" | High |
| `missing-requirement` | Behaviour the feature needs but no requirement states | BR with no AC; error/empty/second-attempt/time with no AC | "What should happen when …?" | High if a BR or main flow is affected, else Medium |
| `boundary` | Limit without inclusivity, unit, precision or reference point | Every number: below / at / above; "в течение N", "от … до …" | "Is N itself allowed? Counted from what?" | Medium |
| `non-atomic` | One AC checks several behaviours | Many commas / verbs; > 2 conditions | (no question — a fix for the PO: split) | Medium |
| `implementation-detail` | Describes how code works, not what a user observes | Table, class, library, framework behaviour in an AC | "What should the user observe instead?" | Low |
| `terminology` | Term undefined or used in several meanings | Glossary missing the word; synonyms for one thing | "Which term, defined how?" | Low |
| `scope` | Requirement outside scope, or in-scope item with no requirement | Compare §2 Scope with AC list | "Is X in or out of this feature?" | Medium |
| `decision-rationale` | A PO decision without a reason, or a reason that does not support it | Decision table; "because" missing or circular | "What is the reason? Does it hold given …?" | Low–Medium |
| `traceability` | Broken links US/BR → AC → TC → matrix | Scripts; US with no AC | (fix, not a question) | Medium |
| `test-case` | A TC that cannot prove its AC: no oracle, wrong boundary, wrong level, covers only part | Compare TC title with its AC | "Which values / which level?" | Medium |
| `nfr` | Non-functional requirement without metric, measurement method or environment | "≤ 200 KB" — measured how, on which build? | "How and where is it measured?" | Medium |
| `data` | Units, precision, rounding, time zone, date formats, encoding not defined | Numbers and dates in BR/AC/API | "Which unit/precision/time zone?" | Medium |
| `missing-section` | A required spec section is absent (scripts: MISSING_SECTION) | Spec template | "Does it not apply, or was it forgotten?" | Medium |
| `dependency` | Unstated dependency on another feature, service, environment or assumption | References to other specs, ADRs, "после Этапа N" | "Is this dependency available / decided?" | Medium |

When a problem fits two categories, file it under the one that drives the PO's decision (a contradiction that also leaves a gap is a `contradiction`).

## 2. Section-by-section checks

| Section | Check |
|---|---|
| Header | ID, version, status, change log with reasons |
| Purpose | One problem, one user; matches the product brief |
| Scope | Every in-scope item has AC; nothing out-of-scope is required by an AC |
| Glossary | Every domain term used in AC is defined once and used one way |
| User scenarios | Each has AC covering its happy path and its main failure |
| Business rules | `checklist.md` §1; every BR covered by AC |
| AC / NFR | `checklist.md` §2; NFR have a metric and a way to measure |
| Edge cases | Every number and every state has a row; rows agree with AC |
| UI states | Every state has an AC saying when it appears and what the user can do |
| API / data | Status codes for success and each error; field types, units, formats; nothing exposed that should not be |
| Security / performance | Present or explicitly N/A with a reason |
| Test cases | Each AC fully covered; TC values match AC and BR; level fits (unit/component/E2E/manual) |
| Decisions / open questions | Every decision has a reason; no open question blocks an AC silently |

## 3. Choosing severity

Ask: "If development starts today and nobody asks, what happens?"
- Wrong behaviour gets built or a rule is broken → **High**.
- Two people would build or test it differently → **Medium**.
- Everyone would still build the same thing; it is just unclear or untidy → **Low**.

Severity is about consequence, not about how sure you are. If you are unsure whether something is a problem at all, say so in the finding instead of lowering the severity.
