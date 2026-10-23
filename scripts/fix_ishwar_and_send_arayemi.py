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

ISHWAR_CORRECTION = """Hi Ishwar,

Please disregard the previous snippet—it was routed from another channel. 

Here is our formal proposal regarding your Business Analytics project for Rmc Ready Mix India:

We specialize in designing deterministic analytics and KPI frameworks that turn complex operational and dispatch data into automated executive decision models.

Our Approach for Rmc Ready Mix:
1. Metric Architecture: Isolate key dispatch metrics, unit economics, and operational efficiency drivers.
2. Data Automation: Unify existing logs and operational reports into a structured, automated reporting pipeline.
3. Executive Dashboards: Clean visual tracking and scheduled summaries for ongoing management decisions.

Scope & Next Step:
• On-going Support / Pilot: ₹15,000 fixed pilot | ₹25,000 / month ongoing retainer
• Let's connect for 15 minutes over Google Meet to review your current data format and lock the initial metrics scope.

Best regards,
Kunal Das
Director & CTO
isearch.xsolve@gmail.com"""

ARAYEMI_RESET = """Hi Arayemi,

Apologies for the automated test snippet that misfired earlier into this thread from our testing lab. 

Looking forward to reviewing the role overview and client requirements once you share the JD. Let me know when you have it over and we can assess the alignment.

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
    
    # 1. SEND CORRECTION TO ISHWAR (currently active thread in messaging)
    print("Sending formal proposal correction to Ishwar Singh...")
    c.call_tool("browser_navigate", {"url": "https://www.linkedin.com/messaging/"})
    time.sleep(5)
    
    # Ensure Ishwar is selected (he is item 0)
    select_ishwar_js = """
    (() => {
        const items = document.querySelectorAll('li.msg-conversation-listitem');
        if (items.length > 0 && items[0].innerText.includes('ishwar')) {
            items[0].click();
            return { selected: true };
        }
        return { selected: false };
    })()
    """
    c.call_tool("browser_execute_script", {"code": select_ishwar_js})
    time.sleep(2)
    
    # Inject Ishwar correction
    paras_ish = ISHWAR_CORRECTION.split("\n\n")
    inject_ish_js = f"""
    (() => {{
        const boxes = document.querySelectorAll('div.msg-form__contenteditable[contenteditable="true"]');
        if (boxes.length === 0) return {{ ok: false }};
        const box = boxes[boxes.length - 1];
        box.focus();
        box.innerHTML = '';
        const paras = {json.dumps(paras_ish)};
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
    c.call_tool("browser_execute_script", {"code": inject_ish_js})
    time.sleep(2)
    
    # Click send
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
    c.call_tool("browser_execute_script", {"code": send_js})
    time.sleep(4)
    out["ishwar_corrected_shot"] = save_shot(c, "ishwar-proposal-delivered-correct.png")
    
    # 2. DELIVER TO ARAYEMI AFEEZ PROPERLY
    print("Delivering reset to Arayemi Afeez profile...")
    c.call_tool("browser_navigate", {"url": "https://www.linkedin.com/in/arayemi-afeez/"})
    time.sleep(6)
    
    # Click Message on Arayemi profile
    click_msg_js = """
    (() => {
        const btns = Array.from(document.querySelectorAll('button, a'));
        const msgBtn = btns.find(b => b.innerText.trim() === 'Message' || b.getAttribute('aria-label')?.includes('Message Arayemi'));
        if (msgBtn) {
            msgBtn.click();
            return { clicked: true };
        }
        return { clicked: false };
    })()
    """
    c.call_tool("browser_execute_script", {"code": click_msg_js})
    time.sleep(4)
    
    # Inject Arayemi reset
    paras_ara = ARAYEMI_RESET.split("\n\n")
    inject_ara_js = f"""
    (() => {{
        const boxes = document.querySelectorAll('div.msg-form__contenteditable[contenteditable="true"]');
        if (boxes.length === 0) return {{ ok: false }};
        const box = boxes[boxes.length - 1];
        box.focus();
        box.innerHTML = '';
        const paras = {json.dumps(paras_ara)};
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
    c.call_tool("browser_execute_script", {"code": inject_ara_js})
    time.sleep(2)
    
    out["arayemi_presend_shot"] = save_shot(c, "arayemi-actual-presend.png")
    
    # Click send
    c.call_tool("browser_execute_script", {"code": send_js})
    time.sleep(4)
    out["arayemi_postsend_shot"] = save_shot(c, "arayemi-actual-postsend.png")

except Exception as e:
    out["err"] = repr(e)
finally:
    c.close()

p = HERE / "_corrected_both_receipt.json"
p.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
print(f"CORRECTION COMPLETE: {p}")
