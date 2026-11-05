#!/usr/bin/env python3
"""Check that a feature spec has every section the project's spec template requires.

The list follows original-instruction.md section 7 (what every spec must contain).
A missing section is a warning: the content may be N/A, but then the spec should
say so explicitly ("не применимо" + reason), so readers know it was considered.

Usage: check_sections.py SPEC.md [--json]
"""
from __future__ import annotations

import argparse
import re
import sys

from aclib import Finding, Spec, parse_spec, read_text, report

# (label, heading keywords — any match, case-insensitive, substring)
REQUIRED_SECTIONS: list[tuple[str, tuple[str, ...]]] = [
    ("purpose", ("назначение", "purpose")),
    ("scope / out of scope", ("scope", "рамк")),
    ("user scenarios", ("сценари", "user stor", "use case")),
    ("business rules", ("бизнес-правил", "business rule")),
    ("acceptance criteria", ("критерии приёмки", "критерии приемки", "acceptance")),
    ("validation and edge cases", ("граничн", "валидац", "edge case", "validation")),
    ("UI states", ("ui-состояни", "состояния ui", "ui state")),
    ("API contract / data model", ("api", "модель данных", "data model")),
    ("security and performance", ("безопасност", "производительн", "security", "performance")),
    ("test cases", ("тест-кейс", "test case")),
    ("limitations and open questions", ("ограничени", "открытые вопрос", "open question", "limitation")),
]
HEADING_RE = re.compile(r"^#{2,4}\s+(.+?)\s*$")


def check(spec: Spec) -> list[Finding]:
    headings = [(i, m.group(1).lower()) for i, l in enumerate(spec.lines, 1) if (m := HEADING_RE.match(l))]
    out: list[Finding] = []
    for label, keys in REQUIRED_SECTIONS:
        if not any(k in h for _, h in headings for k in keys):
            out.append(Finding("warning", "MISSING_SECTION",
                               f"No section for {label}. If it does not apply, add it and say why "
                               "('не применимо' + reason), so readers know it was considered",
                               spec.path, ref=label))
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    return report(check(parse_spec(read_text(a.spec), a.spec)), "check_sections", [a.spec], a.json)


if __name__ == "__main__":
    sys.exit(main())
