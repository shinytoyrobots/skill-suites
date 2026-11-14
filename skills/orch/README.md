<img src="assets/icon.png" alt="" width="128" align="right">

# orch — orchestrating your other skills

A large skill library has no command layer. Nothing picks which skills fit a problem or puts them in order, and nothing handles a step that fails. The `orch-` suite does that job with methods adapted from military planning. (It was `ops-` before 2.0; the old prefix said nothing about what the skills do.)

The suite has two skills. `orch-plan` takes stock of what you have installed, runs a structured situation check (METT-TC), and recommends a skill sequence with backup skills and risks stated. When you want to run it, it also writes the sequence as the full written plan the run executes (the OPORD), with its adaptation rules set before the run starts. `orch-run` carries out that plan phase by phase, stops where you need to decide, and keeps state so a run can pause for days and resume. It can also monitor a plan you run by hand.

It does not do domain work itself. It orchestrates the skills that do, and it stops early when one or two skills obviously cover the job.

## Why military planning

The underlying problem is old: given a situation and the resources on hand, produce a plan and run it. Military staffs, incident command, and similar fields have already solved it. The suite borrows its structure from US Army planning doctrine, the Military Decision-Making Process (MDMP), and the observe–orient–decide–act loop (OODA) for adjusting mid-run.

Four ideas come from other fields. A step requests a kind of work, not a named skill, the way the Incident Command System requests typed resources. Each critical step has the backup skill to use if the first one fails (an N-1 contingency), a practice from electric-grid reliability. Adaptation rules come in two classes: fixes applied without asking (auto-adapt rules), like a power grid's automatic generation control, and conditions that stop and ask you instead of guessing (escalate triggers), like the anesthesia crisis rule to call for help early.

The doctrine supplies structure and discipline, not capability. A plan is only as good as the skills you have installed.

| Skill | Does |
|---|---|
| `orch-plan` | Inventories installed skills (the force roster), runs a structured situation check (METT-TC), recommends which skills to run and in what order, and with `--order` writes the executable order (the OPORD). `--roster` only lists what is installed. Every recommended skill is checked against what is actually installed. |
| `orch-run` | Executes the OPORD phase by phase with subagents, stops at checkpoints for your decision, and keeps resumable state. Offers unfinished or paused runs before starting anything new. `--manual` checks the output of steps you run by hand. |

## Install

As a plugin, both skills at once:

```sh
claude plugin marketplace add shinytoyrobots/skill-suites
claude plugin install skill-suites-orch@skill-suites

grok plugin install shinytoyrobots/skill-suites#skills/orch
```

As individual skills, with any Agent Skills host:

```sh
npx skills add shinytoyrobots/skill-suites --skill orch-plan --skill orch-run
```

`orch-plan` alone is useful; `orch-run` follows its output.

## Where things are written

The skills make no network calls and send nothing to another service. They read your installed skills and command files, plus whatever you point them at, and write only these files, which stay until you delete them:

- `./.orch/{YYYY-MM-DD}-{topic-slug}/` in your project holds one directory per effort: the skill inventory (force roster), the situation assessment, the recommended plan, the OPORD, execution state, and the report. Add `.orch/` to `.gitignore` if you don't want efforts committed.
- `~/.orch-skills/run-log.md` holds one line per finished run, shared across projects, so you can judge later whether the suite earns its cost. Set `ORCH_STATE` to use another directory.

`orch-run` needs a host that can launch subagents and pause for your decision. Without both, use `--manual`. Everything else runs anywhere Agent Skills load. `orch-run` launches the skills your plan names; what those skills do is up to them.

## Upgrading from `ops-`

2.0 renames the suite and the plugin (`skill-suites-ops` becomes `skill-suites-orch`), folds `ops-recon` and `ops-order` into `orch-plan` and `ops-assess` into `orch-run --manual`, and removes `ops-learn` with its opening book and pattern queue. The learning loop never ran in practice, so it was cut rather than carried. Efforts in `./.ops/` and state in `~/.ops-skills/` are not read; copy a run directory to `./.orch/` to resume it.

The public suite differs from its private original. The differences are recorded in [how the public orch suite was derived](_shared/DERIVATION.md).

## License

Apache-2.0. See [LICENSE](https://github.com/shinytoyrobots/skill-suites/blob/main/LICENSE).
