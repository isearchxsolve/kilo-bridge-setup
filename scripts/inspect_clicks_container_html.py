r"""inspect_clicks_container_html.py - Inspect innerHTML of Clicks container #task_content_14.
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("timebucks", "clicks_html")
with T.session(lane) as client:
    tabs = client.list_tabs()
    tb_tab = next((t for t in tabs if "timebucks.com" in t.get("url", "").lower()), None)
    if tb_tab:
        client.switch_tab(tb_tab["id"])
    else:
        client.call_tool("browser_navigate", {"url": "https://timebucks.com/publishers/index.php?pg=earn&tab=view_content_ads"})
        time.sleep(3)

    container_html = client._js(r"""
        (function() {
            var el = document.querySelector('#task_content_14, .tab-pane.active, [id*="content_14"]');
            if (!el) {
                // Find element containing 'Captcha Required'
                var all = Array.from(document.querySelectorAll('div'));
                el = all.find(d => (d.innerText || '').includes('Captcha Required') && d.children.length > 0);
            }
            if (el) {
                return {
                    found: true,
                    id: el.id,
                    className: el.className,
                    innerHTML: el.innerHTML.slice(0, 2000)
                };
            }
            return {found: false};
        })()
    """)
    print("CLICKS CONTAINER HTML:\n", json.dumps(container_html, indent=2))
