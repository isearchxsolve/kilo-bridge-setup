"""inspect_naukri_detail.py - inspect Apply button on Naukri detail page."""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import lane_tools as T

lane = T.Lane("naukri", "detail page probe")
with T.session(lane) as client:
    url = "https://www.naukri.com/job-listings-ai-architect-tescra-bengaluru-10-to-20-years-140926007815"
    client.call_tool("browser_navigate", {"url": url})
    time.sleep(8)
    
    shot = lane.shot(client, "46-naukri-job-detail-" + time.strftime("%Y%m%d-%H%M%S"))
    page = T.read_page(client)
    res = client._js('''(() => {
        const btns = Array.from(document.querySelectorAll("button, a, input[type=submit]")).map(b => ({
            text: (b.innerText || b.value || "").trim(),
            tag: b.tagName,
            className: b.className || "",
            id: b.id || ""
        })).filter(x => /apply/i.test(x.text) && x.text.length < 30);
        return {
            title: document.title,
            buttons: btns
        };
    })()''')
    print("DETAIL PAGE RESULT:\n", res)
