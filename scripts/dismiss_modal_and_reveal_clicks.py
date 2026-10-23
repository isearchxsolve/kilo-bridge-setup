r"""dismiss_modal_and_reveal_clicks.py - Dismiss modal overlay on Clicks tab.
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("timebucks", "dismiss_modal")
with T.session(lane) as client:
    tabs = client.list_tabs()
    tb_tab = next((t for t in tabs if "timebucks.com" in t.get("url", "").lower()), None)
    if tb_tab:
        client.switch_tab(tb_tab["id"])
    else:
        client.call_tool("browser_navigate", {"url": "https://timebucks.com/publishers/index.php?pg=earn&tab=view_content_ads"})
        time.sleep(3)

    print("Dismissing #appInstallModal overlay...")
    res = client._js(r"""
        (function() {
            var closeBtn = document.querySelector('#closeModalButton');
            var skipBtn = document.querySelector('#confirmSkipOfferBtn');
            var modal = document.querySelector('#appInstallModal');

            if (closeBtn) {
                closeBtn.click();
                return {dismissed: true, button: 'closeModalButton'};
            } else if (skipBtn) {
                skipBtn.click();
                return {dismissed: true, button: 'confirmSkipOfferBtn'};
            } else if (modal) {
                modal.style.display = 'none';
                return {dismissed: true, method: 'hidden'};
            }
            return {dismissed: false};
        })()
    """)
    print("DISMISS RESULT:\n", json.dumps(res, indent=2))
    time.sleep(2)

    shot = lane.shot(client, "timebucks_clicks_after_modal_dismiss")
    print("Screenshot saved to:", shot)

    # Now inspect captcha container again
    captcha_state = client._js(r"""
        (function() {
            var text = document.body.innerText || '';
            var iframes = Array.from(document.querySelectorAll('iframe')).map(f => f.src);
            var captchaBoxes = Array.from(document.querySelectorAll('div[class*="captcha"], div[class*="cf-turnstile"], div[id*="turnstile"]'));
            return {
                iframes: iframes,
                captchaBoxes: captchaBoxes.map(b => b.outerHTML.slice(0, 200)),
                hasRobotText: text.includes('confirm you are not a robot')
            };
        })()
    """)
    print("CAPTCHA STATE AFTER DISMISS:\n", json.dumps(captcha_state, indent=2))
