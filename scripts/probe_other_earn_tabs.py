r"""probe_other_earn_tabs.py - Check Bonus Clicks and Tasks tabs for availability.
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("timebucks", "probe_earn")
with T.session(lane) as client:
    # 1. Check Bonus Clicks
    print("Checking Bonus Clicks...")
    client.call_tool("browser_navigate", {"url": "https://timebucks.com/publishers/index.php?pg=earn&tab=push_clicks"})
    time.sleep(3.5)
    shot1 = lane.shot(client, "timebucks_bonus_clicks")
    page1 = T.read_page(client)
    body1 = page1.get("body", "")
    print("Bonus Clicks available?", "complete your profile" not in body1.lower()[:1500])
    print("Bonus Clicks snippet:\n", body1[500:1500])

    # 2. Check Tasks tab
    print("\nChecking Tasks tab...")
    client.call_tool("browser_navigate", {"url": "https://timebucks.com/publishers/index.php?pg=earn&tab=tasks_tasks"})
    time.sleep(3.5)
    shot2 = lane.shot(client, "timebucks_tasks_tab")
    page2 = T.read_page(client)
    body2 = page2.get("body", "")
    print("Tasks available?", "complete your profile" not in body2.lower()[:1500])
    print("Tasks snippet:\n", body2[500:1500])
