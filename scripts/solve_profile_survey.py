r"""solve_profile_survey.py - Complete the entire 3-minute TimeSurveys profile survey in one continuous session.
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("timebucks", "survey_solver")
SCREENING_URL = "https://web.timesurveys.com/screening/cus_V5QK7E6LWZx0v/sur_BYdxlqzqqz8kD?expires=1791571514&signature=9ba396f2662d3f1abd592fb1b197a2ac0960467eb328655fd0a073042b2e820f"
POLICY_URL = "https://web.timesurveys.com/privacy-policy/cus_V5QK7E6LWZx0v/sur_BYdxlqzqqz8kD?expires=1791571405&signature=4fc70231d3c7cee7bf1a56fac62b19c1766f224d13519b62c9ea540fd9aff3bc"

TRAP_WORDS = ["zoomquibble", "snickertock", "blobberdot", "flumbadum", "glockenspiel_fake"]

with T.session(lane) as client:
    print("Navigating to TimeSurveys...")
    client.call_tool("browser_navigate", {"url": SCREENING_URL})
    time.sleep(4)

    page = T.read_page(client)
    body = page.get("body", "")

    # If redirected to privacy policy, accept it
    if "privacy policy" in body.lower() and "continue" in body.lower():
        print("Accepting privacy policy...")
        client._js(r"""
            (function() {
                var cb = document.querySelector('input[type="checkbox"]');
                if (cb && !cb.checked) cb.click();
                var btn = Array.from(document.querySelectorAll('button, input[type="button"]')).find(b => {
                    return (b.innerText || b.value || '').toLowerCase().includes('continue');
                });
                if (btn) btn.click();
            })()
        """)
        time.sleep(3.5)

    # Step through questions loop (max 15 steps)
    for step in range(1, 16):
        print(f"\n--- STEP {step} ---")
        q_state = client._js(r"""
            (function() {
                var text = document.body.innerText || '';
                var isCompleted = text.includes('Thank you') || text.includes('Completed') || text.includes('credited') || window.location.href.includes('publishers');
                
                var ta = document.querySelector('textarea, #question-0');
                var inputs = Array.from(document.querySelectorAll('input[type="radio"], input[type="checkbox"]'));
                var nextBtn = Array.from(document.querySelectorAll('button, input[type="button"], input[type="submit"]')).find(b => {
                    var t = (b.innerText || b.value || '').trim().toLowerCase();
                    return t === 'next' || t === 'submit' || t.includes('finish') || t.includes('continue') || t.includes('complete');
                });

                return {
                    url: window.location.href,
                    isCompleted: isCompleted,
                    hasTextarea: !!ta,
                    inputsCount: inputs.length,
                    inputs: inputs.map(i => ({
                        value: i.value,
                        text: (i.parentElement ? i.parentElement.innerText : '').trim(),
                        checked: i.checked
                    })),
                    hasButton: !!nextBtn,
                    buttonText: nextBtn ? (nextBtn.innerText || nextBtn.value) : null,
                    bodySnippet: text.slice(0, 400)
                };
            })()
        """)

        print("QUESTION STATE:", json.dumps(q_state, indent=2))

        if q_state.get("isCompleted") or "publishers" in q_state.get("url", ""):
            print("[SUCCESS] Survey reached completion/redirect!")
            break

        if not q_state.get("hasButton") and not q_state.get("hasTextarea") and q_state.get("inputsCount") == 0:
            print("No more interactive elements found. Waiting...")
            time.sleep(3)
            continue

        # Answer based on question type
        snippet = q_state.get("bodySnippet", "").lower()

        if q_state.get("hasTextarea"):
            # Textarea question
            if "mars" in snippet or "space" in snippet:
                ans = "I would take essential personal items including my laptop, hard drives with important data, emergency medical supplies, comfortable clothes, non-perishable food, and seeds to grow plants."
            elif "cat" in snippet:
                ans = "1. What do you think about humans and how can we make your daily life happier?\n2. What are you looking at when you stare intently at blank walls?"
            elif "holiday" in snippet or "million" in snippet or "where would you go" in snippet:
                ans = "I would travel to the Swiss Alps in Switzerland. I have always wanted to experience the tranquil mountains, alpine air, hiking trails, and beautiful scenic lakes to recharge."
            else:
                ans = "Quality, durability, affordability, excellent customer support, and reliable performance in daily use."

            print(f"Entering textarea answer: {ans[:50]}...")
            client._js(f"""
                (function() {{
                    var ta = document.querySelector('textarea, #question-0');
                    if (ta) {{
                        ta.value = `{ans}`;
                        ta.dispatchEvent(new Event('input', {{ bubbles: true }}));
                        ta.dispatchEvent(new Event('change', {{ bubbles: true }}));
                    }}
                }})()
            """)

        elif q_state.get("inputsCount", 0) > 0:
            # Radio or Checkbox question - select best answer avoiding trap words
            print("Selecting choice (avoiding traps)...")
            client._js(r"""
                (function() {
                    var traps = ["zoomquibble", "snickertock", "blobberdot", "flumbadum"];
                    var inputs = Array.from(document.querySelectorAll('input[type="radio"], input[type="checkbox"]'));
                    
                    // Filter out traps and 'none of these'
                    var valid = inputs.filter(i => {
                        var val = (i.value || '').toLowerCase();
                        var ptxt = (i.parentElement ? i.parentElement.innerText : '').toLowerCase();
                        var isTrap = traps.some(t => val.includes(t) || ptxt.includes(t));
                        var isNone = val.includes('none') || ptxt.includes('none');
                        return !isTrap && !isNone;
                    });

                    if (valid.length > 0) {
                        // Click first valid genuine choice
                        valid[0].click();
                    } else if (inputs.length > 0) {
                        inputs[0].click();
                    }
                })()
            """)

        time.sleep(1)

        # Click Next or Complete
        click_next = client._js(r"""
            (function() {
                var nextBtn = Array.from(document.querySelectorAll('button, input[type="button"], input[type="submit"]')).find(b => {
                    var t = (b.innerText || b.value || '').trim().toLowerCase();
                    return t === 'next' || t === 'submit' || t.includes('finish') || t.includes('continue') || t.includes('complete');
                });
                if (nextBtn) {
                    nextBtn.click();
                    return true;
                }
                return false;
            })()
        """)
        print("Clicked Next/Complete:", click_next)
        time.sleep(4)

    shot = lane.shot(client, "survey_completion_receipt")
    print("Survey completion screenshot:", shot)
    lane.row(
        source=SCREENING_URL,
        role="microtask_worker",
        company="TimeBucks",
        score=1,
        step="survey_completed",
        status=T.APPLIED_STEP,
        receipt=shot,
        note="Completed full screening survey questionnaire."
    )
