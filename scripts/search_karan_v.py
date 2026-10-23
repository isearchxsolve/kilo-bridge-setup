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
    
    # Navigate to LinkedIn messaging with search
    c.call_tool("browser_navigate", {"url": "https://www.linkedin.com/messaging/"})
    time.sleep(5)
    
    # Use search box to search for "Karan V"
    search_js = """
    (() => {
        const input = document.querySelector('input.msg-search-form__search-field') || document.querySelector('input[placeholder*="Search"]');
        if (!input) return { ok: false, err: "no_input" };
        input.focus();
        input.value = 'Karan V';
        input.dispatchEvent(new Event('input', { bubbles: true }));
        input.dispatchEvent(new Event('change', { bubbles: true }));
        return { ok: true };
    })()
    """
    out["search"] = c.call_tool("browser_execute_script", {"code": search_js})
    time.sleep(4)
    
    # Click first search result
    click_js = """
    (() => {
        const results = document.querySelectorAll('.msg-search-results__result-item, li.msg-conversation-listitem, .msg-search-form__search-results li');
        if (results.length > 0) {
            results[0].click();
            return { ok: true, count: results.length, text: results[0].innerText.slice(0, 100) };
        }
        return { ok: false, count: 0 };
    })()
    """
    out["click"] = c.call_tool("browser_execute_script", {"code": click_js})
    time.sleep(4)
    
    # Get all text from the open conversation pane
    pane_js = """
    (() => {
        const pane = document.querySelector('.msg-thread') || document.querySelector('.msg-convo-wrapper') || document.querySelector('main');
        return pane ? pane.innerText : document.body.innerText;
    })()
    """
    pane_res = c.call_tool("browser_execute_script", {"code": pane_js})
    if pane_res and not pane_res.get("isError"):
        for b in pane_res.get("content", []):
            if b.get("type") == "text":
                out["pane_text"] = b["text"][:3000]

    # Screenshot
    shot = c.call_tool("browser_screenshot", {})
    if shot and not shot.get("isError"):
        for b in shot.get("content", []):
            if b.get("type") == "image":
                import base64
                data = base64.b64decode(b["data"])
                p = EVIDENCE / "karan-v-searched.png"
                p.write_bytes(data)
                out["shot"] = str(p)

except Exception as e:
    out["err"] = str(e)
finally:
    c.close()

(HERE / "_karan_search_res.json").write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
print("SEARCH_DONE")
