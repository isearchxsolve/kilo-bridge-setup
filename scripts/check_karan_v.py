import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import agent360_client as A

EVIDENCE = HERE.parent / "evidence" / "employment-lane"

out = {}
c = A.Agent360Client()
try:
    c.start()
    
    # 1. Open LinkedIn Messaging and find Karan V
    print("Navigating to LinkedIn Messaging...")
    c.call_tool("browser_navigate", {"url": "https://www.linkedin.com/messaging/"})
    time.sleep(5)
    
    # Search for Karan V or click his thread
    js = """
    (() => {
        const items = document.querySelectorAll('li.msg-conversation-listitem');
        let karanThread = null;
        for (const li of items) {
            const nameEl = li.querySelector('.msg-conversation-listitem__participant-names');
            if (nameEl && nameEl.innerText.toLowerCase().includes('karan v')) {
                karanThread = li;
                break;
            }
        }
        if (karanThread) {
            const link = karanThread.querySelector('a');
            if (link) { link.click(); return { clicked: true }; }
        }
        return { clicked: false, total_items: items.length };
    })()
    """
    click_res = c.call_tool("browser_execute_script", {"code": js})
    out["karan_click"] = click_res
    time.sleep(4)
    
    # Read message history of current open conversation
    history_js = """
    (() => {
        const titleEl = document.querySelector('.msg-title-bar__title') || document.querySelector('.msg-entity-lockup__entity-title');
        const messages = Array.from(document.querySelectorAll('.msg-s-message-list__event, .msg-s-event-listitem')).map(el => {
            const sender = el.querySelector('.msg-s-message-group__name') || el.querySelector('.msg-s-message-group__profile-link');
            const text = el.querySelector('.msg-s-event-listitem__body') || el.querySelector('.msg-s-message-group__message-bubble');
            const time = el.querySelector('time');
            return {
                sender: sender ? sender.innerText.trim() : '',
                text: text ? text.innerText.trim() : el.innerText.trim(),
                time: time ? time.innerText.trim() : ''
            };
        });
        return {
            title: titleEl ? titleEl.innerText.trim() : '',
            messages: messages.slice(-10)
        };
    })()
    """
    hist_res = c.call_tool("browser_execute_script", {"code": history_js})
    out["karan_history"] = hist_res
    
    # Take screenshot of Karan V conversation
    shot = c.call_tool("browser_screenshot", {})
    if shot and not shot.get("content", []):
        pass
    else:
        for b in shot.get("content", []):
            if b.get("type") == "image":
                import base64
                data = base64.b64decode(b["data"])
                shot_path = EVIDENCE / "karan-v-thread.png"
                shot_path.write_bytes(data)
                out["karan_shot"] = str(shot_path)
                
except Exception as e:
    out["err"] = str(e)
finally:
    c.close()

(HERE / "_karan_v_report.json").write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
print("KARAN_REPORT_DONE")
