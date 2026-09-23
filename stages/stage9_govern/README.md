# Stage 9 · Govern

One more layer: a human who can say no. Everything above this stage still
needs it — a well-grounded, well-tested agent is still just an opinion until
something physically stops it from acting alone on a P1.

## Files
- **[`hitl_gate.py`](hitl_gate.py)** — wraps Stage 2's `classify()`; a P1 cannot get a `final_priority()` until a named person approves it.
- **[`audit_log.py`](audit_log.py)** — an append-only, hash-chained log; editing any past entry breaks the chain from that point on, detectably.
- **[`explanation.py`](explanation.py)** — builds the explanation alongside the decision, from what the gate and the tree actually used — never generated after the fact.
- **[`governance_tests.py`](governance_tests.py)** — all of the above, proven, including a real tamper attempt.

## Run it

```bash
cd stages/stage9_govern
python3 hitl_gate.py          # demo: a P1 blocked, then approved
python3 audit_log.py          # demo: an honest log verifies, a tampered one doesn't
python3 explanation.py        # demo: a full explanation with evidence
python3 governance_tests.py   # the real test suite — run this one in CI
```

> **Expected:** `governance_tests.py` ends with `10 of 10 governance checks
> passed.` — including a test that plants a fake edit in the audit log and
> confirms `verify()` catches it.

## Could an auditor reconstruct this without asking anyone?
That's the test this stage is built to pass. Given only `audit_log.jsonl`,
an auditor can see every classification, who approved or rejected it, and
verify none of it was edited after the fact — without needing to ask the
NOC engineer what they remember from that shift.

**Next:** [Stage 10 · Prove](../stage10_prove/) — pulling every stage's own
test into one scorecard, and deciding whether to ship.

## See it live

Run `adk web` from `stage_agents/` (see the root [README.md](../../README.md#watching-every-stages-own-agent-one-at-a-time)), pick **stage09_govern_agent**, and try the prompt in the root README's table — every tool call it makes is the real code from this folder, not a simulation.
