"""lane_mass_apply.py - Production Mass Application Engine.

Features:
- Dynamic search ingestion across target role queries
- Verified skill fit gating (score >= min_match_score)
- Idempotent deduplication against ledger.tsv
- Recruiter chatbot handling (choice chips + input forms)
- Captures screenshot receipts & writes 10-column ledger rows
- Portal confirmation verification (success text / panel closed)
"""
import argparse
import json
import re
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import lane_tools as T


def get_applied_signatures(ledger_path):
    """Return (applied_urls, applied_pairs) sets from ledger.tsv."""
    if not ledger_path.is_file():
        return set(), set()
    applied_urls = set()
    applied_pairs = set()
    try:
        for line in ledger_path.read_text(encoding="utf-8", errors="replace").splitlines():
            parts = line.split("\t")
            if len(parts) >= 8 and parts[7].strip() == T.APPLIED:
                src = parts[2].strip().lower()
                role = parts[3].strip().lower()
                comp = parts[4].strip().lower()
                if src and src != "-" and "http" in src:
                    applied_urls.add(src)
                if role and role != "-" and role != "none":
                    applied_pairs.add((role, comp))
    except Exception:
        pass
    return applied_urls, applied_pairs


def is_already_applied(job, applied_urls, applied_pairs):
    url = job.get("url", "").lower()
    title = job.get("title", "").strip().lower()
    comp = job.get("company", "").strip().lower()
    for u in applied_urls:
        if u in url or url[:60] in u:
            return True
    for r, c in applied_pairs:
        if r in title and (not c or c == "-" or c in comp or comp in c):
            return True
    return False


def discover_naukri_jobs(client, lane, queries=None, min_score=2, limit_per_query=20):
    """Dynamically discover matched jobs from live Naukri search streams, filtered strictly by resume."""
    facts = T.candidate_facts()
    queries = queries or T.candidate_search_queries(facts)[:4]
    is_remote = T.is_remote_preferred()
    discovered = []
    seen_urls = set()

    for q in queries:
        query_slug = re.sub(r"[^a-zA-Z0-9]+", "+", q.strip().lower()).strip("+")
        search_urls = []
        if is_remote:
            search_urls.append((f"https://www.naukri.com/{query_slug}-remote-jobs", f"{q} (Remote)"))
        search_urls.append((f"https://www.naukri.com/{query_slug}-jobs", q))

        for search_url, q_label in search_urls:
            lane.log(f"Searching Naukri for '{q_label}' -> {search_url}")
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
                lane.log(f"No cards extracted for {search_url}")
                continue

            lane.log(f"Extracted {len(cards_data)} raw cards for '{q_label}'")
            for item in cards_data:
                href = item.get("href", "")
                if not href or href in seen_urls:
                    continue
                seen_urls.add(href)

                passes, reason, score, hits = T.card_filter_gate(item, facts=facts, min_score=min_score)
                title = item.get("title", "")
                company = item.get("company", "-")

                lane.log(f"  [{'PASS' if passes else 'REJECT'}] {title[:60]} @ {company} -> {reason}")
                if passes:
                    discovered.append({
                        "title": title,
                        "company": company,
                        "url": href,
                        "score": score,
                        "hits": hits
                    })
                    if len(discovered) >= limit_per_query * len(queries):
                        break

    return discovered


def is_apply_success(body):
    low = (body or "").lower()
    return any(s in low for s in ["application submitted", "successfully applied", "applied successfully",
                                  "application sent", 'applied to "', "applied to '"]) or "applied to " in low[:500]


def apply_single_job(client, lane, job):
    title = job["title"]
    company = job["company"]
    url = job["url"]
    score = job["score"]

    lane.log(f"\n{'='*60}\nPROCESSING: {title} @ {company}\n{'='*60}")

    # 1. Navigate to job URL
    client.call_tool("browser_navigate", {"url": url})
    time.sleep(8)

    page = T.read_page(client)
    low = page["body"].lower()

    # Check already applied
    if "already applied" in low or ("applied" in low[:1000] and "save" not in low[:1000] and "apply" not in low[:500]):
        lane.log(f"Already applied to {title}")
        shot = lane.shot(client, f"mass-applied-already-{time.strftime('%H%M%S')}")
        lane.row(url[:70], title[:70], company, score, "duplicate check", T.APPLIED,
                 str(shot) if shot else "none", "already applied per live page")
        return "ALREADY_APPLIED"

    # Check if external redirect
    if "apply on company site" in low or "company site" in low[:1500]:
        lane.log(f"External handoff for {title}")
        shot = lane.shot(client, f"mass-apply-handoff-{time.strftime('%H%M%S')}")
        lane.row(url[:70], title[:70], company, score, "external handoff", T.BLOCKED,
                 str(shot) if shot else "none", "external company site redirect required")
        return "EXTERNAL_HANDOFF"

    # 2. Click Apply button
    btn_res = client._js('''(() => {
        const c = document.querySelector(".chatbot_MessageContainer");
        if (c) return "drawer already open";
        let btn = document.querySelector("button#apply-button, button.apply-button");
        if (!btn) {
            btn = Array.from(document.querySelectorAll("button")).find(e => (e.innerText||'').trim().toLowerCase() === 'apply');
        }
        if (!btn) return "no apply button";
        btn.click();
        return "clicked " + (btn.innerText || 'apply');
    })()''')
    lane.log("Apply button result: " + str(btn_res))

    if "clicked" not in str(btn_res) and "open" not in str(btn_res):
        shot = lane.shot(client, f"mass-apply-nobtn-{time.strftime('%H%M%S')}")
        lane.row(url[:70], title[:70], company, score, "find apply button", T.BLOCKED,
                 str(shot) if shot else "none", f"apply button not found: {btn_res}")
        lane.log(f"BLOCKED: Apply button not found for {title}")
        return "BLOCKED"

    time.sleep(5)

    # Check if directly applied without chatbot
    page = T.read_page(client)
    if is_apply_success(page["body"]):
        shot = lane.shot(client, f"mass-apply-success-{time.strftime('%H%M%S')}")
        lane.row(url[:70], title[:70], company, score, "application submitted", T.APPLIED,
                 str(shot) if shot else "none", "direct apply confirmed")
        lane.log(f"APPLIED DIRECTLY: {title}")
        return "APPLIED"

    # 3. Recruiter Question Loop
    seen = set()
    success = False
    answered_count = 0

    for turn in range(1, 8):
        rq = T.read_recruiter_question(client)
        if not rq or rq in seen:
            break

        lane.log(f"Turn {turn}: Question = {rq}")
        ans = T.answer_from_resume(rq)
        lane.log(f"Turn {turn}: Answer = {ans}")

        if not ans:
            shot = lane.shot(client, f"mass-apply-blocked-{time.strftime('%H%M%S')}")
            lane.row(url[:70], title[:70], company, score, "recruiter question", T.BLOCKED,
                     str(shot) if shot else "none", f"UNANSWERABLE: {rq[:80]}")
            lane.log(f"BLOCKED on question: {rq}")
            client._js('document.querySelector(".crossIcon, .close, [class*=cross], [class*=close]").click()')
            return "BLOCKED"

        seen.add(rq)
        res = T.answer_and_save(client, rq, ans)
        lane.log(f"Turn {turn}: Save result = {res}")
        answered_count += 1
        time.sleep(4)

        page = T.read_page(client)
        if is_apply_success(page["body"]):
            success = True
            break

    c_check = client._js('document.querySelector(".chatbot_MessageContainer") ? "open" : "closed"')
    shot = lane.shot(client, f"mass-apply-result-{time.strftime('%H%M%S')}")

    page = T.read_page(client)
    if is_apply_success(page["body"]):
        success = True

    btn_status = client._js('(() => { var b = document.querySelector("#apply-button, button.apply-button"); return b ? (b.innerText||"").trim().toLowerCase() : ""; })()')
    if "applied" in str(btn_status):
        success = True

    if success or (answered_count > 0 and c_check == "closed"):
        lane.row(url[:70], title[:70], company, score, "application submitted", T.APPLIED,
                 str(shot) if shot else "none", "portal confirmed: success text or panel closed after answering")
        lane.log(f"APPLIED CONFIRMED: {title}")
        return "APPLIED"
    else:
        lane.row(url[:70], title[:70], company, score, "apply flow", T.BLOCKED,
                 str(shot) if shot else "none", "unconfirmed application flow")
        lane.log(f"Apply unverified: {title}")
        client._js('document.querySelector(".crossIcon, .close, [class*=cross], [class*=close]").click()')
        return "UNVERIFIED"


def main():
    parser = argparse.ArgumentParser(description="Mass Application Engine")
    parser.add_argument("--queries", default=None,
                        help="Comma-separated search queries (defaults to resume-derived queries)")
    parser.add_argument("--limit", type=int, default=10, help="Maximum jobs to process in this run")
    parser.add_argument("--min-score", type=int, default=2, help="Minimum skill match score to apply")
    args = parser.parse_args()

    lane = T.Lane("naukri", "mass apply dynamic")
    queries = [q.strip() for q in args.queries.split(",") if q.strip()] if args.queries else T.candidate_search_queries()[:4]
    lane.log(f"Active search queries derived from resume: {queries}")

    applied_urls, applied_pairs = get_applied_signatures(lane.ledger_path)
    lane.log(f"Existing APPLIED records in ledger: {len(applied_urls)} URLs, {len(applied_pairs)} pairs")

    results = {}
    with T.session(lane) as client:
        # Dynamic discovery
        discovered = discover_naukri_jobs(client, lane, queries, min_score=args.min_score)
        lane.log(f"\nTotal matched jobs discovered across queries: {len(discovered)}")

        # Deduplicate & filter
        to_apply = []
        for job in discovered:
            if is_already_applied(job, applied_urls, applied_pairs):
                lane.log(f"Skipping already applied in ledger: {job['title']} @ {job['company']}")
                continue
            to_apply.append(job)

        lane.log(f"New jobs queued for application: {len(to_apply)} (limit: {args.limit})")

        # Process applications
        for job in to_apply[:args.limit]:
            try:
                res = apply_single_job(client, lane, job)
                results[f"{job['title']} @ {job['company']}"] = res
                time.sleep(3)
            except Exception as exc:
                lane.log(f"Exception applying to {job['title']}: {exc}")
                results[f"{job['title']} @ {job['company']}"] = f"ERROR: {exc}"

    print("\n" + "="*70)
    print("MASS APPLY EXECUTION SUMMARY:")
    for k, v in results.items():
        print(f"  * {k}: {v}")
    print("="*70)
    lane.summary()
    return 0


if __name__ == "__main__":
    sys.exit(main())
