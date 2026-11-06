# Form: decision brief

Body sections, after the Executive Summary (which states the recommendation in one sentence,
ending `Basis: F{n}, ...`):

## The Decision
The choice, the options considered, and the criteria that matter.

## Options
For each option: what it is, pros, cons, cost, risk, with evidence and confidence.

## Comparison
A table of options against criteria, with claim IDs in the cells.

## Competing hypotheses (ACH)
Heuer's Analysis of Competing Hypotheses. Rows are the key pieces of evidence (claim IDs);
columns are the options, each framed as a hypothesis ("Option A is the best choice"). Mark each
cell C (consistent), I (inconsistent) or N (neutral). Score each option by how many items are
**inconsistent** with it: evidence rules options out, it doesn't pile up in their favor. Note
which items are diagnostic (consistent with one option, inconsistent with another) and which
would change the result if they turned out wrong.

| Evidence | Option A | Option B | Option C |
|---|---|---|---|
| [F2] ... | C | I | N |
| **Inconsistent count** | 0 | 1 | 0 |

## Recommendation
The recommended option (the one with the fewest serious inconsistencies, not the most support), the
conditions under which a different option wins, ending `Basis: F{n}, ...`. If the recommended
option could not be tested directly on the brief's examples during the run (for example, no API key)
while another option was measured on them, state that in the Executive Summary and include the best
measured option (with its concrete threshold or parameters) as the tested baseline or fallback.
Give each option its Brief items status (`measured`, `literature only`, `blocked`, `not
assessed`). A `blocked` option names the missing prerequisite and a reproducible proposed test
(inputs, method, the result that would change the recommendation).
