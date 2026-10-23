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

ARAYEMI_THREAD_URL = "https://www.linkedin.com/messaging/thread/2-OTA4ZmNkNDQtYzgzMC00Zjg4LWI2OWUtNjM5OGZjZjI4NGE5XzEwMA==/"

ARAYEMI_RESET = """Hi Arayemi,

Apologies for the automated test snippet that misfired earlier into this thread from our testing lab. 

Looking forward to reviewing the role overview and client requirements once you share the JD. Let me know when you have it over and we can assess the mutual alignment.

Best regards,
Kunal Das
Director & CTO
isearch.xsolve@gmail.com"""

c = A.Agent360Client()
out = {}


def save_shot(client, filename):
    try:
        shot = client.call_tool("browser_screenshot", {})
        if shot and not shot.get("isError"):
            for b in shot.get("content", []):
                if b.get("type") == "image":
                    data = base64.b64decode(b["data"])
                    p = EVIDENCE / filename
                    p.write_bytes(data)
                    print(f"Receipt saved: {p} ({len(data)} bytes)")
                    return str(p)
    except Exception as e:
        print(f"Error saving {filename}: {e}")
    return None


try:
    c.start()
    print(f"Navigating directly to Arayemi Afeez thread: {ARAYEMI_THREAD_URL} ...")
    c.call_tool("browser_navigate", {"url": ARAYEMI_THREAD_URL})
    time.sleep(6)

    # 1. Assert thread belongs to Arayemi Afeez
    verify_js = """
    (() => {
        const thread = document.querySelector('.msg-thread') || document.body;
        const header = document.querySelector('.msg-title, .msg-entity-lockup__title, .msg-thread__header');
        const headerText = header ? header.innerText : '';
        const threadText = thread ? thread.innerText : '';
        const isArayemi = headerText.includes('Arayemi') || threadText.includes('Arayemi Afeez');
        return {
            is_arayemi: isArayemi,
            header: headerText.replace(/\\s+/g, ' '),
            url: window.location.href
        };
    })()
    """
    res_ver = c.call_tool("browser_execute_script", {"code": verify_js})
    txt_ver = res_ver.get("content", [{}])[0].get("text", "{}")
    ver_data = json.loads(txt_ver).get("result", {})
    print("THREAD VERIFICATION:", ver_data)
    out["verification"] = ver_data

    if not ver_data.get("is_arayemi"):
        raise RuntimeError(f"ABORT: Active thread is NOT Arayemi! Details: {ver_data}")

    # 2. Inject executive reset into composer
    paras = ARAYEMI_RESET.split("\n\n")
    inject_js = f"""
    (() => {{
        const boxes = Array.from(document.querySelectorAll('div.msg-form__contenteditable[contenteditable="true"]'));
        if (boxes.length === 0) return {{ ok: false, err: 'no_composer_box' }};
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
        return {{ ok: true, box_count: boxes.length, text_length: box.innerText.length }};
    }})()
    """
    res_inj = c.call_tool("browser_execute_script", {"code": inject_js})
    print("INJECT RESULT:", res_inj.get("content", [{}])[0].get("text", "{}"))
    out["inject"] = res_inj
    time.sleep(2)

    # 3. PRE-SEND RECEIPT
    out["presend_shot"] = save_shot(c, "arayemi-real-presend-receipt.png")

    # 4. Click Send
    send_js = """
    (() => {
        const btns = Array.from(document.querySelectorAll('button.msg-form__send-button, form.msg-form button[type="submit"]'));
        const sendBtn = btns[btns.length - 1];
        if (sendBtn && !sendBtn.disabled) {
            sendBtn.click();
            return { ok: true, clicked: true, text: sendBtn.innerText.replace(/\\s+/g, ' ') };
        }
        return { ok: false, err: sendBtn ? 'disabled' : 'not_found' };
    })()
    """
    res_send = c.call_tool("browser_execute_script", {"code": send_js})
    print("SEND CLICK RESULT:", res_send.get("content", [{}])[0].get("text", "{}"))
    out["send"] = res_send
    time.sleep(5)

    # 5. POST-SEND RECEIPT
    out["postsend_shot"] = save_shot(c, "arayemi-real-postsend-receipt.png")

    # 6. Read thread messages to confirm delivery
    read_thread_js = """
    (() => {
        const thread = document.querySelector('.msg-thread') || document.body;
        return {
            text: thread.innerText.slice(0, 3000),
            has_delivered_reset: thread.innerText.includes('Apologies for the automated test snippet')
        };
    })()
    """
    res_read = c.call_tool("browser_execute_script", {"code": read_thread_js})
    out["thread_audit"] = res_read
    print("THREAD AUDIT RESULT:", res_read.get("content", [{}])[0].get("text", "{}"))

except Exception as e:
    out["err"] = repr(e)
    print("Error:", e)
finally:
    c.close()

p = HERE / "_arayemi_delivery_success.json"
p.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
print(f"\nCOMPLETED: Receipt saved to {p}")
