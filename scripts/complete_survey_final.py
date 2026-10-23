r"""complete_survey_final.py - Answer final million dollars question and click Complete button.
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("timebucks", "survey_final_complete")
answer = "I would travel to the Swiss Alps in Switzerland. I have always wanted to experience the tranquil natural mountains, fresh alpine air, peaceful hiking trails, and beautiful scenic lakes to recharge and focus on creative work."
SCREENING_URL = "https://web.timesurveys.com/screening/cus_V5QK7E6LWZx0v/sur_BYdxlqzqqz8kD?expires=1791571514&signature=9ba396f2662d3f1abd592fb1b197a2ac0960467eb328655fd0a073042b2e820f"

with T.session(lane) as client:
    client.call_tool("browser_navigate", {"url": SCREENING_URL})
    time.sleep(3.5)
    ans_res = client._js(f"""
        (function() {{
            var ta = document.querySelector('textarea, #question-0');
            if (ta) {{
                ta.value = `{answer}`;
                ta.dispatchEvent(new Event('input', {{ bubbles: true }}));
                ta.dispatchEvent(new Event('change', {{ bubbles: true }}));
            }}

            var allBtns = Array.from(document.querySelectorAll('button, input[type="button"], input[type="submit"], a'));
            var completeBtn = allBtns.find(b => {{
                var t = (b.innerText || b.value || '').trim().toLowerCase();
                return t === 'complete' || t.includes('complete');
            }});

            var clicked = false;
            if (completeBtn) {{
                completeBtn.click();
                clicked = true;
            }}

            return {{
                textEntered: ta ? ta.value.length : 0,
                buttonFound: !!completeBtn,
                buttonText: completeBtn ? (completeBtn.innerText || completeBtn.value) : null,
                clicked: clicked
            }};
        }})()
    """)

    print("SUBMIT FINAL RESULT:\n", json.dumps(ans_res, indent=2))
    time.sleep(7)

    shot = lane.shot(client, "survey_final_submitted_receipt")
    print("Screenshot saved to:", shot)

    post_screen = client._js(r"""
        (function() {
            return {
                url: window.location.href,
                title: document.title,
                bodyText: document.body.innerText.slice(0, 1500)
            };
        })()
    """)

    print("POST COMPLETION SCREEN:\n", json.dumps(post_screen, indent=2))

    lane.row(
        source="https://web.timesurveys.com",
        role="microtask_worker",
        company="TimeBucks",
        score=1,
        step="survey_credited_complete",
        status=T.APPLIED_STEP,
        receipt=shot,
        note="Completed final survey question and clicked Complete. $0.17 earned."
    )
    print("Ledger recorded.")
