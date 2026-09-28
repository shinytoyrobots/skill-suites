---
name: ops-plan
description: Works out which installed skills to run, in what order, for a problem that needs more than one skill, and writes a tactical assessment with a recommended plan. Use when the operator asks which skills to use for a goal, wants a multi-step effort planned or its options compared before running anything, or says "plan this" about work their skill library could do. Not for general project planning, roadmaps, or questions about military doctrine itself.
license: Apache-2.0
metadata:
  suite: ops
  capability-class: meta-orchestration
  tier: I
---

# Ops Plan — METT-TC Mission Analysis + COA Development

Read [ops-doctrine.md](references/ops-doctrine.md) (METT-TC, wargaming, schemas, run directory, durable state) and [ops-voice.md](references/ops-voice.md) (how to word anything printed to the operator).

Plan is the analytical center of the suite: it turns a problem statement into a situation check (METT-TC) and one or more candidate plans (COAs), and recommends one.

## Input

A problem statement, optionally with `urgency: immediate | routine | deliberate`. When urgency is absent, infer it: "now", "quick", "urgent", "ASAP" → immediate; "strategic", "evaluate options", "high-stakes", "important decision" → deliberate; otherwise routine.

## Phase 0: Opening Book Check

The opening book lives in the durable-state directory (`$OPS_STATE`, else `~/.ops-skills/`). If `opening-book.yaml` is missing, treat it as empty and go to Phase 1 — this skill only reads the book, so it does not create one.

1. Compare the problem statement against each pattern's `triggers`.
2. Score: a trigger phrase present in the problem → the pattern's stored `confidence`; the problem plainly describes the same workflow → stored confidence + 0.1; no match → 0.
3. **> 0.85** — offer the match: which pattern, its capability chain in plain words, and what reuse skips ("reuse the earlier plan and skip the full situation check, or analyze from scratch?"). If the operator reuses it, still run Phase 1 (the run directory and roster), then go to Phase 3 with that chain.
4. **0.5–0.85** — keep the pattern as scaffolding for COA development; continue.
5. **< 0.5** — no match; continue.

Also check `failure-patterns`. A chain resembling a known failure is named in the risk assessment.

## Phase 1: Run Directory and Force Roster

Resolve the run directory:

- If the latest effort directory has a `force-roster.yaml` and no `situation-assessment.yaml`, it is an unclaimed recon: claim it by renaming it to `./.ops/{YYYY-MM-DD}-{topic-slug}/`.
- Otherwise create `./.ops/{YYYY-MM-DD}-{topic-slug}/`. If the latest effort has a roster less than 30 minutes old, copy it in; otherwise run ops-recon with `--out` set to this directory.

A roster older than 30 minutes is refreshed because skills get installed and removed between efforts, and a stale roster plans around skills that are gone.

Read the roster. Exclude the `meta-orchestration` class from Troops so the plan never schedules an `ops-` skill.

## Phase 2: METT-TC Analysis

Run all six variables per the doctrine. Each produces a block in `situation-assessment.yaml`.

**Mission** — `problem-statement` (raw input), `task`, `purpose`, `end-state`, `commander-intent` (the doctrine's format, with 2–3 key tasks), `constraints`, `success-criteria`, and `task-type` (production, evaluation, planning, intelligence, or remediation).

**Enemy** — `blocking-constraints`, `quality-risks`, `capacity-risks`, `failure-modes`, `overall-risk` (low, medium, high, critical). For each candidate skill, check whether the tools and connectors it names are available in this session, whether files it links under its own directory exist, and whether it depends on another skill's output.

**Terrain** — `tools-available`, `output-paths-writable`, `key-terrain` (the single resource whose absence blocks the most), `viable-chains`, `blocked-chains`.

**Troops** — `mission-relevant-skills`, each with `skill`, `capability-class`, `tier`, `readiness`, `fit` (high, medium, low), and `rationale`; a `force-recommendation` with `primary-skills`, `supporting-skills`, and `execution-pattern` (sequential, parallel, staged); and `substitution-options`, each with `blocked`, `substitute`, `tradeoff`. Unclassified roster skills can still be chosen when their description plainly fits — say so in the rationale.

**Time** — `urgency`, `parallel-opportunities` (groups with why they are independent), `sequential-requirements` (first, then, reason), and `context-budget` for orchestration and execution. Orchestration stays under one-third of the budget.

**Civil** — `hitl-level` (the doctrine's checkpoint levels; 2 unless the operator states a preference), `output-routing` (the run directory, plus any skill's own output convention), and `escalation-triggers`.

## Phase 3: COA Development

**Routine — one COA.** Select the primary skills, order them by the sequential requirements, group the parallel ones, give every tier I or II skill an N-1 contingency from the substitution options, wargame the plan's gates and pre-mortem, write auto-adapt rules for predictable failures (empty result → retry with different parameters; timeout → skip an optional step), and write escalate triggers for frame-breaking deviations (problem reframed, cascade failure, key deliverable below bar).

**Deliberate — two or three COAs**, each with a different strategy: A breadth-first (maximum coverage, higher cost), B depth-first (strongest evidence path, lower cost), and optionally C minimal viable (fewest skills that still reach the end state). Wargame each through all four doctrine phases. Compare them on coverage, risk, cost in tokens, number of skills, and the key tradeoff, then recommend one with the reason. Show the operator the comparison and the recommendation before writing, as a single decision.

**Immediate — fast path.** Skip the full situation check. Use the opening-book chain if one matched at any confidence; otherwise match the problem to 1–3 roster skills. Emit skill names, order, and expected output — no wargaming, contingencies, or adaptation rules.

**Single-skill problems** skip COA development and get a direct recommendation.

## Phase 4: Output

Write two files into the run directory:

1. `situation-assessment.yaml` — all six METT-TC blocks.
2. `coa-recommended.md` — the recommended COA in OPORD-lite form, with these sections: a header (title "Tactical Assessment: {topic}", generated timestamp, urgency), **Commander's Intent**, **Recommended Plan** (the one-liner), **Execution Sequence** (table: phase, skills, arguments, mode, depends on), **N-1 Contingencies** (table: skill, trigger, substitute, tradeoff), **Adaptation Rules** (auto-adapt and escalate), **Risk Assessment**, and **Wargaming Notes** (all four phases for deliberate; gates and pre-mortem only for routine; omitted for immediate).

Return to the operator, in the operator register:

```
## Ops plan: {topic}
{Urgency in plain words} | Risk: {level and the one failure mode behind it}
Plan: {skill-A ∥ skill-B} → {skill-C} | N skills, N phases, ~Nk tokens
Written to {run directory}
```

## Gotchas

- **Roster missing and recon fails.** Plan in degraded mode from the problem statement alone, inferring classes from what the operator names, and say so: "No force roster — which skills can actually run is approximate."
- **Nothing in the roster fits.** Report which kinds of work (capability classes) the problem needs so the operator knows what to install.
- **Trigger phrases overmatch.** A short trigger ("review") can appear in unrelated problems. Treat a match that the problem's task type contradicts as no match.

## Next

> Assessment written to {run directory}. Next: ops-order to turn it into a full written plan with per-skill tasking (an OPORD), or run the skills by hand in the order shown.
