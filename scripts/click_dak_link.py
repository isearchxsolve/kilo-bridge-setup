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
    
    js = """
    (() => {
        const links = Array.from(document.querySelectorAll('a.msg-conversation-listitem__link'));
        for (const a of links) {
            if (a.innerText.includes('Dakshesh')) {
                a.focus();
                a.click();
                return { clicked: true, href: a.href, text: a.innerText.slice(0, 150) };
            }
        }
        // Fallback: any link in the 2nd item
        const items = document.querySelectorAll('li.msg-conversation-listitem');
        if (items.length > 1) {
            const a = items[1].querySelector('a');
            if (a) {
                a.focus();
                a.click();
                return { clicked: true, fallback: true, href: a.href };
            }
        }
        return { clicked: false };
    })()
    """
    out["click"] = c.call_tool("browser_execute_script", {"code": js})
    time.sleep(4)
    
    shot = c.call_tool("browser_screenshot", {})
    if shot and not shot.get("isError"):
        for b in shot.get("content", []):
            if b.get("type") == "image":
                data = base64.b64decode(b["data"])
                p = EVIDENCE / "dakshesh-bhardwaj-opened-live.png"
                p.write_bytes(data)
                out["shot"] = str(p)
                
    read_js = """
    (() => {
        const thread = document.querySelector('.msg-thread') || document.querySelector('.msg-conversations-container') || document.body;
        return thread.innerText.slice(0, 4000);
    })()
    """
    out["dakshesh_exact_thread_text"] = c.call_tool("browser_execute_script", {"code": read_js})

except Exception as e:
    out["error"] = repr(e)
finally:
    c.close()

p = HERE / "_dakshesh_direct_link_opened.json"
p.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
print(f"DONE: {p}")
