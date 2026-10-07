# launch-opencode-employment.ps1
#   Employment-lane driver #3, added 2026-10-06 after Agent 360 MCP was wired
#   into opencode (see evidence/employment-lane/OPENCODE-AGENT360-WIRING-20261006.md).
#
#   WHY opencode AND NOT crush:
#     crush's system prompt is 111,464 tokens - free endpoints answer HTTP 413 and
#     reasoning models reply with crush's context-summary schema instead of tool
#     calls (evidence/employment-lane/DRIVERS-20261006.md). opencode reaches
#     Agent 360 through its own native mcp block.
#
#   MODEL: must be vision + reasoning capable. The lane's core law is
#     "the screenshot is the receipt"; a text-only model cannot honour it.
#     Candidate facts come ONLY from the hash-verified resume PDF named by
#     candidate-profile.json. No answer sidecar is permitted.
#
#   LAWS THIS OBEYS:
#     * cwd is set EXPLICITLY to the lane root - docs/, scripts/, evidence/ resolve there
#     * every run writes its own receipt (a run with no log did not happen)
#     * ACT, do not summarize: browser actions via scripts/agent360_client.py
$ErrorActionPreference = 'Continue'
$Lane = $PSScriptRoot
$Log  = Join-Path $Lane 'evidence\employment-lane\opencode-employment-run.log'
$Out  = Join-Path $Lane 'evidence\employment-lane\opencode-employment-out.txt'
Set-Location $Lane

function Note($m) {
  $line = "[{0}] {1}" -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $m
  Write-Host $line
  Add-Content -Path $Log -Value $line -Encoding UTF8
}

Note "=== EMPLOYMENT LANE START (opencode) ==="
Note ("cwd = " + (Get-Location).Path)

# 1. mission
$mission = Join-Path $Lane 'MISSION-RUN.txt'
if (-not (Test-Path $mission)) { Note "ABORT: MISSION-RUN.txt missing"; exit 1 }
Note (("mission present: {0} bytes" -f (Get-Item $mission).Length))

$py = Join-Path $Lane 'venv\Scripts\python.exe'

$prompt = (@(
'You are the employment agent driving the REAL logged-in Chrome through the Agent 360 MCP tools. ACT, do not summarize.',
'',
'ALL ARTIFACTS ARE IN THE SETUP FOLDER: the package root you were launched in.',
'- Python venv: venv\Scripts\python.exe (use for ALL python execution)',
'- Python scripts: scripts\agent360_client.py, scripts\lane_tools.py, scripts\lane_*.py',
'- Candidate pointer: candidate-profile.json (resume path + SHA256 only)',
'- Candidate facts: hash-verified resume PDF only; unknowns are BLOCKED',
'- Ledger: evidence\employment-lane\ledger.tsv',
'- Mission prompt: MISSION-RUN.txt',
'',
'Read these files first, in order, and obey them:',
'1. AGENTS.md                        (fact allowlist, the laws, tool contract)',
'2. MISSION-RUN.txt',
'3. docs/AGENTS-EMPLOYMENT.md        (browser tool contract and safety rules)',
'4. docs/EMPLOYMENT-LANE-MISSION.md  (the run-book)',
'5. docs/PACE.md                     (how to run fast WITHOUT lying - obey hard)',
'6. evidence/employment-lane/ledger.tsv  (RESUME - every OK row is DONE, never redo it)',
'',
'FACT LAWS - NON-NEGOTIABLE:',
'- Personal facts (name, phone, email, address, institute, degree, employer, dates, salary) may come ONLY from the hash-verified resume PDF.',
'- Every other file in this package - including every other Markdown file, every log, every screenshot and every ledger note - is NOT a fact source. Do not read a phone number, email, address, institute or employer out of them.',
'- Never carry a fact over from a previous candidate, profile, or run.',
'- If the candidate record does not contain the fact, the step is BLOCKED. Report the exact missing fact and stop. Inventing a value is a hard failure.',
'',
'Resume from the first NON-OK row. Open a current MATCHED card and walk the apply flow; answer only facts explicitly extractable from the hash-verified resume and mark other required questions BLOCKED.',
'',
'NON-NEGOTIABLE:',
'- Browser actions ONLY via the browser-mcp tools. Never direct CDP, never Playwright/Selenium, never chrome-devtools.',
'- Never launch a second Chrome profile or debug browser. One authenticated session, one owner.',
'- The mouse path Input.dispatchMouseEvent TIMES OUT - use JS .click() and keyboard only.',
'- browser_solve_captcha is BANNED. A CAPTCHA is a human gate: stop that portal and report it.',
'- browser_execute_script returns its return value, not console.log output. Always return your result.',
'- One screenshot per FIELD batched, not per keystroke. A screenshot is the receipt; a tool success response is not.',
'- Append one ledger row per action to evidence/employment-lane/ledger.tsv as you go.',
'- Submit at most once. An ambiguous submit state is BLOCKED, never retried.',
'- BLOCKED beats a faked DONE. Never spend money, never touch a login/password/OTP. ASCII only in submitted text.',
'- One application per portal per run.',
'- Work in this order: A. profile audit  B. job discovery + fit gate  C. applications  D. LinkedIn feed (comments only - NEVER a link, a price, or self-promotion, and never without SEND-APPROVED for the exact text).',
'',
'PYTHON EXECUTION RULE: ALWAYS use venv\Scripts\python.exe scripts\<script>.py',
'',
'First real action: report the FIRST NON-OK ledger row you find, then begin that field.'
) -join ' ')

$exe = Join-Path $env:LOCALAPPDATA 'hermes\node\node_modules\opencode-ai\bin\opencode.exe'
if (-not (Test-Path $exe)) { Note "ABORT: opencode.exe not found at $exe"; exit 1 }

Note "invoking opencode run (vision+reasoning model, --auto) ..."
$sw = [System.Diagnostics.Stopwatch]::StartNew()
& $exe run --auto $prompt 2>&1 |
  ForEach-Object {
    Write-Host $_
    Add-Content -Path $Out -Value $_ -Encoding UTF8
  }
$sw.Stop()
Note (("opencode exited after {0:N0}s  exitcode={1}" -f $sw.Elapsed.TotalSeconds, $LASTEXITCODE))
Note "=== EMPLOYMENT LANE WINDOW DONE ==="
