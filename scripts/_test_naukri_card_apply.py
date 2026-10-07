"""test_naukri_card_apply.py - inspect apply flow for search cards."""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import lane_tools as T

lane = T.Lane("naukri", "search card apply probe")
with T.session(lane) as client:
    url = "https://www.naukri.com/generative+ai+architect-jobs"
    client.call_tool("browser_navigate", {"url": url})
    time.sleep(8)
    
    res = client._js('''(() => {
        const tuples = Array.from(document.querySelectorAll("[class*=job-tuple], [class*=srp-job]")).slice(0, 10);
        return tuples.map(t => {
            const titleA = t.querySelector("a.title, a[class*=title]");
            const applyBtn = t.querySelector("button, [class*=apply]");
            const saveBtn = t.querySelector("[class*=save]");
            return {
                title: titleA ? titleA.innerText.trim() : "",
                href: titleA ? titleA.href : "",
                applyText: applyBtn ? applyBtn.innerText.trim() : "",
                saveText: saveBtn ? saveBtn.innerText.trim() : ""
            };
        }).filter(x => x.title);
    })()''')
    print("SEARCH TUPLES:\n", res)
