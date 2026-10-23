r"""inspect_claim_gift_onclick.py - Inspect event handler on Claim Gift.
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("timebucks", "claim_gift_inspect")
with T.session(lane) as client:
    url = "https://timebucks.com/publishers/index.php?pg=earn&tab=push_clicks"
    client.call_tool("browser_navigate", {"url": url})
    time.sleep(3)

    handler_info = client._js(r"""
        (function() {
            var btn = Array.from(document.querySelectorAll('input, button')).find(b => (b.value || b.innerText || '').toLowerCase().includes('claim gift'));
            if (!btn) return {found: false};
            return {
                found: true,
                onclick: btn.getAttribute('onclick'),
                id: btn.id,
                className: btn.className,
                outerHTML: btn.outerHTML
            };
        })()
    """)
    print("CLAIM GIFT HANDLER:\n", json.dumps(handler_info, indent=2))
