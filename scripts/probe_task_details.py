r"""probe_task_details.py - Inspect task structure on Tasks tab.
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("timebucks", "task_details")
with T.session(lane) as client:
    url = "https://timebucks.com/publishers/index.php?pg=earn&tab=tasks_tasks"
    client.call_tool("browser_navigate", {"url": url})
    time.sleep(3)

    tasks_info = client._js(r"""
        (function() {
            var rows = Array.from(document.querySelectorAll('table tr, .task-row, div.task_holder, div[id*="task"]'));
            // Find rows with View button
            var viewBtns = Array.from(document.querySelectorAll('input[value="View"], button.btn, a.btn'));
            var results = [];
            for (var i = 0; i < Math.min(viewBtns.length, 5); i++) {
                var btn = viewBtns[i];
                var parent = btn.closest('tr, div') || btn.parentElement;
                results.push({
                    text: (parent.innerText || '').slice(0, 150).replace(/\s+/g, ' '),
                    tag: btn.tagName,
                    id: btn.id || '',
                    onclick: btn.getAttribute('onclick') || '',
                    href: btn.getAttribute('href') || ''
                });
            }
            return results;
        })()
    """)
    print("TOP TASKS EXTRACTED:\n", json.dumps(tasks_info, indent=2))
