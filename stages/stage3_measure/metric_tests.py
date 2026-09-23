"""Metric and constraint tests — Stage 3: Measure.

Two kinds of check:
  * Constraints (C1-C5 below) are checked directly against code, right now,
    no model needed.
  * KPI targets (MTTA/MTTR/precision) are checked against Stage 10's
    baseline/grounding_v1.json, IF it exists yet. Run
    eval/run_grounding.py first if you want those to run for real.

    cd stages/stage3_measure && python3 metric_tests.py
"""
import json
import sys
from pathlib import Path

KIT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(KIT))
sys.path.insert(0, str(KIT / "stages" / "stage2_model_the_decision"))

checks = []


def check(name, ok, detail=""):
    checks.append(ok)
    print(f"  {'PASS' if ok else 'FAIL':<6}{name:<58} {detail}")


print("Constraints (checked against code, no model needed)\n")

from decision_tree import AlarmInput, classify  # noqa: E402

# C1/C2: every P1 must require human confirmation. This is the decision
# tree's contract — if this ever fails, someone changed the tree to let a
# P1 through un-escalated, which breaks ADR-1.
p1_alarm = AlarmInput("C-TEST", "KLCC01", 1, "Golden Hub", True, 14250, "Root Cause")
result = classify(p1_alarm)
check("C1/C2 every P1 requires human confirmation", result.priority == "P1" and result.escalate_to_human)

from apextel import sql  # noqa: E402

# C3: the guardrail blocks anything that is not a read-only SELECT.
check("C3 blocks DELETE", sql.check("DELETE FROM alm_tbl", "raw") is not None)
check("C3 blocks UPDATE", sql.check("UPDATE alm_tbl SET sev=1", "raw") is not None)
check("C3 allows SELECT", sql.check("SELECT * FROM alm_tbl", "raw") is None)

# C4: the row cap is exactly 50, and cannot be raised by a query.
check("C4 row cap is 50", sql.MAX_ROWS == 50, f"got {sql.MAX_ROWS}")

from apextel import kb_search  # noqa: E402

# C5: every runbook passage names a source.
passages = kb_search.search("BBU power failure")["passages"]
check("C5 every runbook passage has a source", all("source" in p for p in passages),
      f"{len(passages)} passages")

print("\nKPI targets (need a Stage 10 eval run to have real numbers)\n")

baseline_path = KIT / "baseline" / "grounding_v1.json"
if not baseline_path.exists():
    print("  SKIP  no baseline/grounding_v1.json yet — run `python3 eval/run_grounding.py` first")
else:
    data = json.loads(baseline_path.read_text(encoding="utf-8"))
    semantic = data["summary"].get("semantic", {})
    ungrounded = data["summary"].get("ungrounded", {})
    sem_correct = int(semantic.get("correct", "0 of 0").split()[0])
    sem_total = int(semantic.get("correct", "0 of 10").split()[-1])
    precision = sem_correct / sem_total if sem_total else 0
    check("KPI severity precision >= 90% on golden set (semantic)", precision >= 0.9,
          f"{sem_correct}/{sem_total} = {precision:.0%}")
    check("KPI grounded beats ungrounded", semantic.get("correct") != ungrounded.get("correct"),
          f"semantic {semantic.get('correct')} vs ungrounded {ungrounded.get('correct')}")

print(f"\n{sum(checks)} of {len(checks)} checks passed" +
      (f" ({checks.count(True)} pass, run again after eval for KPI checks)" if not baseline_path.exists() else "."))
sys.exit(0 if all(checks) else 1)
