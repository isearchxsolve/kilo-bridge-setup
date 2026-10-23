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
    
    # 1. Open messaging
    print("Navigating to LinkedIn Messaging...")
    c.call_tool("browser_navigate", {"url": "https://www.linkedin.com/messaging/"})
    time.sleep(6)
    
    out["inbox_shot"] = save_shot(c, "inbox-after-baba-send.png")
    
    # 2. Extract recent threads
    threads_js = """
    (() => {
        const items = document.querySelectorAll('li.msg-conversation-listitem');
        return Array.from(items).slice(0, 10).map((li, idx) => {
            const nameEl = li.querySelector('.msg-conversation-listitem__participant-names');
            const snipEl = li.querySelector('.msg-conversation-card__message-snippet');
            const timeEl = li.querySelector('time');
            return {
                idx: idx,
                name: nameEl ? nameEl.innerText.trim() : '',
                snippet: snipEl ? snipEl.innerText.trim().slice(0, 100) : '',
                time: timeEl ? timeEl.innerText.trim() : ''
            };
        });
    })()
    """
    th_res = c.call_tool("browser_execute_script", {"code": threads_js})
    out["threads"] = th_res
    
    # 3. Find and click Dakshesh thread
    click_dak_js = """
    (() => {
        const items = document.querySelectorAll('li.msg-conversation-listitem');
        for (const li of items) {
            if (li.innerText.toLowerCase().includes('dakshesh')) {
                const link = li.querySelector('a') || li;
                link.click();
                return { clicked: true, name: 'dakshesh' };
            }
        }
        return { clicked: false };
    })()
    """
    c.call_tool("browser_execute_script", {"code": click_dak_js})
    time.sleep(4)
    out["dakshesh_shot"] = save_shot(c, "dakshesh-baba-hand-sent.png")
    
    # Read Dakshesh thread text
    dak_read_js = """
    (() => {
        const thread = document.querySelector('.msg-thread') || document.body;
        return thread.innerText.slice(0, 2000);
    })()
    """
    out["dakshesh_text"] = c.call_tool("browser_execute_script", {"code": dak_read_js})
    
    # 4. Find and click Karan thread
    click_karan_js = """
    (() => {
        const items = document.querySelectorAll('li.msg-conversation-listitem');
        for (const li of items) {
            if (li.innerText.toLowerCase().includes('karan')) {
                const link = li.querySelector('a') || li;
                link.click();
                return { clicked: true, name: 'karan' };
            }
        }
        return { clicked: false };
    })()
    """
    c.call_tool("browser_execute_script", {"code": click_karan_js})
    time.sleep(4)
    out["karan_shot"] = save_shot(c, "karan-baba-hand-sent.png")
    
    # Read Karan thread text
    karan_read_js = """
    (() => {
        const thread = document.querySelector('.msg-thread') || document.body;
        return thread.innerText.slice(0, 2000);
    })()
    """
    out["karan_text"] = c.call_tool("browser_execute_script", {"code": karan_read_js})

except Exception as e:
    out["err"] = str(e)
finally:
    c.close()

res_path = HERE / "_baba_send_verification.json"
res_path.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
print(f"VERIFICATION_COMPLETE: {res_path}")
