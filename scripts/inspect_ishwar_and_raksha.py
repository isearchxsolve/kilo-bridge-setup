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
    
    # --- 1. INSPECT ISHWAR SINGH PROPOSAL FORM ---
    print("Navigating to LinkedIn Service Marketplace requests...")
    c.call_tool("browser_navigate", {"url": "https://www.linkedin.com/service-marketplace/provider/requests/"})
    time.sleep(6)
    
    out["marketplace_shot"] = save_shot(c, "ishwar-marketplace-overview.png")
    
    # Click Submit proposal for Ishwar Singh
    click_submit_js = """
    (() => {
        const btns = Array.from(document.querySelectorAll('button, a'));
        const submitBtn = btns.find(b => b.innerText.trim() === 'Submit proposal');
        if (submitBtn) {
            submitBtn.click();
            return { clicked: true, text: submitBtn.innerText };
        }
        return { clicked: false };
    })()
    """
    res_click = c.call_tool("browser_execute_script", {"code": click_submit_js})
    out["submit_click"] = res_click
    time.sleep(4)
    
    out["proposal_modal_shot"] = save_shot(c, "ishwar-proposal-modal-live.png")
    
    # Inspect modal DOM fields
    modal_fields_js = """
    (() => {
        const modal = document.querySelector('.artdeco-modal, [role="dialog"], form') || document.body;
        const inputs = Array.from(modal.querySelectorAll('input, textarea, select')).map(el => ({
            tag: el.tagName,
            type: el.type,
            name: el.name,
            id: el.id,
            placeholder: el.placeholder,
            value: el.value,
            label: el.closest('label')?.innerText || el.getAttribute('aria-label') || ''
        }));
        return {
            modal_text: modal.innerText.slice(0, 3000),
            inputs: inputs
        };
    })()
    """
    out["modal_fields"] = c.call_tool("browser_execute_script", {"code": modal_fields_js})

    # Close modal if open so we don't block
    close_modal_js = """
    (() => {
        const dismiss = document.querySelector('button[aria-label="Dismiss"], button.artdeco-modal__dismiss');
        if (dismiss) {
            dismiss.click();
            return { closed: true };
        }
        return { closed: false };
    })()
    """
    c.call_tool("browser_execute_script", {"code": close_modal_js})
    time.sleep(2)

    # --- 2. FIND RAKSHA PAL IN MESSAGING ---
    print("Navigating to LinkedIn Messaging to locate Raksha Pal...")
    c.call_tool("browser_navigate", {"url": "https://www.linkedin.com/messaging/"})
    time.sleep(5)
    
    # Search for Raksha in the messaging search bar
    search_raksha_js = """
    (() => {
        const searchInput = document.querySelector('input.msg-search-form__search-field, input[placeholder*="Search"]');
        if (searchInput) {
            searchInput.focus();
            searchInput.value = 'Raksha Pal';
            searchInput.dispatchEvent(new Event('input', { bubbles: true }));
            searchInput.dispatchEvent(new Event('change', { bubbles: true }));
            return { ok: true, value: searchInput.value };
        }
        return { ok: false };
    })()
    """
    out["search_raksha"] = c.call_tool("browser_execute_script", {"code": search_raksha_js})
    time.sleep(4)
    
    out["raksha_search_shot"] = save_shot(c, "raksha-pal-search-live.png")
    
    # Click Raksha from search results if present
    click_raksha_search_js = """
    (() => {
        const items = Array.from(document.querySelectorAll('li, div, a')).filter(el => el.innerText && el.innerText.includes('Raksha Pal'));
        for (const it of items) {
            const link = it.closest('li') || it.closest('a') || it;
            link.click();
            return { clicked: true, text: it.innerText.slice(0, 150) };
        }
        return { clicked: false };
    })()
    """
    out["click_raksha"] = c.call_tool("browser_execute_script", {"code": click_raksha_search_js})
    time.sleep(4)
    
    out["raksha_convo_shot"] = save_shot(c, "raksha-pal-convo-full.png")
    
    read_raksha_js = """
    (() => {
        const thread = document.querySelector('.msg-thread') || document.querySelector('.msg-conversations-container') || document.body;
        return thread.innerText.slice(0, 4000);
    })()
    """
    out["raksha_text"] = c.call_tool("browser_execute_script", {"code": read_raksha_js})

except Exception as e:
    out["err"] = repr(e)
finally:
    c.close()

res_path = HERE / "_ishwar_and_raksha_inspection.json"
res_path.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
print(f"INSPECTION COMPLETE: {res_path}")
