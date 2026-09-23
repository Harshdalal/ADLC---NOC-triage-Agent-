"""The ApexTel NOC database, in two shapes (ADLC Stage 6: Ground).

Real rows pulled from ApexTel's own Live_FM_Alarms, IncidentTickets_prod and
Sites_Master exports (see data/apextel.json), stored the way the fault-management
feed actually stores them: severity as a bare code, subscriber impact split
across five columns.

On top of the raw tables sit three VIEWS, the semantic layer. They use the
Stage 4 ontology's words: severity spelled out, subscriber impact pre-summed,
and the site's SLA profile joined in.

    RAW TABLES                          SEMANTIC VIEWS
    alm_tbl  tkt_tbl  site_tbl           alarms_v  incidents_v  sites_v

Grounding on the raw tables and then on the views, with the same ten
questions, is the Stage 6 experiment.

    python3 -m apextel.database            build data/apextel.db (run from the kit)
"""
import json
import sqlite3
from pathlib import Path

KIT = Path(__file__).resolve().parents[1]
DB_PATH = KIT / "data" / "apextel.db"
DATA = json.loads((KIT / "data" / "apextel.json").read_text(encoding="utf-8"))

SEV_WORD = {1: "Critical", 2: "Major", 3: "Minor"}

RAW_TABLES = {
    "alm_tbl": "aid TEXT, scode TEXT, sev INTEGER, saf TEXT, rca TEXT, edt TEXT, tid TEXT, "
               "s2g INTEGER, s3g INTEGER, s4g INTEGER, s5g INTEGER, smob INTEGER, aname TEXT",
    "tkt_tbl": "tid TEXT, scode TEXT, pri TEXT, rcause TEXT, cdt TEXT, xdt TEXT, sdesc TEXT",
    "site_tbl": "scode TEXT, sname TEXT, prof TEXT, region TEXT, city TEXT",
}


def view_sql(t=lambda name: name):
    """The semantic layer. t() qualifies a table name, so the same SQL works in BigQuery."""
    return {
        "alarms_v": f"""
            SELECT a.aid AS alarm_id,
                   a.scode AS site_code,
                   CASE a.sev WHEN 1 THEN 'Critical' WHEN 2 THEN 'Major' WHEN 3 THEN 'Minor' END AS severity,
                   CASE WHEN a.saf = 'Yes' THEN 'yes' ELSE 'no' END AS service_affecting,
                   a.rca AS rca_classification,
                   a.edt AS event_time,
                   a.tid AS incident_id,
                   a.smob AS subscribers_impacted_total
            FROM {t('alm_tbl')} a""",
        "incidents_v": f"""
            SELECT t.tid AS incident_id,
                   t.scode AS site_code,
                   t.pri AS priority,
                   t.rcause AS root_cause,
                   t.cdt AS created_at,
                   t.xdt AS closed_at,
                   CASE WHEN t.xdt IS NULL OR t.xdt = '' THEN 'yes' ELSE 'no' END AS is_open
            FROM {t('tkt_tbl')} t""",
        "sites_v": f"""
            SELECT s.scode AS site_code, s.sname AS site_name, s.prof AS profile,
                   s.region AS region, s.city AS city
            FROM {t('site_tbl')} s""",
    }


def rows():
    """The records, reshaped into the raw tables exactly as the FM feed stores them."""
    return {
        "alm_tbl": [(a["alarm_id"], a["site_code"], a["severity_num"], a["sa_flag"], a["rca_result"],
                     a["event_time"], a["incident_id"], a["sub_2g"], a["sub_3g"], a["sub_4g"],
                     a["sub_5g"], a["sub_mobile"], a["alarm_name"]) for a in DATA["alarms"]],
        "tkt_tbl": [(t["incident_id"], t["site_code"], t["priority"], t["root_cause"], t["created_at"],
                     t["closed_at"], t["short_description"]) for t in DATA["incidents"]],
        "site_tbl": [(s["site_code"], s["site_name"], s["profile"], s["region"], s["city"])
                     for s in DATA["sites"]],
    }


def build(path=DB_PATH):
    path.parent.mkdir(exist_ok=True)
    if path.exists():
        path.unlink()
    con = sqlite3.connect(path)
    for table, columns in RAW_TABLES.items():
        con.execute(f"CREATE TABLE {table} ({columns})")
        data = rows()[table]
        if data:
            con.executemany(f"INSERT INTO {table} VALUES ({','.join('?' * len(data[0]))})", data)
    for view, sql in view_sql().items():
        con.execute(f"CREATE VIEW {view} AS {sql}")
    con.commit()
    con.close()
    return path


if __name__ == "__main__":
    p = build()
    con = sqlite3.connect(p)
    for name in list(RAW_TABLES) + list(view_sql()):
        n = con.execute(f"SELECT COUNT(*) FROM {name}").fetchone()[0]
        print(f"  {name:<14} {n} rows")
    print(f"\nBuilt {p.relative_to(KIT)}")
