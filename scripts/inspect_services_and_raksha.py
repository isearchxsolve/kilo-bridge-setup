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

out = {
    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "threads_inspected": {},
    "notifications": {},
    "services_page": {}
}

c = A.Agent360Client()

def save_shot(client, filename):
    try:
        shot = client.call_tool("browser_screenshot", {})
        if shot and not shot.get("isError"):
            for b in shot.get("content", []):
                if b.get("type") == "image":
                    data = base64.b64decode(b["data"])
                    p = EVIDENCE / filename
                    p.write_bytes(data)
                    print(f"Receipt saved: {p}")
                    return str(p)
    except Exception as e:
        print(f"Shot error {filename}: {e}")
    return None

try:
    c.start()
    
    # --- 1. OPEN MESSAGING ---
    print("Navigating to LinkedIn Messaging...")
    c.call_tool("browser_navigate", {"url": "https://www.linkedin.com/messaging/"})
    time.sleep(5)
    out["messaging_overview_shot"] = save_shot(c, "services-messaging-overview.png")
    
    # --- 2. INSPECT RAKSHA PAL ---
    print("Searching/Opening Raksha Pal thread...")
    raksha_js = """
    (() => {
        const items = document.querySelectorAll('li.msg-conversation-listitem');
        for (const li of items) {
            if (li.innerText.toLowerCase().includes('raksha')) {
                const link = li.querySelector('a') || li;
                link.click();
                return { clicked: true, text: li.innerText.slice(0, 200) };
            }
        }
        return { clicked: false };
    })()
    """
    res_raksha = c.call_tool("browser_execute_script", {"code": raksha_js})
    time.sleep(3)
    out["threads_inspected"]["raksha_click"] = res_raksha
    out["threads_inspected"]["raksha_shot"] = save_shot(c, "raksha-pal-thread-live.png")
    
    read_thread_js = """
    (() => {
        const thread = document.querySelector('.msg-thread') || document.querySelector('.msg-conversations-container') || document.body;
        return thread.innerText.slice(0, 3000);
    })()
    """
    out["threads_inspected"]["raksha_content"] = c.call_tool("browser_execute_script", {"code": read_thread_js})
    
    # --- 3. INSPECT ABHISHEK DHANANI ---
    print("Searching/Opening Abhishek Dhanani thread...")
    abhishek_js = """
    (() => {
        const items = document.querySelectorAll('li.msg-conversation-listitem');
        for (const li of items) {
            if (li.innerText.toLowerCase().includes('abhishek dhanani') || li.innerText.toLowerCase().includes('abhishek')) {
                const link = li.querySelector('a') || li;
                link.click();
                return { clicked: true, text: li.innerText.slice(0, 200) };
            }
        }
        return { clicked: false };
    })()
    """
    res_abhishek = c.call_tool("browser_execute_script", {"code": abhishek_js})
    time.sleep(3)
    out["threads_inspected"]["abhishek_click"] = res_abhishek
    out["threads_inspected"]["abhishek_shot"] = save_shot(c, "abhishek-dhanani-thread-live.png")
    out["threads_inspected"]["abhishek_content"] = c.call_tool("browser_execute_script", {"code": read_thread_js})

    # --- 4. CHECK NOTIFICATIONS (The 4 new client project requests) ---
    print("Navigating to LinkedIn Notifications...")
    c.call_tool("browser_navigate", {"url": "https://www.linkedin.com/notifications/"})
    time.sleep(5)
    out["notifications"]["shot"] = save_shot(c, "linkedin-notifications-live.png")
    
    notifs_read_js = """
    (() => {
        const notifCards = document.querySelectorAll('article.nt-card, .nt-card__content, .notifications-card');
        const notifs = [];
        notifCards.forEach(c => {
            const text = c.innerText.trim();
            const link = c.querySelector('a')?.href || '';
            notifs.push({ text: text.slice(0, 300), link: link });
        });
        return {
            count: notifs.length,
            items: notifs.slice(0, 15),
            full_body_snippet: document.body.innerText.slice(0, 2000)
        };
    })()
    """
    out["notifications"]["data"] = c.call_tool("browser_execute_script", {"code": notifs_read_js})

    # --- 5. CHECK SERVICES / PROJECTS PAGE ---
    print("Navigating to LinkedIn Services Manage / Projects...")
    c.call_tool("browser_navigate", {"url": "https://www.linkedin.com/services/manage/projects/"})
    time.sleep(5)
    out["services_page"]["shot"] = save_shot(c, "linkedin-services-projects-live.png")
    
    services_read_js = """
    (() => {
        return {
            url: window.location.href,
            body: document.body.innerText.slice(0, 3000)
        };
    })()
    """
    out["services_page"]["content"] = c.call_tool("browser_execute_script", {"code": services_read_js})

except Exception as e:
    out["error"] = repr(e)
finally:
    try:
        c.close()
    except Exception:
        pass

rep_file = HERE / "_services_leads_report.json"
rep_file.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
print(f"REPORT_WRITTEN to {rep_file}")
