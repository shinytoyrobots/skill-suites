# Orch Doctrine — Military Planning Frameworks for Skill Orchestration

The reference every `orch-` skill loads. It defines the frameworks (METT-TC, capability classes, tiers, wargaming, the OPORD), where run artifacts and durable state live, and the exact key names the skills use to hand data to each other.

---

## METT-TC Analysis Framework

Six variables for structured situation assessment. Each maps a military concept to skill orchestration.

| Variable | Military | Skill Orchestration | Key Output |
|----------|----------|-------------------|------------|
| **Mission** | Task + Purpose + End State | Problem → deliverable + goal + success criteria + Commander's Intent | `mission:` block |
| **Enemy** | Opposing forces + capabilities | Constraints, unknowns, failure modes, rate limits, missing data | `enemy:` block |
| **Terrain** | Physical environment (OCOKA) | Tools and connectors, writable paths, repo context, API access, key terrain | `terrain:` block |
| **Troops** | Available forces + readiness | Installed skills by capability class + tier + readiness | `troops:` block |
| **Time** | Timeline + 1/3-2/3 rule | Urgency, context budget (never >1/3 on orchestration), parallel/sequential | `time:` block |
| **Civil** | Stakeholder concerns (ASCOPE) | Checkpoint level, audience, output routing, escalation triggers | `civil:` block |

### Mission Decomposition

```yaml
mission:
  task: "The explicit deliverable"
  purpose: "Why this matters (the underlying goal)"
  end-state: "What success looks like when done"
  commander-intent: "See Commander's Intent format below"
  constraints: ["Must not...", "Cannot..."]
  success-criteria: ["Specific, testable conditions"]
```

**Task type signals**: generate/create/write → production | review/audit/assess → evaluation | plan/design/architect → planning | research/find/explore → intelligence | fix/repair/debug → remediation

### Enemy Classes

| Class | Examples | Risk Level |
|-------|----------|-----------|
| Constraint | Tool unavailable, permission boundary, missing file | blocking |
| Uncertainty | Empty reference file, stale data, ambiguous scope | quality-degrading |
| Resource | Context window exhaustion, model cost, rate limits | capacity |
| Failure Mode | Dependency cascade, output path collision, checkpoint stall | cascade |

### Terrain Assessment

Identify **key terrain** — the single resource whose absence blocks the most. Check: tools and connectors available vs required, output paths writable, repo context (git state), API access (web, connector tools).

### Civil — Checkpoint (HITL) Levels

`hitl-level` sets how often a run stops for the operator. The order step of orch-plan turns it into the per-step `hitl` flags in the tasking table; orch-run acts only on those flags.

| Level | Stops at |
|-------|----------|
| **0** | Nothing planned — only escalate triggers and N-2 fallbacks |
| **1** | Before any terminal deliverable leaves the run directory (published, sent, merged) |
| **2** (default) | Level 1, plus after every tier I or II step |
| **3** | After every step |

Escalate triggers and N-2 fallbacks stop the run at every level.

### Time — Urgency Modes

| Mode | Planning Budget | What Runs |
|------|----------------|-----------|
| **Immediate** | <5% context | Opening book → minimal plan → execute |
| **Routine** | ~15% context | Full METT-TC → 1 COA → wargaming gates + pre-mortem → execute |
| **Deliberate** | ~25% context | Full METT-TC → 2-3 COAs → wargaming → operator review → execute |

**One-third rule**: Never spend more than one-third of available context on orchestration. Orchestration that eats the budget leaves too little for the skills doing the actual work.

---

## Capability-Class Taxonomy (14 Classes)

| Class | Kind of work |
|-------|-------------|
| `intelligence-gathering` | Scanning, researching, monitoring, detecting signals |
| `synthesis-analysis` | Turning gathered material into a structured assessment |
| `content-production` | Writing, drafting, generating content |
| `content-review` | Reviewing, auditing, critiquing, scoring someone's output |
| `planning-design` | Plans, roadmaps, specs, architectures |
| `execution-orchestration` | Multi-step workflows and agent coordination |
| `release-operations` | Shipping, deploying, announcing, post-release monitoring |
| `retrospective-learning` | Retros, debriefs, lessons learned |
| `personal-tracking` | Logging and tracking an individual's own records |
| `market-intelligence` | Competitive intelligence and positioning |
| `financial-legal` | Tax, finance, compliance, contracts |
| `ideation-invention` | Generating novel ideas, exploring concepts |
| `publication-submission` | Manuscripts, pitches, queries, submissions to outlets |
| `meta-orchestration` | Assessing, planning, and dispatching other skills |

## Tier Levels (I–V)

| Tier | Scale | Characteristics |
|------|-------|----------------|
| **I** | Full ops | Multi-phase, launches 2+ subagents, strongest model, large context, multiple artifacts |
| **II** | Substantial | Structured workflow, 0-1 subagents, strong model, medium context |
| **III** | Standard | Single-phase, no subagents, one structured output |
| **IV** | Lightweight | Fast, minimal tooling, read-heavy, feeds higher-tier skills |
| **V** | Atomic | Single-purpose check/log/status, frequent invocation |

---

## Wargaming Methodology (4 Phases)

### Phase 1 — Pre-Execution Gates
- Is the plan fully specified? (No ambiguous steps)
- Is all required context present? (No missing inputs)
- Circular dependencies or race conditions?
- Computational cost tractable within constraints?

### Phase 2 — Action-Reaction-Counteraction
**Method**: Belt (default — step through each plan step sequentially).
For EACH step: ACTION (what the skill does) → REACTION (at least 1 per Enemy class: constraint/uncertainty/resource/failure-mode) → COUNTERACTION (failsafe, retry, escalation, or abort).
A reaction with no counteraction is a **required decision point** — flag it in the wargaming notes.
All steps are evaluated unless explicitly excluded with documented rationale.

### Phase 3 — Quiescence Check (plan-time)
After the planned final step, list all output artifacts. An artifact with no downstream consumer in the plan is **unresolved** (a "volatile" end state). A plan where every artifact has a named consumer or is explicitly marked as a terminal deliverable is **quiet**.
If volatile: flag each unresolved artifact with a recommended disposition (add a finalization step, mark terminal, or escalate).
This is plan-time analysis only. Runtime quiescence (pending calls, partial writes) is orch-run's responsibility.

### Phase 4 — Pre-Mortem
Assume the plan failed. Generate 3 failure narratives. Verify each has a counteraction or decision point.

---

## OPORD Template (5 Paragraphs)

```
1. SITUATION    — Problem context, enemy assessment, terrain summary, troops available
2. MISSION      — Task + purpose + end state (derived from METT-TC Mission)
3. EXECUTION    — Skill sequence with per-skill tasking, dependencies, parallel groups
                  N-1 contingency chains for tier I/II skills
                  Auto-adapt rules (simple failures) + escalate triggers (frame-breaking)
4. SUSTAINMENT  — Reference files, run directory, artifact handoff paths, cost budget
5. COMMAND+SIGNAL — Commander's Intent, operator checkpoints, reporting format, escalation path
```

**One-liner format** (human review): `{skill-A ∥ skill-B} → {skill-C} → {skill-D} | N skills, N phases, ~Nk tokens`

---

## Commander's Intent Format

> Deliver **[task]** in order to **[purpose]**. Success looks like **[end state]**. Key tasks that must be accomplished regardless of plan changes: **[key tasks]**. If the plan diverges, prioritize **[purpose]** over **[specific method]**.

---

## Run Artifacts and Durable State

### The run directory

Every effort gets one directory in the project the operator is working in:

```
./.orch/{YYYY-MM-DD}-{topic-slug}/
  force-roster.yaml          # orch-plan — installed-skill roster
  situation-assessment.yaml  # orch-plan — METT-TC output
  coa-recommended.md         # orch-plan — the recommended COA
  opord.md                   # orch-plan --order — the full OPORD
  execution-state.yaml       # orch-run — resumable execution state
  execution-report.md        # orch-run — execution log
```

Keeping one effort's files together is what lets each skill find its input without being told a path, and lets an operator hand the whole effort to someone else as one folder.

**Latest effort** is the run directory whose newest file is most recent: `find ./.orch -mindepth 2 -maxdepth 2 -type f -exec ls -t {} + 2>/dev/null | head -1`, then take its directory. No output means there is no effort yet. (`find` rather than a `./.orch/*/*` glob, because zsh aborts on an unmatched glob in a fresh project.) Rank by the newest file, not by the directory's own timestamp. A path argument always overrides the latest-effort rule.

**Unfinished runs come before the latest effort.** To resume, collect every `execution-state.yaml` under `./.orch/` whose `status` is `in-progress`, `escalated`, or `paused`, then take the newest of those. A newer completed effort never hides an older unfinished one. If several are unfinished, list them and ask which. A `paused` run is offered, never continued automatically: show where it stopped and why, then wait for the operator to resume, amend, or abort.

Step outputs written by the orchestrated skills go wherever the OPORD's tasking table says. A skill's own output filename with no directory ("write scan.md") goes into the run directory under that name; a skill with no file convention gets `step-{phase}-{skill}.md` there. Only a skill whose convention names a full path outside the project keeps it.

### Where installed skills live

| Scope | Roots |
|---|---|
| project | `./.agents/skills`, `./.claude/skills`, `./.grok/skills`, `./.codex/skills` |
| user | `~/.agents/skills`, `~/.claude/skills`, `~/.grok/skills`, `~/.codex/skills` |
| command files | `~/.claude/commands/*.md` (top level only) |

Scan with symlinks followed (`find -L`), because installers commonly symlink skill directories into place. A skill is installed when `{root}/{name}/SKILL.md` exists in any root. **A roster is a planning aid, not proof a skill exists:** before any plan or run names a skill, check that its `SKILL.md` is present now, and treat a missing one as an error, not a warning.

**Roster fingerprint.** `{count}:{epoch}` over the roots that exist: the number of files, and the newest modification time among them. Compute the count with `find -L {roots} -type f | wc -l` and the epoch with `find -L {roots} -type f -exec sh -c 'stat -c %Y "$1" 2>/dev/null || stat -f %m "$1"' _ {} \; | sort -n | tail -1` (GNU `stat` first, then BSD, so it works on Linux and macOS). A roster is reused only when it is under 30 minutes old and its stored fingerprint matches a fresh one.

### Durable state

One file lives outside any project, so the operator can judge the suite across efforts:

```
~/.orch-skills/run-log.md
```

`orch-run` appends one line per finished run: `{YYYY-MM-DD} | {topic-slug} | {complete|aborted|partial} | {reworked: yes|no} | {rough cost}`. When the `ORCH_STATE` environment variable is set, it replaces `~/.orch-skills/` as the directory. If the file is missing, create it with a `# Run log` heading first. Nothing else reads it; it is a record for the operator.

---

## Schema Reference

Exact key names for inter-skill data contracts. Every skill that produces or consumes these structures uses these names, because the consumer matches on them literally.

### N-1 Contingency Chain (produced by the order step of orch-plan, read by orch-run)
```yaml
n-1-contingencies:
  - skill: "skill-name"
    trigger: "skill unavailable OR output empty after 2 retries"
    substitute-chain: ["alt-skill-1", "alt-skill-2"]
    execution-mode: parallel | sequential
    tradeoff: "description of capability loss"
    n-2-fallback: escalate-to-hitl
```
Required for every tier I and II step; optional for lighter steps the plan depends on. When nothing in the roster can stand in, record `substitute-chain: []` — the step then escalates as soon as it fails, and the tradeoff says so.

### Adaptation Rules (produced by the order step of orch-plan, read by orch-run)
```yaml
auto-adapt-rules:
  - trigger: "empty output"        # string/pattern match against observed output
    response: "retry with simplified query"
escalate-triggers:
  - trigger: "problem reframed"    # condition description
    response: "surface to the operator — re-run orch-plan"
```
**Match mechanism**: A mechanical check on observed output — substring or pattern present or absent, a count of a pattern against a threshold, a file present or absent at the output path — not semantic judgment. A rule that fires on judgment fires unpredictably, and an operator can't audit why.

---

## Execution State Schema

`execution-state.yaml` tracks resumable execution state for an OPORD. orch-run creates it in the run directory at execution start and reads it on resume; orch-run (manual mode) reads it for monitoring.

```yaml
# Execution State: {topic}
opord: "{opord filename}"
started: "{YYYY-MM-DD HH:MM}"
last-updated: "{YYYY-MM-DD HH:MM}"
status: "in-progress"  # in-progress | escalated | paused | complete | aborted
current-phase: 1
total-phases: N

phases:
  1:
    name: "{phase name}"
    status: "pending"  # pending | in-progress | complete | escalated | skipped
    started: null
    completed: null
    skills:
      skill-name:
        status: "pending"  # pending | running | complete | failed | adapted | skipped
        started: null
        completed: null
        output: null
        notes: null
        adaptation: null  # null | {rule that fired, response taken}
        contingency: null  # null | {substitute used, tradeoff}

hitl-decisions: []
  # - checkpoint: N
  #   phase: N
  #   skill: "{skill}"
  #   decision: "{approved | approved-with-conditions | rejected}"
  #   conditions: null | "{operator's conditions}"
  #   timestamp: "{YYYY-MM-DD HH:MM}"

auto-adapts-fired: 0
escalates-fired: 0
n1-contingencies-fired: 0
total-tokens-estimated: 0
```

### Field Reference

| Field | Type | Values | Purpose |
|-------|------|--------|---------|
| `status` (top-level) | string | in-progress, escalated, paused, complete, aborted | Overall execution state |
| `phases.{N}.status` | string | pending, in-progress, complete, escalated, skipped | Per-phase state |
| `phases.{N}.skills.{name}.status` | string | pending, running, complete, failed, adapted, skipped | Per-skill state |
| `hitl-decisions[]` | list | checkpoint, phase, skill, decision, conditions, timestamp | Checkpoint (HITL) decision audit trail |
| `adaptation` | object/null | rule + response taken | Auto-adapt firing record |
| `contingency` | object/null | substitute + tradeoff | N-1 contingency firing record |
