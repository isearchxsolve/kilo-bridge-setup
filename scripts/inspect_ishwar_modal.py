import json
import sys
import time
import base64
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import agent360_client as A

EVIDENCE = HERE.parent / "evidence" / "employment-lane"

c = A.Agent360Client()
out = {}

def save_shot(client, filename):
    shot = client.call_tool("browser_screenshot", {})
    if shot and not shot.get("isError"):
        for b in shot.get("content", []):
            if b.get("type") == "image":
                data = base64.b64decode(b["data"])
                p = EVIDENCE / filename
                p.write_bytes(data)
                print(f"Receipt saved: {p}")
                return str(p)
    return None

try:
    c.start()
    
    # 1. Navigate to service marketplace
    print("Navigating to https://www.linkedin.com/service-marketplace/provider/requests/ ...")
    c.call_tool("browser_navigate", {"url": "https://www.linkedin.com/service-marketplace/provider/requests/"})
    time.sleep(6)
    
    out["pre_click_shot"] = save_shot(c, "ishwar-pre-submit-click.png")
    
    # 2. Click Submit proposal
    click_js = """
    (() => {
        const btns = Array.from(document.querySelectorAll('button, a'));
        const btn = btns.find(b => b.innerText.includes('Submit proposal'));
        if (btn) {
            btn.scrollIntoView();
            btn.click();
            btn.dispatchEvent(new MouseEvent('click', { bubbles: true }));
            return { clicked: true, text: btn.innerText.replace(/\\s+/g, ' ') };
        }
        return { clicked: false, total_btns: btns.length };
    })()
    """
    out["click"] = c.call_tool("browser_execute_script", {"code": click_js})
    time.sleep(4)
    
    out["post_click_shot"] = save_shot(c, "ishwar-proposal-form-live.png")
    
    # 3. Read page/modal DOM
    dom_js = """
    (() => {
        const modal = document.querySelector('.artdeco-modal, [role="dialog"]') || document.body;
        return {
            url: window.location.href,
            heading: modal.querySelector('h1, h2, h3')?.innerText || '',
            text_snippet: modal.innerText.slice(0, 2000),
            inputs: Array.from(modal.querySelectorAll('input, textarea, select')).map(el => ({
                tag: el.tagName,
                type: el.type,
                name: el.name,
                id: el.id,
                placeholder: el.placeholder,
                label: el.closest('label')?.innerText || el.getAttribute('aria-label') || ''
            }))
        };
    })()
    """
    out["dom"] = c.call_tool("browser_execute_script", {"code": dom_js})

except Exception as e:
    out["err"] = repr(e)
finally:
    c.close()

p = HERE / "_ishwar_click_and_inspect.json"
p.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
print(f"DONE: {p}")
