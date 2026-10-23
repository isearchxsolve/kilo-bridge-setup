import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("freecash", "active_surveys")
with T.session(lane) as client:
    print("Navigating to https://freecash.com/en/earn...")
    client.call_tool("browser_navigate", {"url": "https://freecash.com/en/earn"})
    time.sleep(6)

    # Inspect all survey partner cards and direct survey cards
    data = client._js(r"""
        (function() {
            var cards = [];
            // Query all clickable items that might be surveys or offers
            var elements = Array.from(document.querySelectorAll('a, div[role="button"], button')).filter(el => {
                var text = (el.innerText || '').toLowerCase();
                return (
                    text.includes('cpx') || text.includes('bitlabs') || text.includes('inbrain') ||
                    text.includes('pollfish') || text.includes('timewall') || text.includes('survey') ||
                    (text.includes('$') && text.includes('min'))
                );
            });

            elements.forEach((el, idx) => {
                var text = el.innerText.trim().replace(/\n+/g, ' | ');
                if (text.length > 3 && text.length < 250) {
                    cards.push({
                        index: idx,
                        text: text,
                        tag: el.tagName,
                        href: el.getAttribute('href') || ''
                    });
                }
            });

            var bal = document.body.innerText.match(/\$\s*[\d\.]+/g);

            return {
                url: window.location.href,
                title: document.title,
                balancesFound: bal ? [...new Set(bal)].slice(0, 5) : [],
                cardsCount: cards.length,
                cards: cards.slice(0, 15)
            };
        })()
    """)
    print("FREECASH LIVE OFFERS & SURVEYS:\n", json.dumps(data, indent=2))
    shot = lane.shot(client, "freecash_live_surveys_list")
    print("Screenshot saved to:", shot)
