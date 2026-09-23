# Stage 8 · Feed back to data

The Stage 6 data spec, rewritten as the agent's own tool contracts — a
promise: given these inputs, this exact shape of output, nothing else. The
agent can't renegotiate it at runtime, and this stage checks that the real
code still keeps that promise.

## Files
- **[`data_contracts.yaml`](data_contracts.yaml)** — the contract for `describe_data`, `run_sql` and `search_runbook`. ADR-8: every tool is read-only; a write path is reserved but not implemented.
- **[`contract_tests.py`](contract_tests.py)** — runs the real Stage 6 code against this file.

## Run it

```bash
cd stages/stage8_feed_back_to_data
python3 contract_tests.py
```

> **Expected:** `19 of 19 contract checks passed.` — every forbidden SQL
> keyword really is blocked, every response shape matches what's declared,
> and the row/passage limits in the code match the numbers written down here.

## Why this is a separate stage from Stage 6
Stage 6 proves grounding *works*. Stage 8 proves the *promise* behind it
doesn't quietly drift — that six months from now, nobody loosens `MAX_ROWS`
or adds a write path without that change showing up here as a failing test.

**Next:** [Stage 9 · Govern](../stage9_govern/) — the human checkpoint on
top of all of it.

## See it live

Run `adk web` from `stage_agents/` (see the root [README.md](../../README.md#watching-every-stages-own-agent-one-at-a-time)), pick **stage08_feed_back_to_data_agent**, and try the prompt in the root README's table — every tool call it makes is the real code from this folder, not a simulation.
