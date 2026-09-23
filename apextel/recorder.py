"""Recorder: writes model calls (tokens) and turns (seconds) to runs.jsonl.

This is what makes context cost visible: a bigger context means more input
tokens per call. It does not change what the agent does; the SQL guardrail and
the tool boundary still decide everything. This file only watches and writes
one JSON line per event:

    model_call   one call to Gemini, with its input and output tokens
    turn         one user message answered, with how many seconds it took
"""
import json
import time
from datetime import datetime, timezone
from pathlib import Path

RUNS_FILE = Path(__file__).resolve().parents[1] / "runs.jsonl"

_turn_started = {}  # invocation id -> start time


def _session_id(context):
    """The chat session id. Works across ADK versions."""
    session = getattr(context, "session", None)
    if session is None:
        invocation = getattr(context, "_invocation_context", None)
        session = getattr(invocation, "session", None)
    return getattr(session, "id", None) or getattr(context, "invocation_id", "unknown")


def _write(context, event, **fields):
    line = {
        "time": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "session": _session_id(context),
        "agent": getattr(context, "agent_name", None),
        "event": event,
        **fields,
    }
    with open(RUNS_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(line) + "\n")


def before_agent_callback(callback_context):
    _turn_started[callback_context.invocation_id] = time.monotonic()
    return None


def after_agent_callback(callback_context):
    started = _turn_started.pop(callback_context.invocation_id, None)
    if started is not None:
        _write(callback_context, "turn", seconds=round(time.monotonic() - started, 2))
    return None


def after_model_callback(callback_context, llm_response):
    usage = getattr(llm_response, "usage_metadata", None)
    if usage is None or getattr(llm_response, "partial", False):
        return None  # streamed pieces carry no final count
    input_tokens = usage.prompt_token_count or 0
    output_tokens = (usage.candidates_token_count or 0) + (usage.thoughts_token_count or 0)
    _write(callback_context, "model_call", input_tokens=input_tokens, output_tokens=output_tokens)
    return None
