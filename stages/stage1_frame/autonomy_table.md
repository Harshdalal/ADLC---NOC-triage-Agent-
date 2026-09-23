# Autonomy table — who decides what

**Stage 1 · Frame** — ADR-1: the agent may classify and route; it may never
execute a remediation without a human click.

| Branch of the decision | Agent may act alone? | Who is Responsible | Who is Accountable | Consulted | Informed |
|---|---|---|---|---|---|
| Classify severity for P2–P4 alarms | **Yes** | Agent | NOC duty lead | — | On-call engineer |
| Correlate alarms into one incident group | **Yes** | Agent | NOC duty lead | — | On-call engineer |
| Open/route a P2–P4 ticket to the right on-call team | **Yes** | Agent | NOC duty lead | — | On-call engineer |
| Classify severity for a candidate P1 | **No — flags, does not confirm** | Agent proposes | NOC duty engineer | Site owner (if Golden Hub) | Head of Network Ops |
| Open a P1 incident | **No** | NOC duty engineer | NOC duty lead | Agent (evidence) | Enterprise SLA Compliance |
| Any remediation step (genset dispatch, module swap, failover trigger) | **No, ever** | Field/Transmission engineer | Site owner | Agent (runbook citation) | NOC duty lead |
| Escalating to Enterprise Customer Service | **No** | NOC duty lead | Head of Network Ops | Agent (evidence) | Account team |

## The line, in one sentence
If the answer changes what a customer experiences or what a field engineer
does next, a human clicks the button. If the answer only changes which queue
a ticket lands in, the agent can act alone — and every action it takes alone
is still logged (Stage 9) and reversible (Stage 7).
