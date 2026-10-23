r"""inspect_show_profile_fn.py - Inspect window.showProfile implementation.
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("timebucks", "fn_inspect")
with T.session(lane) as client:
    fn_code = client._js(r"""
        (function() {
            return {
                showProfile: window.showProfile ? window.showProfile.toString() : null,
                ajaxSubmit: window.ajaxSubmit ? window.ajaxSubmit.toString() : null
            };
        })()
    """)
    print("FUNCTIONS:\n", json.dumps(fn_code, indent=2))
