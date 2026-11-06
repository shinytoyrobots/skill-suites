# Verification: the last stage before final output

Always runs, in every tier. It has no off switch. The `dr-verifier` agent
(`references/dr-verifier.md`) checks claims and keeps the ledger; you apply its verdicts
once and run the final checks.

## Budget

One verifier launch (model sonnet) from the reserved pool, then one fix pass by you. Tool-call
cap: 20 in quick, 25 in standard, 30 in deep. There is no second verifier pass: the fix pass
applies the verifier's own wording, so it needs no recheck. Record it as one `verification` row
in `plan.md`.

## Pass

1. Launch the verifier in run mode on `draft.md`: folder, report file, cap, and the absolute path of this skill's `scripts/citation-check.py`.
2. Read `verification.md` and write `research-output.md` from `draft.md`, applying every verdict
   once:
   - `supported`: unchanged.
   - `overstated`: replace the claim (and each flagged use of its ID) with the narrower wording
     the verifier quoted as `Supports: "..."`, keeping the ID. Set the row to `narrowed`. Change
     nothing else in the sentence's factual content. If the narrowed claim no longer carries the
     point it was making, remove it instead.
   - `unsupported`, `unchecked` (the verifier's cap ran out), or `overstated` with no quoted
     wording: remove it (below).
   - `untagged`: delete the sentence, or tag it and remove it to Gaps as `Not checked`. Either
     way, set the row to `removed`.
3. Re-read every recommendation and Executive Summary sentence whose basis was narrowed: it must
   still follow from the narrowed wording, or be rewritten on its remaining claims.
4. **Coverage recheck.** Coverage counts in the final output, not in fetched files. For each
   requirement `met` in `plan.md`, confirm a claim in `research-output.md` still carries it. One
   whose only claims were removed reverts to `partial`; a brief item whose only evidence was
   removed reverts to its unresolved status. Update `plan.md`, and add each to Gaps.

## Removing a claim

A claim that ends neither `supported` nor `narrowed` becomes `removed`:

- Delete it from every non-exempt section.
- Add it to Gaps and Uncertainties, keeping its ID:
  - checked and failed: `Not verified: {claim} [F{n}] (cited {file}; verifier: {reason})`
  - never reached: `Not checked: {claim} [F{n}] (cited {file}; verifier budget ran out)`
- Note `failed` or `unchecked` in the ledger's note column.

**Recommendations that lose their basis.** If a recommendation's `Basis` names a removed ID,
rewrite it on its remaining claims, or downgrade it to a labeled `Hypothesis:` under Gaps, or drop
it. No recommendation may rest on a removed claim.

## Outcome

Set `outcome` in the ledger frontmatter:

- `passed`: every claim `supported` or `narrowed`.
- `passed-with-removals`: N removed (k failed, m unchecked).

Copy the outcome and counts into the report's frontmatter (`verification`, `narrowed`, `removed`,
`removed-failed`, `removed-unchecked`) and the Research Log.

## Final checks (mechanical, you run them; no agent)

From the run folder:

1. **Claim placement:**
   `python3 -I scripts/verify-ledger.py {folder}` (the `scripts/` directory of this skill; use its absolute path)
   Fails if an ID neither `supported` nor `narrowed` appears outside the exempt sections, a
   `removed` ID is missing from Gaps, an ID has no ledger entry, a recommendation's `Basis` names
   such an ID, a recommendation has no `Basis`, or the outcome disagrees with the ledger.
2. **URL resolution:**
   `python3 -I scripts/citation-check.py {folder} --exclude-sections "Gaps and Uncertainties"`
   Every URL cited outside Gaps must resolve to a retained, successfully fetched file.

If either fails, fix the report (removing, not re-wording, anything you can't support) and rerun
both. `final output` is `done` only when both pass. The scripts check placement and provenance;
whether a source supports a claim is the verifier's judgment in the ledger.
