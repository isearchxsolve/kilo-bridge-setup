r"""inspect_upi_payment_fields_reliable.py - Reliably navigate and select UPI Payment & Bank Transfer.
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("timebucks", "upi_inspect_reliable")
with T.session(lane) as client:
    print("Navigating to settings...")
    client.call_tool("browser_navigate", {"url": "https://timebucks.com/publishers/index.php?pg=setting#paypal-changes"})
    time.sleep(3.5)

    fields_info = client._js(r"""
        (function() {
            var select = document.querySelector('select[name="contact_subject"]') || document.querySelector('#contact_subject02');
            if (!select) return { error: "No select found" };

            // Set value to 'up' (UPI Payment & Bank Transfer)
            select.value = "up";
            if (window.jQuery) {
                window.jQuery(select).trigger('change');
            } else {
                select.dispatchEvent(new Event('change', { bubbles: true }));
            }

            var form = select.closest('form');
            var allInputs = Array.from(form.querySelectorAll('input, select, textarea')).map(el => {
                var style = window.getComputedStyle(el);
                return {
                    id: el.id,
                    name: el.name,
                    type: el.type,
                    value: el.value,
                    placeholder: el.placeholder,
                    displayed: style.display !== 'none' && style.visibility !== 'hidden'
                };
            });

            return {
                selectedValue: select.value,
                allInputs: allInputs,
                formVisibleText: form.innerText
            };
        })()
    """)

    print("UPI FORM RESULT:\n", json.dumps(fields_info, indent=2))
    time.sleep(2)

    shot = lane.shot(client, "timebucks_upi_payment_configured")
    print("Screenshot saved to:", shot)
