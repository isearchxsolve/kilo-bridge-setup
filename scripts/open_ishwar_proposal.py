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

try:
    c.start()
    print("Navigating to https://www.linkedin.com/service-marketplace/provider/requests/ ...")
    c.call_tool("browser_navigate", {"url": "https://www.linkedin.com/service-marketplace/provider/requests/"})
    time.sleep(6)
    
    # Click Submit proposal button
    click_js = """
    (() => {
        const btns = Array.from(document.querySelectorAll('button, a'));
        const btn = btns.find(b => b.innerText.trim() === 'Submit proposal');
        if (btn) {
            btn.click();
            return { clicked: true, text: btn.innerText };
        }
        return { clicked: false, total_btns: btns.length };
    })()
    """
    out["click"] = c.call_tool("browser_execute_script", {"code": click_js})
    time.sleep(4)
    
    shot = c.call_tool("browser_screenshot", {})
    if shot and not shot.get("isError"):
        for b in shot.get("content", []):
            if b.get("type") == "image":
                data = base64.b64decode(b["data"])
                p = EVIDENCE / "ishwar-proposal-modal-active.png"
                p.write_bytes(data)
                out["shot"] = str(p)
                
    modal_info = """
    (() => {
        const modal = document.querySelector('.artdeco-modal, [role="dialog"], form') || document.body;
        return {
            url: window.location.href,
            modal_text: modal.innerText.slice(0, 3000),
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
    out["modal"] = c.call_tool("browser_execute_script", {"code": modal_info})

except Exception as e:
    out["err"] = repr(e)
finally:
    c.close()

p = HERE / "_ishwar_proposal_active.json"
p.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
print(f"SAVED: {p}")
