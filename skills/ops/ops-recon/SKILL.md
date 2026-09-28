---
name: ops-recon
description: Inventories the Agent Skills installed for the current project and user and sorts them into a force roster by kind of work (capability class) and weight (tier). Use when the operator asks what skills they have, wants their skill library inventoried or mapped, or before planning a multi-skill effort with ops-plan when no fresh roster exists. Not for questions about how a single skill works, or about the agent host's own features.
license: Apache-2.0
metadata:
  suite: ops
  capability-class: meta-orchestration
  tier: III
---

# Ops Recon — Capability Discovery

Read [ops-doctrine.md](references/ops-doctrine.md) for the capability classes, tiers, and the run-directory contract, and [ops-voice.md](references/ops-voice.md) for how to word the summary.

Recon is the Troops half of the situation check that ops-plan runs. Without a current roster, ops-plan can only guess at what the operator can actually launch.

## Input

The operator's request may carry:

- **nothing** — scan the default roots below
- **a path** — scan only that directory (every `SKILL.md` beneath it), replacing all default roots including command files; skills found there get `scope: path`
- **`manual`** — the operator supplies the capability list; ask for name, description, and optionally a capability class for each, then classify as below
- **`--out <dir>`** — write the roster into that run directory (ops-plan passes this)

## Phase 1: Discovery

Scan these roots, following symlinks (`find -L`), because installers commonly symlink skill directories into place:

| Scope | Roots |
|---|---|
| project | `./.agents/skills`, `./.claude/skills`, `./.grok/skills`, `./.codex/skills` |
| user | `~/.agents/skills`, `~/.claude/skills`, `~/.grok/skills`, `~/.codex/skills` |
| command files | `~/.claude/commands/*.md` (top level only) |

In the skill roots, each `*/SKILL.md` is one skill; read its YAML frontmatter for `name`, `description`, `compatibility`, and `metadata`. A command file is one skill named after its filename; read the same fields from its frontmatter if it has any, treating top-level `capability-class` and `tier` like their `metadata` equivalents.

**Duplicates.** The same skill is often installed into several roots at once, one per agent host. Deduplicate by `name`. Keep the project-scope copy over the user-scope one, and record the other locations under `also-at` so the operator can see the overlap.

## Phase 2: Classification

**Declared.** When `metadata.capability-class` (and `metadata.tier`) are present, use them as given. They are strings; a declared class that isn't one of the 14 in the doctrine goes into `readiness-warnings` and the skill is left unclassified.

**Inferred.** Otherwise, read the description against the doctrine's "Kind of work" column. When it fits more than one class, take the most specific (a competitor scan is `market-intelligence`, not `intelligence-gathering`) and say why in a `class-note`. Set `inferred: true`. When the description plainly describes no class, leave the skill **unclassified** — do not fall back to a default class. A wrong class sends ops-plan to the wrong skill with false confidence; an unclassified skill is at least visibly unknown.

**Tier**, when not declared, from the description:

| Signal | Tier |
|---|---|
| multi-phase, orchestrates, launches several agents | I |
| comprehensive, framework-driven, structured multi-step workflow | II |
| one structured output, no subagents | III |
| quick, check, lookup, feeds another skill | IV |
| status, log, single-purpose | V |

Default to III when signals conflict. Overestimating a step's weight costs some budget; underestimating it leaves the step without a backup skill.

**Readiness:**

- **green** — nothing blocking detected
- **amber** — the `SKILL.md` links a file under its own directory that doesn't exist, or `compatibility` names a requirement recon cannot confirm (note which)
- **red** — the frontmatter didn't parse; the skill is listed with the parse error and not classified

## Phase 3: Roster

Write `force-roster.yaml` with a header (`generated` timestamp, `roots-scanned`, `totals` for skills, classified, inferred, unclassified), then a `roster:` map from each non-empty capability class to its skills, then `unclassified:` and `readiness-warnings:` lists. Each skill entry carries `name`, `tier`, `scope` (project, user, command, or path), `path`, `readiness`, `inferred` (true/false), `class-note` when the choice needed reasoning, and `also-at` when duplicated.

## Phase 4: Output

Write the roster to the run directory (see the doctrine's "Run Artifacts and Durable State"):

- `--out <dir>` given → that directory
- otherwise, if the latest effort directory holds a `force-roster.yaml` but no `situation-assessment.yaml`, it is an unclaimed recon — overwrite its roster
- otherwise create `./.ops/{YYYY-MM-DD}-recon/`

Return a 3–5 line summary in the operator register:

```
## Force roster ready
- {N} skills installed; {M} kinds of work covered (capability classes)
- Most coverage: {class} ({n}), {class} ({n}), {class} ({n})
- {U} skills whose kind of work couldn't be read from the description (unclassified) — {one-line consequence, e.g. "ops-plan won't pick these"}
- {Any readiness warning worth acting on}
- Written to {path}
```

## Gotchas

- **Empty roots are normal.** Most machines have two or three of the roots. A missing root is skipped silently; zero skills overall produces a valid empty roster, not an error.
- **Descriptions written for routing, not classification.** Many descriptions say when to use a skill but not what kind of work it does. That's why unclassified is a legitimate outcome — suggest the skill's author add `metadata.capability-class` rather than forcing a guess.
- **This suite classifies itself.** The `ops-` skills declare `meta-orchestration`; ops-plan excludes that class from Troops so a plan never schedules itself.

## Next

> Force roster written. Run ops-plan with the problem statement to get a recommended plan.
