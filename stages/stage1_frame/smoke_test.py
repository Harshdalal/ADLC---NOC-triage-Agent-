"""Stage 1 smoke test: the plumbing, without spending a model call.

    cd stages/stage1_frame && python3 smoke_test.py

Checks that hello_agent builds correctly: right name, an instruction loaded,
no tools yet. The real "did it round-trip to the model" check is running
`adk web` yourself (see hello_agent/agent.py) — that one needs Vertex AI
access and is not automated here, on purpose: Stage 1 is about proving you
*can* call the model, which this script cannot do on your behalf.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

checks = []


def check(name, ok, detail=""):
    checks.append(ok)
    print(f"  {'PASS' if ok else 'FAIL':<6}{name:<44} {detail}")


try:
    from hello_agent.agent import root_agent
    check("hello_agent builds", True)
    check("hello_agent is named correctly", root_agent.name == "hello_agent", root_agent.name)
    check("hello_agent has no tools yet", root_agent.tools == [], str(root_agent.tools))
    check("hello_agent has an instruction", len(root_agent.instruction) > 20)
except ImportError as exc:
    check("hello_agent builds", False, f"google-adk not installed yet: {exc}")

print(f"\n{sum(checks)} of {len(checks)} checks passed.")
sys.exit(0 if all(checks) else 1)
