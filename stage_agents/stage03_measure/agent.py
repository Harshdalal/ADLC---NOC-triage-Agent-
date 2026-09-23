"""stage03_measure_agent — Stage 3: Measure.

Adds a second tool, kpi_status, reporting the real targets from
stages/stage3_measure/kpi_tree.md — so "is it working" has a number the
agent can cite, not just an opinion.

Try it:
    Prompt:   What's our MTTR target for P1 incidents, and how does that
              compare to today's baseline?
    Expected: It calls kpi_status and answers with the real baseline
              (252.6 minutes) and the target (at least 20% below that).

    Prompt:   Classify this alarm: severity 1, site profile Golden Hub,
              service-affecting yes, 14250 subscribers impacted, root cause.
    Expected: Same as Stage 2 — classify_alarm still works; Stage 3 only adds.
"""
import os
import sys
from pathlib import Path

from google.adk.agents import Agent
from google.genai import types

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _shared_tools import classify_alarm, kpi_status  # noqa: E402

MODEL = os.getenv("AGENT_MODEL", "gemini-2.5-flash")

INSTRUCTION = """You are the ApexTel NOC triage assistant, Stage 3. You have two tools:
classify_alarm (the severity decision tree) and kpi_status (the real
targets this build is measured against).

If someone describes an alarm's fields, call classify_alarm. If someone
asks about targets, MTTA, MTTR, precision, or how "working" is measured,
call kpi_status and answer with its real numbers.

You still have no database — you cannot look up a real alarm by ID."""

root_agent = Agent(
    name="stage03_measure_agent",
    model=MODEL,
    description="Stage 3 (Measure): adds kpi_status — the real KPI targets as a tool.",
    instruction=INSTRUCTION,
    tools=[classify_alarm, kpi_status],
    generate_content_config=types.GenerateContentConfig(temperature=0),
)
