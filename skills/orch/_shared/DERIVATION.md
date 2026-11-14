# Derivation: orch

Ported by hand from the private `claude-skills` library, `orch-skills/` at commit `d2e6b58` (2026-11-14). It replaces the earlier `ops` port (from `ops-skills/` at `b8dd8d8`, 2026-09-27). The files here were rewritten rather than generated, and are edited here from now on. The private copy keeps its own bindings, and the two are allowed to diverge.

## Kept

METT-TC; the 14 capability classes; tiers I–V; four-phase wargaming; the five-paragraph OPORD; Commander's Intent; N-1 contingencies; auto-adapt versus escalate with string matching; the execution-state and schema key names; one decision per checkpoint; the jargon gloss table. From the private 2026-11 redesign: two skills (plan and run) instead of six; early exit when one or two skills suffice; a one-screen summary before any file is written; every recommended skill checked against the install, not the roster; the resume rule that offers unfinished and paused runs before the newest effort (paused runs are never auto-continued, and resume at `current-phase`); the closing-block voice rules.

## Deliberate differences

- **Run artifacts** go in `./.orch/{YYYY-MM-DD}-{slug}/`, one directory per effort, instead of a personal notes tree. The private suite files artifacts type-first across several folders and resolves siblings by a mission id; the public layout keeps one effort in one folder, so that machinery is not needed.
- **Durable state** is a single run log in `~/.orch-skills/` (override `ORCH_STATE`). The private opening book, pattern queue, and `ops-learn` are not published: that loop never ran and is archived privately.
- **Discovery** reads `SKILL.md` frontmatter from the standard project and user skill directories plus top-level command files, and fingerprints those roots with a portable GNU/BSD `stat` command. Classes come from `metadata.capability-class` / `metadata.tier` or are inferred from the description; the private prefix-to-class table is gone, and an unreadable skill stays unclassified instead of defaulting to a class.
- **Doctrine examples**: the capability-class table's example-suites column is a kind-of-work description.
- **Voice**: "the operator" replaces the private reader; the four legibility rules are inlined in `orch-voice.md` rather than pointing at a separate private rules file.
- **Bodies**: paste-ready YAML blocks with placeholder comments were replaced with prose field lists (models copy placeholders literally). The shared schemas in `orch-doctrine.md` are unchanged.
- **Hosts**: no host-specific tool lists, and no slash-command names; skills are referred to by name.
- **References**: roster discovery, order format, and manual mode are each used by one skill, so they live in that skill's `references/` rather than `_shared`.
