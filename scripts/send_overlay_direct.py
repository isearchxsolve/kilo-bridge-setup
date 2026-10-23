import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import agent360_client as A

EVIDENCE = HERE.parent / "evidence" / "employment-lane"
EVIDENCE.mkdir(parents=True, exist_ok=True)

out = {}
c = A.Agent360Client()

DAKSHESH_MSG = """Hi Dakshesh,
Appreciate you reaching out. While I am based out of Silchar and operating our engineering lab remotely (so I won't be on the ground in Bengaluru for Cypher tomorrow), I would be glad to connect virtually.

Seeing your work as Co-Founder & COO scaling Data & AI products, we share direct architectural overlap. Over the past 8 months, our team has built and battle-tested deep enterprise infrastructure across three core areas that may be highly relevant to your roadmap:

1. Deterministic Agent Evaluation (ASES v3.1 Engine): Eliminating hallucinations and drift in production agent workflows with zero-token deterministic guardrails.
2. Autonomous Multi-Runtime Pipelines: Distributed worker fabrics (Kaggle/cloud/edge) executing long-horizon data orchestration without burning expensive GPU/API quotas.
3. Fractional Architecture Advisory / Co-Building: Partnering at the leadership level to design scalable data architectures and production-grade LLM systems.

If any of these align with what you're scaling at your product suite, let’s set up a 15-minute Google Meet next week post-Cypher to explore technical synergies.

Let me know what your post-summit calendar looks like.

Best regards,
Kunal Das
Director & CTO | AI-First Technology Leader
(isearch.xsolve@gmail.com)"""

KARAN_MSG = """Hi Karan,
Glad to connect. I was reviewing Techdataseeders’ work around structuring live web and app data for enterprise market intelligence—it directly intersects with our core engineering.

While I am operating remotely from Silchar and dialing in from our lab, we have spent the last 8 months building heavy-duty autonomous data extraction and intelligence engines:

1. Autonomous Multi-Portal Extraction: Resilient headless engines that bypass dynamic DOM walls, gate interactive form inputs, and capture real-time feeds 24/7 without human intervention.
2. AI-Driven Data Normalization & Custom APIs: Automated pipelines that turn unstructured multi-source web streams into clean, validated client schemas.
3. Joint Enterprise Solutions: Pairing Techdataseeders’ data delivery with our Agentic AI synthesis to pitch high-ticket enterprise intelligence suites together.

Since your clients need continuous, high-signal data feeds, there is strong room for us to explore a high-margin technical partnership or joint delivery.

Let’s sync for a 15-minute technical discussion early next week over Google Meet. Share your convenient time slot.

Best regards,
Kunal Das
Director & CTO
(isearch.xsolve@gmail.com)"""


def save_shot(c, name):
    shot = c.call_tool("browser_screenshot", {})
    if shot and not shot.get("isError"):
        for b in shot.get("content", []):
            if b.get("type") == "image":
                import base64
                p = EVIDENCE / name
                p.write_bytes(base64.b64decode(b["data"]))
                print(f"Saved: {p}")
                return str(p)
    return None


def send_message_to_profile(c, profile_url, msg_text, prefix):
    print(f"\n--- Processing {prefix}: {profile_url} ---")
    c.call_tool("browser_navigate", {"url": profile_url})
    time.sleep(6)
    
    # Scroll slightly down so header actions are in view
    c.call_tool("browser_execute_script", {"code": "window.scrollBy(0, 300);"})
    time.sleep(2)
    save_shot(c, f"{prefix}-01-profile.png")
    
    # Click the primary Message button
    click_msg_btn_js = """
    (() => {
        // Look for buttons with text 'Message'
        const buttons = Array.from(document.querySelectorAll('button, a'));
        const msgBtn = buttons.find(b => {
            const txt = b.innerText.trim();
            const aria = b.getAttribute('aria-label') || '';
            return txt === 'Message' || (aria.startsWith('Message ') && !b.closest('.msg-overlay-bubble-header'));
        });
        if (msgBtn) {
            msgBtn.click();
            return { ok: true, text: msgBtn.innerText };
        }
        return { ok: false, err: 'no_msg_btn' };
    })()
    """
    btn_res = c.call_tool("browser_execute_script", {"code": click_msg_btn_js})
    print(f"Message button click: {btn_res}")
    time.sleep(4)
    save_shot(c, f"{prefix}-02-modal-opened.png")
    
    # Type into the message box (whether overlay or standalone)
    paras = msg_text.split("\n\n")
    type_js = f"""
    (() => {{
        // Find contenteditable box (could be in overlay or main)
        const boxes = document.querySelectorAll('div.msg-form__contenteditable[contenteditable="true"]');
        if (boxes.length === 0) return {{ ok: false, err: 'no_box_found' }};
        const box = boxes[boxes.length - 1]; // pick the most recently opened box
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
    type_res = c.call_tool("browser_execute_script", {"code": type_js})
    print(f"Type result: {type_res}")
    time.sleep(3)
    save_shot(c, f"{prefix}-03-typed.png")
    
    # Click Send button
    send_js = """
    (() => {
        // Find send button in the active form
        const forms = document.querySelectorAll('form.msg-form');
        let sendBtn = null;
        if (forms.length > 0) {
            const form = forms[forms.length - 1];
            sendBtn = form.querySelector('button[type="submit"]') || form.querySelector('button.msg-form__send-button');
        }
        if (!sendBtn) {
            const btns = document.querySelectorAll('button.msg-form__send-button');
            sendBtn = btns[btns.length - 1];
        }
        if (sendBtn && !sendBtn.disabled) {
            sendBtn.click();
            return { ok: true };
        }
        return { ok: false, disabled: sendBtn ? sendBtn.disabled : 'not_found' };
    })()
    """
    send_res = c.call_tool("browser_execute_script", {"code": send_js})
    print(f"Send result: {send_res}")
    time.sleep(4)
    save_shot(c, f"{prefix}-04-sent-receipt.png")
    return {"btn": btn_res, "type": type_res, "send": send_res}


try:
    c.start()
    out["dakshesh"] = send_message_to_profile(c, "https://www.linkedin.com/in/daksheshbhardwaj/", DAKSHESH_MSG, "dakshesh")
    out["karan"] = send_message_to_profile(c, "https://www.linkedin.com/in/karan-v-732b95427/", KARAN_MSG, "karan")
except Exception as e:
    out["err"] = str(e)
finally:
    c.close()

p = HERE / "_send_overlay_report.json"
p.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
print(f"\nALL_SENT_REPORT: {p}")
