r"""inspect_children_options.py - Inspect all options in children question.
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
            var labels = Array.from(document.querySelectorAll('label, .p-radio-label')).map(el => (el.innerText || '').trim());
            var inputs = Array.from(document.querySelectorAll('input[type="radio"]')).map(el => el.id);
            return {
                labels: labels,
                inputsCount: inputs.length
            };
        })()
    """)
    print("Children question options:\n", json.dumps(res, indent=2))
