r"""survey_runner.py - Inspect and begin the 3-minute $0.17 profile survey.
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("timebucks", "survey_runner")
with T.session(lane) as client:
    print("Navigating to surveys tab...")
    client.call_tool("browser_navigate", {"url": "https://timebucks.com/publishers/index.php?pg=earn&tab=surveys"})
    time.sleep(3.5)

    # Click on the START link/button
    click_res = client._js(r"""
        (function() {
            var links = Array.from(document.querySelectorAll('a, button, input[type="button"]'));
            var startBtn = links.find(el => {
                var val = (el.value || el.innerText || '').trim();
                return val === 'START' || val.includes('START');
            });

            if (startBtn) {
                var href = startBtn.getAttribute('href');
                startBtn.click();
                return { clicked: true, href: href };
            }
            return { clicked: false };
        })()
    """)

    print("CLICK RES:", json.dumps(click_res, indent=2))
    time.sleep(5)

    # Check tabs in case it opened in a new tab
    tabs = client.list_tabs()
    print("TABS COUNT:", len(tabs))
    survey_tab = next((t for t in tabs if "timesurveys" in t.get("url", "").lower() or "survey" in t.get("url", "").lower()), None)
    if survey_tab:
        print(f"Switching to survey tab: {survey_tab.get('url')}")
        client.switch_tab(survey_tab["id"])
        time.sleep(2)

    page = T.read_page(client)
    print("SURVEY PAGE URL:", page.get("url"))
    print("SURVEY PAGE TITLE:", page.get("title"))

    shot = lane.shot(client, "timebucks_survey_page_1")
    print("Screenshot saved to:", shot)

    # Inspect question and options
    q_data = client._js(r"""
        (function() {
            var inputs = Array.from(document.querySelectorAll('input, select, textarea, button')).map(el => ({
                tag: el.tagName,
                type: el.type,
                name: el.name,
                id: el.id,
                value: el.value,
                text: el.innerText
            }));

            return {
                bodyText: document.body.innerText.slice(0, 1500),
                inputs: inputs.slice(0, 15)
            };
        })()
    """)

    print("QUESTION DATA:\n", json.dumps(q_data, indent=2))

    lane.row(
        source=page.get("url", "https://timebucks.com/publishers/index.php?pg=earn&tab=surveys"),
        role="microtask_worker",
        company="TimeBucks",
        score=1,
        step="survey_start",
        status=T.APPLIED_STEP,
        receipt=shot,
        note=f"Survey opened. Title: {page.get('title')}"
    )
