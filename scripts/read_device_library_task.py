r"""read_device_library_task.py - Read instructions for browser device library task.
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("timebucks", "device_library_task")
with T.session(lane) as client:
    client.call_tool("browser_navigate", {"url": "https://timebucks.com/publishers/index.php?pg=earn&tab=tasks_tasks"})
    time.sleep(3.5)

    # Click View on browser device library task
    res = client._js(r"""
        (function() {
            var rows = Array.from(document.querySelectorAll('table tr, .task_row, .table tr'));
            var targetRow = rows.find(r => (r.innerText || '').includes('browser device library'));
            if (!targetRow) return { found: false };

            var btn = targetRow.querySelector('input[value="View"], button, a.btn');
            if (btn) btn.click();
            return { found: true };
        })()
    """)
    print("CLICK:", json.dumps(res))
    time.sleep(3)

    info = client._js(r"""
        (function() {
            var text = document.body.innerText;
            var instrIdx = text.indexOf('Advertisers Instructions:');
            return {
                instructions: instrIdx !== -1 ? text.slice(instrIdx, instrIdx + 1000) : text.slice(500, 2000)
            };
        })()
    """)
    print("INSTRUCTIONS:\n", json.dumps(info, indent=2))

    shot = lane.shot(client, "timebucks_device_library_task")
    print("Screenshot:", shot)
