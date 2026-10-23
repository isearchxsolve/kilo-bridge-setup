import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("freecash", "inspect_routes")
with T.session(lane) as client:
    print("Navigating to https://freecash.com/en/earn...")
    client.call_tool("browser_navigate", {"url": "https://freecash.com/en/earn"})
    time.sleep(6)

    info = client._js(r"""
        (function() {
            var links = Array.from(document.querySelectorAll('a[href]')).map(a => ({
                href: a.getAttribute('href'),
                text: a.innerText.trim().slice(0, 50)
            })).filter(x => x.href && !x.href.startsWith('#'));

            return {
                url: window.location.href,
                linksCount: links.length,
                links: links.slice(0, 30)
            };
        })()
    """)
    print("FREECASH LINKS:\n", json.dumps(info, indent=2))
