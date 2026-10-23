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

    inspect_attrs_js = """
    (() => {
        const items = Array.from(document.querySelectorAll('li.msg-conversation-listitem'));
        const it = items.find(el => el.innerText.includes('Arayemi'));
        if (!it) return { found: false };
        
        function getAllAttrs(el) {
            if (!el) return {};
            const res = {};
            for (let a of el.attributes) res[a.name] = a.value;
            return res;
        }

        const link = it.querySelector('.msg-conversation-listitem__link');
        const card = it.querySelector('.msg-conversation-card');
        
        return {
            found: true,
            li_attrs: getAllAttrs(it),
            link_attrs: getAllAttrs(link),
            card_attrs: getAllAttrs(card),
            link_classes: link ? link.className : null
        };
    })()
    """
    res = c.call_tool("browser_execute_script", {"code": inspect_attrs_js})
    txt = res.get("content", [{}])[0].get("text", "{}")
    print("\nATTRS:")
    print(txt)

except Exception as e:
    print("Error:", e)
finally:
    c.close()
