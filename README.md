# skill-suites

Agent Skills suites are groups of skills that work together, and each skill installs on its own. Every skill is a self-contained directory in the [Agent Skills](https://agentskills.io) format.

## Suites

| Suite | Does | Plugin |
|---|---|---|
| [`orch-`](skills/orch/README.md) | Plans which of your installed skills to run for a problem, in what order and with what backups, then runs the plan with check-ins where you decide. Two skills (formerly the six-skill `ops-` suite). | `skill-suites-orch` |
| [`dr-`](skills/dr/README.md) | Runs deep research with working memory on disk: explores a topic for leads, or builds a challenged report whose claims an independent verifier checks against retained sources. Audits and refreshes past runs. Four skills. | `skill-suites-dr` |

Each suite's README covers what it does, what it writes, and what it needs from the host.

## Install

Install any skill on its own, with any Agent Skills host:

```sh
npx skills add shinytoyrobots/skill-suites --list
npx skills add shinytoyrobots/skill-suites --skill orch-plan --skill orch-run
```

Or install a whole suite as a plugin. Each suite is its own plugin, named `skill-suites-<suite>`:

```sh
claude plugin marketplace add shinytoyrobots/skill-suites
claude plugin install skill-suites-orch@skill-suites
claude plugin install skill-suites-dr@skill-suites

grok plugin install shinytoyrobots/skill-suites#skills/orch
grok plugin install shinytoyrobots/skill-suites#skills/dr
```

## Repository layout

```text
skills/<suite>/                          one plugin per suite
  suite.yaml                             plugin metadata, edited by hand
  README.md                              what the suite does; the plugin listing text
  .claude-plugin/plugin.json             generated from suite.yaml
  _shared/                               suite doctrine, edited here, vendored into each skill
  skills/<skill>/SKILL.md                one skill per directory
.claude-plugin/marketplace.json          generated: every suite, for Claude
.grok-plugin/marketplace.json            generated: every suite, for Grok
scripts/vendor-references.sh             copies _shared files into the skills that link them
scripts/render-plugins.sh                writes the manifests and marketplaces from suite.yaml
docs/adding-a-suite.md                   rules for the next suite
docs/submitting.md                       listing a suite in the Claude directory and Grok catalog
```

An installed skill never reads outside its own directory; `_shared` has no `SKILL.md` and is not installable. To add a suite, follow the [rules for adding a suite](docs/adding-a-suite.md).

## License

Apache-2.0. See [LICENSE](LICENSE).
