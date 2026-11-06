#!/usr/bin/env python3
"""Claim placement check: does a dr-rigor report follow its claim ledger?

Usage: python3 -I verify-ledger.py <run-folder> [--report FILE] [--ledger FILE]

Defaults: --report research-output.md, --ledger verification.md (both relative to the folder).

The ledger is the markdown table in verification.md whose header has `ID` and `Status`
columns. Claim IDs are tagged in the report as [F1], [F2] ... ([U1] for a sentence the verifier
found untagged); recommendations cite theirs as
`Basis: F3, F7`.

Exempt sections (not checked for placement): Gaps and Uncertainties, Research Log,
Methodology, with their subsections. IDs in headings count. Fenced code blocks (``` or ~~~)
are skipped.

Recommendation structure: each top-level list item under a Recommendations heading is one
recommendation; nested bullets are its details and share its Basis. Each recommendation stated
in the Executive Summary needs its own Basis there too, in that sentence or a later one of the
same paragraph or list item, before the next recommendation. A sentence states a recommendation
if it uses the verb ("we recommend") or the noun ("our second recommendation is to ...");
a "this recommendation ..." or "the recommendation ..." that only comments on one already
stated ("This recommendation is provisional") qualifies it and is not a new one.

Fails (exit 1) if:
  1. an ID not marked `supported` or `narrowed` appears in a non-exempt section
  2. a `removed` ID is missing from Gaps and Uncertainties
  3. an ID in the report has no ledger entry (a claim added after verification)
  4. a recommendation's Basis names an ID that isn't `supported` or `narrowed`
  5. a recommendation has no Basis, or a Basis naming no claim IDs
  6. the ledger still holds an `untagged` row, or a status outside the allowed set
  7. the ledger's recorded outcome disagrees with its rows

It can't detect an untagged factual sentence; that is the verifier's job.
Exit 0 on pass, 1 on fail, 2 on bad input.
"""
import argparse
import re
import sys
from pathlib import Path

HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
TAG_RE = re.compile(r"\[([FU]\d+)\]")
BASIS_RE = re.compile(r"Basis\**\s*:\**\s*([^\n]*)", re.IGNORECASE)
ID_RE = re.compile(r"\b[FU]\d+\b")
LIST_ITEM_RE = re.compile(r"^(?:[-*+]|\d+[.)])\s+")
OUTCOME_RE = re.compile(r"^outcome:\s*([\w-]+)", re.MULTILINE)
FENCE_RE = re.compile(r"^\s{0,3}(`{3,}|~{3,})")


class Fence:
    """Tracks fenced code blocks (``` or ~~~, closed by the same character, at least as long)."""

    def __init__(self):
        self.open = None

    def step(self, line: str) -> bool:
        """Feed one line; return True if the line is inside a fence or is a fence delimiter."""
        m = FENCE_RE.match(line)
        if self.open is None:
            if m:
                self.open = m.group(1)
                return True
            return False
        if m and m.group(1)[0] == self.open[0] and len(m.group(1)) >= len(self.open) \
                and not line.strip()[len(m.group(1)):].strip():
            self.open = None
        return True

EXEMPT = ("gaps and uncertainties", "research log", "methodology")
GAPS = ("gaps and uncertainties",)
RECOMMENDATION = ("recommendation",)
SUMMARY = ("executive summary",)
# The verb states a recommendation. The noun states one too ("Our second recommendation is to ..."),
# unless it only refers back to one: a demonstrative or "the" right before it ("This recommendation
# is provisional"), and nothing after it that gives the recommendation's content ("is to ...", ":").
# Before any recommendation has been stated, every use of the noun counts.
RECOMMEND_VERB = re.compile(r"\brecommend(?:s|ed|ing)?\b", re.IGNORECASE)
RECOMMEND_NOUN = re.compile(r"\brecommendations?\b", re.IGNORECASE)
RECOMMEND_BACKREF = re.compile(r"\b(?:this|that|these|those|the|such|said|above|each|both)\s+$",
                               re.IGNORECASE)
RECOMMEND_CONTENT = re.compile(r"\s*(?:is|are|was|were|remains?)?\s*(?:(?<=\s)(?:to|that)\b|[:—–])",
                               re.IGNORECASE)
SENTENCE_END_RE = re.compile(r"(?<=[.!?])\s+")
STATUSES = {"unchecked", "supported", "narrowed", "overstated", "unsupported", "removed",
            "untagged"}
# A narrowed claim carries the verifier's own supported wording, applied by the orchestrator.
STATEABLE = ("supported", "narrowed")


def sections(text):
    """Yield (title path, line, is_heading); subsections inherit their parent's titles.

    Heading lines are yielded too (under their own section), so IDs in headings are checked.
    """
    stack, fence = [], Fence()
    for line in text.splitlines():
        m = None if fence.step(line) else HEADING_RE.match(line)
        if m:
            level, title = len(m.group(1)), m.group(2).strip().lower()
            while stack and stack[-1][0] >= level:
                stack.pop()
            stack.append((level, title))
        yield [t for _, t in stack], line, bool(m)


def in_any(path, prefixes):
    return any(t.startswith(p) for t in path for p in prefixes)


def parse_ledger(text):
    """Rows of every table whose header has ID and Status columns: {id: status}."""
    rows, header = {}, None
    for line in text.splitlines():
        if not line.strip().startswith("|"):
            header = None
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if header is None:
            lower = [c.lower() for c in cells]
            if "id" in lower and "status" in lower:
                header = (lower.index("id"), lower.index("status"))
            continue
        if set("".join(cells)) <= set("-: "):
            continue
        i, s = header
        if max(i, s) < len(cells) and cells[i]:
            rows[cells[i].strip("[]*` ")] = cells[s].strip("`* ").lower()
    return rows


def recommendation_items(lines):
    """Top-level list items of a Recommendations section, or its prose as one item."""
    items, current = [], None
    for line in lines:
        if LIST_ITEM_RE.match(line):
            current = [line]
            items.append(current)
        elif current is not None and (line[:1] in (" ", "\t") or not line.strip()):
            current.append(line)
        else:
            current = None
    if items:
        return items
    prose = [l for l in lines if l.strip()]
    return [prose] if prose else []


def states_recommendation(sentence, seen):
    """Does this sentence state a recommendation? `seen`: one has already been stated.

    The verb ("recommend", "recommends", "recommended") always does. The noun does too, except
    when it refers back to a recommendation already stated: right after "this", "that", "the" and
    the like, and not followed by its content ("This recommendation is provisional" refers back;
    "This recommendation is to retire all backups" and "Our second recommendation is ..." don't).
    """
    if RECOMMEND_VERB.search(sentence):
        return True
    for m in RECOMMEND_NOUN.finditer(sentence):
        if not seen:
            return True
        refers_back = RECOMMEND_BACKREF.search(sentence[:m.start()]) \
            and not RECOMMEND_CONTENT.match(sentence[m.end():])
        if not refers_back:
            return True
    return False


def summary_recommendations(lines):
    """Each Executive Summary recommendation, with the sentences that follow it up to the next.

    The summary splits into blocks (paragraphs and top-level list items), and each block into
    sentences. A sentence starts a recommendation if `states_recommendation` says so; the later
    sentences of the same block belong to it, so its Basis may follow in a sentence of its own.
    Each one needs its own Basis: one recommendation's Basis never covers another's.
    """
    blocks, current = [], []
    for line in lines:
        if not line.strip() or LIST_ITEM_RE.match(line):
            if current:
                blocks.append(" ".join(current))
            current = [line.strip()] if line.strip() else []
        else:
            current.append(line.strip())
    if current:
        blocks.append(" ".join(current))
    recs = []
    for block in blocks:
        rec = None
        for sentence in SENTENCE_END_RE.split(block):
            if states_recommendation(sentence, bool(recs)):
                rec = [sentence]
                recs.append(rec)
            elif rec is not None:
                rec.append(sentence)
    return [" ".join(r) for r in recs]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument("folder")
    parser.add_argument("--report", default="research-output.md")
    parser.add_argument("--ledger", default="verification.md")
    args = parser.parse_args()

    folder = Path(args.folder).expanduser()
    paths = {}
    for key in ("report", "ledger"):
        p = Path(getattr(args, key)).expanduser()
        paths[key] = p if p.is_absolute() else folder / p
        if not paths[key].is_file():
            print(f"ERROR: missing {key}: {paths[key]}")
            return 2

    ledger_text = paths["ledger"].read_text(errors="replace")
    ledger = parse_ledger(ledger_text)
    if not ledger:
        print(f"ERROR: no ledger table (ID and Status columns) in {paths['ledger'].name}")
        return 2
    report = paths["report"].read_text(errors="replace")

    errors = []
    gaps_ids, rec_lines, summary_lines = set(), {}, []
    for path, line, is_heading in sections(report):
        ids = set(TAG_RE.findall(line))
        for b in BASIS_RE.findall(line):
            ids |= set(ID_RE.findall(b))
        for i in ids:
            if i not in ledger:
                errors.append(f"no ledger entry: {i} (in '{path[-1] if path else 'top'}')")
        if in_any(path, GAPS):
            gaps_ids |= ids
        elif not in_any(path, EXEMPT):
            for i in ids:
                if i in ledger and ledger[i] not in STATEABLE:
                    errors.append(f"{i} is '{ledger[i]}' but stated in '{path[-1] if path else 'top'}'")
        if is_heading:
            continue
        rec = next((t for t in path if t.startswith(RECOMMENDATION)), None)
        if rec:
            rec_lines.setdefault(rec, []).append(line)
        elif in_any(path, SUMMARY):
            summary_lines.append(line)

    for rec in summary_recommendations(summary_lines):
        first = rec[:70]
        ids = {x for b in BASIS_RE.findall(rec) for x in ID_RE.findall(b)}
        if not ids:
            errors.append(f"Executive Summary recommendation without a Basis naming claim IDs: {first}")
        for i in ids:
            if ledger.get(i) not in STATEABLE:
                errors.append(f"Executive Summary recommendation rests on {i} ({ledger.get(i, 'no entry')}): {first}")

    for i, status in sorted(ledger.items()):
        if status not in STATUSES:
            errors.append(f"ledger: {i} has unknown status '{status}'")
        elif status == "untagged":
            errors.append(f"ledger: {i} is still untagged; tag it or remove the sentence")
        elif status == "removed" and i not in gaps_ids:
            errors.append(f"{i} is removed but missing from Gaps and Uncertainties")

    for title, lines in rec_lines.items():
        for item in recommendation_items(lines):
            text = "\n".join(item)
            first = item[0].strip()[:70]
            basis_ids = {x for b in BASIS_RE.findall(text) for x in ID_RE.findall(b)}
            if not basis_ids:
                errors.append(f"recommendation without a Basis naming claim IDs in '{title}': {first}")
                continue
            for i in basis_ids:
                if ledger.get(i) not in STATEABLE:
                    errors.append(f"recommendation rests on {i} ({ledger.get(i, 'no entry')}): {first}")

    left = sorted(i for i, s in ledger.items() if s not in STATEABLE + ("removed",))
    if left:
        errors.append(f"ledger: claims neither supported, narrowed nor removed: {', '.join(left)}")
    m = OUTCOME_RE.search(ledger_text)
    outcome = m.group(1).lower() if m else None
    expected = "passed" if all(s in STATEABLE for s in ledger.values()) else "passed-with-removals"
    if outcome != expected:
        errors.append(f"ledger: outcome '{outcome}' recorded, rows imply '{expected}'")

    counts = {s: sum(1 for v in ledger.values() if v == s) for s in sorted(STATUSES)}
    print(f"report: {paths['report']}")
    print("ledger: " + ", ".join(f"{k} {v}" for k, v in counts.items() if v))
    for e in errors:
        print(f"  FAIL {e}")
    print("placement check: " + ("PASS" if not errors else f"FAIL ({len(errors)})"))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
