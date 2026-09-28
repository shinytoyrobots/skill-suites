---
name: ops-assess
description: Monitors a multi-skill plan the operator is running by hand against its operations order (OPORD) — checking each step's output, applying the order's adaptation rules, asking whether the plan's frame still holds at phase boundaries, and writing the execution report. Use when the operator is running an OPORD's skills themselves and wants each step checked, asks to assess or monitor execution, or wants a partly-run plan evaluated. Not for code review, QA, or general assessments, and not for automated execution (ops-run).
license: Apache-2.0
metadata:
  suite: ops
  capability-class: meta-orchestration
  tier: II
---

# Ops Assess — OODA Execution Loop

Read [ops-doctrine.md](references/ops-doctrine.md) (schemas, run directory, durable state) and [ops-voice.md](references/ops-voice.md).

Assess runs the observe–orient–decide–act loop per step of an OPORD that someone else is executing, so a hand-run plan still gets its contingencies, its anti-fixation checks, and its place in the learning loop.

## Input

- **nothing** — the latest effort directory's `opord.md` (see the doctrine)
- **a path** — an `opord.md`, or a run directory containing one

No OPORD found: "No OPORD found. Run ops-order first." and stop. Read `execution-state.yaml` from the same directory when present — ops-run may have executed some phases already.

## Phase 0: Parse the OPORD

Extract the tasking table (phases, skills, arguments, dependencies, parallel groups, output paths), `n-1-contingencies`, `auto-adapt-rules`, `escalate-triggers`, Commander's Intent, and the checkpoints. An empty tasking table is an error: suggest re-running ops-order.

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

Between phases, ask whether the original frame is still right: have the outputs so far shifted the problem, does Commander's Intent still apply, are the remaining steps still relevant? If the frame has shifted, ask one question — continue, re-run ops-plan with an updated problem statement, or adjust the remaining steps — stating the original intent and the observation. If it holds, log the pass and continue. A single-phase OPORD has no boundary and skips this.

## Phase 3: Report and Pattern Capture

Write `execution-report.md` to the run directory with: a header (title, generated time, `ops-assess`, the OPORD path); outcome (complete, partial, or aborted; steps completed of total); a step log (step, skill, status, adaptation, notes); adaptations, escalations with the operator's decisions, and anti-fixation results; and an overall quality with a one-line rationale.

**Quality** — every step complete without escalation → high; auto-adapt rules needed → medium; escalations or skipped steps → low.

**Pattern capture**, on a complete run only. Append one entry to `pattern-queue.yaml` in the durable-state directory (`$OPS_STATE`, else `~/.ops-skills/`) using the doctrine's Pattern Queue Entry key names: date, problem class from the mission's task type, the capability chain in order with tiers, sequence type, and output quality. If the file is missing, copy [the empty template](assets/pattern-queue.yaml) into place first.

Return, in the operator register:

```
## Assessment: {topic}
{Complete/Partial/Aborted} — {N}/{total} steps
{count} fixes applied without asking (auto-adapt), {count} stops for your decision (escalations)
Quality {level} — {whether it was queued as a candidate opening-book pattern, and why}
Report: {run directory}/execution-report.md
```

## Gotchas

- **Everything already ran.** If every output path has a recent file, say so and run Orient only — verification mode.
- **Partial run.** Resume at the first step with no output.
- **ops-run already reported.** If `execution-report.md` exists from ops-run, don't append a second pattern-queue entry for the same run; update the report instead.

## Next

> Assessment {status}. Next: ops-learn to promote recurring patterns into the opening book, or re-run ops-assess to pick up where a partial run stopped.
