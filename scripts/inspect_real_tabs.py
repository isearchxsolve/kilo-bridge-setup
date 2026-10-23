r"""inspect_real_tabs.py - Inspect real Clicks (view_content_ads) and Surveys (all_surveys).
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("timebucks", "real_tabs")
with T.session(lane) as client:
    # 1. Clicks: view_content_ads
    print("Navigating to view_content_ads...")
    client.call_tool("browser_navigate", {"url": "https://timebucks.com/publishers/index.php?pg=earn&tab=view_content_ads"})
    time.sleep(3.5)

    c_info = client._js(r"""
        (function() {
            var ads = Array.from(document.querySelectorAll('input[type="button"], input[type="submit"], button, a.btn, .click-btn')).map(b => ({
                tag: b.tagName,
                text: (b.value || b.innerText || '').trim(),
                onclick: b.getAttribute('onclick'),
                href: b.getAttribute('href')
            })).filter(x => x.text.length > 0);

            var tables = Array.from(document.querySelectorAll('table tr')).map(r => r.innerText.replace(/\s+/g, ' ').trim());

            return {
                url: window.location.href,
                title: document.title,
                adsButtons: ads,
                tablesSample: tables.slice(0, 10),
                bodySample: document.body.innerText.slice(400, 1800)
            };
        })()
    """)
    print("CLICKS (view_content_ads):\n", json.dumps(c_info, indent=2))
    shot1 = lane.shot(client, "timebucks_view_content_ads")
    print("Shot 1:", shot1)

    # 2. Surveys: all_surveys
    print("Navigating to all_surveys...")
    client.call_tool("browser_navigate", {"url": "https://timebucks.com/publishers/index.php?pg=earn&tab=all_surveys"})
    time.sleep(3.5)

    s_info = client._js(r"""
        (function() {
            var routers = Array.from(document.querySelectorAll('table tr, .survey-card, .router-item, a[href*="survey"]')).map(el => ({
                text: el.innerText.replace(/\s+/g, ' ').trim().slice(0, 150),
                href: el.getAttribute('href')
            })).filter(x => x.text.includes('$') || x.text.includes('Start') || x.text.includes('Survey'));

            return {
                url: window.location.href,
                title: document.title,
                routersSample: routers.slice(0, 15),
                bodySample: document.body.innerText.slice(400, 1800)
            };
        })()
    """)
    print("SURVEYS (all_surveys):\n", json.dumps(s_info, indent=2))
    shot2 = lane.shot(client, "timebucks_all_surveys_tab")
    print("Shot 2:", shot2)
