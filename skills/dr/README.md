# dr — deep research you can audit

Most research prompts collapse into one shallow pass: a few searches, a quick summary, no trail. The `dr-` suite runs research as a sequence of phases that write to disk as they go, so a long run keeps its place and a finished report can be checked against what was actually fetched.

The suite has four skills, split by the job you need done.

| Skill | Does |
|---|---|
| `dr-explore` | Maps a topic and follows leads, including a lateral-thinking scout that tests non-obvious connections. It makes no independent claim check. Use it for discovery. |
| `dr-rigor` | Adds a depth tier with a budget, a challenge phase that looks for counter-evidence, stated gaps, and an independent verifier that checks every tagged claim against the retained sources. Use it when others will rely on or challenge the answer. |
| `dr-verify` | Audits an existing report against the evidence its run folder kept, and writes a claim ledger without changing the report. |
| `dr-update` | Searches only for what changed since an earlier run and writes a dated delta and a revised, verified report beside the original. |

## What the evidence says

The rigorous skill has not been shown to produce a better answer than the bare model. In head-to-head runs on the same briefs it tied with the original exploratory skill and with the model alone, and it cost several times more. What it adds is inspectability: counter-evidence, named gaps, and a link from each claim to a retained source. Choose `dr-rigor` for that, not for accuracy you can't yet demonstrate.

## Install

As a plugin, all four skills at once:

```sh
claude plugin marketplace add shinytoyrobots/skill-suites
claude plugin install skill-suites-dr@skill-suites

grok plugin install shinytoyrobots/skill-suites#skills/dr
```

As individual skills, with any Agent Skills host:

```sh
npx skills add shinytoyrobots/skill-suites --skill dr-explore --skill dr-rigor \
  --skill dr-verify --skill dr-update
```

Each skill installs on its own and carries the methodology files it needs.

## Where things are written

The skills make network calls: they use the host's web search and web fetch tools to read public pages, and send nothing else anywhere. They write only to these places, which stay until you delete them:

- `./.dr/{YYYY-MM-DD}-{topic-slug}/` in your project holds one folder per run: the brief, the plan, the notes log with an agent spend table, one file per fetched source and per research thread, the draft, the claim ledger, and `research-output.md`. The brief can name another destination. Add `.dr/` to `.gitignore` if you don't want runs committed.
- `./.dr/index.md` is a table with one row per finished run. `dr-rigor` and `dr-update` append to it.

`dr-update` never edits an earlier run's files; everything it writes carries a new `update-` or `u{date}` name.

## What the host needs

A host that can launch subagents, search and fetch the web, and write files. `python3` runs the two mechanical checks (`citation-check.py`, `verify-ledger.py`). Subagent launches name model tiers (`sonnet`, `haiku`, `opus`); on another host, map them to a capable, a fast, and a strongest model. A rigorous run launches many subagents. `dr-budget.md` sets the caps per tier, and a standard run is expected to cost far more than a plain chat answer.

This public port differs from its private original. The differences are recorded in [how the public dr suite was derived](_shared/DERIVATION.md).

## License

Apache-2.0. See [LICENSE](https://github.com/shinytoyrobots/skill-suites/blob/main/LICENSE).
