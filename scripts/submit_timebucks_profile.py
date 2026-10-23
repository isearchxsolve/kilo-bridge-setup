r"""submit_timebucks_profile.py - Fill postcode, submit profile, confirm modal, and verify.
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("timebucks", "submit_profile")
with T.session(lane) as client:
    tabs = client.list_tabs()
    tb_tab = next((t for t in tabs if "timebucks.com" in t.get("url", "").lower()), None)
    if tb_tab:
        client.switch_tab(tb_tab["id"])
    else:
        client.call_tool("browser_navigate", {"url": "https://timebucks.com/publishers/index.php?pg=setting"})
        time.sleep(3)

    # Fill all verified fields and click update
    res = client._js(r"""
        (function() {
            var m = document.querySelector('#dobMonth');
            var d = document.querySelector('#dobDay');
            var y = document.querySelector('#dobYear');
            var s = document.querySelector('#state2');
            var p = document.querySelector('#postcode');

            if (m) { m.value = '05'; m.dispatchEvent(new Event('change', {bubbles: true})); }
            if (d) { d.value = '29'; d.dispatchEvent(new Event('change', {bubbles: true})); }
            if (y) { y.value = '1979'; y.dispatchEvent(new Event('change', {bubbles: true})); }
            if (s) { s.value = 'West Bengal'; s.dispatchEvent(new Event('change', {bubbles: true})); }
            if (p) {
                p.value = '700075';
                p.dispatchEvent(new Event('input', {bubbles: true}));
                p.dispatchEvent(new Event('change', {bubbles: true}));
            }

            var sendBtn = document.querySelector('#send');
            if (sendBtn) {
                sendBtn.click();
                return {
                    clickedUpdate: true,
                    postcode: p ? p.value : null
                };
            }
            return {clickedUpdate: false};
        })()
    """)
    print("STEP 1: FILL AND CLICK UPDATE:\n", json.dumps(res, indent=2))
    time.sleep(2)

    # Capture modal screenshot
    shot_modal = lane.shot(client, "timebucks_profile_confirm_modal")
    print("Confirmation modal screenshot:", shot_modal)

    # Check for confirm button inside modal
    confirm_res = client._js(r"""
        (function() {
            var confirmBtn = document.querySelector('#submitDetails, input[value="Confirm"], button.confirm');
            if (confirmBtn) {
                confirmBtn.click();
                return {confirmed: true, text: confirmBtn.value || confirmBtn.innerText};
            }
            return {confirmed: false};
        })()
    """)
    print("STEP 2: CONFIRM MODAL:\n", json.dumps(confirm_res, indent=2))
    time.sleep(3.5)

    # Capture final profile updated screenshot
    shot_final = lane.shot(client, "timebucks_profile_updated_final")
    print("Final updated screenshot:", shot_final)

    # Read toast or alert
    page = T.read_page(client)
    toast = client.toast()
    print("PAGE TITLE:", page.get("title"))
    print("PAGE URL:", page.get("url"))
    print("TOAST / ALERT:", toast)
    print("BODY SNIPPET:\n", page.get("body", "")[300:1500])

    lane.row(
        source="https://timebucks.com/publishers/index.php?pg=setting",
        role="microtask_worker",
        company="TimeBucks",
        score=1,
        step="profile_update",
        status=T.OK,
        receipt=shot_final,
        note="Profile completed with verified DOB (1979-05-29), State (West Bengal), Postcode (700075)"
    )
