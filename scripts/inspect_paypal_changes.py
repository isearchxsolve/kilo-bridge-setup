r"""inspect_paypal_changes.py - Inspect elements inside #paypal-changes.
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("timebucks", "paypal_changes")
with T.session(lane) as client:
    url = "https://timebucks.com/publishers/index.php?pg=setting#paypal-changes"
    client.call_tool("browser_navigate", {"url": url})
    time.sleep(2)

    client._js(r"""
        (function() {
            var el = document.querySelector('#paypal-changes');
            if (el) {
                el.style.display = 'block';
                el.scrollIntoView();
            }
        })()
    """)
    time.sleep(1)

    shot = lane.shot(client, "timebucks_paypal_changes_view")
    print("Screenshot saved to:", shot)

    container_data = client._js(r"""
        (function() {
            var el = document.querySelector('#paypal-changes');
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
                    options: (i.tagName === 'SELECT') ? Array.from(i.options).map(o => o.text) : []
                }))
            };
        })()
    """)
    print("PAYPAL CHANGES DATA:\n", json.dumps(container_data, indent=2))
