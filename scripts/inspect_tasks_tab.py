r"""inspect_tasks_tab.py - Inspect Tasks tab (tasks_tasks) with 151 available tasks.
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("timebucks", "inspect_tasks")
with T.session(lane) as client:
    tabs = client.list_tabs()
    tb_tab = next((t for t in tabs if "timebucks.com" in t.get("url", "").lower()), None)
    if tb_tab:
        client.switch_tab(tb_tab["id"])
        time.sleep(1)

    print("Navigating to tasks_tasks...")
    client.call_tool("browser_navigate", {"url": "https://timebucks.com/publishers/index.php?pg=earn&tab=tasks_tasks"})
    time.sleep(4)

    page = T.read_page(client)
    print("PAGE TITLE:", page.get("title"))
    print("PAGE URL:", page.get("url"))

    body = page.get("body", "")
    has_captcha = "captcha required" in body.lower() or "please confirm you are not a robot" in body.lower()
    print("HAS CAPTCHA ON TASKS TAB?:", has_captcha)

    shot = lane.shot(client, "timebucks_tasks_tab_inspect")
    print("Screenshot:", shot)

    # Extract available tasks
    tasks_data = client._js(r"""
        (function() {
            var taskRows = Array.from(document.querySelectorAll('tr, .task-row, .task_item, div[class*="task"]'))
                .filter(el => {
                    var t = el.innerText || '';
                    return (t.includes('Start') || t.includes('View') || t.includes('Submit')) && t.includes('$');
                });

            // Extract table rows if table exists
            var tables = Array.from(document.querySelectorAll('table'));
            var tableRows = [];
            tables.forEach(tbl => {
                var rows = Array.from(tbl.querySelectorAll('tr'));
                rows.forEach(r => {
                    var text = r.innerText.replace(/\s+/g, ' ').trim();
                    if (text.includes('$') && (text.includes('Start') || text.includes('View'))) {
                        tableRows.push(text.slice(0, 200));
                    }
                });
            });

            var buttons = Array.from(document.querySelectorAll('input[type="button"], input[type="submit"], button, a.btn'))
                .map(b => ({
                    val: (b.value || b.innerText || '').trim(),
                    tag: b.tagName,
                    href: b.getAttribute('href') || '',
                    onclick: b.getAttribute('onclick') || ''
                })).filter(b => b.val.toLowerCase().includes('start') || b.val.toLowerCase().includes('view'));

            return {
                taskRowsCount: taskRows.length,
                tableRows: tableRows.slice(0, 10),
                actionButtons: buttons.slice(0, 10),
                bodySnippet: document.body.innerText.slice(400, 1600)
            };
        })()
    """)

    print("TASKS DATA:\n", json.dumps(tasks_data, indent=2))
