"""Unit tests for the req-review scripts.

Run from the skill folder:  python3 -m unittest discover -s scripts/tests -v
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import check_ids  # noqa: E402
import check_sections  # noqa: E402
import check_traceability  # noqa: E402
import lint_terms  # noqa: E402
from aclib import expand_refs, parse_matrix, parse_spec  # noqa: E402

SPEC = """\
# F-X-001

| Поле | Значение |
|---|---|
| ID | F-X-001 |
| Версия | 0.1 |
| Статус | Draft |

## 4. BR

- **BR-1.** Вес от 20 до 300 кг.
- **BR-2.** Ввод должен быть удобным.

## 5. AC

| ID | Критерий |
|---|---|
| **AC-X-001** | Кнопка «Открыть меню» открывает выдвижное меню. |
| **AC-X-002** | Сообщение понятное. |
| **NFR-X-001** | Ответ ≤ 200 ms. |

## 11. TC

| TC | Название | Тип | Уровень | AC |
|---|---|---|---|---|
| TC-X-001 | Открытие | positive | E | AC-X-001, 002 |
| TC-X-002 | Ответ | perf | S | NFR-X-001 |
"""

MATRIX = """\
## F-X-001

| Требование | Тест-кейсы | Уровни | Статус |
|---|---|---|---|
| AC-X-001 | TC-X-001 | E | Not implemented |
| AC-X-002 | TC-X-001 | E | Not implemented |
| NFR-X-001 | TC-X-002 | S | Not implemented |

Покрытие: 2/2 AC и 1/1 NFR; 2 TC.
"""


def codes(findings, severity=None):
    return sorted(f.code for f in findings if severity is None or f.severity == severity)


class ExpandRefs(unittest.TestCase):
    def test_shorthand_comma_and_slash(self):
        self.assertEqual(expand_refs("AC-UI-001, 017"), ["AC-UI-001", "AC-UI-017"])
        self.assertEqual(expand_refs("TC-UI-016/017/033"), ["TC-UI-016", "TC-UI-017", "TC-UI-033"])

    def test_prefix_switches_between_kinds(self):
        self.assertEqual(expand_refs("AC-UI-004, NFR-UI-002, 003"), ["AC-UI-004", "NFR-UI-002", "NFR-UI-003"])

    def test_prefix_with_digit(self):
        self.assertEqual(expand_refs("AC-DEMO2-001, 002"), ["AC-DEMO2-001", "AC-DEMO2-002"])
        spec = parse_spec(SPEC.replace("-X-", "-X2-"))
        self.assertEqual(sorted(spec.requirements), ["AC-X2-001", "AC-X2-002", "NFR-X2-001"])

    def test_four_digit_number_is_not_shorthand(self):
        self.assertEqual(expand_refs("AC-UI-001, 1024 px"), ["AC-UI-001"])


class CheckIds(unittest.TestCase):
    def test_clean_spec_has_no_errors(self):
        self.assertEqual(codes(check_ids.check(parse_spec(SPEC)), "error"), [])

    def test_duplicate_id_is_error(self):
        spec = SPEC.replace("| **NFR-X-001** |", "| **AC-X-002** | dup |\n| **NFR-X-001** |")
        self.assertIn("DUPLICATE_ID", codes(check_ids.check(parse_spec(spec)), "error"))

    def test_undefined_reference_is_error(self):
        spec = SPEC.replace("Сообщение понятное.", "См. AC-X-009.")
        found = [f for f in check_ids.check(parse_spec(spec)) if f.code == "UNDEFINED_REF"]
        self.assertEqual([f.ref for f in found], ["AC-X-009"])

    def test_other_feature_reference_is_info_only(self):
        spec = SPEC.replace("Сообщение понятное.", "См. AC-NUT-001.")
        self.assertIn("EXTERNAL_REF", codes(check_ids.check(parse_spec(spec)), "info"))

    def test_gap_is_info(self):
        spec = SPEC.replace("AC-X-002", "AC-X-004")
        self.assertIn("ID_GAP", codes(check_ids.check(parse_spec(spec)), "info"))

    def test_retired_ids_are_not_errors_or_gaps(self):
        spec = SPEC.replace("AC-X-002", "AC-X-003").replace("# F-X-001", "# F-X-001\nВыведены из употребления: AC-X-002, TC-X-009 (v0.2).\nСм. AC-X-002.")
        found = check_ids.check(parse_spec(spec))
        self.assertEqual([f for f in found if f.code in ("UNDEFINED_REF", "ID_GAP")], [])

    def test_retired_but_still_defined_is_error(self):
        spec = SPEC.replace("# F-X-001", "# F-X-001\nВыведены из употребления: AC-X-002 (v0.2).")
        self.assertIn("RETIRED_BUT_DEFINED", codes(check_ids.check(parse_spec(spec)), "error"))

    def test_missing_status_header_is_warning(self):
        spec = SPEC.replace("| Статус | Draft |\n", "")
        self.assertIn("MISSING_HEADER", codes(check_ids.check(parse_spec(spec)), "warning"))


class CheckSections(unittest.TestCase):
    FULL = """# F
## 1. Назначение
## 2. Scope
## 3. Пользовательские сценарии
## 4. Бизнес-правила
## 5. Критерии приёмки
## 6. Валидация и граничные случаи
## 7. UI-состояния
## 8. API-контракт
## 10. Безопасность и производительность
## 11. Тест-кейсы
## 12. Ограничения и открытые вопросы
"""

    def test_complete_spec_has_no_findings(self):
        self.assertEqual(check_sections.check(parse_spec(self.FULL)), [])

    def test_missing_sections_are_named(self):
        spec = self.FULL.replace("## 7. UI-состояния\n", "").replace("## 6. Валидация и граничные случаи\n", "")
        found = check_sections.check(parse_spec(spec))
        self.assertEqual({f.code for f in found}, {"MISSING_SECTION"})
        self.assertEqual(sorted(f.ref for f in found), ["UI states", "validation and edge cases"])

    def test_english_headings_count(self):
        spec = "## Purpose\n## Out of scope\n## User stories\n## Business rules\n## Acceptance criteria\n" \
               "## Edge cases\n## UI states\n## Data model\n## Security\n## Test cases\n## Open questions\n"
        self.assertEqual(check_sections.check(parse_spec(spec)), [])


class BusinessRules(unittest.TestCase):
    def test_business_rules_are_parsed(self):
        spec = parse_spec(SPEC)
        self.assertEqual(list(spec.business_rules), ["BR-1", "BR-2"])
        self.assertEqual(spec.business_rules["BR-1"].text, "Вес от 20 до 300 кг.")

    def test_duplicate_br_is_error(self):
        spec = SPEC.replace("- **BR-2.**", "- **BR-1.**")
        found = [f for f in check_ids.check(parse_spec(spec)) if f.code == "DUPLICATE_ID"]
        self.assertEqual([f.ref for f in found], ["BR-1"])

    def test_reference_to_undefined_br_is_error(self):
        spec = SPEC.replace("Сообщение понятное.", "Согласно BR-7.")
        found = [f for f in check_ids.check(parse_spec(spec)) if f.code == "UNDEFINED_REF"]
        self.assertEqual([f.ref for f in found], ["BR-7"])

    def test_vague_word_in_br_is_linted(self):
        found = lint_terms.check(parse_spec(SPEC), ["удобн"], {})
        self.assertEqual([f.ref for f in found], ["BR-2"])


class CheckTraceability(unittest.TestCase):
    def run_check(self, spec=SPEC, matrix=MATRIX):
        return check_traceability.check(parse_spec(spec), parse_matrix(matrix))

    def test_consistent_documents_have_no_findings(self):
        self.assertEqual(codes(self.run_check()), [])

    def test_empty_parse_is_error_not_silent_pass(self):
        spec = SPEC.replace("**AC-X-001**", "AC-X-001").replace("**AC-X-002**", "AC-X-002").replace("**NFR-X-001**", "NFR-X-001")
        self.assertEqual(codes(self.run_check(spec)), ["NOTHING_TO_TRACE"])

    def test_requirement_without_tc(self):
        spec = SPEC.replace("AC-X-001, 002 |", "AC-X-001 |")
        matrix = MATRIX.replace("| AC-X-002 | TC-X-001 |", "| AC-X-002 | |")
        self.assertEqual(codes(self.run_check(spec, matrix), "error"), ["REQ_WITHOUT_TC"])

    def test_link_only_in_matrix(self):
        matrix = MATRIX.replace("| NFR-X-001 | TC-X-002 |", "| NFR-X-001 | TC-X-001, TC-X-002 |")
        self.assertEqual(codes(self.run_check(matrix=matrix), "error"), ["LINK_ONLY_IN_MATRIX"])

    def test_link_only_in_spec(self):
        matrix = MATRIX.replace("| AC-X-002 | TC-X-001 |", "| AC-X-002 | TC-X-002 |")
        self.assertIn("LINK_ONLY_IN_SPEC", codes(self.run_check(matrix=matrix), "error"))

    def test_requirement_missing_in_matrix(self):
        matrix = MATRIX.replace("| NFR-X-001 | TC-X-002 | S | Not implemented |\n", "")
        self.assertIn("MISSING_IN_MATRIX", codes(self.run_check(matrix=matrix), "error"))

    def test_tc_linked_to_undefined_requirement(self):
        spec = SPEC.replace("| NFR-X-001 |\n", "| NFR-X-001, AC-X-007 |\n")
        self.assertIn("TC_REF_UNDEFINED", codes(self.run_check(spec), "error"))

    def test_pass_without_date_is_warning(self):
        matrix = MATRIX.replace("| AC-X-001 | TC-X-001 | E | Not implemented |", "| AC-X-001 | TC-X-001 | E | Pass |")
        self.assertEqual(codes(self.run_check(matrix=matrix), "warning"), ["PASS_WITHOUT_EVIDENCE"])

    def test_pass_with_date_is_fine(self):
        matrix = MATRIX.replace("| AC-X-001 | TC-X-001 | E | Not implemented |",
                                "| AC-X-001 | TC-X-001 | E | Pass 2026-11-02 run #12 |")
        self.assertEqual(codes(self.run_check(matrix=matrix)), [])

    def test_stale_summary(self):
        matrix = MATRIX.replace("2 TC.", "3 TC.")
        self.assertEqual(codes(self.run_check(matrix=matrix), "warning"), ["STALE_SUMMARY"])


class LintTerms(unittest.TestCase):
    VAGUE = ["понятн", "быстр"]
    BARE = {"меню": ["выдвижн", "Открыть меню", "Закрыть меню"]}

    def lint(self, spec, scope="requirements"):
        return lint_terms.check(parse_spec(spec), self.VAGUE, self.BARE, scope)

    def test_vague_word_in_ac_is_flagged_with_ref(self):
        found = [f for f in self.lint(SPEC) if f.code == "VAGUE_WORD"]
        self.assertEqual([(f.ref, f.quote is not None) for f in found], [("AC-X-002", True)])

    def test_vague_word_outside_requirements_ignored_by_default(self):
        spec = SPEC.replace("# F-X-001", "# F-X-001\nБыстрый обзор.")
        self.assertEqual(len([f for f in self.lint(spec) if f.code == "VAGUE_WORD"]), 1)
        self.assertEqual(len([f for f in self.lint(spec, "all") if f.code == "VAGUE_WORD"]), 2)

    def test_stem_does_not_match_inside_word(self):
        # "непонятный" contains the stem "понятн" inside the word; it must not match
        spec = SPEC.replace("Сообщение понятное.", "Текст непонятный.")
        self.assertEqual([f for f in self.lint(spec) if f.code == "VAGUE_WORD"], [])

    def test_vague_word_inside_ui_label_or_code_is_ignored(self):
        spec = SPEC.replace("Сообщение понятное.", "Карточка «Быстрый ввод» и `fastPath`; ответ быстрый.")
        found = [f.quote for f in self.lint(spec) if f.code == "VAGUE_WORD"]
        self.assertEqual(len(found), 1)
        self.assertIn("ответ быстрый", found[0])

    def test_qualified_term_passes_and_bare_term_is_flagged(self):
        self.assertEqual([f for f in self.lint(SPEC) if f.code == "BARE_TERM"], [])
        spec = SPEC.replace("Сообщение понятное.", "Меню закрывается.")
        self.assertEqual([f.ref for f in self.lint(spec) if f.code == "BARE_TERM"], ["AC-X-002"])

    def test_default_rules_file_loads(self):
        vague, bare = lint_terms.load_rules(None)
        self.assertIn("ненавязчив", vague)
        self.assertEqual(bare, {})


if __name__ == "__main__":
    unittest.main()
