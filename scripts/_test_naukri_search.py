"""test_naukri_search.py - search Naukri for Generative AI Architect and score cards."""
import sys
import time
from pathlib import Path
from urllib.parse import quote_plus

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import lane_tools as T

query = "generative ai architect"
url = f"https://www.naukri.com/{quote_plus(query)}-jobs"

lane = T.Lane("naukri", f"search: {query}")
skills = T.candidate_skills()

with T.session(lane) as client:
    print("Navigating to:", url)
    client.call_tool("browser_navigate", {"url": url})
    time.sleep(10)
    
    shot = lane.shot(client, "45-naukri-search-" + time.strftime("%Y%m%d-%H%M%S"))
    cards = T.read_cards(client, "naukri", limit=30)
    print("Cards selector:", cards["selector"], "count:", cards["n"])
    
    matched = []
    for i, c in enumerate(cards["cards"]):
        title = c.get("title")
        score, hits = T.score_card(c.get("text"), skills)
        gate = score >= 2
        print(f"[{i+1:02d}] score={score} {'PASS' if gate else 'skip'} {title[:60]} (hits: {','.join(hits[:5])})")
        if gate:
            matched.append((title, c.get("href"), score, hits))
            
    print(f"\nTotal evaluated: {len(cards['cards'])}, Total matched: {len(matched)}")
