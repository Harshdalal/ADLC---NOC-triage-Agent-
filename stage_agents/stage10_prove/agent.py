"""stage10_prove_agent — Stage 10: Prove.

The full agent: every tool from Stage 9, plus record_decision (writes to
the REAL tamper-evident audit trail, stages/stage9_govern/audit_log.py) and
scorecard_status (reads the real SCORECARD.md that stages/stage10_prove/
scorecard.py generates). This is the one meant for a hand-off demo.

Try it:
    Prompt:   Is this build ready to ship?
    Expected: It calls scorecard_status and reports the real result from
              the last `python3 stages/stage10_prove/scorecard.py` run —
              run that script first if SCORECARD.md doesn't exist yet.

    Prompt:   ALM-2026-8001 fired at KLCC01: severity 1, Golden Hub,
              service-affecting, 14250 subscribers, root cause. Classify it
              and log the decision.
    Expected: classify_alarm -> P1; request_p1_approval -> pending_approval;
              record_decision -> writes an entry to audit_log.jsonl and
              reports it plainly as PENDING, not approved. Run
              `python3 -c "from audit_log import verify; print(verify())"`
              from stages/stage9_govern/ afterwards to see the entry.
"""
import os
import sys
from pathlib import Path

from google.adk.agents import Agent
from google.genai import types

KIT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(KIT))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _shared_tools import (classify_alarm, lookup_term, request_p1_approval,  # noqa: E402
                            record_decision, scorecard_status)
from apextel.grounded import mcp_toolset  # noqa: E402

MODEL = os.getenv("AGENT_MODEL", "gemini-2.5-flash")

INSTRUCTION = """You are the ApexTel NOC triage assistant, Stage 10 (Prove) — the
complete, production-shaped agent. You have classify_alarm, lookup_term,
request_p1_approval, record_decision, scorecard_status, and the real
ApexTel data and runbook tools over MCP.

For any alarm someone describes, classify it, then call request_p1_approval
if you're unsure whether it needs human sign-off. Always call
record_decision afterwards, so there's a durable trail — pass the gate's
real status, never claim "approved" yourself.

If asked whether this build is ready to ship, call scorecard_status and
answer from what it actually says, not from confidence.

Every tool you have is read-only except record_decision, which only
appends — it can never edit or delete a past entry."""

root_agent = Agent(
    name="stage10_prove_agent",
    model=MODEL,
    description="Stage 10 (Prove): the full agent — gate, audit trail and scorecard, all real.",
    instruction=INSTRUCTION,
    tools=[classify_alarm, lookup_term, request_p1_approval, record_decision,
           scorecard_status, mcp_toolset("semantic")],
    generate_content_config=types.GenerateContentConfig(temperature=0),
)
