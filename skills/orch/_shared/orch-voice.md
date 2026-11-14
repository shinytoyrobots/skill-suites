# Orch Operator Voice

How `orch-` skills talk to the person running them (the operator). The doctrine vocabulary is the product, so it stays in every file and every message. This file sets how to make it legible to someone who has never opened `orch-doctrine.md`.

## Why this suite needs it

`orch-run` executes multi-phase OPORDs, pauses at operator checkpoints, and fires rules mid-run. It reports on runs that may be days old. The reader is often resuming cold, reading out of order, and facing METT-TC and OPORD terms that mean nothing without the doctrine open.

## The four rules

1. **Plain phrase with the canonical term, every time.** In anything printed to the operator, say the plain phrase and put the canonical term in parentheses, on every use and not only the first. A reader who resumes mid-run never saw the first use.
2. **A number is printed only with what it decides.** Never print a bare score or count. Say what it means for the decision in front of the operator, or leave it out.
3. **One decision per prompt.** A prompt asks exactly one question: question first, at most three sentences of context, then the options and what each would do next. Several decisions stacked behind one prompt get approved together without being read.
4. **End with a closing block of at most 150 words**, in this order: what happened (one or two plain sentences), what it means (the consequence for the work), decisions needed ("None" is valid), next step (one command or action, with a one-clause reason). Detail lives in the files and is referenced by path.

## Jargon gloss table

Canonical terms stay as-is in `execution-state.yaml`, `situation-assessment.yaml`, and the run log. Rule 1 applies to anything printed to the operator.

| Canonical | Operator phrasing |
|---|---|
| METT-TC | "a structured situation check (METT-TC)" |
| COA | "a candidate plan (a COA)" |
| OPORD | "the full written plan the run executes (the OPORD)" |
| force roster | "the list of installed skills it can choose from (the force roster)" |
| Commander's Intent | "the one sentence that has to survive even if the plan changes (Commander's Intent)" |
| key terrain | "the one resource whose absence would block the most (key terrain)" |
| wargaming | "stress-testing the plan before running it (wargaming)" |
| quiescence check | "checking every output has somewhere to go (a quiescence check)" |
| volatile (end state) | "an output nothing downstream reads (volatile)" |
| pre-mortem | "assuming the plan failed and working out why (a pre-mortem)" |
| N-1 contingency | "the backup skill to use if the first one fails (an N-1 contingency)" |
| N-2 fallback | "the second-level fallback when a backup skill also fails (N-2)" |
| auto-adapt rule | "a fix it applies on its own without asking (an auto-adapt rule)" |
| escalate trigger | "a condition that stops and asks you instead of guessing (an escalate trigger)" |
| HITL checkpoint | "a point where the run stops for your decision (a HITL checkpoint)" |
| anti-fixation check | "a check that the plan still fits what the run has found (an anti-fixation check)" |
| tier (I–V) | "how heavy a lift this step is (tier I = full multi-agent effort … tier V = a quick check)" |
| capability-class | "what kind of work this step is doing (its capability-class)" |

Terms not in the table follow the same pattern: plain phrase first, canonical term in parentheses, every time.

## Numbers that read wrong at face value

- **Quality** (high/medium/low on a finished run) is a retrospective tag on that run: whether its steps finished without stopping to ask the operator. It is not a grade on the work. Print it with that meaning, or not at all.
- **Readiness** (green/amber/red on a roster entry) says no missing file or tool was found. It does not mean the skill works well. Print counts as "N ready, M need something fixed", and name the M.

## Surface map

| Surface | Register |
|---|---|
| `orch-plan` one-screen summary, early-exit answer, closing block; roster and order summaries | Operator: the four rules apply |
| `orch-run` checkpoint, escalation, N-2, anti-fixation and resume prompts; narration between phases; completion block | Operator: the four rules apply |
| OPORD one-liner (`{skill-A ∥ skill-B} → {skill-C} \| N skills, N phases, ~Nk tokens`) | Operator: already the compressed human form; keep imitating it |
| Full 5-paragraph OPORD (`opord.md`) | Audit-leaning: written for `orch-run` to execute and for the operator to approve at the planning gate; stays dense |
| `execution-state.yaml`, `situation-assessment.yaml`, `execution-report.md`, run log | Audit: canonical terms only |
