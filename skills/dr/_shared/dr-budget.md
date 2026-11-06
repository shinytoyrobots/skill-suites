# Budget: tiers, caps, models, spend

Read this before launching the first agent. The numbers are starting values, set from early runs that used 19-32 subagents and 1.28M-2.09M subagent tokens against a declared 4. Loosen them only if coverage or accuracy drops.

## Depth tiers

Weight goes to Phases 1-3: all searching, lateral thinking and challenge follow-up happen there.
Phase 4 launches only extractions and one verifier.

Each tier splits its agents into a **research pool**, a **reserved pool**, a **gap pool** and an
**extraction allowance**. Research stages (scan, lateral exploration, Phase 2 threads, expansion and
challenge threads) draw only on the research pool. The reserved pool holds the two mandatory
agents and can't be spent on research. The gap pool is only for the Phase 3 coverage pass. When
the research pool runs out, stop researching, run the challenge if it hasn't run, then the
coverage pass, and move to Phase 4.

| Tier | Research pool | Reserved pool | Gap pool | Extractions | Total agents |
|---|---|---|---|---|---|
| quick | 2: scan 1, lateral exploration 1. No expansion. | 2: challenge 1, verifier 1 | 0 (no coverage pass) | up to 2 | 4-6 |
| standard | 6-10: scan, lateral exploration, Phase 2 threads, up to 2 expansion iterations (challenge threads first; keep at least 2 slots for Phase 3) | 2, as for quick | up to 4 | up to 6 | 9-22 |
| deep | 9-15, with expansion looping while productive (keep at least 3 slots for Phase 3) | 2, as for quick | up to 6 | up to 8 | 12-31 |

No pool lends to another: an unused reserved or gap slot never moves to the research pool, and an
unused research slot never moves to the gap pool.

**Extractions** (haiku, cap 8) pin single sources and don't use research-pool slots. The
allowance is one cumulative count across Phases 2-4, not per phase. Priority: pages behind a
requirement not yet satisfied (the plan schema's Requirements table), then an
open-record alternative for a blocked host, then Executive Summary sources. Success is a
requirement met with usable evidence, not a `source-*` file count.

Default tier: **standard**. An unused reserved agent is never moved to the research pool.

## Per-agent caps

| Role | Model | Tool-call cap | Notes |
|---|---|---|---|
| Web scan (Phase 1) | sonnet | 25 | reads `references/web-researcher.md` |
| Thread agent (search, expansion, challenge, gap) | sonnet | 20 | web-researcher methodology |
| Extraction (one URL) | haiku | 8 | reads `references/structured-notes.md` |
| Lateral (exploration, challenge) | sonnet | 12 | reads `references/lateral-thinking.md` |
| Lateral (quick-tier challenge) | sonnet | 6 | |
| Verifier | sonnet | 20 quick, 25 standard, 30 deep | one pass; reads `references/dr-verifier.md`; see `references/dr-verification.md` |
| Orchestrator (you) | opus | none | synthesis only; never does subagent work inline |

Pass `model` explicitly on every launch; never rely on inheritance. An agent that hits its cap
stops and reports what it didn't reach.

Search agents run on sonnet and extraction on haiku. On haiku, search threads fetched poorly in testing:
one fell back to `curl`, never used the fetch tool, and left most flagged claims resting on snippets.

## Search budget

WebSearch is capped at 200 searches per session, and the early runs hit that cap by Phase 1-3,
which starved later phases. Allocate per run:

| Tier | Total | Phase 1-2 | Phase 3 (challenge, expansion) | Coverage pass |
|---|---|---|---|---|
| quick | 40 | 34 | 6 (challenge only) | 0 |
| standard | 100 | 60 | 25 | 15 |
| deep | 160 | 95 | 40 | 25 |

Phase 4 has no search allowance. The coverage allowance is the last stage of Phase 3; unused
Phase 1-2 and Phase 3 searches roll forward into it. Disconfirming queries are part of each thread agent's own
allowance (checklist item 9). Each column is a separate allowance; a phase can't borrow from a
later one, and unused Phase 1-2 searches roll forward to Phase 3. Hold the challenge agent's
allowance (6, or 8 in standard and deep) back from Phase 3 until it launches. Give each
agent an explicit search allowance in its prompt (for example "at most 8 WebSearch calls"), and
**debit it at launch**, not on return: the spend table's "Searches allocated" total is
the sum of allowances handed out, so parallel agents can't jointly overrun the budget. When an
agent returns, replace its allowance with the searches it actually used and reclaim the rest.
When a phase's allowance is allocated, stop launching search agents for that phase. Extraction agents get an allowance of 0.

## Concurrency

At most **10 subagents run at once**. Launch more in batches as earlier ones return. A launch
refused for capacity waits and retries; it is **never** done inline by the orchestrator. Inline
subagent work defeats the budget and the audit trail.

## Fetch once

- Before launching Phase 2 or 3 agents, read `sources-index.md` and list the pages more than one
  thread will need. Assign each such page to a single agent (or one extraction agent first).
- Every agent prompt says: check `sources-index.md` and existing `source-*.md` files first, and
  fetch only what is missing.

## Launch prompt checklist

Every launch prompt includes:

1. The methodology file to read first: the absolute path of the file in this skill's `references/` directory.
2. The task, the working directory, and the file name(s) to write.
3. `Tool-call cap: N (keep the last 2 calls for writing your file). Search allowance: M. When the
   search allowance is spent, stop searching but still fetch and write up what you found. When the
   tool-call cap is reached, stop and list what you didn't reach.` An allowance of 0 means don't
   search at all; it never means stop working.
4. `Stop early when new sources repeat what is already in the folder.`
5. `Check sources-index.md and source-*.md before fetching; fetch only what is missing.`
6. `Write full findings to disk. Return only a 3-5 line summary, plus: tool calls used, searches used.`
7. For extraction: `Start the file with YAML frontmatter: url, published (date), and fetch-status:
   ok or failed. If the fetch fails, is blocked, paywalled or the wrong page, write the file
   anyway with fetch-status: failed and the reason.`
8. For thread agents: `Fetch at least one source for every assigned sub-topic before deepening any single sub-topic. When a publisher URL blocks (403, paywall, redirect loop), don't retry that host — fetch the open record instead (https://api.openalex.org/works/doi:{doi}, https://api.crossref.org/works/{doi}, PMC/Europe PMC, arXiv, or a reputable secondary summary). Mark any URL you cite but didn't fetch successfully with "(snippet)" or "(fetch failed)" right after the URL. Those are leads, not evidence.`
9. For thread agents: `The main claim you are testing: {claim}. Spend at least one search on a
   query phrased to find evidence against it, and fetch the strongest counter-evidence source you
   find. Record each disconfirming query, what it found (or that it found nothing), and the
   fetched source under a "## Disconfirming" heading in your file.`

## Spend table

`notes.md` carries an **Agent spend** table. Write the row **at launch** (status `launched`, with
its search allowance), then complete it from the completion notice when the agent returns:

| # | Stage | Agent | Model | Status (launched/returned) | Search allowance | Searches used | Tool calls | Tokens |
|---|---|---|---|---|---|---|---|---|

Keep running totals under the table: agents launched (by pool), searches allocated, subagent
tokens. On resume, a `launched` row with no return still counts: its agent against its pool and
its full allowance against the search budget. Mark it `lost` and relaunch only if the pool allows.

## Spend checkpoint

Fires only past a threshold, so the default run is unsupervised. The threshold is **2.5M subagent
tokens** (above the maximum seen in early runs), unless `$ARGUMENTS` names another. Phase 0 doesn't ask. When the running
total crosses it, show tokens so far and the planned next agents, and ask: continue, narrow, or
go to the draft. In a non-interactive run, skip the question and go to the draft.
