---
tagline: Works out which of your installed skills to run, in what order, with backups, before anything runs.
---
## What it does

You describe a problem that needs more than one skill. It checks what is installed, sizes up the situation, and recommends a plan with the order, the risks, and a backup for each key step. If one or two skills clearly cover the problem, it says so and stops. When you plan to run the result, it writes an executable order for orch-run.

## Where it came from

orch-plan borrows its method from US military planning. The situation check follows METT-TC (mission, enemy, terrain, troops, time, civil considerations), candidate plans are tested by four-phase wargaming, and the executable order uses the five-paragraph OPORD format with a Commander's Intent statement. Wargaming ends with a pre-mortem: assume the plan failed, write three failure narratives, and check each has a counteraction. Each important step gets an N-1 contingency, a named fallback if its primary skill is missing. Your installed skills are sorted into 14 capability classes and five tiers so the plan can swap one for another. It was ported by hand from a private skill library and has been edited in this repository since.
