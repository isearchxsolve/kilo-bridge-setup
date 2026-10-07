<#
  Kilo Bridge client setup and employment mission-agent launcher.
  All package paths are rooted at this script; no D:\anonym, vault, OpenCode,
  model key, or machine-specific project config is read or edited.

  Launch the configured mission agent:
    powershell -ExecutionPolicy Bypass -File .\kilo-bridge-setup.ps1 -Launch
  One real, explicitly authorized Naukri application:
    powershell -ExecutionPolicy Bypass -File .\kilo-bridge-setup.ps1 -Launch `
      -SubmitOne -Title "Exact matched role title"
  Install the Agent360 MCP package locally in this folder if missing:
    powershell -ExecutionPolicy Bypass -File .\kilo-bridge-setup.ps1 -InstallMcp
#>
[CmdletBinding()]
param(
    [switch]$Launch,
    [switch]$SubmitOne,
    [switch]$InstallMcp,
    [string]$Title,
    [string]$CandidateConfig = 'candidate-profile.json'
)

$ErrorActionPreference = 'Stop'
$Root = $PSScriptRoot
$Scripts = Join-Path $Root 'scripts'
$Evidence = Join-Path $Root 'evidence\employment-lane'
$Runtime = Join-Path $Root '.runtime'
$Py = $null
$Node = $null
$Mcp = $null
$OpenCode = $null
# Mission model. Chosen by measurement, not preference: a read-only shell smoke on
# 2026-10-07 (scripts\_model_smoke.ps1) showed nano-omni and glm-5.3-flash could not
# follow a shell instruction (glm stalled with no output), while super-120b executed
# the exact command and returned its stdout. The mission needs correct tool/shell
# behavior more than vision, so the stronger executor is the default.
$MissionModel = 'nvidia/nvidia/nemotron-3-super-120b-a12b'

function Fail([string]$Message) {
    Write-Host "[FAIL] $Message" -ForegroundColor Red
    exit 1
}

Write-Host 'Kilo Bridge standalone employment agent launcher' -ForegroundColor Cyan
Write-Host "Package root: $Root"

if ($SubmitOne -and -not $Launch) { Fail '-SubmitOne requires -Launch.' }
if ($SubmitOne -and [string]::IsNullOrWhiteSpace($Title)) { Fail '-SubmitOne requires -Title with the exact current matched role.' }
if (-not $SubmitOne -and -not [string]::IsNullOrWhiteSpace($Title)) { Fail '-Title is only used with -SubmitOne.' }

# Prefer a packaged interpreter, but the automation itself uses only Python stdlib.
$PackagedPy = Join-Path $Root 'venv\Scripts\python.exe'
if (Test-Path $PackagedPy) { $Py = $PackagedPy }
else {
    $PythonCommand = Get-Command python -ErrorAction SilentlyContinue
    if ($PythonCommand) { $Py = $PythonCommand.Source }
}
if (-not $Py) { Fail 'Python 3 is required. Install Python 3.11+ and rerun.' }
$PyParts = @(& $Py -c 'import sys; print(sys.version_info[0]); print(sys.version_info[1])')
$PyVersion = "$($PyParts[0]).$($PyParts[1])"
if ($PyVersion -notmatch '^3\.(1[1-9]|[2-9][0-9])$') { Fail "Python 3.11+ required; found $PyVersion" }
Write-Host "[ OK ] Python $PyVersion ($Py)" -ForegroundColor Green

$HermesNode = Join-Path $env:LOCALAPPDATA 'hermes\node\node.exe'
if (Test-Path $HermesNode) { $Node = $HermesNode }
else {
    $NodeCommand = Get-Command node -ErrorAction SilentlyContinue
    if ($NodeCommand) { $Node = $NodeCommand.Source }
}
if (-not $Node) { Fail 'Node.js is required for Agent360 MCP. Install Node.js 20+ and rerun.' }
$NodeVersion = (& $Node --version).Trim()
if ($NodeVersion -notmatch '^v?(\d+)\.') { Fail "Could not parse Node.js version: $NodeVersion" }
if ([int]$Matches[1] -lt 20) { Fail "Node.js 20+ required for Agent360 MCP; found $NodeVersion" }
Write-Host "[ OK ] Node $NodeVersion" -ForegroundColor Green

$Candidates = @(
    (Join-Path $Runtime 'node_modules\@agent360\browser-mcp\index.js'),
    (Join-Path $env:LOCALAPPDATA 'hermes\node\node_modules\@agent360\browser-mcp\index.js'),
    (Join-Path $env:APPDATA 'npm\node_modules\@agent360\browser-mcp\index.js')
)
$Mcp = $Candidates | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $Mcp -and $InstallMcp) {
    $Npm = Get-Command npm -ErrorAction SilentlyContinue
    if (-not $Npm) { Fail 'npm was not found. Install Node.js with npm or provide Agent360 MCP.' }
    New-Item -ItemType Directory -Force -Path $Runtime | Out-Null
    Write-Host 'Installing @agent360/browser-mcp locally in the package folder...'
    & $Npm.Source install --prefix $Runtime --no-save '@agent360/browser-mcp@latest'
    if ($LASTEXITCODE -ne 0) { Fail "Agent360 MCP install failed (exit $LASTEXITCODE)." }
    $Mcp = Join-Path $Runtime 'node_modules\@agent360\browser-mcp\index.js'
}
if (-not $Mcp -or -not (Test-Path $Mcp)) { Fail 'Agent360 browser-mcp missing. Run once with -InstallMcp.' }
Write-Host "[ OK ] Agent360 MCP: $Mcp" -ForegroundColor Green

$OpenCodeCandidates = @(
    (Join-Path $env:LOCALAPPDATA 'hermes\node\node_modules\opencode-ai\bin\opencode.exe'),
    (Join-Path $env:APPDATA 'npm\opencode.cmd'),
    (Join-Path $env:LOCALAPPDATA 'Programs\opencode\opencode.exe')
)
$OpenCode = $OpenCodeCandidates | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
if (-not $OpenCode) {
    $OpenCodeCommand = Get-Command opencode -ErrorAction SilentlyContinue
    if ($OpenCodeCommand) { $OpenCode = $OpenCodeCommand.Source }
}
if (-not $OpenCode) { Fail 'OpenCode CLI is required to launch the mission agent. Install/configure OpenCode and Agent360 MCP, then rerun.' }

$Required = @('agent360_client.py','lane_tools.py','prove_lane.py','lane_resume.py',
              'lane_jobs.py','lane_foundit.py','lane_market_probe.py','lane_apply.py',
              'resume_facts.py')
foreach ($Name in $Required) {
    if (-not (Test-Path (Join-Path $Scripts $Name))) { Fail "Package file missing: scripts\$Name" }
}
if (-not (Test-Path (Join-Path $Root 'candidate-profile.example.json'))) { Fail 'Package file missing: candidate-profile.example.json' }
$MissionAgentConfig = Join-Path $Root '.opencode\agents\employment-mission.md'
if (-not (Test-Path -LiteralPath $MissionAgentConfig)) { Fail 'Package agent policy missing: .opencode\agents\employment-mission.md' }

# Installation/setup must be possible before per-candidate private data is configured.
if (-not $Launch) {
    Write-Host "`nSETUP-VERDICT: READY" -ForegroundColor Green
    Write-Host 'Agent360 and package files are available.'
    Write-Host 'Next: copy candidate-profile.example.json to candidate-profile.json, point'
    Write-Host 'resume_path at the candidate own resume PDF, and set its real SHA256.'
    Write-Host 'That PDF is the single source of truth for every candidate fact - there is'
    Write-Host 'nothing else to fill in. Then run -Launch.'
    exit 0
}

$ConfigPath = if ([IO.Path]::IsPathRooted($CandidateConfig)) { $CandidateConfig } else { Join-Path $Root $CandidateConfig }
if (-not (Test-Path $ConfigPath)) { Fail "Candidate config missing: $ConfigPath. Copy candidate-profile.example.json to candidate-profile.json and set the pinned resume path and SHA256." }
$Config = Get-Content -Raw -Path $ConfigPath | ConvertFrom-Json
# The pointer file carries NO personal value. The PINNED RESUME PDF is the single
# source of truth: name, phone, email, location, skills, education, employers are
# read from it at runtime by scripts\resume_facts.py and never stored anywhere else.
if ([string]::IsNullOrWhiteSpace($Config.resume_path) -or [string]::IsNullOrWhiteSpace($Config.resume_sha256)) { Fail 'Candidate config must include resume_path and resume_sha256.' }
if ($Config.resume_sha256 -notmatch '^[A-Fa-f0-9]{64}$') { Fail 'Candidate config resume_sha256 must be a 64-character SHA256 hex digest.' }
if ($Config.resume_path -notmatch '\.pdf$') { Fail 'The pinned candidate record must be the resume PDF.' }
$Resume = if ([IO.Path]::IsPathRooted($Config.resume_path)) { $Config.resume_path } else { Join-Path (Split-Path $ConfigPath -Parent) $Config.resume_path }
if (-not (Test-Path $Resume)) { Fail "Candidate resume is missing: $Resume" }
$ResumeHash = (Get-FileHash -Algorithm SHA256 $Resume).Hash
if ($ResumeHash -ne $Config.resume_sha256.ToUpperInvariant()) { Fail "Candidate resume hash mismatch: $ResumeHash" }

# The resume must be machine-readable before the mission starts, because every
# candidate fact is extracted from it at runtime. Install pypdf if it is missing.
$PyPdf = & $Py -c @"
import sys
sys.path.insert(0, r'$Scripts')
import resume_facts as RF
ok, msg = RF.require_pypdf(sys.executable)
print(('OK ' if ok else 'NO ') + msg)
"@
if ($PyPdf -notlike 'OK *') { Fail "Resume parsing dependency unavailable. $PyPdf" }

# Read the facts straight out of the pinned PDF. This is the preflight report; no
# fact is stored anywhere. Anything the resume does not state shows as BLOCKED and
# the agent is told to stop on it rather than guess.
$FactReport = & $Py (Join-Path $Scripts 'resume_facts.py') $Resume
if ($LASTEXITCODE -ne 0) { Fail 'Could not read candidate facts from the pinned resume.' }
Write-Host "`n[ OK ] Candidate facts read from the pinned resume ($Resume):" -ForegroundColor Green
$FactReport | ForEach-Object {
    if ($_ -match '^\s*([A-Z_]+)\s+(.+)$') {
        $label = $Matches[1]
        $state = if ($Matches[2] -match '^UNCONFIRMED') { 'UNCONFIRMED -> BLOCKED' } else { 'CONFIRMED (value withheld)' }
        Write-Host ('  {0,-22} {1}' -f $label,$state)
    }
}
$SkillCount = (& $Py -c @"
import sys
sys.path.insert(0, r'$Scripts')
import resume_facts as RF
print(len(RF.facts(r'$Resume').get('SKILL') or []))
"@)
if ([int]$SkillCount -lt 2) { Fail "The pinned resume yielded only $SkillCount skills; the match gate needs at least two." }

$env:KILO_CANDIDATE_CONFIG = $ConfigPath
Write-Host "`n[ OK ] Resume hash verified; $SkillCount verified skills" -ForegroundColor Green

# Resolve the project-local agent before any browser work. This is a read-only
# OpenCode config inspection; it does not start the mission or touch the browser.
$AgentConfigOutput = $null
$AgentConfigExit = 1
Push-Location $Root
try {
    $AgentConfigOutput = & $OpenCode debug agent employment-mission --pure 2>$null
    $AgentConfigExit = $LASTEXITCODE
}
finally { Pop-Location }
if ($AgentConfigExit -ne 0 -or -not $AgentConfigOutput) { Fail 'OpenCode could not resolve the project-local employment-mission agent policy.' }
try { $ResolvedAgent = ($AgentConfigOutput -join "`n") | ConvertFrom-Json }
catch { Fail 'OpenCode returned invalid JSON while resolving the employment-mission agent policy.' }
if ($ResolvedAgent.name -ne 'employment-mission') { Fail 'OpenCode resolved an unexpected mission agent.' }
$RequiredAllowedTools = @(
    'browser-mcp_browser_navigate','browser-mcp_browser_screenshot',
    'browser-mcp_browser_get_page_content','browser-mcp_browser_click',
    'browser-mcp_browser_click_xy','browser-mcp_browser_fill',
    'browser-mcp_browser_press_key','browser-mcp_browser_wait',
    'browser-mcp_browser_list_tabs','browser-mcp_browser_switch_tab',
    'browser-mcp_browser_get_new_tab','browser-mcp_browser_close_tab'
)
$RequiredDeniedTools = @(
    'browser-mcp_browser_execute_script'
)
$PermissionRules = @($ResolvedAgent.permission)
foreach ($ToolName in $RequiredAllowedTools + $RequiredDeniedTools) {
    $ApplicableRules = @($PermissionRules | Where-Object { $ToolName -like $_.permission })
    if ($ApplicableRules.Count -eq 0) { Fail "OpenCode agent policy has no decision for $ToolName." }
    $Decision = $ApplicableRules[-1].action
    $Expected = if ($ToolName -in $RequiredAllowedTools) { 'allow' } else { 'deny' }
    if ($Decision -ne $Expected) { Fail "OpenCode agent policy for $ToolName is '$Decision'; expected '$Expected'." }
}
Write-Host '[ OK ] Project-local OpenCode agent policy resolved; browser tool permissions verified.' -ForegroundColor Green

$MissionFiles = @(
    (Join-Path $Root 'MISSION-RUN.txt'),
    (Join-Path $Root 'docs\AGENTS-EMPLOYMENT.md'),
    (Join-Path $Root 'docs\EMPLOYMENT-LANE-MISSION.md'),
    (Join-Path $Root 'docs\PACE.md'),
    (Join-Path $Evidence 'ledger.tsv')
)
foreach ($Path in $MissionFiles) {
    if (-not (Test-Path -LiteralPath $Path)) { Fail "Mission input missing: $Path" }
}
# The resume itself is not attached; the agent must retrieve facts through the
# package parser. AGENTS.md, logs, and sidecar files are deliberately excluded as
# fact sources. The resume path and SHA256 pointer are the only candidate config.

$env:KILO_AGENT360_NODE = $Node
$env:KILO_AGENT360_MCP_ENTRYPOINT = $Mcp
New-Item -ItemType Directory -Force -Path $Evidence | Out-Null
$RunLog = Join-Path $Evidence 'mission-agent-run.log'
$RunOutput = Join-Path $Evidence 'mission-agent-output.txt'
$Prompt = @"
CRITICAL BROWSER STARTUP GATE — follow Agent360's tab lifecycle:
1. First call browser_list_tabs once. If it returns Unknown or empty, record it and continue; do not repeat blindly.
2. Call browser_navigate to https://www.naukri.com/mnjuser/profile without new_tab=true.
3. Call browser_list_tabs once, identify the Naukri tab owned by this Agent360 session, and browser_switch_tab to its tab_id.
4. Then call browser_screenshot to a unique timestamped path under evidence/employment-lane/, followed by browser_get_page_content.
5. A single tab-list Unknown is not an outage if navigation and screenshot succeed. If navigation fails or the target session tab cannot be activated, make no profile/application/feed changes, write a BLOCKED receipt, and report the exact errors.
6. For click/fill/key timeouts, do not repeat blindly: list tabs, switch to the target session tab, read/screenshot the page, and retry at most once only if the same visible control remains.
7. Only state facts visible in page content/screenshots or extracted from the hash-verified resume. Never speculate from unreadable image regions or aggregate counts. Never describe an action as complete unless a fresh screenshot/page read verifies it. Do not click a data value to guess its edit control.
8. Keep narration concise. Do not expose chain-of-thought; report only observations, actions, receipts, and blockers.

Execute the employment mission now using the attached mission files and the configured Agent360 browser MCP. This is an agent mission launch, not a lane-test command. Do not invoke kilo-bridge-setup.ps1 -Launch recursively: this launcher has already completed environment and candidate preflight.

FACT LAWS - READ BEFORE ANY BROWSER ACTION:
- The ONE and ONLY source of candidate facts is the pinned resume at $Resume. It is hash-verified, and it is NOT attached to this mission because the Read tool cannot parse PDFs.
- Read candidate facts ONLY by running: venv\Scripts\python.exe scripts\resume_facts.py $Resume
  That prints every fact it can confirm. For skills in code, use: venv\Scripts\python.exe scripts\lane_tools.py is not a script - import lane_tools and call candidate_fact('KEY') / candidate_skills().
- The preflight above already ran that extraction and printed the result. Treat any field shown there as UNCONFIRMED as UNCONFIRMED. Do not re-derive it from any other file.
- Any recruiter question must be answered from an exact fact the resume parser confirms. A general experience duration is not proof of years in a particular domain. If the resume does not explicitly support an answer, mark the question BLOCKED.
- Every other file in this package is NOT a fact source: not the other Markdown files, not any log, not any screenshot, not any ledger note, not any script comment. Do not read candidate facts from them.
- Never carry a fact over from a previous candidate, profile, or run.
- A fact absent from the pinned resume means UNCONFIRMED. Report the exact missing fact and stop that step as BLOCKED. Never guess, never infer, never fill from another file. Inventing a value is a hard failure.

LEDGER WRITE CONTRACT (append rows through the package CLI - never a raw file write):
- Record every action as a row by running: venv\Scripts\python.exe scripts\lane_ledger.py --portal P --source S --role R --company C --score N --step STEP --status STATUS --receipt RECEIPT --note NOTE
- One invocation writes exactly one 10-column row. NEVER call a generic write/editor tool against evidence\employment-lane\ledger.tsv, and never hand-assemble a tab-joined line. The CLI owns the TSV shape, the relative receipt path, ASCII folding and the column caps.
- STATUS must be exactly one of: MATCHED APPLIED APPLIED_STEP BLOCKED NO_MATCH RATE_LIMITED FAILED OK. The CLI rejects any other value with exit 2.
- Confirm a row landed by re-reading it: venv\Scripts\python.exe scripts\lane_ledger.py --tail 1
- If the CLI prints `RESULT: BLOCKED ...`, fix the missing/typo flag and re-run. Do not fall back to a raw write; the ledger is append-only.

Read the attached files in their prescribed order, inspect the current ledger chronologically, and perform the next authorized mission actions through the browser MCP tools. Keep receipts in the package evidence folder and report completed, blocked, and pending work honestly. Follow every approval, candidate-fact, dedupe, and submission rule in the mission documents.

FINAL REPORT FORMAT: Use these exact Markdown headings on separate lines: `## Profile changes`, `## Applications`, `## Blocked`, `## Skipped`. Keep each section concise. These are required for the launcher to recognize this run's report.
"@
if ($SubmitOne) {
    $Prompt += "`nFor this run only, limit application submission to the exact currently matched role title: $Title. Verify title and employer in the live UI and candidate facts before any submit; never submit another role."
}

Write-Host "`nLaunching OpenCode mission agent with $MissionModel (no deterministic/live lane test loop will run)." -ForegroundColor Cyan
Write-Host "Agent CLI: $OpenCode"
Write-Host "Mission receipts: $Evidence"
Write-Host "Agent log: $RunLog"
$AgentArgs = @('run',$Prompt,'--dir',$Root,'--agent','employment-mission','--title','Kilo Bridge employment mission','--model',$MissionModel)
foreach ($Path in $MissionFiles) { $AgentArgs += @('--file',$Path) }
$Started = Get-Date
$RunStamp = $Started.ToString('yyyyMMdd-HHmmss')
foreach ($PriorPath in @($RunOutput, $RunLog)) {
    if (Test-Path -LiteralPath $PriorPath) {
        $ArchivePath = "$PriorPath.$RunStamp.previous"
        Move-Item -LiteralPath $PriorPath -Destination $ArchivePath
    }
}
$LedgerPath = Join-Path $Evidence 'ledger.tsv'
$LedgerLinesBefore = if (Test-Path -LiteralPath $LedgerPath) { @(Get-Content -LiteralPath $LedgerPath).Count } else { 0 }
"[$($Started.ToString('s'))] Agent mission started; launcher preflight passed." | Set-Content -LiteralPath $RunLog -Encoding UTF8
$PreviousErrorActionPreference = $ErrorActionPreference
try {
    # External CLI errors should be captured and reported through the exit code,
    # not converted into a terminating PowerShell NativeCommandError.
    $ErrorActionPreference = 'Continue'
    & $OpenCode @AgentArgs 2>&1 | Tee-Object -FilePath $RunOutput -Append | ForEach-Object {
        Write-Host $_
        Add-Content -LiteralPath $RunLog -Value $_ -Encoding UTF8
    }
}
finally { $ErrorActionPreference = $PreviousErrorActionPreference }
$AgentExit = $LASTEXITCODE
"[$((Get-Date).ToString('s'))] Agent mission ended; exitcode=$AgentExit" | Add-Content -LiteralPath $RunLog -Encoding UTF8
if ($AgentExit -ne 0) { Fail "OpenCode mission agent exited with code $AgentExit. Review $RunOutput and the latest ledger/screenshot before retrying." }

# Grade only this run's output and fresh receipts. A zero process exit alone means nothing.
$Output = if (Test-Path -LiteralPath $RunOutput) { Get-Content -Raw -LiteralPath $RunOutput } else { '' }
$ReportSections = @('profile changes','applications','blocked','skipped')
$Missing = @()
foreach ($Section in $ReportSections) {
    if ($Output -notmatch ("(?im)^\s*#{0,3}\s*" + [regex]::Escape($Section) + "\s*:?\s*$")) { $Missing += $Section }
}
$Degenerate = $Output -match '<\|open\|>|<\|[a-z_]+\|>'
$RunLogText = Get-Content -Raw -LiteralPath $RunLog
$BrowserCalls = [regex]::Matches($RunLogText, 'browser-mcp_browser_([a-z_]+)')
$ProtocolIssue = $null
if ($BrowserCalls.Count -lt 5) { $ProtocolIssue = 'Fewer than five browser startup calls were recorded.' }
elseif ($BrowserCalls[0].Groups[1].Value -ne 'list_tabs' -or
        $BrowserCalls[1].Groups[1].Value -ne 'navigate' -or
        $BrowserCalls[2].Groups[1].Value -ne 'list_tabs' -or
        $BrowserCalls[3].Groups[1].Value -ne 'switch_tab' -or
        $BrowserCalls[4].Groups[1].Value -ne 'screenshot') {
    $ProtocolIssue = 'Browser startup was not list-tabs, navigate, list-tabs, switch-tab, screenshot.'
}
$FreshScreenshot = $false
$ScreenshotPaths = [regex]::Matches($RunLogText, 'browser-mcp_browser_screenshot\s+\{[^\r\n]*?"path"\s*:\s*"([^"]+\.png)"')
foreach ($Match in $ScreenshotPaths) {
    $ShotPath = $Match.Groups[1].Value.Replace('/', [IO.Path]::DirectorySeparatorChar)
    $ShotFullPath = if ([IO.Path]::IsPathRooted($ShotPath)) { [IO.Path]::GetFullPath($ShotPath) } else { [IO.Path]::GetFullPath((Join-Path $Root $ShotPath)) }
    $EvidencePrefix = [IO.Path]::GetFullPath($Evidence).TrimEnd([IO.Path]::DirectorySeparatorChar) + [IO.Path]::DirectorySeparatorChar
    if ($ShotFullPath.StartsWith($EvidencePrefix, [StringComparison]::OrdinalIgnoreCase) -and (Test-Path -LiteralPath $ShotFullPath)) {
        $Shot = Get-Item -LiteralPath $ShotFullPath
        if ($Shot.Length -gt 0 -and $Shot.LastWriteTime -ge $Started.AddSeconds(-2)) { $FreshScreenshot = $true; break }
    }
}
$RowsAdded = 0
if (Test-Path -LiteralPath $LedgerPath) {
    $LedgerLines = @(Get-Content -LiteralPath $LedgerPath)
    $RowsAdded = [Math]::Max(0, $LedgerLines.Count - $LedgerLinesBefore)
}
$Duration = [int]((Get-Date) - $Started).TotalMinutes

if ($Degenerate) {
    Write-Host "`nMISSION-AGENT-VERDICT: DEGENERATE OUTPUT - not a result" -ForegroundColor Red
    Write-Host "The agent stream contains raw control tokens, which means the model broke down." -ForegroundColor Red
    Write-Host "Do NOT treat any task from this run as complete." -ForegroundColor Red
    Fail "Agent output was malformed. Review $RunOutput before another run."
}
elseif ($ProtocolIssue) {
    Write-Host "`nMISSION-AGENT-VERDICT: BROWSER PROTOCOL FAILURE" -ForegroundColor Red
    Write-Host $ProtocolIssue -ForegroundColor Red
    Write-Host "No task is complete unless it has a fresh visible receipt." -ForegroundColor Red
    Fail "Agent violated the browser startup gate. Review $RunOutput and $RunLog."
}
elseif (-not $FreshScreenshot) {
    Write-Host "`nMISSION-AGENT-VERDICT: NO FRESH BROWSER RECEIPT" -ForegroundColor Red
    Fail "No fresh screenshot under this package's evidence folder was verified. Review $RunOutput and $RunLog."
}
elseif ($RowsAdded -eq 0) {
    Write-Host "`nMISSION-AGENT-VERDICT: NO FRESH LEDGER RECEIPT" -ForegroundColor Red
    Fail "No new ledger row was written during this run. The agent narrative is not completion proof."
}
elseif ($Missing.Count -gt 0) {
    Write-Host "`nMISSION-AGENT-VERDICT: INCOMPLETE - no final report" -ForegroundColor Red
    Write-Host ("The agent exited 0 but its output is missing the required section(s): " + ($Missing -join ', ')) -ForegroundColor Red
    Write-Host ("Ledger rows for today: $RowsAdded. Duration: $Duration min.") -ForegroundColor Yellow
    Fail "Mission report is incomplete. Read the output and receipts before retrying."
}
else {
    Write-Host "`nMISSION-AGENT-VERDICT: REPORT PRESENT - verify it before believing it" -ForegroundColor Green
    Write-Host ("Ledger rows for today: $RowsAdded. Duration: $Duration min.") -ForegroundColor Green
    Write-Host "The four report sections are present. Check each claim against its receipt." -ForegroundColor Yellow
}
Write-Host "Agent output: $RunOutput"
Write-Host "Agent log: $RunLog"
Write-Host "Receipts: $Evidence"
