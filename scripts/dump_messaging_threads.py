import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import agent360_client as A

c = A.Agent360Client()

try:
    c.start()
    print("Navigating to https://www.linkedin.com/messaging/ ...")
    c.call_tool("browser_navigate", {"url": "https://www.linkedin.com/messaging/"})
    
    # Wait for conversation list to render
    for i in range(10):
        time.sleep(2)
        check_js = "document.querySelectorAll('li.msg-conversation-listitem').length"
        res = c.call_tool("browser_execute_script", {"code": check_js})
        try:
            txt = res.get("content", [{}])[0].get("text", "{}")
            cnt = json.loads(txt).get("result", 0)
            if cnt > 0:
                print(f"Found {cnt} conversation items on attempt {i+1}!")
                break
        except Exception:
            pass
            
    # Inspect all conversation items
    dump_js = """
    (() => {
        const items = Array.from(document.querySelectorAll('li.msg-conversation-listitem'));
        return items.map((li, idx) => {
            const nameEl = li.querySelector('.msg-conversation-listitem__participant-names');
            const linkEl = li.querySelector('a');
            return {
                idx: idx,
                name: nameEl ? nameEl.innerText.trim() : '',
                full_text: li.innerText.replace(/\\s+/g, ' ').slice(0, 100),
                href: linkEl ? linkEl.getAttribute('href') : null
            };
        });
    })()
    """
    res_dump = c.call_tool("browser_execute_script", {"code": dump_js})
    print("\n--- CONVERSATION LIST ITEMS ---")
    txt = res_dump.get("content", [{}])[0].get("text", "{}")
    items = json.loads(txt).get("result", [])
    for it in items:
        print(f"[{it['idx']}] Name: '{it['name']}' | Href: '{it['href']}' | Text: '{it['full_text']}'")
        
    p = HERE / "_conversation_items_dump.json"
    p.write_text(json.dumps(items, indent=2), encoding="utf-8")
    print(f"\nSaved dump to {p}")

finally:
    c.close()
