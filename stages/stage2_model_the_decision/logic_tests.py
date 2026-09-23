"""Logic tests for the severity decision tree — Stage 2: Model the decision.

20 scenarios in, expected branch out, no LLM. Run:

    cd stages/stage2_model_the_decision && python3 logic_tests.py

The KLCC01 / BKBT02 cascade (10 Aug 2026) is scenarios 1-3, exactly as it
appears in the real ApexTel data used from Stage 6 onward.
"""
import sys

from decision_tree import AlarmInput, classify

checks = []


def case(name, alarm, expected_priority, expected_escalate):
    result = classify(alarm)
    ok = result.priority == expected_priority and result.escalate_to_human == expected_escalate
    checks.append(ok)
    print(f"  {'PASS' if ok else 'FAIL':<6}{name:<52} got {result.priority}"
          f"{'*' if result.escalate_to_human else ' '}  ({result.reason})")


print("Scenarios 1-3: the real KLCC01 / BKBT02 cascade\n")

case("ALM-2026-8001, KLCC01 BBU DC Power Off",
     AlarmInput("ALM-2026-8001", "KLCC01", 1, "Golden Hub", True, 14250, "Root Cause"),
     "P1", True)

case("ALM-2026-8002, KLCC01 Cell Down (symptom of 8001)",
     AlarmInput("ALM-2026-8002", "KLCC01", 1, "Golden Hub", True, 4200, "Symptom"),
     "P1", True)

case("ALM-2026-8003, BKBT02 cascading transmission fault",
     AlarmInput("ALM-2026-8003", "BKBT02", 2, "Silver", True, 9100, "Cascading"),
     "P2", False)

print("\nScenarios 4-20: coverage of every branch\n")

case("Critical, Golden Hub, small impact -> still P1 on site profile alone",
     AlarmInput("T04", "KLCC01", 1, "Golden Hub", True, 10, "Root Cause"), "P1", True)

case("Critical, not Golden Hub, huge impact -> P1 on impact alone",
     AlarmInput("T05", "BGSR03", 1, "Standard", True, 9000, "Root Cause"), "P1", True)

case("Critical, not Golden Hub, small impact -> P2, no escalation",
     AlarmInput("T06", "BGSR03", 1, "Standard", True, 200, "Root Cause"), "P2", False)

case("Major, service-affecting -> P2",
     AlarmInput("T07", "KLSN15", 2, "Standard", True, 3200, "Symptom"), "P2", False)

case("Minor, service-affecting -> P3",
     AlarmInput("T08", "BGSR03", 3, "Standard", True, 950, "Standalone"), "P3", False)

case("Critical but NOT service-affecting -> P4, no escalation",
     AlarmInput("T09", "KLCC01", 1, "Golden Hub", False, 0, "Root Cause"), "P4", False)

case("Major but NOT service-affecting -> P4",
     AlarmInput("T10", "BKBT02", 2, "Silver", False, 0, "Symptom"), "P4", False)

case("Transient always P4, regardless of severity or site",
     AlarmInput("T11", "KLCC01", 1, "Golden Hub", True, 14250, "Transient"), "P4", False)

case("Transient beats even a Golden Hub P1-looking alarm",
     AlarmInput("T12", "KLCC01", 1, "Golden Hub", True, 20000, "Transient"), "P4", False)

case("Exactly at the large-impact threshold (5000) -> P1",
     AlarmInput("T13", "BGSR03", 1, "Standard", True, 5000, "Root Cause"), "P1", True)

case("One below the large-impact threshold (4999), not Golden Hub -> P2",
     AlarmInput("T14", "BGSR03", 1, "Standard", True, 4999, "Root Cause"), "P2", False)

case("Cascading, Critical, Golden Hub -> still evaluated as P1 (Cascading is not exempt)",
     AlarmInput("T15", "KLCC01", 1, "Golden Hub", True, 8000, "Cascading"), "P1", True)

case("Minor at a Golden Hub, service-affecting -> P3, site profile does not override severity 3",
     AlarmInput("T16", "KLCC01", 3, "Golden Hub", True, 500, "Standalone"), "P3", False)

case("Major at a Golden Hub -> P2, Golden Hub only escalates Critical alarms",
     AlarmInput("T17", "KLCC01", 2, "Golden Hub", True, 500, "Symptom"), "P2", False)

case("Standard site, Critical, zero subscribers, not Golden Hub -> P2",
     AlarmInput("T18", "KLSN15", 1, "Standard", True, 0, "Root Cause"), "P2", False)

case("Silver profile is not Golden Hub -> does not trigger the site-profile P1 path",
     AlarmInput("T19", "BKBT02", 1, "Silver", True, 100, "Root Cause"), "P2", False)

case("Symptom classification does not change the priority math",
     AlarmInput("T20", "BGSR03", 2, "Standard", True, 3200, "Symptom"), "P2", False)

print(f"\n{sum(checks)} of {len(checks)} scenarios passed.")
print("\nALL SCENARIOS PASS" if all(checks) else "SOME SCENARIOS FAILED")
sys.exit(0 if all(checks) else 1)
