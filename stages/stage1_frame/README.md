# Stage 1 · Frame

Before any code, three things get written down and signed off:

1. **[`decision_card.md`](decision_card.md)** — the job, its inputs, its output.
2. **[`autonomy_table.md`](autonomy_table.md)** — ADR-1: what the agent may do alone, and what a human must click.
3. **[`hello_agent/`](hello_agent/)** — a stub agent with no tools, proving the plumbing works.

## Run it

```bash
# Structural check, no model call, no cost:
cd stages/stage1_frame
python3 smoke_test.py

# The real round-trip (needs Vertex AI access — see the root README's setup steps):
cd hello_agent
adk web
# ask it anything about an alarm — it should say plainly that it has no data yet
```

## What this stage delivers
A signed-off decision card, an autonomy table, and a hello-agent that runs
end to end. Nothing here talks to real ApexTel data — that starts at Stage 4
(Context) and is fully wired up by Stage 6 (Ground).

**Next:** [Stage 2 · Model the decision](../stage2_model_the_decision/) turns
the decision card into an explicit, testable severity tree.

## See it live

Run `adk web` from `stage_agents/` (see the root [README.md](../../README.md#watching-every-stages-own-agent-one-at-a-time)), pick **stage01_frame_agent**, and try the prompt in the root README's table — every tool call it makes is the real code from this folder, not a simulation.
