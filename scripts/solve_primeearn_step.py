r"""solve_primeearn_step.py - Inspect current PrimeEarn question, select best response, click next, and record receipt.
"""
import json
import re
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("timebucks", "primeearn_survey")
with T.session(lane) as client:
    print("Navigating to https://monetize.primeearn.com/questions...")
    client.call_tool("browser_navigate", {"url": "https://monetize.primeearn.com/questions"})
    time.sleep(3)

    # 1. Inspect current question and options
    q_data = client._js(r"""
        (function() {
            var bodyText = document.body.innerText;
            var h1_h3 = Array.from(document.querySelectorAll('h1, h2, h3, h4, .question-title, .title')).map(h => (h.innerText || '').trim()).filter(t => t.length > 0);
            
            var options = Array.from(document.querySelectorAll('.p-checkbox-wrapper, .p-radio-wrapper, label, li, .answer-item')).map(el => {
                var text = (el.innerText || '').trim();
                return {
                    tag: el.tagName,
                    className: el.className ? el.className.toString() : '',
                    text: text
                };
            }).filter(o => o.text.length > 0 && o.text.length < 150);

            var inputs = Array.from(document.querySelectorAll('input, select, textarea')).map(el => ({
                tag: el.tagName,
                type: el.type || '',
                id: el.id || '',
                name: el.name || '',
                placeholder: el.placeholder || '',
                value: el.value || ''
            }));

            return {
                url: window.location.href,
                title: document.title,
                headings: h1_h3,
                options: options,
                inputs: inputs,
                bodyText: bodyText.slice(0, 1000)
            };
        })()
    """)
    print("CURRENT QUESTION DATA:\n", json.dumps(q_data, indent=2))

    headings = " ".join(q_data.get("headings", [])) + " " + q_data.get("bodyText", "")
    headings_lower = headings.lower()
    options = q_data.get("options", [])

    target_choice = None

    if "smartphone" in headings_lower or "phone" in headings_lower:
        target_choice = "Android"
    elif "gender" in headings_lower or "sex" in headings_lower:
        target_choice = "Male"
    elif "employment" in headings_lower or "work" in headings_lower or "status" in headings_lower:
        target_choice = "Employed full-time"
    elif "industry" in headings_lower or "field" in headings_lower:
        target_choice = "Information Technology"
    elif "education" in headings_lower or "degree" in headings_lower:
        target_choice = "Bachelor"
    elif "state" in headings_lower or "region" in headings_lower:
        target_choice = "West Bengal"
    elif "zip" in headings_lower or "postal" in headings_lower or "pin" in headings_lower:
        target_choice = "700075"

    print("Target choice identified:", target_choice)

    # Click the option
    if target_choice:
        click_opt = client._js(r"""
            (function(targetText) {
                var items = Array.from(document.querySelectorAll('.p-checkbox-wrapper, .p-radio-wrapper, label, div, span')).filter(el => {
                    var t = (el.innerText || '').trim();
                    return t.toLowerCase() === targetText.toLowerCase() || (t.toLowerCase().includes(targetText.toLowerCase()) && t.length < 80);
                });
                if (items.length > 0) {
                    items[0].click();
                    return { ok: true, clicked: items[0].innerText.trim(), class: items[0].className };
                }
                return { ok: false, error: 'target text not found: ' + targetText };
            })(%s)
        """ % json.dumps(target_choice))
        print("Click option result:", click_opt)
        time.sleep(1.5)

    # Click next button
    next_click = client._js(r"""
        (function() {
            var btn = document.querySelector('button.p-btn--icon-only, .next-button button, button.p-btn--primary');
            if (btn) {
                btn.click();
                return { ok: true, class: btn.className };
            }
            return { ok: false, error: 'Next button not found' };
        })()
    """)
    print("Next click result:", next_click)

    time.sleep(5)

    # Inspect resulting screen
    new_info = client._js(r"""
        (function() {
            return {
                url: window.location.href,
                title: document.title,
                body: document.body.innerText.slice(0, 1000)
            };
        })()
    """)
    print("RESULTING SCREEN:\n", json.dumps(new_info, indent=2))

    shot = lane.shot(client, "primeearn_survey_progress")
    print("Screenshot:", shot)
