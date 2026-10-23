r"""inspect_current_q.py - Inspect current question on PrimeEarn with navigate.
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
    client.call_tool("browser_navigate", {"url": "https://monetize.primeearn.com/questions"})
    time.sleep(3)

    res = client._js(r"""
        (function() {
            var headings = Array.from(document.querySelectorAll('h1, h2, h3, h4, .title, p')).map(el => (el.innerText || '').trim()).filter(t => t.length > 5);
            var checkboxes = Array.from(document.querySelectorAll('input[type="checkbox"]')).map(el => el.id);
            var radios = Array.from(document.querySelectorAll('input[type="radio"]')).map(el => el.id);
            var labels = Array.from(document.querySelectorAll('label, .p-checkbox-label, .p-radio-label')).map(el => (el.innerText || '').trim());
            return {
                url: window.location.href,
                headings: headings.slice(0, 5),
                checkboxesCount: checkboxes.length,
                radiosCount: radios.length,
                labels: labels,
                body: document.body.innerText.slice(0, 1000)
            };
        })()
    """)
    print("CURRENT SCREEN:\n", json.dumps(res, indent=2))
    shot = lane.shot(client, "primeearn_alcohol_question")
    print("Screenshot:", shot)
