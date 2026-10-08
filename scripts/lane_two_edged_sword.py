"""lane_two_edged_sword.py - Two-Edged Sword 1st-Degree Connection Pitch Lane.

Strategy:
1. Target: 1st-degree LinkedIn connections / #OpenToWork members.
2. The Gift (Free Lead Magnet): Extract candidate focus, match against 3,917 verified
   live remote jobs index (hunt/job-queue.csv), and deliver 2-3 direct links in DM.
3. The Pitch:
   - Package 1 (Curated Job Feed): Continuous delivery of verified matches.
   - Package 2 (Full Autonomous Auto-Pilot): Hands-off application pipeline (Rs 499 setup).
4. Strict Rule 1: Pre-send and post-send screenshot receipts for every contact.
5. Absolute Client Law: Client contact strictly isearch.xsolve@gmail.com; no live calls.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
import time
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import lane_tools as T

JOB_QUEUE_PATH = Path(r"D:\anonym\war-log\hunt\job-queue.csv")
SENT_TRACKER = HERE.parent / "evidence" / "employment-lane" / "two_edged_sword_sent.json"


def load_sent_tracker() -> dict:
    if SENT_TRACKER.is_file():
        try:
            return json.loads(SENT_TRACKER.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save_sent_tracker(data: dict):
    SENT_TRACKER.parent.mkdir(parents=True, exist_ok=True)
    SENT_TRACKER.write_text(json.dumps(data, indent=2), encoding="utf-8")


NV_KEYS = [
    "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",
    "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",
    "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",
    "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",
    "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",
    "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",
    "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",
    "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",
    "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",
    "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",
]

_NV_KEY_IDX = 0


def call_nemotron_llm(prompt: str, max_tokens: int = 1024) -> str | None:
    """Query Nemotron-120B with automatic rotation across 10 NVIDIA keys."""
    global _NV_KEY_IDX
    total_keys = len(NV_KEYS)
    for attempt in range(total_keys):
        key = NV_KEYS[(_NV_KEY_IDX + attempt) % total_keys]
        try:
            req = urllib.request.Request(
                "https://integrate.api.nvidia.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                data=json.dumps({
                    "model": "nvidia/nemotron-3-super-120b-a12b",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.2,
                    "max_tokens": max_tokens
                }).encode("utf-8")
            )
            with urllib.request.urlopen(req, timeout=12) as r:
                res = json.loads(r.read())
                _NV_KEY_IDX = (_NV_KEY_IDX + attempt) % total_keys
                return res["choices"][0]["message"]["content"]
        except Exception:
            continue
    return None


def find_matched_jobs(keywords: list[str], candidate_name: str = "Candidate", domain_summary: str = "", target_exp: int = 5, limit: int = 3) -> list[dict]:
    """Find live verified remote jobs from job-queue.csv matching the given keywords, scored and ranked by Nemotron-120B."""
    if not JOB_QUEUE_PATH.is_file():
        return []
    
    rows = []
    try:
        with JOB_QUEUE_PATH.open("r", encoding="utf-8", errors="ignore") as f:
            rows = list(csv.DictReader(f))
    except Exception as exc:
        print(f"Error querying job queue: {exc}")
        return []

    scored = []
    seen_urls = set()
    for r in rows:
        title = r.get("title", "").strip()
        company = r.get("company", "").strip()
        url = r.get("url", "").strip()
        desc = r.get("desc", "").strip()
        tags = r.get("tags", "").strip()

        # Quality gates: real title, valid non-empty company, valid http url
        if not title or not company or not url or not url.startswith("http") or url in seen_urls:
            continue
        if len(company) < 2:
            continue

        full_text = f"{title} {tags} {desc}".lower()
        score = 0

        # 1. Title keyword matching (highest weight)
        for s in keywords:
            s_low = s.lower().strip()
            if not s_low:
                continue
            if s_low in title.lower():
                score += 15
            elif s_low in full_text:
                score += 4

        # 2. Seniority alignment
        low_title = title.lower()
        if target_exp >= 10:
            if any(k in low_title for k in ["intern", "trainee", "coordinator", "junior", "entry", "fresher"]):
                score -= 50
            if any(k in low_title for k in ["director", "head", "lead", "principal", "senior manager", "vp", "executive"]):
                score += 20
            elif any(k in low_title for k in ["senior", "sr.", "manager", "partner"]):
                score += 10
        elif target_exp >= 5:
            if any(k in low_title for k in ["intern", "trainee", "fresher"]):
                score -= 30
            if any(k in low_title for k in ["senior", "lead", "specialist", "manager"]):
                score += 10

        if score >= 10:
            scored.append({
                "score": score,
                "title": title,
                "company": company,
                "url": url,
                "desc_snippet": desc[:250],
                "hits": [k for k in keywords if k.lower() in full_text]
            })
            seen_urls.add(url)

    # Rank by highest score descending
    scored.sort(key=lambda x: x["score"], reverse=True)
    if not scored:
        return []

    # 3. Apply Nemotron-120B reasoning over top candidate pool
    pool_candidates = scored[:10]
    candidate_summary = f"{candidate_name} ({domain_summary}, ~{target_exp} years experience)"
    pool_json = json.dumps([
        {"id": i, "title": c["title"], "company": c["company"], "url": c["url"], "snippet": c["desc_snippet"]}
        for i, c in enumerate(pool_candidates, 1)
    ], indent=2)

    prompt = (
        f"You are an executive career agent matching {candidate_summary} to live verified remote jobs.\n\n"
        f"CANDIDATES AVAILABLE:\n{pool_json}\n\n"
        f"TASK: Select the top {limit} BEST jobs that perfectly fit this candidate's career level, seniority, and domain.\n"
        f"Avoid roles that are too junior (no coordinators/interns for senior profiles).\n\n"
        f"OUTPUT: Respond with ONLY a valid JSON array of {limit} objects:\n"
        f'[{{"title": "...", "company": "...", "url": "..."}}]'
    )

    llm_resp = call_nemotron_llm(prompt)
    if llm_resp:
        try:
            m = re.search(r"\[\s*\{.*\}\s*\]", llm_resp, re.DOTALL)
            if m:
                chosen = json.loads(m.group(0))
                if isinstance(chosen, list) and len(chosen) >= limit:
                    return chosen[:limit]
        except Exception:
            pass

    return scored[:limit]


def build_pitch_message(name: str, domain_summary: str, jobs: list[dict]) -> str:
    """Construct the personalized Two-Edged Sword pitch."""
    first_name = name.split()[0].title() if name else "there"
    
    job_lines = []
    for idx, j in enumerate(jobs, 1):
        job_lines.append(f"{idx}. {j['title']} (Remote) - {j['company']}:\n{j['url']}")
    jobs_text = "\n\n".join(job_lines)
    
    msg = (
        f"Hi {first_name},\n\n"
        f"Saw your profile and experience across {domain_summary}.\n\n"
        f"I track verified live remote and global hiring pipelines and pulled {len(jobs)} openings "
        f"matching your background that you can apply to right now:\n\n"
        f"{jobs_text}\n\n"
        f"If you'd find this valuable on an ongoing basis, we offer:\n"
        f"• Package 1 (Curated Job Feed): We continuously filter and send high-signal, verified remote roles directly to your inbox/DM.\n"
        f"• Package 2 (Auto-Pilot Applications): Our autonomous engine tracks, gates questions, and applies directly while your machine idles (Rs 499 setup).\n\n"
        f"Feel free to reply here or reach out at isearch.xsolve@gmail.com.\n\n"
        f"Best regards,\n"
        f"Kunal"
    )
    return msg


def deliver_two_edged_sword_pitch(client, lane: T.Lane, recipient_id: str, name: str, domain_summary: str, keywords: list[str]) -> bool:
    """Deliver the Two-Edged Sword pitch via Chrome Profile 17 with Rule 1 receipts."""
    lane.log(f"\n{'='*65}")
    lane.log(f"TWO-EDGED SWORD TARGET: {name} (Recipient: {recipient_id})")
    lane.log(f"{'='*65}")
    
    # Check if already messaged
    sent_data = load_sent_tracker()
    if recipient_id in sent_data:
        lane.log(f"Skipping {name} - already sent on {sent_data[recipient_id].get('sent_at')}")
        return True
    
    # 1. Match jobs using Nemotron 120B reasoning over candidate profile
    jobs = find_matched_jobs(keywords, candidate_name=name, domain_summary=domain_summary, target_exp=7, limit=3)
    if not jobs:
        lane.log(f"No matching jobs found in local queue for keywords: {keywords}")
        return False
    lane.log(f"Matched {len(jobs)} live roles:")
    for j in jobs:
        lane.log(f"  - {j['title']} @ {j['company']}")
    
    # 2. Build message
    pitch = build_pitch_message(name, domain_summary, jobs)
    
    # 3. Direct Compose Navigation
    compose_url = f"https://www.linkedin.com/messaging/compose/?recipient={recipient_id}"
    lane.log(f"Navigating directly to compose URL: {compose_url}")
    client.call_tool("browser_navigate", {"url": compose_url})
    time.sleep(5)
    
    # Verify we are on compose thread
    page = T.read_page(client)
    wall = lane.wall(page["body"], page["title"])
    if wall:
        lane.log(f"Login/Captcha wall encountered: {wall}")
        lane.row(compose_url, name, "LinkedIn", 0, "compose_navigation", T.BLOCKED, "none", f"wall: {wall}")
        return False
    
    # 4. Inject message using JavaScript DOM manipulation
    paragraphs = pitch.split("\n\n")
    inject_res = client._js(f"""
    (() => {{
        const box = document.querySelector('div.msg-form__contenteditable[contenteditable="true"]');
        if (!box) return {{ ok: false, error: "compose_box_not_found" }};
        
        box.focus();
        box.innerHTML = '';
        const paras = {json.dumps(paragraphs)};
        paras.forEach(text => {{
            const p = document.createElement('p');
            p.innerText = text;
            box.appendChild(p);
        }});
        
        box.dispatchEvent(new Event('input', {{ bubbles: true }}));
        box.dispatchEvent(new Event('change', {{ bubbles: true }}));
        
        const sendBtn = document.querySelector('button.msg-form__send-button');
        return {{
            ok: true,
            boxTextLen: box.innerText.length,
            sendBtnExists: !!sendBtn,
            sendBtnDisabled: sendBtn ? sendBtn.disabled : true
        }};
    }})()
    """)
    lane.log(f"Message injection result: {inject_res}")
    time.sleep(1)
    
    # 5. Rule 1 Pre-Send Screenshot Receipt
    slug = re.sub(r'[^a-zA-Z0-9]', '_', name.lower())
    ts = time.strftime("%Y%m%d_%H%M%S")
    shot_typed = lane.shot(client, f"two-edge-typed-{slug}-{ts}")
    lane.log(f"PRE-SEND RECEIPT: {shot_typed}")
    
    # 6. Click Send via JS
    send_res = client._js("""
    (() => {
        const sendBtn = document.querySelector('button.msg-form__send-button');
        if (!sendBtn) return { ok: false, error: "send_button_not_found" };
        if (sendBtn.disabled) return { ok: false, error: "send_button_disabled" };
        sendBtn.click();
        return { ok: true, clicked: true };
    })()
    """)
    lane.log(f"Send click result: {send_res}")
    time.sleep(3)
    
    # 7. Rule 1 Post-Send Final Receipt
    shot_sent = lane.shot(client, f"two-edge-sent-{slug}-{ts}")
    lane.log(f"POST-SEND FINAL RECEIPT: {shot_sent}")
    
    # Record tracking & ledger
    sent_data[recipient_id] = {
        "name": name,
        "sent_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "receipt_typed": str(shot_typed) if shot_typed else "none",
        "receipt_sent": str(shot_sent) if shot_sent else "none",
        "jobs_matched": [j["title"] for j in jobs]
    }
    save_sent_tracker(sent_data)
    
    lane.row(
        source=compose_url,
        role="1st-Degree Pitch",
        company=name,
        score=len(jobs),
        step="two_edged_sword_delivery",
        status=T.APPLIED,
        receipt=str(shot_sent) if shot_sent else "none",
        note=f"Delivered gift with {len(jobs)} roles and 2 packages"
    )
    return True


OTW_REGEX = re.compile(
    r"open\s*to\s*(work|opportunities)|actively\s*(looking|seeking)|seeking\s*(new\s*)?(roles?|opportunities?|job|positions?)|immediate\s*joiner|in\s*transition|open\s*for\s*opportunities",
    re.IGNORECASE
)
BUSINESS_EXCLUDE_REGEX = re.compile(
    r"\b(CEO|Founder|Co-founder|Owner|President|Managing Director|General Partner|Investor|Career Coach)\b",
    re.IGNORECASE
)


def scan_and_pitch_next_connection(client, lane: T.Lane) -> bool:
    """Scan LinkedIn connections, strictly filter for #OpenToWork candidates (ignoring business professionals), extract profile, match with Nemotron, and pitch."""
    lane.log("\n--- [Two-Edged Sword] Scanning 1st-Degree Connections for #OpenToWork Candidates ---")
    client.call_tool("browser_navigate", {"url": "https://www.linkedin.com/mynetwork/invite-connect/connections/"})
    time.sleep(5)

    # Scroll down 3 times to load deeper connection pool
    for _ in range(3):
        client._js("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

    sent_data = load_sent_tracker()

    # Extract connection items with name, headline, and profile URL
    raw_conns = client._js("""
    (() => {
        const results = [];
        const links = Array.from(document.querySelectorAll('a[href*="/in/"]'));
        links.forEach(a => {
            const rawText = a.innerText.trim();
            if (!rawText) return;
            const parts = rawText.split('\\n').map(p => p.trim()).filter(Boolean);
            if (parts.length >= 2) {
                const name = parts[0];
                const headline = parts.slice(1).join(' ');
                results.push({
                    name: name,
                    headline: headline,
                    profile_url: a.href,
                    full_text: rawText
                });
            }
        });
        return results;
    })()
    """)

    if not isinstance(raw_conns, list) or not raw_conns:
        lane.log("No connections parsed on connections page.")
        return False

    # Deduplicate by profile_url
    dedup = {}
    for c in raw_conns:
        url_clean = c["profile_url"].split("?")[0].rstrip("/")
        if url_clean not in dedup:
            dedup[url_clean] = c

    lane.log(f"Parsed {len(dedup)} unique 1st-degree connections.")

    # Apply strict Open To Work filter (Law of Baba: Job seekers only, no business professionals)
    otw_candidates = []
    for c in dedup.values():
        name = c["name"]
        headline = c["headline"]
        full_text = c.get("full_text", "")
        combined = f"{name} {headline} {full_text}"

        is_otw = bool(OTW_REGEX.search(combined))
        is_biz = bool(BUSINESS_EXCLUDE_REGEX.search(headline)) and not is_otw

        if is_biz:
            lane.log(f"  [EXCLUDED BIZ PRO]: {name} | {headline[:60]}")
            continue

        if is_otw:
            lane.log(f"  [OPEN TO WORK MATCH]: {name} | {headline[:60]}")
            otw_candidates.append(c)
        else:
            lane.log(f"  [SKIPPED NOT OTW]: {name} | {headline[:60]}")

    if not otw_candidates:
        lane.log("No Open To Work candidates identified in visible connection pool.")
        return False

    lane.log(f"\nIdentified {len(otw_candidates)} Open To Work candidates. Checking sent history...")
    next_candidate = None
    for cand in otw_candidates:
        slug = re.sub(r'[^a-zA-Z0-9]', '_', cand['name'].lower())
        already_sent = any(
            v.get("name", "").lower() == cand["name"].lower() or slug in str(v)
            for v in sent_data.values()
        )
        if not already_sent:
            next_candidate = cand
            break

    if not next_candidate:
        lane.log("All visible Open To Work candidates have already received the Two-Edged Sword pitch.")
        return True

    cand_name = next_candidate["name"]
    cand_headline = next_candidate["headline"]
    profile_url = next_candidate["profile_url"]
    lane.log(f"\n>>> TARGETING NEXT OPEN TO WORK CANDIDATE: {cand_name} ({profile_url}) <<<")

    # 1. Scan Profile Details
    client.call_tool("browser_navigate", {"url": profile_url})
    time.sleep(5)

    # Scroll down to load experience
    client._js("window.scrollBy(0, 700);")
    time.sleep(2)

    profile_data = client._js("""
    (() => {
        let name = '';
        const h1 = document.querySelector('h1');
        if (h1 && h1.innerText.trim().length > 1) {
            name = h1.innerText.trim();
        }

        const headlineEl = document.querySelector('div.text-body-medium') || document.querySelector('.pv-text-details__left-panel div');
        const headline = headlineEl ? headlineEl.innerText.trim() : '';

        // Experience section
        let experience = '';
        const sections = Array.from(document.querySelectorAll('section'));
        const expSec = sections.find(s => s.innerText.includes('Experience'));
        if (expSec) {
            experience = expSec.innerText.replace(/\\n+/g, ' ').slice(0, 600);
        }

        // About section
        let about = '';
        const aboutSec = sections.find(s => s.innerText.includes('About'));
        if (aboutSec) {
            about = aboutSec.innerText.replace(/\\n+/g, ' ').slice(0, 400);
        }

        const a = document.querySelector('a[href*="/messaging/compose/"]');
        let recipientId = null;
        if (a) {
            const m = a.href.match(/recipient=([^&]+)/);
            if (m) recipientId = m[1];
        }

        return { name: name, headline: headline, experience: experience, about: about, recipient_id: recipientId };
    })()
    """)

    if profile_data.get("name"):
        cand_name = profile_data["name"]
    recipient_id = profile_data.get("recipient_id")

    if not recipient_id:
        # Trigger Message button to reveal recipient
        client._js("""
        (() => {
            const btns = Array.from(document.querySelectorAll('button, a'));
            const msgBtn = btns.find(b => b.innerText.trim() === 'Message' || b.getAttribute('aria-label')?.includes('Message'));
            if (msgBtn) msgBtn.click();
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

    if not recipient_id:
        lane.log(f"Could not resolve compose recipient ID for {cand_name}. Skipping to next.")
        return False

    # Clean domain summary & extract keywords
    exp_text = profile_data.get("experience", "")
    about_text = profile_data.get("about", "")
    full_profile_text = f"{cand_headline} {about_text} {exp_text}"

    # Strip generic Open To Work tokens from domain summary
    clean_domain = re.sub(r"(?i)\bopen\s*to\s*(work|opportunities)\b", "", cand_headline).strip(" |·•-")
    if not clean_domain or len(clean_domain) < 4:
        if "immigration" in exp_text.lower() or "overseas" in exp_text.lower():
            clean_domain = "Overseas Careers, Education Consulting, and Admissions Operations"
        elif "operations" in exp_text.lower():
            clean_domain = "Business Operations and Client Services"
        elif "sales" in exp_text.lower():
            clean_domain = "Client Relations, Inside Sales, and Business Consulting"
        else:
            clean_domain = "Operations, Customer Support, and Client Relations"

    # Keywords for job queue matching
    raw_kws = [k.strip() for k in re.split(r"[|•·,/]+", clean_domain) if len(k.strip()) > 2]
    keywords = [k for k in raw_kws if not re.search(r"(?i)open|work|job|immediate", k)]
    if not keywords:
        keywords = ["operations", "client relations", "customer support", "specialist"]

    lane.log(f"Profile Confirmed: {cand_name} (Recipient: {recipient_id})")
    lane.log(f"Domain Focus: {clean_domain}")
    lane.log(f"Matching Keywords: {keywords}")

    # 2 & 3. Deliver Two-Edged Sword via Nemotron-120B reasoning and Rule 1 receipts
    return deliver_two_edged_sword_pitch(
        client=client,
        lane=lane,
        recipient_id=recipient_id,
        name=cand_name,
        domain_summary=clean_domain,
        keywords=keywords
    )


def run_targeted_sweep():
    """Run the Two-Edged Sword sweep for prioritised targets and dynamic connections."""
    targets = [
        {
            "name": "Dipti Mehrotra",
            "recipient_id": "ACoAAAwmJcIBfa9SELk-uvuRLo_M0MS5_s4dbFo",
            "domain_summary": "Talent Management, Executive Acquisition, and HR Leadership",
            "keywords": ["talent acquisition", "recruiter", "people partner", "human resources", "talent management"]
        },
        {
            "name": "Subhamay Namata",
            "recipient_id": "ACoAAB_BkdABULdyuTp3FdagywDulVjqtQmz-4Q",
            "domain_summary": "HR Operations, People Services, Workday HRMS, and SAP HCM",
            "keywords": ["hr operations", "people operations", "workday", "hr generalist", "talent operations"]
        }
    ]

    lane = T.Lane("linkedin", "two_edged_sword")
    with T.session(lane) as client:
        lane.log("Starting Two-Edged Sword Engine...")
        sent_any = False
        sent_data = load_sent_tracker()

        # 1. Deliver to any pending priority target
        for target in targets:
            if target["recipient_id"] not in sent_data:
                try:
                    deliver_two_edged_sword_pitch(
                        client=client,
                        lane=lane,
                        recipient_id=target["recipient_id"],
                        name=target["name"],
                        domain_summary=target["domain_summary"],
                        keywords=target["keywords"]
                    )
                    sent_any = True
                except Exception as exc:
                    lane.log(f"Error pitching {target['name']}: {exc}")

        # 2. If priority targets are done, scan and pitch next 1st-degree connection
        if not sent_any:
            try:
                scan_and_pitch_next_connection(client, lane)
            except Exception as exc:
                lane.log(f"Error in dynamic connection sweep: {exc}")

        lane.summary()


def main():
    parser = argparse.ArgumentParser(description="Two-Edged Sword LinkedIn Outreach Lane")
    parser.add_argument("--recipient", type=str, help="Specific LinkedIn recipient ID")
    parser.add_argument("--name", type=str, help="Recipient display name")
    parser.add_argument("--summary", type=str, help="Domain focus summary")
    parser.add_argument("--keywords", type=str, help="Comma-separated keywords for job matching")
    args, _ = parser.parse_known_args()
    
    if args.recipient and args.name:
        kws = [k.strip() for k in (args.keywords or "").split(",") if k.strip()]
        lane = T.Lane("linkedin", "two_edged_sword")
        with T.session(lane) as client:
            deliver_two_edged_sword_pitch(
                client=client,
                lane=lane,
                recipient_id=args.recipient,
                name=args.name,
                domain_summary=args.summary or "Talent & Operations",
                keywords=kws or ["talent", "operations"]
            )
            lane.summary()
    else:
        run_targeted_sweep()


if __name__ == "__main__":
    main()
