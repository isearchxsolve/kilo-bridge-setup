import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("freecash", "open_cpx_verified")
with T.session(lane) as client:
    print("Navigating to https://freecash.com/en/earn...")
    client.call_tool("browser_navigate", {"url": "https://freecash.com/en/earn"})
    
    # Wait and scroll to trigger lazy loading
    for step in range(3):
        time.sleep(3)
        client._js("window.scrollBy(0, 600);")

    time.sleep(4)

    # Now find and click CPX Research or BitLabs
    click_res = client._js(r"""
        (function() {
            var items = Array.from(document.querySelectorAll('*')).filter(el => {
                var t = (el.innerText || '').trim();
                return t === 'CPX Research' || t === '3CPX Research' || t === 'BitLabs' || t === '3BitLabs';
            });

            if (items.length > 0) {
                var target = items[0];
                var clickable = target.closest('div[role="button"]') || target.closest('a') || target.closest('button') || target.parentElement || target;
                clickable.scrollIntoView({ behavior: 'smooth', block: 'center' });
                clickable.click();
                return {
                    ok: true,
                    text: target.innerText.trim(),
                    tag: clickable.tagName
                };
            }
            return {
                ok: false,
                allCards: Array.from(document.querySelectorAll('[class*="partner"], [class*="card"]')).map(c => c.innerText.slice(0, 50))
            };
        })()
    """)
    print("CLICK RESULT:\n", json.dumps(click_res, indent=2))
    time.sleep(6)

    # Check state after click
    state = client._js(r"""
        (function() {
            var iframes = Array.from(document.querySelectorAll('iframe')).map(f => f.src);
            var modal = document.querySelector('[role="dialog"], [class*="modal"], [class*="Modal"]');
            return {
                url: window.location.href,
                hasModal: !!modal,
                modalText: modal ? modal.innerText.slice(0, 600).replace(/\n+/g, ' | ') : null,
                iframes: iframes
            };
        })()
    """)
    print("STATE AFTER CLICK:\n", json.dumps(state, indent=2))

    shot = lane.shot(client, "freecash_cpx_opened_live")
    print("Screenshot saved to:", shot)
