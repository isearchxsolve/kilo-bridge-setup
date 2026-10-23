r"""list_fast_surveys.py - Find all fast (<= 5 min), high-yield surveys on TimeBucks.
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("timebucks", "fast_surveys")
with T.session(lane) as client:
    print("Navigating to all_surveys...")
    client.call_tool("browser_navigate", {"url": "https://timebucks.com/publishers/index.php?pg=earn&tab=all_surveys"})
    time.sleep(3.5)

    fast_list = client._js(r"""
        (function() {
            var cards = Array.from(document.querySelectorAll('.survey-card, div[id^="survey-"]'));
            var results = [];

            cards.forEach(c => {
                var btn = c.querySelector('.btn-start') || c.querySelector('button');
                var rateEl = c.querySelector('.survey-rate') || c;
                var rate = (rateEl.innerText || '').match(/\$[\d.]+/g);
                var lastRate = rate ? rate[rate.length - 1] : '';
                var text = (c.innerText || '').replace(/\s+/g, ' ').trim();
                var minMatch = text.match(/(\d+)\s*min/);
                var minutes = minMatch ? parseInt(minMatch[1], 10) : 999;
                var provider = c.getAttribute('data-provider') || (btn ? btn.getAttribute('data-provider') : '');
                var link = btn ? (btn.getAttribute('data-link') || btn.getAttribute('href')) : '';

                results.push({
                    id: c.id,
                    provider: provider,
                    rateText: lastRate,
                    rateVal: parseFloat(lastRate.replace('$', '')) || 0,
                    minutes: minutes,
                    link: link,
                    fullText: text
                });
            });

            // Sort by: highest rate / minute (yield efficiency)
            results.sort((a, b) => {
                var effA = a.rateVal / Math.max(1, a.minutes);
                var effB = b.rateVal / Math.max(1, b.minutes);
                return effB - effA;
            });

            return results;
        })()
    """)

    print("TOP FAST HIGH-YIELD SURVEYS (sorted by yield efficiency):\n", json.dumps(fast_list[:15], indent=2))
