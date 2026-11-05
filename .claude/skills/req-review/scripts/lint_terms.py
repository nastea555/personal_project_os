#!/usr/bin/env python3
"""Lint requirement wording: unmeasurable words and glossary terms used without a qualifier.

Warnings only. A hit is a candidate, not a verdict: the reviewer decides whether the
word really makes the AC untestable.

  VAGUE_WORD  a word from the vague-word list (rules/default-rules.json + project rules)
  BARE_TERM   a glossary term used without any of its allowed qualifiers nearby
              (e.g. "меню" must be "выдвижное меню", "Открыть меню" or "Закрыть меню")

Project rules: docs/qa/req-review-rules.json, searched upwards from the spec, or --rules.
  {"bare_terms": {"меню": ["выдвижн", "Открыть меню"]},
   "vague_words_extra": ["..."], "vague_words_ignore": ["..."]}

Usage: lint_terms.py SPEC.md [--rules FILE] [--scope requirements|all] [--json]
       requirements = BR lines and AC, NFR, TC rows (default); all = every line.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from aclib import BR_LINE_RE, REQ_ROW_RE, TC_ROW_RE, Finding, Spec, find_up, parse_spec, read_text, report

DEFAULT_RULES = Path(__file__).with_name("rules") / "default-rules.json"
WINDOW_BEFORE, WINDOW_AFTER = 40, 20


def load_rules(project_rules: Path | None) -> tuple[list[str], dict[str, list[str]]]:
    base = json.loads(read_text(DEFAULT_RULES))
    vague = [w for ws in base["vague_words"].values() for w in ws]
    bare: dict[str, list[str]] = {}
    if project_rules:
        proj = json.loads(read_text(project_rules))
        vague += proj.get("vague_words_extra", [])
        ignore = {w.lower() for w in proj.get("vague_words_ignore", [])}
        vague = [w for w in vague if w.lower() not in ignore]
        bare = proj.get("bare_terms", {})
    return vague, bare


def stem_pattern(words: list[str]) -> re.Pattern[str]:
    # each entry is a word start: "удобн" matches "удобно", "удобный"; not inside another word
    alts = sorted((re.escape(w) for w in words), key=len, reverse=True)
    return re.compile(rf"(?<!\w)(?:{'|'.join(alts)})\w*", re.IGNORECASE)


def scoped_lines(spec: Spec, scope: str) -> list[tuple[int, str, str | None]]:
    out = []
    for i, line in enumerate(spec.lines, 1):
        m = BR_LINE_RE.match(line) or REQ_ROW_RE.match(line) or TC_ROW_RE.match(line)
        if m:
            out.append((i, line, m.group(1)))
        elif scope == "all":
            out.append((i, line, None))
    return out


QUOTED_RE = re.compile(r"«[^»]*»|`[^`]*`")


def quoted_spans(line: str) -> list[tuple[int, int]]:
    """Spans of «UI labels» and `code`: names, not claims, so vague words there are not flagged."""
    return [m.span() for m in QUOTED_RE.finditer(line)]


def check(spec: Spec, vague: list[str], bare: dict[str, list[str]], scope: str = "requirements") -> list[Finding]:
    out: list[Finding] = []
    vague_re = stem_pattern(vague) if vague else None
    bare_res = {t: re.compile(rf"(?<!\w){re.escape(t)}(?!\w)", re.IGNORECASE) for t in bare}
    for i, line, ref in scoped_lines(spec, scope):
        spans = quoted_spans(line)
        if vague_re:
            for m in vague_re.finditer(line):
                if any(a <= m.start() < b for a, b in spans):
                    continue
                out.append(Finding("warning", "VAGUE_WORD",
                                   f"'{m.group(0)}' is not measurable: give a pass/fail threshold or make it a manual check",
                                   spec.path, i, ref, snippet(line, m.start(), m.end())))
        for term, pattern in bare_res.items():
            for m in pattern.finditer(line):
                window = line[max(0, m.start() - WINDOW_BEFORE):m.end() + WINDOW_AFTER].lower()
                if not any(q.lower() in window for q in bare[term]):
                    out.append(Finding("warning", "BARE_TERM",
                                       f"'{term}' without a qualifier ({' / '.join(bare[term])})",
                                       spec.path, i, ref, snippet(line, m.start(), m.end())))
    return out


def snippet(line: str, start: int, end: int, pad: int = 40) -> str:
    a, b = max(0, start - pad), min(len(line), end + pad)
    return ("…" if a else "") + line[a:b].strip() + ("…" if b < len(line) else "")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec")
    ap.add_argument("--rules")
    ap.add_argument("--scope", choices=["requirements", "all"], default="requirements")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    rules_path = Path(a.rules) if a.rules else find_up(a.spec, "docs/qa/req-review-rules.json")
    vague, bare = load_rules(rules_path)
    spec = parse_spec(read_text(a.spec), a.spec)
    files = [a.spec] + ([str(rules_path)] if rules_path else [])
    return report(check(spec, vague, bare, a.scope), "lint_terms", files, a.json)


if __name__ == "__main__":
    sys.exit(main())
