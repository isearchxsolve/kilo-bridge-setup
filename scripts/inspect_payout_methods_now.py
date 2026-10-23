r"""inspect_payout_methods_now.py - Check Payment Method options after profile update.
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("timebucks", "payout_methods")
with T.session(lane) as client:
    url = "https://timebucks.com/publishers/index.php?pg=setting"
    client.call_tool("browser_navigate", {"url": url})
    time.sleep(3)

    # Click Payment Method tab
    click_res = client._js(r"""
        (function() {
            var els = Array.from(document.querySelectorAll('a, button, li'));
            var pTab = els.find(e => (e.innerText || '').trim().toLowerCase() === 'payment method');
            if (pTab) {
                pTab.click();
                return {clicked: true};
            }
            return {clicked: false};
        })()
    """)
    print("CLICK PAYMENT METHOD TAB:", click_res)
    time.sleep(2)

    shot = lane.shot(client, "timebucks_payment_method_tab")
    print("Payment method screenshot:", shot)

    methods = client._js(r"""
        (function() {
            var selects = Array.from(document.querySelectorAll('select'));
            var pSelect = selects.find(s => s.name.includes('payment') || s.id.includes('payment') || Array.from(s.options).some(o => o.text.toLowerCase().includes('wise') || o.text.toLowerCase().includes('litecoin') || o.text.toLowerCase().includes('crypto')));
            if (!pSelect) {
                // If not found, list all select options
                return {
                    found: false,
                    allSelects: selects.map(s => ({id: s.id, name: s.name, options: Array.from(s.options).map(o => o.text)}))
                };
            }
            return {
                found: true,
                id: pSelect.id,
                name: pSelect.name,
                options: Array.from(pSelect.options).map(o => ({text: o.text, value: o.value}))
            };
        })()
    """)
    print("PAYMENT METHODS AVAILABLE:\n", json.dumps(methods, indent=2))
