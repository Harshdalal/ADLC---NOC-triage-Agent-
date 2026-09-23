"""The scorecard — Stage 10: Prove.

ADR-10: sign-off requires the scorecard to beat the Stage 5 baseline on
every KPI, not just look good in a live demo. This script runs every
earlier stage's own test suite (no model calls — those are all pure-code
checks) and writes one pass/fail scorecard covering the whole build.

The one thing this script does NOT do automatically is call the real model
(Stage 6's eval/run_grounding.py) — that costs money and needs Vertex AI
access, so it's a separate, explicit step. Run it first if you want the KPI
section to have real numbers instead of "not yet run".

    cd stages/stage10_prove
    python3 ../../eval/run_grounding.py     # optional, needs model access
    python3 scorecard.py
"""
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

KIT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).parent / "SCORECARD.md"

STAGES = [
    ("Stage 2 · Model the decision", "logic_tests.py", KIT / "stages" / "stage2_model_the_decision"),
    ("Stage 3 · Measure",            "metric_tests.py", KIT / "stages" / "stage3_measure"),
    ("Stage 6 · Ground",             None, None),  # handled specially: tests/check_parts.sh at the root
    ("Stage 7 · Operate",            "fire_drill.py", KIT / "stages" / "stage7_operate"),
    ("Stage 8 · Feed back to data",  "contract_tests.py", KIT / "stages" / "stage8_feed_back_to_data"),
    ("Stage 9 · Govern",             "governance_tests.py", KIT / "stages" / "stage9_govern"),
]


def run(cmd, cwd):
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return result.returncode == 0, result.stdout + result.stderr


def main():
    rows = []

    for name, script, cwd in STAGES:
        if script is None:  # Stage 6's own combined check
            ok, output = run(["bash", "tests/check_parts.sh"], KIT)
        else:
            ok, output = run([sys.executable, script], cwd)
        tail = [l for l in output.strip().splitlines() if l.strip()][-1] if output.strip() else ""
        rows.append((name, ok, tail))
        print(f"  {'PASS' if ok else 'FAIL':<6}{name:<32} {tail}")

    baseline_path = KIT / "baseline" / "grounding_v1.json"
    kpi_line = "Not yet run — `python3 eval/run_grounding.py` from the kit root needs Vertex AI access."
    if baseline_path.exists():
        data = json.loads(baseline_path.read_text(encoding="utf-8"))
        summary = data["summary"]
        kpi_line = "  |  ".join(f"{k}: {v['correct']}, {v['tokens']:,} tok" for k, v in summary.items())

    all_pass = all(ok for _, ok, _ in rows)

    lines = [
        "# Scorecard",
        "",
        f"Generated {datetime.now(timezone.utc).isoformat(timespec='seconds')}",
        "",
        "| Stage | Result | Detail |",
        "|---|---|---|",
    ]
    for name, ok, tail in rows:
        lines.append(f"| {name} | {'PASS' if ok else 'FAIL'} | {tail} |")
    lines += [
        "",
        "## Golden-question KPI (Stage 6, against the Stage 5 baseline)",
        "",
        kpi_line,
        "",
        f"## Sign-off gate (ADR-10)",
        "",
        f"**{'READY TO SHIP' if all_pass else 'NOT READY — see the FAILed stage(s) above'}**",
        "",
        "Sign-off requires every stage above to PASS, and (once run) the "
        "semantic-grounded agent to beat both the Stage 5 baseline and the "
        "Stage 3 KPI targets — not just look good in a live demo.",
    ]
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"\n{'READY TO SHIP' if all_pass else 'NOT READY'} — wrote {OUT.relative_to(KIT)}")
    sys.exit(0 if all_pass else 1)


if __name__ == "__main__":
    main()
