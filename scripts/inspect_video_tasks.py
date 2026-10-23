r"""inspect_video_tasks.py - Read instructions for Watch 2 mins of video and Youtube Like.
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("timebucks", "video_tasks")
with T.session(lane) as client:
    client.call_tool("browser_navigate", {"url": "https://timebucks.com/publishers/index.php?pg=earn&tab=tasks_tasks"})
    time.sleep(3.5)

    # Click View on 'Watch 2 mins of video'
    res = client._js(r"""
        (function() {
            var rows = Array.from(document.querySelectorAll('table tr, .task_row, .table tr'));
            var targetRow = rows.find(r => (r.innerText || '').includes('Watch 2 mins of video'));
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
    print("WATCH 2 MINS INSTRUCTIONS:\n", json.dumps(info, indent=2))

    shot = lane.shot(client, "timebucks_watch_video_task")
    print("Screenshot:", shot)
