r"""inspect_upi_payment_fields.py - Select 'UPI Payment & Bank Transfer' and inspect revealed form fields.
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("timebucks", "upi_inspect")
with T.session(lane) as client:
    # Select UPI in the dropdown and trigger change event
    fields_info = client._js(r"""
        (function() {
            var select = document.querySelector('select[name="contact_subject"]');
            if (!select) return { error: "No select found" };

            select.value = "up";
            select.dispatchEvent(new Event('change', { bubbles: true }));

            // Give UI a moment to update display
            var form = select.closest('form');
            var visibleInputs = Array.from(form.querySelectorAll('input, select, textarea')).filter(el => {
                var style = window.getComputedStyle(el);
                return style.display !== 'none' && style.visibility !== 'hidden' && el.type !== 'hidden';
            }).map(el => ({
                id: el.id,
                name: el.name,
                type: el.type,
                value: el.value,
                placeholder: el.placeholder,
                outerHTML: el.outerHTML
            }));

            // Check container visibility
            var containers = Array.from(form.querySelectorAll('div, tr, p')).filter(c => {
                var t = (c.innerText || '').toLowerCase();
                return (t.includes('upi') || t.includes('bank') || t.includes('ifsc')) && c.children.length > 0;
            }).map(c => c.innerText.trim()).slice(0, 5);

            return {
                selectedValue: select.value,
                visibleInputs: visibleInputs,
                containersText: containers,
                formTextSnippet: form.innerText.slice(0, 1500)
            };
        })()
    """)

    print("UPI FORM INSPECTION:\n", json.dumps(fields_info, indent=2))

    shot = lane.shot(client, "timebucks_upi_payment_selected")
    print("Screenshot saved to:", shot)
