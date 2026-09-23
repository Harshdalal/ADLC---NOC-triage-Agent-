# Scorecard

Generated 2026-09-22T16:27:05+00:00

| Stage | Result | Detail |
|---|---|---|
| Stage 2 · Model the decision | PASS | ALL SCENARIOS PASS |
| Stage 3 · Measure | PASS | 6 of 6 checks passed (6 pass, run again after eval for KPI checks) |
| Stage 6 · Ground | PASS | ALL PARTS PASS. The agents are worth scoring. |
| Stage 7 · Operate | PASS | DRILL PASSED — the bad release was caught and rolled back automatically. |
| Stage 8 · Feed back to data | PASS | 19 of 19 contract checks passed. |
| Stage 9 · Govern | PASS | 10 of 10 governance checks passed. |

## Golden-question KPI (Stage 6, against the Stage 5 baseline)

Not yet run — `python3 eval/run_grounding.py` from the kit root needs Vertex AI access.

## Sign-off gate (ADR-10)

**READY TO SHIP**

Sign-off requires every stage above to PASS, and (once run) the semantic-grounded agent to beat both the Stage 5 baseline and the Stage 3 KPI targets — not just look good in a live demo.