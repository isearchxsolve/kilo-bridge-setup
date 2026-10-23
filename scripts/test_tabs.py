r"""test_tabs.py - Check tabs and navigate to questions page.
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("timebucks", "tabs_check")
with T.session(lane) as client:
    # Check what tabs exist
    try:
        tabs = client.call_tool("browser_tabs", {})
        print("browser_tabs output:", tabs)
    except Exception as e:
        print("browser_tabs error:", e)

    # Let's navigate to https://monetize.primeearn.com/questions
    client.call_tool("browser_navigate", {"url": "https://monetize.primeearn.com/questions"})
    time.sleep(3)
    info = client._js(r"({ url: window.location.href, title: document.title, body: document.body.innerText.slice(0, 500) })")
    print("Page info after navigate:", json.dumps(info, indent=2))
