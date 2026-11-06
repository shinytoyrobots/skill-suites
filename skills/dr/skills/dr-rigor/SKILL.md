---
name: dr-rigor
description: Rigorous research with a tiered budget, a challenge phase and an independent claim check. Use when the answer will be relied on or challenged by others and you need counter-evidence, stated gaps and a claim ledger. For open-ended discovery use dr-explore.
license: Apache-2.0
compatibility: Needs a host that can launch subagents and has web search, web fetch and file write tools. The mechanical checks need python3.
metadata:
  suite: dr
  capability-class: intelligence-gathering
  tier: "I"
---

# dr-rigor: rigorous deep research

Files this skill reads or launches, all in its own directory:
- Methodology for subagents: [web-researcher.md](references/web-researcher.md), [lateral-thinking.md](references/lateral-thinking.md), [structured-notes.md](references/structured-notes.md), [dr-verifier.md](references/dr-verifier.md)
- Budget, plan and verification rules: [dr-budget.md](references/dr-budget.md), [dr-plan-schema.md](references/dr-plan-schema.md), [dr-verification.md](references/dr-verification.md)
- Output frame and forms: [dr-output-common.md](references/dr-output-common.md), [strategic assessment](references/dr-output-strategic-assessment.md), [literature review](references/dr-output-literature-review.md), [decision brief](references/dr-output-decision-brief.md), [landscape map](references/dr-output-landscape-map.md); synthesis steps in [synthesis.md](references/synthesis.md)
- Final checks: [citation-check.py](scripts/citation-check.py), [verify-ledger.py](scripts/verify-ledger.py)

Paths such as `references/…` and `scripts/…` are relative to this skill's directory. Resolve them to absolute paths before handing one to a subagent or running a script.

## Input

`$ARGUMENTS` = the research question, or a path to an existing run folder.

- An existing run folder (it holds `plan.md`, `brief.md` or `notes.md`): **resume**. Read
  `references/dr-plan-schema.md` and follow its Resume section, including its rule for folders with
  no `plan.md`. Skip Phase 0.
- Empty: ask for a research question.
- If the invocation says the brief is complete (a non-interactive run), ask no Phase 0 questions: use the
  brief as given, tier **standard** unless it names one.

## Phase 0: Brief, tier, plan

One `AskUserQuestion` call, then start. The research question comes from `$ARGUMENTS`; a tier or
destination given there is used without asking. Ask:

1. **Known context**: what the user already knows or assumes.
2. **Sources to check**: URLs, papers, people, organizations to prioritize.
3. **Desired output**: strategic assessment, literature review, decision brief, or landscape map.
4. **Depth tier**: quick, standard (default), or deep.

Destination defaults to `./.dr/` in the current project (see Working memory). The spend threshold is the silent
default in `references/dr-budget.md`; never ask for it.

Then, without another round-trip:
- **Prior research.** Check the run index (see Run index below) for an obvious match on the
  topic. If one exists, name it in your first progress message (and suggest dr-update if it
  mostly needs refreshing), then carry on. Don't wait for an answer. Skip in a non-interactive run.
- Write `brief.md` with the answers.
- Read `references/dr-budget.md`. It governs every launch below.
- Write `plan.md` from `references/dr-plan-schema.md`, and `notes.md` with an empty Agent spend table.
  Fill the plan:
  - **Perspectives**: 3-5 stakeholders who'd see the question differently (for example buyer,
    builder, regulator, critic).
  - **Sub-questions**: 3-6, covering the brief's explicit questions and flagged items first, then
    key stakeholder angles, each with realistic criteria for what would answer it.
  - **Requirements**: split each sub-question's criteria into named requirements, one per tool,
    claim, source or measure, each `open` (see Requirements in the schema).
  - **Brief items**: one row for each stated assumption, each claim the brief flags for checking,
    and each option or method it asks to compare or test, with its type's starting status.
  - **Fast-moving**: whether the topic changes month to month, and if so a freshness threshold.
- Start Phase 1 immediately. The plan isn't shown for approval; it is on disk if the user wants
  to edit it.
- Mark the `brief` stage `done`. Update each stage's status in `plan.md` as it starts and finishes.

## Launch rules (every agent)

Follow `references/dr-budget.md`: explicit `model`, the role's tool-call cap and a search allowance in
the prompt, fetch-once, at most 10 agents at once, and the launch prompt checklist. Write each
agent's spend-table row at launch, debiting its allowance. Never do an agent's work inline
because a launch was refused; wait and retry. After each agent returns,
complete its spend-table row and check the spend threshold. When the research pool or search
budget is spent, mark the open research stages `skipped` (reason `budget`), run the Phase 3
challenge if it hasn't run, then the coverage pass (its own pool and allowance), then go to
Phase 4.

## Phase 1: Initial scan

1. Write 5-8 diverse queries (vary keywords, angles, specificity).
2. In parallel: a **web scan** agent (web-researcher methodology) running those queries, and a
   **lateral** agent (lateral-thinking methodology) scouting non-obvious connections from the
   question and known context.
3. Write summaries to `notes.md`. Add any "worth pursuing" leaps to the threads list.
4. Read `notes.md` back and list the **threads to pull**: leads, unexpected angles,
   contradictions, gaps.

## Phase 2: Deep dive

For each thread: launch **extraction** agents (`references/structured-notes.md`), one per source URL,
each writing `source-{name}.md`; and **thread** agents (web-researcher methodology) for threads
that need more search, each writing `thread-{name}.md`. Give every thread agent the main claim
it is testing; it runs a disconfirming query and fetches the strongest counter-evidence (launch
checklist item 9 in `references/dr-budget.md`). Then cross-reference claims, flag
contradictions, and record findings in `notes.md` with confidence (High/Medium/Low). A claim
whose counter-evidence was fetched and holds up can't be High confidence.

Two articles from the same origin (one press release, paper or post) count as one source; High
confidence needs two independent origins. Each `source-*.md` records its publish date. Update
requirement, sub-question and brief-item statuses in `plan.md` as evidence arrives, recording the
search scope behind every `met-negative`, `not found` or `untraced`.

**Provenance.** A claim needs the URL of a source that was fetched and written to a `source-*.md`
or `thread-*.md` file. A search snippet, a failed or paywalled fetch, or a page never written to
disk is not a source.

## Phase 3: Challenge and scope expansion

All lateral thinking and all web research finish here; Phase 4 searches nothing.

**Challenge** (every tier, never skipped; `thread-lateral-challenge.md`). First, write the
emerging conclusions to `notes.md` under `## Emerging conclusions`: the 3-5 claims the report
would lead with, each with its confidence and files. Then launch one lateral agent (sonnet,
reserved pool, cap 12; 6 in quick) with this prompt after the methodology line:

> Read `notes.md` in {folder}, section "Emerging conclusions". Your topic is those conclusions, not
> the original question. For each of the 2-3 most consequential, ask: which adjacent discipline,
> or which inverted premise, would disagree, and why? Generate each challenge with one of your
> named methods, name its test ("if this challenge is right, we'd expect to find X"), and check
> it. Rate each as your methodology says: worth pursuing (test found, or inconclusive with a named
> search that would settle it), tenuous, or dead end. Write `thread-lateral-challenge.md`.

**Expansion** (standard and deep; loop while productive). Each iteration is a row in `plan.md`:

1. Read `notes.md` and `thread-lateral-challenge.md`. List the expansions in this order:
   challenges rated worth pursuing; then requirements not yet satisfied and unresolved brief
   items; then adjacent topics that keep appearing, perspectives not yet represented,
   contradictions to resolve.
2. Launch thread agents for the most valuable, from the research pool and the Phase 3 search
   allowance. A challenge's thread writes `thread-challenge-{slug}.md`.
3. Record productive expansions and dead ends, and update the emerging conclusions. Loop only if
   this iteration surfaced meaningful new information and the pool and search budget allow it
   (standard: at most 2 iterations). Don't stop early by judging an item the brief names
   (its questions, flagged claims, options to test, named tools or sources) "low-consequence":
   while one is unresolved and the pool allows, run the iteration. Whatever is left goes to the
   coverage pass.

**Coverage pass** (standard and deep; one pass, no loop; a `coverage` row in `plan.md`):

1. List the candidates: every requirement `open`, `partial` or `not found`, and every brief item
   not resolved (schema, Brief items). `blocked` items are never candidates. If none, mark the
   stage `skipped`, reason `nothing missing`.
2. Group related candidates (one thread takes up to 3 that share sources) and rank: items the
   brief names explicitly first, then requirements behind the emerging conclusions, then the
   rest. You may rank a brief-named item lower; you may not drop it as low-consequence.
3. Launch from the gap pool and the coverage search allowance (`references/dr-budget.md`),
   at most the pool's size, recording each in the Coverage targets table. Each is a thread agent
   (sonnet, cap 20) writing `thread-gap-{slug}.md`, told the exact missing evidence, the search
   scope already tried (from the requirement's record), and to fetch open records before giving
   up on a blocked host. Up to 2 may instead be extraction agents for known URLs.
4. When they return, update the requirement and brief-item verdicts. Candidates beyond the pool
   go to Gaps and Uncertainties as `Not reached: {item} (coverage pool)`.

In quick there is no expansion or coverage pass (mark both `skipped`, reason "quick tier"): run the
challenge after Phase 2. Its worth-pursuing challenges go to Gaps unresolved, and every
requirement not satisfied and every unresolved brief item goes to Gaps as
`Not reached: {item} (quick tier)`.

## Phase 4: Synthesis and verification

Read `references/synthesis.md`, `references/dr-output-common.md` and the form file
(`references/dr-output-strategic-assessment.md`, `references/dr-output-literature-review.md`,
`references/dr-output-decision-brief.md`, or `references/dr-output-landscape-map.md`). Three
stages, each a `plan.md` row:

1. **Pin evidence**: extraction agents for any unfetched source a key claim needs.
2. **Draft** → `draft.md`, once, accounting for every challenge.
3. **Verification** (`references/dr-verification.md`): one verifier pass, one fix pass →
   `research-output.md`. Mark `final output` done only when a verification outcome is recorded
   and both final checks pass.

## Working memory

**Directory**: the brief's destination, or
`./.dr/{YYYY-MM-DD}-{topic-slug}/`.

- `brief.md`, `plan.md`: the brief and the checkpoint.
- `notes.md`: summaries, thread lists, the Agent spend table. Read it to re-orient at each phase.
- `source-{name}.md`: one per fetched source (URL, publish date, key quotes, reliability).
- `thread-{name}.md`: one per substantial thread, with the URLs it rests on.
- `sources-index.md`: every source consulted, one line each with its URL.

Write to disk after every agent return; read back from files, not memory. Keep every file after
synthesis. A finding is checked against them later.

## Run index

After the final checks pass, append one row to the **Run records** table at the end of
`./.dr/index.md` (add the heading and
table if missing), from the report's frontmatter. Non-interactive runs are not indexed.

| Date | Folder | Form | Tier | Agents | Subagent tokens | Sources | Verification (removed) | Verifier pass rate | Lateral (proposed / pursued / in findings) |
|---|---|---|---|---|---|---|---|---|---|

## Blocked protocol

If you can't make progress for 5 minutes (API failures, paywalls, ambiguous direction), write
`blocked.md` (what you tried, what failed, what's needed, suggested manual steps) and continue on
the unblocked threads.
