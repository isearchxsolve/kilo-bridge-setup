r"""open_freecash_tab.py - Open Freecash in a new tab so user has both RewardJoy and Freecash open.
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("timebucks", "open_freecash")
with T.session(lane) as client:
    res = client._js(r"""
        (function() {
            var w = window.open('https://freecash.com', '_blank');
            return { opened: !!w };
        })()
    """)
    print("Window open result:", res)
    time.sleep(3)
