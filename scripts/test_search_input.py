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
    time.sleep(5)

    # Find search input
    find_search_js = """
    (() => {
        const inp = document.querySelector('input.msg-search-form__search-field, input[placeholder*="Search"]');
        if (!inp) return { ok: false };
        inp.focus();
        inp.value = 'Arayemi';
        inp.dispatchEvent(new Event('input', { bubbles: true }));
        inp.dispatchEvent(new Event('change', { bubbles: true }));
        return { ok: true, placeholder: inp.placeholder };
    })()
    """
    res = c.call_tool("browser_execute_script", {"code": find_search_js})
    print("SEARCH INPUT:", res.get("content", [{}])[0].get("text"))
    time.sleep(3)

    # Press Enter
    c.call_tool("browser_press_key", {"key": "Enter"})
    time.sleep(3)

    # Inspect results
    inspect_results_js = """
    (() => {
        const results = Array.from(document.querySelectorAll('.msg-search-results__list-item, li.msg-conversation-listitem, .search-result'));
        return {
            count: results.length,
            items: results.map(r => r.innerText.replace(/\\s+/g, ' ').slice(0, 100))
        };
    })()
    """
    res_items = c.call_tool("browser_execute_script", {"code": inspect_results_js})
    print("RESULTS:")
    print(res_items.get("content", [{}])[0].get("text"))

except Exception as e:
    print("Error:", e)
finally:
    c.close()
