r"""inspect_primeearn_policy.py - Inspect policy elements and continue button on PrimeEarn.
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("timebucks", "primeearn_policy")
with T.session(lane) as client:
    client.call_tool("browser_navigate", {"url": "https://monetize.primeearn.com/policy"})
    time.sleep(3.5)
    res = client._js(r"""
        (function() {
            var allBtns = Array.from(document.querySelectorAll('button, input, a, div[role="button"]')).map(el => ({
                tag: el.tagName,
                type: el.type || '',
                id: el.id || '',
                className: el.className || '',
                text: (el.innerText || el.value || '').trim()
            })).filter(b => b.text.length > 0 && b.text.length < 50);

            return {
                url: window.location.href,
                title: document.title,
                allClickables: allBtns,
                fullText: document.body.innerText.slice(0, 1500)
            };
        })()
    """)

    print("PRIMEEARN POLICY INSPECTION:\n", json.dumps(res, indent=2))
    shot = lane.shot(client, "primeearn_policy_view")
    print("Screenshot:", shot)
