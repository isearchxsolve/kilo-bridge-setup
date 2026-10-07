import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import lane_tools as T

lane = T.Lane("naukri", "inspect_options")
with T.session(lane) as client:
    tabs = client.list_tabs()
    n_tab = next((t for t in tabs if "naukri.com" in str(t.get("url", ""))), None)
    if n_tab and n_tab.get("id"):
        client.switch_tab(n_tab["id"])
    import time; time.sleep(1)
    res = client._js('''(() => {
        const c = document.querySelector('.chatbot_MessageContainer');
        if (!c) return "no chatbot; url=" + location.href;
        const all = Array.from(c.querySelectorAll('*'));
        const hits = all.filter(e => e.innerText && e.innerText.trim() === 'Kolkata');
        return hits.map(h => ({
            tag: h.tagName,
            className: h.className,
            outerHTML: h.outerHTML.slice(0, 300),
            parentTag: h.parentElement ? h.parentElement.tagName : 'none',
            parentClass: h.parentElement ? h.parentElement.className : 'none'
        }));
    })()''')
    print("KOLKATA HITS:\n", res)

