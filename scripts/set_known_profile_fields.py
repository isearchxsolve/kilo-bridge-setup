r"""set_known_profile_fields.py - Set DOB and State in the profile form.
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("timebucks", "set_profile")
with T.session(lane) as client:
    tabs = client.list_tabs()
    tb_tab = next((t for t in tabs if "timebucks.com" in t.get("url", "").lower()), None)
    if tb_tab:
        client.switch_tab(tb_tab["id"])
    else:
        client.call_tool("browser_navigate", {"url": "https://timebucks.com/publishers/index.php?pg=setting"})
        time.sleep(3)

    set_res = client._js(r"""
        (function() {
            var m = document.querySelector('#dobMonth');
            var d = document.querySelector('#dobDay');
            var y = document.querySelector('#dobYear');
            var s = document.querySelector('#state2');

            if (m) { m.value = '05'; m.dispatchEvent(new Event('change', {bubbles: true})); }
            if (d) { d.value = '29'; d.dispatchEvent(new Event('change', {bubbles: true})); }
            if (y) { y.value = '1979'; y.dispatchEvent(new Event('change', {bubbles: true})); }
            if (s) { s.value = 'West Bengal'; s.dispatchEvent(new Event('change', {bubbles: true})); }

            return {
                dobMonth: m ? m.value : null,
                dobDay: d ? d.value : null,
                dobYear: y ? y.value : null,
                state: s ? s.value : null
            };
        })()
    """)
    print("FIELDS SET IN DOM:\n", json.dumps(set_res, indent=2))

    shot = lane.shot(client, "timebucks_profile_dob_set")
    print("Screenshot saved to:", shot)
