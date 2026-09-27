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
  throw "Required executable not found. Supply its path explicitly."
}

$Rscript = Resolve-Executable $Rscript @(
  'Rscript',
  'C:\Program Files\R\R-4.6.1\bin\Rscript.exe'
)
$Python = Resolve-Executable $Python @(
  'python',
  'python3'
)

$Library = Join-Path $Root 'Cognition\Reproducibility\R_library'
New-Item -ItemType Directory -Force -Path $Library | Out-Null
$env:R_LIBS_USER = $Library
& $Rscript --vanilla (Join-Path $Root 'setup_packages.R') $Library
if ($LASTEXITCODE -ne 0) { throw 'R package setup failed.' }

$Stamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$RunRoot = Join-Path $Root "Reruns\$Stamp"
$Cog = Join-Path $RunRoot 'Cognition'
$EEG = Join-Path $RunRoot 'EEG'
New-Item -ItemType Directory -Force -Path $Cog, $EEG | Out-Null

Copy-Item -LiteralPath (Join-Path $Root 'Cognition\Inputs') -Destination (Join-Path $Cog 'Inputs') -Recurse
Copy-Item -LiteralPath (Join-Path $Root 'Cognition\Code_used') -Destination (Join-Path $Cog 'Code_used') -Recurse
New-Item -ItemType Directory -Force -Path (Join-Path $Cog 'Outputs'), (Join-Path $Cog 'Logs') | Out-Null
Get-ChildItem -LiteralPath (Join-Path $Root 'Cognition\Recorded_Outputs') -File | Where-Object {
  $_.Name -match '^(harmonization|all_outcomes|external)_r0\.[258]\.csv$'
} | Copy-Item -Destination (Join-Path $Cog 'Outputs')
Get-ChildItem -LiteralPath (Join-Path $Root 'Cognition\Code_used') -File |
  Copy-Item -Destination $Cog -Force

& $Rscript --vanilla (Join-Path $Cog 'audit_models.R')
if ($LASTEXITCODE -ne 0) { throw 'Cognition model run failed.' }
& $Python (Join-Path $Cog 'independent_pool.py') $Cog
if ($LASTEXITCODE -ne 0) { throw 'Independent cognition verification failed.' }

$Corrected = Join-Path $Cog 'Working_corrected'
New-Item -ItemType Directory -Force -Path (Join-Path $Corrected 'Inputs'), (Join-Path $Corrected 'Outputs'), (Join-Path $Corrected 'Logs') | Out-Null
Get-ChildItem -LiteralPath (Join-Path $Cog 'Inputs') -File |
  Copy-Item -Destination (Join-Path $Corrected 'Inputs') -Force
Get-ChildItem -LiteralPath (Join-Path $Root 'Cognition\Recorded_Outputs') -File | Where-Object {
  $_.Name -match '^(harmonization|all_outcomes|external)_r0\.[258]\.csv$'
} | Copy-Item -Destination (Join-Path $Corrected 'Outputs')
& $Rscript --vanilla (Join-Path $Cog 'audit_models.R') $Corrected
if ($LASTEXITCODE -ne 0) { throw 'Corrected cognition model run failed.' }
& $Python (Join-Path $Cog 'independent_pool.py') $Corrected
if ($LASTEXITCODE -ne 0) { throw 'Corrected independent verification failed.' }
& $Rscript --vanilla (Join-Path $Cog 'audit_additional.R')
if ($LASTEXITCODE -ne 0) { throw 'Cognition formula/figure run failed.' }
& $Rscript --vanilla (Join-Path $Cog 'audit_parameters.R')
if ($LASTEXITCODE -ne 0) { throw 'Exploratory parameter run failed.' }
& $Python (Join-Path $Cog 'independent_eeg_extra.py')
if ($LASTEXITCODE -ne 0) { throw 'Additional EEG source checks failed.' }

Copy-Item -LiteralPath (Join-Path $Root 'EEG\Scripts') -Destination (Join-Path $EEG 'Scripts') -Recurse
Copy-Item -LiteralPath (Join-Path $Root 'EEG\Inputs') -Destination (Join-Path $EEG 'Inputs') -Recurse
Copy-Item -LiteralPath (Join-Path $Root 'EEG\Reproducibility') -Destination (Join-Path $EEG 'Reproducibility') -Recurse
New-Item -ItemType Directory -Force -Path (Join-Path $EEG 'Outputs') | Out-Null
& $Python (Join-Path $EEG 'Scripts\run_eeg.py') --rscript $Rscript
if ($LASTEXITCODE -ne 0) { throw 'EEG workflow failed.' }

& $Python (Join-Path $Root 'validate_release.py') --release $Root --rerun $RunRoot
if ($LASTEXITCODE -ne 0) { throw 'Recorded-versus-rerun validation failed.' }
Set-Content -LiteralPath (Join-Path $RunRoot 'PASS.txt') -Value "VALIDATION PASSED $((Get-Date).ToString('o'))"
Write-Output "VALIDATION PASSED. Rerun saved at: $RunRoot"
