r"""check_tasks_tab.py - Inspect Tasks tab now that profile is updated.
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("timebucks", "tasks_check")
with T.session(lane) as client:
    url = "https://timebucks.com/publishers/index.php?pg=earn&tab=tasks_tasks"
    print("Navigating to Tasks tab:", url)
    client.call_tool("browser_navigate", {"url": url})
    time.sleep(4)

    shot = lane.shot(client, "timebucks_tasks_tab_unlocked")
    print("Screenshot saved to:", shot)

    page = T.read_page(client)
    body = page.get("body", "")
    print("PAGE TITLE:", page.get("title"))
    print("Profile gate still present?", "complete your profile" in body.lower()[:1500])
    print("Tasks body snippet:\n", body[400:1500])
