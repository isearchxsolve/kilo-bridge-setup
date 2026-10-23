r"""inspect_clicks_tab.py - Navigate to Clicks tab and inspect available ads.
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("timebucks", "clicks_tab")
with T.session(lane) as client:
    url = "https://timebucks.com/publishers/index.php?pg=earn&tab=view_content_ads"
    print("Navigating to:", url)
    client.call_tool("browser_navigate", {"url": url})
    time.sleep(4)

    shot = lane.shot(client, "timebucks_clicks_offers")
    print("Screenshot saved to:", shot)

    page = T.read_page(client)
    print("PAGE TITLE:", page.get("title"))
    print("PAGE URL:", page.get("url"))

    # Extract ad offers
    ads_info = client._js(r"""
        (function() {
            var bodyText = document.body.innerText || '';
            // Look for View buttons or offer blocks
            var buttons = Array.from(document.querySelectorAll('input[type="submit"], input[type="button"], button, a.btn, a[class*="btn"]'));
            var viewButtons = buttons.map(b => ({
                tag: b.tagName,
                value: b.value || '',
                text: (b.innerText || '').trim(),
                href: b.getAttribute('href') || '',
                onclick: b.getAttribute('onclick') || '',
                id: b.id || '',
                className: b.className || ''
            }));

            // Also check table rows or offer cards
            var rows = Array.from(document.querySelectorAll('table tr, .offer-card, .card, div[class*="offer"]'));
            var rowTexts = rows.map(r => (r.innerText || '').trim().replace(/\s+/g, ' ')).filter(t => t.length > 10 && t.length < 300);

            return {
                buttonsCount: buttons.length,
                viewButtons: viewButtons,
                sampleRowTexts: rowTexts.slice(0, 10),
                bodySnippet: bodyText.slice(0, 1500)
            };
        })()
    """)

    print("ADS INFO SUMMARY:")
    print("Buttons found:", ads_info.get("buttonsCount"))
    print("View buttons:", json.dumps(ads_info.get("viewButtons"), indent=2))
    print("Sample rows:", json.dumps(ads_info.get("sampleRowTexts"), indent=2))
    print("Body snippet:\n", ads_info.get("bodySnippet", "")[:800])
