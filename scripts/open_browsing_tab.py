r"""open_browsing_tab.py - Click 'ब्राउज़िंग' on RewardJoy and inspect available surf ads.
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("coinpayu", "browsing_ads")
with T.session(lane) as client:
    print("Navigating to https://www.rewardjoy.com/dashboard/offers...")
    client.call_tool("browser_navigate", {"url": "https://www.rewardjoy.com/dashboard/offers"})
    time.sleep(3.5)

    # Click on 'ब्राउज़िंग' sidebar item
    click_res = client._js(r"""
        (function() {
            var items = Array.from(document.querySelectorAll('*')).filter(el => {
                var t = (el.innerText || '').trim();
                return t === 'ब्राउज़िंग' || t.includes('ब्राउज़िंग');
            });

            if (items.length > 0) {
                // Click the deepest element or its parent button/link
                var target = items[items.length - 1];
                var clickTarget = target.closest('a') || target.closest('div[role="button"]') || target.parentElement || target;
                clickTarget.click();
                return {
                    ok: true,
                    clickedTag: clickTarget.tagName,
                    text: target.innerText.trim(),
                    href: clickTarget.getAttribute ? clickTarget.getAttribute('href') : null
                };
            }
            return { ok: false, error: 'ब्राउज़िंग not found' };
        })()
    """)
    print("Click result:", json.dumps(click_res, indent=2))
    time.sleep(4)

    # Inspect the resulting page
    page_info = client._js(r"""
        (function() {
            var bodyText = document.body.innerText;
            var ads = Array.from(document.querySelectorAll('a, button, .ad-card, .surf-item, tr')).map(el => ({
                text: el.innerText ? el.innerText.replace(/\s+/g, ' ').trim() : '',
                href: el.getAttribute ? el.getAttribute('href') : '',
                tag: el.tagName
            })).filter(x => x.text.length > 0 && x.text.length < 150 && (
                x.text.includes('$') || x.text.includes('sec') || x.text.includes('s') || x.text.includes('सर्फ') || x.text.includes('कॉइन')
            ));

            return {
                url: window.location.href,
                title: document.title,
                bodySnippet: bodyText.slice(0, 1000),
                adsCount: ads.length,
                adsSample: ads.slice(0, 15)
            };
        })()
    """)
    print("PAGE INFO AFTER CLICK:\n", json.dumps(page_info, indent=2))

    shot = lane.shot(client, "rewardjoy_browsing_page_live")
    print("Screenshot:", shot)
