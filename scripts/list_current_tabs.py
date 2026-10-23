import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("browser", "list_tabs")
with T.session(lane) as client:
    res = client.call_tool("browser_list_tabs", {})
    tabs = T.A._parse_tabs(res) if hasattr(T, 'A') else res
    print("TABS:\n", json.dumps(tabs, indent=2))
