#!/usr/bin/env python3
"""Run all deterministic checks on one spec: check_sections, check_ids, check_traceability, lint_terms.

Usage: run_all.py SPEC.md [--matrix MATRIX.md] [--rules RULES.json] [--json]
       exit code 1 if any check reports an error (warnings never fail)
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

import check_ids
import check_sections
import check_traceability
import lint_terms
from aclib import find_up, parse_matrix, parse_spec, read_text, report


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec")
    ap.add_argument("--matrix")
    ap.add_argument("--rules")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    spec = parse_spec(read_text(a.spec), a.spec)
    matrix_path = Path(a.matrix) if a.matrix else find_up(a.spec, "docs/qa/traceability-matrix.md")
    matrix = parse_matrix(read_text(matrix_path), str(matrix_path)) if matrix_path else None
    rules_path = Path(a.rules) if a.rules else find_up(a.spec, "docs/qa/req-review-rules.json")
    vague, bare = lint_terms.load_rules(rules_path)

    runs = [
        ("check_sections", [a.spec], check_sections.check(spec)),
        ("check_ids", [a.spec], check_ids.check(spec)),
        ("check_traceability", [a.spec] + ([str(matrix_path)] if matrix_path else []),
         check_traceability.check(spec, matrix)),
        ("lint_terms", [a.spec] + ([str(rules_path)] if rules_path else []), lint_terms.check(spec, vague, bare)),
    ]
    if a.json:
        print(json.dumps({"spec": a.spec, "inventory": {
            "business_rules": len(spec.business_rules), "requirements": len(spec.requirements),
            "test_cases": len(spec.test_cases)},
            "checks": [{"tool": t, "files": f, "findings": [asdict(x) for x in fs]} for t, f, fs in runs]},
            ensure_ascii=False, indent=2))
        return 1 if any(x.severity == "error" for _, _, fs in runs for x in fs) else 0
    print(f"Inventory: {len(spec.business_rules)} BR, {len(spec.requirements)} AC/NFR, {len(spec.test_cases)} TC\n")
    codes = [report(fs, t, f, False) for t, f, fs in runs]
    return max(codes)


if __name__ == "__main__":
    sys.exit(main())
