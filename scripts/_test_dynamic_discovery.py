"""_test_dynamic_discovery.py - test dynamic job discovery on Naukri."""
import json
import re
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import lane_tools as T

lane = T.Lane("naukri", "dynamic discovery test")
skills = T.candidate_skills()
queries = ["generative ai architect", "agentic ai"]

with T.session(lane) as client:
    discovered = []
    seen_urls = set()
    
    for q in queries:
        query_slug = re.sub(r"[^a-zA-Z0-9]+", "+", q.strip().lower()).strip("+")
        search_url = f"https://www.naukri.com/{query_slug}-jobs"
        print(f"\nNavigating to: {search_url}")
        client.call_tool("browser_navigate", {"url": search_url})
        time.sleep(9)
        
        cards_data = client._js('''(() => {
            const wrappers = Array.from(document.querySelectorAll('.srp-jobtuple-wrapper, div[data-job-id]'));
            const list = [];
            for (const w of wrappers) {
                const titleEl = w.querySelector('a.title, a[class*=title]');
                if (!titleEl) continue;
                const title = titleEl.innerText.trim();
                const href = titleEl.href;
                if (!title || !href) continue;
                const compEl = w.querySelector('a.comp-name, [class*=comp-name]');
                const expEl = w.querySelector('.exp, [class*=exp]');
                const locEl = w.querySelector('.loc, [class*=loc]');
                list.push({
                    title: title,
                    href: href,
                    company: compEl ? compEl.innerText.trim() : '',
                    exp: expEl ? expEl.innerText.trim() : '',
                    loc: locEl ? locEl.innerText.trim() : '',
                    text: w.innerText
                });
            }
            return list;
        })()''')
        
        if not cards_data or not isinstance(cards_data, list):
            print(f"No cards extracted for {search_url}")
            continue
            
        print(f"Extracted {len(cards_data)} raw cards for query '{q}'")
        for item in cards_data:
            href = item.get("href", "")
            if not href or href in seen_urls:
                continue
            seen_urls.add(href)
            
            score, hits = T.score_card(item.get("text", ""), skills)
            title = item.get("title", "")
            company = item.get("company", "-")
            gate = score >= 2
            
            print(f"  [{'PASS' if gate else 'SKIP'}] score={score} {title[:60]} @ {company} (hits: {','.join(hits[:4])})")
            if gate:
                discovered.append({
                    "title": title,
                    "company": company,
                    "url": href,
                    "score": score,
                    "hits": hits
                })
                
    print(f"\nTOTAL MATCHED DISCOVERED: {len(discovered)}")
    for d in discovered:
        print(f"  * [{d['score']}] {d['title']} @ {d['company']} -> {d['url']}")
