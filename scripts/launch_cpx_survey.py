r"""launch_cpx_survey.py - Start $1.35 CPX Research survey and inspect screen.
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("timebucks", "launch_cpx")
with T.session(lane) as client:
    print("Navigating to all_surveys...")
    client.call_tool("browser_navigate", {"url": "https://timebucks.com/publishers/index.php?pg=earn&tab=all_surveys"})
    time.sleep(3.5)

    # Click start on survey-3178397591 ($1.35)
    click_res = client._js(r"""
        (function() {
            var card = document.getElementById('survey-3178397591');
            if (!card) {
                // Fallback: search by text $1.35
                var cards = Array.from(document.querySelectorAll('.survey-card')).filter(c => (c.innerText || '').includes('$1.35'));
                if (cards.length > 0) card = cards[0];
            }

            if (card) {
                var btn = card.querySelector('.btn-start, button');
                if (btn) {
                    var link = btn.getAttribute('data-link') || btn.getAttribute('href');
                    btn.click();
                    return { ok: true, clicked: true, dataLink: link };
                }
            }
            return { ok: false, error: 'card or button not found' };
        })()
    """)
    print("Click result:", json.dumps(click_res, indent=2))
    time.sleep(6)

    info = client._js(r"""
        (function() {
            return {
                url: window.location.href,
                title: document.title,
                bodySnippet: document.body.innerText.slice(0, 1500)
            };
        })()
    """)
    print("SURVEY LAUNCH STATE:\n", json.dumps(info, indent=2))
    shot = lane.shot(client, "timebucks_cpx_survey_launched")
    print("Screenshot:", shot)
