r"""claim_hourly_crown.py - Claim Hourly Crown on TimeBucks.
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("timebucks", "hourly_crown")
with T.session(lane) as client:
    print("Navigating to Hourly Crown...")
    client.call_tool("browser_navigate", {"url": "https://timebucks.com/publishers/index.php?pg=earn&tab=hourly_crown"})
    time.sleep(3.5)

    # Click Claim the Crown button
    claim_res = client._js(r"""
        (function() {
            var btn = Array.from(document.querySelectorAll('input, button, a')).find(b => {
                var t = (b.value || b.innerText || '').trim();
                return t.includes('Claim the Crown');
            });

            if (btn) {
                btn.click();
                return { ok: true, text: btn.value || btn.innerText };
            }
            return { ok: false, error: 'Claim the Crown button not found' };
        })()
    """)
    print("Claim result:", json.dumps(claim_res, indent=2))
    time.sleep(3)

    info = client._js(r"""
        (function() {
            var text = document.body.innerText;
            return {
                url: window.location.href,
                bodySnippet: text.slice(text.indexOf('Hourly Crown'), text.indexOf('Hourly Crown') + 800)
            };
        })()
    """)
    print("After claim info:\n", json.dumps(info, indent=2))
    shot = lane.shot(client, "timebucks_hourly_crown_claimed")
    print("Screenshot:", shot)
