r"""inspect_specific_task_row.py - Inspect elements and click target task.
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("timebucks", "task_inspect")
with T.session(lane) as client:
    print("Navigating to tasks_tasks...")
    client.call_tool("browser_navigate", {"url": "https://timebucks.com/publishers/index.php?pg=earn&tab=tasks_tasks"})
    time.sleep(3.5)

    res = client._js(r"""
        (function() {
            var rows = Array.from(document.querySelectorAll('table tr')).filter(r => {
                var t = r.innerText || '';
                return t.includes('YouTube Channel') || t.includes('Twitter') || t.includes('Instagram');
            });

            return rows.map(r => ({
                text: r.innerText.replace(/\s+/g, ' ').trim(),
                allLinksAndButtons: Array.from(r.querySelectorAll('a, button, input[type="button"], input[type="submit"]')).map(el => ({
                    tag: el.tagName,
                    text: (el.innerText || el.value || '').trim(),
                    href: el.getAttribute('href') || '',
                    onclick: el.getAttribute('onclick') || '',
                    id: el.id || '',
                    className: el.className || ''
                }))
            }));
        })()
    """)

    print("SPECIFIC TASK ROWS:\n", json.dumps(res, indent=2))
