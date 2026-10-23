import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import agent360_client as A

EVIDENCE = HERE.parent / "evidence" / "employment-lane"

out = {}
c = A.Agent360Client()
try:
    c.start()
    
    # 1. Type "Karan V" into the search input or scroll conversation list
    js = """
    (() => {
        const list = document.querySelector('.msg-conversations-container__conversations-list');
        if (list) {
            list.scrollTop = 1000;
        }
        return { scrolled: !!list };
    })()
    """
    c.call_tool("browser_execute_script", {"code": js})
    time.sleep(3)
    
    # Click Karan V
    click_js = """
    (() => {
        const items = document.querySelectorAll('li.msg-conversation-listitem');
        for (const li of items) {
            if (li.innerText.includes('Karan V') || li.innerText.includes('Karan')) {
                const link = li.querySelector('a') || li;
                link.click();
                return { clicked: true, text: li.innerText.slice(0, 100) };
            }
        }
        return { clicked: false, available: Array.from(items).map(i => i.innerText.slice(0, 40)) };
    })()
    """
    res = c.call_tool("browser_execute_script", {"code": click_js})
    out["click"] = res
    time.sleep(4)
    
    # Extract message history
    hist_js = """
    (() => {
        const titleEl = document.querySelector('.msg-title-bar__title') || document.querySelector('.msg-entity-lockup__entity-title');
        const msgs = Array.from(document.querySelectorAll('.msg-s-message-list__event, .msg-s-event-listitem')).map(el => el.innerText.trim());
        return {
            title: titleEl ? titleEl.innerText.trim() : '',
            msgs: msgs
        };
    })()
    """
    h_res = c.call_tool("browser_execute_script", {"code": hist_js})
    out["history"] = h_res
    
    # Take screenshot
    shot = c.call_tool("browser_screenshot", {})
    if shot and not shot.get("isError"):
        for b in shot.get("content", []):
            if b.get("type") == "image":
                import base64
                data = base64.b64decode(b["data"])
                p = EVIDENCE / "karan-v-actual-thread.png"
                p.write_bytes(data)
                out["shot"] = str(p)

except Exception as e:
    out["err"] = str(e)
finally:
    c.close()

(HERE / "_karan_exact.json").write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
print("EXACT_DONE")
