"""lane_daemon.py - 24/7 Autonomous Employment Engine.

Continuous, multi-portal automation pipeline running round-the-clock:
- Re-verifies candidate resume hash integrity every round
- Discovers freshly posted roles via resume-derived queries
- Filters cards through tri-factor gate (Seniority, Work Model/Remote, Skills)
- Submits verified applications with local AI recruiter chatbot answering
- Gathers receipts across Naukri, Foundit, Indeed, and LinkedIn
- Strictly obeys pacing, rate-limiting, and all 11 Laws
"""
from __future__ import annotations

import argparse
import datetime
import os
import random
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import lane_tools as T
import lane_resume
import lane_jobs
import lane_mass_apply
import lane_foundit
import lane_market_probe
import lane_linkedin_feed
import lane_two_edged_sword
import lane_payment_pipeline


def log(msg: str):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    try:
        log_file = HERE.parent / "evidence" / "employment-lane" / "daemon.log"
        log_file.parent.mkdir(parents=True, exist_ok=True)
        with log_file.open("a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


def execute_cycle(cycle: int, limit_per_round: int = 3):
    log(f"======================================================================")
    log(f"STARTING 24/7 AUTONOMOUS CYCLE #{cycle}")
    log(f"======================================================================")

    # 1. Integrity check
    ok, msg = T.verify_candidate_resume()
    if not ok:
        log(f"CRITICAL: Candidate resume hash verification failed: {msg}")
        return False
    facts = T.candidate_facts()
    queries = T.candidate_search_queries()
    log(f"Candidate: {facts.get('NAME')} | Work Model: {facts.get('WORK_MODEL')} | Experience: {facts.get('YEARS_EXPERIENCE')} yrs")
    log(f"Active Target Queries ({len(queries)}): {queries[:4]}")

    # Snapshot applied count before
    ledger_path = HERE.parent / "evidence" / "employment-lane" / "ledger.tsv"
    before_rows = len(ledger_path.read_text(encoding="utf-8", errors="replace").splitlines()) if ledger_path.is_file() else 0

    # 2. Naukri Profile Audit & Recommended Jobs
    log("\n--- [LANE 1/4] NAUKRI: Profile Verification & Recommended Scan ---")
    try:
        lane_jobs.main()
    except Exception as exc:
        log(f"Naukri recommended scan error: {exc}")

    # 3. Naukri Dynamic Mass Application Engine
    log(f"\n--- [LANE 2/4] NAUKRI: Discovery & Mass Apply (limit: {limit_per_round}) ---")
    try:
        sys.argv = ["lane_mass_apply.py", "--limit", str(limit_per_round)]
        lane_mass_apply.main()
    except Exception as exc:
        log(f"Naukri mass apply error: {exc}")

    # 4. Foundit Live Search & Fit Gating
    log("\n--- [LANE 3/4] FOUNDIT: Search & Fit Gating ---")
    try:
        lane_foundit.main(["lane_foundit.py"])
    except Exception as exc:
        log(f"Foundit lane error: {exc}")

    # 5. Indeed & LinkedIn Market Search + Feed
    log("\n--- [LANE 4/5] INDEED & LINKEDIN: Market Search & Feed ---")
    try:
        lane_market_probe.main()
    except Exception as exc:
        log(f"Market search error: {exc}")
    try:
        lane_linkedin_feed.main()
    except Exception as exc:
        log(f"LinkedIn feed error: {exc}")

    # 6. LinkedIn Two-Edged Sword 1st-Degree Outreach & Magnet (Stage-only in 24/7 daemon)
    log("\n--- [LANE 5/5] LINKEDIN: Two-Edged Sword Discovery & Stage-Only Verification ---")
    try:
        sys.argv = ["lane_two_edged_sword.py", "--stage-only"]
        lane_two_edged_sword.main()
    except Exception as exc:
        log(f"Two-Edged Sword lane error: {exc}")


    # 7. LinkedIn Inbound Payment & Deliverable Pipeline Listener
    log("\n--- [PAYMENT PIPELINE] LinkedIn Inbound Reply & Deliverable Listener ---")
    try:
        sys.argv = ["lane_payment_pipeline.py"]
        lane_payment_pipeline.main()
    except Exception as exc:
        log(f"Payment pipeline listener error: {exc}")

    # Snapshot applied count after
    after_rows = len(ledger_path.read_text(encoding="utf-8", errors="replace").splitlines()) if ledger_path.is_file() else 0
    delta_rows = after_rows - before_rows

    log(f"======================================================================")
    log(f"CYCLE #{cycle} COMPLETED: {delta_rows} new ledger events recorded (Total: {after_rows})")
    log(f"======================================================================")
    return True


def run_preflight() -> bool:
    print("=" * 75)
    print("KILO BRIDGE 24/7 EMPLOYMENT SYSTEM: FULL PREFLIGHT VERIFICATION")
    print("=" * 75)
    
    # 1. Environment checks
    print(f"[ OK ] Python {sys.version.split()[0]} ({sys.executable})")

    # 2. Candidate Pointer Configuration
    cfg = T.candidate_config()
    resume_p = cfg.get("resume_path")
    expected_sha = cfg.get("resume_sha256")
    if not resume_p or not expected_sha:
        print("[FAIL] candidate-profile.json must contain resume_path and resume_sha256")
        return False
    print(f"[ OK ] Candidate pointer file: candidate-profile.json")

    # 3. Cryptographic Resume Integrity Check
    ok, msg = T.verify_candidate_resume()
    if not ok:
        print(f"[FAIL] Resume hash mismatch or missing: {msg}")
        return False
    print(f"[ OK ] Pinned Resume SHA-256 verified: {str(expected_sha).upper()}")

    # 4. Resume Parsing & Fact Extraction
    path = T.resume_path()
    try:
        import resume_facts as RF
        pypdf_ok, pypdf_msg = RF.require_pypdf(sys.executable)
        if not pypdf_ok:
            print(f"[FAIL] pypdf parser dependency missing: {pypdf_msg}")
            return False
        print(f"[ OK ] Resume Parser: {pypdf_msg}")
        
        print("\n--- Candidate Verified Facts (Sole Source of Truth: Resume.pdf) ---")
        report_text = RF.report(path)
        print(report_text)
    except Exception as exc:
        print(f"[FAIL] Failed extracting facts from pinned resume: {exc}")
        return False

    # 5. Derived Preferences & Dynamic Search Targets
    facts = T.candidate_facts()
    queries = T.candidate_search_queries(facts)
    skills = T.candidate_skills()
    if len(skills) < 2:
        print(f"[FAIL] Insufficient skills ({len(skills)} found, minimum 2 required)")
        return False
        
    print("\n--- Derived Dynamic Preferences & Target Roles ---")
    print(f"  NAME:                {facts.get('NAME')}")
    print(f"  LOCATION:            {facts.get('LOCATION')}")
    print(f"  WORK_MODEL:          {facts.get('WORK_MODEL')}")
    print(f"  RELOCATION ANSWER:   {T.answer_from_resume('Are you willing to relocate?')}")
    print(f"  WORK MODE ANSWER:    {T.answer_from_resume('What is your preferred work mode?')}")
    print(f"  TARGET ROLES ({len(queries)}):    {', '.join(queries[:5])}")

    # 6. Browser MCP Session Liveness Check
    print("\n--- Browser MCP Session Liveness Check ---")
    try:
        import agent360_client as A
        client = A.Agent360Client()
        client.start()
        tabs = client.call_tool("browser_list_tabs", {})
        client.close()
        tab_count = len(tabs.get("content", [])) if isinstance(tabs, dict) else 0
        print(f"[ OK ] Agent360 MCP browser session active ({tab_count} tabs detected)")
    except Exception as exc:
        print(f"[WARN] Agent360 session verification warning: {exc}")

    print("\n" + "=" * 75)
    print("PREFLIGHT VERDICT: ALL SYSTEMS GO. ENTERING 24/7 AUTONOMOUS OPERATION.")
    print("=" * 75 + "\n")
    return True


def run_daemon(interval: int = 1200, jitter: int = 120, limit_per_round: int = 3, once: bool = False):
    # Execute full preflight verification first
    if not run_preflight():
        log("CRITICAL: Preflight verification failed. Aborting daemon.")
        return

    log("Initializing 24/7 Autonomous Employment Daemon...")
    log(f"Configuration: interval={interval}s, jitter={jitter}s, limit_per_round={limit_per_round}, once={once}")

    cycle = 1
    while True:
        try:
            execute_cycle(cycle, limit_per_round=limit_per_round)
        except KeyboardInterrupt:
            log("Daemon interrupted by operator (SIGINT). Exiting cleanly.")
            break
        except Exception as exc:
            log(f"Unexpected cycle exception (self-healing): {exc}")

        if once:
            log("Run-once flag set. Exiting.")
            break

        # Calculate paced delay
        current_jitter = random.randint(-jitter, jitter)
        sleep_duration = max(60, interval + current_jitter)
        wake_time = (datetime.datetime.now() + datetime.timedelta(seconds=sleep_duration)).strftime("%H:%M:%S")
        log(f"Sleeping for {sleep_duration}s until next cycle (Wake time: {wake_time})...\n")

        try:
            time.sleep(sleep_duration)
        except KeyboardInterrupt:
            log("Daemon interrupted during sleep by operator. Exiting cleanly.")
            break

        cycle += 1


def main():
    parser = argparse.ArgumentParser(description="24/7 Autonomous Employment Daemon")
    parser.add_argument("--interval", type=int, default=1200, help="Base interval between cycles in seconds (default: 1200 = 20 min)")
    parser.add_argument("--jitter", type=int, default=120, help="Max random jitter in seconds (default: 120)")
    parser.add_argument("--limit", type=int, default=3, help="Max applications to submit per cycle (default: 3)")
    parser.add_argument("--once", action="store_true", help="Execute single cycle and exit")
    args = parser.parse_args()

    run_daemon(interval=args.interval, jitter=args.jitter, limit_per_round=args.limit, once=args.once)


if __name__ == "__main__":
    main()
