r"""probe_instant_claims.py - Inspect Hourly Crown, Daily Streak, and Bonus Clicks for instant free earnings.
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("timebucks", "instant_claims")
urls = [
    ("Hourly Crown", "https://timebucks.com/publishers/index.php?pg=earn&tab=hourly_crown"),
    ("Daily Streak", "https://timebucks.com/publishers/index.php?pg=earn&tab=daily_streak"),
    ("Bonus Clicks", "https://timebucks.com/publishers/index.php?pg=earn&tab=bonus_clicks")
]

with T.session(lane) as client:
    for name, url in urls:
        print(f"--- Probing {name} ({url}) ---")
        client.call_tool("browser_navigate", {"url": url})
        time.sleep(3.5)

        info = client._js(r"""
            (function() {
                var buttons = Array.from(document.querySelectorAll('input[type="button"], input[type="submit"], button, a.btn')).map(b => ({
                    val: (b.value || b.innerText || '').trim(),
                    tag: b.tagName,
                    id: b.id,
                    className: b.className
                })).filter(b => b.val.length > 0 && b.val.length < 50);

                return {
                    title: document.title,
                    url: window.location.href,
                    buttons: buttons,
                    textSnippet: document.body.innerText.slice(400, 1600)
                };
            })()
        """)

        shot = lane.shot(client, f"timebucks_{name.lower().replace(' ', '_')}")
        print(f"{name} Result:\n", json.dumps(info, indent=2))
        print("Screenshot:", shot)
