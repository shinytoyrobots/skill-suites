---
name: ops-learn
description: Promotes recurring, successful skill sequences from the ops pattern queue into the opening book that ops-plan consults first, records known-bad sequences, and ages out plans that have gone unused. Use when the operator asks to update or review the opening book, promote learned patterns, or close the learning loop after several ops-run or ops-assess executions. Not for model training or general "what did we learn" retrospectives.
license: Apache-2.0
metadata:
  suite: ops
  capability-class: meta-orchestration
  tier: IV
---

# Ops Learn — Opening Book Promotion

Read [ops-doctrine.md](references/ops-doctrine.md) (Opening Book Schema, Pattern Queue Entry, durable state) and [ops-voice.md](references/ops-voice.md).

Learn closes the loop: ops-run and ops-assess queue a structural pattern after each completed execution, and learn decides which of those have earned a place in the opening book. The book is what lets ops-plan skip analysis on a problem shape it has seen succeed before.

## Input

None. Both files are in the durable-state directory: `$OPS_STATE` if set, else `~/.ops-skills/`.

## Phase 1: Load

- `pattern-queue.yaml` — if missing, copy [the empty queue template](assets/pattern-queue.yaml) into place. If the queue is empty, skip Phase 2 and go to decay.
- `opening-book.yaml` — if missing, copy [the empty book template](assets/opening-book.yaml) into place.

## Phase 2: Pattern Analysis

**Group** queue entries by the ordered list of `class` values in their `capability-chain`. Tiers are not part of the key — the same class sequence at different weights is the same structure. `problem-class` feeds trigger phrases, not grouping. For each group, collect the count, the spread of `output-quality`, the `problem-class` values, and the date range.

**Promote** each group with **3 or more `high` entries.**

- *New structure* (no book pattern has this class sequence): `pattern-id` from the most common `problem-class`, kebab-cased (append `-2`, `-3` on collision); `triggers` from the distinct `problem-class` values; `capability-chain` from the class sequence, with the most common tier per position; `reference-example` with an empty `skills-used` (the queue stores classes, not skill names) and the latest entry's date; `confidence: 0.75`; `sessions` = the group's count; `last-used` = the latest date.
- *Existing structure*: add the group's count to `sessions`, set `last-used` to the latest date, raise `confidence` by 0.02 per new session, capped at 0.95.

Three is the threshold because one good run is luck and two is a coincidence; the book should hold only shapes that keep working.

**Capture failures** — each group with **2 or more `low` entries** goes into `failure-patterns`, same schema, `confidence: 0.60` (here, how sure the approach fails).

**Trim** the queue: remove entries that contributed to a promotion or a failure capture. Everything else stays to keep accumulating. Write the trimmed queue back.

## Phase 3: Confidence Decay

For each book pattern: `last-used: null` is exempt (never used is not unused); a non-null `last-used` more than 30 days ago loses 0.05, floor 0.30; anything more recent is unchanged. Write the book back.

## Phase 4: Summary

Return, in the operator register — every count with what it changes:

```
## Opening book updated
- {N} new plans added to the library of plans that worked before (the opening book) — ops-plan will offer these first on matching problems
- {N} existing plans reinforced; {N} known-bad sequences recorded (failure patterns)
- {N} plans aged for sitting unused over 30 days (confidence decay) — they'll get more re-checking before reuse
- Queue: {N} entries cleared, {N} still accumulating
- Book: {N} plans, {N} failure patterns — {path}
```

## Gotchas

- **Nothing to do.** Empty queue and nothing old enough to decay: "Nothing to process — queue empty, no plans due for decay." Stop.
- **All medium.** Medium entries never promote or fail. Say how many are accumulating so the operator knows the loop is working, just not yet deciding.
- **Hand-edited files.** The operator may edit the book directly. Preserve unknown keys and comments you don't need to change.

## Next

> Opening book updated. Next: ops-plan on a new problem to use it, or ops-recon if skills have changed.
