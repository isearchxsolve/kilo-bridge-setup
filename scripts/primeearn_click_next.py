r"""primeearn_click_next.py - Navigate, wait for React mount, find the next button, click it, and report.
"""
import json
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
    time.sleep(4)

    # Inspect current state
    state = client._js(r"""
        (function() {
            var bodyText = document.body.innerText;
            var buttons = Array.from(document.querySelectorAll('button, div, a')).filter(el => {
                var r = el.getBoundingClientRect();
                return r.width > 20 && r.height > 20;
            }).map(el => ({
                tag: el.tagName,
                className: el.className ? el.className.toString() : '',
                id: el.id || '',
                text: (el.innerText || '').trim(),
                hasSvg: !!el.querySelector('svg'),
                r: { x: Math.round(el.getBoundingClientRect().x), y: Math.round(el.getBoundingClientRect().y), w: Math.round(el.getBoundingClientRect().width), h: Math.round(el.getBoundingClientRect().height) }
            })).filter(x => x.hasSvg || x.className.includes('btn') || x.className.includes('arrow') || x.className.includes('next') || x.text.length > 0 && x.text.length < 30);

            return {
                url: window.location.href,
                title: document.title,
                bodySample: bodyText.slice(0, 500),
                buttons: buttons.slice(0, 30)
            };
        })()
    """)
    print("State:\n", json.dumps(state, indent=2))

    # Click the round arrow button
    click_res = client._js(r"""
        (function() {
            // Find svg or element containing svg
            var svgs = Array.from(document.querySelectorAll('svg'));
            for (var svg of svgs) {
                var rect = svg.getBoundingClientRect();
                if (rect.width > 10 && rect.height > 10) {
                    var parent = svg.closest('button') || svg.closest('div[role="button"]') || svg.parentElement;
                    if (parent) {
                        parent.click();
                        return { ok: true, method: 'svg_parent_click', tag: parent.tagName, class: parent.className };
                    }
                    svg.click();
                    return { ok: true, method: 'svg_click' };
                }
            }

            // Fallback: look for button
            var btn = document.querySelector('button');
            if (btn) {
                btn.click();
                return { ok: true, method: 'btn_click', text: btn.innerText };
            }

            return { ok: false, error: 'no arrow or button found' };
        })()
    """)
    print("Click result:", click_res)

    time.sleep(5)

    # Next state
    next_info = client._js(r"""
        (function() {
            return {
                url: window.location.href,
                title: document.title,
                body: document.body.innerText.slice(0, 1000)
            };
        })()
    """)
    print("Next screen:\n", json.dumps(next_info, indent=2))

    shot = lane.shot(client, "primeearn_q2_result")
    print("Screenshot:", shot)
