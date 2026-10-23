r"""survey_step.py - Find and switch to timesurveys tab, accept terms, read question.
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("timebucks", "survey_step")
with T.session(lane) as client:
    tabs = client.list_tabs()
    print("ALL TABS:")
    for t in tabs:
        print("  ", t.get("id"), "|", t.get("title"), "|", t.get("url"))

    survey_tab = next((t for t in tabs if "timesurveys" in t.get("url", "").lower()), None)
    if not survey_tab:
        print("No timesurveys tab found in list_tabs! Navigating...")
        survey_url = "https://web.timesurveys.com/privacy-policy/cus_V5QK7E6LWZx0v/sur_BYdxlqzqqz8kD?expires=1791571405&signature=4fc70231d3c7cee7bf1a56fac62b19c1766f224d13519b62c9ea540fd9aff3bc"
        client.call_tool("browser_navigate", {"url": survey_url})
        time.sleep(4)
    else:
        print(f"Switching to timesurveys tab {survey_tab['id']}...")
        client.switch_tab(survey_tab["id"])
        time.sleep(2)

    page = T.read_page(client)
    print("PAGE TITLE:", page.get("title"))
    print("PAGE URL:", page.get("url"))

    # If on privacy policy, check box and click continue
    action_res = client._js(r"""
        (function() {
            var cb = document.querySelector('input[type="checkbox"]');
            var btn = Array.from(document.querySelectorAll('button, input[type="button"]')).find(b => {
                var t = (b.innerText || b.value || '').trim().toLowerCase();
                return t.includes('continue to survey') || t.includes('continue') || t.includes('next');
            });

            if (cb && !cb.checked) {
                cb.click();
            }

            var clicked = false;
            if (btn) {
                btn.click();
                clicked = true;
            }

            return {
                hadCheckbox: !!cb,
                checked: cb ? cb.checked : null,
                hadButton: !!btn,
                clicked: clicked
            };
        })()
    """)

    print("ACTION RES:", json.dumps(action_res, indent=2))
    time.sleep(4)

    shot = lane.shot(client, "survey_active_screen")
    print("Screenshot saved to:", shot)

    # Inspect the question/screen after click
    screen_info = client._js(r"""
        (function() {
            var inputs = Array.from(document.querySelectorAll('input, select, textarea, button')).map(i => ({
                tag: i.tagName,
                type: i.type,
                name: i.name,
                id: i.id,
                value: i.value,
                text: (i.innerText || '').slice(0, 60)
            }));

            return {
                url: window.location.href,
                title: document.title,
                bodySnippet: document.body.innerText.slice(0, 1500),
                inputs: inputs
            };
        })()
    """)

    print("SCREEN INFO:\n", json.dumps(screen_info, indent=2))
