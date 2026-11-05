#!/usr/bin/env python3
"""Check requirement and test-case IDs in a feature spec.

Errors:   duplicate IDs (AC, NFR, TC, BR); references to IDs of this feature or to
          business rules (BR-n) that are not defined.
Warnings: missing header fields (ID, version, status).
Info:     numbering gaps (except retired IDs), references to retired IDs or other
          features, no change-log row. Retired IDs are declared on a line
          "Выведены из употребления: AC-UI-019, TC-UI-039" (or "Retired IDs: …").

Usage: check_ids.py SPEC.md [--json]      exit code 1 if any error
"""
from __future__ import annotations

import argparse
import sys
from collections import defaultdict

from aclib import Finding, Spec, id_parts, parse_spec, read_text, report

HEADER_FIELDS = {
    "ID": ("id",),
    "version": ("версия", "version"),
    "status": ("статус", "status"),
}
CHANGELOG_KEYS = ("изменения", "changes", "changelog")


def defined_ids(spec: Spec) -> set[str]:
    return set(spec.requirements) | set(spec.test_cases)


def check(spec: Spec) -> list[Finding]:
    out: list[Finding] = []
    f = spec.path
    if not spec.requirements:
        out.append(Finding("error", "NO_REQUIREMENTS",
                           "No requirement rows found (expected '| **AC-XX-001** | text |')", f))

    for item_id in sorted(spec.retired & defined_ids(spec)):
        out.append(Finding("error", "RETIRED_BUT_DEFINED",
                           f"{item_id} is declared retired but is still defined", f, ref=item_id))

    for item_id, lines in spec.duplicates:
        out.append(Finding("error", "DUPLICATE_ID",
                           f"{item_id} is defined {len(lines)} times (lines {', '.join(map(str, lines))})",
                           f, lines[1], item_id))

    defined = set(spec.requirements) | set(spec.test_cases)
    undefined: dict[str, list[int]] = defaultdict(list)
    external: dict[str, list[int]] = defaultdict(list)
    for ref, line in spec.mentions:
        if ref in defined or ref in spec.retired:
            continue
        (undefined if id_parts(ref)[1] in spec.prefixes else external)[ref].append(line)
    for ref, lines in sorted(undefined.items()):
        out.append(Finding("error", "UNDEFINED_REF",
                           f"{ref} is referenced ({len(lines)}x) but not defined in this spec", f, lines[0], ref))
    for ref, lines in sorted(external.items()):
        out.append(Finding("info", "EXTERNAL_REF",
                           f"{ref} belongs to another feature; not checked here", f, lines[0], ref))

    undefined_br: dict[str, list[int]] = defaultdict(list)
    for ref, line in spec.br_mentions:
        if ref not in spec.business_rules:
            undefined_br[ref].append(line)
    for ref, lines in sorted(undefined_br.items()):
        out.append(Finding("error", "UNDEFINED_REF",
                           f"{ref} is referenced ({len(lines)}x) but not defined in this spec", f, lines[0], ref))

    groups: dict[tuple[str, str], set[int]] = defaultdict(set)
    for item_id in defined:
        kind, prefix, num = id_parts(item_id)
        groups[(kind, prefix)].add(num)
    for (kind, prefix), nums in sorted(groups.items()):
        retired_nums = {id_parts(r)[2] for r in spec.retired if id_parts(r)[:2] == (kind, prefix)}
        missing = sorted(set(range(1, max(nums) + 1)) - nums - retired_nums)
        if missing:
            out.append(Finding("info", "ID_GAP",
                               f"{kind}-{prefix}: {', '.join(f'{n:03d}' for n in missing)} not defined "
                               "(fine if retired; say so in the change log)", f))

    keys = {k.strip().lower() for k in spec.header}
    for name, aliases in HEADER_FIELDS.items():
        if not keys & set(aliases):
            out.append(Finding("warning", "MISSING_HEADER", f"Header table has no '{name}' field", f))
    if not keys & set(CHANGELOG_KEYS):
        out.append(Finding("info", "NO_CHANGELOG", "Header has no change-log row ('Изменения' / 'Changes')", f))
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    spec = parse_spec(read_text(a.spec), a.spec)
    return report(check(spec), "check_ids", [a.spec], a.json)


if __name__ == "__main__":
    sys.exit(main())
