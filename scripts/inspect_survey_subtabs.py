r"""inspect_survey_subtabs.py - Inspect subtabs under Surveys tab on TimeBucks.
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("timebucks", "survey_subtabs")
with T.session(lane) as client:
    print("Navigating to Earn Surveys...")
    client.call_tool("browser_navigate", {"url": "https://timebucks.com/publishers/index.php?pg=earn&tab=surveys"})
    time.sleep(3.5)

    subnav = client._js(r"""
        (function() {
            var subLinks = Array.from(document.querySelectorAll('a[href*="tab="]')).map(a => ({
                text: (a.innerText || '').trim(),
                href: a.getAttribute('href')
            })).filter(x => x.text.length > 0 && x.text.length < 30);

            var tables = Array.from(document.querySelectorAll('table tr')).map(r => r.innerText.replace(/\s+/g, ' ').trim());

            return {
                url: window.location.href,
                subLinks: subLinks,
                tables: tables.slice(0, 15),
                body: document.body.innerText.slice(400, 1800)
            };
        })()
    """)
    print("SURVEY SUBTABS INFO:\n", json.dumps(subnav, indent=2))
    shot = lane.shot(client, "timebucks_surveys_subtabs")
    print("Screenshot:", shot)
