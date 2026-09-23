# Decision card — NOC alarm triage

**Stage 1 · Frame** — the one-page artefact that exists before any code does.

| | |
|---|---|
| **The job** | Classify each incoming alarm's severity, correlate it with related alarms, identify the probable root cause, and open or route a ticket with a clear explanation. |
| **Who asks it today** | NOC duty engineers (Tier 1/2), by hand, checking Live_FM_Alarms, Sites_Master and past tickets across separate systems. |
| **Inputs** | One alarm record (or a correlated group) from `Live_FM_Alarms`: site, device, event time, raw severity code, subscriber-impact columns. |
| **Output** | A severity call (P1–P4), a root-cause classification (Root Cause / Symptom / Cascading / Transient), and either an auto-routed ticket or an escalation with a named next action. |
| **Autonomy level** | See the autonomy table below. Routing P2–P4 is autonomous. Every P1 classification, and every remediation step of any priority, requires human approval before it takes effect. |
| **Success looks like** | Lower MTTA/MTTR than the current hand-triage baseline, at the same or better accuracy, with every answer traceable to a source (Stage 3 makes this a number). |
| **Owner** | Network Operations, with Data Engineering owning the alarm feed and RAN/TX NOC teams owning the runbooks. |

## Why this decision, and not a bigger one
This kit does not try to have the agent *fix* anything. It answers "how bad is
this, and who should look at it" — a bounded, checkable decision. Remediation
(replacing hardware, rerouting traffic) stays a human action, informed by the
agent's answer. That boundary is what makes Stage 9's governance meaningful
rather than decorative.

## What "done" means for Stage 1
- This decision card, signed off by a NOC duty lead.
- The autonomy table below, signed off by Network Operations leadership.
- `hello_agent/` runs end to end (see `hello_agent/README.md`), proving the
  plumbing — model access, one tool call, one response — before any real
  logic exists.
