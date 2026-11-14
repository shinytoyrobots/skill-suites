---
tagline: Brings an old research run up to date by searching only for what changed.
---
## What it does

Point it at a finished dr-rigor or dr-explore folder. It grades the old findings against their retained sources, searches for what has changed since the run date, and writes a dated delta plus a revised report next to the original. The original files are never edited.

## Where it came from

dr-update reuses the budget, plan and verification rules of dr-rigor, so a refreshed report passes through the same claim check as a new one. Every file it writes carries an update ID built from the date, which lets two updates on the same day coexist. The design came from the private library this suite was ported from.
