r"""accept_survey_privacy.py - Check policy checkbox and click Continue to Survey.
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("timebucks", "survey_accept")
with T.session(lane) as client:
    res = client._js(r"""
        (function() {
            var cb = document.querySelector('input[type="checkbox"]');
            if (cb && !cb.checked) {
                cb.click();
            }

            var btn = Array.from(document.querySelectorAll('button, input[type="button"]')).find(b => {
                var t = (b.innerText || b.value || '').trim().toLowerCase();
                return t.includes('continue to survey') || t.includes('continue');
            });

            if (btn) {
                btn.click();
                return { checkboxChecked: cb ? cb.checked : false, btnClicked: true };
            }
            return { error: "Button not found" };
        })()
    """)

    print("ACCEPT RESULT:", json.dumps(res, indent=2))
    time.sleep(5)

    shot = lane.shot(client, "survey_question_1")
    print("Screenshot:", shot)

    # Inspect question
    q_info = client._js(r"""
        (function() {
            var inputs = Array.from(document.querySelectorAll('input, select, textarea, button')).map(i => ({
                tag: i.tagName,
                type: i.type,
                name: i.name,
                id: i.id,
                value: i.value,
                text: (i.innerText || '').trim().slice(0, 80)
            }));

            return {
                url: window.location.href,
                title: document.title,
                bodyText: document.body.innerText.slice(0, 1500),
                inputs: inputs
            };
        })()
    """)

    print("QUESTION 1 INFO:\n", json.dumps(q_info, indent=2))
