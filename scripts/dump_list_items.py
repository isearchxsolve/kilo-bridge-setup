import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import agent360_client as A

c = A.Agent360Client()
out = {}

try:
    c.start()
    js = """
    (() => {
        const list = document.querySelector('.msg-conversations-container__conversations-list') || document.querySelector('aside ul') || document.querySelector('ul.msg-conversations-container__conversations-list');
        const items = Array.from(document.querySelectorAll('li'));
        return items.map((li, idx) => ({
            idx,
            className: li.className,
            text: li.innerText.slice(0, 100),
            hasA: !!li.querySelector('a'),
            aHref: li.querySelector('a')?.href
        })).filter(x => x.text.includes('Dakshesh') || x.text.includes('Karan'));
    })()
    """
    out["items"] = c.call_tool("browser_execute_script", {"code": js})
except Exception as e:
    out["err"] = repr(e)
finally:
    c.close()

p = HERE / "_list_items_dump.json"
p.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
print(f"DUMPED: {p}")
