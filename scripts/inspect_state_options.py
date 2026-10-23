r"""inspect_state_options.py - Inspect options in #state2.
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("timebucks", "state_options")
with T.session(lane) as client:
    tabs = client.list_tabs()
    tb_tab = next((t for t in tabs if "timebucks.com" in t.get("url", "").lower()), None)
    if tb_tab:
        client.switch_tab(tb_tab["id"])
    else:
        client.call_tool("browser_navigate", {"url": "https://timebucks.com/publishers/index.php?pg=setting"})
        time.sleep(3)

    state_data = client._js(r"""
        (function() {
            var stateEl = document.querySelector('#state2, select[name="state"], select[name="state2"]');
            if (!stateEl) return {found: false};
            return {
                found: true,
                id: stateEl.id,
                name: stateEl.name,
                optionsCount: stateEl.options.length,
                options: Array.from(stateEl.options).map(o => ({text: o.text, value: o.value}))
            };
        })()
    """)
    print("STATE SELECT DATA:\n", json.dumps(state_data, indent=2))
