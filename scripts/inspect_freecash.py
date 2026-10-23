import sys
import json
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import lane_tools as T

lane = T.Lane("freecash", "session_inspect")
with T.session(lane) as client:
    print("Navigating to Freecash...")
    client.call_tool('browser_navigate', {'url': 'https://freecash.com/earn'})
    time.sleep(4)
    shot_path = lane.shot(client, "freecash_dashboard_check")
    print("Screenshot saved to:", shot_path)
    page = T.read_page(client)
    print("URL:", page.get("url"))
    print("TITLE:", page.get("title"))
    print("BODY SNIPPET:\n", page.get("body", "")[:1000])
