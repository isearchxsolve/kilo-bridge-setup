r"""inspect_cpx_cards.py - Get exact data-link and attributes of CPX Research surveys.
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("timebucks", "cpx_surveys")
with T.session(lane) as client:
    print("Navigating to all_surveys...")
    client.call_tool("browser_navigate", {"url": "https://timebucks.com/publishers/index.php?pg=earn&tab=all_surveys"})
    time.sleep(3.5)

    cpx_data = client._js(r"""
        (function() {
            var cards = Array.from(document.querySelectorAll('.survey-card, div[id^="survey-"]'));
            var cpxCards = cards.filter(c => (c.getAttribute('data-provider') || '').toLowerCase().includes('cpx') || (c.innerText || '').toLowerCase().includes('cpx'));

            return cpxCards.map(c => {
                var btn = c.querySelector('.btn-start, button, a');
                return {
                    id: c.id,
                    text: c.innerText.replace(/\s+/g, ' ').trim(),
                    link: btn ? (btn.getAttribute('data-link') || btn.getAttribute('href')) : null,
                    btnClass: btn ? btn.className : null
                };
            });
        })()
    """)

    print("CPX SURVEYS EXACT DETAILS:\n", json.dumps(cpx_data, indent=2))
