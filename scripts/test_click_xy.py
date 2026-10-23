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
    
    for i in range(10):
        time.sleep(2)
        res = c.call_tool("browser_execute_script", {"code": "document.querySelectorAll('li.msg-conversation-listitem').length"})
        try:
            txt = res.get("content", [{}])[0].get("text", "{}")
            if json.loads(txt).get("result", 0) > 0:
                print(f"Loaded on attempt {i+1}")
                break
        except Exception:
            pass

    # First, let's get Arayemi's exact center coordinates in viewport
    coords_js = """
    (() => {
        const items = Array.from(document.querySelectorAll('li.msg-conversation-listitem'));
        const it = items.find(el => el.innerText.includes('Arayemi'));
        if (!it) return { ok: false };
        it.scrollIntoView({ block: 'center' });
        const rect = it.getBoundingClientRect();
        return {
            ok: true,
            x: Math.round(rect.left + rect.width / 2),
            y: Math.round(rect.top + rect.height / 2)
        };
    })()
    """
    res_coords = c.call_tool("browser_execute_script", {"code": coords_js})
    print("COORDS:", res_coords.get("content", [{}])[0].get("text"))
    txt = res_coords.get("content", [{}])[0].get("text", "{}")
    c_data = json.loads(txt).get("result", {})

    if c_data.get("ok"):
        x = c_data["x"]
        y = c_data["y"]
        print(f"Calling browser_click_xy({x}, {y}) ...")
        res_click = c.call_tool("browser_click_xy", {"x": x, "y": y})
        print("browser_click_xy result:", res_click)

    time.sleep(4)

    # Check active thread now!
    check_js = """
    (() => {
        const activeLink = document.querySelector('.msg-conversations-container__convo-item-link--active');
        const activeCard = activeLink ? activeLink.closest('li') : null;
        const threadHeader = document.querySelector('.msg-title, .msg-entity-lockup__title, .msg-thread__header');
        return {
            url: window.location.href,
            active_item: activeCard ? activeCard.innerText.replace(/\\s+/g, ' ').slice(0, 100) : 'none',
            header: threadHeader ? threadHeader.innerText.replace(/\\s+/g, ' ') : 'none'
        };
    })()
    """
    res_chk = c.call_tool("browser_execute_script", {"code": check_js})
    print("CHECK AFTER CLICK_XY:")
    print(res_chk.get("content", [{}])[0].get("text"))

except Exception as e:
    print("Error:", e)
finally:
    c.close()
