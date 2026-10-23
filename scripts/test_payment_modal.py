r"""test_payment_modal.py - Check if showProfile opens a confirmation modal on payment update.
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("timebucks", "payment_modal_check")
phone = T.candidate_fact("PHONE")

with T.session(lane) as client:
    print("Navigating to payment settings...")
    client.call_tool("browser_navigate", {"url": "https://timebucks.com/publishers/index.php?pg=setting#paypal-changes"})
    time.sleep(3.5)

    step1 = client._js(f"""
        (function() {{
            var select = document.querySelector('#contact_subject02') || document.querySelector('select[name="contact_subject"]');
            if (select) {{
                select.value = "up";
                if (window.jQuery) window.jQuery(select).trigger('change');
            }}

            var phoneEl = document.querySelector('#paypalemail');
            if (phoneEl) {{
                phoneEl.value = "{phone}";
            }}

            // Check showProfile function
            var fnStr = window.showProfile ? window.showProfile.toString() : "Not on window";

            var btn = document.querySelector('input[value="Update Payment Method"]');
            if (btn) btn.click();

            return {{
                fnStr: fnStr,
                btnFound: !!btn
            }};
        }})()
    """)

    print("STEP 1:", json.dumps(step1, indent=2))
    time.sleep(2)

    # Check for modals
    modal_info = client._js(r"""
        (function() {
            var visibleModals = Array.from(document.querySelectorAll('.modal, .modal-dialog, div[class*="popup"], div[id*="popup"], div[id*="modal"]')).filter(m => {
                var style = window.getComputedStyle(m);
                return style.display !== 'none' && style.visibility !== 'hidden';
            }).map(m => ({
                id: m.id,
                className: m.className,
                text: m.innerText.slice(0, 500)
            }));

            var buttons = Array.from(document.querySelectorAll('input[type="button"], button, a.btn')).filter(b => {
                var val = (b.value || b.innerText || '').toLowerCase();
                return val.includes('confirm') || val.includes('ok') || val.includes('yes') || val.includes('submit');
            }).map(b => ({
                id: b.id,
                val: b.value || b.innerText,
                onclick: b.getAttribute('onclick'),
                visible: window.getComputedStyle(b).display !== 'none'
            }));

            return {
                visibleModals: visibleModals,
                buttons: buttons
            };
        })()
    """)

    print("MODALS & BUTTONS:\n", json.dumps(modal_info, indent=2))

    shot = lane.shot(client, "timebucks_payment_modal_check")
    print("Screenshot saved to:", shot)
