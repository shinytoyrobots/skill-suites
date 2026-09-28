# skill-suites

Agent Skills suites are groups of skills that work together, and each skill installs on its own. Every skill is a self-contained directory in the [Agent Skills](https://agentskills.io) format.

## Suites

| Suite | Does | Plugin |
|---|---|---|
| [`ops-`](skills/ops/README.md) | Plans, orders, runs, and learns from multi-skill efforts across your installed skills. Six skills. | `skill-suites-ops` |

Each suite's README covers what it does, what it writes, and what it needs from the host.

## Install

Install any skill on its own, with any Agent Skills host:

```sh
npx skills add shinytoyrobots/skill-suites --list
npx skills add shinytoyrobots/skill-suites --skill ops-recon --skill ops-plan --skill ops-order \
  --skill ops-run --skill ops-assess --skill ops-learn
```

Or install a whole suite as a plugin. Each suite is its own plugin, named `skill-suites-<suite>`:

```sh
claude plugin marketplace add shinytoyrobots/skill-suites
claude plugin install skill-suites-ops@skill-suites

grok plugin install shinytoyrobots/skill-suites#skills/ops
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
