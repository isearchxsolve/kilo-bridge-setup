r"""verify_payout_persisted.py - Verify the saved payout method on TimeBucks.
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("timebucks", "verify_payout")
with T.session(lane) as client:
    client.call_tool("browser_navigate", {"url": "https://timebucks.com/publishers/index.php?pg=setting#paypal-changes"})
    time.sleep(3.5)

    res = client._js(r"""
        (function() {
            var select = document.querySelector('select[name="contact_subject"]');
            var phone = document.querySelector('#paypalemail');
            return {
                selectedVal: select ? select.value : null,
                selectedText: select ? (select.selectedIndex >= 0 ? select.options[select.selectedIndex].text : null) : null,
                phoneVal: phone ? phone.value : null
            };
        })()
    """)
    print("PERSISTED PAYMENT STATE:\n", json.dumps(res, indent=2))
