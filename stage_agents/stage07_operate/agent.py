"""stage07_operate_agent — Stage 7: Operate.

Same as Stage 6, plus release_info — a tool reporting this build's version
and its last fire-drill result (see stages/stage7_operate/fire_drill.py).
Every model call is also traced to runs.jsonl by apextel/recorder.py,
wired in via mcp_toolset — that part isn't a tool, it happens automatically.

Try it:
    Prompt:   What version of the triage agent am I talking to, and did it
              pass its last fire drill?
    Expected: It calls release_info and reports the version tag and PASSED.

    Prompt:   How many subscribers were impacted by the KLCC01 power
              outage, ALM-2026-8001?
    Expected: Still works exactly as Stage 6 — 14,250, via run_sql.
"""
import os
import sys
from pathlib import Path

from google.adk.agents import Agent
from google.genai import types

KIT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(KIT))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _shared_tools import classify_alarm, kpi_status, lookup_term, release_info  # noqa: E402
from apextel.grounded import mcp_toolset  # noqa: E402

MODEL = os.getenv("AGENT_MODEL", "gemini-2.5-flash")
INSTRUCTION = (KIT / "apextel" / "instructions" / "noc_assistant.txt").read_text(encoding="utf-8") + \
    "\n\nYou also have release_info — use it if asked about your version or operational status."

root_agent = Agent(
    name="stage07_operate_agent",
    model=MODEL,
    description="Stage 7 (Operate): adds release_info — versioning and fire-drill status.",
    instruction=INSTRUCTION,
    tools=[classify_alarm, kpi_status, lookup_term, release_info, mcp_toolset("semantic")],
    generate_content_config=types.GenerateContentConfig(temperature=0),
)
