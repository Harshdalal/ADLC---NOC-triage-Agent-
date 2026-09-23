"""Contract tests — Stage 8: Feed back to data.

Checks the real tool code (Stage 6's apextel/sql.py and apextel/kb_search.py)
against data_contracts.yaml, so the contract and the code cannot silently
drift apart.

    cd stages/stage8_feed_back_to_data && python3 contract_tests.py
"""
import sys
from pathlib import Path

import yaml

KIT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(KIT))

from apextel import kb_search, sql  # noqa: E402

CONTRACT = yaml.safe_load((Path(__file__).parent / "data_contracts.yaml").read_text(encoding="utf-8"))
checks = []


def check(name, ok, detail=""):
    checks.append(ok)
    print(f"  {'PASS' if ok else 'FAIL':<6}{name:<58} {detail}")


print("run_sql against its contract\n")

limits = CONTRACT["run_sql"]["limits"]
check("MAX_ROWS matches the contract", sql.MAX_ROWS == limits["max_rows"], f"got {sql.MAX_ROWS}")

for kw in limits["write_keywords_forbidden"]:
    blocked = sql.check(f"SELECT * FROM alm_tbl; {kw.upper()} alm_tbl", "raw") is not None \
        or sql.check(f"{kw.upper()} FROM alm_tbl", "raw") is not None
    check(f"'{kw}' is forbidden", blocked)

ok_result = sql.run("SELECT aid FROM alm_tbl LIMIT 1", "raw")
check("ok-shaped response matches contract",
      set(ok_result) >= set(CONTRACT["run_sql"]["output"]["ok"]), str(list(ok_result)))

blocked_result = sql.run("DELETE FROM alm_tbl", "raw")
check("blocked-shaped response matches contract",
      set(blocked_result) == set(CONTRACT["run_sql"]["output"]["blocked"]), str(list(blocked_result)))

print("\nsearch_runbook against its contract\n")

result = kb_search.search("BBU power failure")
passages_contract = CONTRACT["search_runbook"]["output"]["passages"]
max_items = passages_contract["max_items"]
check(f"returns at most {max_items} passages", len(result["passages"]) <= max_items, len(result["passages"]))
item_schema = set(passages_contract["item"])
check("every passage has the contracted fields",
      all(set(p) == item_schema for p in result["passages"]))

print("\ndescribe_data against its contract\n")

raw_desc = sql.describe("raw")
check("raw mode returns {mode, tables}", set(raw_desc) == {"mode", "tables"}, str(list(raw_desc)))
sem_desc = sql.describe("semantic")
check("semantic mode returns {mode, views}", set(sem_desc) == {"mode", "views"}, str(list(sem_desc)))

print(f"\n{sum(checks)} of {len(checks)} contract checks passed.")
sys.exit(0 if all(checks) else 1)
