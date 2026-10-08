# User Guide — 24/7 Autonomous Employment Lane Package

A production-grade, zero-defect autonomous job application and market intelligence engine spanning **Naukri**, **Foundit**, **Indeed**, and **LinkedIn**.

---

## 1. System Overview & Architecture

This package runs continuously (24/7) to discover matching senior leadership and architect roles, perform multi-step recruiter screening dialogues, submit verified applications, and monitor job feeds.

### Core Foundations
* **Sole Source of Truth (Allowlist)**: The candidate's pinned resume PDF (named in `candidate-profile.json` and verified against its SHA-256 hash). All personal facts, skills, tenures, locations, and preferences are parsed at runtime by `scripts/resume_facts.py`.
* **Intelligence Layer**: **Free OpenCode + NVIDIA NIM Nemotron-120B Super** (`nvidia/nemotron-3-super-120b-a12b`). Zero `agy` dependency.
* **Browser Automation**: CDP-level browser actions through `@agent360/browser-mcp` on your authenticated Chrome profile.
* **The 11 Operating Laws**: Strict adherence to no hallucinated data (Law 2), screenshot receipts (Law 1), human gate safety (Laws 4 & 5), and honest halts over faked completions (Law 11).

---

## 2. Prerequisites

1. **Operating System**: Windows 10/11 (PowerShell 5.1 or PowerShell 7+).
2. **Runtimes**:
   - Python 3.11+ (with virtual environment in `venv/`).
   - Node.js 20+ (for OpenCode CLI and MCP).
3. **Browser**:
   - Google Chrome running with the **Agent360** extension installed.
   - User logged into the target portals (**Naukri**, **Foundit**, **Indeed**, **LinkedIn**) in the authenticated Chrome profile.
4. **OpenCode & Nemotron**:
   - OpenCode installed (`npm i -g opencode-ai`).
   - Configured with NVIDIA NIM (`~/.config/opencode/opencode.jsonc`) using the free `nvidia/nemotron-3-super-120b-a12b` model.

---

## 3. Quick Start — Running the System

### Option A: 24/7 Autonomous Daemon (Recommended)
Runs an infinite autonomous loop across all 4 employment lanes with crash recovery and jittered cycle pacing (default ~20 minutes between cycles):

```powershell
powershell -ExecutionPolicy Bypass -File .\run-247.ps1
```

Or double-click:
```bat
run-247.bat
```

### Option B: Single Full-Cycle Pass
Runs one complete pass across all 4 portals (Naukri Profile, Naukri Mass Apply, Foundit Fit Gating, Indeed/LinkedIn Market Search & Feed) and exits cleanly:

```powershell
python scripts\lane_all.py
```

### Option C: Running Individual Lanes
You can run any specific portal independently:

```powershell
# Lane 1: Naukri Profile Verification & Recommended Scan
python scripts\lane_resume.py

# Lane 2: Naukri Dynamic Discovery & Mass Apply (apply limit: 3)
python scripts\lane_mass_apply.py --limit 3

# Lane 3: Foundit Search & Fit Gating
python scripts\lane_foundit.py

# Lane 4A: Indeed & LinkedIn Market Discovery
python scripts\lane_market_probe.py

# Lane 4B: LinkedIn Feed Engagement
python scripts\lane_linkedin_feed.py
```

---

## 4. Configuration & Candidate Setup

### Candidate Profile Pointer (`candidate-profile.json`)
The candidate record contains **zero hardcoded personal values**. It only points to the pinned resume PDF:

```json
{
  "resume_path": "C:\\Users\\Admin\\Downloads\\Resume.pdf",
  "resume_sha256": "BF2FED8AFACCD67BCA87BBE50F2CF0A43956ED1025DFD068EDCB0719BC5F1394"
}
```

To switch candidates:
1. Place the new candidate's PDF in a secure directory.
2. Calculate its SHA256:
   ```powershell
   Get-FileHash -Algorithm SHA256 "path\to\resume.pdf"
   ```
3. Update `resume_path` and `resume_sha256` in `candidate-profile.json`.

### Cycle Pacing & Jitter
You can adjust cycle intervals directly when invoking `run-247.ps1`:
```powershell
powershell -ExecutionPolicy Bypass -File .\run-247.ps1 -IntervalSeconds 1800 -JitterSeconds 180 -LimitPerRound 5
```
* `-IntervalSeconds`: Base sleep between cycles (default: `1200`s = 20 min).
* `-JitterSeconds`: Random sleep variation to avoid predictable intervals (default: `120`s).
* `-LimitPerRound`: Maximum job applications per round on Naukri (default: `3`).

---

## 5. Recruiter Screening Intelligence & The 11 Laws

The engine uses **Nemotron-120B Super** grounded strictly in candidate resume facts to answer multi-turn screening questions.

### Strict Safety & Integrity Rules:
1. **Residency vs. Relocation**:
   - Questions asking about *residing in India* resolve to `"Yes"` (candidate resides in Kolkata, India).
   - Questions asking to *relocate to on-site cities* resolve to `"No"` because candidate's verified preference is `"Open to Remote only"`.
2. **Technological Release Boundaries**:
   - Model Context Protocol (MCP) experience is bounded to max `1` year (late 2024).
   - Generative AI / LLM / RAG / LangChain experience is bounded to max `2` years (late 2022).
   - Overall AI/ML / Python / AWS experience is bounded to `8` years.
   - Total career experience is `22` years.
3. **Availability & Daily Commitment**:
   - Questions asking about joining immediately or dedicating 4–5 daily hours resolve to `"Yes"` based on verified fact `AVAILABILITY: Available Now`.
4. **Honest Halts on Unconfirmed Facts (Law 2 & Law 11)**:
   - If a recruiter demands a fact not in the resume (e.g. **PAN card number**, **hourly billing rate**, or prior interview history at that specific company), the engine **never invents data**.
   - It records `BLOCKED` in the ledger, saves a screenshot, closes the drawer, and moves to the next job.

---

## 6. Audit Ledger & Evidence

Every single action is recorded in real time to the tab-separated ledger:
* **Ledger Path**: [`evidence/employment-lane/ledger.tsv`](evidence/employment-lane/ledger.tsv)
* **Format**: Exactly 10 tab-separated columns:
  ```
  ts | portal | query_or_source | role | company | match_score | step | status | receipt | note
  ```
* **Status Values**:
  - `MATCHED`: Job cleared skill gate ($\ge 2$ matching skills) and remote location filter.
  - `NO_MATCH`: Job rejected due to skill gate (< 2) or on-site location mismatch.
  - `APPLIED`: Application confirmed by portal modal/banner or history tuple.
  - `BLOCKED`: Step halted due to unconfirmed fact (PAN, hourly rate) or external redirect.
  - `OK`: Action completed successfully (e.g. feed engagement, profile check).

### Screenshot Receipts
Per **Law 1** (*The screenshot is the receipt*), all actions produce timestamped PNGs in `evidence/employment-lane/`:
* `mass-apply-success-*.png`: Confirmed application submissions.
* `mass-apply-blocked-*.png`: Exact recruiter questions or obstacles that blocked submission.
* `mass-apply-handoff-*.png`: External ATS handoffs.
* `40-naukri-recommended-*.png`, `50-foundit-search-*.png`, `60-indeed-search-*.png`, `60-linkedin-search-*.png`, `70-linkedin-feed-*.png`.

---

## 7. Troubleshooting & FAQs

| Symptom | Cause | Solution |
| :--- | :--- | :--- |
| **"Waiting for input" in IDE alerts** | Recruiter question in log contained text like *"Please give PAN number"* | This is a passive terminal regex match. The script never blocks on stdin; it automatically records `BLOCKED` and continues. |
| **Agent360 "Not connected"** | WebSocket bridge starts on demand when a CDP tool is invoked | The extension popup shows "Not connected" when idle. It automatically bridges when a cycle begins. |
| **OTP or CAPTCHA appears** | Human gate encountered on portal | Per Laws 4 & 5, human gates must never be automated. Complete the login or verification manually in Chrome. The runner will proceed on the next cycle. |
| **Single Browser Owner Error** | Multiple scripts trying to access Chrome simultaneously | Ensure only one instance of `run-247.ps1` or individual lane script is running at a time (Law 7). |
