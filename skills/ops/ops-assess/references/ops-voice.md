# Ops Operator Voice

How `ops-` skills talk to the person running them (the operator). The doctrine vocabulary is the product, so it stays in every file and every message. This file sets how to make it legible to someone who has never opened `ops-doctrine.md`.

## Why this suite needs it

`ops-run` executes multi-phase OPORDs, pauses at operator checkpoints, and fires rules mid-run. `ops-assess` and `ops-learn` report on runs that may be days old. The reader is often resuming cold, reading out of order, and facing METT-TC/OPORD terms that mean nothing without the doctrine open.

## The three rules

1. **Plain phrase with the canonical term, every time.** In anything printed to the operator, say the plain phrase and put the canonical term in parentheses — on every use, not only the first. A reader who resumes mid-run never saw the first use.
2. **A number is printed only with what it decides.** Never print a bare score. Say what the number means for the decision in front of the operator, or leave it out.
3. **One decision per checkpoint.** A checkpoint asks exactly one question: the step, the choice, and what approve, reject, or amend would each do next. Several decisions stacked behind one prompt get approved together without being read.

## Jargon gloss table

Canonical terms stay as-is in `execution-state.yaml`, `situation-assessment.yaml`, the opening book, and the pattern queue. Rule 1 applies to anything printed to the operator.

| Canonical | Operator phrasing |
|---|---|
| METT-TC | "a structured situation check (METT-TC)" |
| COA | "a candidate plan (a COA)" |
| OPORD | "the full written plan the run executes (the OPORD)" |
| Commander's Intent | "the one sentence that has to survive even if the plan changes (Commander's Intent)" |
| key terrain | "the one resource whose absence would block the most (key terrain)" |
| wargaming | "stress-testing the plan before running it (wargaming)" |
| quiescence check | "checking every output has somewhere to go (a quiescence check)" |
| volatile (end state) | "an output nothing downstream reads (volatile)" |
| pre-mortem | "assuming the plan failed and working out why (a pre-mortem)" |
| N-1 contingency | "the backup skill to use if the first one fails (an N-1 contingency)" |
| auto-adapt rule | "a fix it applies on its own without asking (an auto-adapt rule)" |
| escalate trigger | "a condition that stops and asks you instead of guessing (an escalate trigger)" |
| HITL checkpoint | "a point where the run stops for your decision (a HITL checkpoint)" |
| opening book | "the library of plans that worked before (the opening book)" |
| confidence routing | "how sure it is an old plan still fits, and how much re-checking that earns (confidence routing)" |
| confidence decay | "an old plan gets checked harder the longer it's sat unused (confidence decay)" |
| pattern queue | "candidate new entries for the opening book, waiting on review (the pattern queue)" |
| tier (I–V) | "how heavy a lift this step is (tier I = full multi-agent effort … tier V = a quick check)" |
| capability-class | "what kind of work this step is doing (its capability-class)" |

Terms not in the table follow the same pattern: plain phrase first, canonical term in parentheses, every time.

## Numbers that read wrong at face value

The doctrine produces two numbers that a cold reader misreads as a grade on the current run:

- **confidence** (0–1 on an opening-book entry) says how much re-checking an old, matched plan still earns. Print it as the routing it causes: "an earlier plan matches closely enough to reuse without the full situation check (confidence 0.9)".
- **output-quality** (high/medium/low on a pattern-queue entry) is a retrospective tag on a past run. Print it with what it changes: whether the run's pattern counts toward promotion.

## Surface map

| Surface | Register |
|---|---|
| `ops-run` narration between phases; checkpoint prompts | Operator — the three rules apply |
| OPORD one-liner (`{skill-A ∥ skill-B} → {skill-C} \| N skills, N phases, ~Nk tokens`) | Operator — already the compressed human form; keep imitating it |
| `ops-recon`, `ops-plan`, `ops-order` summaries; `ops-assess` report; `ops-learn` summary | Operator — the three rules apply |
| Full 5-paragraph OPORD (`opord.md`) | Audit-leaning — written for `ops-run` to execute and for the operator to approve at the planning gate; stays dense |
| `execution-state.yaml`, `situation-assessment.yaml`, opening-book and pattern-queue YAML | Audit — canonical terms only |
