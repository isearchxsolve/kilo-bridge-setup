import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("coinpayu", "test_ad_click")
with T.session(lane) as client:
    client.call_tool("browser_navigate", {"url": "https://www.rewardjoy.com/dashboard/ads_surf"})
    time.sleep(3)

    # Click first ad
    res = client._js(r"""
        (function() {
            var span = document.querySelector('.ags-description span') || document.querySelector('.ags-description');
            if (!span) return { error: 'span not found' };

            var ev = new MouseEvent('click', { bubbles: true, cancelable: true, view: window });
            span.dispatchEvent(ev);

            return {
                clicked: true,
                targetText: span.innerText
            };
        })()
    """)
    print("CLICK DISPATCH:", json.dumps(res))

    # Monitor for 8 seconds
    checks = []
    for i in range(4):
        time.sleep(2)
        state = client._js(r"""
            (function() {
                var firstBox = document.querySelector('.frameless-ad-box');
                var timerEl = document.querySelector('.ags-detail-time, [class*="time"], [class*="countdown"]');
                return {
                    title: document.title,
                    boxText: firstBox ? firstBox.innerText.replace(/\n+/g, ' | ') : null,
                    timerText: timerEl ? timerEl.innerText : null
                };
            })()
        """)
        checks.append(state)

    print("MONITOR RESULTS:\n", json.dumps(checks, indent=2))
    shot = lane.shot(client, "rewardjoy_ad_click_monitor")
    print("Screenshot:", shot)
