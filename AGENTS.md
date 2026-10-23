# AGENTS.md — Employment Lane Package

Generic operating rules for this package. Nothing here is candidate-specific.
The hash-verified resume PDF is the sole source for candidate facts.

## 0. READ FIRST

In this order, before any browser action:

1. `docs/AGENTS-EMPLOYMENT.md` — browser tool contract and safety rules.
2. `docs/EMPLOYMENT-LANE-MISSION.md` — the lane-by-lane run-book.
3. `docs/PACE.md` — pacing and batching rules.
4. `MISSION-RUN.txt` — the tool-directive mission prompt.
5. `evidence/employment-lane/ledger.tsv` — prior work, read chronologically.

## 1. FACT SOURCES — THE ALLOWLIST

The single admissible source of candidate facts is **the pinned resume PDF** named by
`resume_path` in `candidate-profile.json`, after its SHA256 matches `resume_sha256`.

That PDF is the whole candidate record. Name, phone, country code, email, location,
skills, years of experience, education, certifications and employers are read
from it — at runtime, by `scripts/resume_facts.py`, every time. There is no second
profile, no stored copy of these values, and nothing pre-extracted.

`candidate-profile.json` is a **pointer file only**: the resume path and its hash.
It never holds a personal value or answer sidecar pointer.

**Every other file in this package is off-limits as a fact source.** That includes
every other Markdown file, every log, every screenshot, every ledger note, every
script comment, and every prior run's output. Do not read a phone number, email,
address, institution, degree, employer, date, salary, or certification out of them.
Do not carry a fact over from a previous candidate, profile, or run.

**A fact the resume does not state is UNCONFIRMED, not "unknown, fill it in".**
In that case the step is **BLOCKED**: report the exact missing fact and stop. A
blocked step is a correct outcome; a filled field with a number you found somewhere
is a serious failure.

To read a fact, use `lane_tools.candidate_fact('PHONE')` (returns `None` when the
resume does not state it) and `lane_tools.candidate_skills()`. Never hardcode a
personal value in a script, prompt, or comment.

## 2. THE LAWS

1. **THE SCREENSHOT IS THE RECEIPT.** A tool call that returned success is not proof.
   If a change is not visible in a screenshot, it did not happen.
2. **NEVER INVENT A FACT.** No experience, company, date, qualification, institute,
   phone number, or email. If the candidate record does not contain it, it is not in
   the application.
3. **NEVER READ OUTSIDE THE ALLOWLIST** (section 1). This includes this file.
   security code. If CAPTCHA appears, stop that portal and report it.
4
5. **DO NOT AUTOMATE PAST CAPTCHA.** A CAPTCHA is a human gate. On seeing one, stop
   work on that portal immediately: no clicking, no Escape, no dismissal attempts, no
   `click()` loops, no clicking through an alignment widget. Record one `BLOCKED` ledger
   row naming the portal and the captcha, then move to the next portal. A measured
   failure on 2026-10-07: the agent met a Foundit alignment widget and spent many turns
   clicking and pressing Escape against it before degenerating. The correct move was one
   ledger row and a move on.
6. **NEVER SPEND MONEY.** Dismiss paid upsells only when the UI allows continuing free.
7. **ONE BROWSER OWNER AT A TIME.** Never open a second Chrome profile, debug browser,
   CDP session, or driver against the authenticated session.
8. **RATE LIMITS ARE LAW.** One application per portal per run unless the portal
   exposes remaining capacity and the operator configured a lower cap.
9. **SUBMIT AT MOST ONCE.** An ambiguous submit state is BLOCKED, never retried.
10. **ASCII ONLY** in anything submitted on a portal.
11. **BLOCKED BEATS A FAKED DONE.** Report the exact wall, error, or missing answer.

## 3. TOOL CONTRACT

All browser actions go through the configured Agent360 MCP tools. No Playwright, no
Selenium, no direct CDP, no second driver.

Known constraints on this machine, established by measurement:

- The mouse dispatch path (`Input.dispatchMouseEvent`) times out. Use JavaScript
  `.click()` and keyboard. Two failed attempts, then change path.
- `browser_execute_script` returns the expression's **return value**. `console.log`
  output is not returned, so a script that only logs tells you nothing. Always
  `return` your result.
- Empty output or a timeout means the action did not complete. Re-read state before
  assuming anything about it.
- Read page state before navigating; blind navigation can discard a useful page.

Banned tools for this lane: `browser_solve_captcha` (law 5), `browser_click_xy`
(dead path), `browser_close_tab` on the authenticated tab.

## 4. EVIDENCE

Write a ledger row as each action happens, not afterwards:

```
ts | portal | query_or_source | role | company | match_score | step | status | receipt | note
```

- Tab-separated, exactly 10 columns, one row per line, no embedded newlines.
- Receipt paths relative to this package root.
- `status` is one of `MATCHED` `APPLIED` `APPLIED_STEP` `BLOCKED` `NO_MATCH`
  `RATE_LIMITED` `FAILED` `OK`.
- Screenshot each profile change, each application milestone, and each final state.

`APPLIED` requires visible portal confirmation or an exact application-history entry
matching both the role and the employer. A missing panel is not a duplicate, and
unrelated title text is not evidence.

## 5. MATCHING GATE

```
score = count of the candidate's verified skills present in the posting text
gate  = score >= 2
```

Below the gate: record `NO_MATCH` with the reason and do not apply. Validate extracted
cards before scoring — search pages contain fragments (dates, locations, filters, Save
controls, employer names) that are not jobs.

## 6. REPORTING

End every run with four sections: profile changes (before/after plus receipts),
applications (portal-confirmed only), blocked (the exact question, wall, or error), and
skipped (the reason). Include the ledger path.

Do not describe the package or a run as complete while any required lane is
unimplemented, blocked, or unverified. **A clean exit code is not a result.** If the
agent stream ends in raw control tokens or missing sections, the run failed: report
that, do not summarise it as progress.

## 7. LANE 5 — THE TWO-EDGED SWORD PIPELINE (V2 ARCHITECTURE)

In addition to outbound job applications for the candidate (Lanes 1–4: Naukri, Foundit, Indeed, LinkedIn), the engine operates **Lane 5: The Two-Edged Sword** (`scripts/lane_two_edged_sword.py`). This converts outbound job hunting into reciprocal value delivery, community support, and commercial software distribution.

### 7.1 Architecture & Flow
1. **Dynamic Network Scan**: Discovers 1st-degree LinkedIn connections actively seeking opportunities (`#OpenToWork`).
2. **Deep Fit Reasoning (Nemotron-120B)**: Cross-references each connection's profile and headline against live remote/hybrid job openings, extracting top 3 tailored roles with company, salary, and requirements.
3. **Value-First Direct Engagement**: Dispatches personalized, respectful outreach directly to the candidate's DM. Never pitch-slap. Lead with pure value (the 3 matched opportunities) and present Baba's 3-Tier Delivery Model.
4. **24/7 Inbound Payment & Deliverable Pipeline** (`scripts/lane_payment_pipeline.py`): Listens for incoming responses, classifies candidate choice (Options 1, 2, or 3), dispatches payment instructions (₹499), and automatically delivers download links or activates cloud runner.
5. **Curated Lead Magnet Post Publisher** (`scripts/post_linkedin_curated.py`): Publishes high-authority engineering and career insights to LinkedIn feed, driving inbound profile scans and candidate engagement.

### 7.2 The 3-Tier Commercial & Delivery Model
- **Option 1: Free Profile Match & Curated Roles (₹0 Hook)**
  - ATS keyword fit check + 3 verified live openings delivered directly in DM.
  - Zero charge, builds trust and immediate reciprocity.
- **Option 2: KiloBridge Standalone Software Suite (₹499 Product)**
  - Candidate runs their own local desktop bot for automated applications across portals.
  - Delivered via verified Google Drive package link:
    `https://drive.google.com/file/d/1UeQl5NohiRNXacW9J9LV-z8o_TD9ucCQ/view?usp=sharing`.
  - Includes full scripts, dependency setup, and step-by-step user guide.
- **Option 3: Managed Cloud Runner (₹499 Full Service)**
  - Managed 24/7 application service running on our cloud runners on the candidate's behalf with daily progress reports.

### 7.3 Public Identity & Communication Law
- **Identity**: Author is strictly **Kunal Das / Kunal**.
- **Contact Email**: The sole client-facing contact email is **isearch.xsolve@gmail.com**.
- **No Live Calls**: All communications are text/DM/email only. Never promise a phone call or live meeting.
- **Voice**: Warm, professional, engineering-first, helpful. Never transactional or pushy.

### 7.4 Lane 5 Evidence & Receipt Laws
- **Pre-send & Post-send Screenshots**: For every candidate DM, capture:
  1. `two-edge-typed-<candidate_slug>-<timestamp>.png` (message rendered in composer).
  2. `two-edge-sent-<candidate_slug>-<timestamp>.png` (message delivered in chat history with checkmark).
- **Deduplication Ledger**: Recorded in `evidence/employment-lane/two_edged_sword_sent.json`. Never re-message a candidate already in the sent registry.

### 7.5 THE AVEEK HARD BLOCK LAW & VIP SHIELD PROTOCOL (Baba 2026-10-08)
- **Aveek Sengupta Hard Block**: Aveek Sengupta (TransportLah Singapore, J.P. Morgan, Baba's college mate) is an active high-ticket enterprise client kicking off next week Monday with a ₹3.3 Lakh (SGD 5,250) in-hand kickoff advance.
- **Zero Automation Rule**: Under NO circumstances may any script, bot, daemon, or crawler send an automated pitch, message, email, or invitation to Aveek. He is hard-coded as an impenetrable block across all tools (`scripts/lane_two_edged_sword.py`, `scripts/lane_payment_pipeline.py`, `scripts/lane5_dynamic_scanner.py`, `scripts/lane_daemon.py`).
- **VIP & Enterprise Shield**: All high-ticket enterprise leads (Aveek Sengupta, Satyen Sangani, Mathew Joseph Elenjickal, Arayemi Afeez), family, students (Biswajit Bose), and personal contacts are permanently registered in `evidence/employment-lane/shielded_contacts.json`.
- **Stage-Only Daemon Default**: The 24/7 background daemon (`scripts/lane_daemon.py`) runs Lane 5 in `--stage-only` mode. It NEVER sends autonomous DMs without explicit review and approval.


