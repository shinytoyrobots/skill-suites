# Adding a suite

The rules every suite in this repository follows. They exist because an installer copies one skill directory and nothing beside it: anything a skill reaches for outside that directory is missing on someone else's machine.

## Layout

Each suite is one plugin folder. Claude and Grok both look for a plugin's skills at `skills/<name>/SKILL.md` inside it, and the skills CLI finds them three levels under the repo's `skills/`.

```text
skills/<prefix>/
  suite.yaml                          plugin metadata, edited by hand
  README.md                           the plugin listing text
  assets/icon.png                     optional plugin icon
  .claude-plugin/plugin.json          generated
  _shared/                            doctrine, voice, templates
  skills/<prefix>-<action>/SKILL.md   one directory per skill
```

- The skill directory name and the frontmatter `name` match exactly — lowercase, kebab-case, at most 64 characters.
- Doctrine, voice, and templates shared across the suite live in `skills/<prefix>/_shared/`. `_shared` never contains a `SKILL.md`, so it is never listed or installed as a skill.
- No symlinks. The Claude directory's scanner rejects them.

## Shared files are vendored, not referenced

- Edit the file in `_shared`. Link it from a `SKILL.md` as `references/<name>` (read on demand) or `assets/<name>` (copied or filled in, such as templates).
- Run `scripts/vendor-references.sh`. It copies each linked `_shared` file into the skills that link it and removes copies no longer linked.
- Commit the copies with the `_shared` change. A second run of the script must produce no diff.
- Never link `../_shared/...` or any path outside the skill's own directory.

## Plugin metadata

- Copy `skills/ops/suite.yaml` and change every field. `name` is `skill-suites-<prefix>`; a bare prefix such as `ops` is generic enough that the directory holds it for a reviewer.
- `keywords` are brand-scoped only: `skill-suites` plus the suite's skill names. Grok uses them to suggest the plugin, and a generic word gets the entry sent back.
- `description` is one sentence saying what the suite does for the person.
- `icon` is optional: a `./` path to a square PNG inside the suite, conventionally `assets/icon.png`, kept under 256 KB. The render script writes it into `plugin.json`, which both Claude and Grok read. Neither marketplace file has an icon field. The suite-level `assets/` holds no `SKILL.md`, so it is never installed as a skill.
- Bump `version` whenever the suite's behavior changes. The directory asks for a new version on each release.
- After vendoring, run `scripts/render-plugins.sh`. It writes the suite's `plugin.json` and adds the suite to both marketplace files. Never edit those files by hand.

## Suite README

`skills/<prefix>/README.md` is the text the Claude directory lists. At least 40 words. It says what the suite does, every place it writes (project-relative and home-relative, with the override variable), and whether it makes network calls. The root README gets one row in its suite table linking here.

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
5. `scripts/vendor-references.sh` then `scripts/render-plugins.sh`, each run twice, produce no diff, and `scripts/render-plugins.sh --check` exits 0.
6. The suite README is at least 40 words.
7. `claude plugin validate skills/<prefix>` passes, when the Claude Code CLI is on the machine. `grok plugin validate skills/<prefix>` likewise.

Then list it: [submitting a suite](submitting.md).
