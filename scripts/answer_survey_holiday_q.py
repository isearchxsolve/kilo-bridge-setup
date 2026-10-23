r"""answer_survey_holiday_q.py - Select 'New Year' for favorite holiday and click Next.
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("timebucks", "survey_holiday")
with T.session(lane) as client:
    screening_url = "https://web.timesurveys.com/screening/cus_V5QK7E6LWZx0v/sur_BYdxlqzqqz8kD?expires=1791571514&signature=9ba396f2662d3f1abd592fb1b197a2ac0960467eb328655fd0a073042b2e820f"
    client.call_tool("browser_navigate", {"url": screening_url})
    time.sleep(3.5)
    ans_res = client._js(r"""
        (function() {
            var radios = Array.from(document.querySelectorAll('input[type="radio"], input[type="checkbox"]'));
            var target = radios.find(r => (r.value || '').toLowerCase() === 'new year' || (r.parentElement && (r.parentElement.innerText || '').toLowerCase().includes('new year')));
            
            if (target) {
                target.click();
            }

            var nextBtn = Array.from(document.querySelectorAll('button, input[type="button"]')).find(b => {
                var t = (b.innerText || b.value || '').trim().toLowerCase();
                return t === 'next' || t.includes('next');
            });

            var clicked = false;
            if (nextBtn) {
                nextBtn.click();
                clicked = true;
            }

            return {
                selectedNewYear: target ? target.checked : false,
                clickedNext: clicked
            };
        })()
    """)

    print("HOLIDAY SUBMIT RESULT:", json.dumps(ans_res, indent=2))
    time.sleep(4)

    shot = lane.shot(client, "survey_question_after_holiday")
    print("Screenshot saved to:", shot)

    next_screen = client._js(r"""
        (function() {
            var inputs = Array.from(document.querySelectorAll('input, select, textarea, button')).map(i => ({
                tag: i.tagName,
                type: i.type,
                name: i.name,
                id: i.id,
                value: i.value,
                text: (i.innerText || '').trim().slice(0, 80)
            }));

            return {
                url: window.location.href,
                title: document.title,
                bodySnippet: document.body.innerText.slice(0, 1500),
                inputs: inputs
            };
        })()
    """)

    print("NEXT SCREEN INFO:\n", json.dumps(next_screen, indent=2))
