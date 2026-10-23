r"""inspect_timebucks_tab.py - Accurately find TimeBucks tab and inspect current view content ads state.
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("timebucks", "inspect_tab")
with T.session(lane) as client:
    tabs = client.list_tabs()
    print("ALL TABS:")
    for i, t in enumerate(tabs):
        print(f"  [{i}] ID: {t.get('id')} | Title: {t.get('title')} | URL: {t.get('url')}")

    tb_tab = next((t for t in tabs if "timebucks.com" in t.get("url", "").lower()), None)
    if tb_tab:
        print(f"Switching to TimeBucks tab ID {tb_tab['id']}...")
        client.switch_tab(tb_tab["id"])
        time.sleep(1)
    else:
        print("No TimeBucks tab found in list_tabs! Navigating...")
        client.call_tool("browser_navigate", {"url": "https://timebucks.com/publishers/index.php?pg=earn&tab=view_content_ads"})
        time.sleep(3)

    page = T.read_page(client)
    print("CURRENT PAGE URL:", page.get("url"))
    print("CURRENT PAGE TITLE:", page.get("title"))

    # Inspect all forms and inputs inside the main content area
    details = client._js(r"""
        (function() {
            var inputs = Array.from(document.querySelectorAll('input, button, a')).map(el => {
                var val = el.value || el.innerText || '';
                return {
                    tag: el.tagName,
                    type: el.type || '',
                    name: el.name || '',
                    id: el.id || '',
                    value: val.trim(),
                    onclick: el.getAttribute('onclick') || '',
                    href: el.getAttribute('href') || '',
                    className: el.className || '',
                    formAction: el.form ? el.form.action : null
                };
            }).filter(item => {
                var v = item.value.toLowerCase();
                return v.includes('view') || v.includes('click') || item.type === 'submit' || item.type === 'button';
            });

            // Find current balance elements
            var balElems = Array.from(document.querySelectorAll('*')).filter(el => {
                return (el.innerText || '').includes('0.40') || (el.innerText || '').includes('Wallet');
            }).slice(0, 5).map(el => ({ tag: el.tagName, text: el.innerText.slice(0, 100) }));

            // Check if there is an iframe or modal
            var iframes = Array.from(document.querySelectorAll('iframe')).map(f => f.src);

            return {
                buttons: inputs,
                balElems: balElems,
                iframes: iframes,
                textSnippet: document.body.innerText.slice(500, 2000)
            };
        })()
    """)
    print("INSPECTION DETAILS:\n", json.dumps(details, indent=2))
