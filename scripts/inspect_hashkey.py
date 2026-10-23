import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("freecash", "inspect_hashkey")
with T.session(lane) as client:
    info = client._js(r"""
        (function() {
            var cards = Array.from(document.querySelectorAll('*')).filter(el => (el.innerText || '').includes('HashKey Exchange'));
            var target = cards[0];
            var cardBox = target ? (target.closest('a') || target.closest('div[role="button"]') || target.closest('[class*="card"]') || target.parentElement) : null;

            return {
                text: cardBox ? cardBox.innerText.replace(/\n+/g, ' | ') : null,
                tag: cardBox ? cardBox.tagName : null,
                href: cardBox ? cardBox.getAttribute('href') : null,
                className: cardBox ? cardBox.className : null
            };
        })()
    """)
    print("HASHKEY OFFER:\n", json.dumps(info, indent=2))
