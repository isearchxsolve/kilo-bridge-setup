r"""set_timebucks_upi_payment.py - Configure UPI Payment & Bank Transfer payout method with verified phone fact.
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("timebucks", "setup_upi_payout")
phone = T.candidate_fact("PHONE")
if not phone:
    print("ERROR: PHONE fact not found in pinned resume!")
    sys.exit(1)

print(f"Verified candidate phone: {phone}")

with T.session(lane) as client:
    print("Navigating to payment settings...")
    client.call_tool("browser_navigate", {"url": "https://timebucks.com/publishers/index.php?pg=setting#paypal-changes"})
    time.sleep(3.5)

    update_res = client._js(f"""
        (function() {{
            var select = document.querySelector('select[name="contact_subject"]') || document.querySelector('#contact_subject02');
            if (!select) return {{ error: "No select found" }};

            select.value = "up";
            if (window.jQuery) {{
                window.jQuery(select).trigger('change');
            }} else {{
                select.dispatchEvent(new Event('change', {{ bubbles: true }}));
            }}

            var phoneInput = document.querySelector('#paypalemail');
            if (!phoneInput) return {{ error: "No phone input found" }};

            phoneInput.value = "{phone}";
            phoneInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
            phoneInput.dispatchEvent(new Event('change', {{ bubbles: true }}));

            var updateBtn = document.querySelector('input[value="Update Payment Method"]');
            if (!updateBtn) return {{ error: "No Update Payment Method button found" }};

            updateBtn.click();

            return {{
                success: true,
                selectedMethod: select.value,
                phoneEntered: phoneInput.value,
                btnClicked: true
            }};
        }})()
    """)

    print("UPDATE TRIGGER RESULT:\n", json.dumps(update_res, indent=2))
    time.sleep(4)

    shot = lane.shot(client, "timebucks_upi_payout_updated")
    print("Screenshot saved to:", shot)

    # Check alert or confirmation message
    confirm_info = client._js(r"""
        (function() {
            var alerts = Array.from(document.querySelectorAll('.alert, .success, .noty_text, div[class*="success"], div[class*="alert"]'))
                             .map(el => el.innerText.trim()).filter(Boolean);
            return {
                alerts: alerts,
                bodySnippet: document.body.innerText.slice(400, 1500)
            };
        })()
    """)
    print("CONFIRMATION INFO:\n", json.dumps(confirm_info, indent=2))

    lane.row(
        source="https://timebucks.com/publishers/index.php?pg=setting#paypal-changes",
        role="microtask_worker",
        company="TimeBucks",
        score=1,
        step="configure_payout_upi",
        status=T.APPLIED_STEP,
        receipt=shot,
        note=f"Payment method configured to UPI Payment & Bank Transfer via Easebuzz."
    )
    print("Ledger updated.")
