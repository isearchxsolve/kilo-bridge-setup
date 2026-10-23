r"""list_all_tasks.py - Extract all microtasks from TimeBucks tasks_tasks tab.
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("timebucks", "list_tasks")
with T.session(lane) as client:
    print("Navigating to tasks_tasks...")
    client.call_tool("browser_navigate", {"url": "https://timebucks.com/publishers/index.php?pg=earn&tab=tasks_tasks"})
    time.sleep(3.5)

    data = client._js(r"""
        (function() {
            var rows = Array.from(document.querySelectorAll('table tr')).filter(r => {
                var text = r.innerText || '';
                return text.includes('$') && (text.includes('Start') || text.includes('View'));
            });

            var tasks = rows.map((r, idx) => {
                var cells = Array.from(r.querySelectorAll('td')).map(c => c.innerText.replace(/\s+/g, ' ').trim());
                var btn = r.querySelector('input[type="button"], input[type="submit"], button, a');
                var btnInfo = btn ? {
                    tag: btn.tagName,
                    text: (btn.value || btn.innerText || '').trim(),
                    href: btn.getAttribute('href') || '',
                    onclick: btn.getAttribute('onclick') || ''
                } : null;

                return {
                    index: idx,
                    raw: r.innerText.replace(/\s+/g, ' ').trim(),
                    cells: cells,
                    button: btnInfo
                };
            });

            // Check if there are category or sort filters
            var selects = Array.from(document.querySelectorAll('select')).map(s => ({
                id: s.id,
                name: s.name,
                options: Array.from(s.options).map(o => ({ value: o.value, text: o.text }))
            }));

            return {
                url: window.location.href,
                tasksFound: tasks.length,
                tasks: tasks.slice(0, 20),
                filters: selects
            };
        })()
    """)

    print("TASKS OVERVIEW:\n", json.dumps(data, indent=2))
    shot = lane.shot(client, "timebucks_tasks_overview_list")
    print("Screenshot:", shot)
