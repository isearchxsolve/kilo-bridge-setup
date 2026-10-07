# launch-crush-employment.ps1
#   Secondary employment-lane driver (crush backend).
#
#   NOTE: the canonical launcher is kilo-bridge-setup.ps1 -Launch. This script
#   exists for operators who drive the crush CLI directly. It roots every path at
#   its own folder so the package runs from any location.
$ErrorActionPreference = 'Stop'
$Lane = $PSScriptRoot
$prompt = 'Read MISSION-RUN.txt and execute it. Resume from evidence\employment-lane\ledger.tsv, do not redo rows marked OK. Facts come only from candidate-profile.json and its hash-verified resume.'
Start-Process powershell -WindowStyle Normal -ArgumentList @(
  '-NoExit',
  '-Command',
  "cd '$Lane'; crush run '$prompt'"
)
Write-Output 'LAUNCH_SENT crush'