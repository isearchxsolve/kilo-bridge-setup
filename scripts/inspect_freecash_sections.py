import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("freecash", "inspect_earn_sections")
with T.session(lane) as client:
    # Read current state
    info = client._js(r"""
        (function() {
            var headings = Array.from(document.querySelectorAll('h1, h2, h3, h4, h5, [class*="section-title"], [class*="SectionTitle"]')).map(h => ({
                text: h.innerText.trim(),
                top: h.getBoundingClientRect().top + window.scrollY
            }));

            // Find all partner cards or links
            var partnerCards = Array.from(document.querySelectorAll('[class*="partner"], [class*="Partner"], a[href*="partner"], [class*="provider"]')).map(el => ({
                text: el.innerText.trim().replace(/\n+/g, ' | '),
                tag: el.tagName,
                href: el.getAttribute('href') || ''
            }));

            // Let's also check for direct CPX, BitLabs, inBrain, Pollfish links or elements
            var surveyNames = ['cpx', 'bitlabs', 'inbrain', 'pollfish', 'your-surveys', 'tap', 'theorem'];
            var foundSurveyEls = [];
            document.querySelectorAll('*').forEach(el => {
                var t = (el.innerText || '').toLowerCase();
                surveyNames.forEach(name => {
                    if (t.includes(name) && el.children.length === 0) {
                        foundSurveyEls.push({
                            name: name,
                            text: el.innerText.trim(),
                            tag: el.tagName,
                            parentTag: el.parentElement.tagName
                        });
                    }
                });
            });

            return {
                headings: headings,
                partnerCards: partnerCards.slice(0, 15),
                foundSurveyEls: foundSurveyEls.slice(0, 10),
                scrollY: window.scrollY,
                docHeight: document.body.scrollHeight
            };
        })()
    """)
    print("EARN SECTIONS:\n", json.dumps(info, indent=2))
