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
    
    for i in range(10):
        time.sleep(2)
        res = c.call_tool("browser_execute_script", {"code": "document.querySelectorAll('li.msg-conversation-listitem').length"})
        try:
            txt = res.get("content", [{}])[0].get("text", "{}")
            if json.loads(txt).get("result", 0) > 0:
                print(f"Loaded on attempt {i+1}")
                break
        except Exception:
            pass

    search_data_js = """
    (() => {
        // Search in all script/code tags for Arayemi
        const tags = Array.from(document.querySelectorAll('code, script[type="application/json"]'));
        const matches = [];
        for (const t of tags) {
            if (t.innerText.includes('Arayemi')) {
                matches.push({ id: t.id, len: t.innerText.length, preview: t.innerText.slice(0, 500) });
            }
        }
        
        // Also search in document HTML for any thread URLs or URNs
        const rawMatches = document.documentElement.innerHTML.match(/2-[A-Za-z0-9+/=]{20,}/g) || [];
        
        return {
            tag_matches: matches,
            thread_id_candidates: Array.from(new Set(rawMatches)).slice(0, 20)
        };
    })()
    """
    res = c.call_tool("browser_execute_script", {"code": search_data_js})
    print("SEARCH RESULTS:")
    print(res.get("content", [{}])[0].get("text"))

except Exception as e:
    print("Error:", e)
finally:
    c.close()
