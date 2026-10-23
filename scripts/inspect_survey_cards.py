r"""inspect_survey_cards.py - Inspect all survey cards on all_surveys tab.
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("timebucks", "survey_cards")
with T.session(lane) as client:
    print("Navigating to all_surveys...")
    client.call_tool("browser_navigate", {"url": "https://timebucks.com/publishers/index.php?pg=earn&tab=all_surveys"})
    time.sleep(3.5)

    data = client._js(r"""
        (function() {
            // Find all cards / items in the surveys container
            var cards = Array.from(document.querySelectorAll('.survey-card, .surveyItem, .survey-box, div[class*="survey"], div[style*="cursor: pointer"]')).filter(el => {
                var t = el.innerText || '';
                return t.includes('$') && (t.includes('min') || t.includes('Start'));
            });

            // Map each card
            var parsed = [];
            var allElements = Array.from(document.querySelectorAll('*')).filter(el => {
                var t = (el.innerText || '').trim();
                var r = el.getBoundingClientRect();
                return (r.width > 50 && r.height > 50 && t.startsWith('$') && t.includes('min'));
            });

            allElements.forEach((el, idx) => {
                var btn = el.querySelector('button, a, input[type="button"]') || el;
                var text = el.innerText.replace(/\s+/g, ' ').trim();
                parsed.push({
                    index: idx,
                    text: text,
                    tag: el.tagName,
                    btnTag: btn.tagName,
                    btnHref: btn.getAttribute ? btn.getAttribute('href') : null,
                    btnOnclick: btn.getAttribute ? btn.getAttribute('onclick') : null
                });
            });

            return {
                url: window.location.href,
                foundCount: parsed.length,
                sample: parsed.slice(0, 20)
            };
        })()
    """)

    print("SURVEY CARDS:\n", json.dumps(data, indent=2))
