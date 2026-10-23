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

    check_js = """
    (() => {
        const activeLink = document.querySelector('.msg-conversations-container__convo-item-link--active');
        const activeCard = activeLink ? activeLink.closest('li') : null;
        const threadHeader = document.querySelector('.msg-title, .msg-entity-lockup__title, .msg-thread__header');
        return {
            active_item_text: activeCard ? activeCard.innerText.replace(/\\s+/g, ' ').slice(0, 100) : 'none',
            thread_header_text: threadHeader ? threadHeader.innerText.replace(/\\s+/g, ' ') : 'none',
            current_url: window.location.href
        };
    })()
    """
    res = c.call_tool("browser_execute_script", {"code": check_js})
    print("STATUS:", res.get("content", [{}])[0].get("text"))

except Exception as e:
    print("Error:", e)
finally:
    c.close()
