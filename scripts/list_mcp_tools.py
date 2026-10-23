import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("mcp", "list_tools")
with T.session(lane) as client:
    # client has list_tools or similar?
    print("Client methods:", [m for m in dir(client) if not m.startswith('__')])
    tools = client.call_tool("list_tools", {}) if hasattr(client, 'call_tool') else None
    print("Tools response:", tools)
