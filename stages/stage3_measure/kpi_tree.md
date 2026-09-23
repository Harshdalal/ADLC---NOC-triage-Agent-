# KPI tree — is the agent actually working?

**Stage 3 · Measure** — "it's working" as a number, not an opinion.

## The baseline, from ApexTel's own closed tickets
Computed directly from `IncidentTickets_prod` (67 closed P1 tickets):

| Metric | Baseline (hand-triage, today) |
|---|---|
| Mean MTTR, P1 | **252.6 minutes** (~4.2 hours) |
| Median MTTR, P1 | **220 minutes** (~3.7 hours) |
| Range | 135 to 990 minutes |

Every number below is measured against *this* baseline — not a guess, not an
industry average.

## The tree

```
                    Objective: trusted, faster triage
                                    |
              +---------------------+---------------------+
              v                     v                     v
      Speed (MTTA/MTTR)      Accuracy                Cost to run
              |                     |                     |
     MTTA: time from alarm   Precision/recall on    Tokens per answer
     to first triage answer  severity calls           (Stage 6 measures
     MTTR: time from alarm   (against the golden      this directly)
     to incident closed      question set, eval/)
```

## Named targets (Stage 5's baseline scoring is measured against these)

| KPI | Target | Why this number |
|---|---|---|
| MTTA | Under 2 minutes for any P1-candidate alarm | The agent's classification should be near-instant; the human confirmation step (ADR-1) is the only added latency |
| MTTR, P1 | At least 20% below the 252.6-minute baseline | A meaningful, checkable improvement — not "faster," a number |
| Severity precision | At least 90% on the golden question set | False P1s waste a field dispatch; false P2s delay a real outage |
| False-escalation rate | Under 5% | Every false P1 costs a human's attention during a real incident |
| Tokens per answer (grounded) | Under 4,000 tokens, semantic-grounded | From Stage 6's `eval/run_grounding.py` token column |

## Constraints (see `constraints.md`)
A constraint is a limit the agent must never cross, regardless of how good
its other numbers look. Hitting a KPI target while violating a constraint is
not a win.

**Next:** [Stage 4 · Context](../stage4_context/) gives the agent the shared
vocabulary it needs before it can be built.
