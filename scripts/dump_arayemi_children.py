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
    print("Navigating to messaging...")
    c.call_tool("browser_navigate", {"url": "https://www.linkedin.com/messaging/"})
    time.sleep(5)

    dump_children_js = """
    (() => {
        const items = Array.from(document.querySelectorAll('li.msg-conversation-listitem'));
        const it = items.find(el => el.innerText.includes('Arayemi'));
        if (!it) return { ok: false };

        const all = Array.from(it.querySelectorAll('*'));
        return {
            ok: true,
            total_elements: all.length,
            elements: all.map(el => {
                const attrs = {};
                for (let a of el.attributes) attrs[a.name] = a.value;
                return {
                    tag: el.tagName,
                    id: el.id,
                    className: el.className,
                    attrs: attrs,
                    text: el.children.length === 0 ? el.innerText : ''
                };
            })
        };
    })()
    """
    res = c.call_tool("browser_execute_script", {"code": dump_children_js})
    txt = res.get("content", [{}])[0].get("text", "{}")
    p = HERE / "_arayemi_li_dump.json"
    p.write_text(txt, encoding="utf-8")
    print("Dumped to _arayemi_li_dump.json")

except Exception as e:
    print("Error:", e)
finally:
    c.close()
