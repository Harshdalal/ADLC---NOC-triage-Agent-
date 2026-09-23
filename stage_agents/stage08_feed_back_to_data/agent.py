"""stage08_feed_back_to_data_agent — Stage 8: Feed back to data.

Same as Stage 7, plus data_contract_summary — reads the real
stages/stage8_feed_back_to_data/data_contracts.yaml, so the agent can state
its own limits (read-only, 50 rows, 3 passages) instead of you having to
trust the instruction alone.

Try it:
    Prompt:   Can you update the incident's status to closed?
    Expected: It explains, citing its own contract, that every tool is
              read-only (ADR-8) — it has no way to write anything.

    Prompt:   What are the limits on the queries you can run?
    Expected: It calls data_contract_summary and reports: one SELECT/WITH
              statement, at most 50 rows, no write keywords.
"""
import os
import sys
from pathlib import Path

from google.adk.agents import Agent
from google.genai import types

KIT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(KIT))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _shared_tools import classify_alarm, kpi_status, lookup_term, data_contract_summary  # noqa: E402
from apextel.grounded import mcp_toolset  # noqa: E402

MODEL = os.getenv("AGENT_MODEL", "gemini-2.5-flash")
INSTRUCTION = (KIT / "apextel" / "instructions" / "noc_assistant.txt").read_text(encoding="utf-8") + \
    "\n\nYou also have data_contract_summary — use it if asked what you are allowed to " \
    "read or write. Every tool is read-only; you have no way to change a record."

root_agent = Agent(
    name="stage08_feed_back_to_data_agent",
    model=MODEL,
    description="Stage 8 (Feed back to data): adds data_contract_summary — the contract as a tool.",
    instruction=INSTRUCTION,
    tools=[classify_alarm, kpi_status, lookup_term, data_contract_summary, mcp_toolset("semantic")],
    generate_content_config=types.GenerateContentConfig(temperature=0),
)
