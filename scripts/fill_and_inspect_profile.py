r"""fill_and_inspect_profile.py - Populate provided DOB and inspect remaining fields.
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("timebucks", "fill_profile")
with T.session(lane) as client:
    tabs = client.list_tabs()
    tb_tab = next((t for t in tabs if "timebucks.com" in t.get("url", "").lower()), None)
    if tb_tab:
        client.switch_tab(tb_tab["id"])
    else:
        client.call_tool("browser_navigate", {"url": "https://timebucks.com/publishers/index.php?pg=setting"})
        time.sleep(3)

    # Inspect all form elements in detail
    form_inspect = client._js(r"""
        (function() {
            var inputs = Array.from(document.querySelectorAll('input, select, textarea'));
            return inputs.map(i => ({
                tag: i.tagName,
                name: i.name,
                id: i.id,
                type: i.type,
                value: i.value,
                placeholder: i.placeholder,
                outerHTML: i.outerHTML.slice(0, 150)
            })).filter(x => x.type !== 'hidden');
        })()
    """)
    print("ALL INPUTS ON PAGE:\n", json.dumps(form_inspect, indent=2))
