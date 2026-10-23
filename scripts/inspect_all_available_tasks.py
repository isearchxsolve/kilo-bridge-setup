r"""inspect_all_available_tasks.py - Extract full details of available tasks on Tasks tab.
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("timebucks", "tasks_list")
with T.session(lane) as client:
    tabs = client.list_tabs()
    tb_tab = next((t for t in tabs if "timebucks.com" in t.get("url", "").lower()), None)
    if tb_tab:
        client.switch_tab(tb_tab["id"])
        time.sleep(1)
    else:
        client.call_tool("browser_navigate", {"url": "https://timebucks.com/publishers/index.php?pg=earn&tab=tasks_tasks"})
        time.sleep(3)

    tasks_full = client._js(r"""
        (function() {
            var rows = Array.from(document.querySelectorAll('table tr, .task_row, .table tr'));
            var results = [];
            
            rows.forEach((r, idx) => {
                var text = r.innerText.replace(/\s+/g, ' ').trim();
                if (!text || text.length < 10) return;
                
                var viewBtn = r.querySelector('input[value="View"], button, a.btn, input[type="button"]');
                var rateMatch = text.match(/\$([0-9\.]+)/);
                
                if (rateMatch && (text.includes('Instructions') || text.includes('Takes:') || text.includes('Signup') || text.includes('Telegram') || text.includes('Join') || text.includes('Subscribe'))) {
                    results.push({
                        index: idx,
                        rate: rateMatch[0],
                        summary: text.slice(0, 250),
                        btnTag: viewBtn ? viewBtn.tagName : null,
                        btnVal: viewBtn ? (viewBtn.value || viewBtn.innerText) : null,
                        btnOnclick: viewBtn ? viewBtn.getAttribute('onclick') : null
                    });
                }
            });

            return {
                totalFound: results.length,
                tasks: results.slice(0, 20)
            };
        })()
    """)

    print(json.dumps(tasks_full, indent=2))
