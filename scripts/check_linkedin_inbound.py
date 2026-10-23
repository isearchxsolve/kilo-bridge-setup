import io
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
try:
    c.start()
    
    # 1. Check Messaging
    print("Navigating to LinkedIn Messaging...")
    c.call_tool("browser_navigate", {"url": "https://www.linkedin.com/messaging/"})
    time.sleep(6)
    
    # Take screenshot of messaging
    msg_shot = c.call_tool("browser_screenshot", {})
    if msg_shot and not msg_shot.get("isError"):
        for b in msg_shot.get("content", []):
            if b.get("type") == "image":
                import base64
                data = base64.b64decode(b["data"])
                shot_path = EVIDENCE / "linkedin-messaging-live.png"
                shot_path.write_bytes(data)
                out["messaging_screenshot"] = str(shot_path)
                print(f"Saved {shot_path}")

    # Read threads from DOM
    threads_js = """
    (() => {
        const items = document.querySelectorAll('li.msg-conversation-listitem');
        return Array.from(items).slice(0, 15).map(li => {
            const nameEl = li.querySelector('.msg-conversation-listitem__participant-names');
            const snippetEl = li.querySelector('.msg-conversation-card__message-snippet');
            const timeEl = li.querySelector('time');
            const unreadBadge = li.querySelector('.msg-conversation-card__unread-count') || li.querySelector('.msg-conversation-listitem__unread');
            return {
                name: nameEl ? nameEl.innerText.trim() : '',
                snippet: snippetEl ? snippetEl.innerText.trim() : '',
                time: timeEl ? timeEl.innerText.trim() : '',
                is_unread: !!unreadBadge
            };
        });
    })()
    """
    threads_res = c.call_tool("browser_execute_script", {"code": threads_js})
    if threads_res and not threads_res.get("isError"):
        for b in threads_res.get("content", []):
            if b.get("type") == "text":
                try:
                    out["threads"] = json.loads(b["text"])
                except Exception:
                    out["threads_raw"] = b["text"]

    # 2. Check My Network / Invitations
    print("Navigating to LinkedIn Invitations...")
    c.call_tool("browser_navigate", {"url": "https://www.linkedin.com/mynetwork/invitation-manager/"})
    time.sleep(6)

    inv_shot = c.call_tool("browser_screenshot", {})
    if inv_shot and not inv_shot.get("isError"):
        for b in inv_shot.get("content", []):
            if b.get("type") == "image":
                import base64
                data = base64.b64decode(b["data"])
                shot_path = EVIDENCE / "linkedin-invitations-live.png"
                shot_path.write_bytes(data)
                out["invitations_screenshot"] = str(shot_path)
                print(f"Saved {shot_path}")

    inv_js = """
    (() => {
        const cards = document.querySelectorAll('.invitation-card, .invitation-card__details, li.invitation-card');
        const list = Array.from(document.querySelectorAll('section, ul')).find(el => el.innerText.includes('Invitations') || el.innerText.includes('Catch up'));
        return {
            invitations_count: cards.length,
            page_text: document.body.innerText.slice(0, 3000)
        };
    })()
    """
    inv_res = c.call_tool("browser_execute_script", {"code": inv_js})
    if inv_res and not inv_res.get("isError"):
        for b in inv_res.get("content", []):
            if b.get("type") == "text":
                try:
                    out["invitations_data"] = json.loads(b["text"])
                except Exception:
                    out["invitations_raw"] = b["text"]

except Exception as e:
    out["exception"] = repr(e)
finally:
    try:
        c.close()
    except Exception:
        pass

out_path = HERE / "_linkedin_inbound_report.json"
out_path.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
print(f"REPORT_WRITTEN to {out_path}")
