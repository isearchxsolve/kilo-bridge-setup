import sys
import json
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import lane_tools as T

lane = T.Lane("timebucks", "click_login")
with T.session(lane) as client:
    print("Clicking 'Click here to login'...")
    res = client._js("""
        (function() {
            var links = Array.from(document.querySelectorAll('a, button'));
            var target = links.find(el => el.innerText && el.innerText.toLowerCase().includes('click here to login'));
            if (!target) {
                target = links.find(el => el.innerText && el.innerText.trim() === 'Login');
            }
            if (target) {
                target.click();
                return {clicked: true, text: target.innerText};
            }
            return {clicked: false};
        })()
    """)
    print("CLICK RES:", res)
    time.sleep(2)
    shot_path = lane.shot(client, "timebucks_login_modal")
    print("Screenshot saved to:", shot_path)
    page = T.read_page(client)
    print("URL:", page.get("url"))
    print("TITLE:", page.get("title"))
    print("BODY SNIPPET:\n", page.get("body", "")[:1000])
