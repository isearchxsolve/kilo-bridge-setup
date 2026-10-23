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
    print("Navigating to https://www.linkedin.com/messaging/ ...")
    c.call_tool("browser_navigate", {"url": "https://www.linkedin.com/messaging/"})
    time.sleep(6)
    
    # Click Dakshesh
    js = """
    (() => {
        const items = Array.from(document.querySelectorAll('li.msg-conversation-listitem, .msg-conversation-card'));
        for (const it of items) {
            if (it.innerText.includes('Dakshesh')) {
                it.click();
                const a = it.querySelector('a');
                if (a) a.click();
                return { clicked: true, text: it.innerText.slice(0, 200) };
            }
        }
        return { clicked: false, total_items: items.length };
    })()
    """
    out["click"] = c.call_tool("browser_execute_script", {"code": js})
    time.sleep(4)
    
    shot = c.call_tool("browser_screenshot", {})
    if shot and not shot.get("isError"):
        for b in shot.get("content", []):
            if b.get("type") == "image":
                data = base64.b64decode(b["data"])
                p = EVIDENCE / "dakshesh-bhardwaj-live-thread-read.png"
                p.write_bytes(data)
                out["shot"] = str(p)
                
    read_js = """
    (() => {
        const thread = document.querySelector('.msg-thread') || document.querySelector('.msg-conversations-container__convo-item') || document.body;
        return thread.innerText.slice(0, 3000);
    })()
    """
    out["thread_text"] = c.call_tool("browser_execute_script", {"code": read_js})

except Exception as e:
    out["error"] = repr(e)
finally:
    c.close()

p = HERE / "_dak_thread_live.json"
p.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
print(f"DONE: {p}")
