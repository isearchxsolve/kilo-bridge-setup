r"""inspect_cpx_bitlabs.py - Filter by CPX Research and Bitlabs on all_surveys tab.
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("timebucks", "cpx_bitlabs")
with T.session(lane) as client:
    print("Navigating to all_surveys...")
    client.call_tool("browser_navigate", {"url": "https://timebucks.com/publishers/index.php?pg=earn&tab=all_surveys"})
    time.sleep(3.5)

    # Filter by CPX Research
    res = client._js(r"""
        (function() {
            var cards = Array.from(document.querySelectorAll('.survey-card, div[id^="survey-"]'));
            var cpxCards = cards.filter(c => (c.getAttribute('data-provider') || '').toLowerCase().includes('cpx') || (c.innerText || '').toLowerCase().includes('cpx'));
            var bitlabsCards = cards.filter(c => (c.getAttribute('data-provider') || '').toLowerCase().includes('bitlab') || (c.innerText || '').toLowerCase().includes('bitlab'));
            var cintCards = cards.filter(c => (c.getAttribute('data-provider') || '').toLowerCase().includes('cint') || (c.innerText || '').toLowerCase().includes('cint'));

            return {
                totalCards: cards.length,
                cpxCount: cpxCards.length,
                bitlabsCount: bitlabsCards.length,
                cintCount: cintCards.length,
                cpxSample: cpxCards.slice(0, 5).map(c => c.innerText.replace(/\s+/g, ' ').trim()),
                bitlabsSample: bitlabsCards.slice(0, 5).map(c => c.innerText.replace(/\s+/g, ' ').trim()),
                cintSample: cintCards.slice(0, 5).map(c => c.innerText.replace(/\s+/g, ' ').trim())
            };
        })()
    """)

    print("PROVIDER BREAKDOWN:\n", json.dumps(res, indent=2))
