r"""inspect_one_survey_card.py - Inspect HTML and click action for survey card.
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("timebucks", "survey_card_detail")
with T.session(lane) as client:
    print("Navigating to all_surveys...")
    client.call_tool("browser_navigate", {"url": "https://timebucks.com/publishers/index.php?pg=earn&tab=all_surveys"})
    time.sleep(3.5)

    card_info = client._js(r"""
        (function() {
            var cards = Array.from(document.querySelectorAll('*')).filter(el => {
                var t = (el.innerText || '').trim();
                var r = el.getBoundingClientRect();
                return (r.width > 50 && r.height > 50 && t.startsWith('$') && t.includes('min') && t.length < 50);
            });

            if (cards.length === 0) return { error: 'No individual cards found' };

            var firstCard = cards[0];
            var btn = firstCard.querySelector('button, a, input') || firstCard;

            return {
                cardText: firstCard.innerText.replace(/\s+/g, ' ').trim(),
                cardTag: firstCard.tagName,
                cardHtml: firstCard.outerHTML.slice(0, 500),
                btnTag: btn.tagName,
                btnHtml: btn.outerHTML.slice(0, 300),
                allCardsCount: cards.length,
                allCardsText: cards.slice(0, 10).map(c => c.innerText.replace(/\s+/g, ' ').trim())
            };
        })()
    """)

    print("SURVEY CARD DETAIL:\n", json.dumps(card_info, indent=2))
