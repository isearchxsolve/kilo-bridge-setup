r"""inspect_update_payment_btn.py - Inspect the Update Payment Method button event handlers and form.
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("timebucks", "inspect_payout_btn")
with T.session(lane) as client:
    client.call_tool("browser_navigate", {"url": "https://timebucks.com/publishers/index.php?pg=setting#paypal-changes"})
    time.sleep(3.5)

    res = client._js(r"""
        (function() {
            var btn = Array.from(document.querySelectorAll('input, button')).find(b => (b.value || b.innerText || '').trim() === 'Update Payment Method');
            if (!btn) return { found: false };

            var form = btn.closest('form');
            var onclick = btn.getAttribute('onclick');

            var jqEvents = null;
            if (window.jQuery && window.jQuery._data) {
                var ev = window.jQuery._data(btn, 'events');
                if (ev) jqEvents = Object.keys(ev);
            }

            return {
                found: true,
                tagName: btn.tagName,
                id: btn.id,
                onclick: onclick,
                formAction: form ? form.action : null,
                formId: form ? form.id : null,
                formOnsubmit: form ? form.getAttribute('onsubmit') : null,
                jqEvents: jqEvents
            };
        })()
    """)
    print(json.dumps(res, indent=2))
