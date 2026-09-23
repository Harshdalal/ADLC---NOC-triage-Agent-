# Tool catalog — what the agent is told about its own tools

**Stage 4 · Context** — ADK tool-description conventions: each tool is
described for the *model*, not the DBA. These are the real descriptions used
by `mcp_server/apextel_mcp.py` (Stage 6); this document is the human-readable
version, kept next to the ontology it's derived from.

| Tool | Signature | What the agent is told | What it must not be used for |
|---|---|---|---|
| `describe_data` | `() -> str` | "Describe the ApexTel data: three views about alarms, incidents and sites, with what every column means. Call this before writing SQL." (semantic mode) or "List the database tables and their columns." (raw mode) | Never returns actual rows — structure only |
| `run_sql` | `(query: str) -> str` | "Run one read-only SQL SELECT query against the ApexTel data and return the rows. Only the tables or views listed by describe_data may be used. At most 50 rows come back." | Anything that isn't a single `SELECT`/`WITH`; anything outside the current mode's allowed tables (Stage 6's guardrail) |
| `search_runbook` | `(question: str) -> str` | "Find the passages of ApexTel's runbooks most relevant to a question: BBU power failure, alarm correlation, transmission failover, ATS emergency maintenance and diesel generator SOP. Each passage names its source." | Never returns a full document — top 3 passages only (the context budget, Stage 6 §10) |

## Why the description matters as much as the code
The model decides *when* to call a tool from its description alone — it
never reads `sql.py`. A vague description ("run a query") gets called
wrongly or not at all; a precise one ("read-only, this mode's tables only,
50 rows max") sets the model's expectations correctly before it ever writes
a line of SQL.

**Next:** [`single_vs_multi_agent.md`](single_vs_multi_agent.md) — the other
half of Stage 4's decision.
