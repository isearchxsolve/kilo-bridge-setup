r"""inspect_payment_tab_exact.py - Click the a[href="#paypal-changes"] tab explicitly and inspect the payment form.
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("timebucks", "payment_tab_exact")
with T.session(lane) as client:
    tabs = client.list_tabs()
    tb_tab = next((t for t in tabs if "timebucks.com" in t.get("url", "").lower()), None)
    if tb_tab:
        client.switch_tab(tb_tab["id"])
        time.sleep(1)

    res = client._js(r"""
        (function() {
            var link = document.querySelector('a[href="#paypal-changes"]');
            if (link) {
                link.click();
                if (window.jQuery) {
                    window.jQuery(link).tab('show');
                }
                return { clicked: true, outerHTML: link.outerHTML };
            }
            return { clicked: false };
        })()
    """)
    print("CLICK LINK:", json.dumps(res, indent=2))
    time.sleep(3)

    # Now inspect #paypal-changes
    content = client._js(r"""
        (function() {
            var div = document.querySelector('#paypal-changes');
            if (!div) return { foundDiv: false };
            
            var selects = Array.from(div.querySelectorAll('select')).map(s => {
                var opts = Array.from(s.options).map(o => ({ value: o.value, text: o.text }));
                return { id: s.id, name: s.name, options: opts };
            });

            var inputs = Array.from(div.querySelectorAll('input, button')).map(i => ({
                id: i.id,
                name: i.name,
                type: i.type,
                value: i.value
            }));

            return {
                foundDiv: true,
                styleDisplay: window.getComputedStyle(div).display,
                innerHTML: div.innerHTML.slice(0, 1000),
                innerText: div.innerText,
                selects: selects,
                inputs: inputs
            };
        })()
    """)
    print("PAYMENT SECTION CONTENT:\n", json.dumps(content, indent=2))

    shot = lane.shot(client, "timebucks_payment_tab_opened")
    print("Screenshot:", shot)
