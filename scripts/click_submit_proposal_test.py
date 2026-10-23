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
    
    # Click Submit proposal
    js = """
    (() => {
        const btns = Array.from(document.querySelectorAll('button'));
        const btn = btns.find(b => b.innerText.trim() === 'Submit proposal');
        if (btn) {
            btn.focus();
            btn.click();
            btn.dispatchEvent(new MouseEvent('click', { bubbles: true }));
            return { clicked: true, className: btn.className, text: btn.innerText };
        }
        return { clicked: false, total_btns: btns.length };
    })()
    """
    out["click"] = c.call_tool("browser_execute_script", {"code": js})
    time.sleep(5)
    
    shot = c.call_tool("browser_screenshot", {})
    if shot and not shot.get("isError"):
        for b in shot.get("content", []):
            if b.get("type") == "image":
                data = base64.b64decode(b["data"])
                p = EVIDENCE / "after-submit-proposal-click.png"
                p.write_bytes(data)
                out["shot"] = str(p)
                
    page_info = """
    (() => {
        return {
            url: window.location.href,
            body: document.body.innerText.slice(0, 3000)
        };
    })()
    """
    out["page"] = c.call_tool("browser_execute_script", {"code": page_info})

except Exception as e:
    out["err"] = repr(e)
finally:
    c.close()

p = HERE / "_submit_proposal_test.json"
p.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
print(f"DONE: {p}")
