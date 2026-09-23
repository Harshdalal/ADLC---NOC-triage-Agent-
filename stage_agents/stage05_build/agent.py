"""stage05_build_agent — Stage 5: Build.

Agent v1: Stage 2's tree, Stage 3's KPIs and Stage 4's ontology, composed
into one agent on purpose. This is the exact composition scored in
stages/stage5_build/baseline_score.md — deliberately BEFORE grounding
(Stage 6), so its failures on real-alarm questions are visible and
attributable to "no data," not hidden inside a bigger change.

Try it:
    Prompt:   How many subscribers were impacted by the KLCC01 power
              outage, ALM-2026-8001?
    Expected: It cannot know — no database yet. It says so plainly, and
              does not guess 14,250 even though that number appears
              elsewhere in this kit's documentation (it has no tool that
              would let it retrieve it).

    Prompt:   Classify this alarm: severity 1, site profile Golden Hub,
              service-affecting yes, 14250 subscribers impacted, root cause.
    Expected: Still works — P1, needs human confirmation. Composition adds;
              it doesn't remove anything Stage 2-4 already built.
"""
import os
import sys
from pathlib import Path

from google.adk.agents import Agent
from google.genai import types

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _shared_tools import classify_alarm, kpi_status, lookup_term  # noqa: E402

MODEL = os.getenv("AGENT_MODEL", "gemini-2.5-flash")

INSTRUCTION = """You are the ApexTel NOC triage assistant — Agent v1 (Stage 5: Build).
You have three tools: classify_alarm, kpi_status and lookup_term. You do
NOT have a database or runbooks yet — that is Stage 6.

If someone describes an alarm's fields, classify it. If someone asks about
targets or definitions, use the matching tool. If someone asks about a real
alarm, incident or site by name or ID without describing its fields
directly, say plainly that you have no database yet. Never invent a figure,
a site name or an alarm ID."""

root_agent = Agent(
    name="stage05_build_agent",
    model=MODEL,
    description="Stage 5 (Build): Agent v1 — composed, still ungrounded. The Stage 6 baseline.",
    instruction=INSTRUCTION,
    tools=[classify_alarm, kpi_status, lookup_term],
    generate_content_config=types.GenerateContentConfig(temperature=0),
)
