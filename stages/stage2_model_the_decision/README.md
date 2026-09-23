# Stage 2 · Model the decision

Turns the decision card into an explicit, testable severity tree — no model,
no guessing. This is the **guardrail layer** (ADR-2): deterministic branches
live here in code; only genuine judgement calls are left for the agent's
reasoning in later stages.

## Files
- **[`decision_tree.py`](decision_tree.py)** — the tree itself, as a pure function `classify()`.
- **[`logic_tests.py`](logic_tests.py)** — 20 scenarios, including the real KLCC01/BKBT02 cascade.

## Run it

```bash
cd stages/stage2_model_the_decision
python3 logic_tests.py
```

> **Expected:** `20 of 20 scenarios passed.` then `ALL SCENARIOS PASS`. No
> model call, no cost, runs in under a second.

## The tree, in words

```
                        alarm arrives
                             |
                    rca == Transient? --yes--> P4 (clears itself)
                             | no
                    sa_flag == False? --yes--> P4 (not service-affecting)
                             | no
                    severity_num == 1 (Critical)?
                        |                    |
                       yes                   no
                        |                    |
          site is Golden Hub,        severity_num == 2 (Major)?
          OR subscribers >= 5000          |          |
                |            |           yes         no
               yes           no           |          |
                |            |           P2         P3
               P1           P2
          (human confirms)
```

## Why a human confirms every P1
The tree can tell you an alarm *looks* like a P1. Whether it actually opens
as one — and everything that follows, like dispatching a field team — still
needs a person (Stage 1's autonomy table, ADR-1). The tree's job is to make
that person's decision fast and consistent, not to replace it.

**Next:** [Stage 3 · Measure](../stage3_measure/) asks whether this tree is
actually making things better, with a number.

## See it live

Run `adk web` from `stage_agents/` (see the root [README.md](../../README.md#watching-every-stages-own-agent-one-at-a-time)), pick **stage02_model_the_decision_agent**, and try the prompt in the root README's table — every tool call it makes is the real code from this folder, not a simulation.
