#!/usr/bin/env python3
"""Check that URLs cited in a dr-rigor report appear in retained evidence files.

Usage: python3 -I citation-check.py <run-folder> [--report FILE]
                                     [--exclude-sections "Gaps and Uncertainties"]

--report names the report to check: a draft such as draft.md, or a revised output written
by dr-update. A relative path resolves against the run folder. The default is
research-output.md. Pass it explicitly for drafts, so a stale research-output.md from an
earlier run is never checked by mistake.

--exclude-sections skips the named sections of the report (comma-separated heading names,
matched case-insensitively on the start of the heading, subsections included). The final check
excludes Gaps and Uncertainties, which may cite unresolved URLs.

A cited URL counts as resolved when it appears in at least one source-*.md or thread-*.md
file in the run folder. A source file whose header (YAML frontmatter, or its first lines)
records `fetch-status: failed` (a blocked, paywalled, missing or mismatched fetch) is not
evidence, and a thread file can't make its URL resolve. In thread files, a URL on a line marked
`(snippet)` or `(fetch failed)` doesn't count either.

Exit code 0 if every cited URL resolves, 1 otherwise, 2 on bad input.
"""
import argparse
import re
import sys
from pathlib import Path

URL_RE = re.compile(r"https?://[^\s)\]>\"'`|]+")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
# A whole metadata line: `fetch-status: failed`, `**fetch-status**: "failed"`, `- fetch-status: failed (403)`.
STATUS_RE = re.compile(r"""^\s*(?:[-*]\s+)?[*_]*fetch-status[*_]*\s*:\s*[*_"']*\s*([a-z]+)""", re.IGNORECASE)
HEADER_LINES = 15
# A thread line that cites a URL it didn't fetch successfully.
UNFETCHED_RE = re.compile(r"""^[\s/)\]>*_"'`.,;:]*\(\s*(?:snippet|search snippet|fetch failed|not fetched)""",
                          re.IGNORECASE)
# Link syntax that sits between a URL and its marker: [label](url "title") and <url>.
MD_LINK_RE = re.compile(r"""\[([^\]]*)\]\(\s*<?(https?://[^\s)>]+)>?(?:\s+["'(][^)]*)?\)""")
ANGLE_LINK_RE = re.compile(r"<(https?://[^\s>]+)>")
MARK_WINDOW = 40
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


def normalize(url: str) -> str:
    url = url.rstrip(".,;:*_")
    url = url.split("#", 1)[0].rstrip("/").lower()
    # arXiv: /abs/2602.12670v1, /html/2602.12670v1 and /abs/2602.12670 are the same paper.
    url = re.sub(r"arxiv\.org/(?:abs|html|pdf)/(\d{4}\.\d{4,5})(?:v\d+)?", r"arxiv.org/abs/\1", url)
    return url


def urls_in(text: str) -> set[str]:
    return {normalize(u) for u in URL_RE.findall(text)}


def fetch_status(text: str) -> str | None:
    """The fetch-status from YAML frontmatter or the first lines of the header, else None."""
    lines = text.splitlines()
    if lines and lines[0].strip() == "---":
        end = next((i for i, l in enumerate(lines[1:], 1) if l.strip() == "---"), 0)
        header = lines[1:end]
    else:
        header = lines[:HEADER_LINES]
    for line in header:
        m = STATUS_RE.match(line)
        if m:
            return m.group(1).lower()
    return None


def thread_urls(text: str) -> set[str]:
    """URLs in a thread file, minus those marked as snippets or failed fetches.

    The marker applies to the URL it directly follows (within MARK_WINDOW characters, before the
    next URL), so one line can cite a fetched page and a snippet side by side. Link delimiters
    are stripped first: `[label](url) (snippet)` and `<url> (snippet)` mark the URL. A URL marked
    anywhere on a line doesn't count from that line, even if it also appears unmarked there.
    """
    found = set()
    for line in text.splitlines():
        line = ANGLE_LINK_RE.sub(r"\1", MD_LINK_RE.sub(r"\1 \2", line))
        matches = list(URL_RE.finditer(line))
        kept, marked = set(), set()
        for n, m in enumerate(matches):
            end = matches[n + 1].start() if n + 1 < len(matches) else len(line)
            url = normalize(m.group(0))
            if UNFETCHED_RE.search(line[m.end():min(end, m.end() + MARK_WINDOW)]):
                marked.add(url)
            else:
                kept.add(url)
        found |= kept - marked
    return found


def strip_sections(text: str, names: list[str]) -> str:
    """Drop each section whose heading starts with one of names, with its subsections."""
    names = [n.strip().lower() for n in names if n.strip()]
    if not names:
        return text
    kept, skip_level = [], None
    fence = Fence()
    for line in text.splitlines():
        m = None if fence.step(line) else HEADING_RE.match(line)
        if m:
            level, title = len(m.group(1)), m.group(2).strip().lower()
            if skip_level is not None and level <= skip_level:
                skip_level = None
            if skip_level is None and any(title.startswith(n) for n in names):
                skip_level = level
        if skip_level is None:
            kept.append(line)
    return "\n".join(kept)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument("folder", help="run folder holding source-*.md and thread-*.md")
    parser.add_argument("--report", default="research-output.md",
                        help="report to check, relative to the folder or absolute")
    parser.add_argument("--exclude-sections", default="",
                        help="comma-separated section headings to skip in the report")
    args = parser.parse_args()

    folder = Path(args.folder).expanduser()
    if not folder.is_dir():
        print(f"ERROR: not a folder: {folder}")
        return 2
    report = Path(args.report).expanduser()
    if not report.is_absolute():
        report = folder / report
    if not report.is_file():
        print(f"INCOMPLETE: no {report.name} in {report.parent}")
        return 2
    print(f"report: {report}")

    sources, threads, failed_urls, failed = set(), set(), set(), []
    source_files = sorted(folder.glob("source-*.md"))
    thread_files = sorted(folder.glob("thread-*.md"))
    evidence_files = source_files + thread_files
    for f in source_files:
        text = f.read_text(errors="replace")
        if fetch_status(text) == "failed":
            failed.append(f.name)
            failed_urls |= urls_in("\n".join(text.splitlines()[:HEADER_LINES]))
        else:
            sources |= urls_in(text)
    for f in thread_files:
        threads |= thread_urls(f.read_text(errors="replace"))
    # A thread can't rescue a URL whose only fetch record is a failed source file.
    evidence = sources | (threads - (failed_urls - sources))

    excluded = [s for s in args.exclude_sections.split(",") if s.strip()]
    body = strip_sections(report.read_text(errors="replace"), excluded)
    cited = urls_in(body)
    unresolved = sorted(u for u in cited if u not in evidence)
    resolved = len(cited) - len(unresolved)

    print(f"evidence files: {len(evidence_files)} ({len(failed)} failed fetches, not counted)")
    if excluded:
        print(f"excluded sections: {', '.join(s.strip() for s in excluded)}")
    print(f"cited URLs: {len(cited)}  resolved: {resolved}  unresolved: {len(unresolved)}")
    if cited:
        print(f"citation resolution: {resolved / len(cited):.0%}")
    for name in failed:
        print(f"  FAILED-FETCH {name}")
    for u in unresolved:
        print(f"  UNRESOLVED {u}")
    return 0 if not unresolved else 1


if __name__ == "__main__":
    sys.exit(main())
