param(
 [string]$Python = 'C:\Users\fleck\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe',
 [string]$Rscript = 'C:\Program Files\R\R-4.6.1\bin\Rscript.exe',
 [switch]$RefreshSnapshots
)
$ErrorActionPreference = 'Stop'
$auditRoot = $PSScriptRoot
$env:PYTHONIOENCODING = 'utf-8'
function Invoke-AuditStep([string]$exe, [string[]]$stepArgs, [string]$logName) {
 & $exe @stepArgs *> (Join-Path $auditRoot "Logs/$logName")
 if ($LASTEXITCODE -ne 0) { throw "Audit step failed: $logName; inspect Logs/$logName" }
}
# Requires the existing project alongside this audit, existing R libraries and frozen sources.
# Default preserves the initial input/hash baseline. RefreshSnapshots intentionally re-reads originals.
if ($RefreshSnapshots) { Invoke-AuditStep $Python @("$auditRoot/audit_prepare.py") 'prepare_rerun.log' }
Invoke-AuditStep $Rscript @("$auditRoot/audit_models.R") 'original_models_rerun.log'
Invoke-AuditStep $Python @("$auditRoot/independent_pool.py") 'python_original_rerun.log'
Invoke-AuditStep $Python @("$auditRoot/correct_inputs.py") 'correct_inputs_rerun.log'
Invoke-AuditStep $Rscript @("$auditRoot/audit_models.R", "$auditRoot/Working_corrected") 'corrected_models_rerun.log'
Invoke-AuditStep $Python @("$auditRoot/independent_pool.py", "$auditRoot/Working_corrected") 'python_corrected_rerun.log'
Invoke-AuditStep $Rscript @("$auditRoot/audit_additional.R") 'additional_rerun.log'
Invoke-AuditStep $Python @("$auditRoot/source_review.py") 'source_review_rerun.log'
Invoke-AuditStep $Rscript @("$auditRoot/audit_parameters.R") 'parameters_rerun.log'
Invoke-AuditStep $Python @("$auditRoot/EEG_replication/Scripts/01_prepare_eeg.py") 'EEG_python_rerun.log'
Invoke-AuditStep $Rscript @("$auditRoot/EEG_replication/Scripts/02_describe_eeg.R") 'EEG_R_rerun.log'
Invoke-AuditStep $Python @("$auditRoot/audit_eeg_scan.py") 'EEG_scan_rerun.log'
Invoke-AuditStep $Python @("$auditRoot/independent_eeg_extra.py") 'EEG_extra_rerun.log'
Invoke-AuditStep $Python @("$auditRoot/build_audit_report.py") 'report_rerun.log'
Invoke-AuditStep $Python @("$auditRoot/patch_manuscript.py") 'manuscript_rerun.log'
Invoke-AuditStep $Python @("$auditRoot/finalize_audit.py") 'finalize_rerun.log'
Write-Output 'Audit completed. Read AUDIT_REPORT.md and Logs/final_QA.json.'
