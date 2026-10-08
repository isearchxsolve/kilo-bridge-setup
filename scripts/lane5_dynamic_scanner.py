import sys, time, json, re
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import lane_tools as T
import lane_two_edged_sword as TES

def process_candidate_profile(client, lane: T.Lane, profile_url: str):
    # AVEEK HARD BLOCK LAW (Baba 2026-10-08: High-ticket client, SGD 5,250 / Rs 3.3L deal)
    if "aveek" in profile_url.lower():
        lane.log("CRITICAL HARD BLOCK: Aveek Sengupta profile URL detected! Immediate abort.")
        return False

    lane.log(f"--- 1. Profile Scanning: {profile_url} ---")
    client.call_tool("browser_navigate", {"url": profile_url})
    time.sleep(5)
    
    # Extract profile details & compose link
    details = client._js("""
    (() => {
        const titleEl = document.querySelector('h1');
        const name = titleEl ? titleEl.innerText.trim() : '';
        
        // Headline
        const headlineEl = document.querySelector('div.text-body-medium') || document.querySelector('.pv-text-details__left-panel div');
        const headline = headlineEl ? headlineEl.innerText.trim() : '';
        
        // About / Experience text snippets
        const bodyText = document.body.innerText.slice(0, 3000);
        
        // Direct compose link or button
        const a = document.querySelector('a[href*="/messaging/compose/"]');
        let recipientId = null;
        if (a) {
            const m = a.href.match(/recipient=([^&]+)/);
            if (m) recipientId = m[1];
        }
        
        return {
            name: name,
            headline: headline,
            recipient_id: recipientId,
            bodySnippet: bodyText.slice(0, 800)
        };
    })()
    """)
    
    lane.log(f"Scanned Profile Data: Name={details.get('name')} | Recipient={details.get('recipient_id')}")
    lane.log(f"Headline: {details.get('headline')}")
    
    name = details.get("name") or "Candidate"
    headline = details.get("headline") or "Professional"

    # AVEEK & VIP HARD BLOCK CHECK
    if "aveek" in name.lower() or "sengupta" in name.lower() or "aveek" in headline.lower():
        lane.log("CRITICAL HARD BLOCK: Aveek Sengupta detected! Immediate abort.")
        return False

    shielded, reason = TES.is_shielded_contact(name, headline, profile_url)
    if shielded:
        lane.log(f"SHIELD EXCLUSION: Contact {name} is a shielded VIP/client ({reason}). Aborting.")
        return False

    recipient_id = details.get("recipient_id")
    
    if not recipient_id:
        # Click Message button to trigger compose / get recipient
        lane.log("Clicking Message button to reveal recipient...")
        btn_res = client._js("""
        (() => {
            const btns = Array.from(document.querySelectorAll('button'));
            const msgBtn = btns.find(b => b.innerText.trim() === 'Message' || b.getAttribute('aria-label')?.includes('Message'));
            if (msgBtn) { msgBtn.click(); return { clicked: true }; }
            return { clicked: false };
        })()
        """)
        time.sleep(3)
        recipient_id = client._js("""
        (() => {
            const u = window.location.href;
            const m = u.match(/recipient=([^&]+)/);
            if (m) return m[1];
            const a = document.querySelector('a[href*="/messaging/compose/"]');
            if (a) {
                const m2 = a.href.match(/recipient=([^&]+)/);
                if (m2) return m2[1];
            }
            return null;
        })()
        """)
        lane.log(f"Recipient ID after button click: {recipient_id}")
        
    if not recipient_id:
        lane.log(f"Could not resolve recipient ID for {name}. Marking blocked.")
        return False
        
    # 2. Extract keywords from headline
    clean_headline = details.get("headline", "")
    keywords = [k.strip() for k in re.split(r"[|•·,/]+", clean_headline) if len(k.strip()) > 2]
    if not keywords:
        keywords = ["operations", "specialist", "management"]
        
    lane.log(f"--- 2. Applying Fit Roles using Nemotron-120B for: {keywords} ---")
    jobs = TES.find_matched_jobs(
        keywords=keywords,
        candidate_name=name,
        domain_summary=clean_headline[:100],
        target_exp=5,
        limit=3
    )
    
    lane.log(f"Nemotron Selected {len(jobs)} Roles:")
    for j in jobs:
        lane.log(f"  * {j['title']} @ {j['company']}")
        
    # 3. Deliver Double-Edged Sword Pitch
    lane.log(f"--- 3. Delivering Double-Edged Sword Pitch to {name} ---")
    return TES.deliver_two_edged_sword_pitch(
        client=client,
        lane=lane,
        recipient_id=recipient_id,
        name=name,
        domain_summary=clean_headline[:100],
        keywords=keywords
    )

if __name__ == "__main__":
    lane = T.Lane("linkedin", "dynamic_two_edged_sword")
    with T.session(lane) as client:
        # Process Divya Sharma
        process_candidate_profile(client, lane, "https://www.linkedin.com/in/divya-sharma-35b7a5274/")
        lane.summary()
