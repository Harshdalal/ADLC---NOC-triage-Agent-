"""Extracts v1_ungrounded's score from a full eval run into baseline_score.md.

ADR-5: the eval set (tests/golden_questions.csv, eval/grounding_questions.yaml)
is fixed before v1 is built, so this baseline can't be tuned to flatter the
first attempt. Every later stage — Stage 6's grounding comparison, Stage 10's
sign-off gate — is measured against the number this script writes down.

    cd stages/stage5_build
    python3 ../../eval/run_grounding.py     # run this first, from the kit root
    python3 record_baseline.py
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

KIT = Path(__file__).resolve().parents[2]
BASELINE = KIT / "baseline" / "grounding_v1.json"
OUT = Path(__file__).parent / "baseline_score.md"


def main():
    if not BASELINE.exists():
        print(f"No {BASELINE.relative_to(KIT)} yet. Run this first, from the kit root:")
        print("    python3 eval/run_grounding.py")
        sys.exit(1)

    data = json.loads(BASELINE.read_text(encoding="utf-8"))
    ungrounded = data["summary"]["ungrounded"]
    rows = data["questions"]["ungrounded"]

    lines = [
        "# Baseline score — Agent v1 (ungrounded)",
        "",
        f"Recorded from `baseline/grounding_v1.json`, generated {data['recorded_at']}, "
        f"model `{data['model']}`.",
        "",
        f"**{ungrounded['correct']} correct, {ungrounded['tokens']:,} tokens total.**",
        "",
        "This is the number every later stage is measured against: Stage 6's grounded "
        "variants must beat it on correctness; Stage 10's scorecard must beat it (and "
        "the Stage 3 KPI targets) before sign-off.",
        "",
        "| Question | Needs | Correct? | Cause if wrong |",
        "|---|---|---|---|",
    ]
    for r in rows:
        lines.append(f"| {r['id']} | {r['needs']} | {'yes' if r['correct'] else 'no'} | {r['cause'] or '—'} |")
    lines += ["", f"_Written by record_baseline.py, {datetime.now(timezone.utc).isoformat(timespec='seconds')}_"]

    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUT.relative_to(KIT)}")


if __name__ == "__main__":
    main()
