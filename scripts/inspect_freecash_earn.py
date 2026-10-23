import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("freecash", "inspect_earn")
with T.session(lane) as client:
    print("Navigating to https://freecash.com/en/earn...")
    client.call_tool("browser_navigate", {"url": "https://freecash.com/en/earn"})
    time.sleep(5)

    earn_data = client._js(r"""
        (function() {
            var items = [];
            // look for featured offers, quick tasks, or survey partners
            var cards = document.querySelectorAll('[class*="offer-card"], [class*="OfferCard"], [class*="survey-card"], [class*="card"]');
            cards.forEach(c => {
                var title = c.querySelector('[class*="title"], h3, h4, [class*="name"]');
                var payout = c.querySelector('[class*="reward"], [class*="payout"], [class*="coins"], [class*="money"]');
                if (title || payout) {
                    items.push({
                        title: title ? title.innerText.trim() : '',
                        payout: payout ? payout.innerText.trim() : '',
                        textSample: c.innerText.slice(0, 100).replace(/\n/g, ' ')
                    });
                }
            });

            // Also check for survey providers list (CPX, Bitlabs, inBrain, etc.)
            var partners = Array.from(document.querySelectorAll('a, div')).filter(el => {
                var t = (el.innerText || '').toLowerCase();
                return (t.includes('cpx') || t.includes('bitlabs') || t.includes('inbrain') || t.includes('pollfish') || t.includes('timewall') || t.includes('torox') || t.includes('revu'));
            }).map(el => el.innerText.trim().slice(0, 80));

            return {
                url: window.location.href,
                itemsCount: items.length,
                topItems: items.slice(0, 15),
                partners: [...new Set(partners)].slice(0, 10),
                bodySample: document.body.innerText.slice(0, 1500)
            };
        })()
    """)
    print("FREECASH EARN DATA:\n", json.dumps(earn_data, indent=2))

    shot = lane.shot(client, "freecash_earn_catalog")
    print("Screenshot saved to:", shot)
