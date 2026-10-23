import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("freecash", "test_surveys_route")
with T.session(lane) as client:
    print("Navigating to https://freecash.com/en/surveys...")
    client.call_tool("browser_navigate", {"url": "https://freecash.com/en/surveys"})
    time.sleep(5)

    info = client._js(r"""
        (function() {
            return {
                url: window.location.href,
                title: document.title,
                bodySnippet: document.body.innerText.slice(0, 1500)
            };
        })()
    """)
    print("SURVEYS ROUTE RESULT:\n", json.dumps(info, indent=2))
    shot = lane.shot(client, "freecash_surveys_route")
    print("Screenshot:", shot)
