import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("timebucks", "inspect_tasks_clicks")
with T.session(lane) as client:
    print("Navigating to TimeBucks Clicks...")
    client.call_tool("browser_navigate", {"url": "https://timebucks.com/publishers/index.php?pg=earn&tab=view_content_ads"})
    time.sleep(4)

    clicks_info = client._js(r"""
        (function() {
            var cards = Array.from(document.querySelectorAll('.view-ad-box, .ad-card, [id^="ad-"], tr, .card')).map(el => ({
                text: el.innerText.trim().replace(/\n+/g, ' | ').slice(0, 150)
            })).filter(x => x.text.includes('$') || x.text.includes('sec'));

            var viewBtns = Array.from(document.querySelectorAll('button, a.btn, input[type="button"]')).map(b => ({
                text: b.innerText.trim(),
                href: b.getAttribute('href') || '',
                onclick: b.getAttribute('onclick') || ''
            })).filter(x => x.text.toLowerCase().includes('view') || x.text.toLowerCase().includes('click'));

            var bal = document.querySelector('.header-total-balance, [class*="total-balance"], [class*="balance"]');

            return {
                url: window.location.href,
                balance: bal ? bal.innerText.trim() : null,
                cardsCount: cards.length,
                cardsSample: cards.slice(0, 5),
                viewBtns: viewBtns.slice(0, 5)
            };
        })()
    """)
    print("CLICKS INFO:\n", json.dumps(clicks_info, indent=2))
    shot_clicks = lane.shot(client, "timebucks_clicks_live")

    # Now check Tasks tab
    print("Navigating to TimeBucks Tasks...")
    client.call_tool("browser_navigate", {"url": "https://timebucks.com/publishers/index.php?pg=earn&tab=tasks_tasks"})
    time.sleep(4)

    tasks_info = client._js(r"""
        (function() {
            var rows = Array.from(document.querySelectorAll('tr, .task-row, .card')).map(r => ({
                text: r.innerText.trim().replace(/\n+/g, ' | ').slice(0, 150)
            })).filter(x => x.text.includes('$') && (x.text.includes('Start') || x.text.includes('View') || x.text.includes('Submit')));

            var startBtns = Array.from(document.querySelectorAll('button, a.btn')).map(b => ({
                text: b.innerText.trim(),
                href: b.getAttribute('href') || ''
            })).filter(x => x.text.toLowerCase().includes('start') || x.text.toLowerCase().includes('view'));

            return {
                url: window.location.href,
                rowsCount: rows.length,
                rowsSample: rows.slice(0, 5),
                startBtns: startBtns.slice(0, 5)
            };
        })()
    """)
    print("TASKS INFO:\n", json.dumps(tasks_info, indent=2))
    shot_tasks = lane.shot(client, "timebucks_tasks_live")

    lane.row("timebucks.com", "Tasks & Clicks Catalog", "TimeBucks", 0, "catalog_scan", T.OK, shot_tasks, f"Found {clicks_info.get('cardsCount')} clicks, {tasks_info.get('rowsCount')} tasks")
