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
                print(f"Saved receipt: {p}")
                return str(p)
    return None


try:
    c.start()
    
    # ==========================================
    # 1. DAKSHESH BHARDWAJ: ACCEPT & SEND
    # ==========================================
    print("--- STEP 1: Dakshesh Bhardwaj ---")
    c.call_tool("browser_navigate", {"url": "https://www.linkedin.com/mynetwork/invitation-manager/"})
    time.sleep(6)
    out["dakshesh_pre_shot"] = save_shot(c, "dakshesh-pre-accept-20261008.png")

    # Click Accept button on invitation card
    accept_js = """
    (() => {
        const buttons = Array.from(document.querySelectorAll('button'));
        const acceptBtn = buttons.find(b => b.innerText.trim() === 'Accept' || b.getAttribute('aria-label')?.includes('Accept Dakshesh'));
        if (acceptBtn) {
            acceptBtn.click();
            return { ok: true, text: acceptBtn.innerText };
        }
        return { ok: false, err: "accept_not_found" };
    })()
    """
    accept_res = c.call_tool("browser_execute_script", {"code": accept_js})
    out["dakshesh_accept_res"] = accept_res
    print(f"Accept result: {accept_res}")
    time.sleep(5)
    out["dakshesh_accepted_shot"] = save_shot(c, "dakshesh-post-accept-20261008.png")

    # Navigate to Dakshesh's profile to open Message box
    print("Navigating to Dakshesh profile to message...")
    c.call_tool("browser_navigate", {"url": "https://www.linkedin.com/in/daksheshbhardwaj/"})
    time.sleep(6)

    # Click Message button on profile
    open_msg_js = """
    (() => {
        const buttons = Array.from(document.querySelectorAll('button, a'));
        const msgBtn = buttons.find(b => b.innerText.trim() === 'Message' || b.getAttribute('aria-label')?.includes('Message Dakshesh'));
        if (msgBtn) {
            msgBtn.click();
            return { ok: true, text: msgBtn.innerText };
        }
        return { ok: false, err: "msg_btn_not_found" };
    })()
    """
    msg_btn_res = c.call_tool("browser_execute_script", {"code": open_msg_js})
    out["dakshesh_open_msg_res"] = msg_btn_res
    time.sleep(4)

    # Type Dakshesh message
    paras_dak = DAKSHESH_MSG.split("\n\n")
    type_dak_js = f"""
    (() => {{
        const box = document.querySelector('div.msg-form__contenteditable[contenteditable="true"]');
        if (!box) return {{ ok: false, err: "box_not_found" }};
        box.focus();
        box.innerHTML = '';
        const paras = {json.dumps(paras_dak)};
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
    type_res = c.call_tool("browser_execute_script", {"code": type_dak_js})
    out["dakshesh_type_res"] = type_res
    time.sleep(2)
    out["dakshesh_typed_shot"] = save_shot(c, "dakshesh-typed-20261008.png")

    # Send Dakshesh message
    send_dak_js = """
    (() => {
        const form = document.querySelector('form.msg-form');
        const sendBtn = form ? form.querySelector('button[type="submit"]') : document.querySelector('button.msg-form__send-button');
        if (sendBtn && !sendBtn.disabled) {
            sendBtn.click();
            return { ok: true };
        }
        return { ok: false, err: "send_btn_disabled_or_not_found" };
    })()
    """
    send_dak_res = c.call_tool("browser_execute_script", {"code": send_dak_js})
    out["dakshesh_send_res"] = send_dak_res
    print(f"Dakshesh send result: {send_dak_res}")
    time.sleep(4)
    out["dakshesh_sent_shot"] = save_shot(c, "dakshesh-sent-receipt-20261008.png")

    # ==========================================
    # 2. KARAN V: NAVIGATE & SEND
    # ==========================================
    print("--- STEP 2: Karan V ---")
    c.call_tool("browser_navigate", {"url": "https://www.linkedin.com/in/karan-v-732b95427/"})
    time.sleep(6)
    out["karan_profile_shot"] = save_shot(c, "karan-v-profile-pre-20261008.png")

    # Click Message button on profile
    open_karan_msg_js = """
    (() => {
        const buttons = Array.from(document.querySelectorAll('button, a'));
        const msgBtn = buttons.find(b => b.innerText.trim() === 'Message' || b.getAttribute('aria-label')?.includes('Message Karan'));
        if (msgBtn) {
            msgBtn.click();
            return { ok: true, text: msgBtn.innerText };
        }
        return { ok: false, err: "msg_btn_not_found" };
    })()
    """
    karan_btn_res = c.call_tool("browser_execute_script", {"code": open_karan_msg_js})
    out["karan_open_msg_res"] = karan_btn_res
    time.sleep(4)

    # Type Karan message
    paras_karan = KARAN_MSG.split("\n\n")
    type_karan_js = f"""
    (() => {{
        const box = document.querySelector('div.msg-form__contenteditable[contenteditable="true"]');
        if (!box) return {{ ok: false, err: "box_not_found" }};
        box.focus();
        box.innerHTML = '';
        const paras = {json.dumps(paras_karan)};
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
    type_k_res = c.call_tool("browser_execute_script", {"code": type_karan_js})
    out["karan_type_res"] = type_k_res
    time.sleep(2)
    out["karan_typed_shot"] = save_shot(c, "karan-v-typed-20261008.png")

    # Send Karan message
    send_karan_js = """
    (() => {
        const form = document.querySelector('form.msg-form');
        const sendBtn = form ? form.querySelector('button[type="submit"]') : document.querySelector('button.msg-form__send-button');
        if (sendBtn && !sendBtn.disabled) {
            sendBtn.click();
            return { ok: true };
        }
        return { ok: false, err: "send_btn_disabled_or_not_found" };
    })()
    """
    send_k_res = c.call_tool("browser_execute_script", {"code": send_karan_js})
    out["karan_send_res"] = send_k_res
    print(f"Karan send result: {send_k_res}")
    time.sleep(4)
    out["karan_sent_shot"] = save_shot(c, "karan-v-sent-receipt-20261008.png")

except Exception as e:
    out["err"] = str(e)
finally:
    c.close()

report_path = HERE / "_fire_report.json"
report_path.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
print(f"FIRE_EXECUTION_COMPLETE: written to {report_path}")
