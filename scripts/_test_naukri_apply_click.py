"""test_naukri_apply_click.py - click #apply-button and handle recruiter flow."""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import lane_tools as T

lane = T.Lane("naukri", "apply search job")
with T.session(lane) as client:
    url = "https://www.naukri.com/job-listings-ai-architect-tescra-bengaluru-10-to-20-years-140926007815"
    client.call_tool("browser_navigate", {"url": url})
    time.sleep(8)
    
    # Click #apply-button
    res = client._js('''(() => {
        const btn = document.querySelector("#apply-button, button.apply-button");
        if (!btn) return "apply button not found";
        btn.click();
        return "clicked apply";
    })()''')
    print("CLICK RESULT:", res)
    time.sleep(5)
    
    shot = lane.shot(client, "47-naukri-after-apply-click-" + time.strftime("%Y%m%d-%H%M%S"))
    page = T.read_page(client)
    print("PAGE URL:", page["url"])
    print("PAGE BODY SNIPPET:", page["body"][:600])
    
    # Check if chatbot opened or success banner
    q = T.read_recruiter_question(client)
    print("RECRUITER QUESTION:", q)
