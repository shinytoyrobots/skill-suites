# Output: common frame

Every form uses this frame. Read it with the form file for this run
(`references/dr-output-{form}.md`). For a form not listed (playbook, how-to guide, and so on), start
from the nearest form file and adapt its body sections; the frame stays.

## Frontmatter (the run record)

```yaml
---
type: deep-research
question: "{research question}"
form: {strategic-assessment | literature-review | decision-brief | landscape-map | other}
tier: {quick | standard | deep}
generated: {YYYY-MM-DD}
skill-version: {short SHA if known, else omit}
agents: {count, from the spend table}
subagent-tokens: {total, from the spend table}
searches: {total}
sources: {count of source-*.md files with a successful fetch}
verification: {passed | passed-with-removals}
claims: {N, ledger rows}
claims-supported-first-pass: {n; verifier pass rate = n / N}
narrowed: {n}
removed: {N}
removed-failed: {k}
removed-unchecked: {m}
brief-items: {per type, status counts: assumptions held / failed / untested; flagged claims supported / contradicted / untraced / not checked; options measured / literature only / blocked / not assessed}
requirements: {met / met-negative / not satisfied counts}
lateral-proposed: {n}
lateral-pursued: {n}
lateral-in-findings: {n}
---
```

## Header

```markdown
# Deep Research: {Topic}
**Research question**: {original question}
**Data freshness**: {date range of the sources relied on}
```

## Sections, in order

1. **Executive Summary**: 3-5 sentences.
2. **The form's body sections** (from the form file).
3. **Non-obvious connections**: every leap from both lateral passes (the Phase 1 scan and the
   Phase 3 challenge). For a leap kept in the findings: the leap, its method, its logic, the test it
   named, what was found (tagged claims), and which conclusions it changed or sharpened. Every
   other leap gets one untagged line stating no facts: `Dead end: {leap} (test: {test}; not
   found)` or `Set aside: {leap}, see Gaps`. Its substance, if any, lives only in Gaps.
4. **Gaps and Uncertainties**: what we couldn't determine, what was searched and why it fell short,
   conflicting information. Every sub-question in `plan.md` that isn't `answered` appears here,
   and so does every requirement not satisfied (with its search scope; `blocked` ones with the
   missing prerequisite), every candidate the coverage pass couldn't reach
   (`Not reached: {item} (coverage pool)`, or `(quick tier)`), every claim the verifier removed
   (`Not verified:` / `Not checked:`) and every challenge set aside, with the reason.
5. **Brief items**: each row of the Brief items table in `plan.md`, with its type, its status in
   that type's vocabulary, and the evidence (claim IDs) for each. A flagged claim with no source
   found is `untraced`, never "failed" or "false". A `blocked` option names its prerequisite and
   the proposed test.
6. **Sources**: every retained `source-*.md` relied on: title, URL, publish date, access date.
7. **Research Log**: phases run, expansions, dead ends, tier, spend totals, disconfirming searches
   run and what they found, and the verification outcome.

## Rules

- **Provenance.** Every factual claim cites the URL of a source that was fetched and written to a
  `source-*.md` or `thread-*.md` file. A search snippet, a failed or paywalled fetch, or a page
  never written to disk is not a source. Don't state it as a finding.
- **Claim IDs.** Tag every factual claim, in every section and every form, `[F1]`, `[F2]` and so
  on: Executive Summary, findings, landscape, comparison tables, leaps, playbook steps. A claim
  stated twice keeps one ID. Exempt (no ID): Gaps and Uncertainties entries, statements labeled
  `Hypothesis:` or `Speculation:`, the Research Log and methodology notes, and recommendations,
  each of which ends `Basis: F3, F7`, naming the claims it rests on. IDs go in square brackets
  everywhere, table cells and headings included (`[F2]`).
- **Recommendation structure.** Under a Recommendations heading, each top-level list item is one
  recommendation with its own `Basis:`; nested bullets are its details. Each recommendation stated
  in the Executive Summary carries its own `Basis:` there too, before the next one. Only "Gaps and Uncertainties" is exempt,
  not other sections whose names start with "Gaps".
- **Confidence** (High/Medium/Low) describes the evidence: quality, independence and freshness.
  - **High** needs two or more **independent origins**. Two articles quoting the same press
    release, paper or post are one origin.
  - A source older than the plan's freshness threshold on a fast-moving topic is flagged
    `(stale: {date})` and can't carry a High rating alone.
- **Likelihood** describes how probable a judgment is. Use ICD 203 terms (almost certain, very
  likely, likely, roughly even chance, unlikely, very unlikely, almost no chance), and only for
  judgments about the future or the unknown, never for reported facts. Confidence and likelihood
  are independent: "Likely (Low confidence)" is a probable outcome on thin evidence. Low
  confidence never means unlikely.
- Organize findings by theme, not by source.
