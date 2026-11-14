# Order format

If no `coa-recommended.md` exists in the run directory, the plan has not been written: write it first (for a one- or two-skill chain, the minimal version described in the early exit), then continue. Never loop back to the early exit from here. Produce this only when the plan is headed for `orch-run`: the operator asked for the executable order (`--order`) or approves a run. A plan that is only read by a person ends at the recommended plan.

## Phase 1: Parse

From the COA: Commander's Intent, the one-liner, per-skill details (names, arguments, dependencies, parallel groups), risk assessment, wargaming notes. From the assessment: the enemy, terrain, troops, time, and civil blocks.

An empty or malformed COA is reported with the specific problem. Don't produce a malformed OPORD — orch-run will execute whatever it is given.

## Phase 2: The Five Paragraphs

Follow the doctrine's template.

**1. SITUATION** — problem context; enemy assessment with overall risk and the top 2–3 threats; terrain summary (tools, connectors, key terrain); troops available (mission-relevant skills with class and tier).

**2. MISSION** — task, purpose, end state.

**3. EXECUTION** — the core paragraph.

- **One-liner** in the doctrine's format.
- **Tasking table** with columns: Phase, Skill, Arguments, Depends On, Parallel With, Output Path, HITL. Every step gets an output path, set by the doctrine's step-output rule (a bare filename goes into the run directory). orch-run and manual mode find outputs only through this column.
- **HITL column** — set from the assessment's `hitl-level` using the doctrine's checkpoint levels.
- **Phase transition criteria** — for each phase, the testable conditions that must hold before the next starts.
- **N-1 contingencies** — a block for every tier I and II skill, using the doctrine's `n-1-contingencies` key names exactly. Take tiers from the assessment's troops block, or from the roster in the same directory.
- **Adaptation rules** — `auto-adapt-rules` and `escalate-triggers`, in the doctrine's key names. Write them for the skills in this OPORD, not generic ones: each trigger names a concrete, observable condition in that skill's output (a phrase, an empty section, a missing file), because orch-run matches triggers as strings. Include at least one of each.

**4. SUSTAINMENT** — reference files the skills need; the run directory; artifact handoff (which output feeds which step); cost budget (model calls by weight, subagent launches, web calls, estimated tokens).

**5. COMMAND AND SIGNAL** — the full Commander's Intent in the doctrine's format; the checkpoints (from the tasking table's HITL column), each with the criteria the operator decides on; reporting (orch-run or manual mode writes `execution-report.md` to the run directory); the escalation path: auto-adapt fires silently → escalate triggers pause and ask → a failed backup skill (N-2) always asks, whatever the HITL level.

## Phase 3: Output

Write `opord.md` into the same run directory as the COA. When the COA came from a path outside `./.orch/`, create a new run directory for the OPORD and note where the COA came from.

Close with a block of at most 150 words:

```
What happened: the executable order (the OPORD) is written: {skill-A ∥ skill-B} → {skill-C} | N skills, N phases, ~Nk tokens.
What it means: {the one sentence that has to survive even if the plan changes (Commander's Intent), in plain words}; {N} points where the run stops for the operator's decision (HITL checkpoints).
Decisions needed: None until the run starts.
Next step: run orch-run, to start it. Order: {run directory}/opord.md
```

## Gotchas

- **COA from immediate urgency.** It has no tiers or contingencies. Infer tiers from the doctrine's heuristics and warn: "The plan was made on the fast path — the backup skills (N-1 contingencies) are a best guess."
- **Single-skill plan.** Still write all five paragraphs; some are short. A tier I or II skill still gets a contingency.
- **Semantic triggers.** "If the output is poor" can't be string-matched and will never fire. Rewrite it as something observable, or make it an escalate trigger the operator judges at a checkpoint.
