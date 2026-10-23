r"""inspect_turnstile.py - Inspect Turnstile state and render target.
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("timebucks", "turnstile_check")
with T.session(lane) as client:
    ts_info = client._js(r"""
        (function() {
            return {
                hasTurnstile: typeof window.turnstile !== 'undefined',
                callbackFn: typeof window.onloadTurnstileCallback !== 'undefined' ? String(window.onloadTurnstileCallback) : null,
                turnstileKeys: typeof window.turnstile !== 'undefined' ? Object.keys(window.turnstile) : []
            };
        })()
    """)
    print("TURNSTILE INFO:\n", json.dumps(ts_info, indent=2))
