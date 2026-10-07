"""test_foundit_detail.py - inspect Foundit job detail page and Apply button."""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import lane_tools as T

lane = T.Lane("foundit", "job detail probe")
with T.session(lane) as client:
    url = "https://www.foundit.in/job/artificial-intelligence-specialist-publicis-global-delivery-pgd-bengaluru-bangalore-69381649"
    client.call_tool("browser_navigate", {"url": url})
    time.sleep(8)
    
    shot = lane.shot(client, "55-foundit-job-detail-" + time.strftime("%Y%m%d-%H%M%S"))
    res = client._js('''(() => {
        const btns = Array.from(document.querySelectorAll("button, a")).map(b => ({
            text: (b.innerText || "").trim(),
            tag: b.tagName,
            href: b.href || "",
            className: b.className || ""
        })).filter(x => /apply/i.test(x.text));
        return {
            title: document.title,
            applyButtons: btns
        };
    })()''')
    print("DETAIL:", res)
