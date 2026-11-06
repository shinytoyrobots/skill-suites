# Phase 4: synthesis and verification

Three stages, each a row in `plan.md`. Read `references/dr-output-common.md` and the form file first.
Research is finished: Phase 4 runs no searches and launches no thread or lateral agents.

## 1. Pin evidence

Up to what is left of the tier's cumulative extraction allowance in `references/dr-budget.md` (haiku,
`references/structured-notes.md`, cap 8, search allowance 0, at most 10 at once), launch
`source-{name}.md` extraction agents for known URLs only, in this priority order:

- First, any fetchable URL currently marked `(snippet)` in a thread file that is needed to
  satisfy a requirement still `partial` or `not found`, or to resolve a brief item (including
  secondary/practitioner trace pages for folk claims).
- Second, any URL cited by an Executive Summary or High-confidence claim that wasn't already
  fetched in full in a `source-*.md` or `thread-*.md` file. Don't re-extract a URL that a thread
  agent already fetched and quoted in full.

A claim whose page fails to fetch loses High confidence or leaves the summary.

## 2. Draft → `draft.md`

Write it once, from the retained files, not from conversation memory.

1. Tag every factual claim with an ID, account for every sub-question (`answered`, `partial`, or
   `open` in Gaps per `references/dr-plan-schema.md`), and report each brief item with its
   type's status from the schema (assumption, flagged claim, option). Every requirement not
   satisfied appears in Gaps, `blocked` ones with their prerequisite.
2. When the brief asks to evaluate a claim or rule of thumb and fetched sources plus searches show
   no empirical study exists (only a practitioner heuristic or untraced quote), the verdict is
   `untraced` ("no source found; unsupported heuristic"), never "not evaluated", and never
   "false" or "fails". A summary that groups brief claims keeps `untraced` apart from
   `contradicted`: "four of seven are contradicted and three are untraced", not "all seven fail".
3. **Caveats carry forward.** Every fetch-note caveat on a file a claim cites (model-summarized
   rendering, abstract-only, snippet-only, mirror or secondary copy) appears in that finding or in
   Gaps. So does every fetched source that cuts against a finding, even one found outside a
   `## Disconfirming` section.
4. **Counter-evidence.** Weigh the disconfirming sources the thread agents fetched (each thread
   file's `## Disconfirming` section) in the findings and confidence ratings. List every
   disconfirming query and its result in the Research Log, including those that found nothing.
5. **Challenges.** Every challenge in `thread-lateral-challenge.md` lands its substance (claims and
   evidence) in exactly one place:
   - **reflected in the findings**: a conclusion narrowed, qualified, reversed, or confirmed by its
     `thread-challenge-*.md` evidence;
   - **Non-obvious connections**: a challenge that sharpens a conclusion without changing it;
   - **Gaps and Uncertainties**: a challenge set aside, with the reason (tested and failed,
     unresolved in quick, or out of budget).
6. Fill **Non-obvious connections** from both lateral passes (see `references/dr-output-common.md`):
   every leap and challenge by name with its verdict, but only one kept in the findings carries
   claim IDs there.

## 3. Verification → `research-output.md`

Read `references/dr-verification.md` and run it on `draft.md`. It ends with the two final checks.

## Lateral calibration

Before writing the final frontmatter, count across both lateral passes: leaps proposed, leaps rated
worth pursuing, and leaps that reached the final findings (a claim outside Gaps and the Research Log
traces to one; set-aside leaps and dead ends don't count). Record them in `notes.md` and the report's frontmatter (`lateral-proposed`,
`lateral-pursued`, `lateral-in-findings`). The lateral hit rate across runs comes from these.
