---
name: orch-plan
description: Works out which installed skills to run, in what order, for a problem that needs more than one skill, with backups and risks stated, and writes the executable order (an OPORD) when the plan will be run. Use when the operator asks which skills to use for a goal, wants a multi-step effort planned or its options compared before running anything, wants an inventory of installed skills, or asks for the executable order. Not for single-skill requests, general project planning or roadmaps, or questions about military doctrine itself.
license: Apache-2.0
metadata:
  suite: orch
  capability-class: meta-orchestration
  tier: I
---

# Orch Plan — METT-TC Mission Analysis + COA Development

Read [orch-doctrine.md](references/orch-doctrine.md) (METT-TC, wargaming, schemas, run directory, where installed skills live) and [orch-voice.md](references/orch-voice.md) (how to word anything printed to the operator).

Plan turns a problem statement into a structured situation check (METT-TC) and one or more candidate plans (COAs), recommends one, and, when the plan will be run, writes the executable order. It also builds the roster of installed skills it plans from.

## Input

A problem statement, optionally with `urgency: immediate | routine | deliberate`. When urgency is absent, infer it: "now", "quick", "urgent", "ASAP" → immediate; "strategic", "evaluate options", "high-stakes", "important decision" → deliberate; otherwise routine.

Flags: `--roster` builds and prints the skill roster only, then stops. `--order` also writes the executable order after the plan.

## Phase 1: Run Directory and Force Roster

Resolve the run directory: if the latest effort has a `force-roster.yaml` and no `situation-assessment.yaml`, claim it by renaming it to `./.orch/{YYYY-MM-DD}-{topic-slug}/`; otherwise create that directory.

Reuse a roster only under the doctrine's freshness rule (under 30 minutes old and a matching fingerprint). Otherwise build a fresh one by following [roster-discovery.md](references/roster-discovery.md), which also covers `--roster`. If discovery fails, do not guess: for `deliberate` urgency stop and report the error; for `immediate` or `routine` continue, but stamp every output `UNVERIFIED: roster unavailable` and check each skill you name individually against the installed roots.

Exclude the `meta-orchestration` class from Troops so a plan never schedules an `orch-` skill.

**Check every recommendation against the install, not the roster.** Before a skill appears in any plan, confirm its `SKILL.md` exists now (doctrine, "Where installed skills live"). A skill that fails is removed from the plan and reported as an error ("{name} is not installed"), never carried as a warning.

### Early exit

Before the full analysis, check whether the problem needs more than two skills or any ordering decision. If one or two installed skills clearly cover it, say which, in what order, and why nothing more is needed, then stop. Do not run METT-TC, COAs, or wargaming for a problem that does not need them. If `--order` was given, still write the executable order for that short chain (a one- or two-skill order is valid) before stopping.

## Phase 2: METT-TC Analysis

Run all six variables per the doctrine. Each produces a block in `situation-assessment.yaml`.

**Mission** — `problem-statement` (raw input), `task`, `purpose`, `end-state`, `commander-intent` (the doctrine's format, with 2–3 key tasks), `constraints`, `success-criteria`, and `task-type` (production, evaluation, planning, intelligence, or remediation).

**Enemy** — `blocking-constraints`, `quality-risks`, `capacity-risks`, `failure-modes`, `overall-risk` (low, medium, high, critical). For each candidate skill, check whether the tools and connectors it names are available in this session, whether files it links under its own directory exist, and whether it depends on another skill's output.

**Terrain** — `tools-available`, `output-paths-writable`, `key-terrain` (the single resource whose absence blocks the most), `viable-chains`, `blocked-chains`.

**Troops** — `mission-relevant-skills`, each with `skill`, `capability-class`, `tier`, `readiness`, `fit` (high, medium, low), and `rationale`; a `force-recommendation` with `primary-skills`, `supporting-skills`, and `execution-pattern` (sequential, parallel, staged); and `substitution-options`, each with `blocked`, `substitute`, `tradeoff`. Unclassified roster skills can still be chosen when their description plainly fits; say so in the rationale.

**Time** — `urgency`, `parallel-opportunities` (groups with why they are independent), `sequential-requirements` (first, then, reason), and `context-budget` for orchestration and execution. Orchestration stays under one-third of the budget.

**Civil** — `hitl-level` (the doctrine's checkpoint levels; 2 unless the operator states a preference), `output-routing` (the run directory, plus any skill's own output convention), and `escalation-triggers`.

## Phase 3: COA Development

**Routine — one COA.** Select the primary skills, order them by the sequential requirements, group the parallel ones, give every tier I or II skill an N-1 contingency from the substitution options, wargame the plan's gates and pre-mortem, write auto-adapt rules for predictable failures (empty result → retry with different parameters; timeout → skip an optional step), and write escalate triggers for frame-breaking deviations (problem reframed, cascade failure, key deliverable below bar).

**Deliberate — two or three COAs**, each with a different strategy: A breadth-first (maximum coverage, higher cost), B depth-first (strongest evidence path, lower cost), and optionally C minimal viable (fewest skills that still reach the end state). Wargame each through all four doctrine phases. Compare them on coverage, risk, cost in tokens, number of skills, and the key tradeoff, then recommend one with the reason. Show the operator the comparison and the recommendation before writing, as a single decision.

**Immediate — fast path.** Skip the full situation check. Match the problem to 1–3 roster skills and emit skill names, order, and expected output. No wargaming, contingencies, or adaptation rules.

**Single-skill problems** skip COA development and get a direct recommendation.

## Phase 4: Output

### Show first

Before writing any file, print a one-screen summary in plain language: the chain (the one-liner), rough cost, the top two risks (each named as what could go wrong, not as a category), and a go or no-go recommendation with one sentence of reason.

### Write

Write two files into the run directory:

1. `situation-assessment.yaml` — all six METT-TC blocks.
2. `coa-recommended.md` — the recommended COA in OPORD-lite form, with these sections: a header (title "Tactical Assessment: {topic}", generated timestamp, urgency), **Commander's Intent**, **Recommended Plan** (the one-liner), **Execution Sequence** (table: phase, skills, arguments, mode, depends on), **N-1 Contingencies** (table: skill, trigger, substitute, tradeoff), **Adaptation Rules** (auto-adapt and escalate), **Risk Assessment**, and **Wargaming Notes** (all four phases for deliberate; gates and pre-mortem only for routine; omitted for immediate).

### The executable order (only with `--order`, or when the operator approves a run)

Follow [order-format.md](references/order-format.md) to write `opord.md` into the same run directory. Without `--order`, stop at the plan and offer the order in one line.

### Close

End with a closing block of at most 150 words, per the voice file:

```
What happened: {one or two plain sentences: the problem, and the plan chosen}.
What it means: {what the chain gets the operator, the top risk, what it leaves out}.
Decisions needed: {items, or "None"}.
Next step: {one action, e.g. run orch-plan again with --order, with a one-clause reason}.
Plan: {skill-A ∥ skill-B} → {skill-C} | N skills, N phases, ~Nk tokens. Written to {run directory}.
```

Say the risk level in words ("low risk: nothing blocks this"), not as a bare label.

## Gotchas

- **Nothing in the roster fits.** Report which kinds of work (capability classes) the problem needs so the operator knows what to install.
- **A stale roster plans around skills that are gone.** That is why the roster has a fingerprint and every named skill is checked at recommendation time.
- **The operator wants it run.** Do not launch skills from here. Write the order and hand off to `orch-run`.
