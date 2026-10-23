r"""check_tools_and_open_sites.py - Check available Agent360 tools and navigate to target login pages.
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("timebucks", "open_sites")
with T.session(lane) as client:
    # 1. First, navigate to CoinPayU login page
    print("Navigating to CoinPayU login...")
    client.call_tool("browser_navigate", {"url": "https://www.coinpayu.com/login"})
    time.sleep(4)

    coinpayu_info = client._js(r"""
        (function() {
            return {
                url: window.location.href,
                title: document.title,
                body: document.body.innerText.slice(0, 500)
            };
        })()
    """)
    print("COINPAYU STATE:\n", json.dumps(coinpayu_info, indent=2))
    shot_cpu = lane.shot(client, "coinpayu_login_page")
    print("CoinPayU Screenshot:", shot_cpu)
