"""test_foundit_apply.py - inspect Foundit job application controls."""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import lane_tools as T

lane = T.Lane("foundit", "apply probe")
with T.session(lane) as client:
    url = "https://www.foundit.in/search/artificial-intelligence-jobs?query=artificial%20intelligence&queryDerived=true"
    client.call_tool("browser_navigate", {"url": url})
    time.sleep(8)
    
    # Read cards and their apply buttons / links
    res = client._js('''(() => {
        const cards = Array.from(document.querySelectorAll("[class*=jobCard], article, [data-job-id]")).slice(0, 10);
        return cards.map(c => {
            const titleEl = c.querySelector("h3, [class*=title], a[href*='job']");
            const applyBtn = c.querySelector("button, [class*=apply], a[class*=apply]");
            return {
                title: titleEl ? titleEl.innerText.trim() : "",
                href: titleEl && titleEl.href ? titleEl.href : "",
                applyText: applyBtn ? applyBtn.innerText.trim() : "",
                applyTag: applyBtn ? applyBtn.tagName : "",
                applyClass: applyBtn ? applyBtn.className : ""
            };
        }).filter(x => x.title);
    })()''')
    print("FOUNDIT CARDS:", res)
