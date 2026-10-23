import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("coinpayu", "inspect_jquery_events")
with T.session(lane) as client:
    client.call_tool("browser_navigate", {"url": "https://www.rewardjoy.com/dashboard/ads_surf"})
    time.sleep(3)

    info = client._js(r"""
        (function() {
            if (typeof $ === 'undefined' || !$._data) return { error: 'jQuery not found' };

            var el = $('.ags-description')[0];
            var elEvents = el ? $._data(el, 'events') : null;
            var docEvents = $._data(document, 'events');
            var bodyEvents = $._data(document.body, 'events');

            function serializeEvents(evObj) {
                if (!evObj) return null;
                var res = {};
                for (var type in evObj) {
                    res[type] = evObj[type].map(function(h) {
                        return {
                            selector: h.selector,
                            handlerStr: (h.handler ? h.handler.toString() : '').slice(0, 300)
                        };
                    });
                }
                return res;
            }

            return {
                elEvents: serializeEvents(elEvents),
                docClickEvents: docEvents && docEvents.click ? serializeEvents({ click: docEvents.click }) : null,
                bodyClickEvents: bodyEvents && bodyEvents.click ? serializeEvents({ click: bodyEvents.click }) : null
            };
        })()
    """)
    print("JQUERY EVENTS:\n", json.dumps(info, indent=2))
