# Roster discovery

Follow this when `orch-plan` needs a fresh roster, or when asked for `--roster`. It is not a separate skill.

## Input

- **nothing**: scan the doctrine's roots (see "Where installed skills live").
- **a path**: scan only that directory (every `SKILL.md` beneath it), replacing all default roots including command files; skills found there get `scope: path`.
- **`manual`**: the operator supplies the capability list; ask for name, description, and optionally a capability class for each, then classify as below.

## Discovery

Scan the roots with symlinks followed. In the skill roots each `*/SKILL.md` is one skill; read its YAML frontmatter for `name`, `description`, `compatibility`, and `metadata`. A command file is one skill named after its filename; read the same fields if it has frontmatter, treating top-level `capability-class` and `tier` like their `metadata` equivalents.

**Duplicates.** The same skill is often installed into several roots, one per agent host. Deduplicate by `name`, keep the project-scope copy over the user-scope one, and record the other locations under `also-at`.

## Classification

**Declared.** When `metadata.capability-class` (and `metadata.tier`) are present, use them as given. A declared class that is not one of the 14 in the doctrine goes into `readiness-warnings` and the skill is left unclassified.

**Inferred.** Otherwise, read the description against the doctrine's "Kind of work" column. When it fits more than one class, take the most specific (a competitor scan is `market-intelligence`, not `intelligence-gathering`) and say why in a `class-note`. Set `inferred: true`. When the description plainly describes no class, leave the skill **unclassified**. Do not fall back to a default: a wrong class sends the plan to the wrong skill with false confidence, and an unclassified skill is at least visibly unknown.

**Tier**, when not declared, from the description:

| Signal | Tier |
|---|---|
| multi-phase, orchestrates, launches several agents | I |
| comprehensive, framework-driven, structured multi-step workflow | II |
| one structured output, no subagents | III |
| quick, check, lookup, feeds another skill | IV |
| status, log, single-purpose | V |

Default to III when signals conflict. Overestimating a step's weight costs some budget; underestimating it leaves the step without a backup skill.

**Readiness**: green when nothing blocking is detected; amber when the `SKILL.md` links a file under its own directory that does not exist, or `compatibility` names a requirement that cannot be confirmed (note which); red when the frontmatter did not parse (list the error; do not classify).

## Roster file

Write `force-roster.yaml` with a header (`generated` timestamp, `fingerprint` per the doctrine, `roots-scanned`, `totals` for skills, classified, inferred, unclassified), then a `roster:` map from each non-empty capability class to its skills, then `unclassified:` and `readiness-warnings:` lists. Each skill entry carries `name`, `tier`, `scope` (project, user, command, or path), `path`, `readiness`, `inferred`, `class-note` when the choice needed reasoning, and `also-at` when duplicated. Write it to the run directory.

For `--roster`, print a closing block of at most 150 words and stop:

```
What happened: found {N} installed skills (the force roster).
What it means: {X} are ready to use. {Y} need something fixed first: {names, one-line reason each}. {U} could not be classified by kind of work from their descriptions. "Ready" means no missing file or tool was found; it does not mean the skill works well.
Decisions needed: None.
Next step: run orch-plan with the problem statement, to plan from this roster.
Roster: {path}
```

## Gotchas

- **Empty roots are normal.** Most machines have two or three of the roots. A missing root is skipped silently; zero skills overall produces a valid empty roster, not an error.
- **Descriptions written for routing, not classification.** Many descriptions say when to use a skill but not what kind of work it does. Unclassified is a legitimate outcome; suggest the skill's author add `metadata.capability-class` rather than forcing a guess.
- **This suite classifies itself.** The `orch-` skills declare `meta-orchestration`; the plan excludes that class so it never schedules itself.
