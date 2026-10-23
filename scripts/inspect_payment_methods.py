r"""inspect_payment_methods.py - Check available payment methods on TimeBucks.
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("timebucks", "payment_methods")
with T.session(lane) as client:
    tabs = client.list_tabs()
    tb_tab = next((t for t in tabs if "timebucks.com" in t.get("url", "").lower()), None)
    if tb_tab:
        client.switch_tab(tb_tab["id"])
    else:
        client.call_tool("browser_navigate", {"url": "https://timebucks.com/publishers/index.php?pg=setting"})
        time.sleep(3)

    print("Clicking 'Payment Method' subtab...")
    client._js(r"""
        (function() {
            var els = Array.from(document.querySelectorAll('a, button, li, div'));
            var pTab = els.find(e => (e.innerText || '').trim().toLowerCase() === 'payment method');
            if (pTab) pTab.click();
        })()
    """)
    time.sleep(2)

    payment_info = client._js(r"""
        (function() {
            var select = document.querySelector('select[name="payment_method"], #payment_method, select');
            var options = select ? Array.from(select.options).map(o => ({text: o.text, value: o.value})) : [];
            var text = (document.querySelector('form') || document.body).innerText;
            return {
                options: options,
                textSnippet: text.slice(0, 1000)
            };
        })()
    """)

    shot = lane.shot(client, "timebucks_payment_methods")
    print("Screenshot saved to:", shot)
    print("PAYMENT METHODS AVAILABLE:\n", json.dumps(payment_info, indent=2))
