import sys
import json
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(HERE))
import lane_tools as T

def inspect_contacts():
    lane = T.Lane("linkedin", "inspect_high_ticket")
    with T.session(lane) as client:
        # Navigate to LinkedIn messaging
        print("Navigating to LinkedIn messaging...")
        client.call_tool("browser_navigate", {"url": "https://www.linkedin.com/messaging/"})
        time.sleep(5)
        
        # Capture recent conversation items
        convos = client._js('''
        (() => {
            const list = [];
            const items = document.querySelectorAll(".msg-conversation-listitem, [data-view-name*='conversation-list-item'], .msg-conversation-card");
            items.forEach(el => {
                const nameEl = el.querySelector(".msg-conversation-listitem__participant-names, .msg-conversation-card__participant-names, h3");
                const snippetEl = el.querySelector(".msg-conversation-card__message-snippet, .msg-conversation-listitem__message-snippet, p");
                const timeEl = el.querySelector("time, .msg-conversation-listitem__time-stamp");
                if (nameEl) {
                    list.push({
                        name: nameEl.innerText.trim(),
                        snippet: snippetEl ? snippetEl.innerText.trim() : "",
                        time: timeEl ? timeEl.innerText.trim() : ""
                    });
                }
            });
            return list;
        })()
        ''')
        print(f"Found {len(convos)} recent conversations in sidebar:")
        for c in convos[:15]:
            print(f" - {c.get('name')}: {c.get('snippet')} ({c.get('time')})")

        # Now search connections specifically for "Chetan" and "Mathew"
        print("\nChecking connections for Chetan Sangani and Mathew Joseph Elanjikal...")
        for name_query in ["Chetan Sangani", "Mathew Joseph Elanjikal", "Mathew Joseph"]:
            url = f"https://www.linkedin.com/search/results/people/?keywords={name_query.replace(' ', '%20')}&network=%5B%22F%22%5D"
            client.call_tool("browser_navigate", {"url": url})
            time.sleep(4)
            results = client._js('''
            (() => {
                const people = [];
                const cards = document.querySelectorAll(".reusable-search__result-container, .entity-result");
                cards.forEach(card => {
                    const titleEl = card.querySelector(".entity-result__title-text a, .app-aware-link");
                    const headlineEl = card.querySelector(".entity-result__primary-subtitle, .entity-result__summary");
                    const subEl = card.querySelector(".entity-result__secondary-subtitle");
                    if (titleEl) {
                        people.push({
                            name: titleEl.innerText.trim(),
                            href: titleEl.href,
                            headline: headlineEl ? headlineEl.innerText.trim() : "",
                            location: subEl ? subEl.innerText.trim() : ""
                        });
                    }
                });
                return people;
            })()
            ''')
            print(f"\nSearch for '{name_query}' returned {len(results)} 1st-degree results:")
            for p in results[:5]:
                print(f" - Name: {p['name']} | Headline: {p['headline']} | URL: {p['href']}")

inspect_contacts()
