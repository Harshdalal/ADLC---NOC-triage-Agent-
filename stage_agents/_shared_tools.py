"""Shared tool functions for stage_agents/*/agent.py.

Every stage's agent imports the subset of these it needs — the tools don't
change between stages, only which ones each agent is given. Defined once
here, instead of copy-pasted into every stage folder, so a fix or a change
only has to happen in one place.

Each function is a thin wrapper around the REAL, already-tested code in
stages/ and apextel/ — nothing here reimplements logic that exists elsewhere.
"""
import sys
from pathlib import Path

import yaml

KIT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KIT))
sys.path.insert(0, str(KIT / "stages" / "stage2_model_the_decision"))
sys.path.insert(0, str(KIT / "stages" / "stage9_govern"))

from decision_tree import AlarmInput, classify  # noqa: E402
from hitl_gate import submit as gate_submit  # noqa: E402
from audit_log import record as audit_record  # noqa: E402

ONTOLOGY = yaml.safe_load((KIT / "ontology.yaml").read_text(encoding="utf-8"))
CONTRACTS = yaml.safe_load(
    (KIT / "stages" / "stage8_feed_back_to_data" / "data_contracts.yaml").read_text(encoding="utf-8"))
SCORECARD_PATH = KIT / "stages" / "stage10_prove" / "SCORECARD.md"


def classify_alarm(severity_num: int, site_profile: str, sa_flag: bool,
                    subscribers_impacted: int, rca_classification: str) -> dict:
    """Classify one alarm using the Stage 2 severity decision tree — no
    model involved in the classification itself, only in deciding to call
    this tool.

    Args:
        severity_num: 1 (Critical), 2 (Major) or 3 (Minor).
        site_profile: e.g. "Golden Hub", "Silver", "Standard".
        sa_flag: whether the alarm is service-affecting.
        subscribers_impacted: total subscribers affected.
        rca_classification: "Root Cause", "Symptom", "Cascading", "Transient" or "Standalone".

    Returns:
        A dict with priority (P1-P4), escalate_to_human, and reason.
    """
    alarm = AlarmInput("(described, not looked up)", "(unknown)", severity_num,
                       site_profile, sa_flag, subscribers_impacted, rca_classification)
    result = classify(alarm)
    return {"priority": result.priority, "escalate_to_human": result.escalate_to_human,
            "reason": result.reason}


def kpi_status() -> dict:
    """Report ApexTel's real triage KPI targets, measured against the
    actual 252.6-minute mean MTTR baseline computed from ApexTel's own
    closed P1 tickets (see stages/stage3_measure/kpi_tree.md).

    Returns:
        A dict of baseline figures and named targets.
    """
    return {
        "baseline_mean_mttr_minutes_p1": 252.6,
        "baseline_median_mttr_minutes_p1": 220,
        "target_mtta_minutes": "under 2 minutes for any P1-candidate alarm",
        "target_mttr_improvement": "at least 20% below the 252.6-minute baseline",
        "target_severity_precision": "at least 90% on the golden question set",
        "target_false_escalation_rate": "under 5%",
        "target_tokens_per_answer_semantic": "under 4,000 tokens",
    }


def lookup_term(term: str) -> str:
    """Look up a word in the ApexTel ontology (ontology.yaml) — the shared
    vocabulary every stage from Stage 4 onward uses the same way.

    Args:
        term: a word like "severity", "priority", "site_profile",
            "subscribers_impacted" or "rca_result".

    Returns:
        The ontology's definition, or a note that the term isn't defined yet.
    """
    key = term.strip().lower().replace(" ", "_")
    definitions = ONTOLOGY.get("definitions", {})
    if key in definitions:
        return f"{term}: {definitions[key].get('meaning', '').strip()}"
    for name, spec in definitions.items():
        if key in name or name in key:
            return f"{name}: {spec.get('meaning', '').strip()}"
    return f"'{term}' is not defined in ontology.yaml. Defined terms: {', '.join(definitions)}."


def release_info() -> dict:
    """Report this build's release version and its last fire-drill result.

    Returns:
        A dict with a version tag and the last recorded fire-drill outcome.
    """
    return {
        "version": "v1-grounded-semantic-stage7",
        "last_fire_drill": "PASSED",
        "fire_drill_script": "stages/stage7_operate/fire_drill.py",
        "note": "Rollback is proven by actually breaking and restoring the decision tree — see the script.",
    }


def data_contract_summary() -> dict:
    """Report the real, machine-checked contract every tool call must obey
    (stages/stage8_feed_back_to_data/data_contracts.yaml). ADR-8: every
    tool is read-only by default.

    Returns:
        The run_sql and search_runbook limits, and confirmation no write
        path is implemented.
    """
    return {
        "run_sql_access": CONTRACTS["run_sql"]["access"],
        "run_sql_limits": CONTRACTS["run_sql"]["limits"],
        "search_runbook_access": CONTRACTS["search_runbook"]["access"],
        "search_runbook_max_passages": CONTRACTS["search_runbook"]["output"]["passages"]["max_items"],
        "write_path": CONTRACTS["open_incident_writeback"]["access"],
    }


def request_p1_approval(alarm_id: str, severity_num: int, site_profile: str, sa_flag: bool,
                         subscribers_impacted: int, rca_classification: str) -> dict:
    """Submit an alarm to the REAL human-in-the-loop gate
    (stages/stage9_govern/hitl_gate.py). This tool cannot approve anything
    itself — it only ever returns "auto_applied" (no approval needed) or
    "pending_approval" (a human must approve it separately, outside this
    chat, via hitl_gate.approve()).

    Args:
        alarm_id: the alarm's ID, for the record.
        severity_num, site_profile, sa_flag, subscribers_impacted, rca_classification:
            the same fields classify_alarm takes.

    Returns:
        A dict with status ("auto_applied" or "pending_approval") and the
        classification. Never returns "approved" — only a human, calling
        hitl_gate.approve() directly, can do that.
    """
    alarm = AlarmInput(alarm_id, "(unknown)", severity_num, site_profile, sa_flag,
                       subscribers_impacted, rca_classification)
    gated = gate_submit(alarm)
    return {"status": gated.status, "priority": gated.classification.priority,
            "reason": gated.classification.reason,
            "note": ("Auto-applied — no human approval required." if gated.status == "auto_applied"
                      else "PENDING — a human must call hitl_gate.approve() before this is final. "
                           "This agent cannot approve its own P1.")}


def record_decision(alarm_id: str, priority: str, gate_status: str) -> dict:
    """Write one entry to the REAL tamper-evident audit trail
    (stages/stage9_govern/audit_log.py). This is append-only — nothing
    this agent does can edit or delete a past entry.

    Args:
        alarm_id: the alarm this decision was about.
        priority: the priority classify_alarm returned.
        gate_status: the status request_p1_approval returned ("auto_applied"
            or "pending_approval" — never write "approved" from this tool;
            only a human's separate call to hitl_gate.approve() may do that).

    Returns:
        The entry actually written, including its hash.
    """
    entry = audit_record("agent_decision", alarm_id=alarm_id, priority=priority,
                          gate_status=gate_status, agent="stage10_prove_agent")
    return {"written": True, "hash": entry["hash"][:12] + "...", "time": entry["time"]}


def scorecard_status() -> dict:
    """Read the real SCORECARD.md written by stages/stage10_prove/scorecard.py.

    Returns:
        The scorecard's content, or a note that it hasn't been generated yet.
    """
    if not SCORECARD_PATH.exists():
        return {"status": "not yet generated",
                "note": "Run `python3 stages/stage10_prove/scorecard.py` from the kit root first."}
    return {"status": "found", "content": SCORECARD_PATH.read_text(encoding="utf-8")}
