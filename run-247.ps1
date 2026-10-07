# run-247.ps1 - Kilo Bridge 24/7 Autonomous Employment Daemon
param(
    [int]$Interval = 1200,
    [int]$Limit = 3,
    [switch]$Once
)

$Root = $PSScriptRoot
Set-Location $Root
Write-Host "Starting Kilo Bridge 24/7 Autonomous Employment Daemon..." -ForegroundColor Cyan
Write-Host "Interval: $Interval sec | Applications per round: $Limit" -ForegroundColor Gray

$Py = Join-Path $Root "venv\Scripts\python.exe"
$Script = Join-Path $Root "scripts\lane_daemon.py"

$ArgsList = @($Script, "--interval", $Interval, "--limit", $Limit)
if ($Once) { $ArgsList += "--once" }

& $Py @ArgsList
