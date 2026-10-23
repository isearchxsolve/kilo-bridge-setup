r"""select_radio_and_proceed.py - Navigate, inspect radio element HTML, click it, click next.
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
    time.sleep(3.5)

    # Inspect and click
    step1 = client._js(r"""
        (function() {
            var radios = Array.from(document.querySelectorAll('input[type="radio"]'));
            var labels = Array.from(document.querySelectorAll('label'));
            var androidInput = radios[0]; // First one is Android
            var androidLabel = labels.find(l => (l.innerText || '').includes('Android'));

            var report = {
                radiosCount: radios.length,
                labelsCount: labels.length,
                androidInputId: androidInput ? androidInput.id : null,
                androidInputChecked: androidInput ? androidInput.checked : null,
                androidLabelText: androidLabel ? androidLabel.innerText.trim() : null
            };

            // Trigger click on android input and label
            if (androidLabel) {
                androidLabel.click();
            }
            if (androidInput) {
                androidInput.click();
                androidInput.checked = true;
                androidInput.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));
                androidInput.dispatchEvent(new Event('change', { bubbles: true }));
            }

            return report;
        })()
    """)
    print("Step 1 select:", json.dumps(step1, indent=2))
    time.sleep(2)

    # Check button and click it
    step2 = client._js(r"""
        (function() {
            var btn = document.querySelector('button.p-btn--icon-only, .next-button button, button.p-btn--primary');
            if (btn) {
                btn.click();
                return { ok: true, clicked: btn.className };
            }
            return { ok: false, error: 'Next button not found' };
        })()
    """)
    print("Step 2 click next:", json.dumps(step2, indent=2))
    time.sleep(5)

    info = client._js(r"({ url: window.location.href, title: document.title, body: document.body.innerText.slice(0, 1000) })")
    print("Screen after step:\n", json.dumps(info, indent=2))
    shot = lane.shot(client, "primeearn_after_radio_step")
    print("Shot:", shot)
