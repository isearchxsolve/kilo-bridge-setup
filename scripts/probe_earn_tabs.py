r"""probe_earn_tabs.py - Inspect Clicks, Bonus Clicks, and Tasks tabs.
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("timebucks", "probe_tabs")
with T.session(lane) as client:
    # 1. Inspect sub-tab links on the current page
    tabs_data = client._js(r"""
        (function() {
            var allLinks = Array.from(document.querySelectorAll('a, button, div.tab'));
            return allLinks
                .filter(el => {
                    var txt = (el.innerText || '').toLowerCase();
                    return txt.includes('clicks') || txt.includes('tasks') || txt.includes('bonus');
                })
                .map(el => ({
                    tag: el.tagName,
                    text: (el.innerText || '').trim(),
                    href: el.getAttribute('href') || '',
                    onclick: el.getAttribute('onclick') || '',
                    className: el.className
                }));
        })()
    """)
    print("SUB-TABS DETECTED:", json.dumps(tabs_data, indent=2))

    # 2. Click the 'Clicks' tab
    print("Clicking 'Clicks' sub-tab...")
    click_res = client._js(r"""
        (function() {
            var els = Array.from(document.querySelectorAll('a, button, div, span'));
            var target = els.find(e => (e.innerText || '').trim().toLowerCase() === 'clicks');
            if (target) {
                target.click();
                return {clicked: true, text: target.innerText};
            }
            return {clicked: false};
        })()
    """)
    print("CLICK RES:", click_res)
    time.sleep(3.5)

    shot1 = lane.shot(client, "timebucks_tab_clicks")
    print("Clicks tab screenshot:", shot1)
    page1 = T.read_page(client)
    print("Clicks URL:", page1.get("url"))
    print("Clicks Title:", page1.get("title"))
    print("Clicks Body snippet:\n", page1.get("body", "")[:800])
