r"""step_primeearn.py - Click 'Start The Survey' on PrimeEarn and inspect the next screen.
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
    # Check current page URL
    info = client._js(r"({ url: window.location.href, title: document.title })")
    print("Initial state:", info)

    if "primeearn.com/policy" in info.get("url", ""):
        print("Clicking 'Start The Survey'...")
        click_res = client._js(r"""
            (function() {
                var btn = Array.from(document.querySelectorAll('button')).find(b => (b.innerText || '').includes('Start The Survey'));
                if (btn) {
                    btn.click();
                    return { ok: true, text: btn.innerText };
                }
                return { ok: false, error: 'Button not found' };
            })()
        """)
        print("Click result:", click_res)
        time.sleep(5)
    else:
        print("Not on policy page, checking current page...")

    # Inspect current state after click / navigation
    new_state = client._js(r"""
        (function() {
            var inputs = Array.from(document.querySelectorAll('input, select, textarea')).map(el => ({
                tag: el.tagName,
                type: el.type || '',
                name: el.name || '',
                id: el.id || '',
                value: el.value || '',
                placeholder: el.placeholder || '',
                required: el.required
            }));

            var btns = Array.from(document.querySelectorAll('button, input[type="submit"], a.btn, div[role="button"]')).map(el => ({
                tag: el.tagName,
                type: el.type || '',
                id: el.id || '',
                className: el.className || '',
                text: (el.innerText || el.value || '').trim()
            })).filter(b => b.text.length > 0 && b.text.length < 60);

            var radios = Array.from(document.querySelectorAll('input[type="radio"], input[type="checkbox"], label')).map(el => ({
                tag: el.tagName,
                text: (el.innerText || '').trim(),
                checked: el.checked
            })).filter(r => r.text.length > 0 && r.text.length < 100);

            return {
                url: window.location.href,
                title: document.title,
                inputs: inputs,
                buttons: btns,
                labels_sample: radios.slice(0, 20),
                body_sample: document.body.innerText.slice(0, 1500)
            };
        })()
    """)

    print("NEW STATE:\n", json.dumps(new_state, indent=2))
    shot = lane.shot(client, "primeearn_step_after_start")
    print("Receipt screenshot:", shot)
