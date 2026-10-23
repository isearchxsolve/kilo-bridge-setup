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

    search_js = """
    (() => {
        const inp = document.querySelector('input.msg-cross-pillar-search-form__search-field');
        if (!inp) return { ok: false };
        inp.focus();
        inp.value = 'Arayemi';
        inp.dispatchEvent(new Event('input', { bubbles: true }));
        inp.dispatchEvent(new Event('change', { bubbles: true }));
        return { ok: true };
    })()
    """
    res = c.call_tool("browser_execute_script", {"code": search_js})
    print("SEARCH INJECT:", res)
    time.sleep(3)

    # Press Enter
    c.call_tool("browser_press_key", {"key": "Enter"})
    time.sleep(4)

    # Inspect results
    inspect_js = """
    (() => {
        const items = Array.from(document.querySelectorAll('.msg-cross-pillar-search-form__result, .msg-search-result, li.msg-conversation-listitem'));
        return items.map((it, idx) => ({
            idx: idx,
            tag: it.tagName,
            cls: it.className,
            text: it.innerText.replace(/\\s+/g, ' ').slice(0, 100)
        }));
    })()
    """
    res_items = c.call_tool("browser_execute_script", {"code": inspect_js})
    print("ITEMS AFTER SEARCH:")
    print(res_items.get("content", [{}])[0].get("text"))

except Exception as e:
    print("Error:", e)
finally:
    c.close()
