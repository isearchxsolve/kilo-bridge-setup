r"""inspect_profile_exact.py - Switch to Timebucks and inspect Profile tab.
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("timebucks", "profile_exact")
with T.session(lane) as client:
    tabs = client.list_tabs()
    tb_tab = next((t for t in tabs if "timebucks.com" in t.get("url", "").lower()), None)
    if tb_tab:
        client.switch_tab(tb_tab["id"])
        time.sleep(1)
    else:
        client.call_tool("browser_navigate", {"url": "https://timebucks.com/publishers/index.php?pg=setting"})
        time.sleep(3)

    # Click the 'Profile' subtab under Settings
    client._js(r"""
        (function() {
            var els = Array.from(document.querySelectorAll('a, button, li, div'));
            var pTab = els.find(e => (e.innerText || '').trim().toLowerCase() === 'profile');
            if (pTab) pTab.click();
        })()
    """)
    time.sleep(2)

    # Read inputs
    form_inputs = client._js(r"""
        (function() {
            var inputs = Array.from(document.querySelectorAll('input, select, textarea'));
            return inputs.map(i => ({
                name: i.name,
                id: i.id,
                type: i.type,
                value: i.value,
                placeholder: i.placeholder,
                label: (i.closest('div, tr, p') ? i.closest('div, tr, p').innerText.split('\n')[0] : '')
            })).filter(x => x.type !== 'hidden');
        })()
    """)
    print("PROFILE INPUTS:\n", json.dumps(form_inputs, indent=2))

    shot = lane.shot(client, "timebucks_profile_details")
    print("Screenshot saved to:", shot)
