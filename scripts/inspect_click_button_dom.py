r"""inspect_click_button_dom.py - Inspect the View button element, form, listeners, and handlers.
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("timebucks", "inspect_btn_dom")
with T.session(lane) as client:
    # Always ensure we navigate to Clicks URL
    client.call_tool("browser_navigate", {"url": "https://timebucks.com/publishers/index.php?pg=earn&tab=view_content_ads"})
    time.sleep(3.5)

    info = client._js(r"""
        (function() {
            var allInputs = Array.from(document.querySelectorAll('input, button, a'));
            var viewBtn = allInputs.find(b => (b.value || b.innerText || '').toLowerCase().trim() === 'view');
            
            if (!viewBtn) {
                return {
                    found: false,
                    bodyText: document.body.innerText.slice(400, 1500)
                };
            }

            var form = viewBtn.closest('form');
            var parent = viewBtn.parentElement;
            
            // Check jQuery event listeners if jQuery is present
            var jqEvents = null;
            if (window.jQuery && window.jQuery._data) {
                var events = window.jQuery._data(viewBtn, 'events');
                if (events) {
                    jqEvents = Object.keys(events);
                }
            }

            return {
                found: true,
                tagName: viewBtn.tagName,
                outerHTML: viewBtn.outerHTML,
                attributes: Array.from(viewBtn.attributes).map(a => ({ name: a.name, value: a.value })),
                parentHTML: parent ? parent.outerHTML.slice(0, 500) : null,
                formHTML: form ? form.outerHTML.slice(0, 500) : null,
                formAction: form ? form.action : null,
                formMethod: form ? form.method : null,
                jqEvents: jqEvents,
                rect: viewBtn.getBoundingClientRect()
            };
        })()
    """)

    print("INSPECTION RESULT:\n", json.dumps(info, indent=2))
