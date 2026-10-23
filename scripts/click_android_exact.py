r"""click_android_exact.py - Specifically select Android radio button.
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

    # Click exactly the Android radio label
    res = client._js(r"""
        (function() {
            var labels = Array.from(document.querySelectorAll('label, .p-radio-label, .p-radio-wrapper')).filter(el => {
                return (el.innerText || '').trim() === 'Android';
            });
            if (labels.length > 0) {
                labels[0].click();
                return { ok: true, tag: labels[0].tagName, class: labels[0].className };
            }
            // fallback: input with type radio
            var radio = document.querySelector('input[type="radio"]');
            if (radio) {
                radio.click();
                return { ok: true, tag: 'input_radio', id: radio.id };
            }
            return { ok: false, error: 'Android not found' };
        })()
    """)
    print("Radio click result:", res)
    time.sleep(2)

    # Check if next button appeared or if it auto-advanced
    check = client._js(r"""
        (function() {
            var btn = document.querySelector('button.p-btn--icon-only, .next-button button, button.p-btn--primary');
            if (btn) {
                btn.click();
                return { ok: true, clickedBtn: true, class: btn.className };
            }
            return { ok: true, clickedBtn: false };
        })()
    """)
    print("Next button check/click:", check)

    time.sleep(5)

    info = client._js(r"({ url: window.location.href, title: document.title, body: document.body.innerText.slice(0, 1000) })")
    print("Screen after Android:\n", json.dumps(info, indent=2))
    shot = lane.shot(client, "primeearn_after_android")
    print("Screenshot:", shot)
