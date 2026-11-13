param(
  [string]$Rscript = '',
  [string]$Python = ''
)
$ErrorActionPreference = 'Stop'
$Root = $PSScriptRoot

function Resolve-Executable([string]$Requested, [string[]]$Candidates) {
  if ($Requested) {
    if (Test-Path -LiteralPath $Requested) { return (Resolve-Path -LiteralPath $Requested).Path }
    $cmd = Get-Command $Requested -ErrorAction SilentlyContinue
    if ($cmd) { return $cmd.Source }
    throw "Executable not found: $Requested"
  }
  foreach ($candidate in $Candidates) {
    if (Test-Path -LiteralPath $candidate) { return (Resolve-Path -LiteralPath $candidate).Path }
    $cmd = Get-Command $candidate -ErrorAction SilentlyContinue
    if ($cmd) { return $cmd.Source }
  }
  throw 'Required executable not found. Supply its path explicitly.'
}

$Rscript = Resolve-Executable $Rscript @('Rscript', 'C:\Program Files\R\R-4.6.1\bin\Rscript.exe')
$Python = Resolve-Executable $Python @('python', 'python3')

$Venv = Join-Path $Root 'Environment\.venv'
$VenvPython = Join-Path $Venv 'Scripts\python.exe'
if (-not (Test-Path -LiteralPath $VenvPython)) {
  & $Python -m venv $Venv
  if ($LASTEXITCODE -ne 0) { throw 'Python virtual-environment creation failed.' }
}

$Library = Join-Path $Root 'Cognition\Reproducibility\R_library'
New-Item -ItemType Directory -Force -Path $Library | Out-Null
$env:TPBM_R_LIBRARY = $Library
& $Rscript --vanilla (Join-Path $Root 'setup_packages.R') $Library
if ($LASTEXITCODE -ne 0) { throw 'R package setup failed.' }

& $VenvPython -c 'import numpy, scipy'
if ($LASTEXITCODE -ne 0) {
  & $VenvPython -m ensurepip --upgrade
  if ($LASTEXITCODE -ne 0) { throw 'Python pip bootstrap failed.' }
  & $VenvPython -m pip install --disable-pip-version-check -r (Join-Path $Root 'Environment\requirements.txt')
  if ($LASTEXITCODE -ne 0) { throw 'Python dependency setup failed.' }
}

$Stamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$RunRoot = Join-Path $Root "Reruns\$Stamp"
$Cog = Join-Path $RunRoot 'Cognition'
New-Item -ItemType Directory -Force -Path $Cog | Out-Null

foreach ($name in @('Inputs', 'Scripts', 'Original_snapshot')) {
  Copy-Item -LiteralPath (Join-Path $Root "Cognition\$name") -Destination $Cog -Recurse
}
New-Item -ItemType Directory -Force -Path (Join-Path $Cog 'Outputs'), (Join-Path $Cog 'Logs') | Out-Null

& $Rscript --vanilla (Join-Path $Cog 'Scripts\aq_analyze.R')
if ($LASTEXITCODE -ne 0) { throw 'Cognition analysis failed.' }
& $VenvPython (Join-Path $Cog 'Scripts\aq_verify.py')
if ($LASTEXITCODE -ne 0) { throw 'Independent cognition verification failed.' }

& $VenvPython (Join-Path $Root 'validate_release.py') --release $Root --rerun $RunRoot
if ($LASTEXITCODE -ne 0) { throw 'Recorded-versus-rerun validation failed.' }
Set-Content -LiteralPath (Join-Path $RunRoot 'PASS.txt') -Value "VALIDATION PASSED $((Get-Date).ToString('o'))"
Write-Output "VALIDATION PASSED. Rerun saved at: $RunRoot"
