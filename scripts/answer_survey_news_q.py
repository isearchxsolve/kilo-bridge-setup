r"""answer_survey_news_q.py - Select 'BBC' and 'Reuters', avoid Snickertock, click Next.
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("timebucks", "survey_news")
with T.session(lane) as client:
    screening_url = "https://web.timesurveys.com/screening/cus_V5QK7E6LWZx0v/sur_BYdxlqzqqz8kD?expires=1791571514&signature=9ba396f2662d3f1abd592fb1b197a2ac0960467eb328655fd0a073042b2e820f"
    client.call_tool("browser_navigate", {"url": screening_url})
    time.sleep(3.5)

    ans_res = client._js(r"""
        (function() {
            var cbs = Array.from(document.querySelectorAll('input[type="checkbox"]'));
            var bbc = cbs.find(c => (c.value || '').toUpperCase() === 'BBC' || (c.parentElement && (c.parentElement.innerText || '').includes('BBC')));
            var reuters = cbs.find(c => (c.value || '').toUpperCase() === 'REUTERS' || (c.parentElement && (c.parentElement.innerText || '').includes('Reuters')));

            if (bbc && !bbc.checked) bbc.click();
            if (reuters && !reuters.checked) reuters.click();

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
                bbcSelected: bbc ? bbc.checked : false,
                reutersSelected: reuters ? reuters.checked : false,
                clickedNext: clicked
            };
        })()
    """)

    print("NEWS SUBMIT RESULT:", json.dumps(ans_res, indent=2))
    time.sleep(4)

    shot = lane.shot(client, "survey_question_after_news")
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
