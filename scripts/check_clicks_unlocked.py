r"""check_clicks_unlocked.py - Verify Clicks tab is now unlocked.
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("timebucks", "clicks_check")
with T.session(lane) as client:
    url = "https://timebucks.com/publishers/index.php?pg=earn&tab=view_content_ads"
    print("Navigating to Clicks tab:", url)
    client.call_tool("browser_navigate", {"url": url})
    time.sleep(4)

    shot = lane.shot(client, "timebucks_clicks_unlocked_view")
    print("Screenshot saved to:", shot)

    page = T.read_page(client)
    body = page.get("body", "")
    print("PAGE TITLE:", page.get("title"))
    print("PAGE URL:", page.get("url"))
    print("Profile gate still present?", "complete your profile" in body.lower()[:1500])

    # Check available click ads
    ads_data = client._js(r"""
        (function() {
            var bodyText = document.body.innerText || '';
            var buttons = Array.from(document.querySelectorAll('input[type="submit"], input[type="button"], button, a.btn, a[class*="btn"]'));
            var viewBtns = buttons.filter(b => {
                var t = (b.value || b.innerText || '').toLowerCase().trim();
                return t === 'view' || t.includes('view') || t === 'click';
            }).map(b => ({
                tag: b.tagName,
                value: b.value || '',
                text: b.innerText || '',
                id: b.id || '',
                className: b.className || ''
            }));

            // Check any text showing offers count or available ads
            var match = bodyText.match(/Total offers available:\s*(\d+)/i) ||
                        bodyText.match(/(\d+)\s*offers? available/i) ||
                        bodyText.match(/You can earn:\s*\$([0-9\.]+)/i);

            return {
                viewButtonsCount: viewBtns.length,
                viewButtons: viewBtns.slice(0, 5),
                matchInfo: match ? match[0] : null,
                bodySnippet: bodyText.slice(500, 2000)
            };
        })()
    """)
    print("ADS DATA:\n", json.dumps(ads_data, indent=2))
