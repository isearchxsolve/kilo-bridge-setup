r"""run_live_clicks_batch.py - Inspect unlocked click campaigns, execute first batch, capture receipts.
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("timebucks", "clicks_batch")
with T.session(lane) as client:
    tabs = client.list_tabs()
    tb_tab = next((t for t in tabs if "timebucks.com" in t.get("url", "").lower()), None)
    if tb_tab:
        client.switch_tab(tb_tab["id"])
        time.sleep(1)
    else:
        client.call_tool("browser_navigate", {"url": "https://timebucks.com/publishers/index.php?pg=earn&tab=view_content_ads"})
        time.sleep(3)

    # Re-read page to confirm unlock
    page = T.read_page(client)
    body = page.get("body", "")
    print("PAGE TITLE:", page.get("title"))
    print("PAGE URL:", page.get("url"))
    has_captcha = "captcha required" in body.lower()
    print("HAS CAPTCHA STILL?", has_captcha)

    shot = lane.shot(client, "timebucks_clicks_unlocked_confirmed")
    print("Screenshot saved to:", shot)

    # Extract all available click ads
    ads_data = client._js(r"""
        (function() {
            var allBtns = Array.from(document.querySelectorAll('input, button, a'));
            var viewBtns = allBtns.filter(b => {
                var val = (b.value || b.innerText || '').toLowerCase().trim();
                return val === 'view' || val.includes('view ad') || val === 'click';
            });

            var offerList = viewBtns.map(b => {
                var row = b.closest('tr, div.offer, div.card, div[class*="campaign"], div[class*="content"]') || b.parentElement;
                var text = row ? row.innerText.replace(/\s+/g, ' ') : '';
                return {
                    tag: b.tagName,
                    val: b.value || b.innerText || '',
                    id: b.id || '',
                    textSnippet: text.slice(0, 150)
                };
            });

            return {
                count: viewBtns.length,
                offers: offerList.slice(0, 10),
                bodyPreview: document.body.innerText.slice(500, 1500)
            };
        })()
    """)

    print("DETECTED CLICK ADS:\n", json.dumps(ads_data, indent=2))
