# Adding a suite

The rules every suite in this repository follows. They exist because an installer copies one skill directory and nothing beside it: anything a skill reaches for outside that directory is missing on someone else's machine.

## Layout

- One directory per suite at `skills/<prefix>/`, one directory per skill at `skills/<prefix>/<prefix>-<action>/`, each with a `SKILL.md`.
- The directory name and the frontmatter `name` match exactly — lowercase, kebab-case, at most 64 characters.
- Doctrine, voice, and templates shared across the suite live in `skills/<prefix>/_shared/`. `_shared` never contains a `SKILL.md`, so it is never listed or installed as a skill.

## Shared files are vendored, not referenced

- Edit the file in `_shared`. Link it from a `SKILL.md` as `references/<name>` (read on demand) or `assets/<name>` (copied or filled in, such as templates).
- Run `scripts/vendor-references.sh`. It copies each linked `_shared` file into the skills that link it and removes copies no longer linked.
- Commit the copies with the `_shared` change. A second run of the script must produce no diff.
- Never link `../_shared/...` or any path outside the skill's own directory.

## No machine-specific bindings

- No absolute paths into a particular person's home, notes, or tooling. Run artifacts go in a documented project-relative directory (the `ops-` suite uses `./.ops/`); cross-project state goes in a documented home-relative directory with an environment-variable override (`~/.ops-skills/`, `OPS_STATE`).
- No personal state. Ship empty templates in `assets/` and have the skill create the real file on first use. A seeded file that names someone's own work, projects, or dates doesn't ship.
- No dependency on skills outside the suite except by discovery at runtime.

## Frontmatter

- `name`, `description`, `license: Apache-2.0`. Add `compatibility` only when the skill needs something a host may lack, and phrase it as the capability needed, not a specific product's tool name.
- Suite-specific data goes in `metadata` as string values (for example `metadata.capability-class`, `metadata.tier`).
- The description says what the skill does and when to use it, in the third person, with a negative boundary against its nearest neighbors. No workflow summary — a description that summarizes the steps gets followed instead of the body. No all-caps trigger lists.

## Derivation note

When a suite is ported from a private or internal source, `_shared/DERIVATION.md` names the source and commit it was derived from and lists the deliberate differences. The public copy is edited here afterward; the two are allowed to diverge.

## Before calling a suite done

1. `skills-ref validate` passes on every skill directory.
2. `npx skills add <this repo> --list` shows every skill and does not show `_shared`.
3. A repository search finds none of the source's private paths, names, or prefixes. A standard install location that any user of a host has (such as `~/.claude/commands`) is not private, and may appear where a skill scans for installed skills — as in `ops-recon`'s scan-root table. Anywhere else, treat it as a leak: a skill that reads or writes there is binding to one person's setup.
4. After installing one skill alone into an empty project, every link in its `SKILL.md` resolves inside the installed directory.
5. `scripts/vendor-references.sh` run twice produces no diff.
