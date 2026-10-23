r"""open_payment_method.py - Switch to TimeBucks tab and open the Payment Method settings subtab.
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("timebucks", "payment_method")
with T.session(lane) as client:
    tabs = client.list_tabs()
    tb_tab = next((t for t in tabs if "timebucks.com" in t.get("url", "").lower()), None)
    if tb_tab:
        client.switch_tab(tb_tab["id"])
        time.sleep(1)
    else:
        client.call_tool("browser_navigate", {"url": "https://timebucks.com/publishers/index.php?pg=setting"})
        time.sleep(3)

    # Find the Payment Method link / tab on settings page
    nav_res = client._js(r"""
        (function() {
            var allElements = Array.from(document.querySelectorAll('a, li, span, button'));
            var target = allElements.find(el => (el.innerText || '').trim() === 'Payment Method');
            if (target) {
                target.click();
                return {
                    clicked: true,
                    tagName: target.tagName,
                    href: target.getAttribute('href') || '',
                    html: target.outerHTML
                };
            }
            return { clicked: false, available: allElements.map(e => e.innerText.trim()).filter(t => t.length > 2 && t.length < 25).slice(0, 30) };
        })()
    """)
    print("NAV RES:", json.dumps(nav_res, indent=2))
    time.sleep(3)

    shot = lane.shot(client, "timebucks_payment_method_active")
    print("Screenshot:", shot)

    # Inspect the active payment method section
    section_info = client._js(r"""
        (function() {
            var selects = Array.from(document.querySelectorAll('select')).map(s => {
                var opts = Array.from(s.options).map(o => ({ value: o.value, text: o.text }));
                return {
                    id: s.id,
                    name: s.name,
                    options: opts
                };
            });

            var inputs = Array.from(document.querySelectorAll('input')).filter(i => {
                return i.type !== 'hidden';
            }).map(i => ({
                id: i.id,
                name: i.name,
                type: i.type,
                value: i.value,
                placeholder: i.placeholder
            }));

            // Find any payment text
            var paymentBox = document.querySelector('#paypal-changes, #tab_content_payment, .payment_method_container, #payment_method');
            var paymentText = paymentBox ? paymentBox.innerText : '';

            return {
                selects: selects,
                inputs: inputs,
                paymentBoxText: paymentText,
                visibleBody: document.body.innerText.slice(400, 2500)
            };
        })()
    """)
    print("SECTION INFO:\n", json.dumps(section_info, indent=2))
