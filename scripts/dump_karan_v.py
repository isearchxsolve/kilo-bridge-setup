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
    c.call_tool("browser_navigate", {"url": "https://www.linkedin.com/messaging/"})
    time.sleep(5)
    
    # Click 9th item (index 8) which is Karan V
    click_js = """
    (() => {
        const items = document.querySelectorAll('li.msg-conversation-listitem');
        for (let i = 0; i < items.length; i++) {
            const nameEl = items[i].querySelector('.msg-conversation-listitem__participant-names');
            const nameText = nameEl ? nameEl.innerText.trim() : '';
            if (nameText.toLowerCase().includes('karan')) {
                const link = items[i].querySelector('a') || items[i];
                link.click();
                return { clicked: true, index: i, name: nameText };
            }
        }
        // Fallback: click index 8
        if (items.length > 8) {
            const link = items[8].querySelector('a') || items[8];
            link.click();
            return { clicked: true, index: 8, fallback: true };
        }
        return { clicked: false, count: items.length };
    })()
    """
    out["click"] = c.call_tool("browser_execute_script", {"code": click_js})
    time.sleep(5)
    
    # Read entire conversation text
    read_js = """
    (() => {
        const title = document.querySelector('.msg-title-bar__title, .msg-entity-lockup__entity-title');
        const bubbles = Array.from(document.querySelectorAll('.msg-s-message-list__event, .msg-s-event-listitem, .msg-s-message-group')).map(el => el.innerText.trim());
        return {
            title: title ? title.innerText.trim() : '',
            all_text: document.querySelector('.msg-thread') ? document.querySelector('.msg-thread').innerText : document.body.innerText,
            bubbles: bubbles
        };
    })()
    """
    out["conversation"] = c.call_tool("browser_execute_script", {"code": read_js})
    
    # Screenshot
    shot = c.call_tool("browser_screenshot", {})
    if shot and not shot.get("isError"):
        for b in shot.get("content", []):
            if b.get("type") == "image":
                import base64
                data = base64.b64decode(b["data"])
                p = EVIDENCE / "karan-v-convo-full.png"
                p.write_bytes(data)
                out["shot"] = str(p)

except Exception as e:
    out["err"] = str(e)
finally:
    c.close()

(HERE / "_karan_full_dump.json").write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
print("FULL_DUMP_DONE")
