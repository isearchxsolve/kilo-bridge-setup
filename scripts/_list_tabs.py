import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import lane_tools as T

lane = T.Lane("naukri", "list_tabs")
with T.session(lane) as client:
    tabs = client.list_tabs()
    for t in tabs:
        print("TAB:", t)
