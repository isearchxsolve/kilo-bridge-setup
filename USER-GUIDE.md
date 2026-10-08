# User Guide — Autonomous Job Application Assistant

Welcome! This system is your autonomous job application assistant for **Naukri**, **Foundit**, **Indeed**, and **LinkedIn**.

It runs quietly in the background, finds relevant jobs matching your skills, fills out recruiter application forms accurately, and saves screenshot proofs for every action.

---

## ⚡ 3-Step Quick Start

Setting up takes less than 2 minutes.

### Step 1: Copy Your Resume PDF
Copy your resume PDF into this folder and name it:
```text
candidate-resume.pdf
```
*(No hardcoded file paths needed! The system automatically looks in the project folder.)*

### Step 2: Set Your Resume Hash
Open PowerShell in this folder and get the file hash:
```powershell
Get-FileHash -Algorithm SHA256 candidate-resume.pdf
```

Copy the 64-character hash and paste it into `candidate-profile.json`:
```json
{
  "resume_path": "candidate-resume.pdf",
  "resume_sha256": "PASTE_YOUR_SHA256_HASH_HERE"
}
```
> **Note:** That's the only configuration required! You never need to type your name, phone, email, or skills into any JSON file. The system reads everything directly and securely from your resume PDF.

### Step 3: Open Chrome & Log In
Open Google Chrome and make sure you are logged into:
- [Naukri](https://www.naukri.com)
- [Foundit](https://www.foundit.in)
- [Indeed](https://www.indeed.com)
- [LinkedIn](https://www.linkedin.com)

---

## 🚀 Running the Assistant

### Option 1: 24/7 Background Runner (Recommended)
Runs continuously in the background, checking portals, applying to matches, and resting between rounds:

- **Double-click:** `run-247.bat`  
  *or*
- **Run in PowerShell:**
  ```powershell
  powershell -ExecutionPolicy Bypass -File .\run-247.ps1
  ```

### Option 2: Run a Single Round
To run exactly one cycle across all 4 portals and immediately stop:
```powershell
python scripts\lane_all.py
```

### Option 3: Run an Individual Portal
You can run any portal individually:
```powershell
# Naukri Quick Profile Check
python scripts\lane_resume.py

# Naukri Mass Apply (applies up to 3 jobs)
python scripts\lane_mass_apply.py --limit 3

# Foundit Search & Gate Check
python scripts\lane_foundit.py

# Indeed & LinkedIn Market Discovery
python scripts\lane_market_probe.py

# LinkedIn Feed Monitor
python scripts\lane_linkedin_feed.py
```

---

## 📊 Checking Your Results

### 1. The Summary Report
Check [`evidence/employment-lane/latest-mission-report.md`](evidence/employment-lane/latest-mission-report.md) at any time to see:
- Total confirmed job applications.
- Current cycle status.
- Which roles were applied for and matched.

### 2. Screenshot Proofs
Every applied job and form step saves a timestamped screenshot in:
```text
evidence/employment-lane/
```
Look for files named:
- `mass-apply-success-*.png` (Application confirmed)
- `mass-apply-blocked-*.png` (Blocked by unconfirmed question)

### 3. The Activity Log
The full audit trail is recorded in:
```text
evidence/employment-lane/ledger.tsv
```

---

## 🛡️ Built-In Safety Rules

The assistant follows strict safety rules so you stay in total control:

1. **No Made-Up Information**: The assistant only provides facts that exist in your resume. It will never guess or make up a number, degree, or company.
2. **Honest Halts on Private Data**: If a recruiter asks for private data not in your resume (like a PAN number, Aadhaar, or custom hourly rate), the assistant will not guess. It safely skips the job and notes `BLOCKED` in the log.
3. **Respects Your Preferences**:
   - If your resume says "Remote only", it will never say "Yes" to relocating to on-site cities.
   - If a question asks if you reside in India, it checks your resume location.
4. **Never Touches Passwords or CAPTCHAs**: It will never type passwords or try to bypass security checks. If a login session expires, it halts that portal until you sign in.
5. **Never Spends Money**: It will never click paid promotions or subscriptions.

---

## ⚙️ Customizing Settings (Optional)

You can tweak how often the 24/7 runner cycles and how many jobs it applies for per round:

```powershell
powershell -ExecutionPolicy Bypass -File .\run-247.ps1 -IntervalSeconds 1200 -LimitPerRound 3
```

- `-IntervalSeconds 1200`: Wait 20 minutes between cycles (default: 1200s).
- `-LimitPerRound 3`: Maximum applications per round on Naukri (default: 3).

---

## ❓ Frequently Asked Questions

**Q: Does my resume need an absolute path like `C:\Users\...`?**  
**A:** No! Simply name your file `candidate-resume.pdf` in the project root folder. The system uses relative paths automatically.

**Q: What happens if a portal asks for OTP or CAPTCHA?**  
**A:** The assistant immediately halts on that portal and moves to the next. You can simply log in or solve the CAPTCHA in Chrome in your own time, and the next cycle will pick up automatically.

**Q: How do I stop the 24/7 runner?**  
**A:** Press `Ctrl + C` in the PowerShell/Command Prompt window running `run-247`.
