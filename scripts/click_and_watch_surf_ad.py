r"""click_and_watch_surf_ad.py - Click surf ad on RewardJoy, wait countdown, verify credit.
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("coinpayu", "surf_ad_runner")
with T.session(lane) as client:
    print("Navigating to https://www.rewardjoy.com/dashboard/ads_surf...")
    client.call_tool("browser_navigate", {"url": "https://www.rewardjoy.com/dashboard/ads_surf"})
    time.sleep(3.5)

    # 1. Inspect initial balance and ad list
    init_info = client._js(r"""
        (function() {
            var ads = Array.from(document.querySelectorAll('.ags-description, .frameless-ad-box')).map(el => ({
                text: el.innerText.trim(),
                className: el.className
            }));
            var bal = document.querySelector('.user-money, .balance, [class*="money"], [class*="balance"]');
            var balText = bal ? bal.innerText : null;

            return {
                balanceText: balText,
                adsFound: ads.length,
                firstAd: ads[0] ? ads[0].text : null
            };
        })()
    """)
    print("INITIAL STATE:", json.dumps(init_info, indent=2))

    # 2. Click the first ad description
    click_res = client._js(r"""
        (function() {
            var target = document.querySelector('.ags-description');
            if (target) {
                target.click();
                return { ok: true, clickedText: target.innerText.trim() };
            }
            return { ok: false, error: 'No ad found' };
        })()
    """)
    print("CLICK RESULT:", json.dumps(click_res, indent=2))

    # 3. Wait for countdown (e.g. 35 seconds)
    print("Waiting 35 seconds for surf ad timer...")
    time.sleep(35)

    # 4. Check if countdown completed or credit received
    post_info = client._js(r"""
        (function() {
            var bal = document.querySelector('.user-money, .balance, [class*="money"], [class*="balance"]');
            return {
                url: window.location.href,
                balanceText: bal ? bal.innerText : null,
                bodySnippet: document.body.innerText.slice(0, 800)
            };
        })()
    """)
    print("POST STATE:", json.dumps(post_info, indent=2))

    shot = lane.shot(client, "rewardjoy_surf_ad_1_completed")
    print("Receipt Screenshot:", shot)
