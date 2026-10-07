# launch-crush-super120.ps1
#   Employment lane driver on the crush backend.
#   Fixed 2026-10-06 after the token-hang RCA
#   (evidence/employment-lane/RCA-TOKEN-HANG-20261006.md):
#     * cwd is set EXPLICITLY to the lane root (crush resolves relative paths
#       - docs/, evidence/, scripts/ - against it; a wrong cwd = no mission files)
#     * a COLD sweep-browser.token is cleared defensively before start
#       (the client also self-heals now, but a clean start costs nothing)
#     * every run writes its own receipt so silence is never mistaken for work
$ErrorActionPreference = 'Continue'
$Lane = $PSScriptRoot
$Log  = Join-Path $Lane 'evidence\employment-lane\crush-super120-run.log'
Set-Location $Lane

function Note($m) {
  $line = "[{0}] {1}" -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $m
  Write-Host $line
  Add-Content -Path $Log -Value $line -Encoding UTF8
}

Note "=== EMPLOYMENT LANE START (Super-120B) ==="
Note ("cwd = " + (Get-Location).Path)

# 1. defensive: neutralise a cold browser token (age > 300s is not a driver)
$tok = Join-Path $Lane 'war-log\sweep-browser.token'
if (Test-Path $tok) {
  $age = ((Get-Date) - (Get-Item $tok).LastWriteTime).TotalSeconds
  if ($age -gt 300) {
    try { Remove-Item $tok -Force -ErrorAction Stop; Note (("cleared COLD token (age {0:N0}s)" -f $age)) }
    catch { Note (("could not remove cold token (age {0:N0}s) - client will overwrite-take it" -f $age)) }
  } else { Note (("token present but FRESH (age {0:N0}s) - leaving it" -f $age)) }
} else { Note "token absent (clean start)" }

# 2. mission
$mission = Join-Path $Lane 'MISSION-RUN.txt'
if (-not (Test-Path $mission)) { Note "ABORT: MISSION-RUN.txt missing"; exit 1 }
Note (("mission present: {0} bytes" -f (Get-Item $mission).Length))

$prompt = (@(
'You are the employment agent driving the REAL logged-in Chrome through the Agent 360 MCP tools. ACT, do not summarize.',
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
'- Personal facts (name, phone, email, address, institute, degree, employer, dates, salary) may come ONLY from candidate-profile.json, its hash-verified resume, and the configured answers file.',
'- Every other file in this package - including every other Markdown file, every log, every screenshot and every ledger note - is NOT a fact source.',
'- Never carry a fact over from a previous candidate, profile, or run.',
'- If the candidate record does not contain the fact, the step is BLOCKED. Report the exact missing fact and stop.',
'',
'Resume from the first NON-OK row.',
'',
'NON-NEGOTIABLE:',
'- Browser actions ONLY via the browser-mcp tools. Never direct CDP, never Playwright/Selenium, never a second Chrome profile.',
'- The mouse path Input.dispatchMouseEvent TIMES OUT - use JS .click() and keyboard only.',
'- browser_solve_captcha is BANNED. A CAPTCHA is a human gate: stop that portal and report it.',
'- browser_execute_script returns its return value, not console.log output. Always return your result.',
'- One screenshot per FIELD batched, not per keystroke. A screenshot is the receipt; a tool success response is not.',
'- Append one ledger row per action to evidence/employment-lane/ledger.tsv as you go.',
'- Submit at most once. An ambiguous submit state is BLOCKED, never retried.',
'- BLOCKED beats a faked DONE. Never spend money, never touch a login/password/OTP. ASCII only in submitted text.',
'- One application per portal per run.',
'- Work in this order: A. profile audit  B. job discovery + fit gate  C. applications  D. LinkedIn feed (comments only, never without SEND-APPROVED for the exact text).',
'',
'First real action: report the FIRST NON-OK ledger row you find, then begin that field.'
) -join ' ')

Note "invoking crush run (Super-120B) ..."
$OutFile = Join-Path $Lane 'evidence\employment-lane\crush-super120-out.txt'
$sw = [System.Diagnostics.Stopwatch]::StartNew()
$crushCmd = Join-Path $env:LOCALAPPDATA 'hermes\node\crush.cmd'
& $crushCmd run --quiet $prompt 2>&1 |
  ForEach-Object {
    Write-Host $_
    Add-Content -Path $OutFile -Value $_ -Encoding UTF8
  }
$sw.Stop()
Note ("crush exited after {0:N0}s  exitcode={1}" -f $sw.Elapsed.TotalSeconds, $LASTEXITCODE)
Note "=== EMPLOYMENT LANE WINDOW DONE ==="