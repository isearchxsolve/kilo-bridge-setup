import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import lane_tools as T

lane = T.Lane("naukri", "test_panel_q")
with T.session(lane) as client:
    # First navigate to recommended jobs if not there
    page = T.read_page(client)
    if "naukri.com" not in page["url"]:
        client.call_tool("browser_navigate", {"url": "https://www.naukri.com/mnjuser/recommendedjobs"})
        import time; time.sleep(8)
    
    res = client._js('''(() => {
        const c = document.querySelector('.chatbot_MessageContainer');
        if (!c) return { found: false, reason: "no container" };
        
        // Find all clickable chips/buttons in container
        const chips = Array.from(c.querySelectorAll("button, [role=button], span, div, a"))
            .filter(e => {
                const t = (e.innerText || '').trim();
                return t.length > 0 && t.length < 50 && (e.onclick || e.className.includes('chip') || e.className.includes('option') || e.className.includes('pill') || e.className.includes('btn') || e.getAttribute('role') === 'button');
            })
            .map(e => (e.innerText || '').trim());
            
        return {
            found: true,
            text: c.innerText.slice(-500),
            chips: chips
        };
    })()''')
    print("RES:", res)
