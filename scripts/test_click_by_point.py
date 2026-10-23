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

    click_point_js = """
    (() => {
        const items = Array.from(document.querySelectorAll('li.msg-conversation-listitem'));
        const it = items.find(el => el.innerText.includes('Arayemi'));
        if (!it) return { ok: false, err: 'not_found' };

        it.scrollIntoView({ block: 'center' });
        const rect = it.getBoundingClientRect();
        const cx = rect.left + rect.width / 2;
        const cy = rect.top + rect.height / 2;
        const target = document.elementFromPoint(cx, cy);

        if (!target) return { ok: false, err: 'no_target_at_point' };

        // Dispatch full pointer/mouse sequence
        ['pointerdown', 'mousedown', 'pointerup', 'mouseup', 'click'].forEach(evtType => {
            target.dispatchEvent(new MouseEvent(evtType, {
                bubbles: true,
                cancelable: true,
                view: window,
                clientX: cx,
                clientY: cy
            }));
        });
        target.click();

        return {
            ok: true,
            target_tag: target.tagName,
            target_class: target.className,
            cx: cx,
            cy: cy
        };
    })()
    """
    res = c.call_tool("browser_execute_script", {"code": click_point_js})
    print("CLICK AT POINT RESULT:", res.get("content", [{}])[0].get("text"))

    # Now let's wait 4 seconds and check what URL / active item we have!
    time.sleep(4)
    check_js = """
    (() => {
        const activeLink = document.querySelector('.msg-conversations-container__convo-item-link--active');
        const activeCard = activeLink ? activeLink.closest('li') : null;
        return {
            active_item_text: activeCard ? activeCard.innerText.replace(/\\s+/g, ' ').slice(0, 100) : 'none',
            current_url: window.location.href
        };
    })()
    """
    res_chk = c.call_tool("browser_execute_script", {"code": check_js})
    print("NEW ACTIVE STATE:", res_chk.get("content", [{}])[0].get("text"))

except Exception as e:
    print("Error:", e)
finally:
    c.close()
