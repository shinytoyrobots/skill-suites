---
name: ops-order
description: Turns the recommended plan from ops-plan into a full five-paragraph operations order (OPORD) that ops-run can execute, with per-skill tasking, backup skills, and pre-committed adaptation rules. Use when the operator has a plan from ops-plan and wants it made executable, asks for an OPORD, or wants tasking and contingencies written before running a multi-skill effort. Not for general task lists, project plans, or tickets.
license: Apache-2.0
metadata:
  suite: ops
  capability-class: meta-orchestration
  tier: I
---

# Ops Order — OPORD Production

Read [ops-doctrine.md](references/ops-doctrine.md) (OPORD template, Commander's Intent, schema key names, run directory) and [ops-voice.md](references/ops-voice.md).

The OPORD is the executable plan: ops-run drives it and ops-assess monitors against it. Everything a runner needs has to be in it, because the runner may start in a fresh session with nothing else.

## Input

- **nothing** — use the latest effort directory (see the doctrine) and its `coa-recommended.md`
- **a path** — a `coa-recommended.md` file, or a run directory containing one

If no COA is found: "No recommended plan found. Run ops-plan first." and stop.

From the same directory, read `situation-assessment.yaml` if present. If it is missing, derive the Situation paragraph from the COA alone and note: "Situation paragraph derived from the recommended plan only — no situation check (METT-TC) available."

## Phase 1: Parse

From the COA: Commander's Intent, the one-liner, per-skill details (names, arguments, dependencies, parallel groups), risk assessment, wargaming notes. From the assessment: the enemy, terrain, troops, time, and civil blocks.

An empty or malformed COA is reported with the specific problem. Don't produce a malformed OPORD — ops-run will execute whatever it is given.

## Phase 2: The Five Paragraphs

Follow the doctrine's template.

**1. SITUATION** — problem context; enemy assessment with overall risk and the top 2–3 threats; terrain summary (tools, connectors, key terrain); troops available (mission-relevant skills with class and tier).

**2. MISSION** — task, purpose, end state.

**3. EXECUTION** — the core paragraph.

- **One-liner** in the doctrine's format.
- **Tasking table** with columns: Phase, Skill, Arguments, Depends On, Parallel With, Output Path, HITL. Every step gets an output path, set by the doctrine's step-output rule (a bare filename goes into the run directory). ops-run and ops-assess find outputs only through this column.
- **HITL column** — set from the assessment's `hitl-level` using the doctrine's checkpoint levels.
- **Phase transition criteria** — for each phase, the testable conditions that must hold before the next starts.
- **N-1 contingencies** — a block for every tier I and II skill, using the doctrine's `n-1-contingencies` key names exactly. Take tiers from the assessment's troops block, or from the roster in the same directory.
- **Adaptation rules** — `auto-adapt-rules` and `escalate-triggers`, in the doctrine's key names. Write them for the skills in this OPORD, not generic ones: each trigger names a concrete, observable condition in that skill's output (a phrase, an empty section, a missing file), because ops-run matches triggers as strings. Include at least one of each.

**4. SUSTAINMENT** — reference files the skills need; the run directory; artifact handoff (which output feeds which step); cost budget (model calls by weight, subagent launches, web calls, estimated tokens).

**5. COMMAND AND SIGNAL** — the full Commander's Intent in the doctrine's format; the checkpoints (from the tasking table's HITL column), each with the criteria the operator decides on; reporting (ops-run or ops-assess writes `execution-report.md` to the run directory); the escalation path: auto-adapt fires silently → escalate triggers pause and ask → a failed backup skill (N-2) always asks, whatever the HITL level.

## Phase 3: Output

Write `opord.md` into the same run directory as the COA. When the COA came from a path outside `./.ops/`, create a new run directory for the OPORD and note where the COA came from.

Return, in the operator register:

```
## OPORD ready: {topic}
Plan: {skill-A ∥ skill-B} → {skill-C} | N skills, N phases, ~Nk tokens
The one sentence that has to survive if the plan changes (Commander's Intent): Deliver {task} in order to {purpose}…
{N} points where the run stops for your decision (HITL checkpoints)
Written to {run directory}/opord.md
```

## Gotchas

- **COA from immediate urgency.** It has no tiers or contingencies. Infer tiers from the doctrine's heuristics and warn: "The plan was made on the fast path — the backup skills (N-1 contingencies) are a best guess."
- **Single-skill plan.** Still write all five paragraphs; some are short. A tier I or II skill still gets a contingency.
- **Semantic triggers.** "If the output is poor" can't be string-matched and will never fire. Rewrite it as something observable, or make it an escalate trigger the operator judges at a checkpoint.

## Next

> OPORD written to {path}. Next: ops-run to execute it with checkpoints, or run the tasking table by hand and use ops-assess to monitor.
