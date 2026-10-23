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
    print("Navigating to https://www.linkedin.com/messaging/ ...")
    c.call_tool("browser_navigate", {"url": "https://www.linkedin.com/messaging/"})
    
    # Wait for list
    for i in range(10):
        time.sleep(2)
        res = c.call_tool("browser_execute_script", {"code": "document.querySelectorAll('li.msg-conversation-listitem').length"})
        try:
            txt = res.get("content", [{}])[0].get("text", "{}")
            if json.loads(txt).get("result", 0) > 0:
                print(f"Conversation list ready ({i+1})")
                break
        except Exception:
            pass

    test_switch_js = """
    (() => {
        const items = Array.from(document.querySelectorAll('li.msg-conversation-listitem'));
        const it = items.find(el => el.innerText.includes('Arayemi'));
        if (!it) return { found: false, err: 'no_arayemi_item' };

        // Inspect header before click
        const getHeader = () => {
            const h = document.querySelector('.msg-title, .msg-entity-lockup__title, .msg-thread__header, .msg-title-bar__title');
            return h ? h.innerText.replace(/\\s+/g, ' ') : '';
        };

        const beforeHeader = getHeader();

        // Let's try clicking the link div, the image, and pressing Enter
        const link = it.querySelector('.msg-conversation-listitem__link');
        const img = it.querySelector('img');
        const nameEl = it.querySelector('.msg-conversation-listitem__participant-names');

        it.scrollIntoView({ block: 'center' });

        // Try method 1: click on the link div
        if (link) {
            link.focus();
            link.click();
            link.dispatchEvent(new MouseEvent('mousedown', { bubbles: true, cancelable: true }));
            link.dispatchEvent(new MouseEvent('mouseup', { bubbles: true, cancelable: true }));
            link.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));
            
            // Also dispatch Enter key
            link.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true }));
            link.dispatchEvent(new KeyboardEvent('keyup', { key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true }));
        }

        // Try method 2: if image exists, click image
        if (img) {
            img.click();
        }

        // Try method 3: click nameEl
        if (nameEl) {
            nameEl.click();
        }

        return {
            found: true,
            before_header: beforeHeader,
            link_tag: link ? link.tagName : null,
            img_tag: img ? img.tagName : null,
            name_text: nameEl ? nameEl.innerText : null
        };
    })()
    """
    res = c.call_tool("browser_execute_script", {"code": test_switch_js})
    print("Action executed:", res.get("content", [{}])[0].get("text"))
    
    # Wait for thread header to update
    for wait_step in range(6):
        time.sleep(1.5)
        check_header_js = """
        (() => {
            const headers = Array.from(document.querySelectorAll('.msg-title, .msg-entity-lockup__title, .msg-thread__header, .msg-title-bar, .msg-entity-lockup__content'));
            const texts = headers.map(h => h.innerText.replace(/\\s+/g, ' '));
            const composer = document.querySelector('div.msg-form__contenteditable[contenteditable="true"]');
            return {
                url: window.location.href,
                headers: texts,
                has_composer: !!composer
            };
        })()
        """
        res_h = c.call_tool("browser_execute_script", {"code": check_header_js})
        print(f"Wait step {wait_step+1}:", res_h.get("content", [{}])[0].get("text"))

finally:
    c.close()
