"""stage02_model_the_decision_agent — Stage 2: Model the decision.

Adds ONE tool: classify_alarm, a thin wrapper around the real, tested
decision tree (stages/stage2_model_the_decision/decision_tree.py). Still no
database, no runbooks — the agent can classify an alarm you describe to it,
but cannot look one up itself.

Try it:
    Prompt:   Classify this alarm: severity 1, site profile Golden Hub,
              service-affecting yes, 14250 subscribers impacted, root cause.
    Expected: It calls classify_alarm, and answers P1, noting a human must
              confirm before the incident opens.

    Prompt:   Classify this alarm: severity 3, site profile Standard,
              service-affecting yes, 950 subscribers impacted, standalone.
    Expected: P3, no escalation needed.

    Prompt:   What alarm did KLCC01 raise at 14:10 UTC?
    Expected: It still doesn't know — it has no database yet. It can only
              classify an alarm you describe to it directly.
"""
import os
import sys
from pathlib import Path

from google.adk.agents import Agent
from google.genai import types

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _shared_tools import classify_alarm  # noqa: E402

MODEL = os.getenv("AGENT_MODEL", "gemini-2.5-flash")

INSTRUCTION = """You are the ApexTel NOC triage assistant, Stage 2. You have one tool,
classify_alarm, which runs the real severity decision tree — no database yet.

If someone describes an alarm's severity, site profile, service-affecting
flag, subscriber impact and RCA classification, call classify_alarm and
report the result plainly, including whether a human must confirm it.

If someone asks about a real alarm by ID or site name without describing its
fields, say plainly that you have no database yet (that's Stage 6) — you can
only classify an alarm someone describes to you directly."""

root_agent = Agent(
    name="stage02_model_the_decision_agent",
    model=MODEL,
    description="Stage 2 (Model the decision): classify_alarm, the severity tree as a tool.",
    instruction=INSTRUCTION,
    tools=[classify_alarm],
    generate_content_config=types.GenerateContentConfig(temperature=0),
)
