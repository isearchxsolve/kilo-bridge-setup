r"""get_profile_link.py - Get the exact link for 'Click here to complete your profile'.
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("timebucks", "profile_link")
with T.session(lane) as client:
    url = "https://timebucks.com/publishers/index.php?pg=earn&tab=view_content_ads"
    client.call_tool("browser_navigate", {"url": url})
    time.sleep(3)

    link_data = client._js(r"""
        (function() {
            var links = Array.from(document.querySelectorAll('a'));
            var profileLink = links.find(l => (l.innerText || '').toLowerCase().includes('complete your profile') || (l.innerText || '').toLowerCase().includes('click here'));
            if (profileLink) {
                return {
                    found: true,
                    text: profileLink.innerText,
                    href: profileLink.getAttribute('href') || '',
                    absHref: profileLink.href || ''
                };
            }
            return {found: false};
        })()
    """)
    print("PROFILE LINK DATA:\n", json.dumps(link_data, indent=2))

    if link_data and link_data.get("found"):
        target_url = link_data.get("absHref") or link_data.get("href")
        print("Navigating to target:", target_url)
        client.call_tool("browser_navigate", {"url": target_url})
        time.sleep(3)
        shot = lane.shot(client, "timebucks_actual_profile_form")
        print("Shot saved:", shot)
        page = T.read_page(client)
        print("URL:", page.get("url"))
        print("TITLE:", page.get("title"))
        body = page.get("body", "")
        print("BODY SNIPPET:\n", body[:1200])
