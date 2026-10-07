"""test_foundit_click_apply.py - click Apply Now on Foundit and inspect result."""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import lane_tools as T

lane = T.Lane("foundit", "click apply")
with T.session(lane) as client:
    url = "https://www.foundit.in/job/artificial-intelligence-specialist-publicis-global-delivery-pgd-bengaluru-bangalore-69381649"
    client.call_tool("browser_navigate", {"url": url})
    time.sleep(8)
    res = client._js('''(() => {
        const btn = document.querySelector(".jobMainInfoCard__applyButton, button.applyJob__btn");
        if (!btn) return "apply button not found";
        btn.click();
        return "clicked " + btn.innerText;
    })()''')
    print("CLICK RESULT:", res)
    time.sleep(6)

    
    shot = lane.shot(client, "56-foundit-after-apply-click-" + time.strftime("%Y%m%d-%H%M%S"))
    page = T.read_page(client)
    print("PAGE TITLE:", page["title"])
    print("PAGE URL:", page["url"])
    print("PAGE BODY SNIPPET:", page["body"][:500])
