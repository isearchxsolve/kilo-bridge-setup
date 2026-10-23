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
    
    click_js = """
    (() => {
        const items = document.querySelectorAll('li.msg-conversation-listitem');
        if (items.length > 1) {
            const dakItem = items[1]; // Dakshesh is 2nd item
            const link = dakItem.querySelector('.msg-conversation-card__archive, a, div') || dakItem;
            dakItem.click();
            link.click();
            return { clicked: true, text: dakItem.innerText };
        }
        return { clicked: false };
    })()
    """
    res_click = c.call_tool("browser_execute_script", {"code": click_js})
    time.sleep(3)
    out["click"] = res_click
    
    shot = c.call_tool("browser_screenshot", {})
    if shot and not shot.get("isError"):
        for b in shot.get("content", []):
            if b.get("type") == "image":
                data = base64.b64decode(b["data"])
                p = EVIDENCE / "dakshesh-bhardwaj-active-thread.png"
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

p = HERE / "_dak_thread_text.json"
p.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
print(f"DONE: {p}")
