r"""inspect_payment_settings.py - Inspect payment method options on TimeBucks settings page.
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("timebucks", "payment_settings")
with T.session(lane) as client:
    tabs = client.list_tabs()
    tb_tab = next((t for t in tabs if "timebucks.com" in t.get("url", "").lower()), None)
    if tb_tab:
        client.switch_tab(tb_tab["id"])
        time.sleep(1)

    print("Navigating to settings...")
    client.call_tool("browser_navigate", {"url": "https://timebucks.com/publishers/index.php?pg=setting"})
    time.sleep(3.5)

    # Click on "Payment Method" tab inside settings
    tab_click = client._js(r"""
        (function() {
            var tabs = Array.from(document.querySelectorAll('a, button, li')).filter(el => {
                var t = (el.innerText || '').toLowerCase().trim();
                return t.includes('payment method') || t.includes('payment');
            });
            if (tabs.length > 0) {
                tabs[0].click();
                return { clicked: true, text: tabs[0].innerText };
            }
            return { clicked: false };
        })()
    """)
    print("Tab click result:", json.dumps(tab_click))
    time.sleep(2)

    shot = lane.shot(client, "timebucks_payment_settings_page")
    print("Payment settings screenshot:", shot)

    # Inspect payment method dropdown or form
    payment_form = client._js(r"""
        (function() {
            var selects = Array.from(document.querySelectorAll('select')).map(s => {
                var opts = Array.from(s.options).map(o => ({ value: o.value, text: o.text }));
                return {
                    name: s.name,
                    id: s.id,
                    options: opts
                };
            });

            var inputs = Array.from(document.querySelectorAll('input')).map(i => ({
                name: i.name,
                id: i.id,
                type: i.type,
                value: i.value,
                placeholder: i.placeholder
            })).filter(i => i.type !== 'hidden');

            return {
                selects: selects,
                inputs: inputs,
                bodySnippet: document.body.innerText.slice(400, 2000)
            };
        })()
    """)

    print("PAYMENT FORM DETAILS:\n", json.dumps(payment_form, indent=2))
