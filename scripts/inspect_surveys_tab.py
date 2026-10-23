r"""inspect_surveys_tab.py - Inspect surveys tab and high-paying surveys available.
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("timebucks", "surveys_inspect")
with T.session(lane) as client:
    print("Navigating to surveys tab...")
    client.call_tool("browser_navigate", {"url": "https://timebucks.com/publishers/index.php?pg=earn&tab=surveys"})
    time.sleep(4)

    surveys_data = client._js(r"""
        (function() {
            var allLinks = Array.from(document.querySelectorAll('a, button, input[type="button"]')).map(el => ({
                tag: el.tagName,
                val: (el.value || el.innerText || '').trim(),
                href: el.getAttribute('href') || ''
            })).filter(el => el.val.toLowerCase().includes('start') || el.val.toLowerCase().includes('take survey') || el.val.includes('$'));

            var tables = Array.from(document.querySelectorAll('table tr, .survey_row, .table tr')).map(r => {
                return r.innerText.replace(/\s+/g, ' ').trim().slice(0, 200);
            }).filter(t => t.includes('$') || t.includes('Start'));

            return {
                title: document.title,
                url: window.location.href,
                actionButtons: allLinks.slice(0, 10),
                tableRows: tables.slice(0, 10),
                bodySnippet: document.body.innerText.slice(400, 1600)
            };
        })()
    """)

    print("SURVEYS DATA:\n", json.dumps(surveys_data, indent=2))

    shot = lane.shot(client, "timebucks_surveys_tab_inspect")
    print("Screenshot saved to:", shot)
