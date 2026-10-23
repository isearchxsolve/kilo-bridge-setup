import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("coinpayu", "inspect_surf_js")
with T.session(lane) as client:
    client.call_tool("browser_navigate", {"url": "https://www.rewardjoy.com/dashboard/ads_surf"})
    time.sleep(3)

    info = client._js(r"""
        (function() {
            // Find script sources
            var scripts = Array.from(document.querySelectorAll('script')).map(s => s.src).filter(Boolean);

            // Find global functions or objects
            var globals = Object.keys(window).filter(k => (
                k.includes('surf') || k.includes('ad') || k.includes('timer') || k.includes('count') || k.includes('ags')
            ));

            // Check if there is an onclick handler on any parent or child
            var desc = document.querySelector('.ags-description');
            var onclickDesc = desc ? desc.onclick : null;
            var box = desc ? desc.closest('.frameless-ad-box') : null;
            var onclickBox = box ? box.onclick : null;

            return {
                scripts: scripts,
                globals: globals,
                hasOnclickDesc: !!onclickDesc,
                hasOnclickBox: !!onclickBox,
                descEvents: window.getEventListeners ? Object.keys(window.getEventListeners(desc)) : 'no getEventListeners'
            };
        })()
    """)
    print("SURF JS INSPECTION:\n", json.dumps(info, indent=2))
