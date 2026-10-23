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
    
    # Read the full thread text of the current active conversation (Ishwar)
    read_js = """
    (() => {
        const thread = document.querySelector('.msg-thread') || document.body;
        return {
            title: document.querySelector('.msg-title')?.innerText || '',
            text: thread.innerText.slice(0, 3000)
        };
    })()
    """
    out["ishwar_thread"] = c.call_tool("browser_execute_script", {"code": read_js})

except Exception as e:
    out["err"] = repr(e)
finally:
    c.close()

p = HERE / "_ishwar_thread_check.json"
p.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
print(f"DONE: {p}")
