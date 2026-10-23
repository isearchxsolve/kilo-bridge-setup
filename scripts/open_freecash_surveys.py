import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("freecash", "open_surveys")
with T.session(lane) as client:
    print("Navigating to https://freecash.com/en/earn...")
    client.call_tool("browser_navigate", {"url": "https://freecash.com/en/earn"})
    time.sleep(6)

    # Scroll down to Survey Partners
    scroll_info = client._js(r"""
        (function() {
            window.scrollBy(0, 800);
            return { scrolled: true, scrollY: window.scrollY };
        })()
    """)
    time.sleep(3)

    # Find Survey Partners: CPX Research, BitLabs, etc.
    partners_info = client._js(r"""
        (function() {
            var all = Array.from(document.querySelectorAll('a, button, div, span')).filter(el => {
                var t = (el.innerText || '').toLowerCase();
                return t.includes('cpx research') || t.includes('bitlabs') || t.includes('surveys');
            }).map(el => ({
                text: el.innerText.trim().slice(0, 50),
                tag: el.tagName,
                href: el.getAttribute('href') || ''
            }));

            // Click CPX Research or Bitlabs if found
            var cpx = Array.from(document.querySelectorAll('*')).find(el => {
                var t = (el.innerText || '').toLowerCase();
                return t.includes('cpx research') || t === 'cpx';
            });
            var clickedPartner = null;
            if (cpx) {
                var clickable = cpx.closest('a') || cpx.closest('button') || cpx.closest('div[role="button"]') || cpx;
                clickable.click();
                clickedPartner = 'CPX Research';
            } else {
                var bitlabs = Array.from(document.querySelectorAll('*')).find(el => {
                    var t = (el.innerText || '').toLowerCase();
                    return t.includes('bitlabs');
                });
                if (bitlabs) {
                    var clickable = bitlabs.closest('a') || bitlabs.closest('button') || bitlabs.closest('div[role="button"]') || bitlabs;
                    clickable.click();
                    clickedPartner = 'BitLabs';
                }
            }

            return {
                url: window.location.href,
                title: document.title,
                partnersFound: partners_info.slice(0, 10),
                clickedPartner: clickedPartner
            };
        })()
    """)
    print("SURVEY PARTNERS STATE:\n", json.dumps(partners_info, indent=2))
    time.sleep(4)

    shot = lane.shot(client, "freecash_survey_partner_opened")
    print("Screenshot saved to:", shot)
    lane.row("freecash.com/en/earn", "Open Survey Partner", "Freecash", 0, "open_survey_partner", T.OK, shot, f"Clicked {partners_info.get('clickedPartner', 'none')}")
