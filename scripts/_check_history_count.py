"""check_history_count.py - check total applied jobs count on Naukri history."""
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import lane_tools as T

lane = T.Lane("naukri", "history audit")
with T.session(lane) as client:
    client.call_tool("browser_navigate", {"url": "https://www.naukri.com/myapply/historypage"})
    time.sleep(8)
    
    shot = lane.shot(client, "99-naukri-history-final-" + time.strftime("%Y%m%d-%H%M%S"))
    page = T.read_page(client)
    res = client._js('''(() => {
        const h1 = document.querySelector("h1, [class*=heading], [class*=count]");
        const text = document.body.innerText;
        const matches = text.match(/(\\d+)\\s+Total applies/i);
        return {
            totalApplies: matches ? matches[1] : "unknown",
            firstFewJobs: Array.from(document.querySelectorAll("[class*=tuple], article, [class*=card]"))
                .slice(0, 10).map(e => e.innerText.split('\\n').slice(0, 3).join(' | '))
        };
    })()''')
    print("HISTORY AUDIT:\n", res)
