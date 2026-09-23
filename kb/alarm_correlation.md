# Network Element Alarm Correlation Guide

Source: KB-SRC-006 · Owner: Fault Management Team

## Alarm Correlation and RCA Classification
SA (Service Affecting) flag criteria: an alarm is SA=Yes if it directly causes, or
has the potential to cause, loss of customer service. RCA classification: Root
Cause is the primary fault that caused the event. Symptom is a downstream alarm
caused by the root cause, at the same site. Cascading is an alarm on a different
network element caused by the root cause event, typically at a dependent site.
Transient is an alarm that clears within 5 minutes automatically. Best practice:
always correlate alarms by devicename, event_datetime within +/- 5 minutes, and
site_name to identify cascading scenarios before raising multiple tickets. A
single root-cause alarm at a hub site may generate 5-15 symptom or cascading
alarms at dependent sites.

## Severity vs. priority
Severity (Critical, Major, Minor) describes how serious one alarm is on its own.
Priority (P1-P4) is the incident's handling priority, decided when the ticket is
opened, and takes the site's SLA profile into account. A Major alarm at a Golden
Hub site can still open as a P1 incident; do not assume the two scales always
move together.
