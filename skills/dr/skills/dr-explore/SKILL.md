---
name: dr-explore
description: Exploratory deep research with working memory and phased discovery, including a lateral-thinking scout. Use to map a topic, find leads and non-obvious connections. No independent claim check; for work that will be challenged use dr-rigor, and audit any run afterward with dr-verify.
license: Apache-2.0
compatibility: Needs a host that can launch subagents and has web search, web fetch and file write tools. The mechanical checks need python3.
metadata:
  suite: dr
  capability-class: intelligence-gathering
  tier: "I"
---

# dr-explore: exploratory deep research

Methodology files for the subagents this skill launches: [web-researcher.md](references/web-researcher.md), [lateral-thinking.md](references/lateral-thinking.md), [structured-notes.md](references/structured-notes.md). Paths such as `references/…` and `scripts/…` are relative to this skill's directory. Resolve them to absolute paths before handing one to a subagent or running a script.

## Input

`$ARGUMENTS` = the research question or topic.

If `$ARGUMENTS` is empty, ask the user for a research question before proceeding.

## Phase 0: Research Brief

Before starting research, collect a structured brief. Use `AskUserQuestion` to gather:

1. **Research question** (confirmed from $ARGUMENTS or clarified)
2. **Known context** — "What do you already know or assume about this topic? Paste any relevant text, notes, or background."
3. **Sources to check** — "Any specific URLs, papers, people, or organizations I should prioritize?"
4. **Desired output** — "What form should the final output take?"
5. **Output destination** — "Where should I write the research output? Provide a path, or leave blank for `./.dr/` in the current project."

Options for desired output:
- **Strategic assessment** — findings + recommendations + next steps
- **Literature review** — comprehensive survey of what's known, with gaps identified
- **Decision brief** — pros/cons/recommendation for a specific choice
- **Landscape map** — who's doing what, where the space is heading

Store the brief answers for use throughout the research. The output destination from the brief determines where all files are written (working memory, final output, cleanup).

## Research Philosophy

This skill is designed to run with minimal human supervision. **Be thorough, not fast.** The goal is depth and breadth of understanding — exhaust available sources before synthesizing. Every phase should leave no obvious stone unturned before moving on.

**Context management**: The working notes directory is your external memory. Write findings to disk frequently — after reading a source, after an agent returns, after exploring a thread. Use granular temp files (per-source, per-topic, per-thread) in addition to the main notes file. Read back from disk when you need prior findings. This keeps conversation context clean and lets you operate over extended sessions. Don't hold large bodies of findings in conversation context.

**Scope expansion is not optional.** Good research reveals questions you didn't know to ask. After the initial scan and deep dive, actively look for adjacent angles, missing perspectives, and unexplored threads.

**Let the topic dictate the depth.** Some questions are well-answered in 10 minutes. Others need an hour. Don't pad shallow topics or rush deep ones. Keep researching as long as you're learning genuinely new, useful information. Stop when you're not.

## Phase 1: Initial Scan (broad mapping)

**Goal**: Map the landscape. Understand what exists, who the key players/voices are, and where the information lives.

1. Generate 5-8 diverse search queries from the research question (vary keywords, angles, specificity)
2. Use the Agent tool (model: sonnet) to launch a subagent. Tell it to first read `references/web-researcher.md` for its methodology, then execute the search with these queries. Instruct the subagent to write full findings to the working notes directory and return only a 3-5 line summary to the caller.
3. In parallel, use the Agent tool (model: sonnet) to launch a second subagent. Tell it to first read `references/lateral-thinking.md` for its methodology, then scout non-obvious connections using the research question and any known context from the brief. Instruct it to write full findings to the working notes directory and return only a 3-5 line summary.
4. Write initial findings summaries to the working notes file (see Working Memory below). If the lateral-thinking agent found any "worth pursuing" leaps, add them to the threads list.
5. Read back the notes file to identify **threads to pull** — promising leads, unexpected angles, contradictions, gaps, and any lateral connections worth investigating

## Phase 2: Deep Dive (follow the threads)

**Goal**: Go deep on the most promising leads from Phase 1. Be thorough — read full articles, not summaries.

For each thread identified:
1. Use the Agent tool (model: haiku) to launch parallel subagents (one per source URL). Tell each to first read `references/structured-notes.md` for its methodology, then fetch and extract the assigned source. Instruct each to write full extraction to a `source-{name}.md` file in the working notes directory and return only a 3-5 line summary to the caller.
2. Cross-reference claims across sources — flag contradictions
3. Write findings to working notes after each thread, marking confidence level (High/Medium/Low)
4. Track provenance. Every claim needs the URL of a source that was fetched and written to a `source-*.md` or `thread-*.md` file. A search snippet, a failed or paywalled fetch, or a page that was never written to disk is not a source — do not state it as a finding.

Use the Agent tool (model: sonnet) to launch parallel subagents for independent threads that need additional search (tell each to first read `references/web-researcher.md` for its methodology). For targeted URL extraction, launch subagents (model: haiku) that first read `references/structured-notes.md`. Instruct all subagents to write full findings to disk and return only a 3-5 line summary. After agents return, merge summaries into the notes file.

## Phase 3: Scope Expansion (loop while productive)

**Goal**: Based on what Phases 1-2 revealed, identify angles the original question didn't anticipate. **This phase loops — but only while it's producing genuinely new information.**

Each iteration:
1. Read working notes from disk and review for:
   - Adjacent topics that keep appearing
   - Questions the research raised but didn't answer
   - Perspectives or stakeholders not yet represented
   - Contradictions that need resolution
2. Generate new search queries for the most valuable expansions
3. Use the Agent tool (model: sonnet) to launch subagents for expanded scope (tell each to first read `references/web-researcher.md` for its methodology). Instruct each to write full findings to disk and return only a 3-5 line summary.
4. On the first iteration only, use the Agent tool (model: sonnet) to launch a subagent. Tell it to first read `references/lateral-thinking.md` for its methodology, then explore non-obvious connections using the accumulated findings from Phases 1-2 as context. Richer context produces better leaps. If it surfaces "worth pursuing" connections, fold them into subsequent iterations.
5. Write results to temp notes files (one per thread/topic)
6. Assess: **Did this iteration surface meaningful new information?**
   - **Yes** — loop again from step 1
   - **No** — sources are repeating, new angles aren't producing substance, or the topic is well-covered. Move to Phase 4.
7. Note which expansions were productive and which were dead ends

Don't skip this phase, but don't force it either. If the initial scan and deep dive already covered the topic thoroughly, one quick expansion pass that confirms coverage is enough. If the topic is sprawling and every thread opens three more, keep going.

## Phase 4: Synthesis

**Goal**: Produce the final output in the format requested in the brief.

### Standard Output Structure

```markdown
# Deep Research: {Topic}
**Generated**: {YYYY-MM-DD HH:MM}
**Skill**: dr-explore
**Data freshness**: {sources and their dates}
**Research question**: {original question}
---

## Executive Summary
{3-5 sentence overview of key findings}

## Key Findings
{Organized by theme, not by source. Each finding includes:}
- **Finding**: {What we learned}
- **Evidence**: {Supporting sources with URLs from retained source or thread files}
- **Confidence**: {High/Medium/Low — based on source quality and corroboration}
- **Implication**: {So what — why this matters for the research question}

## Landscape / Context
{Map of the space: key players, trends, state of play}

## Gaps and Uncertainties
{What we couldn't determine, conflicting information, areas needing further research}

## Recommendations
{Actionable next steps, ranked by priority}

## Sources
{Complete bibliography with URLs, access dates, and brief relevance notes}

## Research Log
{Summary of phases, scope expansions, and dead ends — meta-transparency on how the research was conducted}
```

Adapt this structure to match the desired output format from the brief (strategic assessment, literature review, decision brief, or landscape map). Apply the provenance rule in Phase 2 before each finding.

## Working Memory

The working notes directory is critical infrastructure — it is your **external memory** that keeps the conversation context clean over a long research session.

**Directory**: Use the output destination from the brief. If none was specified, default to `./.dr/{YYYY-MM-DD}-{topic-slug}/`

**File strategy**: Use multiple files, not one monolith. Write frequently and granularly:

- **`notes.md`** — Main notes file. Updated after each phase with summaries and thread lists. This is the file you read back to orient yourself.
- **`brief.md`** — Captured research brief (written once in Phase 0)
- **`source-{name}.md`** — One file per significant source after deep-reading it (URL, key quotes, takeaways, reliability assessment). Kept after synthesis.
- **`thread-{name}.md`** — One file per research thread when a thread gets substantial (findings, cross-references, open questions, and the URLs they rest on). Kept after synthesis.
- **`sources-index.md`** — Running list of all sources consulted with one-line summaries and URLs

**Rules**:
- **Write to disk early and often** — after reading a source, after an agent returns, after exploring a thread. Don't accumulate findings in conversation context.
- **Read back from files** (not from conversation memory) when you need prior findings for synthesis or scope expansion
- When starting a new phase, read `notes.md` to re-orient rather than relying on what's in context
- This pattern lets you run extended research without context bloat

## Persistence

Save final output to `research-output.md` in the working directory established in Working Memory (user-specified destination, or the `./.dr/` default).


### Retained files

After synthesis is complete and `research-output.md` is written, keep the working files. The directory should contain:
- `research-output.md` — the final deliverable
- `notes.md` — the research log / audit trail
- `brief.md` — the original research brief
- `sources-index.md` — the source bibliography
- `source-*.md` and `thread-*.md` — what was actually fetched. Do not delete them. A finding is checked against these files later.

## Blocked Protocol

If at any point you cannot make progress for 5 minutes (API failures, paywalled sources, ambiguous direction), write a `blocked.md` to the same run directory explaining:
- What you were trying to do
- What went wrong
- What information is still needed
- Suggested manual steps the user could take

Then continue researching whatever threads remain unblocked.
