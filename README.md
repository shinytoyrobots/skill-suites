# skill-suites

Agent Skills suites: groups of skills that work together, each installable on its own. Every skill is a self-contained directory that follows the [Agent Skills](https://agentskills.io) format.

## ops — orchestrating your other skills

A large skill library has no command layer: nothing that picks which skills fit a problem, sequences them, handles a step that fails, and remembers which sequences worked. The `ops-` suite adapts military planning doctrine to that job. Recon inventories what's installed; plan runs a structured situation check (METT-TC) and recommends a skill sequence; order writes it up as a five-paragraph operations order (OPORD) with backup skills and pre-committed adaptation rules; run executes it phase by phase, stopping at your checkpoints; assess monitors a plan you run by hand; learn promotes sequences that keep succeeding into an opening book that plan checks first. The book stores kinds of work, not skill names, so what it learns survives changes to your library.

| Skill | Does |
|---|---|
| `ops-recon` | Inventories installed skills into a force roster by kind of work and weight |
| `ops-plan` | Recommends which skills to run, in what order, for a problem |
| `ops-order` | Turns the recommendation into an executable OPORD |
| `ops-run` | Executes the OPORD with subagents, checkpoints, and resumable state |
| `ops-assess` | Monitors a hand-run OPORD and writes the execution report |
| `ops-learn` | Promotes recurring successful sequences into the opening book |

### Install

```sh
npx skills add <owner>/skill-suites --skill ops-recon --skill ops-plan --skill ops-order \
  --skill ops-run --skill ops-assess --skill ops-learn
```

Or `--list` to see what's available, and install any subset. `ops-plan` alone is useful; the others follow its output.

### Where things are written

- `./.ops/{YYYY-MM-DD}-{topic}/` in your project — one directory per effort: roster, assessment, recommended plan, OPORD, execution state, report. Add `.ops/` to `.gitignore` if you don't want efforts committed.
- `~/.ops-skills/` — the opening book and pattern queue, shared across projects. Set `OPS_STATE` to use another directory.

`ops-run` needs a host that can launch subagents and pause for your decision. Everything else runs anywhere Agent Skills load.

## Repository layout

```
skills/<suite>/<skill>/SKILL.md     one skill per directory
skills/<suite>/_shared/             suite doctrine, edited here, vendored into each skill
scripts/vendor-references.sh        copies _shared files into the skills that link them
docs/adding-a-suite.md              rules for the next suite
```

An installed skill never reads outside its own directory; `_shared` has no `SKILL.md` and is not installable.

## License

Apache-2.0. See [LICENSE](LICENSE).
