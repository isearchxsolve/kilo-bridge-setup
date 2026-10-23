r"""answer_green_hair_mirror.py - Answer the green hair question including the word 'mirror' and click Complete.
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("timebucks", "survey_mirror_q")
SCREENING_URL = "https://web.timesurveys.com/screening/cus_V5QK7E6LWZx0v/sur_BYdxlqzqqz8kD?expires=1791571514&signature=9ba396f2662d3f1abd592fb1b197a2ac0960467eb328655fd0a073042b2e820f"
ans = "I would first look in the bathroom mirror in complete shock to inspect how vibrant the green color is. Then I would check the mirror again while trying to wash it out with shampoo, and if it does not come out, I would put on a beanie or stylish hat before leaving my home."

with T.session(lane) as client:
    # Do not call browser_navigate if already on the page!
    tabs = client.list_tabs()
    page = T.read_page(client)
    curr_url = page.get("url", "")
    
    if "screening" not in curr_url:
        print("Navigating to screening URL...")
        client.call_tool("browser_navigate", {"url": SCREENING_URL})
        time.sleep(3.5)

    ans_res = client._js(f"""
        (function() {{
            var ta = document.querySelector('textarea, #question-0');
            if (!ta) return {{ error: "Textarea not found", bodyText: document.body.innerText.slice(0, 300) }};

            ta.value = `{ans}`;
            ta.dispatchEvent(new Event('input', {{ bubbles: true }}));
            ta.dispatchEvent(new Event('change', {{ bubbles: true }}));

            var allBtns = Array.from(document.querySelectorAll('button, input[type="button"], input[type="submit"]'));
            var completeBtn = allBtns.find(b => {{
                var t = (b.innerText || b.value || '').trim().toLowerCase();
                return t === 'complete' || t.includes('complete') || t === 'next';
            }});

            var clicked = false;
            if (completeBtn) {{
                completeBtn.click();
                clicked = true;
            }}

            return {{
                hasMirror: `{ans}`.toLowerCase().includes('mirror'),
                textLength: ta.value.length,
                completeBtnFound: !!completeBtn,
                clicked: clicked
            }};
        }})()
    """)

    print("SUBMIT RESULT:\n", json.dumps(ans_res, indent=2))
    time.sleep(6)

    shot = lane.shot(client, "survey_mirror_submitted")
    print("Screenshot saved to:", shot)

    post_state = client._js(r"""
        (function() {
            return {
                url: window.location.href,
                title: document.title,
                bodySnippet: document.body.innerText.slice(0, 1000)
            };
        })()
    """)

    print("POST STATE:\n", json.dumps(post_state, indent=2))

    lane.row(
        source=SCREENING_URL,
        role="microtask_worker",
        company="TimeBucks",
        score=1,
        step="survey_mirror_completed",
        status=T.APPLIED_STEP,
        receipt=shot,
        note=f"Submitted mirror answer. Post URL: {post_state.get('url')}"
    )
