r"""switch_and_probe_timebucks.py - Locate Timebucks tab, switch to it, and probe.
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("timebucks", "switch_and_probe")
with T.session(lane) as client:
    tabs = client.list_tabs()
    print("ALL OPEN TABS:")
    for t in tabs:
        print(f"  ID: {t.get('id')} | URL: {t.get('url')} | TITLE: {t.get('title')}")

    tb_tab = next((t for t in tabs if "timebucks.com" in t.get("url", "").lower()), None)
    if tb_tab:
        print(f"Switching to TimeBucks tab {tb_tab['id']}...")
        client.switch_tab(tb_tab["id"])
        time.sleep(1.5)
    else:
        print("TimeBucks tab not in list; navigating directly...")
        client.call_tool("browser_navigate", {"url": "https://timebucks.com/publishers/index.php?pg=earn"})
        time.sleep(3.5)

    page = T.read_page(client)
    print("ACTIVE URL:", page.get("url"))
    print("ACTIVE TITLE:", page.get("title"))

    # Now find the sub-tabs
    subtabs = client._js(r"""
        (function() {
            var els = Array.from(document.querySelectorAll('a, button, div.tab, li'));
            return els
                .map(e => ({
                    text: (e.innerText || '').trim(),
                    href: e.getAttribute('href') || '',
                    onclick: e.getAttribute('onclick') || '',
                    tag: e.tagName
                }))
                .filter(x => x.text && ['tasks', 'surveys', 'clicks', 'bonus clicks', 'games', 'daily streak'].includes(x.text.toLowerCase()));
        })()
    """)
    print("MATCHED SUB-TABS:", json.dumps(subtabs, indent=2))

    # Let's inspect the href or click the 'Clicks' tab
    clicks_tab = next((s for s in (subtabs or []) if s["text"].lower() == "clicks"), None)
    if clicks_tab and clicks_tab.get("href"):
        url_to_go = clicks_tab["href"]
        if not url_to_go.startswith("http"):
            url_to_go = "https://timebucks.com/publishers/" + url_to_go.lstrip("/")
        print("Navigating to Clicks URL directly:", url_to_go)
        client.call_tool("browser_navigate", {"url": url_to_go})
    else:
        print("Clicking element with text 'Clicks'...")
        client._js(r"""
            (function() {
                var els = Array.from(document.querySelectorAll('a, button, div, span, li'));
                var target = els.find(e => (e.innerText || '').trim().toLowerCase() === 'clicks');
                if (target) target.click();
            })()
        """)

    time.sleep(4)
    shot = lane.shot(client, "timebucks_clicks_view")
    print("Clicks page shot:", shot)
    clicks_page = T.read_page(client)
    print("CLICKS PAGE URL:", clicks_page.get("url"))
    print("CLICKS PAGE BODY SNIPPET:\n", clicks_page.get("body", "")[:1200])
