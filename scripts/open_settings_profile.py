r"""open_settings_profile.py - Open settings profile page and extract form HTML.
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("timebucks", "settings_profile")
with T.session(lane) as client:
    url = "https://timebucks.com/publishers/index.php?pg=setting"
    print("Navigating to:", url)
    client.call_tool("browser_navigate", {"url": url})
    time.sleep(3.5)

    shot = lane.shot(client, "timebucks_settings_main")
    print("Screenshot saved to:", shot)
    page = T.read_page(client)
    print("URL:", page.get("url"))
    print("TITLE:", page.get("title"))

    # Extract all tabs under Settings
    setting_tabs = client._js(r"""
        (function() {
            var links = Array.from(document.querySelectorAll('a, button, li'));
            return links
                .map(l => ({text: (l.innerText || '').trim(), href: l.getAttribute('href') || ''}))
                .filter(x => ['profile', 'password', 'email', 'payment method', 'username'].includes(x.text.toLowerCase()));
        })()
    """)
    print("SETTING TABS:", json.dumps(setting_tabs, indent=2))
