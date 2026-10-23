import sys
import json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import lane_tools as T

lane = T.Lane("timebucks", "status_check")
with T.session(lane) as client:
    res = client.call_tool('browser_list_tabs', {})
    print("RAW LIST TABS:", json.dumps(res, indent=2))
    tabs = client.list_tabs()
    print("PARSED TABS:", tabs)
    if tabs:
        page = T.read_page(client)
        print("CURRENT PAGE:", page.get("url"), page.get("title"))
