"""The human-in-the-loop gate — Stage 9: Govern.

Wraps Stage 2's classify() so that anything requiring a human (every P1,
Stage 1's ADR-1) is physically blocked from taking effect until a named
person approves it. This is not a suggestion the agent can talk itself out
of — it's a separate function the agent's output has to pass through.

    cd stages/stage9_govern && python3 hitl_gate.py     # runs its own demo
"""
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

KIT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(KIT / "stages" / "stage2_model_the_decision"))

from decision_tree import AlarmInput, Classification, classify  # noqa: E402


@dataclass
class GateResult:
    status: str              # "auto_applied" or "pending_approval" or "approved" or "rejected"
    classification: Classification
    approved_by: Optional[str] = None


class PendingApproval(Exception):
    """Raised when a caller tries to use a gated classification before it's approved."""


def submit(alarm: AlarmInput) -> GateResult:
    """The only entry point an agent (or a script) may use. Never returns an
    action the caller can just run — a gated result must go through
    approve() or reject() before it counts as final."""
    result = classify(alarm)
    if result.escalate_to_human:
        return GateResult(status="pending_approval", classification=result)
    return GateResult(status="auto_applied", classification=result)


def approve(gate_result: GateResult, approved_by: str) -> GateResult:
    if gate_result.status != "pending_approval":
        raise ValueError(f"Nothing to approve — status is {gate_result.status!r}, not pending_approval.")
    if not approved_by:
        raise ValueError("approved_by is required — the audit trail must name a person.")
    return GateResult(status="approved", classification=gate_result.classification, approved_by=approved_by)


def reject(gate_result: GateResult, rejected_by: str) -> GateResult:
    if gate_result.status != "pending_approval":
        raise ValueError(f"Nothing to reject — status is {gate_result.status!r}, not pending_approval.")
    return GateResult(status="rejected", classification=gate_result.classification, approved_by=rejected_by)


def final_priority(gate_result: GateResult) -> str:
    """The priority a downstream system may actually act on. Raises if the
    gate hasn't cleared yet — this is what makes the gate load-bearing
    rather than decorative."""
    if gate_result.status == "pending_approval":
        raise PendingApproval(f"{gate_result.classification.priority} is not final until a human approves it.")
    if gate_result.status == "rejected":
        raise PendingApproval("This classification was rejected. It has no final priority.")
    return gate_result.classification.priority


if __name__ == "__main__":
    print("HITL gate demo\n")

    p1_alarm = AlarmInput("ALM-2026-8001", "KLCC01", 1, "Golden Hub", True, 14250, "Root Cause")
    gated = submit(p1_alarm)
    print(f"  submit(ALM-2026-8001) -> {gated.status}")
    try:
        final_priority(gated)
        print("  UNEXPECTED: got a final priority before approval")
    except PendingApproval as e:
        print(f"  correctly blocked: {e}")

    approved = approve(gated, approved_by="j.tan@apextel.example")
    print(f"  approve(...) -> {approved.status}, by {approved.approved_by}")
    print(f"  final_priority(...) -> {final_priority(approved)}")

    print()
    p3_alarm = AlarmInput("ALM-2026-7880", "BGSR03", 3, "Standard", True, 950, "Standalone")
    gated2 = submit(p3_alarm)
    print(f"  submit(ALM-2026-7880) -> {gated2.status}")
    print(f"  final_priority(...) -> {final_priority(gated2)}  (no approval needed for P3)")
