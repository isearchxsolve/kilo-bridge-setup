r"""inspect_slideshows_tab.py - Check Slideshows tab on TimeBucks.
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("timebucks", "slideshows")
with T.session(lane) as client:
    url = "https://timebucks.com/publishers/index.php?pg=earn&tab=slideshows"
    print("Navigating to Slideshows:", url)
    client.call_tool("browser_navigate", {"url": url})
    time.sleep(3.5)

    shot = lane.shot(client, "timebucks_slideshows_view")
    print("Screenshot saved to:", shot)

    page = T.read_page(client)
    body = page.get("body", "")
    print("SLIDESHOWS BODY SNIPPET:\n", body[400:1500])
