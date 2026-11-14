# Manual mode

Use when the operator runs the order's skills by hand and wants each output checked instead of launching subagents (`--manual`).

## Phase 0: Parse the OPORD

Extract the tasking table (phases, skills, arguments, dependencies, parallel groups, output paths), `n-1-contingencies`, `auto-adapt-rules`, `escalate-triggers`, Commander's Intent, and the checkpoints. An empty tasking table is an error: suggest re-running orch-plan (order step).

## Phase 1: The Loop, Step by Step

Work through the steps in order, checking each output before moving on.

**Observe.** Read the file at the step's output path. If it doesn't exist, ask one question: "Step {N} ({skill}) — no output at {path} yet. Has it been run?" with options check again, skip, or run it now. If it exists, note its size and modification time; an empty file is a likely failure.

**Orient.** Is the output the expected kind of deliverable, substantive rather than truncated, and coherent with the mission? Note each deviation.

**Decide.**

1. Matches expectations → proceed.
2. Exists but deviates, or missing or empty → check the auto-adapt rules by string or pattern match against the output (not judgment); if none matches, check the escalate triggers.
3. Escalate trigger matched → ask the operator.

**Act.**

- **Proceed** — log the step as verified.
- **Auto-adapt** — carry out the rule's response and log it; don't interrupt the operator for it.
- **Escalate** — one question stating what happened, what the OPORD expected, and which trigger matched (or that none did), with options continue anyway, re-run this step, abort and re-plan, or give guidance.
- **Backup skill (N-1 contingency)** — a step still failing after its auto-adapt retry gets its substitute chain. If the substitute also fails (N-2), escalate whatever the HITL level.

## Phase 2: Anti-Fixation at Phase Boundaries

Between phases, ask whether the original frame is still right: have the outputs so far shifted the problem, does Commander's Intent still apply, are the remaining steps still relevant? If the frame has shifted, ask one question — continue, re-run orch-plan with an updated problem statement, or adjust the remaining steps — stating the original intent and the observation. If it holds, log the pass and continue. A single-phase OPORD has no boundary and skips this.

## Phase 3: Report and Run Log

Write `execution-report.md` to the run directory: a header (title, generated time, `orch-run --manual`, the OPORD path); outcome (complete, partial, or aborted; steps completed of total); a step log (step, skill, status, adaptation, notes); adaptations, escalations with the operator's decisions, and anti-fixation results; and an overall quality (every step complete without escalation → high; auto-adapt rules needed → medium; escalations or skipped steps → low). Append the run-log line described in the doctrine ("Durable state"), then close with the closing block from the voice file.

## Gotchas

- **Everything already ran.** If every output path has a recent file, say so and run Orient only — verification mode.
- **Partial run.** Resume at the first step with no output.
- **An automated run already reported.** If `execution-report.md` exists from an earlier automated run of this order, update that report and do not append a second run-log line for the same run.
