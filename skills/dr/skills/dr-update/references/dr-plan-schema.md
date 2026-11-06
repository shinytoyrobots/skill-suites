# plan.md: checkpoint and resume

`plan.md` is written at the end of Phase 0 and updated as each stage starts and finishes. It is
the run's checkpoint: a rerun pointed at an existing folder resumes from it.

## Statuses

`open`, `in-progress`, `done`, `skipped`. `done` and `skipped` are terminal.

`skipped` needs a reason in Notes, and is valid in these cases:

- the tier doesn't require the stage (expansion and coverage in quick), or
- **budget**: the research pool or the search budget ran out. When the run moves on for this
  reason, every research stage still `open` or `in-progress` (scan, deep-dive, expansion) becomes
  `skipped`, reason `budget`, with the unfinished threads listed in Notes. Those threads go to
  Gaps and Uncertainties. The challenge still runs, from the reserved pool, and the coverage
  stage still runs, from the gap pool and the coverage allowance. Coverage is `skipped`, reason
  `budget`, only when the coverage allowance itself is spent, or
- **nothing missing** (coverage only): every requirement is satisfied or `blocked`, and every
  brief item is resolved or `blocked`.

**Never skippable:** brief, challenge, draft, verification, final output.

## Schema

```markdown
---
tier: quick | standard | deep
fast-moving: true | false
freshness-threshold: {months, or n/a}
spend-threshold: {subagent tokens}
form: {output form from the brief}
---

## Stages
| Stage | Status | Output file | Notes |
|---|---|---|---|
| brief | done | brief.md | |
| scan | open | thread-*.md | |
| deep-dive | open | source-*.md | |
| challenge | open | thread-lateral-challenge.md | after deep-dive, before expansion |
| expansion (iteration 1) | open | thread-*.md | one row per iteration; skipped in quick |
| coverage | open | thread-gap-*.md | gap pool; skipped: nothing missing, quick tier, or budget |
| evidence pinning | open | source-*.md | |
| draft | open | draft.md | |
| verification | open | verification.md | one verifier pass, one fix pass |
| final output | open | research-output.md | done only after a verification outcome is recorded and both final checks pass |

## Sub-questions
| # | Sub-question | Perspective | What would answer it | Status (open/partial/answered) | Files |

## Requirements
| ID | Sub-question | Requirement | Kind (existence/evidence) | Investigation (open/searched/fetched) | Verdict | Files and search scope |

## Brief items
| ID | Type (assumption/flagged claim/option) | Item | Status | Evidence |

## Coverage targets
| # | Targets (requirement or brief-item IDs) | Missing evidence | Thread file | Status (launched/returned) |
```

Add an expansion row each time a new iteration starts.

## Requirements

At Phase 0, split each sub-question's "What would answer it" into requirements (R1a, R1b, ...).
Every tool, claim, source, registry or measure the brief or the cell names is its own row, so one
example never stands for a whole category. **Kind**: `existence` for "does any X do Y" or a
survey; `evidence` for anything that needs a source or a measurement. **Files and search scope**
lists the files that satisfy it, or the queries and sources tried.

Verdicts:

- `met`: retained evidence satisfies it.
- `met-negative`: an `existence` requirement whose recorded search scope found nothing. Satisfied.
- `not found`: an `evidence` requirement whose recorded search found nothing. Not satisfied; the
  report says "no source found", never "false" or "fails".
- `partial`: some evidence, but a core part is missing or snippet-only. Not satisfied.
- `blocked`: a named prerequisite is missing (an API key, a paywall with no open record). Not
  satisfied, and not a coverage target; it goes to Gaps with the prerequisite.
- `open`: not yet investigated.

`met-negative` and `not found` both need a recorded search scope; without one the verdict is
`open`.

## Sub-question statuses

`answered` only when every one of its requirements is `met` or `met-negative`; `open` when no
usable evidence was fetched for any of them; otherwise `partial`, with the unsatisfied
requirement IDs in Files. Normal scope or transfer caveats belong in Gaps without downgrading the
status. A heuristic-origin trace (the claim comes from a practitioner, with no study behind it)
satisfies a requirement to trace the claim's origin, not one to test it.

## Brief items

At Phase 0, one row (B1, B2, ...) for each stated assumption, each claim the brief flags for
checking, and each option or method it asks to compare or test. IDs are stable for the run.
Statuses by type:

- **assumption**: `untested` / `held` / `failed`.
- **flagged claim**: `not checked` / `supported` / `contradicted` / `untraced` (no source found
  after a recorded search). `untraced` is never reported as false.
- **option**: `not assessed` / `literature only` / `measured` (run or measured in this research) /
  `blocked` (a named prerequisite is missing; record it and a reproducible proposed test). When
  the brief asks for a test and the run's tools allow it, measure it.

**Resolved** (not a coverage target): `held`, `failed`, `supported`, `contradicted`, `untraced`,
`measured`, and `literature only` when the brief didn't ask for a test. `blocked` is reported in
Gaps, never targeted. Everything else is unresolved.

## Resume

1. Read `plan.md`, `brief.md` and `notes.md`. Don't re-ask Phase 0 questions.
2. Find the first stage whose status is `open` or `in-progress`. Resume there. An `in-progress`
   stage restarts from its inputs, reusing any output files already on disk.
3. A run that answered every sub-question but stopped mid-draft resumes at `draft`: synthesis and
   verification are stages, so "every sub-question answered" never means "nothing left".
4. **A plan from before Requirements** (it has "Hypotheses from the brief" and no Requirements
   or Coverage targets table): migrate it before resuming. Classify each old hypothesis row
   against `brief.md` (a claim the brief flags for checking becomes a flagged claim, a test or
   comparison it asks for becomes an option, anything else an assumption), keep its evidence, and
   reassess its status under the new vocabulary: a `failed` whose evidence is "untraced" or "no
   source found" becomes `untraced`. Build Requirements from each sub-question's cell and Files,
   and add an empty Coverage targets table.
5. **Coverage stage**: relaunch only the Coverage targets rows not yet `returned`; never restart
   the whole pass.
6. Recount spend from the Agent spend table before launching anything (see the spend table in
   `references/dr-budget.md`): agents launched but never returned still count.
7. If the folder has no `plan.md` (a run from before this schema), say so and ask whether to
   rebuild one from `brief.md`, `notes.md` and the files on disk, marking stages whose outputs
   exist as `done`, or to start fresh.
