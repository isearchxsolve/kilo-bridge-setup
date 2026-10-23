import json
import sys
import time
import base64
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import agent360_client as A

EVIDENCE = HERE.parent / "evidence" / "employment-lane"

c = A.Agent360Client()
out = {}

try:
    c.start()
    
    # 1. Ensure we are on messaging
    print("Navigating to messaging...")
    c.call_tool("browser_navigate", {"url": "https://www.linkedin.com/messaging/"})
    time.sleep(5)
    
    # 2. Extract all conversation cards with all their links and snippets
    dump_js = """
    (() => {
        const items = document.querySelectorAll('.msg-conversation-listitem');
        return Array.from(items).map((li, i) => {
            const name = li.querySelector('.msg-conversation-listitem__participant-names')?.innerText.trim() || '';
            const snippet = li.querySelector('.msg-conversation-card__message-snippet')?.innerText.trim() || '';
            const time = li.querySelector('time')?.innerText.trim() || '';
            const link = li.querySelector('a')?.href || '';
            return { i, name, snippet, time, link };
        });
    })()
    """
    cards = c.call_tool("browser_execute_script", {"code": dump_js})
    out["cards"] = cards
    
    # 3. Find Dakshesh link and navigate directly to it!
    dak_link = None
    if cards and not cards.get("isError"):
        for b in cards.get("content", []):
            if b.get("type") == "text":
                arr = json.loads(b["text"]).get("result", [])
                for item in arr:
                    if "dakshesh" in item.get("name", "").lower():
                        dak_link = item.get("link")
                        out["dak_found"] = item
                        break
    
    if dak_link:
        print(f"Navigating directly to Dakshesh URL: {dak_link}")
        c.call_tool("browser_navigate", {"url": dak_link})
        time.sleep(5)
    else:
        # Click the 2nd card via JS dispatch
        click_2nd = """
        (() => {
            const items = document.querySelectorAll('.msg-conversation-listitem');
            if (items.length > 1) {
                items[1].dispatchEvent(new MouseEvent('click', {bubbles: true}));
                return { clicked: true };
            }
            return { clicked: false };
        })()
        """
        c.call_tool("browser_execute_script", {"code": click_2nd})
        time.sleep(4)

    # 4. Screenshot
    shot = c.call_tool("browser_screenshot", {})
    if shot and not shot.get("isError"):
        for b in shot.get("content", []):
            if b.get("type") == "image":
                data = base64.b64decode(b["data"])
                p = EVIDENCE / "dakshesh-convo-full.png"
                p.write_bytes(data)
                out["shot"] = str(p)

    # 5. Extract thread text
    thread_js = """
    (() => {
        const msgList = document.querySelector('.msg-s-message-list-container') || document.querySelector('.msg-thread') || document.body;
        return msgList.innerText.slice(0, 5000);
    })()
    """
    out["thread_full_text"] = c.call_tool("browser_execute_script", {"code": thread_js})

except Exception as e:
    out["error"] = repr(e)
finally:
    c.close()

p = HERE / "_dak_full_convo.json"
p.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
print(f"DONE: {p}")
