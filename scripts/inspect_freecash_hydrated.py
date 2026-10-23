import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("freecash", "inspect_offers")
with T.session(lane) as client:
    print("Waiting 6 seconds for DOM to hydrate...")
    time.sleep(6)

    data = client._js(r"""
        (function() {
            // Scroll down a bit to trigger lazy loading
            window.scrollBy(0, 400);

            var offers = [];
            document.querySelectorAll('a[href*="/earn/"], [class*="offer"], [class*="card"]').forEach(el => {
                var text = el.innerText.trim();
                if (text && text.length > 5 && text.length < 200 && text.includes('$')) {
                    offers.push(text.replace(/\n+/g, ' | '));
                }
            });

            var surveys = Array.from(document.querySelectorAll('button, a, div')).filter(el => {
                var t = (el.innerText || '').toLowerCase();
                return t.includes('cpx') || t.includes('bitlabs') || t.includes('inbrain') || t.includes('pollfish') || t.includes('your-surveys');
            }).map(el => el.innerText.trim().slice(0, 50));

            return {
                url: window.location.href,
                title: document.title,
                offers: offers.slice(0, 10),
                surveys: [...new Set(surveys)].slice(0, 10)
            };
        })()
    """)
    print("HYDRATED OFFERS:\n", json.dumps(data, indent=2))

    shot = lane.shot(client, "freecash_offers_hydrated")
    print("Screenshot:", shot)
