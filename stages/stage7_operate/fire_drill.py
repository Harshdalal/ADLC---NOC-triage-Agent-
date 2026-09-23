"""Fire drill — Stage 7: Operate.

ADR-7: a failed fire drill blocks promotion to production, no exceptions.

This drill does the real thing, not a simulation of one: it mutates Stage 2's
decision tree so a Golden-Hub P1 stops being flagged, proves Stage 2's own
test suite catches it, rolls the file back, and proves the suite is green
again — timing every step, the way a real incident would be timed.

    cd stages/stage7_operate && python3 fire_drill.py
"""
import subprocess
import sys
import time
from pathlib import Path

KIT = Path(__file__).resolve().parents[2]
TREE = KIT / "stages" / "stage2_model_the_decision" / "decision_tree.py"
TEST_DIR = KIT / "stages" / "stage2_model_the_decision"

BAD_LINE = "    golden_hub = alarm.site_profile in GOLDEN_HUB_PROFILES"
INJECTED_BUG = "    golden_hub = False  # BUG injected by fire_drill.py"


def run_tests():
    result = subprocess.run([sys.executable, "logic_tests.py"], cwd=TEST_DIR,
                             capture_output=True, text=True)
    return result.returncode == 0, result.stdout


def main():
    original = TREE.read_text(encoding="utf-8")
    if BAD_LINE not in original:
        print(f"Could not find the line to mutate. Has {TREE.name} changed? Aborting drill.")
        sys.exit(1)

    print("=" * 62)
    print("  FIRE DRILL: bad release to the severity decision tree")
    print("=" * 62)

    t0 = time.monotonic()
    print("\n[1] Baseline: confirming the suite is green before we break anything...")
    ok, _ = run_tests()
    print(f"    {'green' if ok else 'RED ALREADY — fix before drilling'}")
    if not ok:
        sys.exit(1)

    print("\n[2] Injecting a bad release: Golden Hub sites no longer escalate to P1...")
    TREE.write_text(original.replace(BAD_LINE, INJECTED_BUG), encoding="utf-8")
    t_deployed = time.monotonic()

    print("\n[3] Running the test suite against the bad release...")
    ok, output = run_tests()
    t_detected = time.monotonic()
    if ok:
        print("    UNEXPECTED: the bad release passed the suite. Rolling back and failing the drill.")
        TREE.write_text(original, encoding="utf-8")
        sys.exit(1)
    failed_lines = [l for l in output.splitlines() if l.strip().startswith("FAIL")]
    print(f"    RED, as expected — {len(failed_lines)} scenario(s) failed:")
    for line in failed_lines[:3]:
        print(f"      {line.strip()}")
    print(f"    Detected in {t_detected - t_deployed:.2f}s")

    print("\n[4] Rolling back...")
    TREE.write_text(original, encoding="utf-8")
    t_rolled_back = time.monotonic()

    print("\n[5] Confirming the suite is green again...")
    ok, _ = run_tests()
    t_confirmed = time.monotonic()
    print(f"    {'green' if ok else 'STILL RED — rollback failed, escalate to a human now'}")

    print("\n" + "=" * 62)
    print("  RESULT")
    print("=" * 62)
    print(f"  Bad release -> detected      : {t_detected - t_deployed:.2f}s")
    print(f"  Detected    -> rolled back    : {t_rolled_back - t_detected:.2f}s")
    print(f"  Rolled back -> confirmed green: {t_confirmed - t_rolled_back:.2f}s")
    print(f"  Total                         : {t_confirmed - t0:.2f}s")
    print()
    if ok:
        print("DRILL PASSED — the bad release was caught and rolled back automatically.")
    else:
        print("DRILL FAILED — rollback did not restore a green suite. Escalate.")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
