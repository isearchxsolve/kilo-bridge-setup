r"""scroll_and_inspect_tasks.py - Scroll down to tasks table on TimeBucks and inspect.
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("timebucks", "scroll_tasks")
with T.session(lane) as client:
    print("Navigating to tasks_tasks...")
    client.call_tool("browser_navigate", {"url": "https://timebucks.com/publishers/index.php?pg=earn&tab=tasks_tasks"})
    time.sleep(3.5)

    # Scroll down to reveal tasks table
    client._js(r"window.scrollBy(0, 500);")
    time.sleep(1)

    tasks_info = client._js(r"""
        (function() {
            // Find all tables and their rows
            var rows = Array.from(document.querySelectorAll('table tr, .table tr, #tasksTable tr, div[id*="task"] tr')).map(r => {
                var text = r.innerText.replace(/\s+/g, ' ').trim();
                var btn = r.querySelector('input[type="button"], input[type="submit"], button, a.btn, a');
                return {
                    text: text.slice(0, 250),
                    hasButton: !!btn,
                    btnText: btn ? (btn.value || btn.innerText || '').trim() : null,
                    btnOnclick: btn ? btn.getAttribute('onclick') : null
                };
            }).filter(r => r.text.includes('$') || r.hasButton);

            // Also check for task cards/divs if not in table
            var cards = Array.from(document.querySelectorAll('.taskCard, .task-card, .task, [class*="task-item"]')).map(c => ({
                text: c.innerText.replace(/\s+/g, ' ').trim().slice(0, 200)
            }));

            return {
                url: window.location.href,
                rowsCount: rows.length,
                rowsSample: rows.slice(0, 15),
                cardsCount: cards.length,
                cardsSample: cards.slice(0, 10),
                totalPageTextLength: document.body.innerText.length
            };
        })()
    """)

    print("TASKS INSPECTION:\n", json.dumps(tasks_info, indent=2))
    shot = lane.shot(client, "timebucks_tasks_scrolled")
    print("Screenshot:", shot)
