r"""inspect_and_next_primeearn.py - Check arrow button on PrimeEarn questions and proceed.
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
    # Find the next arrow button
    res = client._js(r"""
        (function() {
            var clickable = Array.from(document.querySelectorAll('*')).filter(el => {
                var style = window.getComputedStyle(el);
                var rect = el.getBoundingClientRect();
                return (rect.width > 20 && rect.height > 20 && (
                    style.cursor === 'pointer' ||
                    el.tagName === 'BUTTON' ||
                    el.tagName === 'A' ||
                    el.getAttribute('role') === 'button' ||
                    el.className.toString().includes('next') ||
                    el.className.toString().includes('arrow') ||
                    el.className.toString().includes('btn') ||
                    el.className.toString().includes('circle')
                ));
            }).map(el => ({
                tag: el.tagName,
                className: el.className ? el.className.toString() : '',
                id: el.id || '',
                text: (el.innerText || '').trim(),
                rect: {
                    x: el.getBoundingClientRect().x,
                    y: el.getBoundingClientRect().y,
                    w: el.getBoundingClientRect().width,
                    h: el.getBoundingClientRect().height
                }
            }));

            return {
                url: window.location.href,
                clickables: clickable
            };
        })()
    """)
    print("Found clickables:\n", json.dumps(res, indent=2))

    # Click the round arrow button (likely a svg / button / div with blue background or arrow)
    click_res = client._js(r"""
        (function() {
            // Check for svg or button near bottom center
            var candidates = Array.from(document.querySelectorAll('button, div, a, span, svg')).filter(el => {
                var rect = el.getBoundingClientRect();
                var style = window.getComputedStyle(el);
                // The blue circle button in screenshot is roughly in bottom center
                return rect.width >= 35 && rect.width <= 80 && rect.height >= 35 && rect.height <= 80 && (
                    style.borderRadius.includes('50%') ||
                    style.borderRadius.includes('999') ||
                    style.backgroundColor.includes('rgb(41') || // blue
                    style.backgroundColor.includes('blue') ||
                    style.cursor === 'pointer' ||
                    el.querySelector('svg') ||
                    el.tagName === 'svg'
                );
            });

            if (candidates.length > 0) {
                // Find candidate closest to bottom center
                var target = candidates[candidates.length - 1];
                target.click();
                return { ok: true, clicked: target.tagName, className: target.className ? target.className.toString() : '' };
            }

            // Fallback: search by svg path
            var svg = document.querySelector('svg');
            if (svg && svg.parentElement) {
                svg.parentElement.click();
                return { ok: true, clicked: 'svg.parentElement' };
            }

            return { ok: false, error: 'arrow button not found' };
        })()
    """)
    print("Click result:", click_res)

    time.sleep(5)

    # Next state inspection
    next_state = client._js(r"""
        (function() {
            return {
                url: window.location.href,
                title: document.title,
                body: document.body.innerText.slice(0, 1500)
            };
        })()
    """)
    print("Next state:\n", json.dumps(next_state, indent=2))

    shot = lane.shot(client, "primeearn_question_2")
    print("Shot:", shot)
