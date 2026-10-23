r"""open_freecash_for_user.py - Navigate to Freecash so the user can log in.
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("freecash", "login_gate")
with T.session(lane) as client:
    print("Navigating to https://freecash.com...")
    client.call_tool("browser_navigate", {"url": "https://freecash.com"})
    time.sleep(5)

    info = client._js(r"""
        (function() {
            var btns = Array.from(document.querySelectorAll('button, a')).map(b => ({
                text: (b.innerText || '').trim(),
                href: b.getAttribute('href') || ''
            })).filter(x => x.text.toLowerCase().includes('sign in') || x.text.toLowerCase().includes('log in') || x.text.toLowerCase().includes('google'));

            return {
                url: window.location.href,
                title: document.title,
                authButtons: btns.slice(0, 10),
                bodySample: document.body.innerText.slice(0, 500)
            };
        })()
    """)
    print("FREECASH STATE:\n", json.dumps(info, indent=2))

    shot = lane.shot(client, "freecash_login_gate")
    print("Freecash Screenshot:", shot)
