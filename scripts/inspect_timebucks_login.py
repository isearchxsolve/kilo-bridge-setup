import sys
import json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import lane_tools as T

lane = T.Lane("timebucks", "login_inspect")
with T.session(lane) as client:
    print("Navigating to TimeBucks login...")
    client.call_tool('browser_navigate', {'url': 'https://timebucks.com/index.php?pg=login'})
    shot_path = lane.shot(client, "timebucks_login_page")
    print("Screenshot saved to:", shot_path)
    page = T.read_page(client)
    print("URL:", page.get("url"))
    print("TITLE:", page.get("title"))
    print("BODY:\n", page.get("body", "")[:2000])
