r"""click_claim_gift.py - Inspect and click Claim Gift button.
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("timebucks", "claim_gift")
with T.session(lane) as client:
    url = "https://timebucks.com/publishers/index.php?pg=earn&tab=push_clicks"
    client.call_tool("browser_navigate", {"url": url})
    time.sleep(3)

    click_details = client._js(r"""
        (function() {
            var btn = Array.from(document.querySelectorAll('input, button')).find(b => (b.value || b.innerText || '').toLowerCase().includes('claim gift'));
            if (!btn) return {found: false};
            var form = btn.closest('form');
            var btnInfo = {
                tag: btn.tagName,
                type: btn.type,
                value: btn.value,
                id: btn.id,
                name: btn.name,
                hasForm: !!form,
                formAction: form ? form.action : null
            };

            // Trigger click
            btn.click();
            return {
                found: true,
                btnInfo: btnInfo
            };
        })()
    """)
    print("CLICK DETAILS:\n", json.dumps(click_details, indent=2))
    time.sleep(4)

    shot = lane.shot(client, "timebucks_claim_gift_result")
    print("Screenshot saved to:", shot)
    page = T.read_page(client)
    print("PAGE SNIPPET:\n", page.get("body", "")[500:1500])
