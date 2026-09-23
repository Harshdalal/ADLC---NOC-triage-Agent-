"""stage01_frame_agent — Stage 1: Frame.

No tools at all. Proves the plumbing — model access, one round trip — before
any real logic exists. See stages/stage1_frame/decision_card.md.

Try it (after `adk web` from this folder's parent, stage_agents/):
    Prompt:   What alarm did KLCC01 raise at 14:10 UTC?
    Expected: It says plainly that it has no data yet — this is a
              connectivity test, nothing more. It does NOT guess a figure,
              a site name or an alarm ID.
"""
import os

from google.adk.agents import Agent
from google.genai import types

MODEL = os.getenv("AGENT_MODEL", "gemini-2.5-flash")

INSTRUCTION = """You are a placeholder for the ApexTel NOC triage agent. You have no tools and
no access to any data yet — this is Stage 1, proving the plumbing works
before any real logic exists.

If asked about an alarm, a site, or an incident, say plainly that you have no
data yet and this is just a connectivity test. Do not guess or invent a
figure, a site name or an alarm ID."""

root_agent = Agent(
    name="stage01_frame_agent",
    model=MODEL,
    description="Stage 1 (Frame): proves model access. No tools.",
    instruction=INSTRUCTION,
    tools=[],
    generate_content_config=types.GenerateContentConfig(temperature=0),
)
