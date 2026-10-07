import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import lane_tools as T

lane = T.Lane("naukri", "inspect")
with T.session(lane) as client:
    msg = client._js('''(() => {
        const c = document.querySelector(".chatbot_MessageContainer");
        if (!c) return "no chatbot container";
        return c.innerText;
    })()''')
    print("MESSAGES:\n", msg)
    submit_btn = client._js('''(() => {
        const btns = Array.from(document.querySelectorAll("button, input[type=submit], [role=button]"));
        return btns.map(b => ({
            text: (b.innerText || b.value || "").trim(),
            disabled: b.disabled,
            visible: b.offsetWidth > 0 && b.offsetHeight > 0
        })).filter(x => x.visible);
    })()''')
    print("BUTTONS:\n", submit_btn)
