r"""inspect_task_instructions.py - Open instructions for Telegram / YouTube tasks on Tasks tab.
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
    print("Navigating to tasks tab...")
    client.call_tool("browser_navigate", {"url": "https://timebucks.com/publishers/index.php?pg=earn&tab=tasks_tasks"})
    time.sleep(4)

    # Find the row for 'TimeBucks India' or 'Official TimeBucks Telegram'
    task_info = client._js(r"""
        (function() {
            var rows = Array.from(document.querySelectorAll('table tr, .task_row, .table tr'));
            var targetRow = rows.find(r => {
                var t = r.innerText || '';
                return t.includes('TimeBucks India Telegram') || t.includes('TimeBucks Telegram') || t.includes('TimeBucks YouTube');
            });

            if (!targetRow) return { found: false };

            var viewBtn = targetRow.querySelector('input[value="View"], button, a.btn, input[type="button"]');
            var btnInfo = null;
            if (viewBtn) {
                btnInfo = {
                    tag: viewBtn.tagName,
                    val: viewBtn.value || viewBtn.innerText,
                    onclick: viewBtn.getAttribute('onclick'),
                    id: viewBtn.id
                };
                // Click the View button to open instructions
                viewBtn.click();
            }

            return {
                found: true,
                rowText: targetRow.innerText.slice(0, 300),
                btnInfo: btnInfo
            };
        })()
    """)

    print("TASK ROW FOUND & CLICKED:", json.dumps(task_info, indent=2))
    time.sleep(3.5)

    shot = lane.shot(client, "timebucks_task_opened")
    print("Screenshot:", shot)

    # Read page/modal after clicking view
    modal_info = client._js(r"""
        (function() {
            var modal = document.querySelector('.modal, .modal-dialog, .popup, #task_content, .task-details, div[class*="instruction"]');
            var forms = Array.from(document.querySelectorAll('form')).map(f => ({
                action: f.action,
                inputs: Array.from(f.querySelectorAll('input, textarea, button, select')).map(i => ({
                    tag: i.tagName,
                    name: i.name,
                    id: i.id,
                    type: i.type,
                    value: i.value,
                    placeholder: i.placeholder
                }))
            }));

            return {
                modalText: modal ? modal.innerText.slice(0, 1000) : null,
                bodySnippet: document.body.innerText.slice(500, 2500),
                formsCount: forms.length,
                forms: forms.slice(0, 3)
            };
        })()
    """)

    print("AFTER CLICK DETAILS:\n", json.dumps(modal_info, indent=2))
