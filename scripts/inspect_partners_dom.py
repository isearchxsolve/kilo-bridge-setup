import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("freecash", "inspect_partners_dom")
with T.session(lane) as client:
    # Do not re-navigate to about:blank if already on freecash, or navigate to freecash.com/en/earn
    client.call_tool("browser_navigate", {"url": "https://freecash.com/en/earn"})
    time.sleep(6)
    client._js("window.scrollTo(0, document.body.scrollHeight / 2);")
    time.sleep(3)

    info = client._js(r"""
        (function() {
            var allPartners = [];
            // Find all cards with names like BitLabs, CPX, TimeWall, AdGate, etc.
            var names = ['BitLabs', 'CPX Research', 'TimeWall', 'AdGate', 'Torox', 'Ayet Studios'];
            names.forEach(name => {
                var el = Array.from(document.querySelectorAll('*')).find(x => x.children.length === 0 && (x.innerText || '').trim() === name);
                if (el) {
                    var parent = el.closest('div[class*="card"], div[class*="partner"], a, button') || el.parentElement;
                    allPartners.push({
                        name: name,
                        tag: el.tagName,
                        parentTag: parent ? parent.tagName : null,
                        parentClass: parent ? parent.className : '',
                        parentHref: parent ? parent.getAttribute('href') : null,
                        parentOnClick: parent ? parent.getAttribute('onclick') : null
                    });
                }
            });

            return {
                scrollY: window.scrollY,
                partners: allPartners
            };
        })()
    """)
    print("PARTNERS DOM INSPECTION:\n", json.dumps(info, indent=2))
