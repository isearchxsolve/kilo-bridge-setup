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
    
    # Click via dispatchEvent or click() on all candidate elements
    js = """
    (() => {
        const elements = Array.from(document.querySelectorAll('*'));
        const dakElements = elements.filter(el => el.children.length === 0 && el.innerText && el.innerText.includes('Dakshesh Bhardwaj'));
        if (dakElements.length > 0) {
            const target = dakElements[0].closest('li') || dakElements[0].closest('a') || dakElements[0];
            target.click();
            // Also try mouse events
            target.dispatchEvent(new MouseEvent('mousedown', {bubbles: true}));
            target.dispatchEvent(new MouseEvent('mouseup', {bubbles: true}));
            target.dispatchEvent(new MouseEvent('click', {bubbles: true}));
            return { clicked: true, tagName: target.tagName, text: target.innerText.slice(0, 200) };
        }
        return { clicked: false, total_dak: dakElements.length };
    })()
    """
    res = c.call_tool("browser_execute_script", {"code": js})
    time.sleep(3)
    out["click_res"] = res
    
    shot = c.call_tool("browser_screenshot", {})
    if shot and not shot.get("isError"):
        for b in shot.get("content", []):
            if b.get("type") == "image":
                data = base64.b64decode(b["data"])
                p = EVIDENCE / "dakshesh-opened-live.png"
                p.write_bytes(data)
                out["shot"] = str(p)
                
    read_thread = """
    (() => {
        const msgs = document.querySelectorAll('.msg-s-message-list__event, .msg-s-event-listitem, .msg-thread');
        return Array.from(msgs).map(m => m.innerText.trim()).filter(Boolean);
    })()
    """
    out["messages"] = c.call_tool("browser_execute_script", {"code": read_thread})

except Exception as e:
    out["error"] = repr(e)
finally:
    c.close()

p = HERE / "_dak_open_result.json"
p.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
print(f"DONE: {p}")
