"""hello_agent — Stage 1's smoke test.

Proves the plumbing before any real logic exists: can we build an ADK agent,
does it load its instruction, does one round-trip to the model work. No
tools, no database, no MCP server — those come in later stages.

    cd stages/stage1_frame/hello_agent
    adk web              # then ask it: "What alarm did KLCC01 raise at 14:10 UTC?"
    # Expected: it says it doesn't know — it has no tools yet. That's the point.
"""
import os
from pathlib import Path

from google.adk.agents import Agent
from google.genai import types

INSTRUCTION = (Path(__file__).parent / "instruction.txt").read_text(encoding="utf-8")
MODEL = os.getenv("AGENT_MODEL", "gemini-2.5-flash")

root_agent = Agent(
    name="hello_agent",
    model=MODEL,
    description="Stage 1 smoke test: proves model access and one round trip. No tools.",
    instruction=INSTRUCTION,
    tools=[],
    generate_content_config=types.GenerateContentConfig(temperature=0),
)
