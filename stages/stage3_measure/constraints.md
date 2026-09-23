# Constraints — what the agent must never do

**Stage 3 · Measure** — these are checked by `metric_tests.py`, not left to
good intentions. A constraint violation fails the build regardless of how
good the KPI numbers look (see `kpi_tree.md`).

| # | Constraint | Enforced by |
|---|---|---|
| C1 | The agent never auto-closes a P1 incident | Stage 9's HITL gate; `metric_tests.py::test_no_autonomous_p1_close` |
| C2 | The agent never issues a remediation instruction without a human click | Stage 1's autonomy table (ADR-1); Stage 9's HITL gate |
| C3 | Every SQL query is read-only | Stage 6's `sql.check()` guardrail |
| C4 | No single answer reads more than 50 database rows or 3 runbook passages | Stage 6's context budget |
| C5 | Every answer that cites a record or a runbook names its source | Stage 9's explanation-by-construction |
| C6 | A failed fire drill blocks promotion to production | Stage 7 (ADR-7) |
| C7 | Grounded-semantic MTTR must not regress versus the Stage 5 baseline | Stage 10's scorecard sign-off gate |

A constraint is binary — pass or fail — on purpose. KPIs can trade off
against each other (faster vs. more accurate); constraints cannot.
