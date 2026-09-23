"""Governance tests — Stage 9: Govern.

Every P1 and every remediation path in the eval set must stop for approval;
any that don't fail the build (this is Stage 3's C1/C2, re-checked here
against the HITL gate directly rather than just the raw decision tree).

    cd stages/stage9_govern && python3 governance_tests.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "stages" / "stage2_model_the_decision"))

from decision_tree import AlarmInput  # noqa: E402
from hitl_gate import GateResult, PendingApproval, approve, final_priority, reject, submit  # noqa: E402
from audit_log import GENESIS_HASH, _hash, record, verify  # noqa: E402

checks = []


def check(name, ok, detail=""):
    checks.append(ok)
    print(f"  {'PASS' if ok else 'FAIL':<6}{name:<58} {detail}")


print("The HITL gate\n")

p1 = submit(AlarmInput("G-P1", "KLCC01", 1, "Golden Hub", True, 14250, "Root Cause"))
check("a P1 is gated as pending_approval", p1.status == "pending_approval")

try:
    final_priority(p1)
    check("cannot read a final priority before approval", False)
except PendingApproval:
    check("cannot read a final priority before approval", True)

approved = approve(p1, approved_by="test-runner")
check("approval requires a named approver", approved.approved_by == "test-runner")
check("approved P1 has a final priority", final_priority(approved) == "P1")

try:
    approve(GateResult(status="pending_approval", classification=p1.classification), approved_by="")
    check("approval without a name is rejected", False)
except ValueError:
    check("approval without a name is rejected", True)

rejected = reject(p1, rejected_by="test-runner")
try:
    final_priority(rejected)
    check("a rejected classification has no final priority", False)
except PendingApproval:
    check("a rejected classification has no final priority", True)

p3 = submit(AlarmInput("G-P3", "BGSR03", 3, "Standard", True, 950, "Standalone"))
check("a P3 does not require approval", p3.status == "auto_applied")
check("auto-applied P3 has an immediate final priority", final_priority(p3) == "P3")

print("\nThe audit trail\n")

log_path = Path(__file__).parent / "audit_log.jsonl"
if log_path.exists():
    log_path.unlink()

record("classification", alarm_id="G-P1", priority="P1")
record("approval", alarm_id="G-P1", approved_by="test-runner")
ok, detail = verify()
check("a fresh two-entry log verifies", ok, detail)

# Tamper with the second entry and confirm it's caught.
lines = log_path.read_text(encoding="utf-8").splitlines()
import json  # noqa: E402
tampered = json.loads(lines[1])
tampered["approved_by"] = "an-attacker"
lines[1] = json.dumps(tampered)
log_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
ok, detail = verify()
check("tampering with an entry is detected", not ok, detail)

log_path.unlink()

print(f"\n{sum(checks)} of {len(checks)} governance checks passed.")
sys.exit(0 if all(checks) else 1)
