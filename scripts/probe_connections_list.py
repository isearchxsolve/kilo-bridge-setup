import sys, json, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import lane_tools as T

lane = T.Lane("linkedin", "scan_connections")
with T.session(lane) as c:
    lane.log("Navigating to LinkedIn Connections...")
    c.call_tool("browser_navigate", {"url": "https://www.linkedin.com/mynetwork/invite-connect/connections/"})
    time.sleep(5)
    
    entries = c._js("""
    (() => {
        const items = [];
        // Each connection card
        const links = Array.from(document.querySelectorAll('a[href*="/in/"]'));
        links.forEach(a => {
            const name = a.innerText.trim();
            if (name && name.length > 2 && !items.some(x => x.name === name)) {
                let card = a.closest('li') || a.parentElement;
                while (card && card.tagName !== 'LI' && card !== document.body) {
                    card = card.parentElement;
                }
                const text = card ? card.innerText.trim().replace(/\\n+/g, ' | ') : '';
                const msgBtn = card ? card.querySelector('button, a[href*="/messaging/compose/"]') : null;
                const msgHref = msgBtn && msgBtn.tagName === 'A' ? msgBtn.href : '';
                items.push({
                    name: name,
                    profile_url: a.href,
                    card_text: text,
                    msg_href: msgHref
                });
            }
        });
        return items;
    })()
    """)
    
    lane.log(f"Found {len(entries) if isinstance(entries, list) else 0} connections:")
    if isinstance(entries, list):
        for idx, item in enumerate(entries[:8], 1):
            lane.log(f"[{idx}] {item['name']}")
            lane.log(f"    Snippet: {item['card_text'][:120]}")
            lane.log(f"    Profile: {item['profile_url']}")
            lane.log(f"    MsgHref: {item['msg_href']}")
