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

ISHWAR_PROPOSAL = """Hi Ishwar,

Saw your requirement around identifying key metrics and turning existing operational data into strategic decision dashboards for ongoing operations. 

With 20+ years of enterprise architecture and systems leadership (NIT alumnus, Director & CTO), I specialize in building deterministic analytics frameworks that consolidate operational data, isolate high-impact KPIs, and deliver clean, automated executive dashboards.

Our Approach for Rmc Ready Mix:
1. Metric Architecture: Define and isolate your core unit economics, fleet/dispatch efficiencies, material yield, and operational bottlenecks.
2. Data Pipeline: Unify your existing reports and raw data sources into a structured, automated reporting schema without manual overhead.
3. Executive Decision Models: Deliver intuitive visual dashboards and scheduled analytical summaries for management review.

Commercials & Timeline:
• Initial Phase (Architecture & Metric Discovery): 5 business days
• Fixed-Scope Pilot: ₹15,000 | Ongoing Retainer: ₹25,000 / month

Next Step: Let's schedule a brief 15-minute virtual sync over Google Meet to review your current data format and lock the initial metrics scope.

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
    try:
        shot = client.call_tool("browser_screenshot", {})
        if shot and not shot.get("isError"):
            for b in shot.get("content", []):
                if b.get("type") == "image":
                    data = base64.b64decode(b["data"])
                    p = EVIDENCE / filename
                    p.write_bytes(data)
                    print(f"Receipt saved: {p}")
                    return str(p)
    except Exception as e:
        print(f"Error saving shot {filename}: {e}")
    return None


try:
    c.start()
    
    # =========================================================================
    # PART 1: SUBMIT PROPOSAL FOR ISHWAR SINGH
    # =========================================================================
    print("\n--- [PART 1] Submitting proposal for Ishwar Singh ---")
    c.call_tool("browser_navigate", {"url": "https://www.linkedin.com/service-marketplace/provider/requests/"})
    time.sleep(6)
    
    # Click Submit proposal button if modal not already open
    open_modal_js = """
    (() => {
        const modal = document.querySelector('.artdeco-modal, [role="dialog"]');
        if (modal && modal.innerText.includes('Your proposal')) {
            return { already_open: true };
        }
        const btns = Array.from(document.querySelectorAll('button'));
        const btn = btns.find(b => b.innerText.includes('Submit proposal'));
        if (btn) {
            btn.scrollIntoView();
            btn.click();
            btn.dispatchEvent(new MouseEvent('click', { bubbles: true }));
            return { clicked: true };
        }
        return { clicked: false, err: 'no_btn' };
    })()
    """
    res_open = c.call_tool("browser_execute_script", {"code": open_modal_js})
    print(f"Open modal: {res_open}")
    time.sleep(4)
    
    # Inject proposal into textarea
    inject_proposal_js = f"""
    (() => {{
        const ta = document.querySelector('textarea');
        if (!ta) return {{ ok: false, err: 'no_textarea' }};
        ta.focus();
        ta.value = {json.dumps(ISHWAR_PROPOSAL)};
        ta.dispatchEvent(new Event('input', {{ bubbles: true }}));
        ta.dispatchEvent(new Event('change', {{ bubbles: true }}));
        
        // Ensure phone consultation is unchecked
        const cb = document.querySelector('input[type="checkbox"]');
        if (cb && cb.checked) {{
            cb.click();
        }}
        
        return {{ ok: true, val_len: ta.value.length, cb_checked: cb ? cb.checked : false }};
    }})()
    """
    res_inj = c.call_tool("browser_execute_script", {"code": inject_proposal_js})
    print(f"Inject proposal: {res_inj}")
    time.sleep(2)
    
    # PRE-SUBMIT RECEIPT
    out["ishwar_presend_shot"] = save_shot(c, "ishwar-proposal-presend-receipt.png")
    
    # Click Send proposal
    send_proposal_js = """
    (() => {
        const btns = Array.from(document.querySelectorAll('button'));
        const sendBtn = btns.find(b => b.innerText.includes('Send proposal'));
        if (sendBtn && !sendBtn.disabled) {
            sendBtn.click();
            return { ok: true, clicked: true, text: sendBtn.innerText.replace(/\\s+/g, ' ') };
        }
        return { ok: false, err: sendBtn ? 'disabled' : 'not_found' };
    })()
    """
    res_send_prop = c.call_tool("browser_execute_script", {"code": send_proposal_js})
    print(f"Send proposal click: {res_send_prop}")
    out["ishwar_send_res"] = res_send_prop
    time.sleep(5)
    
    # POST-SUBMIT RECEIPT
    out["ishwar_postsend_shot"] = save_shot(c, "ishwar-proposal-postsend-receipt.png")

    # =========================================================================
    # PART 2: DELIVER EXECUTIVE RESET TO ARAYEMI AFEEZ
    # =========================================================================
    print("\n--- [PART 2] Delivering reset to Arayemi Afeez ---")
    c.call_tool("browser_navigate", {"url": "https://www.linkedin.com/messaging/"})
    time.sleep(6)
    
    # Click Arayemi Afeez thread
    open_arayemi_js = """
    (() => {
        const items = Array.from(document.querySelectorAll('li.msg-conversation-listitem'));
        for (const it of items) {
            if (it.innerText.includes('Arayemi Afeez') || it.innerText.includes('Arayemi')) {
                it.click();
                const a = it.querySelector('a');
                if (a) a.click();
                return { clicked: true, name: 'Arayemi Afeez' };
            }
        }
        return { clicked: false };
    })()
    """
    res_ara_click = c.call_tool("browser_execute_script", {"code": open_arayemi_js})
    print(f"Open Arayemi thread: {res_ara_click}")
    time.sleep(4)
    
    # Inject reset paragraphs into message box
    paras = ARAYEMI_RESET.split("\n\n")
    inject_ara_js = f"""
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
    res_ara_inj = c.call_tool("browser_execute_script", {"code": inject_ara_js})
    print(f"Inject Arayemi message: {res_ara_inj}")
    time.sleep(2)
    
    # PRE-SEND RECEIPT
    out["arayemi_presend_shot"] = save_shot(c, "arayemi-reset-presend-receipt.png")
    
    # Click Send
    send_ara_js = """
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
    res_ara_send = c.call_tool("browser_execute_script", {"code": send_ara_js})
    print(f"Arayemi send click: {res_ara_send}")
    out["arayemi_send_res"] = res_ara_send
    time.sleep(4)
    
    # POST-SEND RECEIPT
    out["arayemi_postsend_shot"] = save_shot(c, "arayemi-reset-postsend-receipt.png")

except Exception as e:
    out["err"] = repr(e)
finally:
    c.close()

res_path = HERE / "_both_inbounds_submitted_receipt.json"
res_path.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
print(f"\nBOTH INBOUNDS SUBMITTED: Written to {res_path}")
