# WORK LOG - kilo-bridge-setup

Living record of work on the employment-lane launcher and package. One dated
section per session, newest first. Facts only, with receipts where a claim is
made. Candidate personal values are never copied here (see AGENTS.md section 1;
the pinned resume PDF is the sole fact source).

---

## 2026-10-07 - Launcher grading hardened; live -Launch run graded honest RED; latent false-red heading defect fixed

### Goal
Prove the employment-lane OpenCode launcher grades green only on a real APPLIED
row written *this run* with an in-package receipt, and remove any path that could
grade green without one.

### Done
- Root-caused the earlier false-green: prior APPLIED rows cited receipts outside
  the package (D:\anonym\delivery\...), so a run could look finished with no
  proof inside the package.
- Hardened `kilo-bridge-setup.ps1`:
  - Ledger length snapshot is taken BEFORE the agent starts; only rows added this
    run are graded (`$RowsAdded` / `$NewRows`).
  - `$AppliedWithReceipt` counts APPLIED rows whose receipt path resolves inside
    `evidence\employment-lane\` and really exists; `$BadReceiptRows` flags the
    rest and blocks the run.
  - Policy gate requires `browser-mcp_browser_execute_script = allow` (the JS
    interactive path; the CDP mouse path times out at 1500 ms per call here).
- Ran a live `-Launch` (wrapper PID 6608, ~44 min, ended 21:39:43).
  - This run appended 23 ledger rows, 0 APPLIED
    (4 BLOCKED: Naukri OTP, Naukri 22-skill cap, Foundit CAPTCHA, LinkedIn
    unresponsive; 14 NO_MATCH; 2 MATCHED; 3 OK).
  - All receipts resolve inside the package (`evidence\employment-lane\`).
  - Launcher rendered an honest RED:
    `MISSION-AGENT-VERDICT: INCOMPLETE - no final report`, `[FAIL]`, exit 1.
    No false green.

### Key finding (latent false-red)
- The INCOMPLETE verdict was a misdiagnosis. The agent DID emit the four report
  sections, but as `## ## Profile changes` (doubled hash). The detector regex
  `^\s*#{0,3}\s*<title>\s*:?\s*$` did not match the doubled-hash form, and that
  check runs BEFORE the `$AppliedWithReceipt` green branch. A future genuine
  APPLIED run could therefore be graded INCOMPLETE. Latent false-red.

### Fix (applied, verified)
- Detector regex replaced with `(?im)^\s*(?:#{1,6}\s*)*<title>\s*:?\s*$`, which
  matches single-hash, doubled-hash and plain-text headings while still requiring
  the heading to sit on its own line.
- Note: this edit was written to disk by a concurrent sibling session (mtime
  21:43:04) while this run was still being investigated; it is the exact change
  identified here. Diff against the pre-fix backup shows only that regex change
  plus its explanatory comment. No other file changed.

### Validation (all green; current file SHA256 D3E7EC5A...5640EE)
- PowerShell parse: OK.
- Section regex vs the real run output: all four sections match.
- Gate sim - real output + 0 APPLIED  -> RED:NO-APPLICATION (honest).
- Gate sim - doubled/single hash + APPLIED with in-package receipt -> GREEN.
- Negative headings (prose that merely contains the words) do not match.
- Policy gate: `employment-mission` resolves; all 13 browser tools allow;
  `edit`/`webfetch` = deny are tolerated.
- `-Launch`-less smoke: `SETUP-VERDICT: READY`, exit 0.
- Ledger audit: the only 3 APPLIED rows are prior-run rows citing
  `D:\anonym\delivery\...` receipts; they are inert because only this-run rows
  are graded, and the ledger is append-only per AGENTS.md.

### Verdict
- This run: honest RED (0 APPLIED). The remaining walls are genuine portal gates
  (Naukri OTP / recruiter questions, Foundit CAPTCHA), not launcher defects, and
  must stay BLOCKED under AGENTS.md laws 4 and 5.
- The launcher now grades green only on a this-run APPLIED row with an
  in-package receipt.

### Artifacts
- Console + verdict: `evidence\employment-lane\launcher-console-20261007-205542.txt`
- Agent output/log: `evidence\employment-lane\mission-agent-output.txt`, `mission-agent-run.log`
- Ledger: `evidence\employment-lane\ledger.tsv`
- Backups: `_backup-fix\kilo-bridge-setup.20261007-214230.ps1` (pre-fix),
  `_backup-fix\kilo-bridge-setup.20261007-214856.ps1` (post-fix, identical to current)