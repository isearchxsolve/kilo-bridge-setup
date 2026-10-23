r"""inspect_top_tasks_proofs.py - Inspect advertiser instructions and required proofs for top tasks.
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("timebucks", "tasks_proofs")
with T.session(lane) as client:
    print("Navigating to tasks_tasks...")
    client.call_tool("browser_navigate", {"url": "https://timebucks.com/publishers/index.php?pg=earn&tab=tasks_tasks"})
    time.sleep(4)

    page_info = client._js(r"""
        (function() {
            var rows = Array.from(document.querySelectorAll('table tr, .task_row, .table tr'));
            var targetTasks = [];
            
            rows.forEach((r, idx) => {
                var text = r.innerText.replace(/\s+/g, ' ').trim();
                var btn = r.querySelector('input[value="View"], button, a.btn');
                if (btn && (text.includes('Telegram') || text.includes('YouTube') || text.includes('Twitter') || text.includes('Instagram') || text.includes('Tiktok') || text.includes('video'))) {
                    targetTasks.push({
                        idx: idx,
                        title: text.slice(0, 150),
                        btnId: btn.id
                    });
                }
            });

            return {
                totalFound: targetTasks.length,
                tasks: targetTasks.slice(0, 8)
            };
        })()
    """)

    print("TARGET TASKS:\n", json.dumps(page_info, indent=2))
