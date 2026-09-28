# Derivation: ops

Ported by hand from the private `claude-skills` command library, `ops-skills/` at commit `b8dd8d8` (2026-09-27). The files here were rewritten rather than generated, and are edited here from now on. The private copy keeps its own bindings, and the two are allowed to diverge.

## Kept

The pipeline (recon → plan → order → run, with assess beside execution and learn after it); METT-TC; the 14 capability classes; tiers I–V; four-phase wargaming; the five-paragraph OPORD; Commander's Intent; N-1 contingencies; auto-adapt versus escalate with string matching; the opening-book, pattern-queue, and execution-state schemas and their key names; one decision per checkpoint; the jargon gloss table.

## Deliberate differences

- **Run artifacts** go in `./.ops/{YYYY-MM-DD}-{slug}/`, one directory per effort, instead of a personal notes tree. Latest effort is ranked by its newest file rather than the directory timestamp.
- **Durable state** (opening book, pattern queue) lives in `~/.ops-skills/`, overridable with `OPS_STATE`, created from empty templates in `assets/`. The private seeded book is not published.
- **Discovery** reads `SKILL.md` frontmatter from the standard project and user skill directories plus top-level command files. Classes come from `metadata.capability-class` / `metadata.tier` or are inferred from the description; the private prefix-to-class table is gone, and an unreadable skill stays unclassified instead of defaulting to `intelligence-gathering`.
- **ops-run** validates skills against a refreshed roster, not a command-file path, and launches subagents through whatever the host provides. Host-specific tool lists were dropped.
- **Doctrine examples**: the capability-class table's example-suites column is now a kind-of-work description; the opening-book example names no skills.
- **Voice**: "the operator" replaces the private reader; the three legibility rules are inlined in `ops-voice.md` rather than pointing at a separate private rules file. An `OPORD` and a `HITL checkpoint` gloss row were added.
- **Bodies**: paste-ready YAML blocks with placeholder comments in the skill bodies were replaced with prose field lists (models copy placeholders literally). The shared schemas in `ops-doctrine.md` are unchanged.
- **Output routing** from the private shared output-routing file is replaced by the run-directory rule. The empty private agents directory was not ported.
- **Templates** are vendored into the three skills that write durable state: `ops-run` and `ops-assess` (append to the queue) and `ops-learn` (both files). `ops-plan` only reads the book and treats a missing one as empty.
