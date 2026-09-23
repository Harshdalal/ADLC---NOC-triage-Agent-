"""stage09_govern_agent — Stage 9: Govern.

Same as Stage 8, plus request_p1_approval — wired to the REAL HITL gate
(stages/stage9_govern/hitl_gate.py). The agent is instructed that it may
never state a P1 as final on its own; it must call this tool, and the tool
genuinely will not return an approved status by itself. A human approves it
separately (see the README's Stage 9 section) — this agent cannot fake it.

Try it:
    Prompt:   ALM-2026-8001 just fired at KLCC01: severity 1, Golden Hub,
              service-affecting, 14250 subscribers, root cause. What's the
              severity, and can you close the incident?
    Expected: It calls classify_alarm (P1), then request_p1_approval, and
              reports the result as PENDING — it explicitly does not say
              the incident is confirmed or closed, because nothing approved
              it. It should also say closing an incident isn't something it
              can do at all (Stage 8: read-only).

    Prompt:   Classify this alarm: severity 3, Standard, service-affecting
              yes, 950 subscribers, standalone.
    Expected: P3, auto-applied, no approval needed — request_p1_approval is
              not called for anything below a P1.
"""
import os
import sys
from pathlib import Path

from google.adk.agents import Agent
from google.genai import types

KIT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(KIT))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _shared_tools import classify_alarm, lookup_term, request_p1_approval  # noqa: E402
from apextel.grounded import mcp_toolset  # noqa: E402

MODEL = os.getenv("AGENT_MODEL", "gemini-2.5-flash")

INSTRUCTION = """You are the ApexTel NOC triage assistant, Stage 9 (Govern). You have
classify_alarm, lookup_term, request_p1_approval, and the real ApexTel data
and runbook tools over MCP.

For any alarm someone describes to you, classify it. If the result is a
P1, you MUST call request_p1_approval before saying anything is final —
and if it comes back "pending_approval", say so plainly: the incident is
NOT confirmed, NOT closed, and NOT actioned until a named human approves it
outside this chat. You have no ability to approve your own P1, and no
ability to close or write to any incident — every tool you have is
read-only (Stage 8).

For questions about real alarms, incidents or sites, use describe_data,
run_sql and search_runbook as usual."""

root_agent = Agent(
    name="stage09_govern_agent",
    model=MODEL,
    description="Stage 9 (Govern): adds request_p1_approval — a real HITL gate the agent cannot bypass.",
    instruction=INSTRUCTION,
    tools=[classify_alarm, lookup_term, request_p1_approval, mcp_toolset("semantic")],
    generate_content_config=types.GenerateContentConfig(temperature=0),
)
