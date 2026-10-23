r"""configure_timebucks_payout.py - Navigate directly to pg=setting#paypal-changes and configure UPI/Litecoin.
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("timebucks", "payout_setup")
with T.session(lane) as client:
    print("Navigating to settings with hash #paypal-changes...")
    client.call_tool("browser_navigate", {"url": "https://timebucks.com/publishers/index.php?pg=setting#paypal-changes"})
    time.sleep(4)

    # Trigger the tab switch via JS in page context
    tab_status = client._js(r"""
        (function() {
            var tabLink = document.querySelector('a[href="#paypal-changes"]') ||
                          Array.from(document.querySelectorAll('a')).find(a => (a.innerText || '').includes('Payment Method'));
            
            if (tabLink) {
                tabLink.click();
            }

            var pane = document.querySelector('#paypal-changes');
            if (pane) {
                pane.classList.add('active', 'in');
                pane.style.display = 'block';
            }

            var forms = Array.from(document.querySelectorAll('form')).map(f => ({
                action: f.action,
                selects: Array.from(f.querySelectorAll('select')).map(s => ({
                    id: s.id,
                    name: s.name,
                    options: Array.from(s.options).map(o => ({ value: o.value, text: o.text }))
                })),
                inputs: Array.from(f.querySelectorAll('input')).map(i => ({
                    id: i.id,
                    name: i.name,
                    type: i.type,
                    value: i.value,
                    placeholder: i.placeholder
                }))
            }));

            return {
                tabFound: !!tabLink,
                paneFound: !!pane,
                paneText: pane ? pane.innerText.slice(0, 1000) : '',
                forms: forms
            };
        })()
    """)

    print("TAB STATUS:\n", json.dumps(tab_status, indent=2))

    shot = lane.shot(client, "timebucks_payout_methods_revealed")
    print("Screenshot saved to:", shot)
