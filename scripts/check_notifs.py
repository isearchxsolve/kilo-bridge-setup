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
    c.call_tool("browser_navigate", {"url": "https://www.linkedin.com/notifications/"})
    time.sleep(5)
    
    shot = c.call_tool("browser_screenshot", {})
    if shot and not shot.get("isError"):
        for b in shot.get("content", []):
            if b.get("type") == "image":
                import base64
                data = base64.b64decode(b["data"])
                shot_path = EVIDENCE / "linkedin-notifications-live.png"
                shot_path.write_bytes(data)
                out["shot"] = str(shot_path)

    js = """
    (() => {
        const items = document.querySelectorAll('article.nt-card, .notification-item, .nt-item');
        return Array.from(items).slice(0, 10).map(el => el.innerText.trim());
    })()
    """
    res = c.call_tool("browser_execute_script", {"code": js})
    if res and not res.get("isError"):
        for b in res.get("content", []):
            if b.get("type") == "text":
                out["items"] = json.loads(b["text"])
except Exception as e:
    out["err"] = str(e)
finally:
    c.close()

(HERE / "_notifs.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
print("NOTIFS_DONE")
