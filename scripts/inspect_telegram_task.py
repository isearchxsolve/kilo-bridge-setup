r"""inspect_telegram_task.py - View instructions for Telegram channel task.
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("timebucks", "telegram_task")
with T.session(lane) as client:
    url = "https://timebucks.com/publishers/index.php?pg=earn&tab=tasks_tasks"
    client.call_tool("browser_navigate", {"url": url})
    time.sleep(3.5)

    # Click View on the Telegram task
    click_res = client._js(r"""
        (function() {
            var rows = Array.from(document.querySelectorAll('table tr, div'));
            var targetRow = rows.find(r => (r.innerText || '').includes('TimeBucks India Telegram Channel'));
            if (!targetRow) return {found: false};

            var viewBtn = targetRow.querySelector('input[value="View"], button.btn, a.btn');
            if (viewBtn) {
                viewBtn.click();
                return {clicked: true, text: targetRow.innerText.slice(0, 200)};
            }
            return {found: true, clicked: false};
        })()
    """)
    print("CLICK RES:\n", json.dumps(click_res, indent=2))
    time.sleep(3)

    shot = lane.shot(client, "timebucks_telegram_task_view")
    print("Screenshot saved to:", shot)
    page = T.read_page(client)
    print("PAGE TITLE:", page.get("title"))
    print("PAGE URL:", page.get("url"))
    print("INSTRUCTIONS SNIPPET:\n", page.get("body", "")[300:2000])
