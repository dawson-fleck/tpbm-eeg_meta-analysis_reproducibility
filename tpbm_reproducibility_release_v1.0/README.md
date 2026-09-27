# tPBM cognition and EEG reproducibility package

Release candidate: v1.0; numerical analysis snapshot frozen 19 September 2026

This package reproduces the 17-cohort numerical analyses in the current submission, including the final source-corrected 17-cohort cognition analysis and the non-pooled EEG evidence audit. It intentionally excludes copyrighted full-text articles, private correspondence, and obsolete 23-cohort analysis code from the executable path.

## Fast rerun on Windows

1. Extract the ZIP to a normal writable folder.
2. Open PowerShell in the extracted folder.
3. Run:

```powershell
powershell -ExecutionPolicy Bypass -File .\RUN_ALL.ps1
```

The runner detects R and Python, installs the two required R packages at the recorded versions into a project-local library when necessary, creates a timestamped folder under `Reruns`, runs cognition and EEG in fresh processes, and compares the key numerical results with the frozen outputs. It never overwrites the frozen package files.

If automatic detection fails, provide explicit executables:

```powershell
.\RUN_ALL.ps1 -Rscript "C:\Program Files\R\R-4.6.1\bin\Rscript.exe" -Python "C:\path\to\python.exe"
```

A successful run ends with `VALIDATION PASSED` and writes `PASS.txt` inside the timestamped rerun folder.

## Contents

- `Cognition/Inputs`: frozen specifications and supporting inputs.
- `Cognition/Recorded_Outputs`: final corrected 17-cohort model-ready datasets, model results, sensitivity analyses, moderator analyses, reporting-bias analyses, influence diagnostics, and saved R models.
- `Cognition/Audit_Records`: effect derivations, 23-to-17 reconciliation, source/correction provenance, formula checks, rounding sensitivity, and explicit model membership.
- `Cognition/Code_used`: the R and Python analysis code used for the final audit. The rerun wrapper copies these scripts into a disposable working folder so their original relative-path assumptions are preserved.
- `Cognition/Full_Audit_Code`: the complete current audit script set exactly as archived, including snapshot, source-review, correction, reporting, manuscript-patch, and final-QA stages. Some of these provenance stages require copyrighted/private local source materials and are therefore not invoked by the public quick rerun.
- `EEG/Inputs`: final audited extraction and analysis inputs.
- `EEG/Reproducibility/Source_snapshots`: shareable frozen extraction records and numerical snapshots needed by the EEG workflow; no article PDFs or email files are included.
- `EEG/Scripts`: complete Python/base-R EEG workflow.
- `EEG/Recorded_Outputs`: final numerical EEG outputs and environment records. EEG is described, checked, and gated for compatibility; no pooled EEG model is fit.
- `MANUSCRIPT_OUTPUT_MAP.csv`: manuscript result/table/figure to code/input/output crosswalk.
- `Environment`: recorded software versions and final QA record.
- `SHA256SUMS.txt`: release integrity manifest.

## Current reported results

The authoritative cognition input is `Cognition/Recorded_Outputs/harmonization_r0.5.csv` (17 cohorts). Primary domain and secondary overall results are rows in `Cognition/Recorded_Outputs/model_results.csv` whose model names begin with `primary__`.

- Memory: k = 7, g = 0.251, 95% CI -0.111 to 0.614.
- Global cognition: k = 5, g = 0.399, 95% CI -0.011 to 0.808.
- Executive function/sustained attention: k = 3, g = 0.617, 95% CI 0.057 to 1.177.
- Secondary overall cognition: k = 17, g = 0.380, 95% CI 0.200 to 0.561; I-squared = 49.4%; prediction interval -0.115 to 0.876.

The EEG workflow retains 207 provisional descriptive effects from nine report clusters after quarantining five conflicted Zomorrodi rows. No compatible EEG family reaches three independent datasets, so no EEG pooled effect, heterogeneity estimate, moderator analysis, or funnel analysis is produced.

## Software

The final cognition run used R 4.6.1, `metafor` 5.0-1, and `clubSandwich` 0.7.0. Python 3.12.14 was used for independent standard-library checks. The EEG pipeline requires Python 3.10+ and base R 4.x only. Full recorded versions are in `Environment/R_session.txt`, `Environment/python_version.txt`, and the EEG recorded environment files.

## Interpretation limits

A successful computational rerun verifies arithmetic, model implementation, file integrity, and agreement with recorded outputs. It does not independently validate every extraction judgment, source interpretation, risk-of-bias judgment, or eligibility decision. The historical 23-cohort results are not the reported manuscript results and must not replace the source-corrected 17-cohort outputs.

## Before public deposition

1. Obtain all authors' approval of the frozen release.
2. Choose and insert code/data licenses; no license is granted by this draft package.
3. Confirm that the included extraction summaries and source-provenance text may be publicly redistributed under the selected terms.
4. Make the reviewed repository public, enable its Zenodo integration, and publish a tagged GitHub release for archival.
5. Add the assigned DOI/permanent URL to the manuscript Data and Code Availability statement.

Do not add full-text PDFs, private emails, or credentials to the public release.
