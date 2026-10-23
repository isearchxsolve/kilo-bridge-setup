import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("freecash", "trigger_cpx")
with T.session(lane) as client:
    print("Navigating to https://freecash.com/en/earn...")
    client.call_tool("browser_navigate", {"url": "https://freecash.com/en/earn"})
    time.sleep(6)
    client._js("window.scrollTo(0, 900);")
    time.sleep(3)

    res = client._js(r"""
        (function() {
            var targetSpan = Array.from(document.querySelectorAll('span')).find(s => (s.innerText || '').trim() === 'CPX Research' || (s.innerText || '').trim() === 'BitLabs');
            if (!targetSpan) return { error: 'Survey partner span not found' };

            var card = targetSpan.closest('.motion-safe\\:data-pressed\\:animate-cardPressBounce') || targetSpan.parentElement;

            // Dispatch full pointer and mouse sequence
            var rect = card.getBoundingClientRect();
            var x = rect.left + rect.width / 2;
            var y = rect.top + rect.height / 2;

            var opts = { bubbles: true, cancelable: true, view: window, clientX: x, clientY: y };
            card.dispatchEvent(new PointerEvent('pointerdown', opts));
            card.dispatchEvent(new MouseEvent('mousedown', opts));
            card.dispatchEvent(new PointerEvent('pointerup', opts));
            card.dispatchEvent(new MouseEvent('mouseup', opts));
            card.dispatchEvent(new MouseEvent('click', opts));

            return {
                ok: true,
                target: targetSpan.innerText.trim(),
                cardTag: card.tagName,
                cardClass: card.className
            };
        })()
    """)
    print("TRIGGER RESULT:\n", json.dumps(res, indent=2))
    time.sleep(5)

    check = client._js(r"""
        (function() {
            var iframes = Array.from(document.querySelectorAll('iframe')).map(f => f.src).filter(Boolean);
            var modal = document.querySelector('[role="dialog"], [class*="modal"], [class*="Modal"], [class*="Drawer"], [class*="drawer"]');
            return {
                url: window.location.href,
                hasModal: !!modal,
                modalText: modal ? modal.innerText.slice(0, 500).replace(/\n+/g, ' | ') : null,
                iframes: iframes
            };
        })()
    """)
    print("CHECK RESULT:\n", json.dumps(check, indent=2))

    shot = lane.shot(client, "freecash_partner_modal_opened")
    print("Screenshot saved to:", shot)
