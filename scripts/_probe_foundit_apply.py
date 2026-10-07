import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import lane_tools as T

lane = T.Lane("foundit", "probe apply")
with T.session(lane) as client:
    cards = client._js('''(() => {
        const cards = Array.from(document.querySelectorAll("[class*=jobCard]")).slice(0, 5);
        return cards.map(c => ({
            title: (c.querySelector("h3, a[href*='job']") || {}).innerText || c.innerText.split('\\n')[0],
            buttons: Array.from(c.querySelectorAll("button, a")).map(b => ({
                text: b.innerText.trim(),
                href: b.getAttribute('href'),
                tag: b.tagName
            })).filter(x => x.text)
        }));
    })()''')
    print("Foundit cards:", cards)
