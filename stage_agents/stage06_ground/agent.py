"""stage06_ground_agent — Stage 6: Ground.

Agent v1, now grounded: the same classify_alarm/kpi_status/lookup_term
tools as Stage 5, PLUS the real ApexTel MCP server (describe_data, run_sql,
search_runbook), in semantic mode. This is the moment the agent can finally
answer a real question about a real alarm.

Try it:
    Prompt:   How many subscribers were impacted by the KLCC01 power
              outage, ALM-2026-8001?
    Expected: It calls describe_data, then run_sql, and answers 14,250 —
              the exact question Stage 5's agent could not answer.

    Prompt:   What is the response procedure for a BBU DC Power Off alarm?
    Expected: It calls search_runbook and cites bbu_power_failure.md.

    Prompt:   What is the root cause of the KLCC01 outage, and what does
              the runbook say to do next?
    Expected: It uses BOTH run_sql (root cause: rectifier module failure)
              and search_runbook (the hot-swap procedure).
"""
import os
import sys
from pathlib import Path

from google.adk.agents import Agent
from google.genai import types

KIT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(KIT))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _shared_tools import classify_alarm, kpi_status, lookup_term  # noqa: E402
from apextel.grounded import mcp_toolset  # noqa: E402

MODEL = os.getenv("AGENT_MODEL", "gemini-2.5-flash")
INSTRUCTION = (KIT / "apextel" / "instructions" / "noc_assistant.txt").read_text(encoding="utf-8")

root_agent = Agent(
    name="stage06_ground_agent",
    model=MODEL,
    description="Stage 6 (Ground): Agent v1 + the real ApexTel MCP server, semantic mode.",
    instruction=INSTRUCTION,
    tools=[classify_alarm, kpi_status, lookup_term, mcp_toolset("semantic")],
    generate_content_config=types.GenerateContentConfig(temperature=0),
)
