# Stage 3 · Measure

Before the agent is built, "working" gets a number.

## Files
- **[`kpi_tree.md`](kpi_tree.md)** — MTTA/MTTR/precision targets, measured against ApexTel's real 252.6-minute P1 baseline.
- **[`constraints.md`](constraints.md)** — hard limits the agent must never cross, whatever its KPIs say.
- **[`metric_tests.py`](metric_tests.py)** — turns both into a CI-runnable pass/fail gate.

## Run it

```bash
cd stages/stage3_measure
python3 metric_tests.py
```

> **Expected:** all 6 constraint checks pass immediately, no model needed.
> The KPI checks print `SKIP` until you've run Stage 10's
> `eval/run_grounding.py` at least once — then re-run this to see the real
> precision number against the 90% target.

**Next:** [Stage 4 · Context](../stage4_context/) — the shared vocabulary
the agent, and this KPI tree, both depend on.

## See it live

Run `adk web` from `stage_agents/` (see the root [README.md](../../README.md#watching-every-stages-own-agent-one-at-a-time)), pick **stage03_measure_agent**, and try the prompt in the root README's table — every tool call it makes is the real code from this folder, not a simulation.
