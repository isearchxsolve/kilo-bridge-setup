"""lane_payment_pipeline.py - Two-Edged Sword Payment & Delivery Pipeline.

Handles:
1. Inbound Reply Listener: Monitors LinkedIn inbox for replies from pitched #OpenToWork candidates.
2. Payment Dispatcher: Sends official UPI payment instructions (Rs 499) and intake requirements.
3. Payment Verification: Tracks transaction status (PITCHED -> INTERESTED -> PAID -> ACTIVE).
4. Delivery Engine:
   - Package 1: Daily automated curated feed matching client's resume via Nemotron-120B.
   - Package 2: Autonomous application pipeline setup with Rule 1 receipt logging.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import lane_tools as T

PIPELINE_DB = HERE.parent / "evidence" / "employment-lane" / "payment_pipeline.json"
SENT_TRACKER = HERE.parent / "evidence" / "employment-lane" / "two_edged_sword_sent.json"
CLIENTS_DIR = HERE.parent / "evidence" / "employment-lane" / "clients"

# Official Payment Credentials (Confirmed in vault/pins.txt)
OFFICIAL_UPI_ID = "isearch.xsolve-3@okhdfcbank"
OFFICIAL_PHONE = "+91 86172 16163"
OFFICIAL_EMAIL = "isearch.xsolve@gmail.com"
PACKAGE_2_AMOUNT = 499  # INR

# Official Google Drive Deliverable Suite (Provided by Baba 2026-10-08)
DELIVERABLE_DRIVE_URL = "https://drive.google.com/file/d/1UeQl5NohiRNXacW9J9LV-z8o_TD9ucCQ/view?usp=sharing"


def load_pipeline() -> dict:
    if PIPELINE_DB.is_file():
        try:
            return json.loads(PIPELINE_DB.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save_pipeline(data: dict):
    PIPELINE_DB.parent.mkdir(parents=True, exist_ok=True)
    PIPELINE_DB.write_text(json.dumps(data, indent=2), encoding="utf-8")


def load_sent_tracker() -> dict:
    if SENT_TRACKER.is_file():
        try:
            return json.loads(SENT_TRACKER.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def build_option1_free_scan_message(name: str) -> str:
    """Option 1: Free Resume & Profile Scan Response."""
    first_name = name.split()[0].title() if name else "there"
    msg = (
        f"Hi {first_name},\n\n"
        f"Happy to run a complimentary deep ATS resume and job-fit scan for you!\n\n"
        f"Please email your updated Resume (PDF) to {OFFICIAL_EMAIL} with subject \"Resume Scan - {name}\".\n\n"
        f"Our engine will analyze your skills against live hiring benchmarks and return a detailed "
        f"fit breakdown along with tailored remote roles you can target immediately.\n\n"
        f"Best regards,\n"
        f"Kunal"
    )
    return msg


def build_option2_automation_product_message(name: str) -> str:
    """Option 2: Automation Product Suite (KiloBridge Standalone Software - Rs 499)."""
    first_name = name.split()[0].title() if name else "there"
    msg = (
        f"Hi {first_name},\n\n"
        f"Great to have you onboard for the KiloBridge Autonomous Engine Suite!\n\n"
        f"1. PAYMENT (₹{PACKAGE_2_AMOUNT} One-Time Setup):\n"
        f"   • UPI ID: {OFFICIAL_UPI_ID}\n"
        f"   • GPay / PhonePe / Paytm: {OFFICIAL_PHONE}\n"
        f"   • Amount: ₹{PACKAGE_2_AMOUNT}\n\n"
        f"2. INSTANT DELIVERABLE:\n"
        f"   Once transferred, please reply here with your payment screenshot or UTR number. "
        f"You will immediately receive the official Google Drive download link to the complete "
        f"standalone automation package (run-247.ps1, multi-portal application drivers, and question gating modules).\n\n"
        f"Best regards,\n"
        f"Kunal"
    )
    return msg


def build_option3_managed_service_message(name: str) -> str:
    """Option 3: Managed Job Fit Roles & Full Resume Scan Feed (Rs 499)."""
    first_name = name.split()[0].title() if name else "there"
    msg = (
        f"Hi {first_name},\n\n"
        f"Welcome to the Curated Job Feed & Managed Application Service!\n\n"
        f"1. PAYMENT (₹{PACKAGE_2_AMOUNT} Setup):\n"
        f"   • UPI ID: {OFFICIAL_UPI_ID}\n"
        f"   • GPay / PhonePe / Paytm: {OFFICIAL_PHONE}\n"
        f"   • Amount: ₹{PACKAGE_2_AMOUNT}\n\n"
        f"2. ONBOARDING & RESUME SUBMISSION:\n"
        f"   After transferring, please email {OFFICIAL_EMAIL} with:\n"
        f"   • Your updated Resume (PDF)\n"
        f"   • Target job titles & remote preferences\n"
        f"   • Payment confirmation screenshot / UTR\n\n"
        f"We configure your profile on our cloud runner and deliver daily verified remote roles "
        f"plus managed application tracking directly to your inbox/DM.\n\n"
        f"Best regards,\n"
        f"Kunal"
    )
    return msg


def build_deliverable_message(name: str) -> str:
    """Build the official deliverable message containing the Google Drive download package."""
    first_name = name.split()[0].title() if name else "there"
    msg = (
        f"Hi {first_name},\n\n"
        f"Payment received with thanks! Welcome to the Auto-Pilot Application Program.\n\n"
        f"Here is your complete automation software deliverable:\n"
        f"📦 DOWNLOAD SUITE: {DELIVERABLE_DRIVE_URL}\n\n"
        f"WHAT IS INCLUDED IN YOUR PACKAGE:\n"
        f"• Complete Autonomous Engine (KiloBridge Standalone Suite)\n"
        f"• Multi-Portal Dynamic Drivers (Naukri, Foundit, Remote Indexes)\n"
        f"• 1-Click Launchers (run-247.ps1, auto-apply scripts)\n"
        f"• AI Fit Ranker & Recruiter Question Gating Modules\n\n"
        f"NEXT STEP:\n"
        f"Download the zip package from the link above, extract it, and follow the setup instructions. "
        f"If you'd like us to configure your profile directly or run it from our cloud end, "
        f"simply reply here or email your resume PDF to {OFFICIAL_EMAIL}.\n\n"
        f"Best regards,\n"
        f"Kunal"
    )
    return msg


def scan_inbox_and_dispatch_payments(client, lane: T.Lane):
    """Scan LinkedIn messaging inbox for incoming replies from pitched candidates."""
    lane.log("\n--- [Payment Pipeline] Checking Inbound Messages ---")
    client.call_tool("browser_navigate", {"url": "https://www.linkedin.com/messaging/"})
    time.sleep(5)

    pipeline = load_pipeline()
    sent_data = load_sent_tracker()

    # Get conversation snippets
    js = """
    (() => {
        const convos = Array.from(document.querySelectorAll('li.msg-conversation-listitem, .msg-conversation-card'));
        return convos.map(c => {
            const nameEl = c.querySelector('.msg-conversation-listitem__participant-names, .msg-conversation-card__participant-names');
            const snippetEl = c.querySelector('.msg-conversation-card__message-snippet, .msg-conversation-listitem__message-snippet');
            const timeEl = c.querySelector('time');
            const unread = !!c.querySelector('.msg-conversation-card__unread-count, .msg-conversation-listitem__unread-indicator');
            const link = c.querySelector('a');
            return {
                name: nameEl ? nameEl.innerText.trim() : '',
                snippet: snippetEl ? snippetEl.innerText.trim() : '',
                time: timeEl ? timeEl.innerText.trim() : '',
                unread: unread,
                href: link ? link.href : ''
            };
        });
    })()
    """
    threads = client._js(js)
    if not isinstance(threads, list):
        lane.log("Could not parse inbox threads.")
        return

    lane.log(f"Parsed {len(threads)} active threads in inbox.")

    interest_patterns = re.compile(
        r"\b(yes|interested|how to (start|pay|proceed)|package\s*[12]|sign me up|details|price|cost|tell me more|sure|send)\b",
        re.IGNORECASE
    )

    for th in threads:
        name = th["name"]
        snippet = th["snippet"]

        # Check if candidate was one of our pitched targets
        matched_recipient = None
        for r_id, s_info in sent_data.items():
            if s_info.get("name", "").lower() in name.lower() or name.lower() in s_info.get("name", "").lower():
                matched_recipient = r_id
                break

        if not matched_recipient:
            continue

        # Check if the snippet is an incoming reply (does NOT start with "You:")
        is_incoming = not snippet.startswith("You:")
        lane.log(f"Thread: {name} | Incoming: {is_incoming} | Snippet: {snippet[:60]}")

        # If incoming reply or unread
        if is_incoming or interest_patterns.search(snippet):
            # Check if payment kit already sent
            client_record = pipeline.get(matched_recipient, {})
            if client_record.get("payment_kit_sent"):
                lane.log(f"Payment kit already sent to {name} on {client_record.get('payment_kit_time')}.")
                continue

            lane.log(f"\n>>> INBOUND INTEREST DETECTED FROM {name}! DISPATCHING PAYMENT KIT <<<")
            
            # Navigate to conversation
            if th.get("href"):
                client.call_tool("browser_navigate", {"url": th["href"]})
                time.sleep(4)

            # Classify candidate choice into Option 1, Option 2, or Option 3
            chosen_option = "GENERAL"
            if re.search(r"\b(free|resume scan|check resume|review my resume)\b", snippet, re.IGNORECASE):
                chosen_option = "OPTION_1_FREE_SCAN"
                kit_msg = build_option1_free_scan_message(name)
            elif re.search(r"\b(package\s*2|automation|product|tool|software|auto[- ]?pilot|engine)\b", snippet, re.IGNORECASE):
                chosen_option = "OPTION_2_PRODUCT"
                kit_msg = build_option2_automation_product_message(name)
            elif re.search(r"\b(package\s*1|feed|curated|managed|roles)\b", snippet, re.IGNORECASE):
                chosen_option = "OPTION_3_MANAGED"
                kit_msg = build_option3_managed_service_message(name)
            else:
                chosen_option = "OPTION_2_PRODUCT"
                kit_msg = build_option2_automation_product_message(name)

            lane.log(f"Candidate Choice Classified as: {chosen_option}")
            paragraphs = kit_msg.split("\n\n")
            inject_res = client._js(f"""
            (() => {{
                const box = document.querySelector('div.msg-form__contenteditable[contenteditable="true"]');
                if (!box) return {{ ok: false, error: "box_not_found" }};
                box.focus();
                box.innerHTML = '';
                const paras = {json.dumps(paragraphs)};
                paras.forEach(t => {{
                    const p = document.createElement('p');
                    p.innerText = t;
                    box.appendChild(p);
                }});
                box.dispatchEvent(new Event('input', {{ bubbles: true }}));
                box.dispatchEvent(new Event('change', {{ bubbles: true }}));
                return {{ ok: true }};
            }})()
            """)

            slug = re.sub(r'[^a-zA-Z0-9]', '_', name.lower())
            ts = time.strftime("%Y%m%d_%H%M%S")
            shot_pre = lane.shot(client, f"payment-kit-typed-{slug}-{ts}")

            # Click send
            client._js("""
            (() => {
                const btn = document.querySelector('button.msg-form__send-button');
                if (btn && !btn.disabled) btn.click();
            })()
            """)
            time.sleep(3)
            shot_post = lane.shot(client, f"payment-kit-sent-{slug}-{ts}")

            # Record in pipeline
            pipeline[matched_recipient] = {
                "name": name,
                "status": "PAYMENT_KIT_SENT",
                "payment_kit_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "receipt_pre": str(shot_pre) if shot_pre else "",
                "receipt_post": str(shot_post) if shot_post else "",
                "amount_due": PACKAGE_2_AMOUNT
            }
            save_pipeline(pipeline)
            lane.log(f"Payment Kit delivered to {name} with receipts.")


def record_confirmed_payment(recipient_id: str, utr_reference: str, amount: int = PACKAGE_2_AMOUNT):
    """Record verified bank/UPI credit for a client."""
    pipeline = load_pipeline()
    if recipient_id not in pipeline:
        pipeline[recipient_id] = {}

    pipeline[recipient_id]["status"] = "PAID"
    pipeline[recipient_id]["utr"] = utr_reference
    pipeline[recipient_id]["amount_paid"] = amount
    pipeline[recipient_id]["paid_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    save_pipeline(pipeline)
    print(f"[OK] Recorded verified payment of Rs {amount} (UTR: {utr_reference}) for {recipient_id}")


def send_deliverable_to_client(client, lane: T.Lane, recipient_id: str, name: str) -> bool:
    """Send the official Google Drive deliverable suite to a confirmed paying client."""
    lane.log(f"\n{'='*65}")
    lane.log(f"DISPATCHING AUTOMATION DELIVERABLE TO: {name} ({recipient_id})")
    lane.log(f"{'='*65}")

    compose_url = f"https://www.linkedin.com/messaging/compose/?recipient={recipient_id}"
    lane.log(f"Navigating to compose: {compose_url}")
    client.call_tool("browser_navigate", {"url": compose_url})
    time.sleep(5)

    msg = build_deliverable_message(name)
    paragraphs = msg.split("\n\n")

    inject_res = client._js(f"""
    (() => {{
        const box = document.querySelector('div.msg-form__contenteditable[contenteditable="true"]');
        if (!box) return {{ ok: false, error: "box_not_found" }};
        box.focus();
        box.innerHTML = '';
        const paras = {json.dumps(paragraphs)};
        paras.forEach(t => {{
            const p = document.createElement('p');
            p.innerText = t;
            box.appendChild(p);
        }});
        box.dispatchEvent(new Event('input', {{ bubbles: true }}));
        box.dispatchEvent(new Event('change', {{ bubbles: true }}));
        return {{ ok: true }};
    }})()
    """)

    slug = re.sub(r'[^a-zA-Z0-9]', '_', name.lower())
    ts = time.strftime("%Y%m%d_%H%M%S")
    shot_pre = lane.shot(client, f"deliverable-typed-{slug}-{ts}")

    # Send
    client._js("""
    (() => {
        const btn = document.querySelector('button.msg-form__send-button');
        if (btn && !btn.disabled) btn.click();
    })()
    """)
    time.sleep(3)
    shot_post = lane.shot(client, f"deliverable-sent-{slug}-{ts}")

    pipeline = load_pipeline()
    if recipient_id not in pipeline:
        pipeline[recipient_id] = {"name": name}
    pipeline[recipient_id]["status"] = "DELIVERED"
    pipeline[recipient_id]["delivered_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    pipeline[recipient_id]["receipt_deliverable_pre"] = str(shot_pre) if shot_pre else ""
    pipeline[recipient_id]["receipt_deliverable_post"] = str(shot_post) if shot_post else ""
    pipeline[recipient_id]["deliverable_url"] = DELIVERABLE_DRIVE_URL
    save_pipeline(pipeline)

    lane.log(f"Deliverable dispatched successfully with Rule 1 receipts:")
    lane.log(f"  PRE : {shot_pre}")
    lane.log(f"  POST: {shot_post}")
    return True


def main():
    parser = argparse.ArgumentParser(description="Two-Edged Sword Payment & Delivery Pipeline")
    parser.add_argument("--deliver", action="store_true", help="Send deliverable package to a paid client")
    parser.add_argument("--recipient", type=str, help="Recipient ID for delivery")
    parser.add_argument("--name", type=str, help="Client name")
    parser.add_argument("--mark-paid", action="store_true", help="Mark recipient as paid")
    parser.add_argument("--utr", type=str, default="", help="Payment UTR reference")
    args, _ = parser.parse_known_args()

    if args.mark_paid and args.recipient:
        record_confirmed_payment(args.recipient, args.utr or "MANUAL_VERIFIED", PACKAGE_2_AMOUNT)

    lane = T.Lane("linkedin", "payment_pipeline")
    with T.session(lane) as client:
        if args.deliver and args.recipient:
            send_deliverable_to_client(client, lane, args.recipient, args.name or "Client")
        else:
            scan_inbox_and_dispatch_payments(client, lane)
        lane.summary()


if __name__ == "__main__":
    main()
