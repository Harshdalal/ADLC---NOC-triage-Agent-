# ApexTel NOC Incident Triage Agent — Stage 6: Ground

This is the working implementation behind the *ADLC Webinar: NOC Incident Triage
Agent* deck. Stages 1–5 framed the decision, modelled the severity tree, set the
KPIs, defined the ontology and assembled Agent v1. This kit is where **Stage 6**
happens: Agent v1 stops guessing and starts answering from ApexTel's own alarm
records and runbooks, reached through an **MCP server** that owns them.

| Technique | What it does here |
|---|---|
| **RAG** | `search_runbook` finds the passages of five runbook documents most relevant to a question |
| **NLP2SQL** | `describe_data` and `run_sql` turn a question into one read-only SQL query |
| **MCP** | One ApexTel server offers all three tools. The agents connect to it; they never touch the data directly |

The experiment is three agents answering the same ten golden questions:

| Agent | Sees | Role |
|---|---|---|
| `v1_ungrounded` | Nothing but its instruction | **Before**: what the model knows on its own |
| `v1_grounded_raw` | Raw tables and the runbooks, over MCP | **Run 1** |
| `v1_grounded_semantic` | Ontology-aligned views and the runbooks, over MCP | **Run 2**: only the shape of the data changed |

The running scenario throughout is real, structurally: **14:10 UTC, 10 Aug 2026**,
a DC power failure at **KLCC01** (a Golden Hub site) cascades to **BKBT02**
two minutes later. Two incidents open: `INC-APX-2026-0811` (P1, KLCC01,
14,250 subscribers) and `INC-APX-2026-0812` (P2, BKBT02, a transmission
reroute). Every alarm ID, incident number and subscriber count in this kit is
pulled from ApexTel's own synthetic OSS/BSS export — nothing here is invented
for the demo.

Read in this order:

1. `docs/problem_statement.pdf` or the deck's early slides — the business case.
2. This README — setup, then run the three agents, then measure the before and after.
3. `ARCHITECTURE.md` — how the pieces fit together, and why.
4. `STEP_BY_STEP.md` — the same setup and run steps, without the narrative, for a quick re-run.

The code lives under this repository's root. The commands below set one
variable, `$KIT`, pointing at it, and use it everywhere.

---

## Setup: first time only

### 1. Get the code and point at the kit

```bash
git clone <YOUR_REPO_URL> apextel-noc-triage
cd apextel-noc-triage
echo 'export KIT="$(pwd)"' >> ~/.bashrc && source ~/.bashrc
echo $KIT
```

### 2. Sign in to Google Cloud

Two sign-ins: one for the `gcloud` command, one for the agents themselves.

```bash
gcloud auth login --no-launch-browser
gcloud auth application-default login --no-launch-browser
gcloud config set project <YOUR_PROJECT_ID>
gcloud services enable aiplatform.googleapis.com --project=<YOUR_PROJECT_ID>
```

### 3. Create the ADK environment

```bash
python3 -m venv ~/adk-env
source ~/adk-env/bin/activate
pip install -r "$KIT/requirements.txt"
adk --version
```

> The agents reach the data through an MCP server, which needs the `mcp`
> package, **version 1.x**. `pip install "google-adk[mcp]"` (already in
> `requirements.txt`) installs the right one. Do **not** run a plain
> `pip install mcp` — that installs version 2, which ADK does not support yet.

### 4. Run the setup check

```bash
bash "$KIT/setup.sh"
```

This writes `agents/.env` (your project, region and model — see
`.env.example` for what it looks like) and makes one real call to the model,
so any access problem shows up here rather than mid-demo.

> **Expected:** `Model access ... OK`, then `MCP support .... OK 1.x.x`, then `Setup finished.`

---

## Look inside the grounding (no model)

### 5. Build the database

```bash
source ~/adk-env/bin/activate
cd "$KIT"
python3 -m apextel.database
```

> **Expected:**
> ```
>   alm_tbl        12 rows
>   tkt_tbl        11 rows
>   site_tbl       4 rows
>   alarms_v       12 rows
>   incidents_v    11 rows
>   sites_v        4 rows
>
> Built data/apextel.db
> ```

The same 12 alarms, in two shapes: three **raw tables**, as ApexTel's fault
management feed actually stores them, and three **views** on top, the
semantic layer. The agents build the database themselves if it is missing;
building it here lets you look at it.

### 6. Run every component test

```bash
bash tests/check_parts.sh
```

> **Expected:** two blocks, then the verdict — `ALL PARTS PASS. The agents are worth scoring.`

| Part | What it checks |
|---|---|
| The database | The two traps: severity as a bare code, subscriber impact split across five columns |
| The SQL guardrail | Only one read-only `SELECT`, only on the tables the mode allows |
| Runbook search | The right passage comes first (a DC power question finds `bbu_power_failure.md`) |
| The MCP server | It starts, and offers the same three tools in both modes, described differently |
| The ontology | Referential integrity against `data/apextel.json` — every alarm has a site, no severity outside 1–3 |

### 7. Compare the two shapes, and try the guardrail

What the raw agent is told about the data:

```bash
python3 -c "from apextel import sql; import json; print(json.dumps(sql.describe('raw'), indent=1))"
```

> **Expected:** bare table and column names — `alm_tbl: aid, scode, sev, saf, rca, edt, tid, s2g, s3g, s4g, s5g, smob, aname`.
> `sev` is 1, 2 or 3, with nothing to say which is Critical.

What the semantic agent is told:

```bash
python3 -c "from apextel import sql; import json; print(json.dumps(sql.describe('semantic'), indent=1))"
```

> **Expected:** three views, each with a description and every column explained,
> for example `severity: Critical, Major or Minor (there is no fourth level)`.

A runbook search, exactly as the agent would run it:

```bash
python3 -c "from apextel import kb_search as k; r = k.search('What do we do when a BBU DC power alarm fires?')['passages'][0]; print(r['source']); print(r['text'][:200])"
```

> **Expected:** `bbu_power_failure.md#DC Power Failure Initial Response`, followed by the runbook text.

And the guardrail, stopping two unsafe queries:

```bash
python3 -c "from apextel import sql; print(sql.run('DELETE FROM alm_tbl', 'raw')); print(sql.run('SELECT * FROM alarms_v', 'raw'))"
```

> **Expected:**
> ```
> {'status': 'blocked', 'reason': 'Only SELECT queries are allowed.'}
> {'status': 'blocked', 'reason': 'Not allowed in raw mode: alarms_v. Allowed: alm_tbl, ...'}
> ```

---

## Run the three agents

### 8. Start the chat server

```bash
source ~/adk-env/bin/activate
cd "$KIT/agents"
adk web
```

> **Expected:** `Uvicorn running on http://127.0.0.1:8000`

Leave this terminal alone. The first time you talk to a grounded agent, ADK
starts the MCP server for it — you'll see lines like `ListToolsRequest` and
`CallToolRequest`. That's the agent and the server talking.

### 9. Ask all three agents the same questions

In the browser, go to **http://127.0.0.1:8000**. For each question, ask each
of the three agents, clicking **New Session** every time.

```
How many subscribers were impacted by the KLCC01 power outage, ALM-2026-8001?
```
> **Expected:** `v1_ungrounded` cannot know. `v1_grounded_semantic` answers **14,250**,
> from `subscribers_impacted_total`. `v1_grounded_raw` may get this wrong: five
> columns look like additive parts, but `smob` is already the total, so summing
> all five overcounts (32,000) — click its `run_sql` box to see which it did.

```
What priority is incident INC-APX-2026-0812, and what caused it?
```
> **Expected:** both grounded agents answer **P2**, root cause a cascading
> transmission failure from the KLCC01 hub outage. The ungrounded agent guesses.

```
What is the response procedure for a BBU DC Power Off alarm?
```
> **Expected:** both grounded agents call `search_runbook` and cite
> `bbu_power_failure.md`: check AC mains, verify rectifier status, dispatch a
> mobile genset if all rectifiers are offline.

```
What is the root cause of the KLCC01 outage, and what does the runbook say to do next?
```
> **Expected:** a grounded agent uses **both** tools: `run_sql` finds the root
> cause (rectifier module failure), `search_runbook` finds the hot-swap
> procedure. The ungrounded agent can give the second half at best, generically.

Record what you see — this is the same worksheet exercise as the deck's Stage
6 closer-look slide: **same records, fewer tokens, fewer wrong answers.**

---

## Measure the before and after

### 10. Run all ten golden questions on all three agents

```bash
cd "$KIT"
cat eval/grounding_questions.yaml
python3 eval/run_grounding.py
```

> **Expected:** one line per question, one column per agent, then totals —
> ungrounded scores lowest, and `Fixed by the semantic layer` names the
> questions where the shape of the data decided the answer. Results are
> written to `baseline/grounding_v1.json`.

### 11. Diagnose a failure

```bash
python3 -m json.tool baseline/grounding_v1.json | less
python3 eval/run_grounding.py raw G1     # re-run one question on one agent
```

| Cause | Typical fix |
|---|---|
| Context | Better data: a clearer view, a missing column, a runbook that says it |
| Tool | A better tool: clearer description, a better error message |
| Reasoning | A better instruction, or move the decision into code |

Do not change the data, views or runbooks during the exercise — write your
findings as an ADR (Architecture Decision Record) instead. See `ARCHITECTURE.md §9`.

---

## Optional: BigQuery and Vertex AI RAG

The default route needs nothing but this machine. These options move the same
data and runbooks into Google Cloud, with no change to the agents.

**BigQuery instead of SQLite:**
```bash
pip install google-cloud-bigquery
export BQ_DATASET="<YOUR_PROJECT_ID>.apextel_noc"
cd "$KIT"
python3 -c "from apextel import sql; sql.bigquery_setup()"
export SQL_BACKEND=bigquery
```

**Vertex AI RAG Engine instead of local search:**
```bash
pip install google-cloud-aiplatform
export GOOGLE_CLOUD_PROJECT="<YOUR_PROJECT_ID>"
cd "$KIT"
python3 -c "from apextel import kb_search as k; k.vertex_setup()"
# then export the printed VERTEX_RAG_CORPUS line, and:
export RAG_BACKEND=vertex
```

Start `adk web` again in the **same terminal**, so the agents and their MCP
server see these settings. To go back to the defaults: `unset SQL_BACKEND RAG_BACKEND`.

---

## Stop the chat server

```bash
# Normally: Ctrl + C in the terminal running `adk web`.

# If that terminal is gone, or the port is still busy:
pgrep -af "bin/adk"
pkill -f "bin/adk"

# If an MCP server is left running on its own:
pgrep -af apextel_mcp || echo "no MCP server running"
pkill -f apextel_mcp

# Clear saved chat sessions:
rm -rf "$KIT"/agents/*/.adk
```

Still busy on port 8000? `adk web --port 8001`.

---

## If something breaks

| Symptom | Likely cause | Fix |
|---|---|---|
| `ModuleNotFoundError: No module named 'mcp'` | ADK's MCP support is not installed | `pip install "google-adk[mcp]"` |
| `No module named 'mcp.server.fastmcp'` | `mcp` version 2 is installed | `pip install "mcp>=1.24,<2"` |
| `ModuleNotFoundError: No module named 'yaml'` or `'apextel'` | ADK environment not active, or not run from `$KIT` | `source ~/adk-env/bin/activate`, `cd "$KIT"` |
| `adk: command not found` | Environment not active in this terminal | `source ~/adk-env/bin/activate` |
| A grounded agent hangs, or says it cannot reach its tools | The MCP server failed to start | `Ctrl+C`, run `bash tests/check_parts.sh` — Part 4 shows whether the server starts |
| A tool box shows `"status": "blocked"` | The SQL guardrail stopped a query | Working as intended — the agent should rewrite the query |
| `PERMISSION_DENIED` / `403` | Identity cannot call Vertex AI | `bash setup.sh` and follow what it prints |
| `SERVICE_DISABLED` | Vertex AI API is off | `gcloud services enable aiplatform.googleapis.com --project=<YOUR_PROJECT_ID>` |
| Port 8000 already in use | Old chat server still running | `pkill -f "bin/adk"`, or `adk web --port 8001` |

---

## Why this stage matters

Stage 5 gave you Agent v1: the decision tree, the KPI tree and the ontology,
wired into one agent that could reason but not look anything up. Stage 6 is
the difference between an agent that sounds confident and one that is
*right, and can show you why*. The three agents in this kit are identical in
every way except what they're allowed to see — which is exactly what makes
the comparison mean something.

## See it live

This deep dive's own `agents/` folder (`v1_ungrounded`, `v1_grounded_raw`,
`v1_grounded_semantic`) is for the raw-vs-semantic comparison above. For the
stage-by-stage progression demo, run `adk web` from `stage_agents/` instead
and pick **`stage06_ground_agent`** — see the root
[README.md](../../README.md#watching-every-stages-own-agent-one-at-a-time)
for its prompt and expected output.
