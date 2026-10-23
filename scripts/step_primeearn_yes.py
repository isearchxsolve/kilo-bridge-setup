r"""step_primeearn_yes.py - Select 'Yes, let's continue' and proceed to next question.
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("timebucks", "primeearn_survey")
with T.session(lane) as client:
    print("Navigating to https://monetize.primeearn.com/questions...")
    client.call_tool("browser_navigate", {"url": "https://monetize.primeearn.com/questions"})
    time.sleep(3)

    # 1. Select 'Yes, let\'s continue'
    sel = client._js(r"""
        (function() {
            var labels = Array.from(document.querySelectorAll('label, .p-radio-label, .p-radio-wrapper')).filter(el => {
                var t = (el.innerText || '').trim().toLowerCase();
                return t.includes("yes") || t.includes("continue");
            });

            if (labels.length > 0) {
                labels[0].click();
                return { ok: true, clicked: labels[0].innerText.trim() };
            }
            return { ok: false, error: 'Yes option not found' };
        })()
    """)
    print("Option selection:", sel)
    time.sleep(2)

    # 2. Click next button
    nxt = client._js(r"""
        (function() {
            var btn = document.querySelector('button.p-btn--icon-only, .next-button button, button.p-btn--primary');
            if (btn) {
                btn.click();
                return { ok: true, class: btn.className };
            }
            return { ok: false, error: 'Next button not found' };
        })()
    """)
    print("Next click:", nxt)

    time.sleep(5)

    info = client._js(r"({ url: window.location.href, title: document.title, body: document.body.innerText.slice(0, 1000) })")
    print("Screen after step:\n", json.dumps(info, indent=2))
    shot = lane.shot(client, "primeearn_step_after_yes")
    print("Screenshot:", shot)
