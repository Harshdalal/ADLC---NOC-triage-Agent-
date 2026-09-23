"""The audit trail — Stage 9: Govern.

ADR-9: the audit trail is append-only and stored separately from the
agent's own state, so the agent can't edit its own history.

Each entry is chained to the previous one by a hash, the way a tamper-evident
log works: change or delete an old entry and every entry after it fails to
verify. This file does not stop someone editing audit_log.jsonl directly —
nothing running on the same machine can promise that — but it does mean any
such edit is *detectable*, which is the property that actually matters.

    cd stages/stage9_govern && python3 audit_log.py     # runs its own demo
"""
import hashlib
import json
from dataclasses import asdict, is_dataclass
from datetime import datetime, timezone
from pathlib import Path

LOG_PATH = Path(__file__).parent / "audit_log.jsonl"
GENESIS_HASH = "0" * 64


def _default(o):
    return asdict(o) if is_dataclass(o) else str(o)


def _hash(prev_hash: str, entry: dict) -> str:
    payload = json.dumps({"prev_hash": prev_hash, **entry}, sort_keys=True, default=_default)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _last_hash() -> str:
    if not LOG_PATH.exists() or LOG_PATH.stat().st_size == 0:
        return GENESIS_HASH
    with open(LOG_PATH, "rb") as f:
        last_line = f.readlines()[-1]
    return json.loads(last_line)["hash"]


def record(event: str, **fields) -> dict:
    """Append one entry. Returns the entry actually written, hash included."""
    entry = {
        "time": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "event": event,
        **fields,
    }
    prev_hash = _last_hash()
    entry["prev_hash"] = prev_hash
    entry["hash"] = _hash(prev_hash, entry)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, default=_default) + "\n")
    return entry


def verify() -> tuple[bool, str]:
    """Walk the whole chain. Returns (ok, detail)."""
    if not LOG_PATH.exists():
        return True, "empty log"
    prev_hash = GENESIS_HASH
    with open(LOG_PATH, encoding="utf-8") as f:
        for i, line in enumerate(f, start=1):
            entry = json.loads(line)
            claimed_hash = entry.pop("hash")
            if entry["prev_hash"] != prev_hash:
                return False, f"entry {i}: prev_hash does not match the entry before it"
            recomputed = _hash(prev_hash, entry)
            if recomputed != claimed_hash:
                return False, f"entry {i}: hash does not match its own contents — this entry was edited"
            prev_hash = claimed_hash
    return True, f"chain intact, {i} entries"


if __name__ == "__main__":
    if LOG_PATH.exists():
        LOG_PATH.unlink()

    print("Audit log demo\n")

    record("classification", alarm_id="ALM-2026-8001", site="KLCC01", priority="P1",
           reason="Critical, service-affecting, Golden Hub site.")
    record("approval", alarm_id="ALM-2026-8001", approved_by="j.tan@apextel.example",
           final_priority="P1")
    record("classification", alarm_id="ALM-2026-8003", site="BKBT02", priority="P2",
           reason="Major, service-affecting.")

    ok, detail = verify()
    print(f"  verify() after 3 honest entries -> {ok}: {detail}")

    print("\n  Now tampering with the log directly (editing one entry's priority)...")
    lines = LOG_PATH.read_text(encoding="utf-8").splitlines()
    tampered = json.loads(lines[0])
    tampered["priority"] = "P4"  # an attacker quietly downgrades a P1 after the fact
    lines[0] = json.dumps(tampered)
    LOG_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")

    ok, detail = verify()
    print(f"  verify() after tampering -> {ok}: {detail}")
