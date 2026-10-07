import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import lane_tools as T

lane = T.Lane("naukri", "inspect chips")
with T.session(lane) as client:
    chips = client._js('''(() => {
        const c = document.querySelector(".chatbot_MessageContainer");
        if (!c) return "no container";
        const all = Array.from(c.querySelectorAll("*"));
        return all.map(el => ({
            tag: el.tagName,
            className: el.className,
            text: el.innerText ? el.innerText.trim() : "",
            clickable: typeof el.onclick === "function" || el.getAttribute("role") === "button" || el.tagName === "BUTTON" || el.tagName === "A" || el.tagName === "SPAN" || el.tagName === "DIV"
        })).filter(x => ["Chennai", "Hyderabad", "Kolkata", "Skip this question"].includes(x.text));
    })()''')
    print("CHIPS:\n", chips)
