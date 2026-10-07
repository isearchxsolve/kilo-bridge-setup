"""get_all_naukri_matches.py - extract all matched job URLs from search."""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import lane_tools as T

lane = T.Lane("naukri", "extract search matches")
skills = T.candidate_skills()

with T.session(lane) as client:
    url = "https://www.naukri.com/generative+ai+architect-jobs"
    client.call_tool("browser_navigate", {"url": url})
    time.sleep(8)
    
    tuples = client._js('''(() => {
        const rows = Array.from(document.querySelectorAll("[class*=job-tuple], [class*=srp-job], article")).slice(0, 40);
        return rows.map(r => {
            const a = r.querySelector("a.title, a[class*=title]");
            const comp = r.querySelector("a.comp-name, a[class*=comp-name], [class*=company]");
            return {
                title: a ? a.innerText.trim() : "",
                href: a ? a.href : "",
                company: comp ? comp.innerText.trim() : "",
                text: r.innerText
            };
        }).filter(x => x.title && x.href);
    })()''')
    
    matched = []
    seen = set()
    for item in tuples:
        title = item["title"]
        if title in seen:
            continue
        seen.add(title)
        score, hits = T.score_card(item["text"], skills)
        if score >= 2:
            matched.append({
                "title": title,
                "company": item["company"],
                "href": item["href"],
                "score": score,
                "hits": hits
            })
            
    print(f"FOUND {len(matched)} MATCHED JOBS ON NAUKRI:")
    for m in matched:
        print(f"  * [{m['score']} hits: {','.join(m['hits'][:4])}] {m['title']} @ {m['company']}")
        print(f"    URL: {m['href']}")
