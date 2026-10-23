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
    js = """
    (() => {
        const btns = Array.from(document.querySelectorAll('a, button')).filter(el => el.innerText.trim() === 'Message');
        return btns.map(b => ({
            tag: b.tagName,
            href: b.href || '',
            className: b.className,
            outerHTML: b.outerHTML.slice(0, 300)
        }));
    })()
    """
    res = c.call_tool("browser_execute_script", {"code": js})
    print(res)
finally:
    c.close()
