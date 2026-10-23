r"""primeearn_select_language_and_next.py - Select English, verify next button appears, click it, and report.
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

    # 1. Select English
    select_res = client._js(r"""
        (function() {
            var items = Array.from(document.querySelectorAll('.p-checkbox-wrapper, label, div')).filter(el => {
                return (el.innerText || '').trim() === 'English';
            });

            if (items.length > 0) {
                // Click the English item
                items[0].click();
                return { ok: true, clicked: items[0].className };
            }
            return { ok: false, error: 'English item not found' };
        })()
    """)
    print("Select result:", select_res)
    time.sleep(1.5)

    # 2. Check if next button is present and click it
    btn_res = client._js(r"""
        (function() {
            var btn = document.querySelector('button.p-btn--icon-only, .next-button button, button.p-btn--primary');
            if (btn) {
                btn.click();
                return { ok: true, buttonClass: btn.className };
            }
            return { ok: false, error: 'Next button not found' };
        })()
    """)
    print("Button click result:", btn_res)

    time.sleep(5)

    # 3. Inspect new screen
    new_state = client._js(r"""
        (function() {
            return {
                url: window.location.href,
                title: document.title,
                body: document.body.innerText.slice(0, 1500)
            };
        })()
    """)
    print("New state:\n", json.dumps(new_state, indent=2))

    shot = lane.shot(client, "primeearn_after_language")
    print("Screenshot:", shot)
