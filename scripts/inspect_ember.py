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

    find_ember_js = """
    (() => {
        const items = Array.from(document.querySelectorAll('li.msg-conversation-listitem'));
        const it = items.find(el => el.innerText.includes('Arayemi'));
        if (!it) return { ok: false };
        
        const link = it.querySelector('.msg-conversation-listitem__link');
        const card = it.querySelector('.msg-conversation-card');
        
        // Let's inspect Ember container or window properties
        const emberViews = window.Ember ? 'window.Ember exists' : 'no window.Ember';
        
        // Check for any links or click handlers or hrefs anywhere inside it
        const allDescendants = Array.from(it.querySelectorAll('*'));
        const clickableDescendants = allDescendants.filter(d => d.onclick || d.hasAttribute('href') || d.hasAttribute('data-control-name') || d.hasAttribute('data-view-name'));

        return {
            emberViews,
            it_id: it.id,
            card_id: card ? card.id : null,
            link_id: link ? link.id : null,
            clickable_count: clickableDescendants.length,
            clickable_info: clickableDescendants.map(d => ({
                tag: d.tagName,
                class: d.className,
                href: d.getAttribute('href'),
                attrs: Array.from(d.attributes).map(a => a.name + '=' + a.value)
            }))
        };
    })()
    """
    res = c.call_tool("browser_execute_script", {"code": find_ember_js})
    print("EMBER INSPECTION:")
    print(res.get("content", [{}])[0].get("text"))

except Exception as e:
    print("Error:", e)
finally:
    c.close()
