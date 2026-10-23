r"""inspect_campaign_3510_instructions.py - Inspect instructions and proof requirements for YouTube task.
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("timebucks", "task_3510")
with T.session(lane) as client:
    info = client._js(r"""
        (function() {
            var allText = document.body.innerText;
            var startBtn = document.querySelector('input[value="Start Campaign"], button[type="submit"]');
            var forms = Array.from(document.querySelectorAll('form')).map(f => ({
                action: f.action,
                method: f.method,
                inputs: Array.from(f.querySelectorAll('input, textarea, button')).map(i => ({
                    tag: i.tagName,
                    type: i.type,
                    name: i.name,
                    value: i.value
                }))
            }));

            return {
                url: window.location.href,
                hasStartBtn: !!startBtn,
                forms: forms,
                bodyLower: allText.slice(allText.indexOf('Campaign ID: 3510'), allText.indexOf('Campaign ID: 3510') + 2500)
            };
        })()
    """)
    print("CAMPAIGN 3510 DETAILS:\n", json.dumps(info, indent=2))
