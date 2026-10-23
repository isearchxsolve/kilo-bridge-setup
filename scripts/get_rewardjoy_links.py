r"""get_rewardjoy_links.py - Find exact URLs of RewardJoy sidebar menu.
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("coinpayu", "menu_check")
with T.session(lane) as client:
    res = client._js(r"""
        (function() {
            var allA = Array.from(document.querySelectorAll('a')).map(a => ({
                text: a.innerText.replace(/\s+/g, ' ').trim(),
                href: a.href
            })).filter(x => x.text.length > 0 && x.text.length < 30);
            return allA;
        })()
    """)
    print("ALL A LINKS:\n", json.dumps(res, indent=2))
