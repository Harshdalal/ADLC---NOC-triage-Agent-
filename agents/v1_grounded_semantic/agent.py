"""Stage 6 run 2: grounded on the ONTOLOGY-ALIGNED views, over MCP. Same
questions, same runbooks, same tools; only the shape and description of the
data changed."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # the kit folder, where apextel/ lives

from apextel.grounded import make_agent  # noqa: E402

root_agent = make_agent("v1_grounded_semantic", "semantic")
