r"""inspect_rewardjoy.py - Inspect RewardJoy authenticated state and browsing/surf ads tab.
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("coinpayu", "rewardjoy_surf")
with T.session(lane) as client:
    print("Navigating to https://www.rewardjoy.com/dashboard/offers...")
    client.call_tool("browser_navigate", {"url": "https://www.rewardjoy.com/dashboard/offers"})
    time.sleep(3.5)

    shot = lane.shot(client, "rewardjoy_authenticated_dashboard")
    print("Dashboard receipt:", shot)

    # Inspect left sidebar navigation links (especially 'ब्राउज़िंग' / Browsing / Surf ads)
    nav_info = client._js(r"""
        (function() {
            var links = Array.from(document.querySelectorAll('a, div[role="button"], button')).map(el => ({
                tag: el.tagName,
                text: (el.innerText || '').trim(),
                href: el.getAttribute('href') || '',
                className: el.className || ''
            })).filter(x => x.text.length > 0 && x.text.length < 40);

            return {
                url: window.location.href,
                title: document.title,
                links: links.slice(0, 30)
            };
        })()
    """)
    print("REWARDJOY NAV LINKS:\n", json.dumps(nav_info, indent=2))

    # Find the link for 'ब्राउज़िंग' (Browsing) or surf ads and click it
    click_res = client._js(r"""
        (function() {
            var surfLink = Array.from(document.querySelectorAll('a, div, span, p')).find(el => {
                var t = (el.innerText || '').trim();
                return t.includes('ब्राउज़िंग') || t.toLowerCase().includes('browsing') || t.toLowerCase().includes('surf');
            });

            if (surfLink) {
                var clickable = surfLink.closest('a') || surfLink;
                clickable.click();
                return { ok: true, clickedText: surfLink.innerText.trim(), href: clickable.getAttribute('href') };
            }
            return { ok: false, error: 'Browsing link not found' };
        })()
    """)
    print("Click browsing result:", json.dumps(click_res, indent=2))
    time.sleep(4)

    # Inspect the browsing/ads page
    ads_page_info = client._js(r"""
        (function() {
            var items = Array.from(document.querySelectorAll('a, button, tr, div[class*="item"], div[class*="ad"]')).map(el => ({
                text: el.innerText ? el.innerText.replace(/\s+/g, ' ').trim() : '',
                href: el.getAttribute ? el.getAttribute('href') : ''
            })).filter(x => x.text.length > 0 && (x.text.includes('$') || x.text.includes('sec') || x.text.includes('s') || x.text.includes('Coin') || x.text.includes('सर्फ')));

            return {
                url: window.location.href,
                title: document.title,
                bodySnippet: document.body.innerText.slice(0, 1000),
                itemsSample: items.slice(0, 15)
            };
        })()
    """)
    print("ADS PAGE INFO:\n", json.dumps(ads_page_info, indent=2))

    shot_ads = lane.shot(client, "rewardjoy_browsing_ads_tab")
    print("Ads Tab Screenshot:", shot_ads)
