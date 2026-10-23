r"""execute_clicks_probe.py - Check if Clicks campaigns are now visible and execute.
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("timebucks", "clicks_exec")
with T.session(lane) as client:
    tabs = client.list_tabs()
    tb_tab = next((t for t in tabs if "timebucks.com" in t.get("url", "").lower()), None)
    if tb_tab:
        client.switch_tab(tb_tab["id"])
    else:
        client.call_tool("browser_navigate", {"url": "https://timebucks.com/publishers/index.php?pg=earn&tab=view_content_ads"})
        time.sleep(3)

    # Read current state
    page = T.read_page(client)
    body = page.get("body", "")
    print("CURRENT URL:", page.get("url"))
    print("CURRENT TITLE:", page.get("title"))
    has_captcha = "captcha required" in body.lower()
    print("HAS CAPTCHA:", has_captcha)

    shot = lane.shot(client, "timebucks_clicks_live_state")
    print("Screenshot saved to:", shot)

    # Check for view buttons and offer details
    offers_info = client._js(r"""
        (function() {
            var bodyText = document.body.innerText || '';
            var allBtns = Array.from(document.querySelectorAll('input, button, a'));
            var viewBtns = allBtns.filter(b => {
                var val = (b.value || b.innerText || '').toLowerCase().trim();
                return val === 'view' || val.includes('view ad');
            });

            var offerRows = Array.from(document.querySelectorAll('.offer-row, tr, div[class*="campaign"]'));
            var details = viewBtns.map(b => {
                var p = b.closest('tr, div') || b.parentElement;
                return {
                    buttonTag: b.tagName,
                    buttonVal: b.value || b.innerText || '',
                    text: (p ? p.innerText : '').slice(0, 200).replace(/\s+/g, ' ')
                };
            });

            return {
                viewCount: viewBtns.length,
                details: details.slice(0, 5),
                bodySnippet: bodyText.slice(300, 1500)
            };
        })()
    """)
    print("OFFERS DETECTED:\n", json.dumps(offers_info, indent=2))
