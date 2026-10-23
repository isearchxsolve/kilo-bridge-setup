r"""inspect_captcha_container.py - Inspect elements under Captcha Required.
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("timebucks", "captcha_container")
with T.session(lane) as client:
    info = client._js(r"""
        (function() {
            var iframes = Array.from(document.querySelectorAll('iframe')).map(f => ({
                src: f.src,
                id: f.id,
                className: f.className,
                style: f.getAttribute('style')
            }));

            var captchaElements = Array.from(document.querySelectorAll('[class*="captcha"], [id*="captcha"], [class*="cf-"], [id*="cf-"]')).map(e => ({
                tag: e.tagName,
                id: e.id,
                className: e.className,
                innerHTML: e.innerHTML.slice(0, 150)
            }));

            // Check if there's any container with text 'confirm you are not a robot'
            var allDivs = Array.from(document.querySelectorAll('div, p, form'));
            var target = allDivs.find(d => (d.innerText || '').includes('Please confirm you are not a robot'));

            return {
                iframes: iframes,
                captchaElements: captchaElements,
                targetParentHTML: target ? target.parentElement.innerHTML.slice(0, 600) : null
            };
        })()
    """)
    print("CAPTCHA CONTAINER DETAILS:\n", json.dumps(info, indent=2))
