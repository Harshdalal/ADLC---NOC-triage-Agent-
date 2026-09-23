"""The severity decision tree — Stage 2: Model the decision.

Turns the NOC duty engineer's tacit judgement into an explicit, testable
function. No model, no tools: this is the deterministic guardrail layer
(Stage 4's "agent control planes" — the system plane). The agent's later
reasoning (Stages 5-6) sits on top of this, for the branches that genuinely
need judgement; it never overrides what this function decides.

ADR-2: guardrails handle clear-cut severity; the agent's reasoning handles
judgement calls (e.g. "is this actually related to that other alarm"); both
are logged the same way (Stage 9).
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class AlarmInput:
    """The minimum an alarm needs before it can be classified."""
    alarm_id: str
    site_code: str
    severity_num: int          # 1 (Critical), 2 (Major) or 3 (Minor) — from the raw feed
    site_profile: str          # e.g. "Golden Hub", "Silver", "Standard"
    sa_flag: bool              # service-affecting
    subscribers_impacted: int
    rca_classification: str    # "Root Cause", "Symptom", "Cascading", "Transient", "Standalone"


@dataclass
class Classification:
    priority: str               # P1-P4
    escalate_to_human: bool
    reason: str


# Thresholds. These are the assumptions Stage 1's decision card flags for
# sign-off by Network Operations leadership — change them here, not in the
# agent's instruction, so every change is one diff and one set of test runs.
GOLDEN_HUB_PROFILES = {"Golden Hub"}
LARGE_IMPACT_SUBSCRIBERS = 5000


def classify(alarm: AlarmInput) -> Classification:
    """Deterministic first pass. Returns a priority and whether a human must
    confirm it before it is final. This function never calls a model."""

    # Transient alarms never open an incident — they clear themselves.
    if alarm.rca_classification == "Transient":
        return Classification("P4", escalate_to_human=False,
                               reason="Transient: clears within 5 minutes, no ticket needed.")

    # A Cascading alarm inherits urgency from its root cause but is still its
    # own incident (see ontology.yaml) — treat it seriously, but it is not
    # automatically the same severity as the root cause.
    if not alarm.sa_flag:
        return Classification("P4", escalate_to_human=False,
                               reason="Not service-affecting.")

    critical = alarm.severity_num == 1
    golden_hub = alarm.site_profile in GOLDEN_HUB_PROFILES
    large_impact = alarm.subscribers_impacted >= LARGE_IMPACT_SUBSCRIBERS

    if critical and (golden_hub or large_impact):
        return Classification(
            "P1", escalate_to_human=True,
            reason=f"Critical, service-affecting, and {'a Golden Hub site' if golden_hub else f'{alarm.subscribers_impacted} subscribers impacted'}."
            " P1 always needs a human to confirm before the incident opens (ADR-1).")

    if critical:
        return Classification("P2", escalate_to_human=False,
                               reason="Critical but not Golden Hub and under the large-impact threshold.")

    if alarm.severity_num == 2:
        return Classification("P2", escalate_to_human=False, reason="Major, service-affecting.")

    return Classification("P3", escalate_to_human=False, reason="Minor, service-affecting.")


def explain(alarm: AlarmInput, result: Optional[Classification] = None) -> str:
    """A one-line, human-readable explanation — what Stage 9's audit trail stores."""
    result = result or classify(alarm)
    return (f"{alarm.alarm_id} at {alarm.site_code} -> {result.priority}"
            f"{' (needs human confirmation)' if result.escalate_to_human else ''}: {result.reason}")
