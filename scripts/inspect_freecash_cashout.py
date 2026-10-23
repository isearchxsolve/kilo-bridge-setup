import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("freecash", "inspect_cashout")
with T.session(lane) as client:
    print("Navigating to https://freecash.com/en/cashout...")
    client.call_tool("browser_navigate", {"url": "https://freecash.com/en/cashout"})
    time.sleep(5)

    cashout_info = client._js(r"""
        (function() {
            var options = Array.from(document.querySelectorAll('a, div, button')).filter(el => {
                var text = (el.innerText || '').toLowerCase();
                return (text.includes('litecoin') || text.includes('crypto') || text.includes('bitcoin') || text.includes('upi') || text.includes('bank') || text.includes('gift card') || text.includes('airtm') || text.includes('stake'));
            }).map(el => ({
                text: el.innerText.trim().slice(0, 100),
                tagName: el.tagName,
                href: el.getAttribute('href') || ''
            }));

            var bal = document.body.innerText.match(/\$\s*[\d\.]+/g);

            return {
                url: window.location.href,
                title: document.title,
                detectedBalances: bal ? bal.slice(0, 5) : [],
                bodySample: document.body.innerText.slice(0, 1000)
            };
        })()
    """)
    print("FREECASH CASHOUT INSPECTION:\n", json.dumps(cashout_info, indent=2))

    shot = lane.shot(client, "freecash_cashout_options")
    print("Screenshot saved to:", shot)

    # Record ledger row
    lane.row("freecash.com/en/cashout", "Cashout Inspection", "Freecash", 0, "inspect_cashout_options", T.OK, shot, "Freecash authenticated as Kunal with $0.50 balance")
