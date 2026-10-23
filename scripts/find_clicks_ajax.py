r"""find_clicks_ajax.py - Find how Clicks tab is populated.
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("timebucks", "clicks_ajax")
with T.session(lane) as client:
    tabs = client.list_tabs()
    tb_tab = next((t for t in tabs if "timebucks.com" in t.get("url", "").lower()), None)
    if tb_tab:
        client.switch_tab(tb_tab["id"])

    ajax_info = client._js(r"""
        (function() {
            var btn = document.querySelector('a[href*="task_content_14"], a[href*="view_content_ads"]');
            var onclick = btn ? (btn.getAttribute('onclick') || btn.onclick) : null;

            // Search scripts for view_content_ads
            var scripts = Array.from(document.querySelectorAll('script')).map(s => s.innerText).filter(t => t.includes('task_content_14') || t.includes('view_content_ads'));

            return {
                btnOuter: btn ? btn.outerHTML : null,
                onclick: String(onclick),
                scriptsFound: scripts.length,
                scriptSnippets: scripts.map(s => s.slice(0, 300))
            };
        })()
    """)
    print("CLICKS AJAX INFO:\n", json.dumps(ajax_info, indent=2))
