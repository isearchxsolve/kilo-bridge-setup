import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("freecash", "inspect_card_ancestors")
with T.session(lane) as client:
    info = client._js(r"""
        (function() {
            var span = Array.from(document.querySelectorAll('span')).find(s => (s.innerText || '').trim() === 'CPX Research');
            if (!span) return { error: 'CPX Research span not found' };

            var ancestors = [];
            var cur = span;
            while (cur && cur !== document.body) {
                ancestors.push({
                    tag: cur.tagName,
                    className: cur.className,
                    role: cur.getAttribute('role'),
                    tabIndex: cur.tabIndex,
                    dataset: Object.keys(cur.dataset)
                });
                cur = cur.parentElement;
            }

            return {
                ancestors: ancestors.slice(0, 8)
            };
        })()
    """)
    print("CPX CARD ANCESTORS:\n", json.dumps(info, indent=2))
