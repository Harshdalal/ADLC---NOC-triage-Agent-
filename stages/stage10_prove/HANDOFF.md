# Hand-off runbook

**Stage 10 · Prove** — the document that lets someone else operate what
was built, without the builder in the room.

## What you're taking ownership of
A NOC triage agent with three variants (`v1_ungrounded`, `v1_grounded_raw`,
`v1_grounded_semantic`), grounded in ApexTel's real alarm feed and five
runbooks, gated so every P1 and remediation step needs a named human's
approval, with a tamper-evident audit trail and an automated fire drill
proving rollback works.

## Before you run it in anger
1. `python3 stages/stage10_prove/scorecard.py` — confirm every stage still says PASS.
2. `python3 eval/run_grounding.py` — confirm the semantic agent still beats the ungrounded baseline (`stages/stage5_build/baseline_score.md`) and clears Stage 3's KPI targets (`stages/stage3_measure/kpi_tree.md`).
3. `python3 stages/stage7_operate/fire_drill.py` — confirm rollback still works on today's code, not last month's.

## Day-to-day operation
| Task | Where |
|---|---|
| Start the agent | `cd agents && adk web` (see the root README, step 8) |
| Check what it's costing | `runs.jsonl` at the kit root — tokens and turns per call, written by `apextel/recorder.py` |
| Approve or reject a gated P1 | `stages/stage9_govern/hitl_gate.py` — `approve(gate_result, approved_by=...)` |
| Audit a past decision | `stages/stage9_govern/audit_log.py` — `verify()` the chain, then read the entries |
| Add a sixth runbook | Drop a `.md` file into `kb/`, no code change — `apextel/kb_search.py` picks it up automatically |
| Change a severity threshold | `stages/stage2_model_the_decision/decision_tree.py` — then `python3 logic_tests.py` before committing |
| Roll back a bad change | `git checkout <last-good-tag> -- <path>`, or see `stages/stage7_operate/fire_drill.py` for the pattern |

## Who to call
| Symptom | Escalate to |
|---|---|
| The agent hangs, or a tool box shows `blocked`/`error` repeatedly | Whoever owns `mcp_server/apextel_mcp.py` — check `bash tests/check_parts.sh` first |
| A golden question starts failing that used to pass | Whoever owns the KB runbooks or the alarm feed schema — the ontology (`ontology.yaml`) may be out of date |
| `scorecard.py` reports NOT READY | Do not promote. Fix the failing stage; re-run the full scorecard |
| An audit_log.jsonl chain fails `verify()` | Security incident, not a bug — treat as a compromised host |

## What "done" looked like when this was built
`stages/stage10_prove/SCORECARD.md`, generated the day this was signed off,
with every stage showing PASS. Re-generate it before every release; a stale
scorecard is worth nothing.
