r"""click_profile_modal.py - Inspect onclick handler and click 'Click here'.
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("timebucks", "click_profile")
with T.session(lane) as client:
    url = "https://timebucks.com/publishers/index.php?pg=earn&tab=view_content_ads"
    client.call_tool("browser_navigate", {"url": url})
    time.sleep(3)

    link_info = client._js(r"""
        (function() {
            var links = Array.from(document.querySelectorAll('a'));
            var target = links.find(l => (l.innerText || '').toLowerCase().includes('click here'));
            if (!target) return {found: false};
            return {
                found: true,
                outerHTML: target.outerHTML,
                onclick: target.getAttribute('onclick'),
                href: target.getAttribute('href')
            };
        })()
    """)
    print("LINK INFO:", json.dumps(link_info, indent=2))

    print("Triggering .click() on target...")
    click_res = client._js(r"""
        (function() {
            var links = Array.from(document.querySelectorAll('a'));
            var target = links.find(l => (l.innerText || '').toLowerCase().includes('click here'));
            if (target) {
                target.click();
                return {clicked: true};
            }
            return {clicked: false};
        })()
    """)
    print("CLICK RESULT:", click_res)
    time.sleep(3)

    shot = lane.shot(client, "timebucks_after_profile_click")
    print("Screenshot saved to:", shot)
    page = T.read_page(client)
    print("URL after click:", page.get("url"))
    print("BODY SNIPPET:\n", page.get("body", "")[300:1500])
