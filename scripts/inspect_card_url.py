import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("freecash", "inspect_partner_url")
with T.session(lane) as client:
    print("Navigating to https://freecash.com/en/earn...")
    client.call_tool("browser_navigate", {"url": "https://freecash.com/en/earn"})
    time.sleep(6)
    client._js("window.scrollTo(0, 900);")
    time.sleep(3)

    info = client._js(r"""
        (function() {
            var span = Array.from(document.querySelectorAll('span')).find(s => (s.innerText || '').trim() === 'CPX Research' || (s.innerText || '').trim() === 'BitLabs');
            if (!span) return { error: 'No span found' };

            var cur = span;
            var dataDump = {};

            while (cur && cur !== document.body) {
                var fiberKey = Object.keys(cur).find(k => k.startsWith('__reactFiber$'));
                var propKey = Object.keys(cur).find(k => k.startsWith('__reactProps$'));
                if (propKey && cur[propKey]) {
                    var p = cur[propKey];
                    dataDump.propsKeys = Object.keys(p);
                    dataDump.href = p.href || (p.to ? p.to : null);
                    dataDump.partner = p.partner || p.offer || p.data || p.item;
                }
                if (fiberKey && cur[fiberKey]) {
                    var f = cur[fiberKey];
                    var memo = f.memoizedProps;
                    if (memo) {
                        dataDump.memoKeys = Object.keys(memo);
                        if (memo.partner || memo.url || memo.href || memo.offer) {
                            dataDump.fiberData = memo.partner || memo.url || memo.href || memo.offer;
                        }
                    }
                }
                cur = cur.parentElement;
            }

            return dataDump;
        })()
    """)
    print("DATA DUMP:\n", json.dumps(info, indent=2, default=str))
