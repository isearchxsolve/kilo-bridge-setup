r"""inspect_all_earn_subtabs.py - Switch to Timebucks and inspect all Earn surfaces.
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("timebucks", "all_subtabs")
with T.session(lane) as client:
    tabs = client.list_tabs()
    tb_tab = next((t for t in tabs if "timebucks.com" in t.get("url", "").lower()), None)
    if tb_tab:
        client.switch_tab(tb_tab["id"])
        time.sleep(1)
    else:
        client.call_tool("browser_navigate", {"url": "https://timebucks.com/publishers/index.php?pg=earn"})
        time.sleep(3)

    # 1. Inspect exact captcha elements on Clicks tab
    print("Checking Clicks tab DOM...")
    client.call_tool("browser_navigate", {"url": "https://timebucks.com/publishers/index.php?pg=earn&tab=view_content_ads"})
    time.sleep(3)

    clicks_dom = client._js(r"""
        (function() {
            var body = document.body.innerText || '';
            var target = Array.from(document.querySelectorAll('div, p')).find(e => (e.innerText || '').includes('confirm you are not a robot'));
            var parent = target ? target.parentElement : null;
            return {
                bodyText: body.slice(500, 1500),
                parentHTML: parent ? parent.innerHTML.slice(0, 1000) : 'none'
            };
        })()
    """)
    print("CLICKS DOM:\n", json.dumps(clicks_dom, indent=2))
    shot_clicks = lane.shot(client, "timebucks_clicks_exact_dom")

    # 2. Check Tasks tab
    print("\nChecking Tasks tab...")
    client.call_tool("browser_navigate", {"url": "https://timebucks.com/publishers/index.php?pg=earn&tab=tasks_tasks"})
    time.sleep(3)
    page_tasks = T.read_page(client)
    print("TASKS PAGE TITLE:", page_tasks.get("title"))
    tasks_snippet = page_tasks.get("body", "")[500:1500]
    print("TASKS SNIPPET:\n", tasks_snippet)
    shot_tasks = lane.shot(client, "timebucks_tasks_ready")
