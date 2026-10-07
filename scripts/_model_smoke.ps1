<#
  _model_smoke.ps1 - read-only, no-browser model discriminator.

  WHY: the 2026-10-07 live run proved the harness is fixed but the mission model
  (nemotron-3-nano-omni-30b) could not follow a shell instruction - it ran cmd
  `dir /b` inside PowerShell and misfired the fact reader. Before spending another
  live account run, prove which candidate can actually execute a shell command and
  use the ledger CLI.

  This touches NO browser and writes NO ledger row (lane_ledger --count is read-only).
  Each candidate gets one tiny prompt; results land in evidence/employment-lane/smoke-*.txt.
#>
$root = Split-Path -Parent $PSScriptRoot
$oc   = Join-Path $env:LOCALAPPDATA 'hermes\node\node_modules\opencode-ai\bin\opencode.exe'
$ev   = Join-Path $root 'evidence\employment-lane'
$py   = Join-Path $root 'venv\Scripts\python.exe'
$led  = Join-Path $root 'scripts\lane_ledger.py'
if (-not (Test-Path $oc)) { Write-Output "opencode.exe missing: $oc"; exit 1 }

# No spaces in these paths, so the prompt needs no quotes.
$prompt = 'Run this exact PowerShell command and return its raw stdout verbatim, ' +
          'nothing else: & ' + $py + ' ' + $led + ' --count'

$models = [ordered]@{
  'kimi-k3'    = 'nvidia/moonshotai/kimi-k3'
  'glm53flash' = 'nvidia/z-ai/glm-5.3-flash'
  'nsuper120'  = 'nvidia/nvidia/nemotron-3-super-120b-a12b'
}
foreach ($tag in $models.Keys) {
  $m   = $models[$tag]
  $log = Join-Path $ev ("smoke-$tag.txt")
  if (Test-Path -LiteralPath $log) { Remove-Item -LiteralPath $log -Force }
  $cmd = "& '$oc' run '$prompt' --model $m --dir '$root' 2>&1 | Out-File -Encoding utf8 '$log'"
  Start-Process -FilePath 'powershell' `
      -ArgumentList @('-NoProfile','-ExecutionPolicy','Bypass','-Command',$cmd) `
      -WorkingDirectory $root -WindowStyle Hidden | Out-Null
  Write-Output "launched smoke: $tag -> $m"
}
Write-Output 'NOTE: read evidence\employment-lane\smoke-*.txt shortly for results.'