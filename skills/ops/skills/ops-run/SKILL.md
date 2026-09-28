---
name: ops-run
description: Executes an operations order (OPORD) from ops-order phase by phase — launching each skill as a subagent, applying its pre-committed adaptation rules, stopping at operator checkpoints, and keeping resumable state. Use when the operator wants an OPORD executed, asks to run or resume the plan, or wants to start from a given phase. Not for producing the plan (ops-plan, ops-order), for monitoring skills the operator runs by hand (ops-assess), or for running a single skill directly.
license: Apache-2.0
compatibility: Execution needs a host that can launch subagents and pause mid-run for a person's decision. Without both, use ops-assess to monitor a hand-run plan instead.
metadata:
  suite: ops
  capability-class: meta-orchestration
  tier: I
---

# Ops Run — OPORD Execution Engine

Read [ops-doctrine.md](references/ops-doctrine.md) (schemas, execution state, run directory, durable state) and [ops-voice.md](references/ops-voice.md) (checkpoint wording — one decision per checkpoint).

Run is the runtime complement to ops-plan and ops-order. Its state file survives across sessions, so a run can pause for days at a checkpoint and resume where it stopped.

## Input

- **nothing** — resume an in-progress execution, or start the latest OPORD
- **a path** — an `opord.md`, or a run directory containing one
- **`--phase N`** — start or resume at phase N
- **`--dry-run`** — parse and display what would run; launch nothing and write no state

### Resolution

1. In the latest effort directory (see the doctrine), if `execution-state.yaml` has `status: in-progress`, `escalated`, or `paused`, offer to resume it (see Resume below).
2. Otherwise use that directory's `opord.md`.
3. None found: "No OPORD found. Run ops-order first." and stop.

Also read `situation-assessment.yaml` (for Commander's Intent fallback decisions) and `coa-recommended.md` (for wargaming notes) from the same directory when present.

## Phase 0: Parse and Validate

Build an execution plan from the OPORD: topic, Commander's Intent, phases (each with steps — skill, arguments, depends-on, parallel-with, output path, hitl, tier — and transition criteria), the checkpoints with their criteria, and the parsed `n-1-contingencies`, `auto-adapt-rules`, and `escalate-triggers`.

Validate before anything runs:

1. **Every skill is installed.** Check each step's skill, and each substitute in the contingencies, against `force-roster.yaml` in the run directory. First refresh that roster with the ops-recon scan (write it back with `--out` set to the run directory) — skills may have been installed or removed since planning. A missing primary skill with an installed substitute is a warning; with no substitute, it blocks.
2. No circular dependencies in phase ordering.
3. Every `depends-on` resolves to an earlier phase or a step in the same phase.
4. Every checkpoint has criteria.
5. At least one auto-adapt rule and one escalate trigger exist.

On a validation failure, report the specific issue and stop — executing a malformed OPORD produces confident garbage.

**Dry run** — show the parsed plan as a table, the phase dependency graph, the checkpoints with criteria, and all rules and triggers; then "Dry run complete — run without --dry-run to execute." Stop.

## Phase 1: Initialize State

Create `execution-state.yaml` in the run directory, following the doctrine's Execution State Schema exactly. If resuming, load it instead.

## Phase 2: Execute Phases

Process phases in order from `current-phase` (or `--phase N`).

### 1. Phase entry

Set the phase `in-progress` with a start time. Print a one-line phase header. For every phase after the first, evaluate the previous phase's transition criteria; if one fails, stop and say which: "Phase {N-1} → {N} blocked: {criterion}."

### 2. Group steps

Steps with no `depends-on` that share `parallel-with` references form a parallel group. Steps depending on an earlier step in this phase wait for it. Steps depending only on an earlier phase are ready now.

### 3. Launch

Launch each step as its own subagent, using whatever subagent mechanism the host provides. Give the subagent:

- the instruction to run the named skill with the OPORD's arguments
- Commander's Intent, and which phase of how many this is
- the output path from the tasking table, and the instruction to write the primary output there and summarize it in its final response

Launch a parallel group together rather than one at a time. Mark each skill `running` with a start time as it launches.

A subagent is used, not an inline call, so each skill's working context stays out of the run's own — the one-third rule in the doctrine is otherwise unreachable over a multi-phase OPORD.

### 4. Evaluate each result

**a. Failure.** An error, an empty response, or a report that the skill could not complete → mark `failed`.

**b. Auto-adapt rules.** For each rule, check whether its `trigger` text appears in the output summary or the output file (substring match, not judgment). On a match, print it as a fix applied without asking (an auto-adapt rule), execute the response — re-launch with modified arguments, skip and note, or add a compensating step — record `adaptation` on the skill, and increment `auto-adapts-fired`.

**c. Escalate triggers.** If a trigger's condition is observable in the output: run any automatic actions the response specifies, then stop and ask the operator, stating what happened, what was done automatically, and the options. Set the skill `failed`, the phase and run `escalated`, increment `escalates-fired`, and wait.

**d. Backup skill (N-1 contingency).** A failed step that no auto-adapt rule resolved → look up its contingency. If one exists, say which skill failed, the substitute, and the tradeoff, then launch the substitute chain (in its `execution-mode`). If the substitutes also fail (N-2), escalate to the operator whatever the HITL level. Record `contingency` and increment `n1-contingencies-fired`.

**e. Success.** Output present, no rule fired → mark `complete` with the completion time and a one-line `output` summary, and print that line.

Write the state file after every change, not at the end of the phase — a crash or a closed session otherwise loses the record of what already ran.

### 5. Checkpoint

When a step with `hitl: true` completes, stop for the operator with exactly one decision: what the step produced, the OPORD's criteria for this checkpoint, and what approve, approve-with-conditions, and reject would each do next. Use the host's structured question tool when it has one.

- **approve** → record and continue
- **approve with conditions** → record the conditions, carry them out (this may re-enter the current phase for a targeted fix), then continue
- **reject** → record, set `status: paused`, and wait for the operator to invoke ops-run again

Record every decision in `hitl-decisions`. When two checkpoints come due in the same phase, ask them one after the other, never together.

### 6. Phase completion

When every step is complete, or adapted or skipped with a recorded reason, mark the phase `complete`, advance `current-phase`, and print a one-line completion with duration.

### 7. Anti-fixation check

At each phase boundary, check whether the plan's frame still holds: have this phase's outputs changed the understanding of the problem, does Commander's Intent still apply, are the remaining phases still the right next steps? If the frame has shifted, stop and ask one question — continue as planned, or pause and re-run ops-plan — stating the observation, the intent, and the remaining phases. If it holds, continue without printing anything.

## Phase 3: Completion

Write `execution-report.md` to the run directory, with: a header (title, generated time, `ops-run`, the OPORD filename, status); a summary (phases completed, skills executed, duration, and counts of auto-adapts, escalations, contingencies, and checkpoint decisions); a phase log; a step log (phase, skill, status, adaptation, contingency, output); tables of adaptations, escalations, and checkpoint decisions; anti-fixation results; and a quality assessment.

**Quality** — all steps complete without escalation → high; auto-adapt rules needed but no escalations → medium; escalations or skipped steps → low.

**Pattern capture.** Append one entry to `pattern-queue.yaml` in the durable-state directory (`$OPS_STATE`, else `~/.ops-skills/`), using the doctrine's Pattern Queue Entry key names: date, problem class from the mission's task type and topic, the capability chain of the executed skills in order with tiers, sequence type, output quality. If the file is missing, copy [the empty template](assets/pattern-queue.yaml) into place first.

Set `status: complete`. Return, in the operator register:

```
## Run complete: {topic}
{N}/{N} phases, {executed}/{total} skills | quality {level} — {what it means for the pattern queue}
{count} fixes applied without asking (auto-adapt), {count} stops for your decision (escalations)
Report: {run directory}/execution-report.md
Next: ops-learn to promote recurring patterns into the opening book
```

## Resume

On finding a resumable state, show the topic, the phase and status, the last recorded action, and any pending escalation, then ask one question: resume, restart the current phase, or abort.

- **Resume** — re-read the OPORD for arguments (the state file tracks status, not arguments), find the first step that is `pending` or `failed` in the first phase that is `in-progress`, `escalated`, or `paused`, and continue from Phase 2 step 3.
- **Restart phase** — reset that phase's steps to `pending` and re-enter at Phase 2 step 1.
- **Abort** — set `status: aborted`, write the report with partial data, and still capture the pattern with `output-quality: low`, so the failure counts toward the opening book's failure patterns.

If the OPORD was modified after the state's `started` time, warn that the edits may conflict with in-progress state and ask whether to continue or restart.

## Gotchas

- **All steps in a phase fail** → escalate; never advance with zero completed steps.
- **Rejection at the first checkpoint** → pause; don't re-launch skills speculatively.
- **Subagent timeout or crash** → a failure; check the contingency, else escalate.
- **`--phase N` doesn't exist** → list the available phases and stop.
- **State from a different OPORD in the same directory** → match on the state's `opord` field, not the directory.
- **Single-phase or single-skill OPORD** → full state management still applies; no anti-fixation check without a phase boundary.

## Relationship to ops-assess

ops-run is the active executor. ops-assess is the passive monitor for skills the operator runs by hand. Both write the same `execution-report.md` and pattern-queue entry, so ops-learn treats them identically. A hybrid run works: `--phase` through the automated phases, run the rest by hand, then ops-assess over the whole OPORD.
