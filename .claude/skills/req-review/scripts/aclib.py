"""Shared parsing and reporting for the req-review scripts.

Parses the Markdown conventions used in specs/features/*.md:

    business rule:    - **BR-1.** text
    retired IDs:      Выведены из употребления: AC-UI-019, TC-UI-039 (reason)   (or "Retired IDs: …")
    requirement row:  | **AC-UI-001** | text |              (also NFR-UI-001)
    test case row:    | TC-UI-001 | title | type | level | AC-UI-001, 017 |
    matrix row:       | AC-UI-001 | TC-UI-001, TC-UI-002 | E | Not implemented |

Reference cells may use shorthand: "AC-UI-001, 017" means AC-UI-001 and AC-UI-017;
"TC-UI-016/017" means TC-UI-016 and TC-UI-017. A 3-digit number right after an ID
and a comma/slash is always read as shorthand.
"""
from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from pathlib import Path

REF_GROUP_RE = re.compile(r"\b((?:AC|NFR|TC)-[A-Z][A-Z0-9]*-)(\d{3})((?:\s*[,/]\s*\d{3}(?!\d))*)")
REQ_ROW_RE = re.compile(r"^\|\s*\*\*((?:AC|NFR)-[A-Z][A-Z0-9]*-\d{3})\*\*\s*\|(.*)\|\s*$")
TC_ROW_RE = re.compile(r"^\|\s*(TC-[A-Z][A-Z0-9]*-\d{3})\s*\|(.*)\|\s*$")
MATRIX_ROW_RE = re.compile(r"^\|\s*((?:AC|NFR)-[A-Z][A-Z0-9]*-\d{3})\s*\|(.*)\|\s*$")
BR_LINE_RE = re.compile(r"^\s*[-*]\s*\*\*(BR-\d+)\.?\*\*\s*(.*)$")
BR_MENTION_RE = re.compile(r"\bBR-\d+\b")
RETIRED_RE = re.compile(r"(?:Выведены из употребления|Retired IDs?)\s*:\s*([^.(]*)", re.IGNORECASE)
HEADER_ROW_RE = re.compile(r"^\|\s*([^|*]+?)\s*\|\s*(.+?)\s*\|\s*$")


def expand_refs(text: str) -> list[str]:
    """Return every ID mentioned in text, expanding shorthand groups."""
    out: list[str] = []
    for m in REF_GROUP_RE.finditer(text):
        prefix = m.group(1)
        out.append(prefix + m.group(2))
        out.extend(prefix + n for n in re.findall(r"\d{3}", m.group(3)))
    return out


def id_parts(item_id: str) -> tuple[str, str, int]:
    kind, prefix, num = item_id.split("-")
    return kind, prefix, int(num)


def split_cells(inner: str) -> list[str]:
    return [c.strip() for c in inner.split("|")]


@dataclass
class Item:
    id: str
    line: int
    text: str
    refs: list[str] = field(default_factory=list)


@dataclass
class Spec:
    path: str
    lines: list[str]
    requirements: dict[str, Item]
    test_cases: dict[str, Item]
    business_rules: dict[str, Item]
    duplicates: list[tuple[str, list[int]]]
    header: dict[str, str]
    mentions: list[tuple[str, int]]
    br_mentions: list[tuple[str, int]]
    retired: set[str] = field(default_factory=set)

    @property
    def prefixes(self) -> set[str]:
        return {id_parts(i)[1] for i in (*self.requirements, *self.test_cases)}


def parse_spec(text: str, path: str = "<spec>") -> Spec:
    lines = text.splitlines()
    reqs: dict[str, Item] = {}
    tcs: dict[str, Item] = {}
    brs: dict[str, Item] = {}
    seen: dict[str, list[int]] = defaultdict(list)
    header: dict[str, str] = {}
    in_header = True
    for i, line in enumerate(lines, 1):
        if line.startswith("## "):
            in_header = False
        if in_header:
            m = HEADER_ROW_RE.match(line)
            if m and not set(m.group(1)) <= set("-: "):
                header[m.group(1)] = m.group(2)
        m = BR_LINE_RE.match(line)
        if m:
            bid = m.group(1)
            seen[bid].append(i)
            brs.setdefault(bid, Item(bid, i, m.group(2).strip()))
            continue
        m = REQ_ROW_RE.match(line)
        if m:
            rid = m.group(1)
            seen[rid].append(i)
            reqs.setdefault(rid, Item(rid, i, " | ".join(split_cells(m.group(2)))))
            continue
        m = TC_ROW_RE.match(line)
        if m:
            tid = m.group(1)
            cells = split_cells(m.group(2))
            seen[tid].append(i)
            refs = [r for r in expand_refs(cells[-1]) if not r.startswith("TC-")]
            tcs.setdefault(tid, Item(tid, i, cells[0], refs))
    mentions = [(r, i) for i, l in enumerate(lines, 1) for r in expand_refs(l)]
    br_mentions = [(m.group(0), i) for i, l in enumerate(lines, 1) for m in BR_MENTION_RE.finditer(l)]
    dups = [(k, v) for k, v in seen.items() if len(v) > 1]
    retired = {r for l in lines for m in RETIRED_RE.finditer(l) for r in expand_refs(m.group(1))}
    return Spec(path, lines, reqs, tcs, brs, dups, header, mentions, br_mentions, retired)


@dataclass
class MatrixRow:
    id: str
    line: int
    tcs: list[str]
    levels: str
    status: str
    section: str


@dataclass
class Matrix:
    path: str
    rows: dict[str, MatrixRow]
    duplicates: list[tuple[str, list[int]]]
    summaries: dict[str, tuple[int, str]]  # section -> (line, text)


def parse_matrix(text: str, path: str = "<matrix>") -> Matrix:
    rows: dict[str, MatrixRow] = {}
    seen: dict[str, list[int]] = defaultdict(list)
    summaries: dict[str, tuple[int, str]] = {}
    section = ""
    for i, line in enumerate(text.splitlines(), 1):
        if line.startswith("## "):
            section = line[3:].strip()
            continue
        if re.match(r"^\s*(Покрытие|Coverage)\b", line):
            summaries[section] = (i, line)
            continue
        m = MATRIX_ROW_RE.match(line)
        if not m:
            continue
        cells = split_cells(m.group(2))
        rid = m.group(1)
        seen[rid].append(i)
        rows.setdefault(rid, MatrixRow(
            rid, i,
            [r for r in expand_refs(cells[0]) if r.startswith("TC-")],
            cells[1] if len(cells) > 1 else "",
            cells[2] if len(cells) > 2 else "",
            section,
        ))
    dups = [(k, v) for k, v in seen.items() if len(v) > 1]
    return Matrix(path, rows, dups, summaries)


@dataclass
class Finding:
    severity: str  # error | warning | info
    code: str
    message: str
    file: str | None = None
    line: int | None = None
    ref: str | None = None
    quote: str | None = None


SEVERITY_ORDER = {"error": 0, "warning": 1, "info": 2}


def report(findings: list[Finding], tool: str, files: list[str], as_json: bool) -> int:
    """Print findings; return exit code 1 if any error, else 0."""
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")  # Windows consoles/pipes default to cp1251/cp866
    findings = sorted(findings, key=lambda f: (SEVERITY_ORDER[f.severity], f.file or "", f.line or 0))
    counts = {s: sum(f.severity == s for f in findings) for s in SEVERITY_ORDER}
    if as_json:
        print(json.dumps({"tool": tool, "files": files, "summary": counts,
                          "findings": [asdict(f) for f in findings]}, ensure_ascii=False, indent=2))
    else:
        print(f"== {tool}: {', '.join(files)}")
        for f in findings:
            loc = f"{f.file}:{f.line}" if f.line else (f.file or "")
            ref = f" [{f.ref}]" if f.ref else ""
            print(f"{f.severity.upper():7} {f.code:22} {loc}{ref}  {f.message}")
            if f.quote:
                print(f"{'':30}> {f.quote}")
        print(f"-- {counts['error']} error(s), {counts['warning']} warning(s), {counts['info']} info")
    return 1 if counts["error"] else 0


def read_text(path: str | Path) -> str:
    return Path(path).read_text(encoding="utf-8")


def find_up(start: str | Path, relative: str) -> Path | None:
    """Look for `relative` in start's directory and each parent (e.g. docs/qa/traceability-matrix.md)."""
    for d in [Path(start).resolve().parent, *Path(start).resolve().parents]:
        candidate = d / relative
        if candidate.is_file():
            return candidate
    return None
