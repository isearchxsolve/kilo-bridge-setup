import sys
import json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import lane_tools as T

lane = T.Lane("timebucks", "navigate_test")
with T.session(lane) as client:
    print("Navigating to TimeBucks...")
    nav_res = client.call_tool('browser_navigate', {'url': 'https://timebucks.com/publishers/index.php?pg=earn'})
    print("NAV RES:", json.dumps(nav_res, indent=2))
    tabs = client.list_tabs()
    print("TABS AFTER NAV:", tabs)
    page = T.read_page(client)
    print("PAGE URL:", page.get("url"))
    print("PAGE TITLE:", page.get("title"))
    print("PAGE BODY SNIPPET:", page.get("body", "")[:300])
