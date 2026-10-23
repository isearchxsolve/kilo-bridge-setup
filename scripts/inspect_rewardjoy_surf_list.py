import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("coinpayu", "inspect_surf_list")
with T.session(lane) as client:
    print("Navigating to https://www.rewardjoy.com/dashboard/ads_surf...")
    client.call_tool("browser_navigate", {"url": "https://www.rewardjoy.com/dashboard/ads_surf"})
    time.sleep(4)

    info = client._js(r"""
        (function() {
            var boxes = Array.from(document.querySelectorAll('.frameless-ad-box, tr, [class*="ad-box"], [class*="surf"]'));
            var results = [];

            // Let's also look at all .ags-description
            var descs = Array.from(document.querySelectorAll('.ags-description'));
            descs.forEach((d, idx) => {
                var parent = d.closest('.frameless-ad-box') || d.parentElement;
                var text = d.innerText.trim();
                var fullText = parent ? parent.innerText.trim().replace(/\n+/g, ' | ') : text;
                var isVisited = d.classList.contains('visited') || (parent && parent.classList.contains('visited')) || d.style.color === 'gray';
                results.push({
                    index: idx,
                    title: text,
                    fullInfo: fullText,
                    classes: d.className,
                    parentClasses: parent ? parent.className : ''
                });
            });

            var bal = document.querySelector('.user-money, .balance, [class*="balance"], [class*="money"]');

            return {
                url: window.location.href,
                balance: bal ? bal.innerText.trim() : null,
                totalAds: descs.length,
                ads: results
            };
        })()
    """)

    print("SURF ADS STATUS:\n", json.dumps(info, indent=2))
