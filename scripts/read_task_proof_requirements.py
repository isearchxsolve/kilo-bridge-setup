r"""read_task_proof_requirements.py - Read full instructions and proof fields for Task 4.
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("timebucks", "task_proof_reqs")
with T.session(lane) as client:
    print("Navigating to tasks_tasks...")
    client.call_tool("browser_navigate", {"url": "https://timebucks.com/publishers/index.php?pg=earn&tab=tasks_tasks"})
    time.sleep(3.5)

    # Click on View button for TimeBucks India Telegram
    click_res = client._js(r"""
        (function() {
            var rows = Array.from(document.querySelectorAll('table tr, .task_row, .table tr'));
            var targetRow = rows.find(r => (r.innerText || '').includes('TimeBucks India Telegram Channel'));
            if (!targetRow) return { found: false };

            var btn = targetRow.querySelector('input[value="View"], button, a.btn');
            if (btn) btn.click();

            return { found: true };
        })()
    """)
    print("CLICK RES:", json.dumps(click_res))
    time.sleep(3)

    details = client._js(r"""
        (function() {
            var bodyText = document.body.innerText;
            var instrIdx = bodyText.indexOf('Advertisers Instructions:');
            var instrSnippet = instrIdx !== -1 ? bodyText.slice(instrIdx, instrIdx + 1200) : '';

            // Check form fields
            var submitForm = Array.from(document.querySelectorAll('form')).find(f => {
                var act = f.getAttribute('action') || '';
                return (f.innerText || '').includes('Submit For Approval') || act.includes('SubmitTask');
            });

            var formFields = [];
            if (submitForm) {
                formFields = Array.from(submitForm.querySelectorAll('input, textarea, select')).map(el => ({
                    tag: el.tagName,
                    type: el.type || '',
                    name: el.name || '',
                    id: el.id || '',
                    placeholder: el.placeholder || '',
                    label: el.closest('div, tr, p') ? el.closest('div, tr, p').innerText.slice(0, 100).replace(/\s+/g, ' ').trim() : ''
                }));
            }

            return {
                instructions: instrSnippet,
                formFields: formFields
            };
        })()
    """)

    print("TASK DETAILS:\n", json.dumps(details, indent=2))
