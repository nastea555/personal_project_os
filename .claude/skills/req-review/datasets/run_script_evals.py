#!/usr/bin/env python3
"""Evaluate the deterministic layer of req-review against the planted-defect answer key.

Recall:    planted script-detectable defects that were reported.
Unplanned: errors/warnings the scripts reported that the key does not list
           (each one is either a false positive or a defect missing from the key).

Usage: run_script_evals.py [KEY.json]   (default: F-DEMO-001-expected-findings.json)     exit code 1 if recall < 100%
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))

import check_ids  # noqa: E402
import check_sections  # noqa: E402
import check_traceability  # noqa: E402
import lint_terms  # noqa: E402
from aclib import parse_matrix, parse_spec, read_text  # noqa: E402


def main() -> int:
    key_path = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "F-DEMO-001-expected-findings.json"
    key = json.loads(read_text(key_path))
    spec_path, matrix_path = key_path.parent / key["fixture"], key_path.parent / key["matrix"]
    spec = parse_spec(read_text(spec_path), spec_path.name)
    matrix = parse_matrix(read_text(matrix_path), matrix_path.name)
    vague, bare = lint_terms.load_rules(None)  # default rules only: fixtures must not depend on project rules

    findings = [f for f in (check_sections.check(spec) + check_ids.check(spec) + check_traceability.check(spec, matrix)
                            + lint_terms.check(spec, vague, bare)) if f.severity != "info"]
    reported = {(f.code, f.ref) for f in findings}

    script_defects = [d for d in key["defects"] if d["detectable_by"] == "script"]
    expected_pairs = {(e["code"], e["ref"]) for d in script_defects for e in d["expect"]}
    found = 0
    for d in script_defects:
        missing = [e for e in d["expect"] if (e["code"], e["ref"]) not in reported]
        found += not missing
        status = "FOUND " if not missing else "MISSED"
        print(f"{status} {d['id']} {d['where']:<26} {d['category']}"
              + (f"  missing: {missing}" if missing else ""))
    unplanned = sorted({p for p in reported if p not in expected_pairs}, key=str)
    for code, ref in unplanned:
        print(f"UNPLANNED {code} {ref}")

    ai = sum(d["detectable_by"] == "ai" for d in key["defects"])
    print(f"-- script recall {found}/{len(script_defects)}; unplanned findings {len(unplanned)}; "
          f"{ai} defect(s) left for the AI review pass")
    return 0 if found == len(script_defects) else 1


if __name__ == "__main__":
    sys.exit(main())
