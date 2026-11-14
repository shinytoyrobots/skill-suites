---
name: orch-run
description: Executes an operations order (OPORD) from orch-plan phase by phase, launching each skill as a subagent, applying its pre-committed adaptation rules, stopping at operator checkpoints, and keeping resumable state. Also checks an order the operator runs by hand (--manual). Use when the operator wants an order executed, asks to run, resume, or continue the plan, wants to start from a given phase, or wants hand-run steps monitored. Not for producing the plan or the order (orch-plan) or for running a single skill directly.
license: Apache-2.0
compatibility: Automated execution needs a host that can launch subagents and pause mid-run for a person's decision. Without both, use --manual so the operator runs each step and this skill checks the output.
metadata:
  suite: orch
  capability-class: meta-orchestration
  tier: I
---

# Orch Run — OPORD Execution Engine

Read [orch-doctrine.md](references/orch-doctrine.md) (schemas, execution state, run directory, unfinished-run rule, where installed skills live) and [orch-voice.md](references/orch-voice.md) (prompt wording: one decision per prompt, closing block).

Run is the runtime complement to orch-plan. Its state file survives across sessions, so a run can pause for days at a checkpoint and resume where it stopped.

## Input

- **nothing**: resume an unfinished run, or start the latest OPORD
- **a path**: an `opord.md`, or a run directory containing one
- **`--phase N`**: start or resume at phase N
- **`--dry-run`**: parse and display what would run; launch nothing and write no state
- **`--manual`**: the operator runs the skills by hand and this skill monitors; follow [manual-mode.md](references/manual-mode.md) instead of Phases 2 and 3 below

### Resolution

1. Apply the doctrine's unfinished-run rule: collect `execution-state.yaml` files with `status: in-progress`, `escalated`, or `paused`, take the newest, and offer to resume (see Resume). List several if more than one. A paused run is offered, never continued without the operator's choice.
2. Otherwise use the latest effort's `opord.md`.
3. None found: "No OPORD found. Run orch-plan with --order first." and stop.

Also read `situation-assessment.yaml` (Commander's Intent fallback) and `coa-recommended.md` (wargaming notes) from the same directory when present.

## Phase 0: Parse and Validate

Build an execution plan from the OPORD: topic, Commander's Intent, phases (each with steps: skill, arguments, depends-on, parallel-with, output path, hitl, tier, plus transition criteria), the checkpoints with their criteria, and the parsed `n-1-contingencies`, `auto-adapt-rules`, and `escalate-triggers`.

Validate before anything runs:

1. **Every skill is installed.** Check each step's skill, and each substitute in the contingencies, by confirming its `SKILL.md` (or its command file) exists now (doctrine, "Where installed skills live"). Skills may have been installed or removed since planning. A missing primary skill with an installed substitute is a warning; with no substitute, it blocks.
2. No circular dependencies in phase ordering.
3. Every `depends-on` resolves to an earlier phase or a step in the same phase.
4. Every checkpoint has criteria.
5. At least one auto-adapt rule and one escalate trigger exist.

On a validation failure, report the specific issue and stop. Executing a malformed OPORD produces confident garbage.

**Dry run**: show in plain words what would run, in what order, and where it would stop for the operator; then "Nothing was run. Run without --dry-run to execute." Stop.

## Phase 1: Initialize State

Create `execution-state.yaml` in the run directory, following the doctrine's Execution State Schema exactly. If resuming, load it instead.

## Phase 2: Execute Phases

Process phases in order from `current-phase` (or `--phase N`).

### 1. Phase entry

Set the phase `in-progress` with a start time and print a one-line phase header. For every phase after the first, evaluate the previous phase's transition criteria; if one fails, stop and say which: "Phase {N-1} → {N} blocked: {criterion}."

### 2. Group steps

Steps with no `depends-on` that share `parallel-with` references form a parallel group. Steps depending on an earlier step in this phase wait for it. Steps depending only on an earlier phase are ready now.

### 3. Launch

Launch each step as its own subagent, using whatever subagent mechanism the host provides. Give the subagent the instruction to run the named skill with the OPORD's arguments, Commander's Intent and which phase of how many this is, and the output path from the tasking table (write the primary output there, summarize it in the final response). Launch a parallel group together. Mark each skill `running` with a start time.

A subagent is used, not an inline call, so each skill's working context stays out of the run's own; the one-third rule in the doctrine is otherwise unreachable over a multi-phase OPORD.

### 4. Evaluate each result

**a. Failure.** An error, an empty response, or a report that the skill could not complete → mark `failed`.

**b. Auto-adapt rules.** For each rule, check whether its `trigger` text appears in the output summary or the output file (substring match, not judgment). On a match, say so in one line as a fix applied without asking (an auto-adapt rule), execute the response (re-launch with modified arguments, skip and note, or add a compensating step), record `adaptation` on the skill, and increment `auto-adapts-fired`.

**c. Escalate triggers.** If a trigger's condition is observable in the output, run any automatic actions the response specifies, then stop and ask one question:

```
The run has stopped at {step}: {what happened, one sentence}.
It already did: {automatic actions, or "nothing"}.
This hit a condition that stops and asks you instead of guessing (an escalate trigger): {trigger in plain words}.

How do you want to proceed?
1. {option}: {what happens next}
2. {option}: {what happens next}
```

Set the skill `failed`, the phase and run `escalated`, increment `escalates-fired`, and wait.

**d. Backup skill (N-1 contingency).** A failed step that no auto-adapt rule resolved → look up its contingency. If one exists, say which skill failed, the substitute, and the tradeoff, then launch the substitute chain (in its `execution-mode`). If the substitutes also fail, say "{skill} failed, and so did its backup skills. I'm stopping to ask you rather than guess (the second-level fallback, N-2)", and ask one question whatever the HITL level. Record `contingency` and increment `n1-contingencies-fired`.

**e. Success.** Output present, no rule fired → mark `complete` with the completion time and a one-line `output` summary, and print that line.

Write the state file after every change, not at the end of the phase. A crash or a closed session otherwise loses the record of what already ran.

### 5. Checkpoint

When a step with `hitl: true` completes, stop for the operator with exactly one decision, never several stacked. Shape: question first, at most three sentences of context.

```
Checkpoint {N} of {M}: {the decision, as a question}?
{What was just produced, one or two sentences.} The order says to check: {criteria}.

- Approve: continues to {next step}.
- Approve with conditions: you say what to fix first, then it continues.
- Reject: the run pauses here and nothing else runs until you say so.
```

Use the host's structured question tool when it has one.

- **approve**: record and continue
- **approve with conditions**: record the conditions, carry them out (this may re-enter the current phase for a targeted fix), then continue
- **reject**: record, set `status: paused`, and wait for the operator to invoke orch-run again

Record every decision in `hitl-decisions`. When two checkpoints come due in the same phase, ask them one after the other.

### 6. Phase completion

When every step is complete, or adapted or skipped with a recorded reason, mark the phase `complete`, advance `current-phase`, and print a one-line completion with duration.

### 7. Anti-fixation check

At each phase boundary, check whether the plan's frame still holds: have this phase's outputs changed the understanding of the problem, does Commander's Intent still apply, are the remaining phases still the right next steps? If the frame has shifted, stop and ask one question:

```
Phase {N} turned up something that may change the plan: {observation, one sentence}.
The one sentence that has to survive even if the plan changes (Commander's Intent) is: {intent}.
{M} phases remain.

Continue as planned, or pause and re-plan?
```

If the operator chooses to re-plan, set `status: paused` and suggest orch-plan. If the frame holds, continue without printing anything.

## Phase 3: Completion

Write `execution-report.md` to the run directory, with: a header (title, generated time, `orch-run`, the OPORD filename, status); a summary (phases completed, skills executed, duration, and counts of auto-adapts, escalations, contingencies, and checkpoint decisions); a phase log; a step log (phase, skill, status, adaptation, contingency, output); tables of adaptations, escalations, and checkpoint decisions; anti-fixation results; and a quality line.

**Quality**: all steps complete without escalation → high; auto-adapt rules needed but no escalations → medium; escalations or skipped steps → low.

**Run log.** Append one line to `run-log.md` in the durable-state directory (doctrine, "Durable state"): `{YYYY-MM-DD} | {topic-slug} | {complete|aborted|partial} | {reworked: yes|no} | {rough cost}`. Create the file with a `# Run log` heading if it is missing. Keep to this one line.

Set `status: complete` and close with a block of at most 150 words:

```
What happened: {what ran, whether it finished}.
What it means: {the consequence for the work; mention any fix applied on its own (an auto-adapt rule) and anything it stopped to ask about}.
Decisions needed: {items, or "None"}.
Next step: {one action, with a one-clause reason}.
Report: {run directory}/execution-report.md
```

Print the quality tag only with its meaning: it says whether steps finished without stopping to ask the operator, not whether the work is good. Counts of adaptations and escalations go in the report, not the window.

## Resume

On finding a resumable state, ask one question:

```
Found an unfinished run of "{topic}". It stopped in phase {N} ({still running, stopped to ask you, or paused}).
Last thing it did: {from the state file}.
{If escalated: "It stopped because: {trigger in plain words}."}
{If paused: "You paused it at {checkpoint or re-plan request}. Nothing runs until you choose."}

Resume it, amend it, or abort it?
```

- **Resume**: re-read the OPORD for arguments (the state file tracks status, not arguments). For an `in-progress` or `escalated` run, find the first step that is `pending` or `failed` in the first phase that is `in-progress` or `escalated`, and continue from Phase 2 step 3. For a `paused` run, do not search for an unfinished step: a pause can follow a phase marked complete (the anti-fixation check) or a rejected checkpoint with no step left pending. Resume at `current-phase`; if the last `hitl-decisions` entry is a rejection, re-present that checkpoint first and launch nothing until it is answered; if the pause was a re-plan request, ask whether to re-plan or continue.
- **Amend**: take the operator's change to the order or the remaining steps, record it, then resume.
- **Abort**: set `status: aborted`, write the report with partial data, and append the run-log line with outcome `aborted`.

If the OPORD was modified after the state's `started` time, warn that the edits may conflict with in-progress state and ask whether to continue or restart.

## Gotchas

- **All steps in a phase fail**: escalate; never advance with zero completed steps.
- **Rejection at the first checkpoint**: pause; don't re-launch skills speculatively.
- **Subagent timeout or crash**: a failure; check the contingency, else escalate.
- **`--phase N` doesn't exist**: list the available phases and stop.
- **State from a different OPORD in the same directory**: match on the state's `opord` field, not the directory.
- **Single-phase or single-skill OPORD**: full state management still applies; no anti-fixation check without a phase boundary.
- **Hybrid runs**: use `--phase N` for the automated phases, run the rest by hand, then `--manual` over the whole order. It writes the same report and run-log line.
