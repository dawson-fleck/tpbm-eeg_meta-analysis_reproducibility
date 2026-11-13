# tPBM cognition and EEG reproducibility package

Final locked release: v2.0.0, 12 November 2026.

This public package reproduces the finalized cognitive meta-analysis. The cognitive dataset contains 18 independent cohorts and 680 participants. Private working links, detailed audit notes, and source snapshots have been removed; numerical analysis fields are retained. The unchanged non-pooled EEG audit remains available in the repository's historical v1.0 folder. The v1.0.0/Zenodo cognitive release contains 17 cohorts and is superseded for manuscript interpretation.

## Final cognitive results

- Memory: k = 7, N = 267, Hedges' g = 0.251, 95% CI -0.111 to 0.614.
- Global cognition: k = 6, N = 210, g = 0.315, 95% CI -0.128 to 0.759.
- Executive function/sustained attention: k = 3, N = 91, g = 0.617, 95% CI 0.057 to 1.177.
- Secondary overall cognition: k = 18, N = 680, g = 0.357, 95% CI 0.175 to 0.539; prediction interval -0.149 to 0.863.

The Hwang analyzed sample is n = 15 per selected arm. Kheradmand schizophrenia is included in the core global and overall models. Li and Kerppers are eligible narrative evidence but are not pooled. O'Donnell is retained only as a design-compatibility sensitivity.

## Fast rerun on Windows

1. Extract the release to a writable folder.
2. Open PowerShell in the extracted folder.
3. Run:

```powershell
powershell -ExecutionPolicy Bypass -File .\RUN_ALL.ps1
```

The runner resolves Python and R, installs the pinned Python and R dependencies into release-local libraries when needed, reruns cognition and EEG in a timestamped `Reruns` folder, and compares regenerated results with the recorded outputs. It never overwrites the recorded results. A successful run ends with `VALIDATION PASSED`.

Explicit executable paths may be supplied:

```powershell
.\RUN_ALL.ps1 -Rscript "C:\Program Files\R\R-4.6.1\bin\Rscript.exe" -Python "C:\path\to\python.exe"
```

## Contents

- `Cognition/Inputs`: locked v3 analysis specifications and model-ready files for paired-r scenarios 0.2, 0.5 and 0.8. The public files contain the complete numerical and categorical fields required by the analysis; internal project-management fields are not distributed.
- `Cognition/Scripts`: executable R analysis, independent Python verifier, and a result-table export helper.
- `Cognition/Recorded_Outputs`: finalized model tables, sensitivities, diagnostics, multilevel analyses, audit tables, and session information. Manuscript figures and the machine-specific serialized R model cache are intentionally not distributed; the runner rebuilds the models.
- `Cognition/Audit_Records`: independent numerical verification record.
- `Cognition/Original_snapshot/Approved_plan_outputs`: the two aggregate numerical comparison inputs required by the analysis.
- `PUBLIC_RELEASE_SCOPE.md`: the public/private release boundary and exclusions.
- `Environment`: pinned dependency information and final QA record.
- `LOCKED_DATASET_SHA256.csv`: hashes for locked cognition inputs.
- `SHA256SUMS.txt`: release integrity manifest.

## Software

The final cognition run used R 4.6.1, `metafor` 5.0-1, and `clubSandwich` 0.7.0. Independent verification used Python 3.12.14, NumPy 2.3.5, and SciPy 1.18.1. Exact recorded R session information is in `Environment/R_session.txt`.

## Verification scope

The independent Python verifier checks 54 v3 effect/variance calculations and five principal REML/Hartung-Knapp models without calling R. Computational agreement does not independently validate every source extraction, eligibility judgment, risk-of-bias judgment, or GRADE decision. The EEG audit is unchanged from v1.0 and is not rerun by this v2.0 public package.

## Version and archive note

The existing Zenodo DOI `10.5281/zenodo.23003323` archives v1.0.0 only. A new Zenodo version should be minted from this v2.0.0 package before the manuscript cites a permanent archive for the finalized analysis.
