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
4. **NEVER TOUCH LOGIN CREDENTIALS.** Never request, read, or type a password, OTP, or
   security code. If login, MFA, or CAPTCHA appears, stop that portal and report it.
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
