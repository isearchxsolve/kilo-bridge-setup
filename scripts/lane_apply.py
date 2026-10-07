"""lane_apply.py - the money step: ONE MATCHED title -> the apply flow -> answer -> receipt.

Thin GOAL-RUNNER (2026-10-07). The mechanism lives in lane_tools.py:
  * session / ledger / screenshot / wall        -> T.Lane, T.session
  * card read that MEASURES its selector        -> T.read_cards
  * the recruiter-panel reader (measured wall)  -> T.read_recruiter_question
  * verified answer + save (read-back)          -> T.answer_and_save
This file states the GOAL: open the matched job's apply flow, answer the recruiter
gate from the operator's OWN record, screenshot, ledger - and NEVER claim APPLIED
without a submission-success signal. Every step is APPLIED with evidence,
APPLIED_STEP (gate answered, no submit), or BLOCKED with the exact reason.

LAWS OBEYED: JS .click()/keyboard only (mouse path is dead); screenshot = receipt;
never invent a fact; never force-submit past an unanswered gate; never spend money;
never touch login/password/OTP; ASCII out; BLOCKED beats a faked DONE.
"""
import argparse
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import lane_tools as T  # noqa: E402

JOBS_URL = "https://www.naukri.com/mnjuser/recommendedjobs"
HISTORY_URL = "https://www.naukri.com/myapply/historypage"
DEFAULT_TITLE = "GenAI Architect | Generative AI | LLM | RAG | Agentic AI"

# VERIFY signals: a real apply-flow state marker (NOT 'years of experience', which
# appears in job descriptions -> false positive).
FLOW_SIGNALS = ["answer all the recruiter", "recruiter's question", "apply for this job",
                "submit application", "additional questions", "application submitted"]
SUCCESS = ["application submitted", "successfully applied",
           "you have successfully applied", "applied successfully"]
HISTORY_SUCCESS = ("application sent", "application submitted",
                   "successfully applied")


def _history_entry_for_title(body, title):
    """Return a nearby exact-title history context only when its status is visible.

    A page-wide `title in body and 'applied' in body` check is unsafe: unrelated
    applications make that condition true. Require the title as a complete line,
    then find a success status in the same local text window.
    """
    lines = [" ".join(line.split()) for line in (body or "").splitlines()]
    wanted = " ".join((title or "").split()).casefold()
    if not wanted:
        return None
    for index, line in enumerate(lines):
        if line.casefold() != wanted:
            continue
        context = lines[max(0, index - 2):min(len(lines), index + 10)]
        joined = " | ".join(context)
        low = joined.casefold()
        status = next((token for token in HISTORY_SUCCESS if token in low), None)
        if status:
            company = next((candidate for candidate in lines[index + 1:index + 4]
                            if candidate and candidate.casefold() != wanted), "-")
            return {"company": company, "status": status, "context": joined[:700]}
        return {"company": "-", "status": None, "context": joined[:700]}
    return None


def _verify_history(client, title, expected_company=None):
    """Use the portal UI to check an exact application-history entry."""
    client.call_tool("browser_navigate", {"url": HISTORY_URL})
    time.sleep(7)
    page = T.read_page(client)
    entry = _history_entry_for_title(page.get("body"), title)
    if not entry or not entry.get("status"):
        return {"confirmed": False, "page": page, "entry": entry}
    actual_company = entry.get("company", "-")
    if expected_company and expected_company != "-" and actual_company != "-":
        if expected_company.casefold() not in actual_company.casefold():
            return {"confirmed": False, "page": page, "entry": entry,
                    "reason": "company mismatch: expected %s; history %s" %
                              (expected_company, actual_company)}
    return {"confirmed": True, "page": page, "entry": entry}


def _success_text(client):
    body = (T.read_page(client).get("body") or "").lower()
    return next((signal for signal in SUCCESS if signal in body), None)


def _click_final_submit(client):
    """Click one explicit final-submit control inside the visible apply panel.

    A generic list-page Apply button is deliberately excluded: selecting a role
    and submitting its application are distinct actions.
    """
    r = client._js(
        "(function(){var c=document.querySelector('.chatbot_MessageContainer');"
        "if(!c)return {found:false,reason:'apply panel missing'};"
        "var root=c;for(var k=0;k<5&&root.parentElement;k++)root=root.parentElement;"
        "var all=root.querySelectorAll('button,[role=button],input[type=submit]'),hits=[];"
        "for(var i=0;i<all.length;i++){var e=all[i],t=(e.innerText||e.value||"
        "e.getAttribute('aria-label')||'').trim().toLowerCase();"
        "var r=e.getBoundingClientRect();if(!t||r.width<1||r.height<1||e.disabled)continue;"
        "if(/^(submit|submit application|apply now|finish application|confirm application)$/"
        ".test(t))hits.push({e:e,t:t});}"
        "if(hits.length!==1)return {found:false,reason:'explicit submit controls='+hits.length};"
        "try{hits[0].e.click();return {found:true,label:hits[0].t};}"
        "catch(e){return {found:false,reason:'click failed'};}})()")
    if isinstance(r, str):
        try:
            r = json.loads(r)
        except Exception:
            r = {}
    if isinstance(r, dict) and isinstance(r.get("result"), dict):
        r = r["result"]
    return r if isinstance(r, dict) else {"found": False, "reason": "invalid browser result"}


def _top_matched_title(lane):
    try:
        rows = lane.ledger_path.read_text(encoding="utf-8", errors="replace").splitlines()
    except Exception:
        return None
    for ln in reversed(rows):
        p = ln.split("\t")
        if len(p) >= 8 and p[7].strip() == T.MATCHED:
            return p[3].strip() or None
    return None


def _known_company(lane, title):
    """Return the most recent matched/applied company for this exact role title."""
    try:
        rows = lane.ledger_path.read_text(encoding="utf-8", errors="replace").splitlines()
    except Exception:
        return None
    wanted = " ".join((title or "").split()).casefold()
    for line in reversed(rows):
        fields = line.split("\t")
        if len(fields) < 8 or " ".join(fields[3].split()).casefold() != wanted:
            continue
        if fields[7].strip() in (T.MATCHED, T.APPLIED) and fields[4].strip() not in ("", "-"):
            return fields[4].strip()
    return None


def main(argv):
    parser = argparse.ArgumentParser(description="Apply to one exact, matched Naukri role")
    parser.add_argument("--title", required=True, help="Exact role title from the current matched list")
    parser.add_argument("--submit", action="store_true",
                        help="Submit once after all answer gates and verify the portal confirmation")
    parser.add_argument("--resume", action="store_true",
                        help="Continue an already-open application for this exact role")
    args = parser.parse_args(argv[1:])
    lane = T.Lane("naukri", "apply")
    title = args.title.strip()
    lane.log("LANE_APPLY start :: title = " + title)
    resume_ok, resume_note = T.verify_candidate_resume()
    if not resume_ok or len(__import__("lane_jobs").SKILLS) < 2:
        reason = resume_note if not resume_ok else "pinned resume has fewer than two parsed skills"
        lane.row("-", title[:70], "-", "-", "candidate data preflight", T.BLOCKED,
                 "none", reason)
        lane.log("BLOCKED - " + reason)
        return 2
    with T.session(lane) as c:
        if args.resume:
            # A newly started MCP child may initially attach to about:blank.
            # Bind first, then switch to the already-open Naukri tab by its URL.
            c.call_tool("browser_screenshot", {"format": "png"})
            tabs = c.list_tabs()
            naukri_tab = next((tab for tab in tabs if "naukri.com" in str(tab.get("url", ""))), None)
            if naukri_tab and naukri_tab.get("id"):
                c.switch_tab(naukri_tab["id"])
                time.sleep(1)
            page = T.read_page(c)
            if "naukri.com" not in page["url"]:
                lane.row(page["url"][:70], title[:70], "-", "-", "resume current apply", T.BLOCKED,
                         "none", "current tab is not Naukri")
                return 2
            cards = T.read_cards(c, "naukri")
            hits = [(cd, T.score_card(cd.get("text"), __import__("lane_jobs").SKILLS))
                    for cd in cards["cards"] if title.lower() in (cd.get("title") or "").lower()]
            if not hits:
                lane.row(page["url"][:70], title[:70], "-", "-", "resume current apply", T.BLOCKED,
                         "none", "exact role not present in current Naukri list; no action taken")
                return 2
            card, (score, skills) = hits[0]
            if score < 2 or not T.read_recruiter_question(c):
                lane.row(page["url"][:70], title[:70], "-", score, "resume current apply", T.BLOCKED,
                         "none", "role gate failed or current recruiter panel is absent")
                return 2
            company = T.card_company(card)
            shot = lane.shot(c, "apply-resume-before-" + time.strftime("%Y%m%d%H%M%S"))
            lane.log("RESUME existing role score=%d skills=%s company=%s" % (score, ",".join(skills), company))
            seen, saves_ok, final, success = set(), 0, shot, None
            for turn in range(1, 6):
                rq = T.read_recruiter_question(c)
                if not rq or rq in seen:
                    break
                answer = T.answer_from_resume(rq)
                if not answer:
                    receipt = lane.shot(c, "apply-resume-blocked-" + time.strftime("%H%M%S"))
                    lane.row(page["url"][:70], title[:70], company, score, "recruiter question", T.BLOCKED,
                             str(receipt) if receipt else "none", "UNANSWERABLE Q=" + rq[:150])
                    return 4
                seen.add(rq)
                result = T.answer_and_save(c, rq, answer)
                lane.log("RESUME gate=%s answer=%s save=%s" % (rq[:100], answer, result["save"]))
                if not result["ok"] or not str(result["save"]).startswith("clicked"):
                    receipt = lane.shot(c, "apply-resume-save-failed-" + time.strftime("%H%M%S"))
                    lane.row(page["url"][:70], title[:70], company, score, "recruiter answer", T.BLOCKED,
                             str(receipt) if receipt else "none", "field/save not verified")
                    return 4
                final = lane.shot(c, "apply-resume-answered-%d-%s" % (turn, time.strftime("%H%M%S")))
                transitioned = False
                for _ in range(15):
                    time.sleep(1)
                    success = _success_text(c)
                    next_q = T.read_recruiter_question(c)
                    if success or next_q != rq:
                        transitioned = True
                        break
                if not transitioned:
                    lane.row(page["url"][:70], title[:70], company, score, "recruiter answer", T.BLOCKED,
                             str(final) if final else "none", "Save click had no visible transition; no repeat")
                    return 4
                saves_ok += 1
            if saves_ok != len(seen):
                lane.row(page["url"][:70], title[:70], company, score, "recruiter answers", T.BLOCKED,
                         str(final) if final else "none", "answer/save count mismatch")
                return 4
            success = success or _success_text(c)
            if args.submit and not success:
                submit = _click_final_submit(c)
                lane.log("RESUME final submit -> " + json.dumps(submit, ensure_ascii=True))
                if submit.get("found"):
                    for _ in range(15):
                        time.sleep(2)
                        success = _success_text(c)
                        if success:
                            break
            if success:
                receipt = lane.shot(c, "apply-resume-submitted-" + time.strftime("%Y%m%d%H%M%S"))
                lane.row(page["url"][:70], title[:70], company, score, "application submitted", T.APPLIED,
                         str(receipt) if receipt else "none", "portal confirmation=" + str(success))
                lane.summary()
                return 0
            receipt = lane.shot(c, "apply-resume-unverified-" + time.strftime("%Y%m%d%H%M%S"))
            lane.row(page["url"][:70], title[:70], company, score, "final submission", T.BLOCKED,
                     str(receipt) if receipt else "none", "no success confirmation; final submit not repeated")
            lane.summary()
            return 5

        # A1 - open the recommended list (NAVIGATE-FIRST: attach to the active tab)
        # Dedupe against Naukri's own history before spending another apply attempt.
        lane.log("A0 duplicate check -> " + HISTORY_URL)
        c.call_tool("browser_navigate", {"url": HISTORY_URL})
        time.sleep(7)
        history = T.read_page(c)
        history_wall = lane.wall(history["body"], history["title"])
        if history_wall and len(history["body"]) < 6000:
            lane.row(history["url"][:70], title[:70], "-", "-", "duplicate check", T.BLOCKED,
                     "none", "cannot verify application history; wall=" + history_wall)
            return 2
        entry = _history_entry_for_title(history["body"], title)
        if entry and entry.get("status"):
            known_company = _known_company(lane, title)
            history_company = (entry.get("company") or "-").strip()
            if known_company and history_company not in ("", "-") and known_company.casefold() != history_company.casefold():
                lane.log("HISTORY same title belongs to another employer (%s != %s); continue exact live-role validation." %
                         (history_company, known_company))
                entry = None
            elif not known_company or history_company in ("", "-"):
                receipt = lane.shot(c, "apply-history-employer-ambiguous-" + time.strftime("%Y%m%d%H%M%S"))
                lane.row(history["url"][:70], title[:70], history_company, "-",
                         "verify existing application", T.BLOCKED,
                         str(receipt) if receipt else "none",
                         "exact-title history has a status but employer cannot be matched to the target; no repeat sent")
                lane.log("BLOCKED - history status is confirmed but employer identity is ambiguous; no repeat sent.")
                lane.summary()
                return 2
        if entry and entry.get("status"):
            receipt = lane.shot(c, "apply-history-duplicate-" + time.strftime("%Y%m%d%H%M%S"))
            lane.row(history["url"][:70], title[:70], entry.get("company", "-"), "-",
                     "verify existing application", T.APPLIED,
                     str(receipt) if receipt else "none",
                     "already submitted; exact-title history context: " + entry["context"][:220])
            lane.log("APPLIED - exact role is already confirmed in application history; no repeat sent.")
            lane.summary()
            return 0
        if entry:
            receipt = lane.shot(c, "apply-history-ambiguous-" + time.strftime("%Y%m%d%H%M%S"))
            lane.row(history["url"][:70], title[:70], entry.get("company", "-"), "-",
                     "verify existing application", T.BLOCKED,
                     str(receipt) if receipt else "none",
                     "exact title appears in history but nearby status is unverified: " + entry["context"][:220])
            lane.log("BLOCKED - exact title is in history but its application status is unclear; no repeat sent.")
            return 2
        lane.log("A1 navigate -> " + JOBS_URL)
        c.call_tool("browser_navigate", {"url": JOBS_URL})
        time.sleep(12)

        # A2 - locate the job's card by exact title, POLLING (the SPA hydrates late:
        # article count 0 at +10s cold, 63 at +12s. A fixed sleep read an empty list.)
        idx, sel_used = -1, None
        for _ in range(15):
            cards = T.read_cards(c, "naukri")
            sel_used = cards["selector"]
            names = [(cd.get("title") or "") for cd in cards["cards"]]
            hits = [i for i, nm in enumerate(names) if title and title in nm]
            if hits:
                idx = hits[0]
                break
            lane.log("   A2 wait cards: n=%s selector=%s" % (cards["n"], cards["selector"]))
            time.sleep(2)
        lane.log("A2 card index = %d (selector=%s)" % (idx, sel_used))
        if idx < 0:
            lane.row(JOBS_URL[:70], title[:70], "-", "-", "locate job card", T.BLOCKED,
                     "none", "card not found by exact title")
            return 2

        # Re-check the exact current card against the same resume-derived skill
        # gate used by the read-only matcher. A stale title or an unqualified card
        # must never reach the application flow.
        import lane_jobs as J
        matched_card = cards["cards"][idx]
        score, hits = T.score_card(matched_card.get("text"), J.SKILLS)
        if score < 2:
            lane.row(JOBS_URL[:70], title[:70], "-", score, "live role gate", T.BLOCKED,
                     "none", "current card below skill threshold; hits=" + ",".join(hits))
            lane.log("BLOCKED - current role no longer clears the matched-role gate.")
            return 2
        if "already applied" in (matched_card.get("text") or "").lower():
            lane.row(JOBS_URL[:70], title[:70], "-", score, "duplicate check", T.BLOCKED,
                     "none", "current card says already applied")
            lane.log("BLOCKED - portal marks this role already applied; no duplicate sent.")
            return 2
        company = T.card_company(matched_card)
        lane.log("LIVE MATCH gate score=%d hits=%s company=%s" % (score, ",".join(hits), company))

        # A3 - select the card, then press Apply. Naukri recommended-jobs cards carry
        # no <a>/onclick/React nav (element.click + event dispatch both no-op):
        # SELECT-THEN-APPLY is the proven mechanism (.tuple-check-box -> header button).
        sel = c._js(
            "(function(){var want=%s;var a=document.querySelectorAll('article');"
            "for(var i=0;i<a.length;i++){if((a[i].innerText||'').indexOf(want)>-1){"
            "var cb=a[i].querySelector('.tuple-check-box');if(cb){cb.click();return 'checked';}"
            "return 'no-checkbox';}}return 'nocard';})()" % json.dumps(title))
        lane.log("A3 select -> " + str(sel))
        time.sleep(2)
        ap = c._js(
            "(function(){var b=document.querySelector('.multi-apply-button')||"
            "Array.prototype.slice.call(document.querySelectorAll('button')).filter(function(x){"
            "return /^apply/i.test((x.innerText||'').trim());})[0];"
            "if(!b)return 'nobtn';if(b.disabled)return 'disabled';"
            "b.click();return 'clicked-apply';})()")
        lane.log("A4 apply -> " + str(ap))

        # A5 - wait for the recruiter panel and read the QUESTION itself (the panel
        # opens with a spinner + a header; the question renders seconds later).
        panel_q, in_flow = None, False
        page = {"url": JOBS_URL, "title": "", "body": ""}
        for _ in range(25):
            page = T.read_page(c)
            panel_q = T.read_recruiter_question(c)
            if panel_q:
                in_flow = True
                break
            low = page["body"].lower()
            if "answer all the recruiter" in low or "apply for this job" in low:
                in_flow = True
            time.sleep(2)
        after, low = page["url"], page["body"].lower()
        left_list = after != JOBS_URL and "recommendedjobs" not in after
        in_flow = in_flow or any(s in low for s in FLOW_SIGNALS)
        moved = left_list or in_flow
        p = lane.shot(c, "apply-03-after-apply-" + time.strftime("%Y%m%d%H%M%S"))
        lane.log("A5 url=%s left_list=%s in_flow=%s chars=%d"
                 % (after[:110], left_list, in_flow, len(page["body"])))
        if not moved:
            lane.log("   !! apply did not open a flow - BLOCKED (honest, not a fake DONE)")
            lane.row(after[:70], title[:70], "-", "-", "open apply flow", T.BLOCKED,
                     str(p) if p else "none", "select=%s apply=%s" % (sel, ap))
            return 3

        # A6 - answer the recruiter question(s): read question -> answer from the
        # operator's OWN record -> READ BACK -> Save -> next. Never invent an answer.
        seen, saves_ok, final, success = set(), 0, None, None
        for _round in range(1, 6):
            rq = T.read_recruiter_question(c)
            if not rq or rq in seen:
                break
            ran = T.answer_from_resume(rq)
            if not ran:
                lane.log("   !! not answerable from record -> BLOCKED: " + rq[:120])
                pf = lane.shot(c, "apply-05-blocked-" + time.strftime("%H%M%S"))
                lane.row(after[:70], title[:70], "-", "-", "recruiter question", T.BLOCKED,
                         str(pf) if pf else "none", "UNANSWERABLE Q=" + rq[:150])
                return 4
            seen.add(rq)
            lane.log("   ANSWERING: %s -> %s" % (rq[:110], ran))
            res = T.answer_and_save(c, rq, ran)
            lane.log("   fill elem=%s readback=%s save=%s"
                     % (res["elem"], str(res["actual"])[:25], res["save"]))
            if not res["ok"]:
                lane.log("   !! fill did NOT land - BLOCKED (not a fake APPLIED_STEP)")
                pf = lane.shot(c, "apply-05-fillfail-" + time.strftime("%H%M%S"))
                lane.row(after[:70], title[:70], "-", "-", "recruiter question", T.BLOCKED,
                         str(pf) if pf else "none",
                         "FILL FAILED elem=%s readback=%s" % (res["elem"], str(res["actual"])[:40]))
                return 4
            final = lane.shot(c, "apply-06-answered-%d-%s" % (_round, time.strftime("%H%M%S")))
            if str(res["save"]).startswith("clicked"):
                transitioned = False
                for _wait in range(15):
                    time.sleep(1)
                    success = _success_text(c)
                    next_q = T.read_recruiter_question(c)
                    if success or next_q != rq:
                        transitioned = True
                        break
                if transitioned:
                    saves_ok += 1
                else:
                    lane.log("   !! Save click produced no visible flow transition after 15s")

        if seen and saves_ok == len(seen) and not args.submit:
            lane.row(after[:70], title[:70], "-", "-", "recruiter questions answered",
                     T.APPLIED_STEP, str(final) if final else "none",
                     "answered %d gate(s); saved; no force-submit" % len(seen))
            lane.log("ANSWERED %d gate(s), Save clicked, read-back verified." % len(seen))
            lane.summary()
            return 0
        if seen and saves_ok != len(seen):
            lane.log("   !! answered but Save did not register -> BLOCKED (no honest submit)")
            lane.row(after[:70], title[:70], company, score, "recruiter questions answered",
                     T.BLOCKED, str(final) if final else "none",
                     "answered %d but save not confirmed" % len(seen))
            return 4

        # A successful Save may itself finish the portal flow. Otherwise perform a
        # single, explicit final-submit click only when the panel exposes one.
        success = success or _success_text(c)
        if args.submit and not success:
            submit = _click_final_submit(c)
            lane.log("A7 final submit -> " + json.dumps(submit, ensure_ascii=True))
            if submit.get("found"):
                for _ in range(15):
                    time.sleep(2)
                    success = _success_text(c)
                    if success:
                        break
            if not success and (submit.get("reason") == "apply panel missing" or submit.get("found")):
                checked = _verify_history(c, title, company)
                history_receipt = lane.shot(c, "apply-history-after-panel-close-" + time.strftime("%Y%m%d%H%M%S"))
                if checked.get("confirmed"):
                    entry = checked["entry"]
                    lane.row(checked["page"]["url"][:70], title[:70], entry.get("company", company), score,
                             "verify application history", T.APPLIED,
                             str(history_receipt) if history_receipt else "none",
                             "panel closed; exact-title history status=" + entry["status"] +
                             "; context=" + entry["context"][:180])
                    lane.log("APPLIED - application history confirms the role after panel close.")
                    lane.summary()
                    return 0
                lane.log("   history did not confirm submission: " +
                         str(checked.get("reason") or "exact title/status not found"))
            if not success:
                pf = lane.shot(c, "apply-07-submit-unverified-" + time.strftime("%Y%m%d%H%M%S"))
                detail = "submit=%s; no portal confirmation" % json.dumps(submit, ensure_ascii=True)
                lane.row(after[:70], title[:70], company, score, "final submission", T.BLOCKED,
                         str(pf) if pf else "none", detail[:240])
                lane.log("BLOCKED - no visible application confirmation; no retry was made.")
                lane.summary()
                return 5

        # APPLIED requires a portal success signal visible after the final action.
        page = T.read_page(c)
        if success or any(s in page["body"].lower() for s in SUCCESS):
            receipt = lane.shot(c, "apply-08-submitted-" + time.strftime("%Y%m%d%H%M%S"))
            lane.row(after[:70], title[:70], company, score, "application submitted", T.APPLIED,
                     str(receipt) if receipt else "none", "portal confirmation=" + str(success or "visible success text"))
            lane.log("DONE - portal confirmation visible in screenshot: %s" % (receipt or "SCREENSHOT FAILED"))
            lane.summary()
            return 0
        lane.log("   !! panel open but no recruiter question and no submission evidence"
                 " - BLOCKED (never a fake APPLIED)")
        lane.row(after[:70], title[:70], company, score, "open apply flow", T.BLOCKED,
                 str(p) if p else "none", "panel_open=%s no question rendered" % in_flow)
        return 4


if __name__ == "__main__":
    sys.exit(main(sys.argv))
