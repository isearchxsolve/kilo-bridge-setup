r"""open_task_campaign.py - Click View on TimeBucks YouTube task and inspect details.
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("timebucks", "open_task")
with T.session(lane) as client:
    print("Navigating to tasks_tasks...")
    client.call_tool("browser_navigate", {"url": "https://timebucks.com/publishers/index.php?pg=earn&tab=tasks_tasks"})
    time.sleep(3.5)

    # Click 'View' button on YouTube row
    click_res = client._js(r"""
        (function() {
            var rows = Array.from(document.querySelectorAll('table tr')).filter(r => {
                return (r.innerText || '').includes('TimeBucks YouTube Channel');
            });

            if (rows.length === 0) return { ok: false, error: 'YouTube row not found' };

            var viewBtn = rows[0].querySelector('input[value="View"], .install-btn, a.btnTasksViewCampaign');
            if (viewBtn) {
                viewBtn.click();
                return { ok: true, clicked: viewBtn.tagName, val: viewBtn.value || viewBtn.innerText };
            }
            return { ok: false, error: 'View button not found in row' };
        })()
    """)
    print("Click result:", json.dumps(click_res, indent=2))

    time.sleep(4)

    # Inspect the view/details screen or modal
    details = client._js(r"""
        (function() {
            var popup = document.querySelector('.modal, #task_content, .taskDetails, div[id*="popup"], div[class*="popup"]');
            var inputs = Array.from(document.querySelectorAll('input, textarea, button, a.btn')).map(el => ({
                tag: el.tagName,
                id: el.id,
                name: el.name,
                type: el.type,
                val: (el.value || el.innerText || '').trim(),
                href: el.getAttribute('href') || ''
            })).filter(x => x.val.length > 0 && x.val.length < 50);

            return {
                url: window.location.href,
                popupFound: !!popup,
                popupText: popup ? popup.innerText.slice(0, 1500) : null,
                bodySnippet: document.body.innerText.slice(400, 2000),
                buttons: inputs
            };
        })()
    """)
    print("AFTER CLICK DETAILS:\n", json.dumps(details, indent=2))

    shot = lane.shot(client, "timebucks_youtube_task_details")
    print("Screenshot:", shot)
