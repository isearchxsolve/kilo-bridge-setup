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
    print("Navigating to messaging...")
    c.call_tool("browser_navigate", {"url": "https://www.linkedin.com/messaging/"})
    time.sleep(5)

    test_click_real_arayemi_js = """
    (() => {
        const items = Array.from(document.querySelectorAll('li.msg-conversation-listitem'));
        const realArayemi = items.find(el => {
            const nameEl = el.querySelector('.msg-conversation-listitem__participant-names');
            return nameEl && nameEl.innerText.toLowerCase().includes('arayemi');
        });

        if (!realArayemi) {
            return { ok: false, err: 'real_arayemi_not_found', names: items.map(el => el.querySelector('.msg-conversation-listitem__participant-names')?.innerText) };
        }

        const name = realArayemi.querySelector('.msg-conversation-listitem__participant-names')?.innerText;
        realArayemi.scrollIntoView({ block: 'center' });

        const link = realArayemi.querySelector('.msg-conversation-listitem__link') || realArayemi;
        link.focus();
        link.click();
        
        ['mousedown', 'mouseup', 'click'].forEach(evt => {
            link.dispatchEvent(new MouseEvent(evt, { bubbles: true, cancelable: true }));
        });

        return {
            ok: true,
            found_name: name,
            link_tag: link.tagName,
            link_class: link.className
        };
    })()
    """
    res = c.call_tool("browser_execute_script", {"code": test_click_real_arayemi_js})
    print("CLICK REAL ARAYEMI:")
    print(res.get("content", [{}])[0].get("text"))
    time.sleep(4)

    # Now verify active thread header
    check_js = """
    (() => {
        const thread = document.querySelector('.msg-thread') || document.body;
        const activeItem = document.querySelector('.msg-conversations-container__convo-item-link--active');
        const activeName = activeItem ? activeItem.querySelector('.msg-conversation-listitem__participant-names')?.innerText : null;
        return {
            url: window.location.href,
            active_name: activeName,
            thread_snippet: thread.innerText.slice(0, 500)
        };
    })()
    """
    res_chk = c.call_tool("browser_execute_script", {"code": check_js})
    print("ACTIVE THREAD NOW:")
    print(res_chk.get("content", [{}])[0].get("text"))

except Exception as e:
    print("Error:", e)
finally:
    c.close()
