"""Explanation-by-construction — Stage 9: Govern.

The explanation is built alongside the decision, not reverse-engineered
after the fact by asking a model to justify itself. Every field here comes
from something the gate or the tree actually used — nothing is generated
prose describing a decision after it was already made.

    cd stages/stage9_govern && python3 explanation.py     # runs its own demo
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "stages" / "stage2_model_the_decision"))

from decision_tree import AlarmInput  # noqa: E402
from hitl_gate import GateResult  # noqa: E402


def explain(alarm: AlarmInput, gate_result: GateResult, sources: list[str] | None = None) -> str:
    """A reconstructable explanation: which rule fired, on what input, and
    (if the agent used Stage 6's tools) which records or runbooks backed it up."""
    c = gate_result.classification
    lines = [
        f"Alarm {alarm.alarm_id} at {alarm.site_code} (severity {alarm.severity_num}, "
        f"{alarm.rca_classification}, profile {alarm.site_profile}, "
        f"{alarm.subscribers_impacted} subscribers) classified as {c.priority}.",
        f"Rule fired: {c.reason}",
        f"Gate status: {gate_result.status}"
        + (f", approved by {gate_result.approved_by}" if gate_result.approved_by else ""),
    ]
    if sources:
        lines.append("Evidence used: " + "; ".join(sources))
    else:
        lines.append("Evidence used: decision tree only (no record or runbook lookup for this call).")
    return "\n".join(lines)


if __name__ == "__main__":
    from hitl_gate import approve, submit

    alarm = AlarmInput("ALM-2026-8001", "KLCC01", 1, "Golden Hub", True, 14250, "Root Cause")
    gated = submit(alarm)
    approved = approve(gated, approved_by="j.tan@apextel.example")

    print("Explanation demo\n")
    print(explain(alarm, approved, sources=[
        "alarms_v.alarm_id = ALM-2026-8001 (run_sql, semantic mode)",
        "bbu_power_failure.md#DC Power Failure Initial Response (search_runbook)",
    ]))
