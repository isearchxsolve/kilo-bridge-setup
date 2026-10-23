r"""click_participate.py - Click Participate on PrimeEarn qualify page.
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("timebucks", "primeearn_survey")
with T.session(lane) as client:
    print("Navigating to https://monetize.primeearn.com/qualify...")
    client.call_tool("browser_navigate", {"url": "https://monetize.primeearn.com/qualify"})
    time.sleep(3)

    # Click Participate button
    click_res = client._js(r"""
        (function() {
            var btns = Array.from(document.querySelectorAll('button, a, div[role="button"]')).filter(b => {
                var t = (b.innerText || '').trim();
                return t.toLowerCase().includes('participate');
            });

            if (btns.length > 0) {
                btns[0].click();
                return { ok: true, clicked: btns[0].innerText.trim(), tag: btns[0].tagName, href: btns[0].getAttribute('href') };
            }
            return { ok: false, error: 'Participate button not found' };
        })()
    """)
    print("Participate click result:", json.dumps(click_res, indent=2))

    time.sleep(6)

    info = client._js(r"({ url: window.location.href, title: document.title, body: document.body.innerText.slice(0, 1000) })")
    print("Screen after participate:\n", json.dumps(info, indent=2))
    shot = lane.shot(client, "primeearn_after_participate")
    print("Screenshot:", shot)
