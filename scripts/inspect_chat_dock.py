import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import agent360_client as A

c = A.Agent360Client()

try:
    c.start()
    print("Navigating to https://www.linkedin.com/feed/ ...")
    c.call_tool("browser_navigate", {"url": "https://www.linkedin.com/feed/"})
    time.sleep(5)

    inspect_dock_js = """
    (() => {
        const bubbles = Array.from(document.querySelectorAll('.msg-overlay-conversation-bubble, .msg-overlay-bubble-header, [data-control-name="overlay"]'));
        const forms = Array.from(document.querySelectorAll('.msg-overlay-conversation-bubble form, .msg-form'));
        return {
            bubble_count: bubbles.length,
            bubbles: bubbles.map(b => b.innerText.replace(/\\s+/g, ' ').slice(0, 100)),
            forms_count: forms.length
        };
    })()
    """
    res = c.call_tool("browser_execute_script", {"code": inspect_dock_js})
    txt = res.get("content", [{}])[0].get("text", "{}")
    print("DOCK INFO:", txt)

finally:
    c.close()
