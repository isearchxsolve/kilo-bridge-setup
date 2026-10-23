r"""answer_travel_question.py - Fill in open-ended travel question, click next, and inspect.
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

    # 1. Inspect text input / textarea
    inspect_inp = client._js(r"""
        (function() {
            var inputs = Array.from(document.querySelectorAll('input[type="text"], textarea, input:not([type="radio"]):not([type="checkbox"])')).map(el => ({
                tag: el.tagName,
                type: el.type,
                id: el.id,
                name: el.name,
                placeholder: el.placeholder,
                className: el.className
            }));
            return inputs;
        })()
    """)
    print("Found text inputs:", json.dumps(inspect_inp, indent=2))

    # 2. Type thoughtful human response
    answer_text = "I would travel to the Swiss Alps in Switzerland to hike along the scenic alpine trails, take in the beautiful mountain landscapes, and explore the historic local villages."
    type_res = client._js(r"""
        (function(text) {
            var el = document.querySelector('textarea, input[type="text"], input:not([type="radio"]):not([type="checkbox"])');
            if (el) {
                el.focus();
                el.value = text;
                el.dispatchEvent(new Event('input', { bubbles: true }));
                el.dispatchEvent(new Event('change', { bubbles: true }));
                return { ok: true, value: el.value, id: el.id };
            }
            return { ok: false, error: 'No text input found' };
        })(%s)
    """ % json.dumps(answer_text))
    print("Type result:", json.dumps(type_res, indent=2))
    time.sleep(2)

    # 3. Click next button
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
    print("Next click result:", json.dumps(nxt, indent=2))
    time.sleep(5)

    info = client._js(r"({ url: window.location.href, title: document.title, body: document.body.innerText.slice(0, 1000) })")
    print("Screen after travel answer:\n", json.dumps(info, indent=2))
    shot = lane.shot(client, "primeearn_after_travel_q")
    print("Screenshot:", shot)
