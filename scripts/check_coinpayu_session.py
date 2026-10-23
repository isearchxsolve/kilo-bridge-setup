r"""check_coinpayu_session.py - Navigate to CoinPayU dashboard and check authentication.
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("coinpayu", "check_auth")
with T.session(lane) as client:
    print("Navigating to CoinPayU...")
    client.call_tool("browser_navigate", {"url": "https://www.coinpayu.com/dashboard"})
    time.sleep(4)

    page = T.read_page(client)
    url = page.get("url", "")
    title = page.get("title", "")
    body = page.get("body", "")

    shot = lane.shot(client, "coinpayu_landing_check")
    print("PAGE URL:", url)
    print("PAGE TITLE:", title)
    print("SCREENSHOT:", shot)

    # Check if dashboard elements or login buttons are visible
    auth_check = client._js(r"""
        (function() {
            var text = document.body.innerText || '';
            var isDashboard = text.includes('Main Balance') || text.includes('Purchase Balance') || text.includes('Referrals');
            var isLogin = text.includes('Login') || text.includes('Register') || window.location.href.includes('login');
            var balanceMatch = text.match(/([0-9,]+)\s*Satoshi/i) || text.match(/Main Balance[:\s]*([0-9,]+)/i);

            return {
                url: window.location.href,
                isDashboard: isDashboard,
                isLogin: isLogin,
                balance: balanceMatch ? balanceMatch[0] : null,
                bodySnippet: text.slice(0, 500)
            };
        })()
    """)

    print("AUTH CHECK RESULT:\n", json.dumps(auth_check, indent=2))
