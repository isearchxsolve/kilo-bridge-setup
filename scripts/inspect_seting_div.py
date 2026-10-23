r"""inspect_seting_div.py - Inspect content inside #seting.
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("timebucks", "seting_div")
with T.session(lane) as client:
    url = "https://timebucks.com/publishers/index.php?pg=setting#seting"
    client.call_tool("browser_navigate", {"url": url})
    time.sleep(2)

    # Scroll down to #seting
    client._js(r"""
        (function() {
            var el = document.querySelector('#seting');
            if (el) el.scrollIntoView();
        })()
    """)
    time.sleep(1)

    shot = lane.shot(client, "timebucks_seting_anchor_view")
    print("Screenshot saved to:", shot)

    profile_data = client._js(r"""
        (function() {
            var el = document.querySelector('#seting');
            if (!el) return {found: false};
            var inputs = Array.from(el.querySelectorAll('input, select, textarea'));
            return {
                found: true,
                text: el.innerText.slice(0, 1500),
                inputs: inputs.map(i => ({
                    tag: i.tagName,
                    name: i.name || '',
                    id: i.id || '',
                    type: i.type || '',
                    value: i.value || '',
                    placeholder: i.placeholder || ''
                })).filter(x => x.type !== 'hidden')
            };
        })()
    """)
    print("PROFILE DATA IN #seting:\n", json.dumps(profile_data, indent=2))
