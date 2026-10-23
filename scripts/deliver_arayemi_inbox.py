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

ARAYEMI_RESET = """Hi Arayemi,

Apologies for the automated test snippet that misfired earlier into this thread from our testing lab. 

Looking forward to reviewing the role overview and client requirements once you share the JD. Let me know when you have it over and we can assess the mutual alignment.

Best regards,
Kunal Das
Director & CTO
isearch.xsolve@gmail.com"""

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
    print("Navigating to messaging...")
    c.call_tool("browser_navigate", {"url": "https://www.linkedin.com/messaging/"})
    time.sleep(5)
    
    # Click Arayemi Afeez in list
    click_js = """
    (() => {
        const items = Array.from(document.querySelectorAll('li.msg-conversation-listitem'));
        for (const it of items) {
            const nameEl = it.querySelector('.msg-conversation-listitem__participant-names');
            if (nameEl && nameEl.innerText.includes('Arayemi')) {
                it.click();
                const a = it.querySelector('a');
                if (a) a.click();
                return { clicked: true, name: nameEl.innerText };
            }
        }
        return { clicked: false, total_items: items.length };
    })()
    """
    out["click"] = c.call_tool("browser_execute_script", {"code": click_js})
    time.sleep(4)
    
    # Inject reset paragraphs
    paras = ARAYEMI_RESET.split("\n\n")
    inject_js = f"""
    (() => {{
        const boxes = document.querySelectorAll('div.msg-form__contenteditable[contenteditable="true"]');
        if (boxes.length === 0) return {{ ok: false }};
        const box = boxes[boxes.length - 1];
        box.focus();
        box.innerHTML = '';
        const paras = {json.dumps(paras)};
        paras.forEach(t => {{
            const p = document.createElement('p');
            p.innerText = t;
            box.appendChild(p);
        }});
        box.dispatchEvent(new Event('input', {{ bubbles: true }}));
        box.dispatchEvent(new Event('change', {{ bubbles: true }}));
        return {{ ok: true }};
    }})()
    """
    out["inject"] = c.call_tool("browser_execute_script", {"code": inject_js})
    time.sleep(2)
    
    out["presend_shot"] = save_shot(c, "arayemi-inbox-presend-verified.png")
    
    # Send
    send_js = """
    (() => {
        const btns = Array.from(document.querySelectorAll('button.msg-form__send-button, form.msg-form button[type="submit"]'));
        const sendBtn = btns[btns.length - 1];
        if (sendBtn && !sendBtn.disabled) {
            sendBtn.click();
            return { ok: true, clicked: true };
        }
        return { ok: false };
    })()
    """
    out["send"] = c.call_tool("browser_execute_script", {"code": send_js})
    time.sleep(4)
    
    out["postsend_shot"] = save_shot(c, "arayemi-inbox-postsend-verified.png")

except Exception as e:
    out["err"] = repr(e)
finally:
    c.close()

p = HERE / "_arayemi_inbox_delivery.json"
p.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
print(f"DONE: {p}")
