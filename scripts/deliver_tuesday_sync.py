import json
import sys
import time
import base64
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import agent360_client as A

EVIDENCE = HERE.parent / "evidence" / "employment-lane"
EVIDENCE.mkdir(parents=True, exist_ok=True)

out = {}
c = A.Agent360Client()

DAKSHESH_MSG = """Hi Dakshesh,

Tuesday works perfectly.

I will keep an open window between 2:00 PM and 5:00 PM IST—let me know what 20-minute slot suits your calendar best, or share your preferred email and I’ll send over a Google Meet invite directly.

Have a productive rest of the Cypher summit and safe travels back.

Best regards,
Kunal Das
Director & CTO
(isearch.xsolve@gmail.com)"""

KARAN_MSG = """Hi Karan,

Appreciate the follow-up. Dakshesh and I are aligning on a sync for Tuesday post-Cypher. Looking forward to exploring synergies with the Techdataseeders team.

Best,
Kunal"""


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


def deliver_lead(client, profile_url, msg_text, lead_name):
    print(f"\n==========================================")
    print(f"DELIVERING TO: {lead_name} ({profile_url})")
    print(f"==========================================")
    
    # 1. Navigate to profile
    client.call_tool("browser_navigate", {"url": profile_url})
    time.sleep(6)
    
    # Trigger message window
    find_recipient_js = """
    (() => {
        const a = document.querySelector('a[href*="/messaging/compose/"]');
        if (a) {
            const m = a.href.match(/recipient=([^&]+)/);
            if (m) return { ok: true, recipient: m[1], method: 'compose_link' };
        }
        
        const btns = Array.from(document.querySelectorAll('a, button'));
        const msgBtn = btns.find(b => b.innerText.trim() === 'Message' || b.getAttribute('aria-label')?.includes('Message'));
        if (msgBtn) {
            msgBtn.click();
            return { ok: true, clicked: true, method: 'msg_btn' };
        }
        return { ok: false, err: 'no_recipient' };
    })()
    """
    recip_info = client.call_tool("browser_execute_script", {"code": find_recipient_js})
    print(f"Recipient detection: {recip_info}")
    time.sleep(4)
    
    # Check current URL or find compose link after click
    current_url_js = """
    (() => {
        const u = window.location.href;
        const m = u.match(/recipient=([^&]+)/);
        if (m) return m[1];
        const a = document.querySelector('a[href*="/messaging/compose/"]');
        if (a) {
            const m2 = a.href.match(/recipient=([^&]+)/);
            if (m2) return m2[1];
        }
        return null;
    })()
    """
    rec_res = client.call_tool("browser_execute_script", {"code": current_url_js})
    recip_id = None
    if rec_res and not rec_res.get("isError"):
        for b in rec_res.get("content", []):
            if b.get("type") == "text":
                try:
                    recip_id = json.loads(b["text"]).get("result")
                except Exception:
                    recip_id = b["text"]
    
    if recip_id and isinstance(recip_id, str) and len(recip_id) > 5:
        compose_url = f"https://www.linkedin.com/messaging/compose/?recipient={recip_id}"
        print(f"Navigating to direct compose URL: {compose_url}")
        client.call_tool("browser_navigate", {"url": compose_url})
        time.sleep(5)
    else:
        print("Using current page / overlay message box...")
    
    # Inject paragraphs
    paras = msg_text.split("\n\n")
    inject_js = f"""
    (() => {{
        const boxes = document.querySelectorAll('div.msg-form__contenteditable[contenteditable="true"]');
        if (boxes.length === 0) return {{ ok: false, err: 'no_box_found' }};
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
        return {{ ok: true, box_count: boxes.length }};
    }})()
    """
    inj_res = client.call_tool("browser_execute_script", {"code": inject_js})
    print(f"Inject result: {inj_res}")
    time.sleep(2)
    
    # PRE-SEND RECEIPT
    shot_pre = save_shot(client, f"{lead_name.lower()}-tuesday-presend.png")
    
    # CLICK SEND
    send_js = """
    (() => {
        const btns = Array.from(document.querySelectorAll('button.msg-form__send-button, form.msg-form button[type="submit"]'));
        const sendBtn = btns[btns.length - 1];
        if (sendBtn && !sendBtn.disabled) {
            sendBtn.click();
            return { ok: true, clicked: true };
        }
        return { ok: false, err: sendBtn ? 'disabled' : 'not_found' };
    })()
    """
    send_res = client.call_tool("browser_execute_script", {"code": send_js})
    print(f"Send click result: {send_res}")
    time.sleep(4)
    
    # POST-SEND RECEIPT
    shot_post = save_shot(client, f"{lead_name.lower()}-tuesday-postsend.png")
    
    return {
        "lead": lead_name,
        "recipient_id": recip_id,
        "inject": inj_res,
        "pre_shot": shot_pre,
        "send": send_res,
        "post_shot": shot_post
    }


try:
    c.start()
    out["dakshesh"] = deliver_lead(c, "https://www.linkedin.com/in/daksheshbhardwaj/", DAKSHESH_MSG, "dakshesh")
    time.sleep(3)
    out["karan"] = deliver_lead(c, "https://www.linkedin.com/in/karan-v-732b95427/", KARAN_MSG, "karan")
except Exception as e:
    out["err"] = str(e)
finally:
    c.close()

res_path = HERE / "_tuesday_sync_receipt.json"
res_path.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
print(f"\nTUESDAY SYNC DELIVERED: Written to {res_path}")
