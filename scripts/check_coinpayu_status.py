r"""check_coinpayu_status.py - Check if CoinPayU / RewardJoy is now logged in.
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("coinpayu", "auth_check")
with T.session(lane) as client:
    url = "https://www.coinpayu.com/dashboard"
    print("Navigating to CoinPayU:", url)
    client.call_tool("browser_navigate", {"url": url})
    time.sleep(4)

    shot = lane.shot(client, "coinpayu_live_status")
    print("Screenshot saved to:", shot)

    page = T.read_page(client)
    body = page.get("body", "")
    current_url = page.get("url", "")
    print("COINPAYU CURRENT URL:", current_url)
    print("COINPAYU PAGE TITLE:", page.get("title"))

    is_logged_in = "dashboard" in current_url.lower() and "login" not in current_url.lower()
    print("IS LOGGED IN?", is_logged_in)
    if is_logged_in:
        print("BODY SNIPPET:\n", body[:800])
