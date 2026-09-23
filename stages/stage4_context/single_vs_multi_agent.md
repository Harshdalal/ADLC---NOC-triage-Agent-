# ADR-4: single agent, not multiple

**Stage 4 · Context**

## Decision
One agent owns NOC triage end to end — classification, correlation, root
cause and routing — until a single agent is proven insufficient. This kit
builds `v1_ungrounded`, `v1_grounded_raw` and `v1_grounded_semantic` as three
*variants* of one agent for the Stage 6 experiment, not three specialists
that hand off to each other.

## Why
The job (Stage 1's decision card) is one bounded decision — "how bad is
this, and who should look at it" — answered from one connected pool of
context (alarms, incidents, sites, runbooks). Splitting it into a
"classifier agent" and a "root-cause agent" and a "routing agent" would add
hand-off overhead (state passed between agents, more failure points, more
latency) without a clear boundary where one agent's job stops and another's
starts.

## When this would flip
Multi-agent starts to earn its complexity when sub-tasks have genuinely
different tool sets, different latency budgets, or different human
approvers. A concrete future trigger: if Stage 8's data contracts expand to
include a *write* path (not just read-only `run_sql`), the write-capable
tool should probably live behind its own agent with its own approval gate,
rather than being one more tool on the triage agent's list.

## Consequence
The single agent's instruction (`apextel/instructions/noc_assistant.txt`)
carries all three responsibilities at once. Keep it short and procedural
(steps 1-5) precisely because it is doing several things — a vague
instruction for a broad job fails faster than a vague instruction for a
narrow one.

**Next:** [Stage 5 · Build](../stage5_build/) assembles the first working
agent from Stage 2's tree, Stage 3's KPIs and this stage's ontology.
