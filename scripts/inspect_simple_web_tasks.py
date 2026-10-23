r"""inspect_simple_web_tasks.py - Inspect web/video tasks on TimeBucks tasks tab.
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("timebucks", "simple_tasks")
with T.session(lane) as client:
    print("Navigating to tasks_tasks...")
    client.call_tool("browser_navigate", {"url": "https://timebucks.com/publishers/index.php?pg=earn&tab=tasks_tasks"})
    time.sleep(4)

    tasks_info = client._js(r"""
        (function() {
            var rows = Array.from(document.querySelectorAll('table tr, .task_row, .table tr'));
            var matches = [];

            rows.forEach((r, idx) => {
                var text = r.innerText.replace(/\s+/g, ' ').trim();
                var btn = r.querySelector('input[value="View"], button, a.btn');
                if (btn && (text.includes('browser device library') || text.includes('Youtube Like') || text.includes('Watch 2 mins') || text.includes('Youtube Music'))) {
                    matches.push({
                        idx: idx,
                        text: text.slice(0, 200),
                        btnVal: btn.value || btn.innerText
                    });
                }
            });

            return matches;
        })()
    """)

    print("MATCHED SIMPLE TASKS:\n", json.dumps(tasks_info, indent=2))
