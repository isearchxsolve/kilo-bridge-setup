import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

survey_url = "https://web.timesurveys.com/screening/cus_V5QK7E6LWZx0v/sur_rZyoKJGPpO86J?expires=1791577301&signature=f64b4be21874265403103c8dc413369511bbd4cd9ff13aa3d3f2c211d15288f2"

lane = T.Lane("timebucks", "answer_attention_check")
with T.session(lane) as client:
    print("Navigating to survey URL...")
    client.call_tool("browser_navigate", {"url": survey_url})
    time.sleep(3.5)

    # 1. Click the radio button / container for "disqualified or banned"
    click_res = client._js(r"""
        (function() {
            var all = Array.from(document.querySelectorAll('*'));
            var target = all.find(el => el.children.length === 0 && (el.innerText || '').includes('disqualified or banned'));
            if (!target) {
                target = all.find(el => (el.innerText || '').includes('disqualified or banned'));
            }
            if (target) {
                var clickable = target.closest('div[class*="option"], div[class*="radio"], label') || target.parentElement || target;
                clickable.click();
                return { ok: true, clickedText: target.innerText.trim(), tag: clickable.tagName };
            }
            return { ok: false, error: 'Target option not found' };
        })()
    """)
    print("OPTION CLICK RESULT:", json.dumps(click_res, indent=2))
    time.sleep(1)

    # 2. Click Next button
    next_res = client._js(r"""
        (function() {
            var btn = Array.from(document.querySelectorAll('button, [role="button"]')).find(b => (b.innerText || '').trim().toLowerCase() === 'next');
            if (btn) {
                btn.click();
                return { ok: true, clicked: btn.innerText.trim() };
            }
            return { ok: false, error: 'Next button not found' };
        })()
    """)
    print("NEXT CLICK RESULT:", json.dumps(next_res, indent=2))
    time.sleep(5)

    # 3. Read subsequent screen
    next_screen = client._js(r"""
        (function() {
            var inputs = Array.from(document.querySelectorAll('input, select, textarea, button')).map(el => ({
                tag: el.tagName,
                type: el.type || '',
                id: el.id || '',
                name: el.name || '',
                val: (el.value || el.innerText || '').trim()
            })).filter(x => x.val.length > 0 && x.val.length < 80);

            return {
                url: window.location.href,
                title: document.title,
                inputs: inputs.slice(0, 20),
                bodySample: document.body.innerText.slice(0, 1500)
            };
        })()
    """)
    print("NEXT SCREEN STATE:\n", json.dumps(next_screen, indent=2))

    shot = lane.shot(client, "timebucks_primesurvey_step_2")
    print("Screenshot saved to:", shot)
