---
tagline: Carries out a plan from orch-plan, stopping at check-ins where you make the call.
---
## What it does

Given an executable order, it checks that every skill in it is still installed, then works through the phases in sequence. State is saved to disk after each step, so a run can pause for days at a checkpoint and pick up where it stopped. When a step fails in a predictable way it adapts using the plan's rules. Anything else it escalates to you, one decision at a time.
