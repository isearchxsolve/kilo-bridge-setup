r"""click_yes_exact.py - Select 'Yes, let's continue' with input dispatch.
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

    # 1. Select Yes radio input with events
    sel = client._js(r"""
        (function() {
            var radios = Array.from(document.querySelectorAll('input[type="radio"]'));
            var labels = Array.from(document.querySelectorAll('label'));
            var targetInput = radios[0]; // first option is Yes
            var targetLabel = labels.find(l => (l.innerText || '').toLowerCase().includes('yes'));

            if (targetLabel) {
                targetLabel.click();
            }
            if (targetInput) {
                targetInput.click();
                targetInput.checked = true;
                targetInput.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));
                targetInput.dispatchEvent(new Event('change', { bubbles: true }));
            }

            return {
                radiosCount: radios.length,
                targetInputChecked: targetInput ? targetInput.checked : null,
                targetLabelText: targetLabel ? targetLabel.innerText.trim() : null
            };
        })()
    """)
    print("Radio select attempt:", json.dumps(sel, indent=2))
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
    print("Next button click:", json.dumps(nxt, indent=2))
    time.sleep(5)

    info = client._js(r"({ url: window.location.href, title: document.title, body: document.body.innerText.slice(0, 1000) })")
    print("Screen after step:\n", json.dumps(info, indent=2))
    shot = lane.shot(client, "primeearn_after_yes_exact")
    print("Screenshot:", shot)
