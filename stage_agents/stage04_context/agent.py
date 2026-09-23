"""stage04_context_agent — Stage 4: Context.

Adds a third tool, lookup_term, reading the real ontology.yaml definitions
— the shared vocabulary Stage 6's tool descriptions and this agent's
instruction both draw from.

Try it:
    Prompt:   What's the difference between severity and priority?
    Expected: It calls lookup_term twice (or once with both) and explains:
              severity is per-alarm (Critical/Major/Minor, no fourth level);
              priority is the incident's handling level (P1-P4), decided
              when the ticket opens, and the two don't always move together.

    Prompt:   What does "Golden Hub" mean?
    Expected: It calls lookup_term("site_profile") and explains the SLA tier
              concept, citing ontology.yaml.
"""
import os
import sys
from pathlib import Path

from google.adk.agents import Agent
from google.genai import types

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _shared_tools import classify_alarm, kpi_status, lookup_term  # noqa: E402

MODEL = os.getenv("AGENT_MODEL", "gemini-2.5-flash")

INSTRUCTION = """You are the ApexTel NOC triage assistant, Stage 4. You have three tools:
classify_alarm, kpi_status, and lookup_term (the shared ontology).

If someone asks what a word means, or asks you to distinguish two terms
(e.g. severity vs priority), call lookup_term for each and answer from the
ontology's own words — do not improvise a definition.

You still have no database — you cannot look up a real alarm by ID."""

root_agent = Agent(
    name="stage04_context_agent",
    model=MODEL,
    description="Stage 4 (Context): adds lookup_term — the shared ontology as a tool.",
    instruction=INSTRUCTION,
    tools=[classify_alarm, kpi_status, lookup_term],
    generate_content_config=types.GenerateContentConfig(temperature=0),
)
