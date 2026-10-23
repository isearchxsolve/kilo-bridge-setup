import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("coinpayu", "inspect_ad_html")
with T.session(lane) as client:
    client.call_tool("browser_navigate", {"url": "https://www.rewardjoy.com/dashboard/ads_surf"})
    time.sleep(3)

    info = client._js(r"""
        (function() {
            var box = document.querySelector('.frameless-ad-box');
            if (!box) return { error: 'No ad box found' };

            var links = Array.from(box.querySelectorAll('a')).map(a => ({
                href: a.href,
                text: a.innerText,
                target: a.target
            }));

            return {
                html: box.outerHTML.slice(0, 1500),
                links: links
            };
        })()
    """)
    print("FIRST AD BOX HTML:\n", json.dumps(info, indent=2))
