"""ApexTel's data and runbooks, served over MCP (ADLC Stage 6: Ground).

MCP (Model Context Protocol) is a standard way for an agent to reach tools
that another team runs. This server is that other team: it owns the alarm
database and the runbook documents, decides what is exposed, and enforces its
own rules. Any agent can connect to it; none needs to know how the data is
stored.

It offers three tools:
    describe_data    what data exists, and what it means
    run_sql          one read-only query, checked before it runs
    search_runbook   the runbook passages most relevant to a question

The mode is set when an agent starts the server:
    APEXTEL_GROUNDING=raw        raw tables, bare column names
    APEXTEL_GROUNDING=semantic   ontology-aligned views, with descriptions

Agents start it themselves over stdio. To try it on its own:
    python3 mcp_server/apextel_mcp.py        (it then waits for an MCP client)
"""
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mcp.server.fastmcp import FastMCP  # noqa: E402

from apextel import kb_search, sql  # noqa: E402

MODE = os.getenv("APEXTEL_GROUNDING", "semantic")
server = FastMCP("apextel")

RAW_DESCRIBE = "List the database tables and their columns. Call this before writing SQL."
SEMANTIC_DESCRIBE = ("Describe the ApexTel data: three views about alarms, incidents and sites, "
                     "with what every column means. Call this before writing SQL.")


@server.tool(description=SEMANTIC_DESCRIBE if MODE == "semantic" else RAW_DESCRIBE)
def describe_data() -> str:
    return json.dumps(sql.describe(MODE), indent=1)


@server.tool()
def run_sql(query: str) -> str:
    """Run one read-only SQL SELECT query against the ApexTel data and return the rows.
    Only the tables or views listed by describe_data may be used. At most 50 rows come back."""
    return json.dumps(sql.run(query, MODE), default=str)


@server.tool()
def search_runbook(question: str) -> str:
    """Find the passages of ApexTel's runbooks most relevant to a question: BBU power
    failure, alarm correlation, transmission failover, ATS emergency maintenance and
    diesel generator SOP. Each passage names its source, so answers can cite it."""
    return json.dumps(kb_search.search(question), indent=1)


if __name__ == "__main__":
    server.run()
