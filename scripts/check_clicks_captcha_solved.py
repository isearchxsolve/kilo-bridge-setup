r"""check_clicks_captcha_solved.py - Check if Clicks CAPTCHA is solved.
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("timebucks", "clicks_live")
with T.session(lane) as client:
    url = "https://timebucks.com/publishers/index.php?pg=earn&tab=view_content_ads"
    client.call_tool("browser_navigate", {"url": url})
    time.sleep(3.5)

    shot = lane.shot(client, "timebucks_clicks_current_state")
    page = T.read_page(client)
    body = page.get("body", "")
    has_captcha = "captcha required" in body.lower()
    print("HAS CAPTCHA:", has_captcha)

    # Check for view buttons
    buttons = client._js(r"""
        (function() {
            var allBtns = Array.from(document.querySelectorAll('input, button, a'));
            var viewBtns = allBtns.filter(b => {
                var val = (b.value || b.innerText || '').toLowerCase().trim();
                return val === 'view' || val.includes('view ad');
            });
            return {
                viewCount: viewBtns.length,
                details: viewBtns.slice(0, 5).map(b => (b.closest('tr, div') ? b.closest('tr, div').innerText : ''))
            };
        })()
    """)
    print("VIEW BUTTONS DETECTED:\n", json.dumps(buttons, indent=2))
