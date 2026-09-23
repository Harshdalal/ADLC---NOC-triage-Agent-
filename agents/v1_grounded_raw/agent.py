"""Stage 6 run 1: grounded on the RAW tables, over MCP. Bare column names,
severity as a code, subscriber impact split across five columns."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # the kit folder, where apextel/ lives

from apextel.grounded import make_agent  # noqa: E402

root_agent = make_agent("v1_grounded_raw", "raw")
