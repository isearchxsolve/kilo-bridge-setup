import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("freecash", "open_cpx")
with T.session(lane) as client:
    print("Navigating to https://freecash.com/en/earn...")
    client.call_tool("browser_navigate", {"url": "https://freecash.com/en/earn"})
    time.sleep(5)

    # Click CPX Research
    click_res = client._js(r"""
        (function() {
            var all = Array.from(document.querySelectorAll('*'));
            var target = all.find(el => (el.innerText || '').trim() === 'CPX Research' || (el.innerText || '').trim() === '3CPX Research');
            if (!target) {
                target = all.find(el => (el.innerText || '').toLowerCase().includes('cpx research'));
            }

            if (target) {
                var clickable = target.closest('div[role="button"]') || target.closest('a') || target.closest('button') || target.parentElement || target;
                clickable.scrollIntoView({ behavior: 'smooth', block: 'center' });
                clickable.click();
                return {
                    ok: true,
                    clickedText: target.innerText.trim(),
                    tag: clickable.tagName
                };
            }
            return { ok: false, error: 'CPX Research element not found' };
        })()
    """)
    print("CLICK CPX RESULT:", json.dumps(click_res, indent=2))
    time.sleep(6)

    # Inspect modal, iframe or surveys
    modal_info = client._js(r"""
        (function() {
            var iframes = Array.from(document.querySelectorAll('iframe')).map(f => ({
                src: f.getAttribute('src') || '',
                id: f.id,
                className: f.className
            }));

            var modal = document.querySelector('[role="dialog"], [class*="modal"], [class*="Modal"], [class*="overlay"]');

            return {
                url: window.location.href,
                hasModal: !!modal,
                modalText: modal ? modal.innerText.slice(0, 500).replace(/\n+/g, ' | ') : null,
                iframes: iframes
            };
        })()
    """)
    print("MODAL / IFRAME STATE:\n", json.dumps(modal_info, indent=2))

    shot = lane.shot(client, "freecash_cpx_modal")
    print("Screenshot saved to:", shot)
    lane.row("freecash.com/en/earn", "Open CPX Research", "Freecash", 0, "open_cpx_partner", T.OK, shot, "Clicked CPX Research survey partner")
