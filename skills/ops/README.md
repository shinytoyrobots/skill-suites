# ops — orchestrating your other skills

A large skill library has no command layer. Nothing picks which skills fit a problem or puts them in order. Nothing handles a step that fails. Nothing remembers which sequences worked. The `ops-` suite does that job with methods adapted from military planning.

The suite has six skills, one per stage. `ops-recon` takes stock of what you have installed. `ops-plan` runs a structured situation check (METT-TC) and recommends a skill sequence. `ops-order` writes that sequence up as the full written plan the run executes (the OPORD). That plan names backup skills and sets its adaptation rules before the run starts. `ops-run` carries out the plan phase by phase and stops where you need to decide. `ops-assess` monitors a plan you run by hand instead. `ops-learn` saves sequences that keep succeeding into the library of plans that worked before (the opening book), which `ops-plan` checks first. That library stores kinds of work, not skill names, so what it learns survives changes to your skill library.

## Why military planning

The underlying problem is old: given a situation and the resources on hand, produce a plan and run it. Military staffs, incident command, and similar fields have already solved it. The suite borrows its structure from US Army planning doctrine, the Military Decision-Making Process (MDMP). It borrows the observe–orient–decide–act loop (OODA) for adjusting mid-run.

Four ideas come from other fields. A step requests a kind of work, not a named skill, the way the Incident Command System requests typed resources. Each critical step has the backup skill to use if the first one fails (an N-1 contingency), a practice from electric-grid reliability. Adaptation rules come in two classes. Some are fixes applied without asking (auto-adapt rules), like a power grid's automatic generation control. Others are conditions that stop and ask you instead of guessing (escalate triggers), like the anesthesia crisis rule to call for help early. The library of plans that worked before (the opening book) grows only from repeated success, as a chess opening book does.

Discovery, analysis, planning, execution, and review are separate phases, so they are separate skills. The doctrine supplies structure and discipline, not capability. A plan is only as good as the skills you have installed.

| Skill | Does |
|---|---|
| `ops-recon` | Builds an inventory of installed skills (the force roster), sorted by kind of work (capability class) and weight (tier) |
| `ops-plan` | Runs a structured situation check (METT-TC) and recommends which skills to run, in what order |
| `ops-order` | Turns the recommendation into the full written plan the run executes (the OPORD): a five-paragraph operations order with backup skills and pre-committed adaptation rules |
| `ops-run` | Executes the full written plan (the OPORD) phase by phase with subagents, stops at checkpoints for your decision, and keeps resumable state |
| `ops-assess` | Monitors a full written plan (an OPORD) that you run by hand, and writes the execution report |
| `ops-learn` | Promotes recurring successful sequences into the library of plans that worked before (the opening book), records sequences known to fail, and checks old plans harder the longer they sit unused |

## Install

As a plugin, all six skills at once:

```sh
claude plugin marketplace add shinytoyrobots/skill-suites
claude plugin install skill-suites-ops@skill-suites

grok plugin install shinytoyrobots/skill-suites#skills/ops
```

`grok plugin marketplace add shinytoyrobots/skill-suites` lists every suite in this repository in Grok's plugin browser.

As individual skills, with any Agent Skills host:

```sh
npx skills add shinytoyrobots/skill-suites --skill ops-recon --skill ops-plan --skill ops-order \
  --skill ops-run --skill ops-assess --skill ops-learn
```

Run with `--list` to see what's available, then install any subset. `ops-plan` alone is useful; the others follow its output.

## Where things are written

The skills make no network calls and send nothing to another service. They read your installed skills and command files, plus whatever you point them at, and write only these files, which stay until you delete them:

- `./.ops/{YYYY-MM-DD}-{topic-slug}/` in your project holds one directory per effort. It contains the skill inventory (force roster), the situation assessment, the recommended plan, the full written plan (OPORD), execution state, and the report. Add `.ops/` to `.gitignore` if you don't want efforts committed.
- `~/.ops-skills/` holds the library of plans that worked before (the opening book). It also holds candidate new entries for that library, waiting on review (the pattern queue). Both are shared across projects. Set `OPS_STATE` to use another directory.

`ops-run` needs a host that can launch subagents and pause for your decision. Without both, use `ops-assess` to monitor a plan you run by hand. Everything else runs anywhere Agent Skills load. `ops-run` launches the skills your plan names; what those skills do is up to them.

This public port differs from its private original. The differences are recorded in [how the public ops suite was derived](_shared/DERIVATION.md).

## License

Apache-2.0. See [LICENSE](https://github.com/shinytoyrobots/skill-suites/blob/main/LICENSE).
