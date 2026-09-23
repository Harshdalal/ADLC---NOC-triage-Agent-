# Stage 5 · Build

Agent v1 is assembled from parts that already passed their own tests:
Stage 2's decision tree, Stage 3's KPI tree, Stage 4's ontology. It is
deliberately built **before** grounding, so its failures on real questions
are visible and attributable to "no data," not hidden inside a bigger change.

## Where agent v1 actually lives
Agent v1 has three forms in this kit, built in `../../agents/`:

| Variant | What it is | Stage |
|---|---|---|
| `v1_ungrounded` | Agent v1 exactly as Stage 5 leaves it — instruction only, no tools | **This stage** |
| `v1_grounded_raw` | The same agent, given tools over MCP, raw tables | Stage 6 |
| `v1_grounded_semantic` | The same agent, given tools over MCP, semantic views | Stage 6 |

They share one factory function, `apextel.grounded.make_agent()`, so the
*only* difference between them is what they can see — which is what makes
the Stage 6 comparison mean anything.

## The eval set (ADR-5)
`tests/golden_questions.csv` and `eval/grounding_questions.yaml` are fixed
**before** v1 is scored — so the baseline can't be quietly tuned to flatter
the first attempt. Both live at the kit root because Stage 6's eval harness
reads them directly.

## Run it

```bash
# from the kit root, with the ADK environment active:
python3 eval/run_grounding.py ungrounded
cd stages/stage5_build
python3 record_baseline.py
cat baseline_score.md
```

> **Expected:** `record_baseline.py` writes `baseline_score.md`, showing
> something like "0 of 10 correct" — v1 has no tools yet, so it cannot
> answer anything that needs a record or a runbook. That zero is the whole
> point: it's the number Stage 6 has to beat.

**Next:** [Stage 6 · Ground](../stage6_ground/) gives v1 its tools.

## See it live

Run `adk web` from `stage_agents/` (see the root [README.md](../../README.md#watching-every-stages-own-agent-one-at-a-time)), pick **stage05_build_agent**, and try the prompt in the root README's table — every tool call it makes is the real code from this folder, not a simulation.
