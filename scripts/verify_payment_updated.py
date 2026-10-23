r"""verify_payment_updated.py - Inspect current TimeBucks tab after user payment method update.
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("timebucks", "verify_payment")
with T.session(lane) as client:
    tabs = client.list_tabs()
    tb_tab = next((t for t in tabs if "timebucks.com" in t.get("url", "").lower()), None)
    if tb_tab:
        client.switch_tab(tb_tab["id"])
        time.sleep(1)

    state = client._js(r"""
        (function() {
            var alerts = Array.from(document.querySelectorAll('.alert, .noty_text, .success, div[class*="success"], div[class*="alert"]'))
                             .map(el => el.innerText.trim()).filter(Boolean);

            var select = document.querySelector('#contact_subject02') || document.querySelector('select[name="contact_subject"]');
            var phone = document.querySelector('#paypalemail');

            var modal = document.querySelector('#settingsProfilePopUp');
            var isModalVisible = modal ? (window.getComputedStyle(modal).display !== 'none') : false;

            return {
                url: window.location.href,
                alerts: alerts,
                selectedMethod: select ? (select.options[select.selectedIndex] ? select.options[select.selectedIndex].text : select.value) : null,
                phone: phone ? phone.value : null,
                isModalVisible: isModalVisible,
                modalText: modal ? modal.innerText.slice(0, 300) : null
            };
        })()
    """)

    print("PAYMENT STATE:\n", json.dumps(state, indent=2))

    shot = lane.shot(client, "timebucks_payment_state_verified")
    print("Screenshot saved to:", shot)

    lane.row(
        source=state.get("url", "https://timebucks.com/publishers/index.php?pg=setting#paypal-changes"),
        role="microtask_worker",
        company="TimeBucks",
        score=1,
        step="verify_payment_method",
        status=T.APPLIED_STEP if not state.get("isModalVisible") else T.BLOCKED,
        receipt=shot,
        note=f"Payment method: {state.get('selectedMethod')}, Phone: {state.get('phone')}, Modal visible: {state.get('isModalVisible')}"
    )
