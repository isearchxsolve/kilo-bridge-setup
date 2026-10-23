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

c = A.Agent360Client()
out = {}

ARAYEMI_RESET = """Hi Arayemi,

Apologies for the automated test snippet that misfired earlier into this thread from our testing lab. 

Looking forward to reviewing the role overview and client requirements once you share the JD. Let me know when you have it over and we can assess the mutual alignment.

Best regards,
Kunal Das
Director & CTO
isearch.xsolve@gmail.com"""


def save_shot(client, filename):
    try:
        shot = client.call_tool("browser_screenshot", {})
        if shot and not shot.get("isError"):
            for b in shot.get("content", []):
                if b.get("type") == "image":
                    data = base64.b64decode(b["data"])
                    p = EVIDENCE / filename
                    p.write_bytes(data)
                    print(f"Receipt saved: {p} ({len(data)} bytes)")
                    return str(p)
    except Exception as e:
        print(f"Error saving screenshot {filename}: {e}")
    return None


try:
    c.start()
    print("Navigating to LinkedIn Messaging...")
    c.call_tool("browser_navigate", {"url": "https://www.linkedin.com/messaging/"})
    
    # Wait for messaging list to load
    print("Waiting for messaging conversation list to render...")
    loaded = False
    for attempt in range(12):
        time.sleep(2)
        check_js = """
        (() => {
            const items = document.querySelectorAll('li.msg-conversation-listitem');
            return { count: items.length, url: window.location.href, title: document.title };
        })()
        """
        res = c.call_tool("browser_execute_script", {"code": check_js})
        print(f"Attempt {attempt+1}: {res}")
        try:
            txt = res.get("content", [{}])[0].get("text", "{}")
            data = json.loads(txt)
            if data.get("result", {}).get("count", 0) > 0:
                loaded = True
                out["items_loaded"] = data["result"]["count"]
                break
        except Exception as e:
            print("Parse err:", e)

    out["initial_inbox_shot"] = save_shot(c, "inbox-settled-state.png")

    # Step 1: Find Arayemi in the conversation list or search
    select_arayemi_js = """
    (() => {
        const items = Array.from(document.querySelectorAll('li.msg-conversation-listitem'));
        for (let i = 0; i < items.length; i++) {
            const it = items[i];
            const text = it.innerText || '';
            if (text.toLowerCase().includes('arayemi')) {
                it.scrollIntoView();
                const link = it.querySelector('a') || it;
                link.click();
                return { clicked: true, index: i, name: 'Arayemi in list' };
            }
        }
        return { clicked: false, total_items: items.length };
    })()
    """
    click_res = c.call_tool("browser_execute_script", {"code": select_arayemi_js})
    print("Select Arayemi result:", click_res)
    out["click_res"] = click_res

    # If not found directly in visible list, try searching in messaging search box
    try:
        txt = click_res.get("content", [{}])[0].get("text", "{}")
        cr = json.loads(txt).get("result", {})
    except Exception:
        cr = {}

    if not cr.get("clicked"):
        print("Arayemi not in top visible list, searching in messaging search...")
        search_js = """
        (() => {
            const searchInput = document.querySelector('input[placeholder*="Search messages"], input.msg-search-form__search-field');
            if (searchInput) {
                searchInput.focus();
                searchInput.value = 'Arayemi';
                searchInput.dispatchEvent(new Event('input', { bubbles: true }));
                searchInput.dispatchEvent(new Event('change', { bubbles: true }));
                return { searched: true };
            }
            return { searched: false };
        })()
        """
        c.call_tool("browser_execute_script", {"code": search_js})
        time.sleep(3)
        # Click first result
        click_search_res_js = """
        (() => {
            const items = Array.from(document.querySelectorAll('li.msg-conversation-listitem, .msg-search-result'));
            for (const it of items) {
                if (it.innerText.toLowerCase().includes('arayemi')) {
                    it.click();
                    const a = it.querySelector('a');
                    if (a) a.click();
                    return { clicked: true };
                }
            }
            return { clicked: false };
        })()
        """
        res_sr = c.call_tool("browser_execute_script", {"code": click_search_res_js})
        print("Search click result:", res_sr)
        out["search_click_res"] = res_sr

    time.sleep(4)

    # Step 2: Inject reset message into the active thread composer
    paras = ARAYEMI_RESET.split("\n\n")
    inject_js = f"""
    (() => {{
        const boxes = Array.from(document.querySelectorAll('div.msg-form__contenteditable[contenteditable="true"]'));
        if (boxes.length === 0) return {{ ok: false, err: 'no_box' }};
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
    res_inj = c.call_tool("browser_execute_script", {"code": inject_js})
    print("Inject reset result:", res_inj)
    out["inject_res"] = res_inj
    time.sleep(2)

    # Step 3: PRE-SEND RECEIPT
    out["presend_shot"] = save_shot(c, "arayemi-executive-reset-presend.png")

    # Step 4: Click Send
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
    res_send = c.call_tool("browser_execute_script", {"code": send_js})
    print("Send click result:", res_send)
    out["send_res"] = res_send
    time.sleep(5)

    # Step 5: POST-SEND RECEIPT
    out["postsend_shot"] = save_shot(c, "arayemi-executive-reset-postsend.png")

    # Step 6: Read thread text to confirm
    read_thread_js = """
    (() => {
        const thread = document.querySelector('.msg-thread') || document.body;
        return { text: thread.innerText.slice(0, 2500) };
    })()
    """
    res_thread = c.call_tool("browser_execute_script", {"code": read_thread_js})
    out["thread_content"] = res_thread

except Exception as e:
    out["err"] = repr(e)
    print("Exception occurred:", e)
finally:
    c.close()

p = HERE / "_arayemi_delivery_final.json"
p.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
print(f"\nFINISHED: Written to {p}")
