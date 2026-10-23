import json
import sys
import time
import base64
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import agent360_client as A

EVIDENCE = HERE.parent / "evidence" / "employment-lane"

out = {}
c = A.Agent360Client()

try:
    c.start()
    print("Navigating to messaging...")
    c.call_tool("browser_navigate", {"url": "https://www.linkedin.com/messaging/"})
    time.sleep(5)
    
    # Click Dakshesh
    click_js = """
    (() => {
        const items = document.querySelectorAll('li.msg-conversation-listitem');
        for (const li of items) {
            if (li.innerText.toLowerCase().includes('dakshesh')) {
                const link = li.querySelector('a') || li;
                link.click();
                return { clicked: true };
            }
        }
        return { clicked: false };
    })()
    """
    c.call_tool("browser_execute_script", {"code": click_js})
    time.sleep(3)
    
    shot = c.call_tool("browser_screenshot", {})
    if shot and not shot.get("isError"):
        for b in shot.get("content", []):
            if b.get("type") == "image":
                data = base64.b64decode(b["data"])
                p = EVIDENCE / "dakshesh-bhardwaj-live-reply-602pm.png"
                p.write_bytes(data)
                out["shot"] = str(p)
                
    read_js = """
    (() => {
        const thread = document.querySelector('.msg-thread') || document.body;
        return thread.innerText.slice(0, 3000);
    })()
    """
    out["text"] = c.call_tool("browser_execute_script", {"code": read_js})

except Exception as e:
    out["error"] = repr(e)
finally:
    try:
        c.close()
    except Exception:
        pass

p = HERE / "_dakshesh_exact_text.json"
p.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
print(f"SAVED: {p}")
