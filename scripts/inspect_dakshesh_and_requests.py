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

try:
    c.start()
    
    # 1. Read Dakshesh message
    print("Reading Dakshesh thread...")
    dak_click_js = """
    (() => {
        const items = document.querySelectorAll('li.msg-conversation-listitem');
        for (const li of items) {
            if (li.innerText.toLowerCase().includes('dakshesh')) {
                const link = li.querySelector('a') || li;
                link.click();
                return { clicked: true };
            }
        }
        return { clicked: false };
    })()
    """
    c.call_tool("browser_execute_script", {"code": dak_click_js})
    time.sleep(3)
    
    # Take screenshot of Dakshesh reply
    shot = c.call_tool("browser_screenshot", {})
    if shot and not shot.get("isError"):
        for b in shot.get("content", []):
            if b.get("type") == "image":
                data = base64.b64decode(b["data"])
                p = EVIDENCE / "dakshesh-inbound-reply-live.png"
                p.write_bytes(data)
                out["dakshesh_shot"] = str(p)

    dak_text_js = """
    (() => {
        const thread = document.querySelector('.msg-thread') || document.body;
        return thread.innerText.slice(0, 3000);
    })()
    """
    res_dak = c.call_tool("browser_execute_script", {"code": dak_text_js})
    out["dakshesh_text"] = res_dak

    # 2. Go to notifications and find "View requests"
    print("Navigating to notifications to inspect project requests...")
    c.call_tool("browser_navigate", {"url": "https://www.linkedin.com/notifications/"})
    time.sleep(5)
    
    click_requests_js = """
    (() => {
        const links = Array.from(document.querySelectorAll('a'));
        for (const a of links) {
            if (a.innerText.includes('View requests') || a.href.includes('services')) {
                return { found: true, href: a.href, text: a.innerText };
            }
        }
        // Try finding by card text
        const articles = Array.from(document.querySelectorAll('article, li, div'));
        for (const el of articles) {
            if (el.innerText.includes('new client project requests')) {
                const a = el.querySelector('a');
                if (a) return { found: true, href: a.href, text: el.innerText.slice(0, 200) };
            }
        }
        return { found: false };
    })()
    """
    res_req = c.call_tool("browser_execute_script", {"code": click_requests_js})
    out["requests_link"] = res_req
    
    # If found, navigate to it!
    req_href = None
    if res_req and not res_req.get("isError"):
        for b in res_req.get("content", []):
            if b.get("type") == "text":
                d = json.loads(b["text"])
                if d.get("result", {}).get("found"):
                    req_href = d["result"]["href"]
    
    if req_href:
        print(f"Navigating to requests URL: {req_href}")
        c.call_tool("browser_navigate", {"url": req_href})
        time.sleep(6)
        
        shot_req = c.call_tool("browser_screenshot", {})
        if shot_req and not shot_req.get("isError"):
            for b in shot_req.get("content", []):
                if b.get("type") == "image":
                    data = base64.b64decode(b["data"])
                    p = EVIDENCE / "client-project-requests-live.png"
                    p.write_bytes(data)
                    out["requests_shot"] = str(p)
                    
        page_body_js = """
        (() => {
            return {
                url: window.location.href,
                body: document.body.innerText.slice(0, 4000)
            };
        })()
        """
        out["requests_page_data"] = c.call_tool("browser_execute_script", {"code": page_body_js})

except Exception as e:
    out["error"] = repr(e)
finally:
    try:
        c.close()
    except Exception:
        pass

out_path = HERE / "_dakshesh_and_requests.json"
out_path.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
print(f"DONE: {out_path}")
