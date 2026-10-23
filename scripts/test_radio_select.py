r"""test_radio_select.py - Inspect and click radio element properly.
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("timebucks", "primeearn_survey")
with T.session(lane) as client:
    res = client._js(r"""
        (function() {
            var input = document.querySelector('input[type="radio"]');
            var label = document.querySelector('label.p-radio-label');
            var box = document.querySelector('.p-radio-wrapper');
            
            // Try clicking label first
            if (label) {
                label.click();
            }
            if (input) {
                input.checked = true;
                input.dispatchEvent(new Event('input', { bubbles: true }));
                input.dispatchEvent(new Event('change', { bubbles: true }));
                input.click();
            }
            
            return {
                inputChecked: input ? input.checked : null,
                inputId: input ? input.id : null,
                labelFor: label ? label.getAttribute('for') : null,
                htmlSample: box ? box.outerHTML : null
            };
        })()
    """)
    print("Radio select attempt:", json.dumps(res, indent=2))
    time.sleep(2)

    # Check if next button is visible
    btn_check = client._js(r"""
        (function() {
            var btn = document.querySelector('button.p-btn--icon-only, .next-button button, button.p-btn--primary');
            if (btn) {
                var style = window.getComputedStyle(btn);
                return {
                    found: true,
                    display: style.display,
                    visibility: style.visibility,
                    className: btn.className
                };
            }
            return { found: false };
        })()
    """)
    print("Button check:", json.dumps(btn_check, indent=2))

    shot = lane.shot(client, "test_radio_selected")
    print("Shot:", shot)
