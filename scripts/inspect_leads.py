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
    
    # 1. Search for Dakshesh Bhardwaj
    print("Searching Dakshesh Bhardwaj...")
    c.call_tool("browser_navigate", {"url": "https://www.linkedin.com/search/results/all/?keywords=Dakshesh%20Bhardwaj"})
    time.sleep(6)
    
    # Get profile link
    js_dak = """
    (() => {
        const links = Array.from(document.querySelectorAll('a')).filter(a => a.href.includes('/in/') && a.innerText.toLowerCase().includes('dakshesh'));
        if (links.length > 0) {
            return { href: links[0].href, text: links[0].innerText };
        }
        return { href: null, all_text: document.body.innerText.slice(0, 1000) };
    })()
    """
    dak_search = c.call_tool("browser_execute_script", {"code": js_dak})
    out["dak_search"] = dak_search
    
    dak_url = None
    if dak_search and not dak_search.get("isError"):
        for b in dak_search.get("content", []):
            if b.get("type") == "text":
                try:
                    data = json.loads(b["text"])
                    dak_url = data.get("href")
                except Exception:
                    pass

    if dak_url:
        print(f"Navigating to Dakshesh profile: {dak_url}")
        c.call_tool("browser_navigate", {"url": dak_url})
        time.sleep(6)
        
        # Screenshot profile
        shot = c.call_tool("browser_screenshot", {})
        if shot and not shot.get("isError"):
            for b in shot.get("content", []):
                if b.get("type") == "image":
                    import base64
                    p = EVIDENCE / "dakshesh-profile.png"
                    p.write_bytes(base64.b64decode(b["data"]))
                    out["dak_shot"] = str(p)

        # Scrape profile text
        prof_js = """
        (() => {
            return {
                title: document.title,
                headline: document.querySelector('.text-body-medium') ? document.querySelector('.text-body-medium').innerText : '',
                about: document.querySelector('#about ~ div') ? document.querySelector('#about ~ div').innerText : '',
                experience: document.querySelector('#experience ~ div') ? document.querySelector('#experience ~ div').innerText : '',
                full_body: document.body.innerText.slice(0, 4000)
            };
        })()
        """
        out["dak_profile"] = c.call_tool("browser_execute_script", {"code": prof_js})

    # 2. Search for Karan V
    print("Searching Karan V...")
    c.call_tool("browser_navigate", {"url": "https://www.linkedin.com/search/results/all/?keywords=Karan%20V"})
    time.sleep(6)
    
    js_karan = """
    (() => {
        const links = Array.from(document.querySelectorAll('a')).filter(a => a.href.includes('/in/') && a.innerText.toLowerCase().includes('karan'));
        return {
            links: links.slice(0, 5).map(l => ({ href: l.href, text: l.innerText.slice(0, 80) })),
            page_text: document.body.innerText.slice(0, 2000)
        };
    })()
    """
    out["karan_search"] = c.call_tool("browser_execute_script", {"code": js_karan})

except Exception as e:
    out["err"] = str(e)
finally:
    c.close()

(HERE / "_lead_dna_report.json").write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
print("LEAD_DNA_DONE")
