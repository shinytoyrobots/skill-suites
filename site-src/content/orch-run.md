---
tagline: Carries out a plan from orch-plan, stopping at check-ins where you make the call.
---
## What it does

Given an executable order, it checks that every skill in it is still installed, then works through the phases in sequence. State is saved to disk after each step, so a run can pause for days at a checkpoint and pick up where it stopped. When a step fails in a predictable way it adapts using the plan's rules. Anything else it escalates to you, one decision at a time.

## Where it came from

orch-run is the execution half of the same doctrine as orch-plan. It follows the OPORD the planner writes and holds to its Commander's Intent when something unexpected happens. The split between auto-adapting for known failures and escalating for unknown ones, and the fallback skills drawn from N-1 contingencies, come from that planning method. The rule that paused runs are offered but never continued automatically is from a later redesign of the private library it was ported from.
