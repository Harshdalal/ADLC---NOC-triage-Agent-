# Stage 7 · Operate

A good agent in a notebook is not a good agent in production. This stage
puts versioning, tracing and rollback around the grounded agent, and proves
the rollback actually works with a real fire drill — not a description of
one.

## Files
- **[`versioning_and_tracing.md`](versioning_and_tracing.md)** — how releases are tagged, and what `runs.jsonl` records.
- **[`fire_drill.py`](fire_drill.py)** — injects a real bug, proves it's caught, rolls it back, proves the suite is green again.

## Run it

```bash
cd stages/stage7_operate
python3 fire_drill.py
```

> **Expected:** `DRILL PASSED`, with a detect/rollback/confirm timing
> breakdown. If it ever prints `DRILL FAILED`, don't promote the release —
> that's ADR-7.

**Next:** [Stage 8 · Feed back to data](../stage8_feed_back_to_data/) —
governing what the agent is allowed to read and write, as tightly as its logic.

## See it live

Run `adk web` from `stage_agents/` (see the root [README.md](../../README.md#watching-every-stages-own-agent-one-at-a-time)), pick **stage07_operate_agent**, and try the prompt in the root README's table — every tool call it makes is the real code from this folder, not a simulation.
