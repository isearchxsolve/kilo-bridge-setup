import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("freecash", "invoke_react_survey")
with T.session(lane) as client:
    print("Navigating to https://freecash.com/en/earn...")
    client.call_tool("browser_navigate", {"url": "https://freecash.com/en/earn"})
    time.sleep(6)
    client._js("window.scrollTo(0, 900);")
    time.sleep(3)

    res = client._js(r"""
        (function() {
            var span = Array.from(document.querySelectorAll('span')).find(s => (s.innerText || '').trim() === 'CPX Research' || (s.innerText || '').trim() === 'BitLabs');
            if (!span) return { error: 'No survey span' };

            var cur = span;
            var foundHandler = null;
            var handlerNode = null;

            while (cur && cur !== document.body) {
                var propKey = Object.keys(cur).find(k => k.startsWith('__reactProps$'));
                if (propKey && cur[propKey]) {
                    var p = cur[propKey];
                    if (typeof p.onClick === 'function') {
                        foundHandler = p.onClick;
                        handlerNode = cur;
                        break;
                    }
                    if (typeof p.onPress === 'function') {
                        foundHandler = p.onPress;
                        handlerNode = cur;
                        break;
                    }
                }
                cur = cur.parentElement;
            }

            if (foundHandler && handlerNode) {
                try {
                    var syntheticEvent = {
                        target: handlerNode,
                        currentTarget: handlerNode,
                        nativeEvent: new MouseEvent('click', { bubbles: true, cancelable: true }),
                        preventDefault: function(){},
                        stopPropagation: function(){},
                        persist: function(){}
                    };
                    foundHandler(syntheticEvent);
                    return { ok: true, invokedOn: handlerNode.tagName, class: handlerNode.className };
                } catch(e) {
                    return { ok: false, error: e.toString(), stack: e.stack };
                }
            }

            return { ok: false, error: 'No handler found' };
        })()
    """)
    print("REACT INVOCATION RESULT:\n", json.dumps(res, indent=2))
    time.sleep(6)

    check = client._js(r"""
        (function() {
            var iframes = Array.from(document.querySelectorAll('iframe')).map(f => f.src).filter(Boolean);
            var modal = document.querySelector('[role="dialog"], [class*="modal"], [class*="Modal"], [class*="drawer"]');
            return {
                url: window.location.href,
                hasModal: !!modal,
                modalText: modal ? modal.innerText.slice(0, 500).replace(/\n+/g, ' | ') : null,
                iframes: iframes
            };
        })()
    """)
    print("POST STATE:\n", json.dumps(check, indent=2))

    shot = lane.shot(client, "freecash_react_invoked_success")
    print("Screenshot saved to:", shot)
