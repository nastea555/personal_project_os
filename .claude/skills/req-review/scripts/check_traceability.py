#!/usr/bin/env python3
"""Check traceability between a feature spec and the traceability matrix.

Errors:   requirement without TC; TC without requirement; TC linked to an undefined
          requirement; requirement missing from / unknown in the matrix; AC<->TC link
          present in only one of the two documents; matrix TC not defined in the spec.
Warnings: status 'Pass' without a run date; coverage summary line out of date.

Usage: check_traceability.py SPEC.md [--matrix MATRIX.md] [--json]
       Without --matrix, docs/qa/traceability-matrix.md is searched upwards from the spec.
"""
from __future__ import annotations

import argparse
import re
import sys

from aclib import Finding, Matrix, Spec, find_up, id_parts, parse_matrix, parse_spec, read_text, report

DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")


def check(spec: Spec, matrix: Matrix | None) -> list[Finding]:
    out: list[Finding] = []
    sf = spec.path
    reqs, tcs = spec.requirements, spec.test_cases
    if not reqs:
        # nothing parsed means nothing checked; never let that look like a clean result
        return [Finding("error", "NOTHING_TO_TRACE",
                        "No AC/NFR rows parsed from the spec, so traceability was not checked", sf)]
    spec_links = {(tc, r) for tc, item in tcs.items() for r in item.refs}

    for tc, item in sorted(tcs.items()):
        if not item.refs:
            out.append(Finding("error", "TC_WITHOUT_REQ", f"{tc} is not linked to any AC/NFR", sf, item.line, tc))
        for r in item.refs:
            if r not in reqs:
                out.append(Finding("error", "TC_REF_UNDEFINED", f"{tc} links to {r}, which is not defined",
                                   sf, item.line, tc))
    covered = {r for _, r in spec_links}
    for r in sorted(set(reqs) - covered):
        out.append(Finding("error", "REQ_WITHOUT_TC", f"{r} has no test case", sf, reqs[r].line, r))

    if matrix is None:
        out.append(Finding("warning", "NO_MATRIX", "Traceability matrix not found; matrix checks skipped", sf))
        return out

    mf = matrix.path
    rows = {rid: row for rid, row in matrix.rows.items() if id_parts(rid)[1] in spec.prefixes}
    for rid, lines in matrix.duplicates:
        if rid in rows:
            out.append(Finding("error", "DUPLICATE_MATRIX_ROW", f"{rid} appears {len(lines)} times", mf, lines[1], rid))
    for r in sorted(set(reqs) - set(rows)):
        out.append(Finding("error", "MISSING_IN_MATRIX", f"{r} is not in the matrix", sf, reqs[r].line, r))
    for r in sorted(set(rows) - set(reqs)):
        out.append(Finding("error", "UNKNOWN_IN_MATRIX", f"{r} is in the matrix but not in the spec",
                           mf, rows[r].line, r))

    matrix_links = {(tc, r) for r, row in rows.items() for tc in row.tcs}
    for tc, r in sorted(spec_links - matrix_links):
        if r in rows:
            out.append(Finding("error", "LINK_ONLY_IN_SPEC", f"{tc} -> {r} is in the spec but not in the matrix",
                               sf, tcs[tc].line, tc))
    for tc, r in sorted(matrix_links - spec_links):
        if tc not in tcs:
            out.append(Finding("error", "MATRIX_TC_UNDEFINED", f"{tc} (row {r}) is not defined in the spec",
                               mf, rows[r].line, r))
        elif r in reqs:
            out.append(Finding("error", "LINK_ONLY_IN_MATRIX", f"{tc} -> {r} is in the matrix but not in the spec",
                               mf, rows[r].line, r))

    for r, row in sorted(rows.items()):
        if row.status.lower().startswith("pass") and not DATE_RE.search(row.status):
            out.append(Finding("warning", "PASS_WITHOUT_EVIDENCE",
                               "Status is Pass without a run date/link", mf, row.line, r, row.status))

    sections = {row.section for row in rows.values()}
    for section in sorted(sections):
        if section not in matrix.summaries:
            continue
        line, text = matrix.summaries[section]
        actual = {
            "AC": (sum(1 for r in reqs if r.startswith("AC-") and r in covered), sum(r.startswith("AC-") for r in reqs)),
            "NFR": (sum(1 for r in reqs if r.startswith("NFR-") and r in covered), sum(r.startswith("NFR-") for r in reqs)),
        }
        for kind, (cov, total) in actual.items():
            m = re.search(rf"(\d+)\s*/\s*(\d+)\s*{kind}\b", text)
            if m and (int(m.group(1)), int(m.group(2))) != (cov, total):
                out.append(Finding("warning", "STALE_SUMMARY",
                                   f"Summary says {m.group(1)}/{m.group(2)} {kind}, actual is {cov}/{total}",
                                   mf, line, quote=text.strip()))
        m = re.search(r"(\d+)\s*TC\b", text)
        if m and int(m.group(1)) != len(tcs):
            out.append(Finding("warning", "STALE_SUMMARY", f"Summary says {m.group(1)} TC, spec defines {len(tcs)}",
                               mf, line, quote=text.strip()))
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec")
    ap.add_argument("--matrix")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    spec = parse_spec(read_text(a.spec), a.spec)
    matrix_path = a.matrix or find_up(a.spec, "docs/qa/traceability-matrix.md")
    matrix = parse_matrix(read_text(matrix_path), str(matrix_path)) if matrix_path else None
    files = [a.spec] + ([str(matrix_path)] if matrix_path else [])
    return report(check(spec, matrix), "check_traceability", files, a.json)


if __name__ == "__main__":
    sys.exit(main())
