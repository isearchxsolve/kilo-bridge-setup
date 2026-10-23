r"""inspect_surf_ad_elements.py - Inspect elements inside each surf ad on RewardJoy.
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("coinpayu", "inspect_surf_cards")
with T.session(lane) as client:
    print("Navigating to https://www.rewardjoy.com/dashboard/ads_surf...")
    client.call_tool("browser_navigate", {"url": "https://www.rewardjoy.com/dashboard/ads_surf"})
    time.sleep(3.5)

    res = client._js(r"""
        (function() {
            var cards = Array.from(document.querySelectorAll('*')).filter(el => {
                var t = (el.innerText || '').trim();
                return t.includes('$ 0.007') || t.includes('EARN $780');
            });

            // Find all clickable links or titles in the ads list
            var adLinks = Array.from(document.querySelectorAll('a, div, span, p')).filter(el => {
                var t = (el.innerText || '').trim();
                return (
                    t === 'EARN $780 PER DAY - NO INVESTMENT' ||
                    t.startsWith('Winvest.com') ||
                    t.startsWith('Coins.Game') ||
                    t === 'King of the Faucets'
                );
            }).map(el => ({
                tag: el.tagName,
                text: el.innerText.trim(),
                href: el.getAttribute ? el.getAttribute('href') : null,
                onclick: el.getAttribute ? el.getAttribute('onclick') : null,
                className: el.className || '',
                parentTag: el.parentElement ? el.parentElement.tagName : null,
                parentHref: el.parentElement ? el.parentElement.getAttribute('href') : null
            }));

            return {
                url: window.location.href,
                adLinks: adLinks
            };
        })()
    """)

    print("SURF AD ELEMENTS:\n", json.dumps(res, indent=2))
