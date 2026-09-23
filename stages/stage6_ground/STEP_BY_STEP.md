# Step by step

The same procedure as the README, without the narrative — for a quick re-run
once you already know the story.

```bash
# 1. Get the code
git clone <YOUR_REPO_URL> apextel-noc-triage && cd apextel-noc-triage
export KIT="$(pwd)"

# 2. Sign in
gcloud auth login --no-launch-browser
gcloud auth application-default login --no-launch-browser
gcloud config set project <YOUR_PROJECT_ID>
gcloud services enable aiplatform.googleapis.com --project=<YOUR_PROJECT_ID>

# 3. Environment
python3 -m venv ~/adk-env && source ~/adk-env/bin/activate
pip install -r "$KIT/requirements.txt"

# 4. Setup check (writes agents/.env)
bash "$KIT/setup.sh"

# 5. Build the database
cd "$KIT" && python3 -m apextel.database

# 6. Run component tests
bash tests/check_parts.sh

# 7. Chat with the three agents
cd "$KIT/agents" && adk web
# -> open http://127.0.0.1:8000, ask v1_ungrounded / v1_grounded_raw / v1_grounded_semantic
#    the same question, New Session each time

# 8. Score all three agents on the ten golden questions
cd "$KIT" && python3 eval/run_grounding.py

# 9. Stop
# Ctrl+C in the adk web terminal, then:
rm -rf "$KIT"/agents/*/.adk
```

| Step | Expect to see |
|---|---|
| 4 | `Model access ... OK`, `MCP support .... OK 1.x.x`, `Setup finished.` |
| 5 | `alm_tbl 12 rows`, `tkt_tbl 11 rows`, `site_tbl 4 rows`, plus the three views, then `Built data/apextel.db` |
| 6 | `ALL PARTS PASS. The agents are worth scoring.` |
| 8 | A table: one row per question, one column per agent, then `Fixed by the semantic layer: ...` |

Golden questions and expected answers: `eval/grounding_questions.yaml`.
Full explanation of every step: `README.md`. How it's built: `ARCHITECTURE.md`.
