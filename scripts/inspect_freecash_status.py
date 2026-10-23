import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("freecash", "inspect_status")
with T.session(lane) as client:
    print("Checking current page state...")
    info = client._js(r"""
        (function() {
            return {
                url: window.location.href,
                title: document.title,
                bodySnippet: document.body.innerText.slice(0, 1000)
            };
        })()
    """)
    print("CURRENT PAGE:\n", json.dumps(info, indent=2))

    # If not on freecash, or if on freecash login, check
    if "freecash.com" not in info.get("url", ""):
        print("Navigating to https://freecash.com...")
        client.call_tool("browser_navigate", {"url": "https://freecash.com"})
        time.sleep(5)
    
    # Detailed check
    fc_info = client._js(r"""
        (function() {
            var coins = document.querySelector('[data-testid="header-coins"], [class*="coins"], [class*="balance"], [class*="user-balance"]');
            var avatar = document.querySelector('[data-testid="header-user-avatar"], [class*="avatar"], img[alt*="avatar"], [class*="profile"]');
            var signinBtns = Array.from(document.querySelectorAll('button, a')).filter(el => {
                var t = (el.innerText || '').toLowerCase();
                return t.includes('sign in') || t.includes('log in') || t.includes('sign up');
            }).map(el => el.innerText.trim());

            return {
                url: window.location.href,
                title: document.title,
                hasBalance: !!coins,
                balanceText: coins ? coins.innerText.trim() : null,
                hasAvatar: !!avatar,
                signinBtns: signinBtns.slice(0, 5),
                bodySample: document.body.innerText.slice(0, 800)
            };
        })()
    """)
    print("FREECASH INSPECTION:\n", json.dumps(fc_info, indent=2))

    shot = lane.shot(client, "freecash_status_check")
    print("Screenshot saved to:", shot)
