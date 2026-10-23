r"""claim_bonus_clicks.py - Check and claim bonus on Bonus Clicks tab.
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("timebucks", "bonus_clicks")
with T.session(lane) as client:
    url = "https://timebucks.com/publishers/index.php?pg=earn&tab=push_clicks"
    print("Navigating to Bonus Clicks:", url)
    client.call_tool("browser_navigate", {"url": url})
    time.sleep(3.5)

    shot = lane.shot(client, "timebucks_bonus_clicks_view")
    print("Screenshot saved to:", shot)

    # Check for claim button
    claim_info = client._js(r"""
        (function() {
            var buttons = Array.from(document.querySelectorAll('input, button, a.btn'));
            var claimBtn = buttons.find(b => {
                var t = (b.value || b.innerText || '').toLowerCase().trim();
                return t.includes('claim') || t.includes('get bonus');
            });
            var bodyText = document.body.innerText || '';
            return {
                found: !!claimBtn,
                buttonText: claimBtn ? (claimBtn.value || claimBtn.innerText) : null,
                buttonTag: claimBtn ? claimBtn.tagName : null,
                snippet: bodyText.slice(500, 1500)
            };
        })()
    """)
    print("CLAIM INFO:\n", json.dumps(claim_info, indent=2))

    if claim_info.get("found"):
        print("Clicking claim button...")
        client._js(r"""
            (function() {
                var buttons = Array.from(document.querySelectorAll('input, button, a.btn'));
                var claimBtn = buttons.find(b => {
                    var t = (b.value || b.innerText || '').toLowerCase().trim();
                    return t.includes('claim') || t.includes('get bonus');
                });
                if (claimBtn) claimBtn.click();
            })()
        """)
        time.sleep(3)
        shot_claimed = lane.shot(client, "timebucks_bonus_claimed")
        print("Shot after claim:", shot_claimed)
        page = T.read_page(client)
        print("PAGE SNIPPET:\n", page.get("body", "")[500:1500])
