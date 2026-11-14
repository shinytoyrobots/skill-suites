---
tagline: Audits a finished report against the evidence its run kept, without changing the report.
---
## What it does

It reads a report and the source files saved in its run folder, then writes one claim ledger. Each claim is marked supported, overstated, unsupported or without retained evidence, and any claim still unchecked after three audit passes is reported as such. Nothing else in the folder is touched. It works on reports from dr-explore and dr-rigor, and on other suites' research output when evidence was kept.

## Where it came from

dr-verify is the audit mode of the independent verifier in dr-rigor, packaged as its own skill. It uses the same ledger statuses and the same citation-check script, run in up to three passes. The original design is from the private library this suite was ported from.
