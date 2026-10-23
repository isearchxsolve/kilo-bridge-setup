r"""inspect_profile_fields.py - Inspect the fields in the Profile subtab.
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("timebucks", "profile_fields")
with T.session(lane) as client:
    # Scroll down to reveal profile content
    client._js("window.scrollTo(0, 400);")
    time.sleep(1)

    fields_info = client._js(r"""
        (function() {
            var inputs = Array.from(document.querySelectorAll('input, select, textarea'));
            return inputs.map(i => ({
                tag: i.tagName,
                name: i.name || '',
                id: i.id || '',
                type: i.type || '',
                value: i.value || '',
                placeholder: i.placeholder || '',
                disabled: i.disabled,
                options: (i.tagName === 'SELECT') ? Array.from(i.options).slice(0, 5).map(o => o.text) : []
            })).filter(x => x.type !== 'hidden');
        })()
    """)
    print("ALL VISIBLE FORM INPUTS:\n", json.dumps(fields_info, indent=2))

    # Also capture labels or text
    form_text = client._js(r"""
        (function() {
            var form = document.querySelector('form') || document.body;
            return form.innerText.slice(0, 2000);
        })()
    """)
    print("FORM TEXT SNIPPET:\n", form_text[:1200])

    shot = lane.shot(client, "timebucks_profile_form_scrolled")
    print("Scrolled screenshot:", shot)
