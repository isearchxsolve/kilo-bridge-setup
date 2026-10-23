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
    
    # Extract recipient id from compose links or action buttons
    find_recipient_js = """
    (() => {
        // Method 1: Check compose link
        const a = document.querySelector('a[href*="/messaging/compose/"]');
        if (a) {
            const m = a.href.match(/recipient=([^&]+)/);
            if (m) return { ok: true, recipient: m[1], method: 'compose_link' };
        }
        
        // Method 2: Click Message button to trigger compose navigation
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
        print("Using current page / overlay...")
    
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
    shot_pre = save_shot(client, f"{lead_name.lower()}-presend-verified.png")
    
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
    shot_post = save_shot(client, f"{lead_name.lower()}-postsend-receipt.png")
    
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
    out["karan"] = deliver_lead(c, "https://www.linkedin.com/in/karan-v-732b95427/", KARAN_MSG, "karan")
except Exception as e:
    out["err"] = str(e)
finally:
    c.close()

res_path = HERE / "_fire_final_receipt.json"
res_path.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
print(f"\nFIRE COMPLETE: Written to {res_path}")
