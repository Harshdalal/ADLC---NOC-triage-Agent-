# Stage 4 · Context

The shared vocabulary the agent, the tests and the humans all use the same
way. This is where a "severity" and a "priority" stop being interchangeable
words and become two named, distinct fields.

## Files
- **[`../../ontology.yaml`](../../ontology.yaml)** — the ontology itself, at
  the repository root because Stage 6's `apextel/kb_search.py` reads its
  `synonyms` section directly, and `tests/test_ontology.py` validates data
  against it. This is Context, used live from Stage 6 onward.
- **[`../../apextel/semantic_layer.yaml`](../../apextel/semantic_layer.yaml)** — the ontology's words, applied to the actual database views.
- **[`tool_catalog.md`](tool_catalog.md)** — what the agent is told about `describe_data`, `run_sql` and `search_runbook`.
- **[`single_vs_multi_agent.md`](single_vs_multi_agent.md)** — ADR-4.

## Why the ontology lives at the root, not in this folder
Every other stage folder in this kit is documentation plus small,
self-contained scripts. Stage 4 is different: its artefact is *load-bearing*
— real code imports it at runtime (`apextel/kb_search.py`,
`apextel/sql.py` via `semantic_layer.yaml`, `tests/test_ontology.py`).
Moving it here would mean either duplicating it or breaking those imports,
so this folder documents it in place instead of relocating it.

## Check it
```bash
cd ../..   # the kit root
python3 tests/test_ontology.py
```

**Next:** [Stage 5 · Build](../stage5_build/).

## See it live

Run `adk web` from `stage_agents/` (see the root [README.md](../../README.md#watching-every-stages-own-agent-one-at-a-time)), pick **stage04_context_agent**, and try the prompt in the root README's table — every tool call it makes is the real code from this folder, not a simulation.
