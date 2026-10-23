r"""inspect_earn_subtabs.py - Inspect Clicks, Bonus Clicks, and Hourly Crown tabs.
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("timebucks", "earn_subtabs")
with T.session(lane) as client:
    # 1. Inspect Clicks tab
    print("Navigating to Clicks tab...")
    client.call_tool("browser_navigate", {"url": "https://timebucks.com/publishers/index.php?pg=earn&tab=content_clicks"})
    time.sleep(3.5)
    c_info = client._js(r"""
        (function() {
            var btns = Array.from(document.querySelectorAll('input[type="button"], input[type="submit"], button, a.btn')).map(b => (b.value || b.innerText || '').trim()).filter(t => t.length > 0);
            return {
                url: window.location.href,
                title: document.title,
                buttons: btns.slice(0, 10),
                body: document.body.innerText.slice(400, 1500)
            };
        })()
    """)
    print("CLICKS TAB:\n", json.dumps(c_info, indent=2))
    shot1 = lane.shot(client, "timebucks_tab_clicks")
    print("Clicks shot:", shot1)

    # 2. Inspect Bonus Clicks tab
    print("Navigating to Bonus Clicks tab...")
    client.call_tool("browser_navigate", {"url": "https://timebucks.com/publishers/index.php?pg=earn&tab=bonus_clicks"})
    time.sleep(3.5)
    b_info = client._js(r"""
        (function() {
            var btns = Array.from(document.querySelectorAll('input[type="button"], input[type="submit"], button, a.btn')).map(b => (b.value || b.innerText || '').trim()).filter(t => t.length > 0);
            return {
                url: window.location.href,
                title: document.title,
                buttons: btns.slice(0, 10),
                body: document.body.innerText.slice(400, 1500)
            };
        })()
    """)
    print("BONUS CLICKS TAB:\n", json.dumps(b_info, indent=2))
    shot2 = lane.shot(client, "timebucks_tab_bonus_clicks")
    print("Bonus Clicks shot:", shot2)

    # 3. Inspect Hourly Crown tab
    print("Navigating to Hourly Crown tab...")
    client.call_tool("browser_navigate", {"url": "https://timebucks.com/publishers/index.php?pg=earn&tab=hourly_crown"})
    time.sleep(3.5)
    h_info = client._js(r"""
        (function() {
            var btns = Array.from(document.querySelectorAll('input[type="button"], input[type="submit"], button, a.btn')).map(b => (b.value || b.innerText || '').trim()).filter(t => t.length > 0);
            return {
                url: window.location.href,
                title: document.title,
                buttons: btns.slice(0, 10),
                body: document.body.innerText.slice(400, 1500)
            };
        })()
    """)
    print("HOURLY CROWN TAB:\n", json.dumps(h_info, indent=2))
    shot3 = lane.shot(client, "timebucks_tab_hourly_crown")
    print("Hourly Crown shot:", shot3)
