# Derivation: dr

Ported from the private `claude-skills` library, `deep-research/` at commit `e24f154` (2026-11-05, after the split into `dr-explore` and `dr-rigor`). Rewritten in place and edited here from now on. The private copy keeps its own bindings, and the two are allowed to diverge.

## Kept

The phases (brief, scan, deep dive, challenge and expansion, synthesis and verification); the tier budgets, caps and search allowances; the plan schema with requirements and brief items; the claim-ID and provenance rules; the verifier's ledger and statuses; the two mechanical checks, unchanged apart from their paths.

## Deliberate differences

- **Run folders** go in `./.dr/{YYYY-MM-DD}-{topic-slug}/` and the run index in `./.dr/index.md`, instead of a personal notes tree.
- **Subagent methodology** (`web-researcher`, `lateral-thinking`, `structured-notes`, `dr-verifier`) ships as plain files in `references/`. The private suite installs them as named agents under `~/.claude/agents/`; a skill that reads from outside its own directory fails on someone else's machine. The orchestrator passes each subagent the absolute path of the file to read first.
- **Scripts** are vendored into each skill that runs them, and `scripts/vendor-references.sh` now vendors `scripts/` links as well as `references/` and `assets/`.
- **Frontmatter** is reduced to the Agent Skills fields. Model, tool lists, cost and readiness metadata, and cross-suite `works-with` lists were dropped.
- **Private context files** (`vault-access.md`, `output-patterns-core.md`) are not ported. Their only role was output routing, replaced by the run-folder rule.
- **Eval material** is not published: the briefs, runners, scores and handoffs reference private projects. Budget notes that cited specific eval runs were reworded as general observations.
- **"Eval run" wording** became "non-interactive run".
